import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.google_drive_service import GoogleDriveService
from app.services.payment_service import PaymentService
from app.services.gumroad_service import verify_ping, extract_ping_data

logger = logging.getLogger(__name__)

router = APIRouter(tags=["payments"])

# ── Service singletons ────────────────────────────────────────────────────────

_drive_service: Optional[GoogleDriveService] = None
_payment_service: Optional[PaymentService] = None


def get_drive_service() -> GoogleDriveService:
    global _drive_service
    if _drive_service is None:
        try:
            _drive_service = GoogleDriveService(settings.google_service_account_file)
        except Exception as e:
            logger.error(f"Failed to initialize GoogleDriveService: {e}")
            raise HTTPException(status_code=500, detail="Google Drive service not configured")
    return _drive_service


def get_payment_service(
    drive_service: GoogleDriveService = Depends(get_drive_service),
) -> PaymentService:
    global _payment_service
    if _payment_service is None:
        _payment_service = PaymentService(drive_service)
    return _payment_service


# ── Shared admin auth dependency ──────────────────────────────────────────────

def require_admin_key(x_admin_key: Optional[str] = Header(None)) -> None:
    """Reject the request if the X-Admin-Key header does not match ADMIN_API_KEY."""
    if not settings.admin_api_key:
        raise HTTPException(status_code=503, detail="Admin API key not configured on server")
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin API key")


# ── Gumroad: ping webhook ─────────────────────────────────────────────────────

@router.post("/gumroad/ping")
async def gumroad_ping(
    request: Request,
    db: Session = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Gumroad Ping endpoint.

    Gumroad sends a POST with form-encoded data after each sale.
    We verify seller_id, extract the buyer email and product,
    then grant Google Sheets access.
    """
    form_data = await request.form()
    ping_data = extract_ping_data(dict(form_data))

    # Verify seller_id
    if not verify_ping(ping_data["seller_id"], settings.gumroad_seller_id):
        logger.error("Gumroad ping verification failed - seller_id mismatch")
        return {"status": "rejected"}

    email = ping_data["email"]
    sale_id = ping_data["sale_id"]
    product_permalink = ping_data["product_permalink"]

    if not email:
        logger.error("Missing email in Gumroad ping")
        return {"status": "error", "reason": "missing email"}

    if not sale_id:
        logger.error("Missing sale_id in Gumroad ping")
        return {"status": "error", "reason": "missing sale_id"}

    # Parse price (Gumroad sends as string like "13.00")
    try:
        amount_cents = int(float(ping_data["price"]) * 100)
    except (ValueError, TypeError):
        amount_cents = 0

    try:
        result = payment_service.process_payment(
            db=db,
            payment_id=sale_id,
            transaction_id=sale_id,
            email=email,
            amount=amount_cents,
            product_permalink=product_permalink,
        )

        if result["success"]:
            logger.info(f"Gumroad sale processed: {result}")
        else:
            logger.error(f"Gumroad sale processing failed: {result}")

        return {"status": "received"}

    except Exception as e:
        logger.exception(f"Unexpected error processing Gumroad ping: {e}")
        return {"status": "error"}


# ── Admin: revoke access ──────────────────────────────────────────────────────

class RevokeRequest(BaseModel):
    email: str


@router.post("/admin/revoke", dependencies=[Depends(require_admin_key)])
async def revoke_access(
    body: RevokeRequest,
    db: Session = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Admin endpoint to revoke Google Sheets access for a given email.

    Requires the X-Admin-Key header to match the ADMIN_API_KEY env var.
    """
    result = payment_service.revoke_access_for_email(db, body.email)

    if result["success"]:
        return result
    raise HTTPException(status_code=404, detail=result["message"])
