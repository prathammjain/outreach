from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # Razorpay Configuration
    razorpay_webhook_secret: str
    
    # Google Service Account
    google_service_account_file: str
    
    # Database
    database_url: str = "sqlite:///./payments.db"
    
    # Product Pricing (in paise/smallest currency unit)
    tier_1_price: int  # e.g., 99900 for ₹999
    tier_2_price: int  # e.g., 199900 for ₹1999
    
    # Google Sheet IDs
    indian_sheet_id: str
    yc_sheet_id: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
