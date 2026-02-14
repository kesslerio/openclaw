# Unified Copper AI Integration Server

**One Server, Multiple Platforms (ClearCare + Axxess + Future)**

_Created: Feb 3, 2026 | Nike_

---

## Overview

This is the **production deployment** for Copper AI integrations. Instead of running separate servers for ClearCare and Axxess, this unified server handles BOTH platforms (and future integrations) in a single Node.js application.

**Benefits:**

- ✅ **Lower cost:** $10/mo for ALL integrations (vs $10/mo per platform)
- ✅ **Easier maintenance:** One codebase, one deployment, one database
- ✅ **Shared resources:** Database connections, voice AI, alerts all reused
- ✅ **Better monitoring:** Single dashboard for all platforms
- ✅ **Faster onboarding:** Add new platforms without new infrastructure

**Platforms Supported:**

- ✅ ClearCare (4,500 agencies, Zapier-based)
- ✅ Axxess (7,000 agencies, direct API)
- 🔜 Wellsky Personal Care (future)
- 🔜 MatrixCare (future)
- 🔜 AlayaCare (future)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Unified Copper AI Integration Server           │
│                  (Node.js/Express)                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  ClearCare   │  │    Axxess    │  │   Future     │ │
│  │   Routes     │  │   Routes     │  │   Platforms  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                 │                  │         │
│         └─────────────────┴──────────────────┘         │
│                          │                             │
│              ┌───────────┴───────────┐                 │
│              │  Shared Services      │                 │
│              │  - Voice AI (Retell)  │                 │
│              │  - Database (PG)      │                 │
│              │  - Alerts (Telegram)  │                 │
│              │  - Analytics          │                 │
│              └───────────────────────┘                 │
└─────────────────────────────────────────────────────────┘
         │                    │                  │
         ▼                    ▼                  ▼
    Zapier/Email         Axxess API        Future APIs
    (ClearCare)          (Direct)
```

---

## Features

### Multi-Platform Support

- Automatic platform detection (based on webhook endpoint or agency config)
- Platform-specific logic encapsulated in modules
- Shared database with platform-agnostic schema

### Single Deployment

- Deploy once to Railway/Render
- Handles unlimited agencies across all platforms
- Auto-scales based on total load

### Unified Analytics

- Compare ClearCare vs Axxess performance
- Cross-platform insights (which platform has better no-show reduction?)
- Single dashboard for all agencies

---

## Endpoints

### Health & Status

- `GET /health` - Server health check
- `GET /api/status` - Detailed status (uptime, platforms, agencies)
- `GET /api/platforms` - List supported platforms

### ClearCare (Zapier-based)

- `POST /webhook/clearcare/evv` - Voice EVV clock in/out
- `POST /webhook/clearcare/new-visit` - New visit assigned
- `POST /webhook/clearcare/confirmation` - Confirmation call result

### Axxess (Direct API)

- `POST /webhook/axxess/evv` - Voice EVV clock in/out
- `POST /api/axxess/sync-schedule/:agencyId` - Manual schedule sync
- `POST /api/axxess/sync-caregivers/:agencyId` - Manual caregiver sync
- `GET /api/axxess/status/:agencyId` - Agency API status

### Shared Endpoints

- `POST /cron/no-show-prevention` - Scheduled confirmation calls (all platforms)
- `POST /cron/sync-schedules` - Sync schedules from all platforms
- `GET /api/analytics/:agencyId` - Agency analytics
- `GET /api/analytics/compare` - Platform comparison

---

## Database Schema

Same schema as `integrations/clearcare/database-schema.sql` + `integrations/axxess/database-migrations.sql`.

**Key tables:**

- `agencies` - Platform column: 'clearcare', 'axxess', 'both'
- `caregivers` - Both `clearcare_caregiver_id` and `axxess_caregiver_id`
- `visits` - Both `clearcare_visit_id` and `axxess_visit_id`, `synced_from` column

**Analytics views:**

- `platform_comparison` - ClearCare vs Axxess metrics
- `daily_no_show_rates` - Per-platform breakdown
- `agency_roi` - ROI by platform

---

## Deployment

### Option 1: Railway (Recommended)

```bash
# Clone repo
cd /home/ubuntu/clawd/integrations/unified-server

# Install Railway CLI
npm install -g @railway/cli
railway login

# Create project
railway init

# Add PostgreSQL
railway add --database postgresql

# Set environment variables
railway variables set RETELL_API_KEY="..."
railway variables set AXXESS_CLIENT_ID="..."
# ... (see .env.example)

