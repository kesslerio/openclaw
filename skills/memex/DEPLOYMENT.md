# 🚀 Memex Deployment Guide

**Complete guide to deploying Memex to production**

---

## Architecture Overview

```
┌─────────────────────┐
│   React Frontend    │  ← Vercel
│   (memex/frontend)  │     memex.vercel.app
└──────────┬──────────┘
           │ HTTPS/REST
           ↓
┌─────────────────────┐
│   FastAPI Backend   │  ← Railway
│   (memex/api)       │     memex-api.railway.app
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│   ChromaDB          │  ← Railway (persistent volume)
│   (vector database) │
└─────────────────────┘
           │
           ↓
┌─────────────────────┐
│   Journals/Data     │  ← Railway (persistent volume)
│   (filesystem)      │     /app/data/
└─────────────────────┘
```

---

## Prerequisites

### Required Accounts

1. **Vercel** - Frontend hosting (free tier)
   - Sign up: https://vercel.com/signup

2. **Railway** - Backend hosting ($5/month after free tier)
   - Sign up: https://railway.app/

3. **OpenAI** - GPT API (pay-as-you-go)
   - API key: https://platform.openai.com/api-keys

### Required Tools

```bash
# Node.js 18+
node --version

# Python 3.11+
python --version

# Git
git --version

# Railway CLI (optional)
npm install -g @railway/cli

# Vercel CLI (optional)
npm install -g vercel
```

---

## Part 1: Backend Deployment (Railway)

### Step 1: Prepare Backend

```bash
cd /home/ubuntu/openclaw/skills/memex

# Create requirements.txt for Railway
cat > requirements.txt << 'EOF'
# Historian (Phase 2)
chromadb==0.4.22
openai==1.12.0
sentence-transformers==2.3.1

# Journalist (Phase 3)
openai==1.12.0

# API (Phase 4)
fastapi==0.109.2
uvicorn[standard]==0.27.1
pydantic==2.6.1

# Utilities
python-dateutil==2.8.2
EOF

# Create Procfile for Railway
cat > Procfile << 'EOF'
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
EOF

# Create railway.json
cat > railway.json << 'EOF'
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
```

### Step 2: Deploy to Railway

**Option A: Railway CLI**

```bash
# Login
railway login

# Create new project
railway init

# Add environment variables
railway variables set OPENAI_API_KEY="sk-..."

# Deploy
railway up

# Get URL
railway domain
# Example: memex-api.railway.app
```

**Option B: Railway Dashboard**

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your memex repository
4. Railway auto-detects Python project
5. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI key
6. Deploy!
7. Add custom domain (optional): Settings → Domains

### Step 3: Configure Persistent Storage

```bash
# In Railway dashboard:
# 1. Click your project
# 2. Variables → Add Variable
# 3. Name: RAILWAY_VOLUME_MOUNT_PATH
# 4. Value: /app/data

# This persists:
# - ChromaDB database
# - Journals
# - Transcripts
```

### Step 4: Test Backend

```bash
# Get your Railway URL
BACKEND_URL="https://memex-api.railway.app"

# Health check
curl $BACKEND_URL/

# Status
curl $BACKEND_URL/api/status

# Test chat (demo mode)
curl -X POST $BACKEND_URL/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Memex?"}'
```

**Expected:** JSON response with mock data (demo mode active until you upload transcripts)

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

```bash
cd /home/ubuntu/openclaw/skills/memex/frontend

# Create .env.production
cat > .env.production << 'EOF'
VITE_API_URL=https://memex-api.railway.app
EOF

# Build locally to test
npm run build

# Test production build
npm run preview
```

### Step 2: Deploy to Vercel

**Option A: Vercel CLI**

```bash
# Install CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd /home/ubuntu/openclaw/skills/memex/frontend
vercel

# Production deployment
vercel --prod
```

**Option B: Vercel Dashboard**

1. Go to https://vercel.com/new
2. Import Git Repository
3. Select `memex/frontend` directory
4. Framework: Vite
5. Root Directory: `memex/frontend`
6. Build Command: `npm run build`
7. Output Directory: `dist`
8. Environment Variables:
   - `VITE_API_URL`: `https://memex-api.railway.app`
9. Deploy!

**Option C: GitHub Integration (Recommended)**

1. Push to GitHub
2. Connect Vercel to GitHub
3. Auto-deploys on every push to main
4. Preview deployments for PRs

