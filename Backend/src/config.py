# Fixed src/config.py

"""Application configuration management."""

from functools import lru_cache
from typing import List, Optional, Union

from pydantic import Field, computed_field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = Field("postgresql://localhost/studhelper")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(...)
    OPENAI_ORG_ID: Optional[str] = None
    
    # Pricing per 1M tokens
    ECONOMIC_INPUT_PRICE: float = 0.15
    ECONOMIC_OUTPUT_PRICE: float = 0.60
    STANDARD_INPUT_PRICE: float = 2.50
    STANDARD_OUTPUT_PRICE: float = 10.00
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    
    # File Upload
    MAX_FILE_SIZE: int = 100_000_000  # 100MB
    UPLOAD_DIR: str = "./uploads"
    
    # CORS - can be either a comma-separated string or a list
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:8501"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @validator('CORS_ORIGINS', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Split comma-separated string and strip whitespace
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        elif isinstance(v, list):
            # Already a list, just return it
            return v
        else:
            # Fallback to default
            return ["http://localhost:3000", "http://localhost:8501"]
    
    @computed_field
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()