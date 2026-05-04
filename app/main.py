# app/main.py - Remove lifespan, connect per-request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import db
from app.api.router import api_router
from app.middleware import LoggingMiddleware

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description="Production-ready FastAPI CRUD API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        # NO lifespan here
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(LoggingMiddleware)
    app.include_router(api_router)
    
    @app.get("/health", tags=["Health"])
    def health_check():
        # Lazy connection test
        try:
            db.connect()
            return {"status": "healthy", "mongodb": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @app.get("/", tags=["Root"])
    def root():
        return {"message": "FastAPI MongoDB CRUD API", "docs": "/docs"}
    
    return app

app = create_application()