### Step 3: Custom Domain (Optional)

**In Vercel Dashboard:**

1. Settings → Domains
2. Add domain: `memex.yourdomain.com`
3. Configure DNS:
   ```
   Type: CNAME
   Name: memex
   Value: cname.vercel-dns.com
   ```

### Step 4: Test Frontend

Visit your Vercel URL:

- Production: `https://memex.vercel.app` (or your custom domain)
- Test all three views:
  - Chat interface
  - Journals
  - Search

---

## Part 3: Data Migration

### Upload Transcripts

```bash
# From your local machine
RAILWAY_URL="https://memex-api.railway.app"

# TODO: Add transcript upload endpoint to API
# For now, use Railway CLI to copy files

railway shell

# Inside Railway shell:
mkdir -p /app/data/transcripts
# Upload files via SFTP or git
```

### Generate Journals

```bash
# SSH into Railway
railway shell

# Run journal generation
cd /app
python -m journalist.automation --backfill --start-date 2026-01-01 --end-date 2026-01-31
```

### Initialize Vector Database

```bash
# SSH into Railway
railway shell

# Run ingestion
cd /app
python -m historian.ingest --source /app/data/transcripts
```

---

## Part 4: Environment Variables

### Backend (Railway)

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
MEMEX_MODEL=gpt-4o-mini
CHROMA_PERSIST_DIRECTORY=/app/data/chroma
JOURNALS_DIRECTORY=/app/data/journals
TRANSCRIPTS_DIRECTORY=/app/data/transcripts
```

### Frontend (Vercel)

```bash
# Required
VITE_API_URL=https://memex-api.railway.app

# Optional
VITE_ANALYTICS_ID=your-analytics-id
```

---

## Part 5: CORS Configuration

Update `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://memex.vercel.app",  # Your Vercel domain
        "https://memex.yourdomain.com",  # Custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy after updating.

---

## Part 6: Monitoring

### Railway Logs

```bash
# View logs
railway logs

# Follow logs
railway logs --follow
```

**Monitor for:**

- API errors
- ChromaDB connection issues
- OpenAI API errors
- Slow queries

### Vercel Analytics

1. Enable Web Analytics in Vercel Dashboard
2. Monitor:
   - Page load times
   - User sessions
   - Error rates

### Health Checks

Set up uptime monitoring:

**UptimeRobot (Free):**

1. Add HTTP(s) monitor
2. URL: `https://memex-api.railway.app/api/status`
3. Interval: 5 minutes
4. Alert email on failures

---

## Part 7: Costs

### Monthly Breakdown

**Railway (Backend):**

- Free tier: $5 credit/month
- After free tier: ~$5-10/month
  - API hosting: $5/month
  - Persistent storage (10GB): $0-5/month

**Vercel (Frontend):**

- Hobby tier: FREE
- Pro tier: $20/month (if needed)

**OpenAI API:**

- Embeddings: ~$0.09/month (30 queries/day)
- GPT-4o-mini: ~$2/month (30 queries/day)
- GPT-4o: ~$8/month (if upgraded)
- **Total:** $2-10/month

**Estimated Total: $7-30/month**

---

## Part 8: Scaling

### When to Scale

**Backend (Railway):**

- Default: 512MB RAM, 1 vCPU
- Scale to 1GB RAM if:
  - ChromaDB grows large (>10k documents)
  - Slow search queries
  - Memory errors

**Frontend (Vercel):**

- Auto-scales with traffic
- No action needed

### How to Scale

**Railway:**

```bash
# In Railway dashboard
Settings → Resources
- RAM: 512MB → 1GB ($5 → $10/month)
- CPU: Shared → Dedicated (if needed)
```

---

## Part 9: Backup

### Automated Backups

**Railway Persistent Volumes:**

Railway automatically backs up volumes. To manually export:

```bash
# SSH into Railway
railway shell

# Create backup
cd /app/data
tar -czf backup-$(date +%Y%m%d).tar.gz chroma/ journals/ transcripts/

# Download via SFTP or Railway CLI
```

**Schedule with cron:**

```bash
# In Railway, add cron job (if supported)
# Or use external service like EasyCron
```

---

## Part 10: Security

### API Security

**Add authentication (optional but recommended):**

```python
# api/main.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.post("/api/chat/query")
async def chat_query(
    request: ChatQueryRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify token
    if credentials.credentials != os.getenv("API_TOKEN"):
        raise HTTPException(status_code=401, detail="Invalid token")
    ...
```

