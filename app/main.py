"""
FastAPI Application - Fixed for Both Local and Vercel
=====================================================
Uses async lifespan for Uvicorn compatibility.
Vercel will handle it with Mangum.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import db
from app.api.router import api_router
from app.middleware import LoggingMiddleware
from app.core.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async lifespan context manager.
    REQUIRED by Uvicorn/Starlette - must be async.
    """
    logger.info(f"🚀 Starting {settings.app_title}")
    
    # Connect to MongoDB (synchronous call inside async)
    db.connect()
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down...")
    db.disconnect()


def create_application() -> FastAPI:
    """Create and configure FastAPI app."""
    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description="Production-ready FastAPI CRUD API with MongoDB Atlas",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan  # Now properly async
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Include API routes
    app.include_router(api_router)
    
    @app.get("/health", tags=["Health"])
    def health_check():
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment
        }
    
    @app.get("/", tags=["Root"])
    def root():
        return {
            "message": "FastAPI MongoDB CRUD API",
            "docs": "/docs",
            "health": "/health"
        }
    
    return app


# Create app instance
app = create_application()