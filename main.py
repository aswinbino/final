"""
ClauseGuard AI - FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import router as api_v1_router
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("🚀 ClauseGuard AI starting up...")
    
    # Initialize database
    await init_db()
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Warm up NLP models
    from app.services.nlp_service import NLPService
    NLPService.get_instance()
    
    logger.info("✅ ClauseGuard AI ready!")
    yield
    
    logger.info("🛑 ClauseGuard AI shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Explainable AI-powered contract risk assessment platform.",
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan,
    )

    # CORS — allow local dev + any Vercel deployment
    allowed_origins = [
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    # Accept all Vercel preview / production URLs
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API router
    app.include_router(api_v1_router, prefix="/api/v1")

    # Health check
    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "app": settings.APP_NAME, "version": settings.VERSION}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