**Environment variable:**

```bash
railway variables set API_TOKEN="your-secret-token"
```

**Frontend:**

```javascript
// src/store/useMemexStore.js
const token = import.meta.env.VITE_API_TOKEN;

fetch("/api/chat/query", {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

### HTTPS Only

Railway and Vercel provide HTTPS by default. No additional config needed!

---

## Part 11: Troubleshooting

### Backend won't start

**Check logs:**

```bash
railway logs
```

**Common issues:**

- Missing `OPENAI_API_KEY`
- Import errors (missing dependencies in `requirements.txt`)
- Port binding (use `$PORT` env variable)

### Frontend can't connect to backend

**Check:**

1. `VITE_API_URL` is correct
2. CORS allows your Vercel domain
3. Backend is running: `curl https://memex-api.railway.app/api/status`

### Demo mode is active

**Means:** Backend components not initialized (missing data)

**Fix:**

1. Upload transcripts to `/app/data/transcripts/`
2. Run ingestion pipeline
3. Generate journals
4. Restart API

### Slow queries

**Check:**

- ChromaDB index size
- Query complexity
- Railway RAM allocation

**Fix:**

- Scale RAM to 1GB
- Optimize vector search parameters
- Add caching (Redis)

---

## Part 12: Updates & Maintenance

### Updating Backend

```bash
# Local changes
cd /home/ubuntu/openclaw/skills/memex
git add .
git commit -m "feat: Add feature X"
git push

# Railway auto-deploys from GitHub
# Or manually:
railway up
```

### Updating Frontend

```bash
cd /home/ubuntu/openclaw/skills/memex/frontend
npm run build
vercel --prod

# Or push to GitHub for auto-deploy
```

### Database Migrations

When schema changes:

```bash
# SSH into Railway
railway shell

# Run migration script
python scripts/migrate_db.py
```

---

## Part 13: Alternative Hosting Options

### Backend Alternatives

**1. Fly.io**

- Similar to Railway
- Persistent volumes
- $5-10/month

**2. DigitalOcean App Platform**

- $5/month starter tier
- Built-in databases

**3. AWS (Advanced)**

- ECS Fargate + RDS
- More expensive but scalable

### Frontend Alternatives

**1. Netlify**

- Similar to Vercel
- Free tier

**2. Cloudflare Pages**

- Free, fast CDN
- Easy deployment

**3. GitHub Pages (Static only)**

- Free
- Custom domains

---

## Part 14: Development Workflow

### Local Development

```bash
# Terminal 1: Backend
cd /home/ubuntu/openclaw/skills/memex
uvicorn api.main:app --reload --port 8765

# Terminal 2: Frontend
cd /home/ubuntu/openclaw/skills/memex/frontend
npm run dev

# Access: http://localhost:3000
```

### Staging Environment

**Create staging branches:**

```bash
# Deploy staging from 'develop' branch
git checkout -b develop
git push origin develop

# Railway: Create staging environment
# Vercel: Auto-creates preview deployment
```

---

## Quick Reference

### URLs

- **Frontend:** https://memex.vercel.app
- **Backend:** https://memex-api.railway.app
- **API Docs:** https://memex-api.railway.app/docs

### Commands

```bash
# Backend logs
railway logs --follow

# Deploy frontend
vercel --prod

# Test API
curl https://memex-api.railway.app/api/status

# Backup data
railway shell
tar -czf backup.tar.gz /app/data
```

### Costs

- Railway: $5-10/month
- Vercel: FREE (or $20/month Pro)
- OpenAI: $2-10/month
- **Total: $7-30/month**

---

## Success Checklist

- [ ] Backend deployed to Railway
- [ ] Frontend deployed to Vercel
- [ ] Environment variables configured
- [ ] CORS allows frontend domain
- [ ] Health checks passing
- [ ] Transcripts uploaded
- [ ] Journals generated
- [ ] Vector database initialized
- [ ] Chat interface working
- [ ] Journal browser working
- [ ] Search working
- [ ] Uptime monitoring configured
- [ ] Backups automated

---

## Support

**Issues:**

- Railway: https://help.railway.app/
- Vercel: https://vercel.com/support
- Memex: Check GitHub issues

**Community:**

- Railway Discord
- Vercel Discord
- Memex (TBD)

---

🚀 **Ready to deploy your personal memory AI!**

---

🐾 Nike  
2026-02-02
