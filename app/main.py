"""
FastAPI Application Factory
===========================
This is the entry point of the application.
It creates the FastAPI app instance, configures middleware,
registers routes, and handles startup/shutdown events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import db
from app.api.router import api_router
from app.middleware import LoggingMiddleware
from app.exceptions import validation_exception_handler, general_exception_handler
from app.core.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    
    Startup:
        - Connect to MongoDB
        - Initialize logging
    
    Shutdown:
        - Close MongoDB connection
        - Cleanup resources
    """
    # ===== STARTUP =====
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.app_title} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info("=" * 60)
    
    # Connect to MongoDB Atlas
    await db.connect()
    
    yield  # Application runs here
    
    # ===== SHUTDOWN =====
    logger.info("=" * 60)
    logger.info("🛑 Shutting down application...")
    logger.info("=" * 60)
    
    # Disconnect from MongoDB
    await db.disconnect()


def create_application() -> FastAPI:
    """
    Application factory pattern.
    Creates and configures FastAPI instance.
    
    This pattern allows easy testing with different configurations.
    """
    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description="""
        # FastAPI MongoDB CRUD API
        
        A production-ready CRUD system with:
        - **Async MongoDB** via Motor
        - **Auto-generated Swagger docs**
        - **Structured logging**
        - **Layered architecture** (API → Service → Repository)
        
        """,
        docs_url="/docs",  # Swagger UI path
        redoc_url="/redoc",  # ReDoc path (alternative docs)
        openapi_url="/openapi.json",  # OpenAPI schema
        lifespan=lifespan  # Startup/shutdown events
    )
    
    # ===== CORS MIDDLEWARE =====
    # Allows frontend applications to call API from different domains
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact domains
        allow_credentials=True,
        allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
        allow_headers=["*"],
    )
    
    # ===== CUSTOM MIDDLEWARE =====
    app.add_middleware(LoggingMiddleware)
    
    # ===== EXCEPTION HANDLERS =====
    app.add_exception_handler(Exception, general_exception_handler)
    # Note: FastAPI handles RequestValidationError by default,
    # but we can override if needed
    
    # ===== ROUTES =====
    # Include all API routes under /api prefix
    app.include_router(api_router)
    
    # ===== HEALTH CHECK =====
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint.
        Used by load balancers and monitoring tools.
        """
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment
        }
    
    @app.get("/", tags=["Root"])
    async def root():
        """
        Root endpoint redirects to documentation.
        """
        return {
            "message": "FastAPI MongoDB CRUD API",
            "docs": "/docs",
            "health": "/health"
        }
    
    return app


# Create application instance
app = create_application()