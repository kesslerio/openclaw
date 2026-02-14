# ClearCare/WellSky Personal Care Integration Plan

**Created:** Feb 1, 2026  
**For:** Arvind Sarin / Copper Digital  
**Priority:** **CRITICAL - #1 Strategic Priority**  
**Purpose:** Technical & business plan for integrating Copper AI with ClearCare/WellSky Personal Care

---

## 🎯 Executive Summary

**ClearCare (now WellSky Personal Care) is THE integration target for Copper AI.**

**Why This is #1 Priority:**

- ✅ **4,500 agencies** use this platform (instant TAM)
- ✅ **8 of 10 largest franchise** enterprises use it
- ✅ **Dominant market share** in personal care/non-medical home health
- ✅ Integration = **distribution channel** (sell to 4,500 agencies instantly)
- ✅ Partnership potential (white-label or co-sell)

**Outcome:**

- Build integration in 2-4 weeks
- Unlock access to 4,500 potential customers
- Potential partnership/acquisition path with WellSky

---

## 📊 Market Intelligence: WellSky Personal Care

### Company Background

**Brand Evolution:**

- Founded as "ClearCare" (2000s)
- Acquired by **WellSky** (2018-2019)
- Now: **WellSky Personal Care** (enterprise health tech company)

**WellSky Holdings:**

- Personal Care (formerly ClearCare)
- Home Health & Hospice
- Senior Living
- Pharmacy
- Blood Bank
- Community Services

**Total WellSky reach:** 20,000+ healthcare organizations globally

---

### Customer Base

| Metric                    | Value         | Notes                                  |
| ------------------------- | ------------- | -------------------------------------- |
| **Total Agencies**        | 4,500+        | US & North America                     |
| **Franchise Enterprises** | 8 of top 10   | Comfort Keepers, Visiting Angels, etc. |
| **Market Share**          | ~35-40%       | Dominant in personal care segment      |
| **Client Retention**      | 99%           | Very sticky platform                   |
| **Geographic Coverage**   | North America | US + Canada                            |

**Agency Size Distribution:**

- Small (1-10 caregivers): ~30%
- Medium (11-50 caregivers): ~45%
- Large (51-200 caregivers): ~20%
- Enterprise (200+ caregivers): ~5%

**Total Addressable Market via ClearCare:**

- 4,500 agencies × $500/month = **$2.25M MRR potential**
- Annual: **$27M ARR** (if Copper AI captured 100%)
- Realistic Year 1: 1-2% penetration = $225k-450k ARR

---

### Technology Stack

**Platform Type:** Web-based SaaS (cloud-hosted)

**Key Features:**

1. **Care Delivery:**
   - Scheduling & dispatching
   - Visit tracking (EVV)
   - Care plan management
   - Task checklists

2. **Caregiver Management:**
   - Applicant tracking
   - Onboarding & training
   - Time & attendance
   - Mobile app (iOS/Android)

3. **Back-Office:**
   - Billing & payroll
   - Claims submission (Medicaid/insurance)
   - Reporting & analytics
   - Family Room portal (for families)

4. **Compliance:**
   - HITRUST CSF certified (HIPAA)
   - EVV compliance (federal mandate)
   - State-specific requirements

**Technology Gaps (Copper AI Opportunity):**

- ❌ No voice-first interface
- ❌ No AI-powered no-show prevention
- ❌ No predictive analytics (caregiver burnout, EVV errors)
- ❌ No proactive communication (caregivers still use mobile app for clock-in/out)

---

### Integration Ecosystem

**WellSky Personal Care Connect API:**

- Purpose: Enable third-party integrations
- Access: Partner program (requires application)
- Documentation: https://apidocs.clearcareonline.com/ (protected/partner-only)

**Current Integration Partners (Examples):**

1. **Hireology** - Recruiting & hiring
2. **ADP, Paychex** - Payroll processing
3. **Quickbooks** - Accounting
4. **SalesForce** - CRM
5. **Various telephony providers** - Call tracking

**Integration Categories:**

- HR & Recruiting
- Payroll & Accounting
- CRM & Marketing
- Communication & Telephony ← **Copper AI fits here!**
- Insurance & Billing

**No Current Voice AI Partners** - Blue ocean opportunity!

---

## 🏗️ Integration Architecture

### Integration Approach: Two Phases

**Phase 1: Lightweight Integration (2 weeks)**

