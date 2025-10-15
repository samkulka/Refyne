"""
API Configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Settings
    api_title: str = "Refyne Data Cleanser API"
    api_version: str = "0.1.0"
    api_description: str = "Automatically clean, validate, and transform messy data into AI-ready datasets"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    api_key_prefix: str = "refyne_"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    disable_auth: bool = True  # Set to False in production
    
    # Storage
    upload_dir: Path = Path("storage/uploads")
    output_dir: Path = Path("storage/outputs")
    temp_dir: Path = Path("storage/temp")
    max_file_size_mb: int = 100
    allowed_extensions: List[str] = [".csv", ".xlsx", ".xls", ".json", ".parquet"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 3600  # seconds
    
    # Database (Optional for MVP)
    database_url: str = "sqlite:///./refyne.db"
    
    # Redis (Optional for MVP)
    redis_url: str = "redis://localhost:6379/0"
    
    # CORS - Allow all origins in production, specific origins in dev
    cors_origins: List[str] = ["*"]  # Allow all origins for now
    
    # Cleaning Options
    default_aggressive: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create storage directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()