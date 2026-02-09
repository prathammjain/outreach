# Google Sheets Access Control Backend

FastAPI backend that manages Google Sheets access permissions based on Razorpay payment webhooks.

## 🎯 What This Does

- Listens for Razorpay payment webhooks
- Verifies payment authenticity
- Grants Google Sheets viewer access to buyer's email
- Enforces tier-based access (Tier 1 or Tier 2)
- Prevents downloads, copying, and public sharing
- Supports access revocation

## 🏗️ Architecture

```
Payment Flow:
User → Razorpay → Webhook → FastAPI → Google Drive API → Sheet Access
```

**Key Principle**: This system doesn't protect files—it protects permissions. All access control is delegated to Google Drive's native permission system.

## 📋 Prerequisites

- Python 3.9+
- Google Cloud account with service account
- Razorpay account
- Google Sheets to protect

## 🚀 Quick Start

### 1. Clone and Install

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required variables:
- `RAZORPAY_WEBHOOK_SECRET` - From Razorpay dashboard
- `GOOGLE_SERVICE_ACCOUNT_FILE` - Path to service account JSON
- `TIER_1_PRICE` - Price in paise (e.g., 99900 for ₹999)
- `TIER_2_PRICE` - Price in paise (e.g., 199900 for ₹1999)
- `INDIAN_SHEET_ID` - Google Sheet ID for Tier 1
- `YC_SHEET_ID` - Google Sheet ID for Tier 2

### 3. Set Up Google Service Account

Follow the detailed guide: [docs/GOOGLE_SETUP.md](../docs/GOOGLE_SETUP.md)

**Quick summary:**
1. Create Google Cloud project
2. Enable Google Drive API
3. Create service account
4. Download JSON credentials → save as `service-account.json`
5. Share your sheets with the service account email
6. Disable downloads/copying on sheets

### 4. Configure Razorpay Webhook

Follow the guide: [docs/RAZORPAY_SETUP.md](../docs/RAZORPAY_SETUP.md)

**Quick summary:**
1. Create webhook in Razorpay dashboard
2. Set URL to `https://your-backend/razorpay/webhook`
3. Select `payment.captured` event
4. Copy webhook secret to `.env`

### 5. Run Locally

```bash
uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`

**Test health check:**
```bash
curl http://localhost:8000/health
```

## 📦 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Environment config
│   ├── database.py             # SQLAlchemy setup
│   ├── models.py               # Payment model
│   ├── routers/
│   │   └── webhooks.py         # Webhook endpoints
│   └── services/
│       ├── razorpay_service.py      # Signature verification
│       ├── google_drive_service.py  # Permission management
│       └── payment_service.py       # Business logic
├── requirements.txt
├── .env.example
└── README.md
```

## 🔐 Security Features

- ✅ HMAC SHA256 webhook signature verification
- ✅ Constant-time signature comparison (prevents timing attacks)
- ✅ Email-based access control via Google
- ✅ No public links or downloadable files
- ✅ Idempotent payment processing (handles duplicates)
- ✅ Comprehensive logging for audit trail

## 🧪 Testing

### Test Webhook Locally (with ngrok)

1. Install ngrok: `brew install ngrok`
2. Expose local server:
   ```bash
   ngrok http 8000
   ```
3. Copy ngrok URL (e.g., `https://abc123.ngrok.io`)
4. Update Razorpay webhook URL to: `https://abc123.ngrok.io/razorpay/webhook`
5. Make a test payment in Razorpay Test Mode
6. Check logs for webhook receipt

### Test Payment Processing

Use Razorpay test cards:
- **Card**: 4111 1111 1111 1111
- **CVV**: Any 3 digits
- **Expiry**: Any future date
- **Email**: Your real email (to receive access notification)

## 📊 API Endpoints

### `GET /`
Health check

**Response:**
```json
{
  "status": "healthy",
  "service": "Google Sheets Access Control API",
  "version": "1.0.0"
}
```

### `POST /razorpay/webhook`
Razorpay payment webhook handler

**Headers:**
- `X-Razorpay-Signature`: Webhook signature