- No formal API access required
- Use webhooks + Zapier/Make.com as middleware
- Prove value quickly, get customer feedback

**Phase 2: Deep Integration (4-6 weeks)**

- Apply to WellSky Partner Program
- Get API access (requires NDA, certification)
- Build native integration (no middleware)

---

### Phase 1: Lightweight Integration (MVP)

**Goal:** Connect Copper AI to ClearCare without waiting for API access

**Architecture:**

```
┌─────────────────┐
│ ClearCare User  │ (Caregiver or Admin)
└────────┬────────┘
         │ Calls Copper AI
         ▼
┌─────────────────┐
│   Copper AI     │ (Voice Agent)
└────────┬────────┘
         │ Processes request
         ▼
┌─────────────────┐
│  Zapier/Make    │ (Middleware)
└────────┬────────┘
         │ API calls
         ▼
┌─────────────────┐
│   ClearCare     │ (Via email triggers or webhooks)
└─────────────────┘
```

**Implementation:**

**Step 1: Email-Based Triggers**

- ClearCare can send emails for events (shift assigned, client added, etc.)
- Zapier watches specific email inbox
- Triggers Copper AI actions

**Step 2: Outbound Actions**

- Copper AI → Zapier → ClearCare
- Example: Caregiver calls in "I'm running late" → Copper AI → Zapier → Update ClearCare schedule

**Step 3: Data Sync**

- Daily export from ClearCare (CSV/Excel)
- Copper AI ingests schedule, client list, caregiver roster
- Nightly sync (not real-time, but sufficient for MVP)

**Limitations:**

- Not real-time (delays up to 24 hours for data sync)
- Limited bi-directional updates
- Requires manual CSV exports initially

**Pros:**

- ✅ Fast to build (2 weeks)
- ✅ No API access needed
- ✅ Proves value quickly
- ✅ Can demo to WellSky for partnership discussions

---

### Phase 2: Deep Integration (Production)

**Goal:** Native integration via WellSky Personal Care Connect API

**Architecture:**

```
┌─────────────────┐
│   Copper AI     │ (Voice Agent)
└────────┬────────┘
         │ Direct API calls
         │ OAuth 2.0 auth
         ▼
┌─────────────────┐
│ WellSky Connect │ (REST API)
│      API        │
└────────┬────────┘
         │ Real-time data
         ▼
┌─────────────────┐
│   ClearCare     │ (Agency's instance)
│   Database      │
└─────────────────┘
```

**API Endpoints (Assumed, based on typical home health APIs):**

**Read Operations:**

- `GET /clients` - Fetch client list
- `GET /caregivers` - Fetch caregiver roster
- `GET /schedules` - Fetch shift schedule
- `GET /visits` - Fetch visit history (EVV data)

**Write Operations:**

- `POST /clock-in` - Clock in caregiver for shift
- `POST /clock-out` - Clock out caregiver
- `PUT /schedule/{id}` - Update schedule (reschedule, cancel)
- `POST /notes` - Add visit notes, care documentation

**Webhooks (Real-Time Notifications):**

- `schedule.created` - New shift assigned
- `schedule.updated` - Shift time changed
- `visit.started` - Caregiver clocked in
- `visit.completed` - Caregiver clocked out
- `alert.created` - Agency created alert (late caregiver, missed visit)

**Authentication:**

- OAuth 2.0 (standard for SaaS integrations)
- Per-agency API keys (each agency authorizes Copper AI)

**Data Model Examples:**

**Client Object:**

```json
{
  "id": 12345,
  "name": "Jane Doe",
  "address": "123 Main St, Dallas, TX",
  "care_plan": "Medication reminders, meal prep",
  "emergency_contact": {
    "name": "John Doe",
    "phone": "214-555-1234"
  }
}
```

**Schedule Object:**

```json
{
  "id": 67890,
  "client_id": 12345,
  "caregiver_id": 54321,
  "start_time": "2026-02-03T09:00:00Z",
  "end_time": "2026-02-03T12:00:00Z",
  "status": "scheduled",
  "tasks": ["Medication", "Meal prep", "Light housekeeping"]
}
```

**EVV Clock-In Request:**

```json
{
  "visit_id": 67890,
  "caregiver_id": 54321,
  "clock_in_time": "2026-02-03T09:05:00Z",
  "location": {
    "latitude": 32.7767,
    "longitude": -96.797
  },
  "method": "voice_call" // Copper AI identifier
}
```

