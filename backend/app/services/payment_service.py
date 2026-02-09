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
    
    def determine_tier(self, amount: int) -> Optional[int]:
        """
        Determine product tier from payment amount.
        
        Args:
            amount: Payment amount in paise/smallest currency unit
            
        Returns:
            Tier number (1 or 2) or None if amount doesn't match
        """
        if amount == settings.tier_1_price:
            return 1
        elif amount == settings.tier_2_price:
            return 2
        else:
            logger.warning(f"Unknown payment amount: {amount}")
            return None
    
    def get_sheet_ids_for_tier(self, tier: int) -> List[str]:
        """
        Get list of sheet IDs for a given tier.
        
        Args:
            tier: Product tier (1 or 2)
            
        Returns:
            List of Google Sheet IDs
        """
        if tier == 1:
            return [settings.indian_sheet_id]
        elif tier == 2:
            return [settings.indian_sheet_id, settings.yc_sheet_id]
        else:
            return []
    
    def process_payment(
        self,
        db: Session,
        payment_id: str,
        order_id: Optional[str],
        email: str,
        amount: int
    ) -> Dict[str, Any]:
        """
        Process a successful payment and grant access.
        
        Args:
            db: Database session
            payment_id: Razorpay payment ID
            order_id: Razorpay order ID
            email: Buyer's email
            amount: Payment amount
            
        Returns:
            Dictionary with success status and details
        """
        # Check if payment already processed
        existing = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if existing:
            logger.info(f"Payment {payment_id} already processed")
            return {
                "success": True,
                "message": "Payment already processed",
                "payment_id": payment_id
            }
        
        # Determine tier
        tier = self.determine_tier(amount)
        if tier is None:
            logger.error(f"Invalid amount {amount} for payment {payment_id}")
            return {
                "success": False,
                "message": f"Invalid payment amount: {amount}",
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
                razorpay_order_id=order_id,
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
