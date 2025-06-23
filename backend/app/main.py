from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.endpoints import auth, manufacturers, users, applications, language_model, model_choice
from app.database import init_db, SessionLocal
from app.init_data import ensure_default_invite_exists
import asyncio

app = FastAPI(
    title="inoAIDB API",
    version="1.0.0",
    description="inoAIDB API Documentation",
    docs_url="/docs"
)

settings = get_settings()

origins = [
    "http://localhost:5173",
    f"http://{settings.public_ip}:{settings.port_frontend}",
]

# CORS localhost:5173 = Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

print(f"🔧 Loaded environment: {settings.env}")
print(f"📦 DB: {settings.database_url}")

# API-Routen
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(manufacturers.router, prefix="/api/manufacturers", tags=["manufacturer"])
app.include_router(applications.router, prefix="/api/applications", tags=["application"])
app.include_router(language_model.router, prefix="/api/languagemodels", tags=["languagemodel"])
app.include_router(model_choice.router, prefix="/api/modelchoices", tags=["modelchoice"])

# Startup-Event
@app.on_event("startup")
async def startup():
    init_db()

    if settings.env != "test":
        db = SessionLocal()
        try:
            ensure_default_invite_exists(db)
        finally:
            db.close()
