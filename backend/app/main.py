from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api.endpoints import auth, manufacturers, users, applications, language_model, model_choice, utils
from app.database import init_db, SessionLocal
from app.init_data import ensure_default_invite_exists

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    if settings.env != "test":
        db = SessionLocal()
        try:
            ensure_default_invite_exists(db)
        finally:
            db.close()

    yield

app = FastAPI(
    title="inoAIDB API",
    version="1.0.0",
    description="inoAIDB API Documentation",
    terms_of_service=settings.contact_tos,
    contact={
        "name": settings.contact_name,
        "email": settings.contact_email,
        "url": settings.contact_url,
    },
    docs_url="/docs",
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",
    f"http://{settings.public_ip}:{settings.port_frontend}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

print(f"🔧 Loaded environment: {settings.env}")
print(f"📦 DB: {settings.database_url}")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(manufacturers.router, prefix="/api/manufacturers", tags=["manufacturer"])
app.include_router(applications.router, prefix="/api/applications", tags=["application"])
app.include_router(language_model.router, prefix="/api/languagemodels", tags=["languagemodel"])
app.include_router(model_choice.router, prefix="/api/modelchoices", tags=["modelchoice"])
app.include_router(utils.router, prefix="/api/utils", tags=["utils"])
