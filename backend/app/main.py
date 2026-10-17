import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Performs initial startup checks and cleanup on shutdown.
    Notice: We do NOT silently auto-create uncontrolled tables on startup,
    as required; schema migrations are strictly managed via Alembic.
    """
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(backend_dir, "uploads", "avatars"), exist_ok=True)
    print(f"[{settings.PROJECT_NAME}] Starting up backend in {settings.ENVIRONMENT} mode...")
    print(f"[{settings.PROJECT_NAME}] Database target: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    print(f"[{settings.PROJECT_NAME}] CORS origins enabled: {settings.cors_origins_list}")
    yield
    print(f"[{settings.PROJECT_NAME}] Shutting down backend cleanly.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production-structured prototype backend for the BIO-SNIFF Agricultural IoT System. "
        "Supports 3-node mesh sensing, Master ESP32 5G gateway hourly cycle ingestion, "
        "rolling 5-hour LSTM disease prediction, authoritative spatial localization, and farmer alerting."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS middleware for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploaded media directory
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
uploads_dir = os.path.join(backend_dir, "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Mount all API v1 routes (/api/health, /api/auth, /api/farms, /api/nodes)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def read_root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "operational",
        "docs_url": "/docs",
        "api_v1_base": settings.API_V1_STR,
        "health_endpoint": f"{settings.API_V1_STR}/health"
    }
