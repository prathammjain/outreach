"""Quick script to test the Gumroad ping endpoint locally."""

import requests

URL = "http://localhost:8000/gumroad/ping"

# Mock Gumroad Ping payload (form-encoded)
payload = {
    "seller_id": "your_test_seller_id",
    "product_id": "test_product_123",
    "product_permalink": "vtoipk",
    "email": "test@example.com",
    "price": "13.00",
    "sale_id": "test_sale_abc123",
    "sale_timestamp": "2026-02-26T12:00:00Z",
    "order_number": "1234567890",
}

print(f"Sending POST to {URL}...")

try:
    response = requests.post(URL, data=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
