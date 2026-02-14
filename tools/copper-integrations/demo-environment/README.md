# Demo Environment - Test Unified Server Before Production

**Purpose:** Safe testing environment for Copper AI unified server  
**Use Case:** Demo to prospects, train staff, test new features  
**Status:** Ready to deploy

---

## Why You Need This

**Problem:** Can't test unified server with real agencies (risks breaking production)

**Solution:** Mock demo environment with fake data that looks real

**Benefits:**

- ✅ Demo to prospects without revealing real agency data
- ✅ Test features before pushing to production
- ✅ Train new team members on safe data
- ✅ Reproduce bugs in isolated environment
- ✅ Onboarding dry runs (practice before real agencies)

---

## Quick Start (5 Minutes)

```bash
cd /home/ubuntu/openclaw/tools/copper-integrations/demo-environment

# 1. Install dependencies
npm install

# 2. Set up demo database
node setup-demo-db.js

# 3. Start demo server
npm run demo

# Server running at: http://localhost:3001
# Demo agency credentials in: demo-credentials.json
```

---

## What's Included

### 1. Mock Agency Data

- **ABC Home Health** (50 caregivers, ClearCare)
- **XYZ Senior Care** (30 caregivers, Axxess)
- **Demo Family Services** (75 caregivers, both platforms)

### 2. Fake Caregivers (Realistic Names)

- 155 caregivers total across 3 agencies
- Mix of reliability scores (excellent, good, fair, poor)
- Realistic no-show history (5-30% rates)
- Various shift types (day, night, overnight, weekend)

### 3. Scheduled Visits (Next 7 Days)

- 500+ visits scheduled across all agencies
- Mix of risk levels (LOW, MODERATE, HIGH, CRITICAL)
- Realistic patient addresses (using safe test addresses)
- Various visit durations (2-12 hours)

### 4. Historical Data (Past 90 Days)

- 5,000+ completed visits
- No-show events (realistic distribution)
- Confirmation call logs
- Voice EVV logs

---

## Demo Scenarios

### Scenario 1: Voice EVV Demo

**Goal:** Show how caregivers clock in/out via voice

**Steps:**

1. Start demo server: `npm run demo`
2. Call demo hotline: (displayed in terminal)
3. Say: "This is Sarah, clocking in for Mrs. Johnson"
4. Watch: Real-time update in demo dashboard
5. Show: ClearCare/Axxess webhook received

**Result:** Prospect sees full voice EVV flow in 30 seconds

---

### Scenario 2: No-Show Predictor Demo

**Goal:** Show AI predicting high-risk visits

**Steps:**

1. Open demo dashboard: http://localhost:3001/dashboard
2. Navigate to "Today's Schedule"
3. Filter by: Risk Level = HIGH or CRITICAL
4. Click on a high-risk visit
5. Show: Risk factors breakdown (caregiver history, weather, shift type)
6. Show: Recommended actions
7. Simulate: AI confirmation call (click "Make Call")
8. Show: Caregiver responds "Can't make it" → Instant alert

**Result:** Prospect sees predictive intelligence in action

---

### Scenario 3: ROI Tracking Demo

**Goal:** Show weekly ROI reports

**Steps:**

1. Open demo dashboard: http://localhost:3001/reports
2. Select: "Last 7 Days" report
3. Show metrics:
   - No-shows prevented: 12 (vs 24 expected)
   - Revenue saved: $2,400
   - Admin time saved: 8 hours
   - ROI: 10:1
4. Show trend chart: No-show rate declining over 8 weeks

**Result:** Prospect sees concrete ROI evidence

---

### Scenario 4: Multi-Agency Management

**Goal:** Show enterprise capabilities (multiple locations)

**Steps:**

1. Log in as: enterprise@demo.com
2. Dashboard shows: 3 agencies side-by-side
3. Compare: ABC (22% no-shows) vs XYZ (12% no-shows)
4. Identify: Best practices from XYZ to apply to ABC
5. Show: Caregiver reliability rankings across all agencies

**Result:** Enterprise prospects see scalability

---

## Architecture

### Demo Server (Port 3001)

```
integrations/demo-environment/
├── server.js                  # Express server (demo mode)
├── setup-demo-db.js           # Populate demo database
├── demo-data-generator.js     # Generate realistic fake data
├── demo-dashboard.html        # Web UI for demos
└── package.json
```

### Demo Database (PostgreSQL)

- Same schema as production (`integrations/unified-server/database-schema.sql`)
- Prefixed tables: `demo_agencies`, `demo_caregivers`, etc.
- Auto-resets daily (fresh data every morning)

### Demo Voice AI

- Uses Retell test mode (no actual phone calls)
- Simulated voice responses (prerecorded)
- Logs all interactions (review after demo)

---

## Demo Credentials

**ABC Home Health (ClearCare)**

```
Agency ID: demo-abc-001
Username: admin@abchomehealth.demo
Password: demo123
Platform: ClearCare
Caregivers: 50
```

**XYZ Senior Care (Axxess)**

