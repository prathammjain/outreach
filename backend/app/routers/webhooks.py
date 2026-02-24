import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.google_drive_service import GoogleDriveService
from app.services.payment_service import PaymentService
from app.services.phonepe_service import extract_payment_data, verify_callback

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


# ── PhonePe: create order ─────────────────────────────────────────────────────

class CreateOrderRequest(BaseModel):
    email: str
    tier: int  # 1 or 2


@router.post("/create-order")
async def create_order(body: CreateOrderRequest):
    """
    Called by the frontend when the user clicks "Buy".
    Creates a PhonePe order and returns the checkout redirect URL.

    The buyer's email is embedded in metaInfo.udf1 so PhonePe passes it
    back in the S2S callback — no session state required.
    """
    if body.tier not in (1, 2):
        raise HTTPException(status_code=400, detail="tier must be 1 or 2")
    if not body.email or "@" not in body.email:
        raise HTTPException(status_code=400, detail="Valid email is required")

    amount = settings.tier_1_price if body.tier == 1 else settings.tier_2_price
    merchant_order_id = str(uuid.uuid4())

    if not settings.phonepe_client_id:
        raise HTTPException(status_code=503, detail="PhonePe not configured")

    try:
        from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
        from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import (
            StandardCheckoutPayRequest,
        )
        from phonepe.sdk.pg.env import Env

        env = Env.PRODUCTION if settings.phonepe_env.upper() == "PRODUCTION" else Env.SANDBOX

        client = StandardCheckoutClient.get_instance(
            client_id=settings.phonepe_client_id,
            client_secret=settings.phonepe_client_secret,
            client_version=settings.phonepe_client_version,
            env=env,
        )

        # redirect_url: where the user lands after payment (frontend success page)
        redirect_url = f"{settings.backend_url.rstrip('/')}/payment-complete"

        pay_request = StandardCheckoutPayRequest.build_request(
            merchant_order_id=merchant_order_id,
            amount=amount,
            redirect_url=redirect_url,
            meta_info={"udf1": body.email},   # carry email through checkout
        )

        response = client.pay(pay_request)
        logger.info(f"PhonePe order created: {merchant_order_id} for {body.email}, tier {body.tier}")

        return {
            "merchant_order_id": merchant_order_id,
            "checkout_url": response.redirect_url,
        }

    except Exception as e:
        logger.exception(f"Failed to create PhonePe order: {e}")
        raise HTTPException(status_code=502, detail="Failed to create payment order")


# ── PhonePe: S2S callback ─────────────────────────────────────────────────────

@router.post("/phonepe/callback")
async def phonepe_callback(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    PhonePe Server-to-Server callback endpoint.

    PhonePe authenticates itself by sending:
        Authorization: SHA256(username:password)

    We verify that hash matches our stored credentials, then grant
    Google Sheets access to the buyer.

    Always returns 200 so PhonePe doesn't retry unnecessarily.
    """
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8")

    # ── Verify authenticity ───────────────────────────────────────────────────
    if not settings.phonepe_callback_username or not settings.phonepe_callback_password:
        logger.error("PhonePe callback credentials not configured")
        return {"status": "misconfigured"}

    if not verify_callback(
        callback_body=body_str,
        authorization_header=authorization or "",
        username=settings.phonepe_callback_username,
        password=settings.phonepe_callback_password,
    ):
        logger.error("PhonePe callback verification failed – possible spoofed request")
        # Return 200 to avoid leaking whether we rejected it, but don't process
        return {"status": "rejected"}

    # ── Parse payload ─────────────────────────────────────────────────────────
    payment_data = extract_payment_data(body_str)
    event = payment_data.get("event", "")
    state = payment_data.get("state", "")

    logger.info(f"PhonePe callback: event={event} state={state} order={payment_data.get('merchant_order_id')}")

    # Only process completed payments
    if state != "COMPLETED":
        logger.info(f"Ignoring non-completed state: {state}")
        return {"status": "ignored", "state": state}

    # Validate required fields
    email = payment_data.get("email")
    merchant_order_id = payment_data.get("merchant_order_id")

    if not email:
        logger.error("Missing email in PhonePe callback (check metaInfo.udf1)")
        return {"status": "error", "reason": "missing email"}

    if not merchant_order_id:
        logger.error("Missing merchantOrderId in PhonePe callback")
        return {"status": "error", "reason": "missing order id"}

    # ── Process payment and grant access ──────────────────────────────────────
    try:
        result = payment_service.process_payment(
            db=db,
            payment_id=merchant_order_id,
            transaction_id=payment_data.get("transaction_id"),
            email=email,
            amount=payment_data["amount"],
        )

        if result["success"]:
            logger.info(f"Access granted: {result}")
        else:
            logger.error(f"Payment processing failed: {result}")

        return {"status": "received"}

    except Exception as e:
        logger.exception(f"Unexpected error processing PhonePe callback: {e}")
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


# ── Frontend redirect landing page ────────────────────────────────────────────

@router.get("/payment-complete")
async def payment_complete():
    """
    PhonePe redirects the user here after checkout.
    The frontend should poll /check-status?order_id=... or show a generic
    'check your email' message. This is a minimal JSON response that the
    frontend can detect to show its success modal.
    """
    return {"status": "redirect_received", "message": "Payment processed. Check your email for access."}
