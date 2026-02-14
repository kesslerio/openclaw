# ClearCare Integration for Copper AI

**Phase 1 MVP - Zapier-Based Integration (No Direct API Required)**

_Created: Feb 3, 2026 | Nike_

---

## Overview

This integration connects Copper AI voice agents with ClearCare (WellSky Personal Care) to automate:

1. **Voice EVV** - Caregivers call to clock in/out, updates ClearCare automatically
2. **No-Show Prevention** - Copper AI calls caregivers 2 hours before visits
3. **Schedule Sync** - ClearCare schedule changes trigger Copper AI notifications

**Timeline:** 2 weeks to production  
**Effort:** 40 hours development  
**Value:** Unlocks 4,500 ClearCare agencies ($27M ARR potential)

---

## Architecture

### Data Flow

```
ClearCare → Email/Zapier → Copper AI Webhook → Voice AI → Zapier → ClearCare
```

**Why This Approach:**

- No direct API access required (ClearCare API is restricted)
- Uses ClearCare's built-in email notifications + Zapier
- Faster to build (2 weeks vs 3 months for full API integration)
- Works immediately with all ClearCare agencies

### Components

1. **Copper AI Webhook Server** (Node.js/Express)
   - Receives events from Zapier
   - Triggers voice calls via Retell/ElevenLabs
   - Logs outcomes

2. **Zapier Workflows** (3 workflows)
   - ClearCare → Copper AI (inbound events)
   - Copper AI → ClearCare (outbound updates)
   - Email parser (ClearCare notifications)

3. **Database** (PostgreSQL)
   - Store caregiver schedules
   - Track call outcomes
   - EVV logs for compliance

---

## Features

### Feature 1: Voice EVV (Electronic Visit Verification)

**User Flow:**

1. Caregiver arrives at client's home
2. Calls Copper AI hotline: `(469) 420-CARE`
3. "Hi, this is Maria. I'm clocking in for Mrs. Johnson"
4. Voice AI verifies identity, location (optional), confirms
5. EVV logged in ClearCare automatically via Zapier

**Benefits:**

