"""Database module."""
from typing import Optional
import logging
from ..config import get_settings
from .base import DatabaseInterface
from .arango.database import ArangoDatabase

# Configure logging
logger = logging.getLogger(__name__)

# Global database instance
_database: Optional[DatabaseInterface] = None

async def create_database() -> DatabaseInterface:
    """Create a new database instance.
    
    Returns:
        Database instance (ArangoDB)
    """
    settings = get_settings()
    
    # Create ArangoDB instance
    logger.info(f"Connecting to ArangoDB at {settings.ARANGO_HOST}:{settings.ARANGO_PORT}")
    db = ArangoDatabase(
        host=settings.ARANGO_HOST,
        port=settings.ARANGO_PORT,
        username=settings.ARANGO_USER,
        password=settings.ARANGO_PASSWORD,
        db_name=settings.ARANGO_DB
    )
    
    # Connect to the database
    await db.connect()
    logger.info(f"Successfully connected to ArangoDB database: {settings.ARANGO_DB}")
    return db

async def get_database() -> DatabaseInterface:
    """Get the global database instance.
    
    Returns:
        Database instance
    """
    global _database
    if _database is None:
        _database = await create_database()
    return _database
