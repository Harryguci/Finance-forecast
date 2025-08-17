from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # App settings
    app_name: str = "STOCK_FORECAST"
    debug: bool = True
    version: str = "1.0.0"
    
    # Server settings
    host: str = "127.0.0.1"
    port: int = 5500
    
    # Database settings
    database_url: Optional[str] = "postgresql+asyncpg://root:123456@localhost:5432/STOCK_FORECAST"
    database_name: str = "STOCK_FORECAST"
    
    # PostgreSQL specific settings
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "root"
    postgres_password: str = "123456"
    postgres_db: str = "STOCK_FORECAST"
    postgres_ssl_mode: str = "prefer"
    postgres_pool_size: int = 10
    postgres_max_overflow: int = 20
    postgres_pool_timeout: int = 30
    postgres_pool_recycle: int = 3600
    
    # API settings
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_max_size: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
    
    # Environment
    environment: str = "development"
    
    # External API settings
    external_api_key: Optional[str] = "your_external_api_key_here"
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # Resource directory
    resource_dir: str = "blob"
    
    # Stock sync worker settings
    frequency_minutes: int = 5
    hour_start: int = 9
    hour_end: int = 16
    except_days: str = "sat,sun"
    
    # Yahoo Finance settings
    yahoo_finance_base_url: str = "https://finance.yahoo.com"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.environment.lower() == "testing"
    
    @property
    def postgres_url(self) -> str:
        """Generate PostgreSQL URL from individual components"""
        if self.database_url:
            return self.database_url
        
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}?sslmode={self.postgres_ssl_mode}"
    
    @property
    def except_days_list(self) -> List[str]:
        """Convert except_days string to list"""
        return [day.strip().lower() for day in self.except_days.split(",")]

settings = Settings()