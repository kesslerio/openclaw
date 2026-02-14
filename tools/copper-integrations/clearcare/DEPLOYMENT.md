# Deployment Guide: ClearCare Integration

**Platform:** Railway (recommended) or Render or DigitalOcean App Platform  
**Time to Deploy:** 30 minutes  
**Cost:** $5-15/month (scales automatically)

---

## Option 1: Deploy to Railway (Recommended - Easiest)

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
railway login
```

### Step 2: Create New Project

```bash
cd /home/ubuntu/clawd/integrations/clearcare
railway init
```

### Step 3: Add PostgreSQL Database

```bash
railway add --database postgresql
```

This automatically:

- Creates PostgreSQL instance
- Sets `DATABASE_URL` environment variable
- Configures connection pooling

### Step 4: Set Environment Variables

```bash
# Set all required env vars
railway variables set RETELL_API_KEY="your_key_here"
railway variables set RETELL_AGENT_ID="your_agent_id"
railway variables set TELEGRAM_BOT_TOKEN="your_token"
railway variables set ARVIND_TELEGRAM_ID="7372113399"
railway variables set TWILIO_ACCOUNT_SID="your_sid"
railway variables set TWILIO_AUTH_TOKEN="your_token"
railway variables set TWILIO_PHONE_NUMBER="+14697421095"
railway variables set ZAPIER_WEBHOOK_SECRET="$(openssl rand -hex 32)"
railway variables set CRON_SECRET="$(openssl rand -hex 32)"
```

### Step 5: Deploy

```bash
railway up
```

Railway will:

1. Build your app (install npm packages)
2. Run database migrations automatically
3. Start the server
4. Provide a public URL (e.g., `copper-ai-abc123.railway.app`)

### Step 6: Initialize Database

```bash
# Connect to Railway PostgreSQL
railway run psql $DATABASE_URL -f database-schema.sql
```

### Step 7: Set Up Cron Job (No-Show Prevention)

Railway has built-in cron support:

```bash
railway cron add "*/15 * * * *" "curl -X POST -H 'Authorization: Bearer $CRON_SECRET' https://copper-ai-abc123.railway.app/cron/no-show-prevention"
```

This runs every 15 minutes to check for upcoming visits.

### Step 8: Test

```bash
curl https://copper-ai-abc123.railway.app/health
```

Should return:

```json
{
  "status": "healthy",
  "timestamp": "2026-02-03T00:00:00.000Z",
  "version": "1.0.0"
}
```

**Done! 🎉**

Your webhook URL: `https://copper-ai-abc123.railway.app`

---

## Option 2: Deploy to Render

### Step 1: Create Account

Go to https://render.com and sign up (free tier available)

### Step 2: Create PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Name: `copper-ai-clearcare`
3. Plan: Free tier (sufficient for 5-10 agencies)
4. Click "Create Database"
5. Copy the "Internal Database URL"

### Step 3: Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repo (or use "Deploy a web service manually")
3. Name: `copper-ai-clearcare`
4. Environment: `Node`
5. Build Command: `npm install`
6. Start Command: `npm start`
7. Plan: Free tier (scales to Starter $7/mo when needed)

### Step 4: Set Environment Variables

In Render dashboard:

- Go to "Environment" tab
- Add all variables from `.env.example`
- Use the PostgreSQL Internal URL for `DATABASE_URL`

### Step 5: Deploy

Click "Create Web Service"

Render will:

1. Build your app
2. Start the server
3. Provide a public URL (e.g., `copper-ai.onrender.com`)

### Step 6: Initialize Database

```bash
# Get PostgreSQL connection string from Render dashboard
psql <your_render_postgres_url> -f database-schema.sql
```

### Step 7: Set Up Cron Job

Render has built-in cron jobs:

1. Go to "Cron Jobs" tab
2. Add new cron job:
   - Name: `no-show-prevention`
   - Schedule: `*/15 * * * *` (every 15 minutes)
   - Command: `curl -X POST -H "Authorization: Bearer $CRON_SECRET" https://copper-ai.onrender.com/cron/no-show-prevention`

**Done! 🎉**

---

## Option 3: Deploy to DigitalOcean App Platform

### Step 1: Install doctl CLI

```bash
# macOS
brew install doctl

# Linux
wget https://github.com/digitalocean/doctl/releases/download/v1.98.0/doctl-1.98.0-linux-amd64.tar.gz
tar xf doctl-*.tar.gz
sudo mv doctl /usr/local/bin
```

