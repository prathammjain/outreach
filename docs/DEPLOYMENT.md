# Deployment Guide

This guide covers deploying your FastAPI backend to production using Railway, Render, or Fly.io.

## Prerequisites

- Backend code ready
- Google Service Account JSON file
- Razorpay webhook secret
- Sheet IDs configured

---

## Option 1: Deploy to Railway (Recommended)

Railway offers simple deployment with automatic HTTPS and environment variable management.

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

Or use the web dashboard (easier for first-time users).

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **New Project**
4. Select **Deploy from GitHub repo**
5. Connect your repository (or create a new one)

### Step 3: Configure Environment Variables

In Railway dashboard:

1. Go to your project → **Variables**
2. Add the following variables:

```env
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
GOOGLE_SERVICE_ACCOUNT_FILE=/app/service-account.json
DATABASE_URL=sqlite:///./payments.db
TIER_1_PRICE=99900
TIER_2_PRICE=199900
INDIAN_SHEET_ID=your_indian_sheet_id
YC_SHEET_ID=your_yc_sheet_id
```

### Step 4: Upload Service Account File

Railway doesn't support file uploads directly. Use one of these methods:

**Method A: Base64 Encode (Recommended)**

1. Encode the service account JSON:
   ```bash
   base64 -i service-account.json
   ```

2. Add to Railway variables:
   ```env
   GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=<base64_encoded_content>
   ```

3. Update `google_drive_service.py` to decode:
   ```python
   import base64
   import json
   import os
   
   # In __init__ method:
   if os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON_BASE64'):
       json_content = base64.b64decode(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON_BASE64'))
       credentials_info = json.loads(json_content)
       self.credentials = service_account.Credentials.from_service_account_info(
           credentials_info,
           scopes=SCOPES
       )
   else:
       self.credentials = service_account.Credentials.from_service_account_file(
           service_account_file,
           scopes=SCOPES
       )
   ```

**Method B: Use Railway Volumes**

1. Create a volume in Railway
2. Upload `service-account.json` to the volume
3. Mount the volume to `/app/service-account.json`

### Step 5: Configure Start Command

In Railway, set the start command:

```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Railway automatically sets the `$PORT` variable.

### Step 6: Deploy

1. Push your code to GitHub
2. Railway automatically deploys
3. Get your public URL: `https://your-app.railway.app`
4. Update Razorpay webhook URL with this URL

---

## Option 2: Deploy to Render

### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### Step 2: Create Web Service

1. Click **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `sheets-access-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables

In Render dashboard, add environment variables (same as Railway).

### Step 4: Upload Service Account

Use the Base64 method described in Railway section.

### Step 5: Deploy

Render automatically deploys on git push.

---

## Option 3: Deploy to Fly.io

### Step 1: Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Create Fly App

```bash
cd backend
fly launch
```

Follow the prompts to create your app.

### Step 3: Configure fly.toml

Edit `fly.toml`:

```toml
app = "your-app-name"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

### Step 4: Set Secrets

```bash
fly secrets set RAZORPAY_WEBHOOK_SECRET=your_secret
fly secrets set TIER_1_PRICE=99900
fly secrets set TIER_2_PRICE=199900
fly secrets set INDIAN_SHEET_ID=your_sheet_id
fly secrets set YC_SHEET_ID=your_sheet_id
```

For service account, use Base64 method:

```bash
fly secrets set GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=$(base64 -i service-account.json)
```

### Step 5: Deploy

```bash
fly deploy
```

---

## Post-Deployment Checklist

### 1. Verify Health Check

```bash
curl https://your-app-url.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "service": "operational"
}
```

### 2. Test Webhook Endpoint

```bash
curl https://your-app-url.com/razorpay/webhook
```

Should return 401 (missing signature) - this is correct.

### 3. Update Razorpay Webhook URL

1. Go to Razorpay Dashboard → Webhooks
2. Update webhook URL to: `https://your-app-url.com/razorpay/webhook`
3. Save changes

### 4. Test End-to-End Flow

