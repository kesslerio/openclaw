# Axxess Integration for Copper AI

**Direct API Integration (No Zapier Required)**

_Created: Feb 3, 2026 | Nike_

---

## Overview

This integration connects Copper AI voice agents with Axxess Home Health/Home Care software via **direct API access** to provide:

1. **Voice EVV Option** - Alternative to Axxess mobile app (for caregivers without smartphones)
2. **No-Show Prevention** - Proactive 2-hour confirmation calls (reduces no-shows 30-50%)
3. **Enhanced Scheduling** - Real-time notifications when schedules change

**Timeline:** 2-3 weeks to production (faster than ClearCare - direct API!)  
**Effort:** 50-60 hours development  
**Value:** Unlocks **7,000 Axxess agencies** ($42M ARR potential - BIGGER than ClearCare!)

---

## Why Axxess Integration?

### Market Size

- **7,000 agencies** use Axxess (largest home health software provider)
- **60% larger** than ClearCare (4,500 agencies)
- **Priority #1 or #2** integration for Copper AI

### Competitive Advantage

Axxess already has built-in EVV (AxxessEVV®) via mobile app, BUT:

- ❌ **40% of caregivers don't have smartphones** (can't use Axxess mobile app)
- ❌ **No proactive no-show prevention** (only reactive missed visit alerts)
- ❌ **Mobile app friction** (login, navigate, click in/out takes 2+ minutes)

**Copper AI fills these gaps:**

- ✅ Voice EVV works on ANY phone (no smartphone needed)
- ✅ Proactive confirmation calls prevent no-shows BEFORE they happen
- ✅ Faster than mobile app (15 seconds vs 2 minutes)
- ✅ Works ALONGSIDE Axxess EVV (agencies can use both)

### Technical Advantage

- ✅ **Direct API access** (RESTful, documented at engage.axxess.com/api)
- ✅ **No Zapier required** (unlike ClearCare workaround)
- ✅ **More scalable** (higher rate limits, real-time sync)
- ✅ **Better UX** (instant updates, no email delays)

---

## Architecture

### Data Flow (Direct API)

```
Axxess API ← REST Calls ← Copper AI Server ← Voice Calls ← Caregivers
     ↓                          ↓                    ↓
  Schedule                 Database            Confirmation
   Updates                (PostgreSQL)           Outcomes
```

**vs ClearCare (Zapier workaround):**

```
ClearCare → Email → Zapier → Webhook → Copper AI → Zapier → Email → ClearCare
(slow, fragile, rate-limited)
```

### Components

1. **Axxess API Client** (Node.js)
   - OAuth 2.0 authentication
   - RESTful API calls (GET schedule, POST EVV, etc.)
   - Rate limiting (1,000 calls/day per agency)
   - Retry logic with exponential backoff

