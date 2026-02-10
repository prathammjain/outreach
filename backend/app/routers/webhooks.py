from fastapi import APIRouter, Request, HTTPException, Depends, Header
from sqlalchemy.orm import Session
import json
import logging
from typing import Optional

from app.database import get_db
from app.config import settings
from app.services.razorpay_service import verify_webhook_signature, extract_payment_data
from app.services.google_drive_service import GoogleDriveService
from app.services.payment_service import PaymentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/razorpay", tags=["webhooks"])

# Service singletons (initialized lazily)
_drive_service = None
_payment_service = None

def get_drive_service():
    global _drive_service
    if _drive_service is None:
        try:
            _drive_service = GoogleDriveService(settings.google_service_account_file)
        except Exception as e:
            logger.error(f"Failed to initialize GoogleDriveService: {e}")
            raise HTTPException(status_code=500, detail="Google Drive service unconfigured")
    return _drive_service

def get_payment_service(drive_service: GoogleDriveService = Depends(get_drive_service)):
    global _payment_service
    if _payment_service is None:
        _payment_service = PaymentService(drive_service)
    return _payment_service


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Handle Razorpay payment.captured webhook.
    
    This endpoint:
    1. Verifies webhook signature
    2. Extracts payment data
    3. Processes payment and grants access
    4. Returns 200 OK to Razorpay
    """
    # Get raw request body for signature verification
    body = await request.body()
    
    # Verify signature
    if not x_razorpay_signature:
        logger.error("Missing X-Razorpay-Signature header")
        raise HTTPException(status_code=401, detail="Missing signature header")
    
    if not settings.razorpay_webhook_secret:
        logger.error("RAZORPAY_WEBHOOK_SECRET is not configured")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
        
    if not verify_webhook_signature(
        body,
        x_razorpay_signature,
        settings.razorpay_webhook_secret
    ):
        logger.error("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Extract payment data
    payment_data = extract_payment_data(payload)
    
    # Log webhook event
    logger.info(f"Received webhook event: {payment_data.get('event')}")
    
    # Only process payment.captured events
    if payment_data.get("event") != "payment.captured":
        logger.info(f"Ignoring event: {payment_data.get('event')}")
        return {"status": "ignored", "event": payment_data.get("event")}
    
    # Validate payment status
    if payment_data.get("status") != "captured":
        logger.warning(f"Payment status is not captured: {payment_data.get('status')}")
        return {"status": "ignored", "reason": "payment not captured"}
    
    # Validate required fields
    if not payment_data.get("email"):
        logger.error("Missing email in payment data")
        raise HTTPException(status_code=400, detail="Missing email")
    
    if not payment_data.get("payment_id"):
        logger.error("Missing payment_id in payment data")
        raise HTTPException(status_code=400, detail="Missing payment_id")
    
    # Process payment and grant access
    try:
        result = payment_service.process_payment(
            db=db,
            payment_id=payment_data["payment_id"],
            order_id=payment_data.get("order_id"),
            email=payment_data["email"],
            amount=payment_data["amount"]
        )
        
        if result["success"]:
            logger.info(f"Successfully processed payment: {result}")
            return {
                "status": "success",
                "payment_id": result["payment_id"],
                "message": result["message"]
            }
        else:
            logger.error(f"Failed to process payment: {result}")
            # Still return 200 to Razorpay to acknowledge receipt
            return {
                "status": "failed",
                "payment_id": result["payment_id"],
                "message": result["message"]
            }
    
    except Exception as e:
        logger.exception(f"Unexpected error processing payment: {e}")
        # Still return 200 to Razorpay
        return {
            "status": "error",
            "message": "Internal server error"
        }


@router.post("/revoke")
async def revoke_access(
    email: str,
    db: Session = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Admin endpoint to revoke access for a specific email.
    
    TODO: Add authentication/API key protection in production.
    """
    result = payment_service.revoke_access_for_email(db, email)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=404, detail=result["message"])
