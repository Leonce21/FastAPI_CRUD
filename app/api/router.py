"""
Root API Router
===============
Aggregates all API versions with /api prefix.
"""

from fastapi import APIRouter
from app.api.v1.router import v1_router

api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)