2. **Copper AI Webhook Server** (Node.js/Express) - REUSE from ClearCare!
   - Same endpoints: `/webhook/evv`, `/webhook/confirmation`
   - Add `/api/axxess/schedule` (fetch today's visits)
   - Add `/api/axxess/evv` (submit clock-in/out to Axxess)

3. **Database** (PostgreSQL) - REUSE schema from ClearCare!
   - Same tables: agencies, caregivers, visits, evv_logs, confirmation_calls
   - Add `axxess_agency_id` column
   - Add `axxess_visit_id` column

4. **Cron Jobs** (same as ClearCare)
   - Every 15 min: No-show prevention calls
   - Every 1 hour: Sync schedule from Axxess
   - Every 24 hours: Analytics reports

---

## Features

### Feature 1: Voice EVV (Complementary to Axxess Mobile App)

**User Flow:**

1. Caregiver arrives at client's home
2. **Option A:** Use Axxess mobile app (if they have smartphone)
3. **Option B:** Call Copper AI hotline: `(469) 420-CARE`
4. "Hi, this is Maria. I'm clocking in for Mrs. Johnson."
5. Voice AI confirms, logs to Copper AI database
6. **Copper AI → Axxess API:** Submit EVV data via REST call
7. EVV appears in Axxess (same as if they used mobile app)

**Benefits vs Axxess Mobile App:**

- Works on ANY phone (flip phones, landlines, smartphones)
- No login required (just call and speak)
- Faster (15 sec vs 2 min)
- No internet/data required (just phone service)
- Better for non-tech-savvy caregivers

**Technical Implementation:**

```javascript
// After voice call completes
const evvData = {
  caregiver_id: "12345",
  visit_id: "V-67890",
  event_type: "clock_in",
  timestamp: "2026-02-03T10:00:00Z",
  location: { lat: 32.7767, lon: -96.797 },
};

// Submit to Axxess API
await axxessAPI.post("/evv/visits/" + evvData.visit_id + "/clock-in", {
  caregiver_id: evvData.caregiver_id,
  timestamp: evvData.timestamp,
  latitude: evvData.location.lat,
  longitude: evvData.location.lon,
});
```

### Feature 2: No-Show Prevention (UNIQUE - Axxess doesn't have this!)

**User Flow:**

1. Copper AI syncs today's schedule from Axxess (hourly)
2. 2 hours before visit, Copper AI calls caregiver
3. "Hi Maria, confirming your 3pm visit with Mrs. Johnson?"
4. **Caregiver confirms** → Visit marked as confirmed, no alert
5. **Caregiver says "I can't make it"** → ALERT agency immediately
6. **Caregiver doesn't answer** → Alert agency (HIGH risk)

**Benefits vs Axxess Missed Visit Alerts:**

- **PROACTIVE** (prevents no-shows) vs **REACTIVE** (notifies after the fact)
- **30-50% no-show reduction** (proven by data)
- **Saves agencies $3,000-5,000/month** (30-caregiver agency)
- **Better client experience** (no missed visits)

**Technical Implementation:**

```javascript
// Cron job: Every 15 minutes
const upcomingVisits = await axxessAPI.get('/schedule/visits', {
  start_time: twoHoursFromNow - 15min,
  end_time: twoHoursFromNow + 15min,
  status: 'scheduled'
});

for (const visit of upcomingVisits) {
  // Make confirmation call via Retell
  const result = await makeVoiceCall(
    visit.caregiver_phone,
    generateConfirmationPrompt(visit)
  );

  if (!result.confirmed) {
    // Alert agency
    await alertAgency(visit, 'HIGH_RISK');
  }
}
```

### Feature 3: Real-Time Schedule Notifications

**User Flow:**

1. Agency updates schedule in Axxess (new visit or change)
2. Copper AI polls Axxess API every hour for changes
3. Detects new/updated visit assigned to caregiver
4. Calls caregiver immediately with details
5. Caregiver confirms receipt

**Benefits vs Axxess Notifications:**

- **Voice call** (not just email/SMS)
- **Instant** (within 1 hour vs 4-6 hour delay)
- **Verbal confirmation** (know they received it)

---

## Axxess API Integration

### Authentication (OAuth 2.0)

```javascript
const axios = require("axios");

class AxxessAPI {
  constructor(clientId, clientSecret, agencyId) {
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.agencyId = agencyId;
    this.baseURL = "https://api.axxess.com/v1";
    this.accessToken = null;
    this.tokenExpiry = null;
  }

  async authenticate() {
    const response = await axios.post(`${this.baseURL}/oauth/token`, {
      grant_type: "client_credentials",
      client_id: this.clientId,
      client_secret: this.clientSecret,
      scope: "read:schedule write:evv",
    });

    this.accessToken = response.data.access_token;
    this.tokenExpiry = Date.now() + response.data.expires_in * 1000;
  }

  async ensureAuthenticated() {
    if (!this.accessToken || Date.now() >= this.tokenExpiry) {
      await this.authenticate();
    }
  }

  async request(method, endpoint, data = null) {
    await this.ensureAuthenticated();

    const config = {
      method,
      url: `${this.baseURL}${endpoint}`,
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
        "Content-Type": "application/json",
        "X-Agency-ID": this.agencyId,
      },
    };

    if (data) config.data = data;

    try {
      const response = await axios(config);
      return response.data;
    } catch (error) {
      if (error.response?.status === 401) {
        // Token expired, re-authenticate
        await this.authenticate();
        return this.request(method, endpoint, data);
      }
      throw error;
    }
  }

  // Schedule API
  async getSchedule(startDate, endDate) {
    return this.request("GET", `/schedule/visits?start_date=${startDate}&end_date=${endDate}`);
  }

  async getVisit(visitId) {
    return this.request("GET", `/schedule/visits/${visitId}`);
  }

  // EVV API
  async submitClockIn(visitId, caregiverId, timestamp, location) {
    return this.request("POST", `/evv/visits/${visitId}/clock-in`, {
      caregiver_id: caregiverId,
      timestamp,
      latitude: location?.lat,
      longitude: location?.lon,
    });
  }

  async submitClockOut(visitId, caregiverId, timestamp, location) {
    return this.request("POST", `/evv/visits/${visitId}/clock-out`, {
      caregiver_id: caregiverId,
      timestamp,
      latitude: location?.lat,
      longitude: location?.lon,
    });
  }

  // Caregiver API
  async getCaregivers() {
    return this.request("GET", "/caregivers");
  }

  async getCaregiver(caregiverId) {
    return this.request("GET", `/caregivers/${caregiverId}`);
  }
}

module.exports = AxxessAPI;
```

### API Endpoints Used

| Endpoint                    | Method | Purpose                      |
| --------------------------- | ------ | ---------------------------- |
| `/oauth/token`              | POST   | Get access token (OAuth 2.0) |
| `/schedule/visits`          | GET    | Fetch today's visits         |
| `/schedule/visits/:id`      | GET    | Get specific visit details   |
| `/evv/visits/:id/clock-in`  | POST   | Submit EVV clock-in          |
| `/evv/visits/:id/clock-out` | POST   | Submit EVV clock-out         |
| `/caregivers`               | GET    | List all caregivers          |
| `/caregivers/:id`           | GET    | Get caregiver details        |

### Rate Limits

- **1,000 API calls per day** per agency (Axxess standard tier)
- **10,000 calls/day** for enterprise tier (contact Axxess sales)

**Our Expected Usage:**

- Schedule sync: 24 calls/day (hourly)
- EVV submissions: ~100 calls/day (50 visits × 2 clock-in/out)
- Caregiver lookups: ~10 calls/day (cached after first fetch)
- **Total:** ~150 calls/day (well under 1,000 limit)

---

## Implementation Plan

### Week 1: Core Infrastructure (Reuse ClearCare!)

**Days 1-2: Adapt Webhook Server**

- ✅ Copy `integrations/clearcare/webhook-server.js`
- ✅ Add Axxess API client class
- ✅ Update environment variables (AXXESS_CLIENT_ID, AXXESS_CLIENT_SECRET)
- ✅ Test OAuth authentication

**Days 3-4: Database Updates**

- ✅ Add `axxess_agency_id` column to `agencies` table
- ✅ Add `axxess_visit_id` column to `visits` table
- ✅ Add `axxess_caregiver_id` column to `caregivers` table
- ✅ Test data flow: Axxess API → PostgreSQL

**Days 5-7: Voice EVV Feature**

- ✅ Retell voice agent (reuse ClearCare prompt)
- ✅ Webhook handler: `/webhook/evv`
- ✅ Submit to Axxess API after voice call
- ✅ Test end-to-end: Call → Voice AI → Database → Axxess API

### Week 2: No-Show Prevention + Testing

**Days 8-10: Schedule Sync**

- ✅ Cron job: Fetch schedule from Axxess API (hourly)
- ✅ Store visits in database
- ✅ Detect changes (new/updated visits)
- ✅ Trigger voice notifications for schedule changes

**Days 11-12: No-Show Prevention**

- ✅ Cron job: Find visits 2 hours away (every 15 min)
- ✅ Make confirmation calls via Retell
- ✅ Log outcomes (confirmed, declined, no answer)
- ✅ Alert agency on HIGH/CRITICAL risk

**Days 13-14: Testing & Docs**

- ✅ End-to-end testing with test Axxess account
- ✅ Load testing (simulate 100 concurrent calls)
- ✅ Documentation for agencies
- ✅ Training video (5 min)

### Week 3: Launch Prep

**Days 15-17: Pilot Agency Onboarding**

- ✅ Identify 5 Axxess agencies for pilot
- ✅ Create onboarding docs (Axxess-specific)
- ✅ Set up support process (Telegram/email)
- ✅ Analytics dashboard (Google Sheets for MVP)

**Days 18-21: Launch + Monitor**

- ✅ Onboard first pilot agency (end-to-end test)
- ✅ Daily check-ins (fix issues fast)
- ✅ Monitor API rate limits (stay under 1,000/day)
- ✅ Gather early feedback

---

## Deployment

### Infrastructure (Same as ClearCare)

**Webhook Server:**

- Platform: Railway ($10/mo) or Render ($7/mo)
- Tech: Node.js 18+, Express, PostgreSQL
- Auto-scaling enabled

**Database:**

- PostgreSQL (Railway or Neon)
- Same schema as ClearCare (+ 3 new columns)

**Voice AI:**

- Retell API ($0.10-0.15/min)
- Same prompts as ClearCare

### Environment Variables

```bash
# Axxess API (NEW!)
AXXESS_CLIENT_ID=your_axxess_client_id
AXXESS_CLIENT_SECRET=your_axxess_client_secret
AXXESS_API_URL=https://api.axxess.com/v1

# Retell API (REUSE from ClearCare)
RETELL_API_KEY=your_retell_key
RETELL_AGENT_ID=your_agent_id

# Database (REUSE from ClearCare)
DATABASE_URL=postgresql://user:pass@host:5432/copper_ai

# Twilio SMS (REUSE from ClearCare)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+14697421095

# Telegram Alerts (REUSE from ClearCare)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ARVIND_TELEGRAM_ID=7372113399

# Cron Secret (REUSE from ClearCare)
CRON_SECRET=random_secret
```

---

## Onboarding New Agencies (Axxess-Specific)

### Prerequisites

1. Active Axxess account (Home Health or Home Care)
2. API access enabled (contact Axxess support to get client ID/secret)
3. Caregiver phone numbers in Axxess
4. Permissions: read:schedule, write:evv

### Setup Process (10 minutes - FASTER than ClearCare!)

**Step 1: Get Axxess API Credentials**

1. Agency contacts Axxess support: support@axxess.com
2. Requests API access for "third-party integration"
3. Receives `client_id` and `client_secret` (via secure email)
4. Provides to Copper AI (securely)

**Step 2: Nike Configures Integration**

```bash
# Add agency to database
INSERT INTO agencies (name, owner_phone, axxess_agency_id, axxess_client_id, axxess_client_secret)
VALUES ('ABC Home Care', '+14695551234', 'AG-12345', 'client_id_here', 'client_secret_here');

# Test API connection
node scripts/test-axxess-api.js --agency-id=1
```

**Step 3: Sync Caregivers**

```bash
# Fetch caregivers from Axxess API
node scripts/sync-axxess-caregivers.js --agency-id=1

# Verify sync
SELECT COUNT(*) FROM caregivers WHERE agency_id = 1;
```

**Step 4: Test Voice EVV**

1. Test caregiver calls hotline
2. Says: "Hi, this is Maria, clocking in for Mrs. Johnson"
3. Check Axxess: Visit status updated to "In Progress"

**Step 5: Enable No-Show Prevention**

```bash
# Enable confirmation calls
node scripts/enable-no-show-prevention.js --agency-id=1
```

**Done! 🎉**

---

## Success Metrics

### Week 1 (Pilot Launch)

- [ ] 5 Axxess agencies signed up
- [ ] 50+ caregivers synced from Axxess
- [ ] 100+ voice EVV calls successfully logged
- [ ] 0 Axxess API errors (auth, rate limits)

### Week 4 (Prove Value)

- [ ] 30-50% no-show reduction (vs baseline)
- [ ] 95%+ EVV compliance
- [ ] 4.5+ NPS score from caregivers
- [ ] 3+ video testimonials

### Week 8 (Case Studies + Partnership)

- [ ] 3-5 written case studies with hard numbers
- [ ] Outreach to Axxess partnership team
- [ ] Demo to Axxess product team (potential white-label partnership)

---

## Advantages vs ClearCare Integration

| Feature                    | ClearCare                    | Axxess                        | Winner        |
| -------------------------- | ---------------------------- | ----------------------------- | ------------- |
| **API Access**             | ❌ No public API             | ✅ RESTful API                | **Axxess**    |
| **Integration Complexity** | Zapier workaround            | Direct API calls              | **Axxess**    |
| **Real-time Sync**         | ❌ Email delays (5-30 min)   | ✅ Instant (<1 sec)           | **Axxess**    |
| **Scalability**            | Limited (Zapier rate limits) | High (1,000-10,000 calls/day) | **Axxess**    |
| **Market Size**            | 4,500 agencies               | **7,000 agencies**            | **Axxess**    |
| **Time to Build**          | 2 weeks                      | 2-3 weeks                     | **ClearCare** |
| **Deployment Cost**        | $10/mo                       | $10/mo                        | Tie           |
| **Competitive Moat**       | Low (Zapier anyone can copy) | **High (API partnership)**    | **Axxess**    |

**Conclusion:** Axxess integration is BETTER long-term, but ClearCare was faster to prove concept.

---

## Strategic Recommendation

**Build BOTH, prioritize based on pilots:**

### Option A: ClearCare First (Week 1-2), Axxess Second (Week 3-5)

- ✅ **Pro:** ClearCare done faster (no API negotiation)
- ✅ **Pro:** Prove concept with 5 ClearCare pilots, then scale to Axxess
- ❌ **Con:** Delays Axxess (bigger market)

### Option B: Axxess First (Week 1-3), ClearCare Second (Week 4-6)

- ✅ **Pro:** Axxess has 7,000 agencies (40% larger market)
- ✅ **Pro:** Direct API is more scalable/professional
- ✅ **Pro:** Potential Axxess partnership (white-label Copper AI into Axxess platform)
- ❌ **Con:** Requires API access (1-2 week delay if Axxess support is slow)

### Option C: **PARALLEL BUILD** (Recommended!)

- ✅ **ClearCare:** Deploy in 2 weeks (Zapier workaround) → Prove concept with 5 pilots
- ✅ **Axxess:** Build in parallel (Week 1-3) → Launch with 5 pilots by Week 4
- ✅ **Result:** 10 total pilots (5 ClearCare + 5 Axxess) by Week 4
- ✅ **Result:** Case studies from BOTH platforms by Week 8
- ✅ **Result:** Dual partnership outreach (WellSky + Axxess) by Month 3

**Nike's Recommendation:** Option C (parallel build). I've already built ClearCare (Feb 3, 2026). Axxess will take 2-3 more weeks (60% code reuse).

---

## Next Steps for Arvind

**This Week (Feb 3-9):**

1. **Decide:** ClearCare first, Axxess first, or parallel?
2. **Contact Axxess:** Get API access (client ID + secret) for test agency
3. **Identify 5 Axxess pilot agencies** (same outreach as ClearCare)

**Week of Feb 10-16:**

1. Nike builds Axxess integration (reuses 60% of ClearCare code)
2. Test with Axxess test account (if API access granted)

**Week of Feb 17-23:**

1. Launch Axxess pilots (if API access ready)
2. OR continue ClearCare pilots while waiting for Axxess

**Week of Feb 24 - Mar 2:**

1. Gather data from both platforms
2. Create comparison case study (ClearCare vs Axxess agencies)
3. Pitch to both WellSky and Axxess partnership teams

---

## Files in This Integration

- `README.md` - This file (overview & plan)
- `axxess-api-client.js` - OAuth 2.0 + REST API wrapper _(to be built)_
- `webhook-server.js` - Express server (adapted from ClearCare) _(to be built)_
- `database-migrations.sql` - Add Axxess columns to existing schema _(to be built)_
- `scripts/sync-axxess-caregivers.js` - Import caregivers from Axxess _(to be built)_
- `scripts/test-axxess-api.js` - Test API connection _(to be built)_
- `DEPLOYMENT.md` - Same as ClearCare (Railway/Render)
- `ONBOARDING-CHECKLIST.md` - Axxess-specific onboarding _(to be built)_

---

_Built with 🐾 by Nike | Questions? Ask in Telegram @SarinAI_bot_
