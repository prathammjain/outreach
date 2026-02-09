# Google Cloud Setup Guide

This guide walks you through setting up a Google Service Account and configuring Google Sheets for access control.

## Prerequisites

- Google account
- Google Sheets that you want to protect
- Access to Google Cloud Console

---

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Enter project name (e.g., "sheets-access-control")
4. Click **Create**
5. Wait for project creation to complete

---

## Step 2: Enable Google Drive API

1. In the Google Cloud Console, select your project
2. Go to **APIs & Services** → **Library**
3. Search for "Google Drive API"
4. Click on **Google Drive API**
5. Click **Enable**
6. Wait for the API to be enabled

---

## Step 3: Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Fill in the details:
   - **Service account name**: `sheets-access-manager`
   - **Service account ID**: (auto-generated)
   - **Description**: "Service account for managing Google Sheets access"
4. Click **Create and Continue**
5. Skip the optional steps (Grant access, Grant users access)
6. Click **Done**

---

## Step 4: Create Service Account Key

1. In the **Credentials** page, find your service account
2. Click on the service account email
3. Go to the **Keys** tab
4. Click **Add Key** → **Create new key**
5. Select **JSON** format
6. Click **Create**
7. The JSON file will download automatically
8. **IMPORTANT**: Rename this file to `service-account.json` and keep it secure
9. Move this file to your backend directory: `/Users/pratham/Desktop/outreach/backend/service-account.json`

> [!CAUTION]
> **Never commit this file to version control!** Add `service-account.json` to your `.gitignore`.

---

## Step 5: Share Google Sheets with Service Account

1. Open the downloaded `service-account.json` file
2. Copy the `client_email` value (looks like: `sheets-access-manager@project-id.iam.gserviceaccount.com`)
3. Open your **Indian Sheet** in Google Sheets
4. Click **Share** button
5. Paste the service account email
6. Set permission to **Editor** (required for managing permissions)
7. **Uncheck** "Notify people"
8. Click **Share**
9. Repeat steps 3-8 for your **YC Sheet**

> [!IMPORTANT]
> The service account needs **Editor** access to manage permissions, but it will only grant **Viewer** access to buyers.

---

## Step 6: Configure Sheet Settings (Critical)

For **each sheet** (Indian Sheet and YC Sheet):

### Disable Downloads and Copying

1. Open the sheet
2. Click **File** → **Share** → **Share with others**
3. Click the **Settings** gear icon (⚙️)
4. **Uncheck** the following:
   - ❌ Viewers and commenters can see the option to download, print, and copy
   - ❌ Editors can change permissions and share
5. Click **Done**

### Verify Settings

- Downloads: **Disabled** ✅
- Printing: **Disabled** ✅
- Copying: **Disabled** ✅
- Public access: **Restricted** ✅
- Link sharing: **Off** ✅

> [!WARNING]
> These settings prevent users from downloading or copying the sheet, but **cannot prevent screenshots**. This is an OS-level limitation that no system can prevent.

---

## Step 7: Get Sheet IDs

For each sheet:

1. Open the Google Sheet
2. Look at the URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
3. Copy the `SHEET_ID` portion
4. Save these IDs for your `.env` file:
   - `INDIAN_SHEET_ID`: Your Indian Sheet ID
   - `YC_SHEET_ID`: Your YC Sheet ID

**Example URL:**
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                      ↑_____________SHEET_ID_____________↑
```

---

## Step 8: Test Service Account Access

1. Go to your Google Sheet
2. Click **Share**
3. Verify the service account email is listed with **Editor** access
4. Try opening the sheet while logged into the service account email
   - You should see "Access Denied" (this is correct - service accounts can't browse)
   - The service account can only access via API

---

## Troubleshooting

### "Permission denied" when granting access

**Solution**: Ensure the service account has **Editor** access to the sheet, not just Viewer.

### Service account email not found

**Solution**: Make sure you enabled the Google Drive API and created the service account in the correct project.

### Downloads still enabled

**Solution**: Double-check the sheet settings. You must disable downloads for **each individual sheet**.

---

## Security Checklist

- ✅ Service account JSON file is secure and not committed to git
- ✅ Service account has Editor access to sheets
- ✅ Downloads, printing, and copying are disabled on sheets
- ✅ Public access is disabled
- ✅ Link sharing is disabled
- ✅ Only email-based access is allowed

---

## Next Steps

After completing this setup:

1. Update your `.env` file with the sheet IDs
2. Ensure `service-account.json` is in the backend directory
3. Proceed to [Razorpay Setup](./RAZORPAY_SETUP.md)
