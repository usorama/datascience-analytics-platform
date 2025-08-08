"""Configuration settings for QVF API."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "QVF Platform API"
    debug: bool = False
    
    # CORS settings
    allowed_origins: List[str] = ["http://localhost:3006", "http://localhost:3000"]
    
    # Database settings
    database_url: str = "sqlite:///./qvf.db"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # ADO settings
    ado_organization: str = ""
    ado_project: str = ""
    ado_pat_token: str = ""
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    """Get cached settings instance."""
    return Settings()