from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # ── Gumroad Configuration ─────────────────────────────────────────────
    gumroad_seller_id: Optional[str] = None

    # Product permalinks (the short code in the Gumroad product URL)
    gumroad_indian_permalink: Optional[str] = None
    gumroad_yc_permalink: Optional[str] = None
    gumroad_uk_permalink: Optional[str] = None

    # ── Google Service Account ─────────────────────────────────────────────
    google_service_account_file: Optional[str] = "./service-account.json"
    google_service_account_json_base64: Optional[str] = None

    # ── Database ───────────────────────────────────────────────────────────
    database_url: str = "sqlite:////data/payments.db"   # mounted volume path

    # ── Google Sheet IDs ───────────────────────────────────────────────────
    indian_sheet_id: Optional[str] = None
    yc_sheet_id: Optional[str] = None
    uk_sheet_id: Optional[str] = None

    # ── Admin / Security ───────────────────────────────────────────────────
    # API key required to call the /admin/revoke endpoint
    admin_api_key: Optional[str] = None

    # Comma-separated list of allowed origins for CORS.
    # Example: "https://outreachkit.in,https://www.outreachkit.in"
    # Leave empty to allow all (dev only).
    allowed_origins: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
