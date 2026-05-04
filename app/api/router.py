"""
Root API Router
===============
Aggregates all API versions.
Currently only v1, but easily extensible for v2.
"""

from fastapi import APIRouter
from app.api.v1.router import v1_router

# Root API router
api_router = APIRouter(prefix="/api")

# Include versioned routers
api_router.include_router(v1_router)

# Future: api_router.include_router(v2_router)