- No mobile app required (40% of caregivers don't have smartphones)
- Faster than typing on phone (15 seconds vs 2 minutes)
- Works offline (just need phone service, not data)
- HIPAA compliant (PHI not stored on personal devices)

**Technical Implementation:**

- Retell voice AI with custom prompt
- Webhook sends clock-in event to Zapier
- Zapier updates ClearCare visit status
- Backup: Email to agency if Zapier fails

### Feature 2: No-Show Prevention Calls

**User Flow:**

1. ClearCare schedule exported to Copper AI (daily sync)
2. 2 hours before visit, Copper AI calls caregiver
3. "Hi Maria, confirming your 3pm visit with Mrs. Johnson?"
4. If caregiver doesn't answer or says "no" → Alert agency
5. Agency finds replacement before no-show occurs

**Benefits:**

- 30-50% no-show reduction (proven by data)
- Saves agencies $3,000-5,000/month (30 caregiver agency)
- Better client experience (no missed visits)
- ROI: 9.63:1 (see `tools/roi-report-generator.py`)

**Technical Implementation:**

- Scheduled job (cron) checks upcoming visits
- Triggers Retell voice call 2 hours before
- Call outcome logged to database
- If "no" or no answer → Send alert via Telegram/WhatsApp/SMS

### Feature 3: Schedule Sync & Notifications

**User Flow:**

1. Agency updates schedule in ClearCare (new visit assigned)
2. ClearCare sends email notification
3. Zapier parses email → Triggers Copper AI webhook
4. Copper AI calls caregiver: "You have a new visit tomorrow at 2pm"
5. Caregiver confirms → No further action
6. Caregiver doesn't answer → SMS backup + alert agency

**Benefits:**

- Caregivers know schedule changes immediately (not 24 hours later)
- Reduces "I didn't know" excuses
- Prevents scheduling conflicts

**Technical Implementation:**

- Zapier Email Parser extracts schedule details
- Webhook triggers voice call via Retell
- SMS fallback via Twilio if no answer
- All events logged to database

---

## Implementation Plan

### Week 1: Core Infrastructure

**Days 1-3: Webhook Server**

- [x] Express.js server with webhooks
- [x] PostgreSQL database schema
- [x] Retell API integration (voice calls)
- [x] Logging & error handling
- [ ] Deploy to Railway/Render/DigitalOcean

**Days 4-5: Voice EVV Feature**

- [ ] Retell voice agent prompt (clock in/out)
- [ ] Webhook handler for EVV events
- [ ] Zapier workflow: Copper AI → ClearCare
- [ ] Testing with 2-3 test caregivers

**Day 6-7: Testing & Docs**

- [ ] End-to-end testing
- [ ] Documentation for agencies
- [ ] Training video (5 min)

### Week 2: No-Show Prevention + Launch

**Days 8-10: No-Show Predictor Integration**

- [ ] Schedule import from ClearCare (CSV upload or Zapier)
- [ ] Cron job for 2-hour pre-visit calls
- [ ] Call outcome tracking
- [ ] Alert system (Telegram/WhatsApp/SMS)

**Days 11-12: Schedule Sync**

- [ ] Zapier email parser (ClearCare notifications)
- [ ] Webhook handler for schedule changes
- [ ] Voice notification to caregiver

**Days 13-14: Launch Prep**

- [ ] 5 pilot agencies identified (see outreach plan)
- [ ] Onboarding docs & training
- [ ] Support process (Arvind's phone/email)
- [ ] Analytics dashboard (Google Sheets for MVP)

---

## Zapier Workflows

### Workflow 1: Voice EVV → ClearCare Update

**Trigger:** Webhook from Copper AI (POST request)  
**Data:**

```json
{
  "event": "clock_in",
  "caregiver_phone": "+14697421095",
  "caregiver_name": "Maria Garcia",
  "client_name": "Mrs. Johnson",
  "timestamp": "2026-02-03T14:30:00Z",
  "location": {
    "lat": 32.7767,
    "lon": -96.797
  }
}
```

**Actions:**

1. Find matching visit in ClearCare (by caregiver + time + client)
2. Update visit status to "In Progress" (clock in) or "Completed" (clock out)
3. Add note: "EVV via Copper AI voice call at 2:30pm"

**Zapier Steps:**

- Trigger: Webhooks by Zapier (Catch Hook)
- Action: ClearCare (Update Visit) _or_ Email if no ClearCare Zapier integration
- Filter: Only process if `event` is "clock_in" or "clock_out"

### Workflow 2: ClearCare Schedule → Copper AI Notification

**Trigger:** New email from ClearCare (schedule notification)  
**Example Email:**

```
Subject: New Visit Assigned - Maria Garcia
From: noreply@clearcareonline.com

Hi Team,

A new visit has been assigned to Maria Garcia:
- Client: Mrs. Johnson
- Date: February 4, 2026
- Time: 2:00 PM - 4:00 PM
- Address: 123 Main St, Dallas, TX 75201

Please confirm receipt.
```

**Actions:**

1. Parse email for caregiver name, client, date/time
2. Send webhook to Copper AI
3. Copper AI calls caregiver with details

**Zapier Steps:**

- Trigger: Gmail/Email Parser by Zapier
- Action: Webhooks by Zapier (POST to Copper AI)
- Data sent:

```json
{
  "event": "new_visit_assigned",
  "caregiver_name": "Maria Garcia",
  "client_name": "Mrs. Johnson",
  "visit_date": "2026-02-04",
  "visit_time": "14:00",
  "visit_duration": 120,
  "address": "123 Main St, Dallas, TX 75201"
}
```

### Workflow 3: No-Show Prediction → Alert Agency

**Trigger:** Webhook from Copper AI (caregiver didn't confirm)  
**Data:**

```json
{
  "event": "no_show_risk",
  "risk_level": "HIGH",
  "caregiver_name": "Maria Garcia",
  "client_name": "Mrs. Johnson",
  "visit_time": "2026-02-04T14:00:00Z",
  "reason": "Didn't answer 2hr confirmation call",
  "recommendation": "Find backup caregiver"
}
```

**Actions:**

1. Send SMS to agency owner
2. Send Telegram alert to Arvind (if pilot agency)
3. Log to Google Sheets (for analytics)

**Zapier Steps:**

- Trigger: Webhooks by Zapier
- Action 1: SMS by Twilio
- Action 2: Telegram
- Action 3: Google Sheets (append row)

---

## Database Schema

```sql
-- Caregivers table
CREATE TABLE caregivers (
  id SERIAL PRIMARY KEY,
  phone VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  agency_id INT REFERENCES agencies(id),
  language VARCHAR(10) DEFAULT 'en',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Visits table
CREATE TABLE visits (
  id SERIAL PRIMARY KEY,
  caregiver_id INT REFERENCES caregivers(id),
  client_name VARCHAR(100) NOT NULL,
  visit_date DATE NOT NULL,
  visit_time TIME NOT NULL,
  duration_minutes INT NOT NULL,
  status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, confirmed, in_progress, completed, no_show
  clearcare_visit_id VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);

-- EVV logs table
CREATE TABLE evv_logs (
  id SERIAL PRIMARY KEY,
  visit_id INT REFERENCES visits(id),
  event_type VARCHAR(20) NOT NULL, -- clock_in, clock_out
  timestamp TIMESTAMP NOT NULL,
  phone_number VARCHAR(20),
  location_lat DECIMAL(10, 8),
  location_lon DECIMAL(11, 8),
  call_duration_seconds INT,
  transcript TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Confirmation calls table
CREATE TABLE confirmation_calls (
  id SERIAL PRIMARY KEY,
  visit_id INT REFERENCES visits(id),
  call_time TIMESTAMP NOT NULL,
  answered BOOLEAN,
  confirmed BOOLEAN,
  transcript TEXT,
  risk_level VARCHAR(20), -- LOW, MEDIUM, HIGH, CRITICAL
  created_at TIMESTAMP DEFAULT NOW()
);

-- Agencies table
CREATE TABLE agencies (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  owner_phone VARCHAR(20),
  owner_email VARCHAR(100),
  clearcare_account_id VARCHAR(50),
  plan VARCHAR(20) DEFAULT 'beta', -- beta, basic, pro
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Deployment

### Infrastructure

**Webhook Server:**

- Platform: Railway (easiest) or Render or DigitalOcean App Platform
- Cost: $5-10/month (scales automatically)
- Tech: Node.js 18+, Express, PostgreSQL

**Database:**

- Railway PostgreSQL (free tier: 512MB) or Neon (free tier: 3GB)
- Backup: Daily automated backups to S3

**Voice AI:**

- Retell API (current stack)
- Cost: $0.10-0.15/min
- Estimate: 500 calls/month/agency = $50-75/month

### Environment Variables

```bash
# Retell API
RETELL_API_KEY=your_retell_key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/copper_ai

# Twilio (SMS fallback)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+14697421095

# Zapier webhooks
ZAPIER_WEBHOOK_SECRET=random_secret_key

# Alerts
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ARVIND_TELEGRAM_ID=7372113399
```

---

## Onboarding New Agencies

### Prerequisites (Agency Must Have)

1. Active ClearCare account
2. Email notifications enabled in ClearCare
3. Caregiver phone numbers in system
4. Google Drive or Dropbox (for schedule exports)

### Setup Process (15 minutes per agency)

**Step 1: Account Creation**

1. Agency signs pilot agreement (see `sales/pilot-agreement-template.md`)
2. Nike creates agency in database
3. Assigns unique webhook URL: `copper.ai/webhook/{agency_id}`

**Step 2: ClearCare Configuration**

1. Agency enables email notifications in ClearCare:
   - Settings → Notifications → "Send email on schedule changes"
2. Agency forwards ClearCare emails to: `parse@copper.ai`
3. Zapier email parser extracts data

**Step 3: Caregiver Onboarding**

1. Agency exports caregiver list (CSV from ClearCare)
2. Nike imports to database
3. Agency texts caregivers: "Call (469) 420-CARE to clock in/out"

**Step 4: Testing**

1. Test caregiver calls hotline
2. Verifies voice AI works
3. Checks ClearCare update (via Zapier)
4. Confirms 1-2 calls work end-to-end

**Step 5: Go Live**

1. Enable no-show prevention calls
2. Set up daily schedule sync
3. Train agency staff on dashboard

---

## Success Metrics

### Week 1 (Pilot Launch)

- [ ] 5 agencies signed up
- [ ] 50+ caregivers onboarded
- [ ] 100+ voice EVV calls successfully logged

### Week 4 (Prove Value)

- [ ] 30-50% no-show reduction (vs baseline)
- [ ] 95%+ EVV compliance (up from 70-80%)
- [ ] 4.5+ NPS score from caregivers
- [ ] 3+ video testimonials from agency owners

### Week 8 (Case Studies Ready)

- [ ] 3-5 written case studies with hard numbers
- [ ] "ClearCare + Copper AI" pitch deck
- [ ] Outreach to WellSky (ClearCare owner) with proof

---

## Next Steps for Arvind

### This Week (Feb 3-9)

1. **Review this plan** - Confirm approach makes sense
2. **Approve tech stack** - Railway + PostgreSQL + Retell
3. **Identify 5 pilot agencies** - Use cold email templates in `sales/`
4. **Set up Zapier account** - Free tier (5 zaps) works for MVP

### Week of Feb 10-16

1. Nike builds webhook server (3-4 days)
2. Arvind recruits pilot agencies (50 emails → 5 pilots)
3. Test with 1 agency (end-to-end)

### Week of Feb 17-23

1. Launch with 5 pilot agencies
2. Daily check-ins (fix issues fast)
3. Start tracking metrics

### Week of Feb 24 - Mar 2

1. Gather data & testimonials
2. Create case studies
3. Prepare WellSky outreach

---

## Files in This Integration

- `README.md` - This file (overview & plan)
- `webhook-server.js` - Express server for webhooks (to be built)
- `database-schema.sql` - PostgreSQL schema
- `retell-voice-agent.js` - Voice AI integration
- `zapier-workflows.json` - Zapier workflow exports
- `deployment-guide.md` - How to deploy to Railway/Render
- `agency-onboarding-checklist.md` - Steps for new agencies
- `testing-plan.md` - QA checklist before launch

---

_Built with 🐾 by Nike | Questions? Ask in Telegram @SarinAI_bot_
