# Quick Start Guide - Unified Copper AI Server

**Get your production server running in 30 minutes**

---

## Prerequisites

- Node.js 18+ installed
- PostgreSQL database (or use Railway's managed database)
- Retell API key (for voice calls)
- Twilio account (for SMS)
- Telegram bot token (for alerts)

---

## Step 1: Deploy to Railway (10 minutes)

```bash
# Navigate to unified server
cd /home/ubuntu/clawd/integrations/unified-server

# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway init
# Name it: copper-ai-unified

# Add PostgreSQL database
railway add --database postgresql
```

---

## Step 2: Set Environment Variables (5 minutes)

```bash
# Copy values from your .env or password manager
railway variables set RETELL_API_KEY="sk_your_retell_key"
railway variables set RETELL_AGENT_ID="agent_your_id"
railway variables set TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
railway variables set ARVIND_TELEGRAM_ID="7372113399"
railway variables set TWILIO_ACCOUNT_SID="AC_your_twilio_sid"
railway variables set TWILIO_AUTH_TOKEN="your_twilio_token"
railway variables set TWILIO_PHONE_NUMBER="+14697421095"
railway variables set CRON_SECRET="$(openssl rand -hex 32)"
railway variables set ZAPIER_WEBHOOK_SECRET="$(openssl rand -hex 32)"
```

---

## Step 3: Deploy Server (5 minutes)

```bash
# Deploy to Railway
railway up

# Wait for deployment (usually 1-2 minutes)
railway status

# Get your server URL
railway domain
# Example: copper-ai-unified-production.up.railway.app
```

---

## Step 4: Initialize Database (5 minutes)

```bash
# Run database setup (ClearCare + Axxess schemas)
railway run npm run db:setup

# Verify tables created
railway run psql $DATABASE_URL -c "\dt"
# Should show: agencies, caregivers, visits, evv_logs, confirmation_calls, etc.
```

---

## Step 5: Set Up Cron Jobs (5 minutes)

### Option A: Railway Cron (if available)

```bash
# No-show prevention (every 15 minutes)
railway cron add "*/15 * * * *" "curl -X POST -H 'Authorization: Bearer $CRON_SECRET' https://your-app.railway.app/cron/no-show-prevention"

# Schedule sync (hourly, for Axxess)
railway cron add "0 * * * *" "curl -X POST -H 'Authorization: Bearer $CRON_SECRET' https://your-app.railway.app/cron/sync-schedules"
```

### Option B: External Cron (cron-job.org)

1. Go to https://cron-job.org (free account)
2. Create new cron job:
   - URL: `https://your-app.railway.app/cron/no-show-prevention`
   - Headers: `Authorization: Bearer YOUR_CRON_SECRET`
   - Schedule: Every 15 minutes
3. Create second job for schedule sync (hourly)

---

## Step 6: Test Your Server (5 minutes)

### Health Check

```bash
curl https://your-app.railway.app/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2026-02-03T03:00:00.000Z",
  "uptime": 45.2,
  "version": "1.0.0"
}
```

### Status Check

```bash
curl https://your-app.railway.app/api/status
```

Expected response:

```json
{
  "status": "operational",
  "platforms": [],
  "metrics": {
    "active_agencies": 0,
    "visits_today": 0,
    "evv_calls_today": 0
  }
}
```

### Platform List

```bash
curl https://your-app.railway.app/api/platforms
```

Should show ClearCare and Axxess as available platforms.

---

## Step 7: Add Your First Agency

### ClearCare Agency Example

```bash
# Connect to database
railway run psql $DATABASE_URL

# Insert agency
INSERT INTO agencies (name, owner_name, owner_phone, owner_email, platform, plan, monthly_price)
VALUES ('ABC Home Care', 'John Smith', '+14695551234', 'john@abchomecare.com', 'clearcare', 'beta', 0.00);

# Verify
SELECT id, name, platform FROM agencies;

# Exit
\q
```

### Axxess Agency Example

```bash
# (Get API credentials from Axxess support first)
railway run psql $DATABASE_URL

INSERT INTO agencies (
  name, owner_name, owner_phone, owner_email,
  platform, axxess_agency_id, axxess_client_id, axxess_client_secret,
  plan, monthly_price
)
VALUES (
  'XYZ Home Health', 'Jane Doe', '+14695555678', 'jane@xyzhomehealth.com',
  'axxess', 'AG-12345', 'your_client_id', 'your_client_secret',
  'beta', 0.00
);

\q
```

---

## Step 8: Onboard Caregivers

### For ClearCare (Manual CSV Import)

See: `../clearcare/ONBOARDING-CHECKLIST.md`

### For Axxess (Auto-Sync)

```bash
# Sync caregivers from Axxess API (replace 1 with your agency ID)
curl -X POST https://your-app.railway.app/api/axxess/sync-caregivers/1

# Expected response:
# {"success": true, "caregivers_synced": 47, "errors": 0, "total": 47}
```

---

## Step 9: Configure Webhooks

### For ClearCare (Zapier)

1. Create Zapier account (free tier)
2. Set up webhook URL: `https://your-app.railway.app/webhook/clearcare/evv`
3. Add webhook signature header:
   ```
   X-Webhook-Signature: <generate using ZAPIER_WEBHOOK_SECRET>
   ```
4. Follow: `../clearcare/ONBOARDING-CHECKLIST.md`

### For Axxess (Direct API)

No webhooks needed! Schedule sync runs automatically every hour via cron.

---

## Step 10: Monitor & Test

### View Logs

```bash
# Real-time logs
railway logs --tail

# Filter for errors
railway logs --filter="error"
```

### Test Voice EVV

Call your hotline number (configured in Retell): `(469) 420-CARE`

Say: "Hi, this is [Name]. I'm clocking in for [Client]."

Check logs for EVV event processing.

### Test Confirmation Calls

Wait for cron job to run (every 15 min) or trigger manually:

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_CRON_SECRET" \
  https://your-app.railway.app/cron/no-show-prevention
```

---

## Next Steps

1. **ClearCare Agencies:** Follow `../clearcare/ONBOARDING-CHECKLIST.md`
2. **Axxess Agencies:** Follow `../axxess/ONBOARDING-CHECKLIST.md`
3. **Monitor:** Check `/api/status` daily
4. **Scale:** Add more agencies (same server handles all!)

---

## Troubleshooting

### "Database connection failed"

```bash
# Check DATABASE_URL
railway variables get DATABASE_URL

# Test connection
railway run psql $DATABASE_URL -c "SELECT 1;"
```

### "Retell API error"

```bash
# Verify API key
railway variables get RETELL_API_KEY

# Test with curl
curl https://api.retellai.com/v2/list-agents \
  -H "Authorization: Bearer YOUR_RETELL_KEY"
```

### "Cron not running"

```bash
# Check cron secret matches
railway variables get CRON_SECRET

# Test manually
curl -X POST \
  -H "Authorization: Bearer YOUR_CRON_SECRET" \
  https://your-app.railway.app/cron/no-show-prevention

# Check logs
railway logs --filter="cron"
```

---

## Cost Estimate

**Railway Pricing:**

- Web Service: $5/mo (500 hours)
- PostgreSQL: $5/mo (1GB storage)
- **Total: $10/mo** (handles unlimited agencies!)

**Additional Services:**

- Retell API: $0.10-0.15/min (pay-as-you-go)
- Twilio SMS: $0.0075/SMS (pay-as-you-go)
- Telegram: Free

**Example Monthly Cost (10 agencies, 500 calls/day):**

- Railway: $10
- Retell: ~$150 (500 calls/day × 30 sec × $0.10/min)
- Twilio: ~$10 (100 SMS/month)
- **Total: ~$170/month** for 10 agencies = $17/agency/month (infrastructure only)

---

## Support

- **Documentation:** See README.md and DEPLOYMENT.md
- **Issues:** Check logs with `railway logs --tail`
- **Questions:** Contact Arvind or Nike via Telegram

---

_Built with 🐾 by Nike | Deploy in 30 minutes, scale to thousands of agencies_
