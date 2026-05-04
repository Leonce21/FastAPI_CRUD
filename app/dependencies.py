"""
Shared Dependencies Module
==========================
Common dependencies used across multiple routes.
"""

from fastapi import Header, HTTPException, status


async def verify_api_key(x_api_key: str = Header(..., description="API Key for authentication")):
    """
    Example API key verification dependency.
    In production, validate against database or secret manager.
    """
    # For demo purposes, accept any non-empty key
    # In production: check against hashed keys in database
    if not x_api_key or len(x_api_key) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return x_api_key