---

## 🎁 Use Cases: What Copper AI + ClearCare Can Do

### 1. Voice-First EVV (Clock In/Out)

**Current ClearCare Process:**

1. Caregiver opens mobile app
2. Taps "Clock In"
3. App verifies GPS location
4. Caregiver enters PIN or signature
5. Data synced to ClearCare

**With Copper AI:**

1. Caregiver calls Copper AI: "Clock me in for Mrs. Johnson"
2. Copper AI: "Clocking you in at 123 Main St. Confirmed, you're clocked in at 9:05 AM."
3. Copper AI → ClearCare API → EVV data updated in real-time

**Why This is Better:**

- ✅ Hands-free (safer while driving)
- ✅ No app required (works on any phone)
- ✅ Faster (voice > typing)
- ✅ More accessible (elderly caregivers, non-tech-savvy)

---

### 2. Automated Schedule Notifications

**Current ClearCare Process:**

- Admin assigns shift in ClearCare
- ClearCare sends text/email to caregiver
- Caregiver may or may not see it

**With Copper AI:**

- Admin assigns shift in ClearCare
- ClearCare webhook → Copper AI
- Copper AI **calls caregiver immediately**: "Hi Maria, you have a new shift assigned for tomorrow at 9 AM with Mrs. Johnson. Can you confirm?"
- Caregiver: "Yes, confirmed."
- Copper AI → ClearCare API → Shift marked as confirmed

**Why This is Better:**

