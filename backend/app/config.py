from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # Razorpay Configuration
    razorpay_webhook_secret: Optional[str] = None
    
    # Google Service Account
    google_service_account_file: Optional[str] = "./service-account.json"
    google_service_account_json_base64: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./payments.db"
    
    # Product Pricing (in paise/smallest currency unit)
    tier_1_price: int = 99900   # Default ₹999
    tier_2_price: int = 149900  # Default ₹1499
    
    # Google Sheet IDs
    indian_sheet_id: Optional[str] = None
    yc_sheet_id: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
