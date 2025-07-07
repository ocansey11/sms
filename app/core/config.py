from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings configuration."""
    
    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "debug"
    
    # Database
    DATABASE_URL: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "sms_dev"
    DB_USER: str = "sms_user"
    DB_PASSWORD: str = "sms_password"
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:3001"
    ]
    
    # Email Configuration
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: Optional[str] = None
    
    # SMS Configuration
    SMS_API_KEY: Optional[str] = None
    SMS_PROVIDER_URL: Optional[str] = None
    
    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "application/pdf"]
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # Session Configuration
    SESSION_EXPIRE_MINUTES: int = 30
    
    # Azure Configuration (for production)
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_CONTAINER_NAME: Optional[str] = None
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Validate critical settings
if not settings.SECRET_KEY or settings.SECRET_KEY == "your-super-secret-jwt-key-here-change-in-production":
    if settings.ENV == "production":
        raise ValueError("SECRET_KEY must be set in production environment")
    
if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL must be set")
