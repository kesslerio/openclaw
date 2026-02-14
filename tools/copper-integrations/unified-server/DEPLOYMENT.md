# Unified Server Deployment Guide

**One Server for All Platforms - Deploy in 30 Minutes**

---

## Quick Start (Railway - Recommended)

```bash
# 1. Navigate to unified server directory
cd /home/ubuntu/openclaw/tools/copper-integrations/unified-server

# 2. Install Railway CLI (if not already installed)
npm install -g @railway/cli
railway login

# 3. Create new project
railway init

# 4. Add PostgreSQL database
railway add --database postgresql

# 5. Set environment variables
railway variables set RETELL_API_KEY="your_retell_key"
railway variables set RETELL_AGENT_ID="your_agent_id"
railway variables set TELEGRAM_BOT_TOKEN="your_telegram_token"
railway variables set ARVIND_TELEGRAM_ID="7372113399"
railway variables set TWILIO_ACCOUNT_SID="your_twilio_sid"
railway variables set TWILIO_AUTH_TOKEN="your_twilio_token"
railway variables set TWILIO_PHONE_NUMBER="+14697421095"
railway variables set CRON_SECRET="$(openssl rand -hex 32)"

# 6. Deploy server
railway up

# 7. Initialize database (run both ClearCare + Axxess schemas)
railway run npm run db:setup

# 8. Get your public URL
railway status
```

**Your unified server is now live!** 🎉

**Cost:** $10/mo (includes PostgreSQL + web server for ALL platforms)

---

## Environment Variables

Required for all platforms:

```bash
DATABASE_URL=<auto-set by Railway>
RETELL_API_KEY=<your Retell API key>
RETELL_AGENT_ID=<your Retell agent ID>
TWILIO_ACCOUNT_SID=<your Twilio SID>
TWILIO_AUTH_TOKEN=<your Twilio token>
TWILIO_PHONE_NUMBER=+14697421095
TELEGRAM_BOT_TOKEN=<your Telegram bot token>
ARVIND_TELEGRAM_ID=7372113399
CRON_SECRET=<random 32-character secret>
```

Platform-specific (optional, per-agency):

```bash
AXXESS_API_URL=https://api.axxess.com/v1
```

---

## Setting Up Cron Jobs

### Railway Cron

```bash
# No-show prevention (every 15 minutes)
railway cron add "*/15 * * * *" \
  "curl -X POST -H 'Authorization: Bearer $CRON_SECRET' \
  https://your-app.railway.app/cron/no-show-prevention"

# Schedule sync (every hour, Axxess only)
railway cron add "0 * * * *" \
  "curl -X POST -H 'Authorization: Bearer $CRON_SECRET' \
  https://your-app.railway.app/cron/sync-schedules"
```

### External Cron (if Railway doesn't support)

Use cron-job.org or EasyCron:

1. Create account at cron-job.org
2. Add new cron job
3. URL: `https://your-app.railway.app/cron/no-show-prevention`
4. Headers: `Authorization: Bearer YOUR_CRON_SECRET`
5. Schedule: Every 15 minutes

---

## Onboarding Agencies

### ClearCare Agency

1. Add agency to database:

```sql
INSERT INTO agencies (name, owner_phone, platform, plan)
VALUES ('ABC Home Care', '+14695551234', 'clearcare', 'beta');
```

2. Follow: `../clearcare/ONBOARDING-CHECKLIST.md`
3. Point Zapier webhooks to: `https://your-app/webhook/clearcare/*`

### Axxess Agency

1. Get API credentials from Axxess support
2. Add agency to database:

```sql
INSERT INTO agencies (name, owner_phone, platform, axxess_agency_id, axxess_client_id, axxess_client_secret, plan)
VALUES ('XYZ Home Health', '+14695555678', 'axxess', 'AG-12345', 'client_id_here', 'client_secret_here', 'beta');
```

3. Follow: `../axxess/ONBOARDING-CHECKLIST.md`

---

## Testing

### Health Check

```bash
curl https://your-app.railway.app/health
```

Expected:

```json
{
  "status": "healthy",
  "timestamp": "2026-02-03T02:00:00.000Z",
  "uptime": 123.45,
  "version": "1.0.0"
}
```

### Status

```bash
curl https://your-app.railway.app/api/status
```

Expected:

```json
{
  "status": "operational",
  "platforms": [
    { "platform": "clearcare", "count": "2" },
    { "platform": "axxess", "count": "3" }
  ],
  "metrics": {
    "active_agencies": 5,
    "visits_today": 47,
    "evv_calls_today": 23
  }
}
```

---

## Monitoring

### Logs

```bash
# Real-time logs
railway logs --tail

# Specific time range
railway logs --since 1h
```

### Metrics

Access at: `https://your-app.railway.app/api/status`

Key metrics:

- Active agencies by platform
- Visits today
- EVV calls today
- Confirmation calls today

### Alerts

Automatic alerts sent to:

- Telegram: High-risk no-shows, platform errors
- SMS: Agency-specific no-show alerts

---

## Scaling

The unified server is designed to scale efficiently:

### Vertical Scaling (Railway)

- Railway auto-scales RAM/CPU based on load
- No configuration needed

### Horizontal Scaling (for 100+ agencies)

1. Deploy multiple instances
2. Add load balancer (Railway handles this)
3. Use connection pooling (already configured)

### Database Scaling

- Add read replica for analytics queries
- Railway provides this as an add-on

---

## Migrating from Separate Servers

If you already deployed ClearCare and Axxess separately:

```bash
# 1. Export data
pg_dump $CLEARCARE_DB_URL > clearcare_backup.sql
pg_dump $AXXESS_DB_URL > axxess_backup.sql

# 2. Merge data (be careful with duplicate IDs)
# ... (manual merge or use ETL tool)

# 3. Point webhooks to unified server
# Update Zapier (ClearCare)
# Update API configs (Axxess agencies)

# 4. Test thoroughly
# Run test EVV call for each platform
# Verify webhooks working

# 5. Decommission old servers
railway delete <old-clearcare-project>
railway delete <old-axxess-project>
```

---

## Troubleshooting

### "Database connection failed"

- Check `DATABASE_URL` is set correctly
- Verify PostgreSQL service is running
- Test connection: `railway run psql $DATABASE_URL -c "SELECT 1;"`

### "Platform error: Axxess API authentication failed"

- Check agency has valid `axxess_client_id` and `axxess_client_secret`
- Verify credentials with: `SELECT * FROM agencies WHERE platform = 'axxess';`
- Test manually: `node lib/axxess-api.js`

### "No-show prevention cron not running"

- Verify cron secret matches: `railway variables get CRON_SECRET`
- Check cron logs: `railway logs --filter="no-show-prevention"`
- Test manually: `curl -X POST -H "Authorization: Bearer $CRON_SECRET" https://your-app/cron/no-show-prevention`

---

## Cost Breakdown

### Railway (Recommended)

- Web Service: $5/mo (500 hours)
- PostgreSQL: $5/mo (1GB storage)
- **Total: $10/mo** for unlimited agencies across all platforms

### Render

- Web Service: $7/mo
- PostgreSQL: $7/mo
- **Total: $14/mo**

### DigitalOcean

- App Platform: $5/mo
- PostgreSQL: $15/mo
- **Total: $20/mo**

**Nike's Recommendation:** Railway ($10/mo) - best value, easiest deployment

---

_Built with 🐾 by Nike | Questions? Telegram @SarinAI_bot_
