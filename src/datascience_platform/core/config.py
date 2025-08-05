"""Configuration management for the DataScience Analytics Platform."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = Field(default="DataScience Analytics Platform")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    
    # Data processing settings
    default_chunk_size: int = Field(default=10000, ge=1)
    max_memory_usage_gb: float = Field(default=4.0, ge=0.1)
    temp_dir: Path = Field(default_factory=lambda: Path("./temp"))
    
    # Database settings
    database_url: Optional[str] = Field(default=None)
    database_timeout: int = Field(default=30, ge=1)
    
    # API settings
    api_host: str = Field(default="localhost")
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_workers: int = Field(default=1, ge=1)
    
    # Logging settings
    log_level: str = Field(default="INFO")
    log_file: Optional[Path] = Field(default=None)
    
    # ETL settings
    supported_formats: List[str] = Field(
        default=["csv", "json", "parquet", "xlsx", "xls"]
    )
    validation_strict: bool = Field(default=True)
    
    # Machine learning settings
    ml_random_seed: int = Field(default=42)
    ml_test_size: float = Field(default=0.2, ge=0.1, le=0.9)
    
    @field_validator("temp_dir", mode="before")
    @classmethod
    def validate_temp_dir(cls, v: Any) -> Path:
        """Ensure temp directory exists."""
        if isinstance(v, str):
            v = Path(v)
        if isinstance(v, Path):
            v.mkdir(parents=True, exist_ok=True)
            return v
        raise ValueError("temp_dir must be a valid path")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @field_validator("supported_formats")
    @classmethod
    def validate_formats(cls, v: List[str]) -> List[str]:
        """Validate supported file formats."""
        if not v:
            raise ValueError("At least one format must be supported")
        return [fmt.lower() for fmt in v]
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = "DSP_"


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()


def get_config_dict() -> Dict[str, Any]:
    """Get configuration as dictionary."""
    return settings.dict()


def update_settings(**kwargs: Any) -> None:
    """Update settings with new values."""
    global settings
    current_dict = settings.dict()
    current_dict.update(kwargs)
    settings = Settings(**current_dict)