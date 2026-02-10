# Quick Setup Checklist

## ✅ Completed
- [x] Frontend integrated with Razorpay
- [x] Backend code complete
- [x] Pushed to GitHub
- [x] Railway deployment configured

## 🔄 In Progress
- [ ] Railway deployment succeeding
- [ ] Environment variables configured
- [ ] Google Service Account setup
- [ ] Razorpay webhook configured

## 📋 Next Steps (After Railway Deploys)

### 1. Add Basic Environment Variables to Railway
```env
TIER_1_PRICE=110000
TIER_2_PRICE=199900
DATABASE_URL=sqlite:///./payments.db
```

### 2. Generate Railway Domain
Settings → Networking → Generate Domain

### 3. Set Up Google Service Account
See: [docs/GOOGLE_SETUP.md](file:///Users/pratham/Desktop/outreach/docs/GOOGLE_SETUP.md)

Quick steps:
- Create Google Cloud project
- Enable Google Drive API
- Create service account
- Download credentials
- Share sheets with service account email

### 4. Add Google Credentials to Railway
```bash
# Convert to Base64
base64 -i service-account.json | pbcopy

# Add to Railway
GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=<paste>
INDIAN_SHEET_ID=<sheet_id>
YC_SHEET_ID=<sheet_id>
```

### 5. Configure Razorpay Webhook
- Dashboard → Settings → Webhooks
- URL: `https://your-railway-url/razorpay/webhook`
- Event: `payment.captured`
- Copy secret → Add to Railway: `RAZORPAY_WEBHOOK_SECRET=whsec_xxx`

### 6. Test End-to-End
- Visit Vercel frontend
- Make test payment
- Verify access granted

## 🎯 Current Status
Waiting for Railway deployment to succeed with fixed configuration.
