"""
API v1 Router Aggregation
=========================
Combines all v1 route modules into a single router.
This makes it easy to version the API (v1, v2, etc.).
"""

from fastapi import APIRouter
from app.api.v1 import items

# Create v1 router
v1_router = APIRouter(prefix="/v1")

# Include all module routers
# Each module defines its own prefix (e.g., /items)
v1_router.include_router(items.router)