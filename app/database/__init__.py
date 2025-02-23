"""Database module."""
from typing import Optional
import os

from .core.database import Neo4jDatabase

# Default configuration
DEFAULT_NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
DEFAULT_NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
DEFAULT_NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "kqml_dev_2025")

_database: Optional[Neo4jDatabase] = None

async def create_database(
    uri: str = DEFAULT_NEO4J_URI,
    user: str = DEFAULT_NEO4J_USER,
    password: str = DEFAULT_NEO4J_PASSWORD
) -> Neo4jDatabase:
    """Create a new database instance.
    
    Args:
        uri: Neo4j URI
        user: Username
        password: Password
        
    Returns:
        Database instance
    """
    db = Neo4jDatabase(uri, user, password)
    await db.connect()
    return db

async def get_database() -> Neo4jDatabase:
    """Get the global database instance.
    
    Returns:
        Database instance
    """
    global _database
    if _database is None:
        _database = await create_database()
    return _database
