import hmac
import hashlib
from typing import Dict, Any


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify Razorpay webhook signature using HMAC SHA256.
    
    Args:
        payload: Raw request body as bytes
        signature: Signature from X-Razorpay-Signature header
        secret: Webhook secret from Razorpay dashboard
        
    Returns:
        True if signature is valid, False otherwise
    """
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature)


def extract_payment_data(webhook_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant payment data from Razorpay webhook payload.
    
    Args:
        webhook_payload: Parsed JSON webhook payload
        
    Returns:
        Dictionary with payment_id, email, amount, order_id, status
    """
    event = webhook_payload.get("event", "")
    payload = webhook_payload.get("payload", {})
    payment = payload.get("payment", {}).get("entity", {})
    
    return {
        "event": event,
        "payment_id": payment.get("id"),
        "order_id": payment.get("order_id"),
        "email": payment.get("email"),
        "amount": payment.get("amount"),  # In paise
        "status": payment.get("status"),
        "method": payment.get("method"),
    }
