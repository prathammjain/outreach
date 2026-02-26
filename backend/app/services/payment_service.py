import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Payment
from app.config import settings
from app.services.google_drive_service import GoogleDriveService

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for processing payments and managing access."""
    
    def __init__(self, drive_service: GoogleDriveService):
        """
        Initialize payment service.
        
        Args:
            drive_service: Google Drive service instance
        """
        self.drive_service = drive_service
    
    def determine_tier(self, product_permalink: str) -> Optional[int]:
        """
        Determine product tier from Gumroad product permalink.

        Returns:
            Tier number (1, 2, or 3) or None if permalink doesn't match
        """
        if product_permalink == settings.gumroad_indian_permalink:
            return 1
        elif product_permalink == settings.gumroad_yc_permalink:
            return 2
        elif product_permalink == settings.gumroad_uk_permalink:
            return 3
        else:
            logger.warning(f"Unknown product permalink: {product_permalink}")
            return None
    
    def get_sheet_ids_for_tier(self, tier: int) -> List[str]:
        """
        Get list of sheet IDs for a given tier.

        Each tier maps to exactly one Google Sheet.
        """
        sheet_ids = []
        if tier == 1 and settings.indian_sheet_id:
            sheet_ids.append(settings.indian_sheet_id)
        elif tier == 2 and settings.yc_sheet_id:
            sheet_ids.append(settings.yc_sheet_id)
        elif tier == 3 and settings.uk_sheet_id:
            sheet_ids.append(settings.uk_sheet_id)

        if not sheet_ids:
            logger.warning(f"No sheet IDs configured for tier {tier}")

        return sheet_ids
    
    def process_payment(
        self,
        db: Session,
        payment_id: str,
        transaction_id: Optional[str],
        email: str,
        amount: int,
        product_permalink: str,
    ) -> Dict[str, Any]:
        """
        Process a successful payment and grant access.

        Args:
            db:                Database session
            payment_id:        Gumroad sale_id (used as idempotency key)
            transaction_id:    Gumroad sale_id
            email:             Buyer's email
            amount:            Payment amount in cents (USD)
            product_permalink: Gumroad product permalink for tier detection

        Returns:
            Dictionary with success status and details
        """
        # Check if payment already processed (idempotency)
        existing = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if existing:
            logger.info(f"Payment {payment_id} already processed")
            return {
                "success": True,
                "message": "Payment already processed",
                "payment_id": payment_id
            }

        # Determine tier
        tier = self.determine_tier(product_permalink)
        if tier is None:
            logger.error(f"Unknown product '{product_permalink}' for payment {payment_id}")
            return {
                "success": False,
                "message": f"Unknown product: {product_permalink}",
                "payment_id": payment_id
            }

        # Get sheet IDs for tier
        sheet_ids = self.get_sheet_ids_for_tier(tier)
        if not sheet_ids:
            logger.error(f"No sheets configured for tier {tier}")
            return {
                "success": False,
                "message": f"No resources configured for tier {tier}",
                "payment_id": payment_id
            }

        # Grant access to sheets
        granted_sheets = self.drive_service.grant_multiple_access(sheet_ids, email)

        if not granted_sheets:
            logger.error(f"Failed to grant access for payment {payment_id}")
            return {
                "success": False,
                "message": "Failed to grant access to resources",
                "payment_id": payment_id
            }

        # Persist payment record
        try:
            payment = Payment(
                payment_id=payment_id,
                gateway_transaction_id=transaction_id,
                email=email,
                amount=amount,
                product_tier=tier,
                granted_resources=json.dumps(granted_sheets)
            )
            db.add(payment)
            db.commit()

            logger.info(f"Successfully processed payment {payment_id} for {email}, tier {tier}")
            return {
                "success": True,
                "message": "Access granted successfully",
                "payment_id": payment_id,
                "tier": tier,
                "granted_resources": granted_sheets
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Database error for payment {payment_id}: {e}")
            return {
                "success": False,
                "message": "Failed to record payment",
                "payment_id": payment_id
            }
    
    def revoke_access_for_email(self, db: Session, email: str) -> Dict[str, Any]:
        """
        Revoke access for a specific email (admin function).
        
        Args:
            db: Database session
            email: User's email
            
        Returns:
            Dictionary with revocation status
        """
        payments = db.query(Payment).filter(Payment.email == email).all()
        
        if not payments:
            return {
                "success": False,
                "message": f"No payments found for {email}"
            }
        
        revoked_count = 0
        for payment in payments:
            sheet_ids = json.loads(payment.granted_resources)
            for sheet_id in sheet_ids:
                if self.drive_service.revoke_access(sheet_id, email):
                    revoked_count += 1
        
        return {
            "success": True,
            "message": f"Revoked access to {revoked_count} resources for {email}",
            "email": email,
            "revoked_count": revoked_count
        }
