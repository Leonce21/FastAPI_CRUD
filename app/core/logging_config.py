"""
Structured Logging Configuration
===============================
This module sets up Python's logging system with structured output.
It includes timestamps, log levels, and module names for easy debugging.
In production, this could be extended to output JSON for log aggregators.
"""

import logging
import sys
from typing import Any


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to console output.
    Makes it easier to distinguish log levels during development.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with color coding."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        
        return super().format(record)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure application-wide logging.
    
    Args:
        log_level: Minimum log level to display (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured root logger instance
    """
    # Get numeric log level (e.g., "INFO" -> 20)
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("fastapi_crud")
    logger.setLevel(numeric_level)
    
    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger
    
    # Console handler (outputs to terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Format: Timestamp | Level | Module | Message
    # Example: 2024-01-15 10:30:45 | INFO | database | Connected to MongoDB
    formatter = ColoredFormatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Log startup message
    logger.info("=" * 50)
    logger.info("Logging system initialized")
    logger.info(f"Log level: {log_level}")
    logger.info("=" * 50)
    
    return logger


# Global logger instance
logger = setup_logging()