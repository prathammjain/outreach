from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # ── PhonePe Configuration ──────────────────────────────────────────────
    phonepe_client_id: Optional[str] = None
    phonepe_client_secret: Optional[str] = None
    phonepe_client_version: int = 1           # Integer version given by PhonePe
    phonepe_env: str = "SANDBOX"              # "SANDBOX" or "PRODUCTION"

    # Callback authentication (set these in PhonePe dashboard → Developer Settings → Webhook)
    phonepe_callback_username: Optional[str] = None
    phonepe_callback_password: Optional[str] = None

    # ── Google Service Account ─────────────────────────────────────────────
    google_service_account_file: Optional[str] = "./service-account.json"
    google_service_account_json_base64: Optional[str] = None

    # ── Database ───────────────────────────────────────────────────────────
    database_url: str = "sqlite:////data/payments.db"   # mounted volume path

    # ── Product Pricing (in paise) ─────────────────────────────────────────
    tier_1_price: int = 99900    # ₹999
    tier_2_price: int = 149900   # ₹1,499

    # ── Google Sheet IDs ───────────────────────────────────────────────────
    indian_sheet_id: Optional[str] = None
    yc_sheet_id: Optional[str] = None

    # ── Admin / Security ───────────────────────────────────────────────────
    # API key required to call the /admin/revoke endpoint
    admin_api_key: Optional[str] = None

    # Comma-separated list of allowed origins for CORS.
    # Example: "https://outreachkit.in,https://www.outreachkit.in"
    # Leave empty to allow all (dev only).
    allowed_origins: str = ""

    # Public URL of this backend – used to build the callback URL sent to PhonePe
    backend_url: str = "https://your-backend.railway.app"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
