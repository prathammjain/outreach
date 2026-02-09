# Railway Deployment Guide for OutreachKit Backend

Follow these steps to deploy your backend to Railway.

## Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click "Login" → "Login with GitHub"
3. Authorize Railway to access your GitHub account

## Step 2: Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Find and select `prathammjain/outreach`
4. Railway will start deploying automatically

## Step 3: Configure Environment Variables

Once deployed, click on your project, then go to "Variables" tab and add these:

```
RAZORPAY_WEBHOOK_SECRET=<leave empty for now, will add after webhook creation>
TIER_1_PRICE=110000
TIER_2_PRICE=199900
DATABASE_URL=sqlite:///./payments.db
INDIAN_SHEET_ID=<your Google Sheet ID>
YC_SHEET_ID=<your Google Sheet ID>
```

## Step 4: Add Google Service Account Credentials

You have two options:

### Option A: Base64 Encoding (Recommended)

1. First, create your Google Service Account (see GOOGLE_SETUP.md)
2. Download the `service-account.json` file
3. Convert to Base64:
   ```bash
   base64 -i service-account.json | pbcopy
   ```
4. In Railway, add variable:
   ```
   GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=<paste the base64 string>
   ```

### Option B: Upload File (Alternative)

1. In Railway, go to "Settings" → "Volumes"
2. Create a volume
3. Upload `service-account.json`
4. Add variable:
   ```
   GOOGLE_SERVICE_ACCOUNT_FILE=/app/service-account.json
   ```

## Step 5: Get Your Backend URL

1. In Railway, go to "Settings" → "Networking"
2. Click "Generate Domain"
3. Copy the URL (e.g., `https://outreach-production.up.railway.app`)

## Step 6: Test Your Backend

Visit: `https://your-app.railway.app/health`

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  "service": "operational"
}
```

## Step 7: Configure Razorpay Webhook

1. Go to Razorpay Dashboard → Settings → Webhooks
2. Click "Create Webhook"
3. **Webhook URL**: `https://your-app.railway.app/razorpay/webhook`
4. **Events**: Select only `payment.captured`
5. Click "Create"
6. **Copy the webhook secret**
7. Go back to Railway → Variables
8. Add: `RAZORPAY_WEBHOOK_SECRET=whsec_xxxxx`

## Step 8: Test End-to-End

1. Visit your Vercel frontend
2. Click "Get Database"
3. Use test card: `4111 1111 1111 1111`
4. Enter your real email
5. Complete payment
6. Check Railway logs to see webhook received
7. Check your email for Google access notification

## Troubleshooting

### Build fails

Check Railway logs. Common issues:
- Missing `requirements.txt` in backend folder
- Python version incompatibility

### Health check fails

- Check environment variables are set
- Check Railway logs for errors

### Webhook not working

- Verify webhook URL is correct
- Check webhook secret matches
- Check Railway logs for signature errors

## Next Steps

After successful deployment:
- Monitor Railway logs for first few payments
- Test access granting works
- Switch to Razorpay Live Mode when ready
