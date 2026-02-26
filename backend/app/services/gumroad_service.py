import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def verify_ping(seller_id_from_ping: str, expected_seller_id: str) -> bool:
    """Verify a Gumroad ping by checking the seller_id matches."""
    if not expected_seller_id:
        logger.error("Gumroad seller_id not configured")
        return False
    return seller_id_from_ping == expected_seller_id


def extract_ping_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and normalize relevant fields from a Gumroad ping."""
    return {
        "seller_id": form_data.get("seller_id", ""),
        "product_id": form_data.get("product_id", ""),
        "product_permalink": form_data.get("product_permalink", ""),
        "email": form_data.get("email", ""),
        "price": form_data.get("price", "0"),
        "sale_id": form_data.get("sale_id", ""),
        "sale_timestamp": form_data.get("sale_timestamp", ""),
        "order_number": form_data.get("order_number", ""),
    }