1. Make a test payment (Test Mode)
2. Check backend logs for webhook receipt
3. Verify database record created
4. Check buyer email for Google access notification
5. Verify sheet access works

---

## Database Persistence

### SQLite (Default)

SQLite stores data in a file (`payments.db`). For persistence:

**Railway**: Use Railway Volumes
**Render**: Use Render Disks
**Fly.io**: Use Fly Volumes

### Upgrade to PostgreSQL (Recommended for Production)

1. Create a PostgreSQL database in your platform
2. Update `DATABASE_URL` environment variable:
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```
3. Add `psycopg2-binary` to `requirements.txt`
4. Redeploy

---

## Monitoring and Logging

### View Logs

**Railway**: Dashboard → Deployments → Logs
**Render**: Dashboard → Logs
**Fly.io**: `fly logs`

### What to Monitor

- ✅ Webhook delivery success rate
- ✅ Payment processing errors
- ✅ Google API failures
- ✅ Database errors
- ✅ Response times

### Set Up Alerts

Configure alerts for:
- Webhook failures
- 500 errors
- High response times
- Database connection issues

---

## Security Hardening

### 1. Restrict CORS

Update `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)
```

### 2. Add Rate Limiting

Install:
```bash
pip install slowapi
```

Add to `main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
```

Add to webhook endpoint:
```python
@router.post("/webhook")
@limiter.limit("10/minute")
async def razorpay_webhook(...):
    ...
```

### 3. Protect Admin Endpoints

Add API key authentication to `/razorpay/revoke`:

```python
from fastapi import Header, HTTPException

async def verify_admin_key(x_admin_key: str = Header(...)):
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")

@router.post("/revoke", dependencies=[Depends(verify_admin_key)])
async def revoke_access(...):
    ...
```

---

## Scaling Considerations

### Current Architecture (Single Instance)

- ✅ Handles ~100 payments/day easily
- ✅ Low cost (₹0-₹500/month)
- ✅ Simple to maintain

### When to Scale

Scale when:
- Processing > 1000 payments/day
- Webhook response time > 2 seconds
- Database queries slow down

### Scaling Options

1. **Horizontal Scaling**: Add more instances (Railway/Render auto-scale)
2. **Database**: Migrate to PostgreSQL with connection pooling
3. **Caching**: Add Redis for frequently accessed data
4. **Queue**: Use Celery for async processing

---

## Backup and Recovery

### Database Backups

**SQLite**:
```bash
# Backup
cp payments.db payments.db.backup

# Restore
cp payments.db.backup payments.db
```

**PostgreSQL**: Use platform's automated backups

### Service Account Key

- Keep backup of `service-account.json` in secure location
- Store in password manager (1Password, LastPass)
- Never commit to git

---

## Troubleshooting

### Deployment fails

**Check**:
- Requirements.txt includes all dependencies
- Python version compatibility (3.9+)
- Build logs for errors

### Webhook not receiving requests

**Check**:
- URL is publicly accessible (not localhost)
- HTTPS is enabled
- Razorpay webhook URL is correct
- No firewall blocking requests

### Google API errors

**Check**:
- Service account JSON is correctly uploaded
- Service account has Editor access to sheets
- Google Drive API is enabled
- Credentials are not expired

### Database errors

**Check**:
- Database file has write permissions
- Volume/disk is mounted correctly
- Connection string is correct

---

## Cost Estimation

### Railway
- Free tier: 500 hours/month
- Paid: ~$5/month for hobby plan

### Render
- Free tier: Available with limitations
- Paid: ~$7/month for starter plan

### Fly.io
- Free tier: 3 shared VMs
- Paid: ~$5/month for small VM

**Total Monthly Cost**: ₹0-₹500 (depending on usage)

---

## Next Steps

After successful deployment:

1. ✅ Test with real payment (small amount)
2. ✅ Verify access granting works
3. ✅ Test access revocation
4. ✅ Monitor logs for 24 hours
5. ✅ Set up alerts
6. ✅ Document any custom configurations
7. ✅ Create runbook for common issues

Your system is now live! 🚀