# Deploy
railway up

# Initialize database
railway run npm run db:setup
```

**Cost:** $10/mo (includes PostgreSQL + web server for ALL platforms)

### Option 2: Render

1. Connect GitHub repo
2. Create PostgreSQL database
3. Create Web Service (Node.js)
4. Set environment variables
5. Deploy

**Cost:** $7/mo web service + $7/mo database = $14/mo total

---

## Adding New Agencies

### ClearCare Agency

```sql
INSERT INTO agencies (name, owner_phone, platform, plan)
VALUES ('ABC Home Care', '+14695551234', 'clearcare', 'beta');
```

Follow onboarding: `integrations/clearcare/ONBOARDING-CHECKLIST.md`

### Axxess Agency

```sql
INSERT INTO agencies (name, owner_phone, platform, axxess_agency_id, axxess_client_id, axxess_client_secret, plan)
VALUES ('XYZ Home Health', '+14695555678', 'axxess', 'AG-12345', 'client_id', 'client_secret', 'beta');
```

Follow onboarding: `integrations/axxess/ONBOARDING-CHECKLIST.md`

---

## Monitoring

### Logs

```bash
# Railway
railway logs --tail

# Render
# View in dashboard
```

### Metrics

- Total API calls (ClearCare + Axxess)
- Voice EVV calls by platform
- Confirmation call success rate by platform
- No-show reduction by platform

### Alerts

- API errors (Telegram/SMS)
- High no-show rates (Telegram/SMS)
- Database connection issues (Sentry)

---

## Scaling

### 1-20 Agencies

- Single server instance
- Shared database
- **Cost:** $10-15/mo

### 20-100 Agencies

- 2-3 server instances (load balanced)
- Read replica for database
- **Cost:** $50-100/mo

### 100-500 Agencies

- Auto-scaling (5-10 instances)
- Dedicated database cluster
- Redis cache
- **Cost:** $300-500/mo

### 500+ Agencies

- Kubernetes cluster
- Multi-region deployment
- Dedicated support team
- **Cost:** $2,000+/mo

---

## Files in This Integration

- `README.md` - This file
- `server.js` - Main Express server (unified)
- `routes/clearcare.js` - ClearCare-specific routes
- `routes/axxess.js` - Axxess-specific routes
- `services/voice.js` - Shared voice AI service (Retell)
- `services/database.js` - Shared database service
- `services/alerts.js` - Shared alert service (Telegram/SMS)
- `lib/axxess-api.js` - Axxess API client (from `axxess-api-client.js`)
- `package.json` - Dependencies
- `.env.example` - Environment template
- `Dockerfile` - Optional containerization

---

## Migration from Separate Servers

If you already deployed ClearCare and Axxess separately:

```bash
# Export data from old servers
pg_dump $CLEARCARE_DB_URL > clearcare_backup.sql
pg_dump $AXXESS_DB_URL > axxess_backup.sql

# Merge into unified database
psql $UNIFIED_DB_URL < clearcare_backup.sql
psql $UNIFIED_DB_URL < axxess_backup.sql

# Update agencies table (add platform column)
psql $UNIFIED_DB_URL -c "UPDATE agencies SET platform = 'clearcare' WHERE clearcare_visit_id IS NOT NULL;"
psql $UNIFIED_DB_URL -c "UPDATE agencies SET platform = 'axxess' WHERE axxess_visit_id IS NOT NULL;"

# Point Zapier/API calls to new unified server
# Update webhook URLs in Zapier (ClearCare)
# Update webhook URLs in agency configs (Axxess)

# Shut down old servers
railway delete <old-clearcare-project>
railway delete <old-axxess-project>
```

---

## Next Steps for Arvind

**Week 1 (Feb 3-9):**

1. Review this unified approach
2. Decide: Deploy unified server OR keep separate (Nike recommends unified)
3. If unified: Deploy to Railway (30 min)
4. If separate: Deploy ClearCare and Axxess individually

**Why Unified?**

- Lower cost ($10/mo vs $20/mo)
- Easier to manage (one server, one database, one dashboard)
- Better for investors/partners (looks more professional)
- Scales better (add platforms without new infrastructure)

**When to Keep Separate?**

- If platforms have VERY different tech stacks (not the case here)
- If one platform needs different security/compliance (not the case)
- If you want to sell platforms separately in the future (unlikely)

**Nike's Recommendation:** Deploy unified server. It's more professional, cheaper, and easier to scale.

---

_Built with 🐾 by Nike | Questions? Ask in Telegram @SarinAI_bot_
