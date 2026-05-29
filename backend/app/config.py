from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Smart Factory IoT API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server Settings
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", 8000))
    
    # Auth Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback_secret_key_change_me_in_prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    ]
    
    # Database Configuration (PostgreSQL)
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "factory_admin")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "change_me_in_production")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "smart_factory")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Snowflake (Optional for backend directly, mostly used by Airflow)
    SNOWFLAKE_ENABLED: bool = os.getenv("SNOWFLAKE_ENABLED", "false").lower() == "true"
    
    class Config:
        case_sensitive = True

settings = Settings()
