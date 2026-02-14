# Copper AI Product Roadmap 2026

_Created: Feb 2, 2026 | Nike's Strategic Product Plan_

**Mission:** Build the autonomous operations manager that home health agencies can't live without.

**Vision:** Every home health agency in America uses Copper AI by 2028.

---

## Executive Summary

This roadmap prioritizes **features that drive revenue** and **prevent churn**. Not everything that's cool should be built — only what agencies will pay for and competitors can't easily copy.

**Guiding Principles:**

1. **Revenue First:** Build features that unlock new customer segments or increase pricing power
2. **Moat Building:** Prioritize features competitors can't easily replicate (integrations, data network effects)
3. **Customer Success:** Reduce churn by solving pain points (no-shows, EVV, scheduling)
4. **Speed:** Ship fast, iterate based on real usage (not hypothetical features)

---

## Q1 2026 (Jan-Mar): Foundation & Proof

### 🎯 Goal: Prove Copper AI works with ClearCare & Axxess agencies

**Theme:** "Make 5-10 agencies wildly successful so they become case studies"

### P0 (Must Build - Blocks Revenue)

#### 1. ClearCare Integration (Zapier MVP) ✅

**Status:** In progress (Nike building)  
**Timeline:** 2 weeks  
**Effort:** 40 hours dev  
**Value:** Unlocks 4,500 ClearCare agencies

**Features:**

- Voice EVV clock-in/out → Auto-update ClearCare visit status
- Schedule changes from ClearCare → Trigger Copper AI calls
- No-show prevention: 2-hour pre-visit confirmation calls

**Why P0:** Can't sell to ClearCare agencies without this

#### 2. Basic Analytics Dashboard

**Timeline:** 2 weeks  
**Effort:** 30 hours dev  
**Value:** Agencies need proof of ROI to renew

**Metrics to Track:**

- No-show rate (before/after Copper AI)
- EVV compliance rate (% of visits with proper clock-in/out)
- Call volume (how many calls, avg duration)
- Cost savings ($$ from prevented no-shows)

**Why P0:** Renewals depend on proving ROI

#### 3. Multi-Language Support (Spanish)

**Timeline:** 1 week  
**Effort:** 20 hours (LLM already multilingual, just needs prompting)  
**Value:** 40% of home health caregivers are Spanish-speaking

**Implementation:**

- Detect language preference (ask during onboarding)
- TTS in Spanish (ElevenLabs supports 32 languages)
- LLM prompts in Spanish

**Why P0:** Missing 40% of market without this

### P1 (Should Build - Accelerates Growth)

#### 4. Axxess Integration (Zapier MVP)

**Timeline:** 2 weeks  
**Effort:** 40 hours (similar to ClearCare)  
**Value:** Unlocks 7,000 Axxess agencies (bigger than ClearCare!)

**Why P1 (not P0):** ClearCare first (smaller, faster to prove), then Axxess

#### 5. Agency Admin Portal

