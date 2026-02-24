import hashlib
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def verify_callback(
    callback_body: str,
    authorization_header: str,
    username: str,
    password: str,
) -> bool:
    """
    Verify PhonePe S2S callback authenticity.

    PhonePe sends:  Authorization: SHA256(username:password)
    We hash our own username:password and compare.

    Args:
        callback_body:        Raw request body string (unused in hash, kept for symmetry)
        authorization_header: Value of the Authorization header from PhonePe
        username:             Merchant callback username (set in PhonePe dashboard)
        password:             Merchant callback password (set in PhonePe dashboard)

    Returns:
        True if the header matches the expected hash, False otherwise.
    """
    if not authorization_header or not username or not password:
        logger.error("Missing authorization header or credentials for callback verification")
        return False

    expected = hashlib.sha256(f"{username}:{password}".encode("utf-8")).hexdigest()

    # Constant-time comparison to prevent timing attacks
    import hmac
    return hmac.compare_digest(expected, authorization_header.strip())


def extract_payment_data(callback_body: str) -> Dict[str, Any]:
    """
    Extract payment data from a PhonePe S2S callback payload.

    The callback body is a JSON string with this shape:
    {
      "type": "PG_ORDER_COMPLETED",   // or PG_ORDER_FAILED / PG_ORDER_ATTEMPTED
      "payload": {
        "merchantOrderId": "...",
        "state":           "COMPLETED",   // FAILED, PENDING
        "amount":          99900,
        "expireAt":        1234567890,
        "metaInfo": {
          "udf1": "user@example.com"   // email stored here by our /create-order
        },
        "paymentDetails": [
          {
            "transactionId": "...",
            "paymentMode":   "UPI",
            "timestamp":     1234567890,
            "state":         "COMPLETED"
          }
        ]
      }
    }

    Returns a normalised dict compatible with the existing PaymentService interface.
    """
    try:
        data = json.loads(callback_body)
    except (json.JSONDecodeError, TypeError):
        logger.error("Failed to parse PhonePe callback body as JSON")
        return {}

    event_type = data.get("type", "")
    payload = data.get("payload", {})

    meta_info = payload.get("metaInfo") or {}
    payment_details = payload.get("paymentDetails") or []
    first_txn = payment_details[0] if payment_details else {}

    return {
        "event":             event_type,            # e.g. PG_ORDER_COMPLETED
        "merchant_order_id": payload.get("merchantOrderId"),
        "transaction_id":    first_txn.get("transactionId"),
        "state":             payload.get("state"),  # COMPLETED / FAILED / PENDING
        "amount":            payload.get("amount"), # paise
        "email":             meta_info.get("udf1"), # stored by us at order creation
        "payment_mode":      first_txn.get("paymentMode"),
    }