**Body:** Razorpay webhook payload

**Response:** `200 OK` (always, even on errors)

### `POST /razorpay/revoke`
Revoke access for an email (admin only)

**Body:**
```json
{
  "email": "user@example.com"
}
```

> ⚠️ **TODO**: Add API key authentication before using in production

## 🚢 Deployment

See detailed guide: [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md)

**Recommended platforms:**
- Railway (easiest)
- Render
- Fly.io

**Key steps:**
1. Deploy backend to platform
2. Set environment variables
3. Upload service account credentials (use Base64 encoding)
4. Update Razorpay webhook URL
5. Test end-to-end flow

## 🔧 Configuration

### Tier Pricing

Update in `.env`:
```env
TIER_1_PRICE=99900   # ₹999 in paise
TIER_2_PRICE=199900  # ₹1999 in paise
```

### Tier → Sheet Mapping

- **Tier 1**: Indian Sheet only
- **Tier 2**: Indian Sheet + YC Sheet

To change, edit `payment_service.py`:
```python
def get_sheet_ids_for_tier(self, tier: int) -> List[str]:
    if tier == 1:
        return [settings.indian_sheet_id]
    elif tier == 2:
        return [settings.indian_sheet_id, settings.yc_sheet_id]
```

## 📝 Database

**Default**: SQLite (`payments.db`)

**Schema:**
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    payment_id VARCHAR(255) UNIQUE,
    razorpay_order_id VARCHAR(255),
    email VARCHAR(255),
    amount INTEGER,
    product_tier INTEGER,
    granted_resources TEXT,  -- JSON array
    timestamp DATETIME
);
```

**Upgrade to PostgreSQL** (recommended for production):
1. Add `psycopg2-binary` to requirements.txt
2. Update `DATABASE_URL` to PostgreSQL connection string

## 🐛 Troubleshooting

### Webhook signature verification fails
- Check `RAZORPAY_WEBHOOK_SECRET` matches dashboard
- Ensure using correct secret for Test/Live mode

### Google API permission denied
- Verify service account has **Editor** access to sheets
- Check Google Drive API is enabled
- Ensure `service-account.json` is valid

### Access not granted
- Check backend logs for errors
- Verify email was collected during payment
- Confirm sheets are shared with service account

### Database errors
- Ensure write permissions on `payments.db`
- Check disk space
- Verify SQLAlchemy connection string

## 📚 Documentation

- [Google Cloud Setup](../docs/GOOGLE_SETUP.md) - Service account configuration
- [Razorpay Setup](../docs/RAZORPAY_SETUP.md) - Webhook configuration
- [Deployment Guide](../docs/DEPLOYMENT.md) - Production deployment

## 🎓 How It Works

1. **User pays** via Razorpay checkout (email required)
2. **Razorpay sends webhook** to `/razorpay/webhook`
3. **Backend verifies** signature using HMAC SHA256
4. **Determines tier** from payment amount
5. **Grants access** via Google Drive API
   - Adds buyer email as viewer
   - Google sends native access email
6. **Persists record** in database for audit

**Result**: User can only access sheets when logged into their Gmail. No downloads, no public sharing.

## 🔒 What's Protected (and What's Not)

### ✅ Protected
- Unauthorized access
- Public sharing
- Link-based access
- Downloads
- Printing
- Copying

### ❌ Not Protected (OS-level limitations)
- Screenshots
- Manual transcription
- Screen recording

**Mitigation**: Watermark sensitive data, log access, psychological deterrence.

## 💰 Cost

- **Hosting**: ₹0-₹500/month (Railway/Render free tier available)
- **Google Drive API**: Free (up to quota limits)
- **Razorpay**: 2% transaction fee only
- **Total**: Cheaper than Gumroad/Zapier after ~10 sales

## 🤝 Support

For issues:
1. Check logs: `uvicorn app.main:app --log-level debug`
2. Review troubleshooting section
3. Check Razorpay webhook delivery logs
4. Verify Google Cloud Console for API errors

## 📄 License

MIT

---

**Built with**: FastAPI, Google Drive API, Razorpay, SQLAlchemy
