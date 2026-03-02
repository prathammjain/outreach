# Frontend Setup Guide

This guide explains how to configure and deploy the OutreachKit frontend with Razorpay payment integration.

## Overview

The frontend is a static HTML landing page that integrates with Razorpay for payments. When a user completes payment, Razorpay automatically sends a webhook to your backend, which grants Google Sheets access.

---

## Configuration

### Step 1: Get Razorpay Key ID

1. Log in to [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Go to **Settings** → **API Keys**
3. Copy your **Key ID**:
   - **Test Mode**: `rzp_test_xxxxx`
   - **Live Mode**: `rzp_live_xxxxx`

### Step 2: Update index.html

Open `index.html` and find this line (around line 652):

```javascript
const RAZORPAY_KEY_ID = 'rzp_test_YOUR_KEY_ID';
```

Replace with your actual Key ID:

**For Testing:**
```javascript
const RAZORPAY_KEY_ID = 'rzp_test_abc123xyz';
```

**For Production:**
```javascript
const RAZORPAY_KEY_ID = 'rzp_live_abc123xyz';
```

> [!IMPORTANT]
> Use **Test Mode** key for testing, **Live Mode** key for production. Never mix them.

---

## How It Works

### Payment Flow

1. **User clicks "Get Database"** button
2. **Razorpay checkout modal opens**
   - User enters email (mandatory)
   - User enters payment details
3. **Payment processed** by Razorpay
4. **Razorpay sends webhook** to your backend
5. **Backend grants access** via Google Drive API
6. **User receives email** from Google with access link
7. **Success modal shows** on frontend

### What Happens on Frontend

```javascript
function handlePurchase(tier) {
    // Opens Razorpay checkout
    const rzp = new Razorpay({
        key: RAZORPAY_KEY_ID,
        amount: 110000,  // ₹1,100 in paise
        currency: 'INR',
        name: 'OutreachKit',
        // ... email collection
    });
    rzp.open();
}
```

### What Happens on Backend

- Webhook receives payment notification
- Verifies signature
- Grants Google Sheets access to buyer's email
- Sends confirmation

---

## Pricing Configuration

Current pricing (already configured):

```javascript
const PRICING = {
    tier1: {
        amount: 110000,  // ₹1,100 in paise
        name: 'Indian Startups Database'
    },
    tier2: {
        amount: 239900,  // ₹2,399 in paise
        name: 'Complete Database (YC + Indian)'
    }
};
```

> [!NOTE]
> Razorpay amounts are in **paise** (smallest currency unit). ₹1,100 = 110000 paise.

### To Change Pricing

1. **Update frontend** (`index.html`):
   ```javascript
   tier1: { amount: 110000 }  // Change this
   ```

2. **Update backend** (`.env`):
   ```env
   TIER_1_PRICE=110000  # Must match frontend
   ```

3. **Update display prices** in HTML:
   - Line 535: `<span class="price-currency">₹</span>1,100`
   - Line 577: `<span class="price-currency">₹</span>2,399`

---

## Testing Locally

### 1. Open in Browser

```bash
cd /Users/pratham/Desktop/outreach
open index.html
```

Or use a local server:

```bash
python3 -m http.server 8080
# Visit http://localhost:8080
```

### 2. Test Payment Flow

1. Click "Get Indian Database" or "Get Complete Database"
2. Razorpay modal should open
3. Enter test email: `test@example.com`
4. Use Razorpay test card:
   - **Card**: `4111 1111 1111 1111`
   - **CVV**: `123`
   - **Expiry**: Any future date
5. Complete payment
6. Success modal should appear

> [!WARNING]
> Local testing won't trigger the webhook (backend must be publicly accessible). Use ngrok for full testing.

---

## Deployment

### Option 1: Vercel (Recommended)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   cd /Users/pratham/Desktop/outreach
   vercel
   ```

3. **Follow prompts:**
   - Project name: `outreachkit`
   - Framework: None (static)
   - Build command: (leave empty)
   - Output directory: `./`

4. **Get deployment URL:**
   ```
   https://outreachkit.vercel.app
   ```

### Option 2: Netlify

1. Go to [netlify.com](https://netlify.com)
2. Drag and drop `index.html` to deploy
3. Get deployment URL

### Option 3: GitHub Pages

1. Create GitHub repository
2. Push `index.html`
3. Enable GitHub Pages in settings
4. Access at `https://username.github.io/repo-name`

---

## Email Collection (Critical)

The Razorpay integration **requires email** for the webhook to work:

```javascript
prefill: {
    email: '',      // Empty = user must enter
    contact: ''
},
readonly: {
    email: false,   // Allow editing
    contact: false
}
```

> [!CAUTION]
> **Do NOT** set `readonly.email: true` or the user won't be able to enter their email, and access won't be granted.

---

## Customization

### Change Brand Colors

In `index.html`, update CSS variables (line 17-30):

```css
:root {
    --accent: #00ff88;      /* Change to your brand color */
    --accent-dim: #00cc6a;  /* Darker shade */
    --bg: #0a0a0a;          /* Background */
}
```

### Add Logo

Update Razorpay options (line 680):

```javascript
image: 'https://yoursite.com/logo.png',  // Add logo URL
```

### Change Success Message

Edit `showSuccessMessage()` function (line 715):

```javascript
modal.innerHTML = `
    <h2>Custom Success Message!</h2>
    <p>Your custom instructions...</p>
`;
```

---

## Troubleshooting

### Razorpay modal doesn't open

**Check:**
- Is `RAZORPAY_KEY_ID` set correctly?
- Is Razorpay SDK loaded? (Check browser console)
- Are there JavaScript errors?

**Solution:**
```javascript
// Add console log to debug
console.log('Razorpay Key:', RAZORPAY_KEY_ID);
```

### Payment succeeds but no access granted

**Check:**
- Is backend webhook URL configured in Razorpay?
- Is backend running and publicly accessible?
- Check backend logs for errors

**Solution:**
- Verify webhook URL in Razorpay dashboard
- Test webhook delivery in Razorpay logs

### Email not collected

**Check:**
- Is `readonly.email` set to `false`?
- Is `prefill.email` empty?

**Solution:**
```javascript
prefill: { email: '' },  // Must be empty
readonly: { email: false }  // Must be false
```

### Wrong amount charged

**Check:**
- Frontend `PRICING` amounts match backend `.env`
- Amounts are in paise (multiply by 100)

**Solution:**
```javascript
// ₹1,100 = 110000 paise
tier1: { amount: 110000 }
```

---

## Security Considerations

### What's Safe to Expose

✅ Razorpay Key ID (public key)
✅ Pricing information
✅ Product descriptions

### What to Keep Secret

❌ Razorpay Key Secret (never in frontend)
❌ Webhook secret (backend only)
❌ Google service account credentials

> [!WARNING]
> **Never** put Razorpay Key Secret in frontend code. Only use Key ID.

---

## Testing Checklist

Before going live:

- [ ] Razorpay Key ID updated (Test Mode)
- [ ] Payment modal opens correctly
- [ ] Email field is editable
- [ ] Test payment completes successfully
- [ ] Success modal appears
- [ ] Backend webhook receives payment
- [ ] Google Sheets access granted
- [ ] Buyer receives Google email
- [ ] Switch to Live Mode Key ID
- [ ] Test with real payment (small amount)
- [ ] Verify end-to-end flow works

---

## Going Live

### 1. Switch to Live Mode

**Frontend:**
```javascript
const RAZORPAY_KEY_ID = 'rzp_live_xxxxx';  // Change from test to live
```

**Backend:**
- Update webhook secret to Live Mode secret
- Redeploy backend

**Razorpay:**
- Create new webhook for Live Mode
- Point to production backend URL

### 2. Deploy Frontend

```bash
vercel --prod
```

### 3. Update Razorpay Webhook

1. Go to Razorpay Dashboard (Live Mode)
2. Settings → Webhooks
3. Update webhook URL to production backend
4. Test with small real payment

### 4. Monitor

- Check Razorpay dashboard for payments
- Monitor backend logs for webhook deliveries
- Verify access grants are working

---

## Support

For issues:

1. **Payment Issues**: Check Razorpay dashboard logs
2. **Access Issues**: Check backend logs
3. **Frontend Issues**: Check browser console

**Contact**: sleektechventures@gmail.com

---

## Next Steps

After frontend is deployed:

1. ✅ Test payment flow end-to-end
2. ✅ Verify Google Sheets access works
3. ✅ Monitor first few real payments
4. ✅ Set up analytics (Google Analytics, etc.)
5. ✅ Add customer support email
6. ✅ Create refund policy page

Your frontend is ready to accept payments! 🚀
