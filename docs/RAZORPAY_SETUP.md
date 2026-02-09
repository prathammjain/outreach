# Razorpay Webhook Setup Guide

This guide explains how to configure Razorpay webhooks to trigger your backend when payments are successful.

## Prerequisites

- Razorpay account (sign up at [razorpay.com](https://razorpay.com))
- Backend deployed and accessible via public URL
- Products configured in Razorpay (or using standard checkout)

---

## Step 1: Access Razorpay Dashboard

1. Log in to [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Switch to **Test Mode** for initial testing (toggle in top-left)
3. Go to **Settings** → **Webhooks**

---

## Step 2: Create Webhook

1. Click **+ Add New Webhook**
2. Fill in the webhook details:

### Webhook URL

Enter your deployed backend URL with the webhook endpoint:

```
https://your-backend-url.com/razorpay/webhook
```

**Examples:**
- Railway: `https://your-app.railway.app/razorpay/webhook`
- Render: `https://your-app.onrender.com/razorpay/webhook`
- Fly.io: `https://your-app.fly.dev/razorpay/webhook`

> [!IMPORTANT]
> The URL must be publicly accessible. Razorpay cannot send webhooks to `localhost`.

### Select Events

**Only select this event:**
- ✅ `payment.captured`

**Do NOT select:**
- ❌ `payment.failed`
- ❌ `order.paid`
- ❌ Other events

> [!NOTE]
> We only process successful payments. Failed payments are ignored.

### Alert Email (Optional)

Enter your email to receive alerts if webhook delivery fails.

---

## Step 3: Save and Get Webhook Secret

1. Click **Create Webhook**
2. Razorpay will generate a **Webhook Secret**
3. **Copy this secret immediately** - you'll need it for your `.env` file
4. The secret looks like: `whsec_1234567890abcdef`

> [!CAUTION]
> Store this secret securely. Never commit it to version control.

---

## Step 4: Configure Environment Variable

Add the webhook secret to your `.env` file:

```env
RAZORPAY_WEBHOOK_SECRET=whsec_1234567890abcdef
```

Redeploy your backend after updating the environment variable.

---

## Step 5: Configure Payment Checkout

### Option A: Razorpay Standard Checkout (Recommended)

In your frontend, configure Razorpay checkout to **require email**:

```javascript
const options = {
  key: 'YOUR_RAZORPAY_KEY_ID',
  amount: 99900, // Amount in paise (₹999)
  currency: 'INR',
  name: 'Your Product Name',
  description: 'Tier 1 Access',
  prefill: {
    email: '', // Leave empty to force user to enter
  },
  readonly: {
    email: false, // Allow user to edit email
  },
  handler: function (response) {
    // Payment successful
    alert('Payment successful! Check your email for access.');
  }
};

const rzp = new Razorpay(options);
rzp.open();
```

> [!IMPORTANT]
> **Email is mandatory.** The webhook will fail if no email is provided.

### Option B: Payment Links

If using Razorpay Payment Links:

1. Go to **Payment Links** in Razorpay Dashboard
2. Create a new payment link
3. **Enable** "Collect customer details"
4. **Check** "Email" as required field
5. Set the amount according to tier:
   - Tier 1: ₹999
   - Tier 2: ₹1999

---

## Step 6: Test Webhook (Test Mode)

### Using Razorpay Test Mode

1. Ensure you're in **Test Mode** (toggle in dashboard)
2. Create a test payment using test card:
   - **Card Number**: `4111 1111 1111 1111`
   - **CVV**: Any 3 digits
   - **Expiry**: Any future date
   - **Email**: Use a real email you can access
3. Complete the payment
4. Check your backend logs to verify webhook received
5. Check the email inbox - you should receive Google's access email

### Verify Webhook Delivery

1. Go to **Settings** → **Webhooks** in Razorpay Dashboard
2. Click on your webhook
3. View **Recent Deliveries**
4. Check for:
   - ✅ Status: 200 OK
   - ✅ Event: `payment.captured`
   - ✅ Response time < 5 seconds

> [!TIP]
> If webhook delivery fails, check:
> - Is your backend URL publicly accessible?
> - Is the webhook secret correct in `.env`?
> - Are there any errors in backend logs?

---

## Step 7: Switch to Live Mode

Once testing is successful:

1. Switch to **Live Mode** in Razorpay Dashboard
2. Create a new webhook for live mode (repeat Step 2)
3. Update your `.env` with the **Live Mode** webhook secret
4. Update frontend with **Live Mode** Razorpay Key ID
5. Redeploy backend and frontend

> [!WARNING]
> Test mode and Live mode have **separate webhook secrets**. Make sure to use the correct one.

---

## Webhook Payload Example

When a payment is captured, Razorpay sends this payload:

```json
{
  "event": "payment.captured",
  "payload": {
    "payment": {
      "entity": {
        "id": "pay_1234567890abcd",
        "order_id": "order_1234567890abcd",
        "amount": 99900,
        "currency": "INR",
        "status": "captured",
        "email": "buyer@example.com",
        "method": "card"
      }
    }
  }
}
```

Your backend extracts:
- `payment_id`: Unique payment identifier
- `email`: Buyer's email (for granting access)
- `amount`: To determine tier (₹999 = Tier 1, ₹1999 = Tier 2)

---

## Troubleshooting

### Webhook returns 401 Unauthorized

**Cause**: Invalid signature or wrong webhook secret

**Solution**:
1. Verify webhook secret in `.env` matches Razorpay dashboard
2. Check backend logs for signature verification errors
3. Ensure you're using the correct secret for Test/Live mode

### Webhook returns 400 Bad Request

**Cause**: Missing email in payment

**Solution**:
1. Ensure checkout is configured to require email
2. Check Razorpay payment details to verify email was collected

### Webhook times out

**Cause**: Backend is slow or unresponsive

**Solution**:
1. Check backend logs for errors
2. Ensure Google Drive API calls are not timing out
3. Optimize database queries

### Payment successful but no access granted

**Cause**: Webhook not triggered or failed

**Solution**:
1. Check Razorpay webhook delivery logs
2. Verify webhook URL is correct
3. Check backend logs for processing errors
4. Verify service account has access to sheets

---

## Security Best Practices

- ✅ Always verify webhook signature
- ✅ Use HTTPS for webhook URL
- ✅ Keep webhook secret secure
- ✅ Log all webhook events for audit
- ✅ Return 200 OK even on errors (to acknowledge receipt)
- ✅ Process webhooks idempotently (handle duplicates)

---

## Next Steps

After completing webhook setup:

1. Test end-to-end flow in Test Mode
2. Verify access is granted correctly
3. Test access revocation
4. Switch to Live Mode
5. Monitor webhook deliveries in production

Proceed to [Deployment Guide](./DEPLOYMENT.md) for production deployment instructions.