### Step 2: Authenticate

```bash
doctl auth init
```

### Step 3: Create PostgreSQL Database

```bash
doctl databases create copper-ai-db --engine pg --region nyc3 --size db-s-1vcpu-1gb
```

### Step 4: Create App

```bash
doctl apps create --spec app.yaml
```

**app.yaml:**

```yaml
name: copper-ai-clearcare
services:
  - name: api
    github:
      repo: your-username/copper-ai
      branch: main
      deploy_on_push: true
    build_command: npm install
    run_command: npm start
    environment_slug: node-js
    instance_count: 1
    instance_size_slug: basic-xxs
    http_port: 3000
    routes:
      - path: /
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${copper-ai-db.DATABASE_URL}
      - key: RETELL_API_KEY
        scope: RUN_TIME
        value: your_retell_key
    # ... add all other env vars

databases:
  - name: copper-ai-db
    engine: PG
    version: "15"
```

### Step 5: Deploy

```bash
doctl apps create-deployment <app-id>
```

**Done! 🎉**

---

## Post-Deployment Checklist

### 1. Test Webhooks

```bash
# Test EVV webhook
curl -X POST https://your-app-url.com/webhook/evv \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: <generate_signature>" \
  -d '{
    "event": "clock_in",
    "caregiver_phone": "+14697421001",
    "caregiver_name": "Maria Garcia",
    "client_name": "Mrs. Anderson",
    "timestamp": "2026-02-03T10:00:00Z"
  }'
```

### 2. Set Up Zapier Workflows

See `zapier-workflows.json` for pre-built workflows

### 3. Monitor Logs

```bash
# Railway
railway logs

# Render
# View in dashboard: https://dashboard.render.com

# DigitalOcean
doctl apps logs <app-id>
```

### 4. Set Up Alerts

Configure alerts for:

- Server downtime (UptimeRobot)
- Database connection errors (PagerDuty)
- Failed webhook calls (Sentry)

---

## Cost Breakdown

### Railway (Recommended)

- **Web Service:** $5/month (500 hours)
- **PostgreSQL:** $5/month (1GB storage)
- **Total:** $10/month for 5-10 agencies

### Render

- **Web Service:** Free tier (750 hours) or $7/month Starter
- **PostgreSQL:** Free tier (90 days) then $7/month
- **Total:** $0-14/month

### DigitalOcean

- **App Platform:** $5/month (Basic)
- **PostgreSQL:** $15/month (1GB RAM)
- **Total:** $20/month

---

## Scaling Guide

### 1-10 Agencies

- Free or basic tier ($0-15/month)
- Single server instance
- Shared database

### 10-50 Agencies

- Upgrade to $20-30/month
- Add read replica for database
- Enable auto-scaling (2-4 instances)

### 50-200 Agencies

- $100-200/month
- Multiple server instances (load balanced)
- Dedicated database with backups
- Add Redis cache for performance

### 200+ Agencies

- $500-1,000/month
- Kubernetes cluster (GKE/EKS)
- Multi-region deployment
- Dedicated support team

---

## Troubleshooting

### Database Connection Errors

```bash
# Check DATABASE_URL is set
railway variables get DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT NOW();"
```

### Webhook Not Receiving Events

- Check Zapier webhook URL is correct
- Verify webhook signature is set in Zapier
- Check server logs for errors
- Test with curl command

### Retell API Errors

- Verify RETELL_API_KEY is valid
- Check Retell dashboard for usage limits
- Ensure phone numbers are in E.164 format (+1...)

### Cron Job Not Running

- Check cron secret is set correctly
- Verify cron schedule syntax
- Test manually: `curl -X POST -H "Authorization: Bearer $CRON_SECRET" https://your-url/cron/no-show-prevention`

---

## Maintenance

### Daily

- [ ] Check logs for errors
- [ ] Monitor confirmation call success rate
- [ ] Review high-risk visits

### Weekly

- [ ] Review analytics (no-show rates, EVV compliance)
- [ ] Update caregiver phone numbers if changed
- [ ] Backup database manually (automated daily)

### Monthly

- [ ] Review server costs and optimize
- [ ] Update dependencies (`npm update`)
- [ ] Analyze ROI for each agency
- [ ] Collect testimonials from happy agencies

---

_Built with 🐾 by Nike | Questions? Ask in Telegram @SarinAI_bot_