- ✅ Proactive (don't wait for caregiver to check email)
- ✅ Immediate confirmation (reduce no-shows)
- ✅ Two-way communication (caregiver can ask questions)

---

### 3. No-Show Prevention

**Current ClearCare Process:**

- Shift scheduled
- Caregiver doesn't show up
- Client calls agency to complain
- Admin scrambles to find replacement

**With Copper AI:**

- 2 hours before shift: Copper AI calls caregiver "Are you still good for your 2 PM visit with Mr. Smith?"
  - Yes → Great, see you then!
  - No/No answer → Copper AI alerts admin + suggests available backup caregivers
- Admin reassigns shift in ClearCare
- Copper AI calls backup caregiver immediately

**Impact:**

- ✅ 30-50% reduction in no-shows (proven from other industries)
- ✅ $2,500-5,000/month savings per agency (based on 500 visits/month)

---

### 4. Real-Time Schedule Changes

**Current ClearCare Process:**

- Caregiver needs to reschedule (sick, car trouble, etc.)
- Calls agency office
- Admin answers (or voicemail)
- Admin updates ClearCare manually

**With Copper AI:**

- Caregiver calls Copper AI: "I'm sick, can't make my 2 PM shift today."
- Copper AI: "I'm sorry to hear that. I'll notify the office and see if we can find a backup. Do you have a doctor's note or need sick leave?"
- Copper AI → ClearCare API → Shift marked as "needs coverage"
- Copper AI calls admin (or sends Slack/Teams message)
- Admin approves → Copper AI finds backup → calls backup caregiver

**Why This is Better:**

- ✅ 24/7 availability (no waiting for office hours)
- ✅ Instant response (caregiver isn't left in limbo)
- ✅ Automated triage (simple requests handled by AI, complex ones escalated to humans)

---

### 5. Voice-Powered Visit Notes

**Current ClearCare Process:**

- Caregiver completes visit
- Opens mobile app
- Types visit notes ("Helped Mrs. Johnson with bath, medication, meal prep...")
- Submits

**With Copper AI:**

- Caregiver calls Copper AI after visit: "I just finished with Mrs. Johnson. Helped her with bath, gave her morning meds, and made lunch. She seemed a bit more tired than usual."
- Copper AI transcribes → structures data → sends to ClearCare API
- ClearCare auto-populates visit note

**Why This is Better:**

- ✅ Faster (speak vs type)
- ✅ More detailed (people speak more than they type)
- ✅ Accessible while driving home

---

### 6. Predictive Analytics (Powered by ClearCare Data)

**Data Copper AI Can Analyze:**

- Caregiver clock-in/out patterns (early, late, on-time)
- No-show history
- Overtime hours
- Client feedback/complaints

**Predictions Copper AI Can Make:**

1. **No-Show Risk:** "Caregiver Maria has been late 3 times this week, and tomorrow is Friday (higher no-show rate). Alert admin to confirm."

2. **Burnout Risk:** "Caregiver John has worked 60+ hours this week, including 4 double shifts. High burnout risk. Suggest offering time off or lighter schedule next week."

3. **EVV Error Prevention:** "Caregiver clocking in from wrong location. Ask: 'Are you at 123 Main St? Our records show you're 2 miles away.'"

**Impact:**

- ✅ Proactive problem-solving (prevent issues before they happen)
- ✅ Improved caregiver retention (detect burnout early)
- ✅ Higher EVV compliance (prevent errors in real-time)

---

## 💼 Business Model: How to Sell This

### Positioning

**To ClearCare Customers (Agencies):**

> "Copper AI is the voice-first AI assistant for your ClearCare platform. Reduce no-shows by 30%, automate EVV compliance, and give your caregivers the freedom to manage their schedules hands-free."

**To WellSky (Partnership Pitch):**

> "We've built the AI voice layer that your customers are asking for. Let's partner to bring voice-first operations to all 4,500 agencies on your platform."

---

### Pricing Models

**Option 1: Direct to Agency (Current Model)**

- $500/month per agency (existing Copper AI pricing)
- ClearCare integration is a **feature**, not an upsell

**Option 2: Per-Caregiver Pricing**

- $5-10/month per active caregiver
- Example: Agency with 20 caregivers = $100-200/month
- Scales with agency size

**Option 3: White-Label Partnership with WellSky**

- WellSky sells as "WellSky Voice Assistant"
- Copper AI provides technology (SaaS backend)
- Revenue share: 50/50 or 70/30 (WellSky/Copper AI)
- Copper AI gets distribution to 4,500 agencies instantly

---

### Go-to-Market Strategy

**Step 1: Build MVP Integration (Phase 1)**

- Timeline: 2 weeks
- Cost: Internal dev time (Nike can build)
- Deliverable: Working demo with 1-2 pilot agencies

**Step 2: Pilot with ClearCare Customers**

- Target: 5-10 agencies already using ClearCare
- Offer: Free for 30 days in exchange for feedback + case study
- Goal: Prove 30% no-show reduction, 50% EVV error reduction

**Step 3: Approach WellSky Partnership Team**

- Armed with: Pilot results, case studies, working demo
- Pitch: "We've built what your customers need. Let's partner."
- Ask: API access, co-marketing, or acquisition discussion

**Step 4: Launch to ClearCare Customer Base**

- Channels:
  - WellSky partner directory (if accepted)
  - Direct sales to ClearCare agencies (LinkedIn, cold email)
  - Webinar: "Voice AI for ClearCare Users"
  - Industry conferences (Home Care 100, etc.)

---

## 🚀 Implementation Roadmap

### Week 1-2: Phase 1 MVP (Lightweight Integration)

**Tasks:**

1. Set up Zapier account + ClearCare test environment
2. Build email-based triggers (Zapier → Copper AI)
3. Test: Schedule notification → Copper AI calls caregiver
4. Test: Caregiver calls Copper AI → Update sent to ClearCare (via email/Zapier)
5. Create demo script + video

**Deliverables:**

- Working demo (screen recording)
- Pilot-ready system
- Case study template

---

### Week 3-4: Pilot Launch

**Tasks:**

1. Recruit 3-5 ClearCare agencies (Texas focus initially)
2. Onboard agencies (connect ClearCare accounts)
3. Train caregivers (how to use Copper AI)
4. Monitor usage + collect feedback
5. Measure KPIs (no-show rate, EVV accuracy, admin time saved)

**Deliverables:**

- 3-5 active pilot agencies
- Usage metrics (# calls, # EVV transactions, etc.)
- Initial case study draft

---

### Week 5-6: Phase 2 Planning + WellSky Outreach

**Tasks:**

1. Apply to WellSky Partner Program
2. Request API access (submit integration plan)
3. Schedule demo with WellSky partnership team
4. Prepare pitch deck (partnership or acquisition)

**Deliverables:**

- Partner application submitted
- Demo scheduled with WellSky
- Decision: Partnership, co-sell, or direct sales

---

### Week 7-12: Deep Integration (If API Access Granted)

**Tasks:**

1. OAuth 2.0 authentication setup
2. Build API connectors (GET /schedules, POST /clock-in, etc.)
3. Replace Zapier with native integration
4. Beta test with pilot agencies
5. Launch to broader ClearCare customer base

**Deliverables:**

- Production-ready ClearCare integration
- Listing in WellSky partner directory
- 20-50 customers onboarded

---

## 📊 Success Metrics

### Technical Metrics

- ✅ API uptime: >99.5%
- ✅ Response time: <2 seconds (voice interactions)
- ✅ Data sync latency: <5 minutes (Phase 1), <30 seconds (Phase 2)

### Business Metrics

- ✅ Agencies onboarded: 5 (Phase 1), 50 (Phase 2)
- ✅ Revenue: $2,500/month (Phase 1), $25k/month (Phase 2)
- ✅ No-show reduction: 30%+ (measured)
- ✅ EVV error reduction: 50%+ (measured)
- ✅ Admin time saved: 15-20 hours/week per agency

### Partnership Metrics

- ✅ WellSky partnership discussions initiated: Yes/No
- ✅ Partner program acceptance: Yes/No
- ✅ Co-marketing opportunities: # of webinars, blog posts, case studies

---

## 💡 Risks & Mitigations

### Risk 1: WellSky Builds Competing Feature

**Likelihood:** Medium  
**Impact:** High (could make Copper AI redundant)

**Mitigation:**

- Move fast (build integration before they do)
- Partner with WellSky (make them an ally, not competitor)
- Patent/IP protection (file provisional patent on voice-first EVV)
- Focus on superior UX (even if WellSky builds voice, Copper AI's will be better)

---

### Risk 2: API Access Denied

**Likelihood:** Low-Medium  
**Impact:** Medium (delays deep integration)

**Mitigation:**

- Phase 1 doesn't require API (use email/Zapier)
- Prove value with pilots → use traction to pressure WellSky for access
- Offer revenue share (incentivize WellSky to grant access)
- Alternative: Build integrations with Axxess, AlayaCare (other platforms)

---

### Risk 3: Low Adoption (Agencies Don't Use It)

**Likelihood:** Low (if we execute well)  
**Impact:** High (no revenue)

**Mitigation:**

- Free pilot period (prove value before charging)
- White-glove onboarding (train agencies + caregivers)
- Quantify ROI (show $5k/month savings > $500/month cost)
- Continuous improvement (listen to feedback, iterate)

---

## 🎯 Next Steps for Arvind

### This Week (Feb 3-7, 2026)

**Priority 1: Approve ClearCare Integration as Strategic Initiative**

- [ ] Review this document
- [ ] Decide: Go/No-Go on ClearCare integration
- [ ] If Go: Assign Nike to build Phase 1 MVP (2 weeks)

**Priority 2: Recruit Pilot Agencies**

- [ ] Reach out to current Texas customers: "Do you use ClearCare?"
- [ ] Target: 3-5 agencies willing to pilot ClearCare integration
- [ ] Offer: Free for 30 days + priority support

**Priority 3: Research WellSky Partnership Process**

- [ ] Find WellSky partnership contact (LinkedIn, website)
- [ ] Send initial outreach email (express interest in partnership)

---

### Next 30 Days (Feb-March 2026)

- [ ] Build Phase 1 MVP (Week 1-2)
- [ ] Launch pilot with 3-5 agencies (Week 3-4)
- [ ] Collect metrics + build case study (Week 3-6)
- [ ] Apply to WellSky Partner Program (Week 5)
- [ ] Demo to WellSky (Week 6-8)
- [ ] Decision: Partnership terms or go direct-to-market

---

## 🏆 The Prize

**If Copper AI successfully integrates with ClearCare:**

**Short-Term (6 months):**

- 50 ClearCare agencies × $500/month = **$25k MRR** ($300k ARR)
- Proven integration = sales asset for other platforms (Axxess, AlayaCare)

**Mid-Term (12 months):**

- 200 ClearCare agencies × $500/month = **$100k MRR** ($1.2M ARR)
- WellSky partnership or white-label deal
- Series A fundraising ($5-10M valuation)

**Long-Term (24 months):**

- 500+ agencies × $500/month = **$250k MRR** ($3M ARR)
- Acquisition target for WellSky ($20-50M)
- OR: Expand to other platforms (Axxess, AlayaCare) + scale to $10M ARR

**The ClearCare integration is the gateway to dominating the home health AI market.** 🚀

---

_Integration plan prepared by Nike, Feb 1, 2026_  
_Ready for immediate execution upon Arvind's approval_
