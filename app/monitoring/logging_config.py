"""Logging configuration module."""
import os
import sys
import uuid
from pathlib import Path
import json
from datetime import datetime
from fastapi import Request
from loguru import logger

def get_log_dir():
    """Get the log directory based on environment."""
    if os.getenv("TEST_LOG_DIR"):
        return Path(os.getenv("TEST_LOG_DIR"))
    elif os.getenv("LOG_DIR"):
        return Path(os.getenv("LOG_DIR"))
    
    # Use relative path from current directory
    base_dir = Path(__file__).parent.parent.parent
    return base_dir / "logs"

def setup_logging():
    """Configure logging settings."""
    # Remove default handlers
    logger.remove()
    
    # Get log directory
    log_dir = get_log_dir()
    
    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure JSON logger for application logs
    logger.add(
        str(log_dir / "app.log"),  # Use .log extension for all files
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        serialize=False,  # Don't serialize for easier testing
        rotation="1 day",
        level="DEBUG" if os.getenv("TESTING") else "INFO",
        enqueue=True,  # Enable thread-safe logging
        catch=True  # Catch errors in handlers
    )
    
    # Configure error logs
    logger.add(
        str(log_dir / "error.log"),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        level="ERROR",
        enqueue=True,
        catch=True,
        diagnose=True,
        filter=lambda record: record["level"].name == "ERROR"
    )
    
    # Configure system logs
    logger.add(
        str(log_dir / "system.log"),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        level="INFO",
        enqueue=True,
        catch=True,
        filter=lambda record: record["level"].name in ["INFO", "WARNING"]
    )
    
    # Add console output for non-test environment
    if not os.getenv("TESTING"):
        logger.add(sys.stdout, level="INFO")

async def log_request_middleware(request: Request, call_next):
    """Log HTTP request information."""
    start_time = datetime.now()
    
    # Log request details
    logger.info(
        "Request started | "
        f"method={request.method} | "
        f"path={request.url.path} | "
        f"client={request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        # Log successful response
        logger.info(
            "Request completed | "
            f"method={request.method} | "
            f"path={request.url.path} | "
            f"status={response.status_code} | "
            f"duration={round((datetime.now() - start_time).total_seconds() * 1000)}ms"
        )
        return response
    except Exception as e:
        # Log error details
        logger.error(
            f"Request failed | "
            f"method={request.method} | "
            f"path={request.url.path} | "
            f"error={str(e)}",
            exc_info=True
        )
        raise