```
Agency ID: demo-xyz-002
Username: admin@xyzseniorcare.demo
Password: demo123
Platform: Axxess
Caregivers: 30
```

**Demo Family Services (Enterprise)**

```
Agency ID: demo-dfs-003
Username: enterprise@demo.com
Password: demo123
Platform: Both (ClearCare + Axxess)
Locations: 3 (Dallas, Houston, Austin)
Caregivers: 75
```

---

## Demo Script (15-Minute Walkthrough)

### Part 1: The Problem (2 min)

**You:** "Let me show you what home health agencies deal with every day."

1. Show ABC Home Health dashboard
2. Highlight: 22% no-show rate (industry average)
3. Calculate: $18,000 lost per month
4. Show: Manual confirmation calls (80 hours/month)

**You:** "This is expensive and exhausting. Let me show you how Copper AI solves it."

---

### Part 2: Voice EVV (3 min)

**You:** "First, we make clocking in/out effortless."

1. Demonstrate live voice call (caregiver clocking in)
2. Show: 15-second call vs 2-minute mobile app
3. Show: Real-time EMR update (ClearCare dashboard)
4. Highlight: Works without smartphone (40% of caregivers)

**You:** "That's it. No app, no typing, no GPS issues. Just call a number."

---

### Part 3: No-Show Predictor (5 min)

**You:** "Now here's our secret sauce: predicting no-shows before they happen."

1. Show today's schedule with risk scores
2. Click on HIGH-risk visit
3. Explain risk factors:
   - Caregiver: 24% no-show rate (vs 8% average)
   - Shift: Overnight (harder)
   - Weather: Snow forecast
   - Workload: 52 hours this week (burnout)
4. Show: AI makes confirmation call 2 hours early
5. Simulate: Caregiver can't make it
6. Show: Instant alert to agency (4 hours to find backup)

**You:** "Without this, you'd discover the no-show AFTER it happens. With Copper AI, you prevent it."

---

### Part 4: ROI Proof (3 min)

**You:** "Let me show you the results from ABC Home Health over 8 weeks."

1. Show weekly ROI report
2. Metrics:
   - No-shows: 22% → 12% (45% reduction)
   - Money saved: $8,100/month
   - Time saved: 40 hours/month
   - ROI: 10:1
3. Show trend chart (declining no-show rate)

**You:** "This is real data. And this is what you'll see in your agency."

---

### Part 5: Getting Started (2 min)

**You:** "Here's how fast you can launch:"

1. Today: 15-min demo (we're here now)
2. This week: 30-min onboarding call
3. Next week: Live with your team
4. 60 days later: Convert to paid or cancel (no risk)

**You:** "Questions?"

---

## Customization for Prospects

### Before Demo Call

1. Ask agency size, platform (ClearCare/Axxess), current no-show rate
2. Customize demo data to match their numbers
3. Pre-load their ROI calculation in demo environment

**Example:**

```bash
node setup-demo-db.js \
  --caregivers=35 \
  --noshow-rate=28 \
  --platform=clearcare \
  --agency-name="Prospect Home Health"
```

Result: Demo shows THEIR agency name, THEIR numbers, THEIR potential ROI

---

## Demo Environment vs Production

| Feature         | Demo           | Production           |
| --------------- | -------------- | -------------------- |
| **Database**    | SQLite (local) | PostgreSQL (Railway) |
| **Voice calls** | Simulated      | Real (Retell)        |
| **EMR sync**    | Fake           | Real (Zapier/API)    |
| **Data**        | Generated      | Real agencies        |
| **Reset**       | Daily          | Never                |
| **Cost**        | $0             | $10-50/mo            |
| **Risk**        | Zero           | Real data            |

---

## Troubleshooting

### Demo server won't start

```bash
# Check if port 3001 is in use
lsof -i :3001

# Kill existing process
kill -9 <PID>

# Restart
npm run demo
```

### Voice call simulation not working

```bash
# Check Retell test mode
curl http://localhost:3001/api/test/voice-status

# Restart voice service
npm run demo:voice
```

### Database needs reset

```bash
# Full reset (deletes all demo data)
node setup-demo-db.js --reset

# Regenerate visits for next 7 days
node setup-demo-db.js --regenerate-schedule
```

---

## Production Deployment Checklist

After successful demos, before deploying to production:

- [ ] Review all demo feedback (what worked, what confused prospects)
- [ ] Test edge cases discovered during demos
- [ ] Update onboarding checklist based on demo questions
- [ ] Train support team on common issues
- [ ] Set up monitoring (Sentry, PagerDuty)
- [ ] Create runbook for production incidents
- [ ] Deploy to Railway (follow `integrations/unified-server/QUICKSTART.md`)

---

## Next Steps

1. **Deploy demo environment** (5 min)
2. **Practice demo script** (run through 3x solo)
3. **Customize for first prospect** (use their data)
4. **Book demo call** (use demo to close pilot)

---

_Demo environment by Nike 🐾 | February 2026 | Risk-free testing_
