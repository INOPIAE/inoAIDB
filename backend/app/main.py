from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.endpoints import auth, manufacturers, users, applications
from app.database import init_db
import asyncio


app = FastAPI(
    title="inoAIDB API",
    version="1.0.0",
    description="inoAIDB API Documentation",
    docs_url="/docs"
)

# CORS für das Frontend (localhost:5173 = Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

settings = get_settings()
print(f"🔧 Loaded environment: {settings.env}")
print(f"📦 DB: {settings.database_url}")


# API-Routen
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(manufacturers.router, prefix="/api/manufacturers", tags=["manufacturer"])
app.include_router(applications.router, prefix="/api/applications", tags=["application"])

# Startup-Event
@app.on_event("startup")
async def startup():
    init_db()