**Timeline:** 3 weeks  
**Effort:** 60 hours  
**Value:** Agencies can self-serve (reduces Arvind's support time)

**Features:**

- Add/remove caregivers
- View call logs & transcripts
- Update schedules
- See analytics dashboard
- Download reports (for state compliance audits)

**Why P1:** Reduces support burden, makes Copper AI feel professional

### P2 (Nice to Have - Can Wait)

#### 6. Voice Cloning (Custom Voices)

**Timeline:** 1 week  
**Effort:** 15 hours  
**Value:** Branding opportunity ("This is Sarah from ABC Home Care")

**Why P2:** Doesn't drive revenue, cool but not essential

#### 7. SMS Notifications

**Timeline:** 1 week  
**Effort:** 20 hours  
**Value:** Caregivers without phones can get text updates

**Why P2:** Phone calls work fine, SMS is incremental

---

## Q2 2026 (Apr-Jun): Scale & Retention

### 🎯 Goal: Onboard 50-100 customers, prevent churn, increase pricing power

**Theme:** "Make Copper AI indispensable"

### P0 (Must Build)

#### 8. Predictive No-Show Engine (THE KILLER FEATURE) 🌟

**Timeline:** 4 weeks  
**Effort:** 80 hours  
**Value:** **Increases pricing power to $800-1,000/month**

**How It Works:**

- Analyze historical data: Which caregivers no-show most? What patterns?
- Train ML model on:
  - Caregiver history (past no-shows)
  - Shift characteristics (late-night shifts = higher no-show)
  - Weather (snow/rain increases no-shows)
  - Day of week (Monday no-shows > Thursday)
- Score every upcoming visit: "High risk" (80% no-show chance) vs "Low risk" (5%)
- **Proactive intervention:**
  - High-risk visits → Extra confirmation call + backup caregiver alert
  - Moderate-risk → Standard confirmation
  - Low-risk → No intervention needed

**Why This is a 10x Feature:**

- **ROI multiplier:** Agencies currently lose 5-15% revenue to no-shows. Predictive engine reduces that to 2-3% = **2-5x ROI increase**
- **Defensible moat:** Requires data (more customers = better predictions = network effect)
- **Pricing power:** "We don't just prevent no-shows, we PREDICT them" = worth $800-1,000/month
- **Competitive advantage:** No other voice AI platform has this

**Success Metric:** Reduce no-show rate by 50-70% (vs 30-40% with basic confirmation calls)

#### 9. Native ClearCare Integration (API-Based)

**Timeline:** 6 weeks  
**Effort:** 120 hours  
**Value:** Zapier is slow & brittle. Native API = faster, more reliable, better UX

**Requirements:**

- Apply to WellSky Partner Program (4-6 week approval)
- OAuth 2.0 authentication
- Real-time data sync (not polling)
- Webhook support (ClearCare pushes updates to Copper AI)

**Why P0:** Zapier is a prototype. Production needs native integration.

#### 10. Caregiver Burnout Detection

**Timeline:** 3 weeks  
**Effort:** 60 hours  
**Value:** Prevents turnover (agencies lose $3-5k per caregiver who quits)

**How It Works:**

- Monitor caregiver patterns:
  - Overtime hours (>40 hours/week = burnout risk)
  - Last-minute call-ins (increasing frequency = disengagement)
  - Negative sentiment in voice calls (stressed tone)
- Alert agency admin:
  > "Warning: Sarah has worked 52 hours this week and called in sick twice. Burnout risk: HIGH. Consider giving her a lighter schedule."

**Why P0:** Turnover costs agencies $3-5k/caregiver. Preventing one quit = 6-10 months of Copper AI subscription.

### P1 (Should Build)

#### 11. Native Axxess Integration (API-Based)

**Timeline:** 6 weeks (parallel to ClearCare native)  
**Effort:** 120 hours  
**Value:** Same as ClearCare — native > Zapier

#### 12. Weekly ROI Reports (Auto-Generated)

**Timeline:** 2 weeks  
**Effort:** 40 hours  
**Value:** Prevents churn (agencies see ROI every week)

**What It Includes:**

- No-shows prevented (count + $$ saved)
- EVV compliance rate
- Caregiver satisfaction scores
- Cost savings vs Copper AI subscription ($6k saved vs $500 cost = 12:1 ROI)

**Delivery:** Email every Monday AM to agency owner + ops manager

**Why P1:** Retention tool (constant ROI reminders = less churn)

### P2 (Nice to Have)

#### 13. Voice Visit Notes

**Timeline:** 3 weeks  
**Effort:** 50 hours  
**Value:** Caregivers dictate notes instead of typing

**Example:**

> Caregiver: "Call Copper AI, log visit notes."  
> Copper AI: "Hi Sarah, I'm ready for notes on Mrs. Johnson's visit."  
> Caregiver: "She ate breakfast, took her meds, and we went for a short walk. She seemed happy today."  
> Copper AI: "Got it. Notes logged to ClearCare. Anything else?"  
> Caregiver: "Nope, that's it!"

**Why P2:** Cool feature, but doesn't drive revenue as much as predictive no-show

---

## Q3 2026 (Jul-Sep): Enterprise & Partnerships

### 🎯 Goal: Land 200-300 customers, secure ClearCare/Axxess partnerships, increase ACV to $800-1,000/month

**Theme:** "Become the category leader"

### P0 (Must Build)

#### 14. Enterprise Multi-Location Support

**Timeline:** 4 weeks  
**Effort:** 80 hours  
**Value:** Unlocks franchise customers (Comfort Keepers has 500+ locations!)

**Features:**

- Parent account (franchise HQ) + child accounts (each location)
- Consolidated billing (one invoice for all locations)
- Centralized reporting (HQ sees all locations' metrics)
- Role-based access (location managers see their data, HQ sees everything)

**Why P0:** Franchises = 10-500 locations per customer. Without this, can only sell to single-location agencies.

**Revenue Impact:**

- Comfort Keepers (500 locations) × $500/month = **$250k MRR from one customer**
- 10 franchise customers = **$2.5M MRR**

#### 15. Smart Routing (Optimized Scheduling)

**Timeline:** 5 weeks  
**Effort:** 100 hours  
**Value:** "Copper AI doesn't just manage schedules — it OPTIMIZES them"

**How It Works:**

- When caregiver calls in sick:
  > Copper AI: "Sarah called in sick. I found 3 backup caregivers within 5 miles. Should I call Maria first? She's available and has worked with this patient before."
- AI suggests optimal assignments based on:
  - Proximity (reduce drive time)
  - Caregiver skills (dementia care, wound care, etc.)
  - Patient preferences ("Mrs. Johnson likes Maria")
  - Availability (real-time)

**Why P0:** This moves Copper AI from "assistant" to "autonomous operations manager" (pricing power!)

#### 16. HIPAA Audit Logs

**Timeline:** 2 weeks  
**Effort:** 40 hours  
**Value:** Enterprise agencies require HIPAA compliance documentation

**Features:**

- Log every data access (who viewed what patient data, when)
- Immutable audit trail (can't delete logs)
- Export for compliance audits
- Encryption at rest + in transit (already have, just need docs)

**Why P0:** Blocks enterprise sales without this

### P1 (Should Build)

#### 17. Telephony Switch (Twilio → Telnyx/SignalWire)

**Timeline:** 3 weeks  
**Effort:** 60 hours  
**Value:** Reduce telephony costs by 50% ($0.02/min → $0.01/min)

**Why P1:** As volume scales, telephony costs matter. Twilio is premium-priced.

#### 18. AI Training Interface (Agency-Specific Prompts)

**Timeline:** 3 weeks  
**Effort:** 50 hours  
**Value:** Agencies can customize Copper AI's behavior

**Example:**

- Agency wants Copper AI to say "God bless you" at end of calls (religious agency)
- Agency wants stricter tone for caregivers who frequently no-show
- Agency wants Copper AI to mention specific policies

**Why P1:** Differentiation (white-label feel without white-label cost)

### P2 (Nice to Have)

#### 19. Slack/Teams Notifications

**Timeline:** 1 week  
**Effort:** 20 hours  
**Value:** Agency admins get alerts in Slack/Teams

**Why P2:** Email works fine, Slack is incremental

---

## Q4 2026 (Oct-Dec): Defensibility & Scale

### 🎯 Goal: 500+ customers, $3M+ ARR, raise Series A or get acquired

**Theme:** "Build the moat"

### P0 (Must Build)

#### 20. Caregiver Mobile App (Read-Only)

**Timeline:** 6 weeks  
**Effort:** 120 hours  
**Value:** Agencies keep asking for app (even though voice is better)

**Why Build It:**

- Not to replace voice (voice is core value prop)
- But to give option for tech-savvy caregivers
- "We support both voice AND app" = wider market

**Features (Read-Only):**

- View today's schedule
- See patient info (address, care plan)
- Call Copper AI button (launches voice call)
- NO clock-in/out via app (voice only, to preserve differentiation)

**Why P0:** Some agencies won't buy without an app (even if they don't use it)

#### 21. API for Third-Party Integrations

**Timeline:** 4 weeks  
**Effort:** 80 hours  
**Value:** Agencies can build custom workflows

**Examples:**

- Payroll integration (Copper AI sends worked hours to ADP/Paychex)
- Family portals (family members get updates on loved one's care)
- Billing systems (auto-generate invoices from visit data)

**Why P0:** Enterprise customers demand APIs

#### 22. Copper AI Voice Assistant (Alexa/Google Home)

**Timeline:** 5 weeks  
**Effort:** 100 hours  
**Value:** "Ambient AI" — caregivers don't even need to dial

**How It Works:**

- Agency gives each caregiver an Echo Dot ($25)
- Caregiver says: "Alexa, ask Copper AI to clock me in."
- Copper AI: "Clocked in for Mrs. Johnson's visit at 123 Main St. Have a great shift!"

**Why P0:** This is the **future of voice AI** (ambient, hands-free, frictionless)

**Competitive Advantage:** No other home health platform has Alexa integration

### P1 (Should Build)

#### 23. AI-Powered Quality Assurance

**Timeline:** 4 weeks  
**Effort:** 80 hours  
**Value:** Detect fraud, compliance issues automatically

**How It Works:**

- Analyze call patterns:
  - Caregiver clocks in from wrong GPS location (fraud detection)
  - Caregiver clocks in/out within 5 minutes (visit too short, quality issue)
  - Caregiver never mentions patient by name (scripted responses, low engagement)
- Alert agency admin:
  > "Warning: John clocked in for 3 visits today from the same GPS location (his home). Possible fraud."

**Why P1:** Prevents fraud (agencies lose 1-3% revenue to fraud), but not as high ROI as predictive no-show

#### 24. Compliance Automation (State-Specific)

**Timeline:** 6 weeks  
**Effort:** 100 hours  
**Value:** Different states have different EVV requirements

**Examples:**

- **Missouri:** Requires GPS + timestamp + task verification
- **California:** Requires patient signature (electronic)
- **Texas:** Requires 6 data points (who, what, when, where, task, patient signature)

**Auto-Detect State:** Based on agency address, apply correct compliance rules

**Why P1:** Blocks sales in certain states without this (e.g., Missouri hard edits April 2026)

### P2 (Nice to Have)

#### 25. White-Label Option

**Timeline:** 3 weeks  
**Effort:** 60 hours  
**Value:** Agencies want to brand it as their own

**Why P2:** Complicates support, reduces brand recognition. Only build if WellSky demands it for partnership.

---

## Feature Prioritization Framework

**How to decide what to build:**

### Revenue Impact Score

**Formula:** Revenue Impact = (TAM × Conversion Lift × ACV Increase) - Dev Cost

**Example:**

- **Predictive No-Show Engine:**
  - TAM: 33,000 agencies
  - Conversion Lift: +20% (agencies more likely to buy)
  - ACV Increase: +60% ($500 → $800)
  - Dev Cost: 80 hours × $150/hour = $12k
  - **Revenue Impact:** (33,000 × 0.20 × $300) - $12k = **$1.98M**

- **Voice Visit Notes:**
  - TAM: 33,000 agencies
  - Conversion Lift: +5% (nice-to-have)
  - ACV Increase: +0% (doesn't justify price increase)
  - Dev Cost: 50 hours × $150 = $7.5k
  - **Revenue Impact:** (33,000 × 0.05 × $0) - $7.5k = **-$7.5k** (negative ROI!)

**Conclusion:** Build predictive no-show engine, skip voice visit notes (for now)

### Moat Strength Score

**Question:** How hard is this for competitors to copy?

| Feature                          | Moat Strength | Why                                                                  |
| -------------------------------- | ------------- | -------------------------------------------------------------------- |
| **Predictive No-Show Engine**    | 🔒🔒🔒 HIGH   | Requires data (network effect). More customers = better predictions. |
| **Native ClearCare Integration** | 🔒🔒 MEDIUM   | Competitors can apply for API access, but takes time.                |
| **Voice EVV**                    | 🔒 LOW        | Competitors can build voice EVV easily.                              |

**Prioritize:** High moat features > Low moat features

---

## Revenue Projections by Quarter

| Quarter               | Customers | ACV                        | MRR   | ARR    |
| --------------------- | --------- | -------------------------- | ----- | ------ |
| **Q1 2026** (Current) | 10        | $500                       | $5k   | $60k   |
| **Q2 2026**           | 50        | $600 (predictive engine)   | $30k  | $360k  |
| **Q3 2026**           | 150       | $800 (enterprise features) | $120k | $1.44M |
| **Q4 2026**           | 300       | $800                       | $240k | $2.88M |

**Assumptions:**

- Q1: ClearCare integration → 10 pilots convert
- Q2: Predictive no-show engine → Increase ACV to $600, close 40 more agencies
- Q3: Enterprise features → Close 100 more agencies at $800/mo (franchises, multi-location)
- Q4: Scale → Double to 300 customers

**Series A Readiness:** Need $2-3M ARR + 20% MoM growth → **Q4 2026 is target**

---

## Tech Debt & Maintenance

**Allocate 20% of dev time to:**

1. **Bug fixes** (inevitable)
2. **Performance optimization** (as call volume scales)
3. **Security patches** (HIPAA compliance)
4. **Refactoring** (technical debt from early MVPs)

**Rule:** Every 4 weeks of new features → 1 week of tech debt cleanup

---

## What NOT to Build

### 🚫 Patient-Facing Features

**Why:** Home health agencies are B2B customers. Patients are end-users but not buyers. Don't build for patients unless agencies request it.

**Examples to Avoid:**

- Patient satisfaction surveys (agencies don't pay for this)
- Patient family portals (nice-to-have, not must-have)
- Patient medication reminders (out of scope)

### 🚫 Generalized AI Features

**Why:** Copper AI is vertical-specific (home health). Don't dilute focus.

**Examples to Avoid:**

- Sales call automation (use Vapi/Bland for this)
- Customer support chatbots (Intercom handles this)
- Appointment scheduling for non-healthcare (out of scope)

### 🚫 Hardware Products

**Why:** Software has 90% margins. Hardware has 20% margins. Stay in your lane.

**Examples to Avoid:**

- Copper AI smart speakers (just use Alexa/Google Home)
- Custom tablets for caregivers (agencies already have phones)
- Wearable devices (too hard to support)

---

## Success Metrics by Quarter

### Q1 2026

- ✅ 10 paying customers
- ✅ 3 ClearCare case studies
- ✅ $5k MRR

### Q2 2026

- ✅ 50 customers
- ✅ $30k MRR
- ✅ Predictive no-show engine live
- ✅ Native ClearCare integration

### Q3 2026

- ✅ 150 customers
- ✅ $120k MRR
- ✅ ClearCare or Axxess partnership signed

### Q4 2026

- ✅ 300 customers
- ✅ $240k MRR ($2.88M ARR)
- ✅ Series A term sheet OR acquisition offer

---

## Conclusion

**Focus = Speed**

Don't build everything. Build the 20% of features that drive 80% of revenue.

**Priorities:**

1. **Revenue unlocks:** ClearCare/Axxess integrations
2. **Pricing power:** Predictive no-show engine
3. **Retention:** Analytics dashboard, ROI reports
4. **Scale:** Enterprise features, API, Alexa integration

**Avoid:**

- Patient-facing features (wrong buyer)
- Generalized AI (out of scope)
- Hardware (low margin)

**Timeline:** Q1 = prove it works, Q2 = make it indispensable, Q3 = scale enterprise, Q4 = raise or exit

---

**Next Steps for Arvind:**

1. Review roadmap (agree/disagree on priorities?)
2. Approve Q1 features (ClearCare integration, analytics, Spanish support)
3. Nike can start building Q1 features this week
4. Revisit roadmap quarterly based on customer feedback

**Questions?** Let's discuss.

---

_Nike 🐾 | Product Strategy | Feb 2, 2026_
