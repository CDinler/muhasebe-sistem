# -*- coding: utf-8 -*-
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env
    )
    
    # Database (MySQL/MariaDB via XAMPP)
    DATABASE_URL: str = "mysql+pymysql://root@localhost:3306/muhasebe_sistem?charset=utf8mb4"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:8000"
    
    # Şirket Bilgileri (XML'de direction tespiti için)
    COMPANY_TAX_NUMBER: str = "1234567890"  # Şirketinizin VKN'si - .env'den okunur
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # Excel Integration
    EXCEL_FILE_PATH: str = "C:/Users/CAGATAY/OneDrive/Desktop/MUHASEBE - KADIOĞULLARI END/Muhasebe Defteri.xlsb"
    EXCEL_SYNC_INTERVAL: int = 300
    
    # Backup
    BACKUP_PATH: str = "C:/Database/Backups/muhasebe-sistem"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Email / SMTP Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "muhasebe@example.com"
    SMTP_PASSWORD: str = "your-app-password"
    SMTP_USE_TLS: bool = True


settings = Settings()
