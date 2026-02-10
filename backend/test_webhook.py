import hmac
import hashlib
import json
import requests

# Test configuration (matching .env)
SECRET = "test_secret"
URL = "http://localhost:8000/razorpay/webhook"

# Mock Razorpay Payload
payload = {
    "event": "payment.captured",
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_TEST12345",
                "amount": 110000,
                "currency": "INR",
                "status": "captured",
                "order_id": "order_TEST678",
                "email": "test@example.com",
                "method": "card"
            }
        }
    }
}

body = json.dumps(payload)

# Generate valid signature
signature = hmac.new(
    SECRET.encode('utf-8'),
    body.encode('utf-8'),
    hashlib.sha256
).hexdigest()

print(f"Sending request to {URL}...")
print(f"Signature: {signature}")

headers = {
    "Content-Type": "application/json",
    "X-Razorpay-Signature": signature
}

try:
    response = requests.post(URL, data=body, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
