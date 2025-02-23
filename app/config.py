"""Configuration module."""
import os
from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # Neo4j settings
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")

    class Config:
        """Pydantic config."""
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
