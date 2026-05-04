"""
Global Exception Handlers
=========================
Centralized error handling for the entire application.
Ensures consistent error responses and proper logging.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logging_config import logger


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.
    
    Returns 422 with detailed field error information.
    """
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": exc.errors()
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions.
    
    Returns 500 to client but logs full traceback for debugging.
    Never expose internal error details to client in production.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error" if True else str(exc)
            # In production, don't expose internal details
        }
    )