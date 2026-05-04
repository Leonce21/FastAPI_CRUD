"""
Custom Middleware Module
========================
Middleware runs before/after each request.
Used for logging, CORS, timing, etc.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs all incoming requests and their processing time.
    Helps with debugging and performance monitoring.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process each request through middleware.
        
        Logic:
            1. Log request start
            2. Record start time
            3. Process request
            4. Calculate duration
            5. Log completion
        """
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"→ Request started: {request.method} {request.url.path}"
        )
        
        # Process the request (call next middleware or route handler)
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log completion with status and timing
        logger.info(
            f"← Request completed: {request.method} {request.url.path} "
            f"| Status: {response.status_code} | Duration: {duration:.3f}s"
        )
        
        # Add custom header with response time
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response