"""
Custom Middleware Module
========================
Middleware runs before/after each request.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs all incoming requests and their processing time.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process each request through middleware.
        MUST be async for Starlette BaseHTTPMiddleware.
        """
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"→ Request started: {request.method} {request.url.path}"
        )
        
        # Process the request - MUST await call_next
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log completion
        logger.info(
            f"← Request completed: {request.method} {request.url.path} "
            f"| Status: {response.status_code} | Duration: {duration:.3f}s"
        )
        
        # Add custom header
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response