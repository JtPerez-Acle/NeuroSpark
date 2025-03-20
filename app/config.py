"""Configuration module."""
import os
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings."""
    
    # ArangoDB settings
    ARANGO_HOST: str = os.getenv("ARANGO_HOST", "localhost")
    ARANGO_PORT: int = int(os.getenv("ARANGO_PORT", "8529"))
    ARANGO_DB: str = os.getenv("ARANGO_DB", "blockchain_intelligence")
    ARANGO_USER: str = os.getenv("ARANGO_USER", "root")
    ARANGO_PASSWORD: str = os.getenv("ARANGO_PASSWORD", "password")

    # Pydantic v2 settings configuration
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
