# Copper AI Product Roadmap - 2026

**Version:** 1.0  
**Last Updated:** February 3, 2026  
**Owner:** Arvind Sarin  
**Contributors:** Nike (SarinAI)

---

## Vision

**"Make no-shows a thing of the past for every home health agency in America."**

By 2027, Copper AI will be:

- The #1 voice intelligence platform for home health
- Integrated with 80%+ of home health EMRs
- Serving 1,000+ agencies across all 50 states
- Preventing 1M+ no-shows per year
- Saving agencies $100M+ annually

---

## Q1 2026 (Feb-Apr): Foundation & Pilots

### Goals

- ✅ Prove the concept with real agencies
- ✅ Achieve product-market fit
- ✅ Build case studies for sales

### Milestones

**Week 1-4 (Feb 2026):**

- [x] Launch ClearCare integration (MVP complete)
- [x] Launch Axxess integration (MVP complete)
- [x] Launch unified server architecture (deployment-ready)
- [ ] Deploy to Railway production ($10/mo)
- [ ] Recruit 5 ClearCare pilot agencies
- [ ] Recruit 5 Axxess pilot agencies

**Week 5-8 (Mar 2026):**

- [ ] Onboard 10 pilot agencies (5 ClearCare + 5 Axxess)
- [ ] Achieve 80%+ caregiver adoption rate
- [ ] Collect weekly feedback, iterate based on learnings
- [ ] Build 3-5 case studies (with agency approval)

**Week 9-12 (Apr 2026):**

- [ ] Measure results: Target 40%+ no-show reduction
- [ ] Convert 3+ pilots to paying customers ($500-800/mo)
- [ ] Create video testimonials (2-3 agencies)
- [ ] Refine onboarding process (reduce time to value)

**Revenue Target:** $2,400 MRR (3 paying customers @ $800/mo)

---

## Q2 2026 (May-Jul): Scale & Partnerships

### Goals

- 🎯 Scale to 50 agencies
- 🤝 Secure strategic partnerships
- 📈 Achieve profitability

### Features to Build

#### 1. Multi-Language Support (May)

**Problem:** 30% of caregivers speak Spanish as primary language  
**Solution:** Add Spanish voice prompts + AI understanding

**Impact:**

- Expand addressable market by 30%
- Higher adoption rates in Hispanic caregiver population
- Competitive differentiator

**Effort:** 2-3 weeks (voice model training + testing)

---

#### 2. Advanced Analytics Dashboard (Jun)

**Problem:** Agencies want to dig deeper into data  
**Solution:** Web dashboard with drill-down analytics

**Features:**

- No-show trends by caregiver, patient, time, day of week
- Caregiver reliability scores (rank top/bottom performers)
- Patient difficulty scores (identify high-risk visits)
- Predictive staffing recommendations
- Export to CSV/Excel

**Impact:**

- Upsell opportunity ($200/mo add-on)
- Increases stickiness (agencies rely on insights)
- Enables data-driven operational improvements

**Effort:** 4-6 weeks (full-stack: backend + frontend)

---

#### 3. SMS/WhatsApp Backup (Jun)

**Problem:** Some caregivers prefer text over voice  
**Solution:** Offer choice (voice OR text confirmations)

**Features:**

- Send SMS confirmation 2 hours before shift
- Caregiver replies YES/NO
- If no response, escalate to voice call
- Still uses no-show predictor

**Impact:**

- Increases response rates (some prefer text)
- Reduces voice minute costs
- More flexibility = higher adoption

**Effort:** 1-2 weeks (Twilio SMS integration)

---

#### 4. WellSky Partnership (Jul)

**Problem:** ClearCare is owned by WellSky (4,500 agencies)  
**Solution:** Become official WellSky app marketplace partner

**What This Unlocks:**

- Listed in WellSky app marketplace (visibility to 4,500 agencies)
- Co-marketing opportunities (webinars, case studies)
- Faster integration approval (priority API access)
- Revenue share model (15-20% to WellSky, worth it for volume)

**Impact:**

- 10x distribution (ClearCare's sales team promotes us)
- Credibility boost ("Official WellSky Partner")
- Path to 500+ agencies in 12 months

**Effort:** 2 months (partnership negotiations + marketplace onboarding)

---

### Milestones

**Week 13-16 (May):**

- [ ] Launch multi-language support (Spanish)
- [ ] Recruit 15 additional agencies (5/month)
- [ ] Revenue: $6,000 MRR (10 paying @ $600 avg)

**Week 17-20 (Jun):**

- [ ] Launch advanced analytics dashboard
- [ ] Launch SMS/WhatsApp backup feature
- [ ] Recruit 15 additional agencies
- [ ] Revenue: $12,000 MRR (20 paying @ $600 avg)

**Week 21-24 (Jul):**

- [ ] Close WellSky partnership agreement
- [ ] Get listed in WellSky marketplace
- [ ] Recruit 20 additional agencies (partnership pipeline)
- [ ] Revenue: $24,000 MRR (40 paying @ $600 avg)

**Q2 Revenue Target:** $24,000 MRR | $288k ARR

---

## Q3 2026 (Aug-Oct): Market Leadership

### Goals

- 📊 Achieve category leader status
- 🚀 Scale to 200+ agencies
- 💰 $100k+ MRR

### Features to Build

#### 5. Caregiver App (iOS + Android) (Aug)

**Problem:** Some agencies want mobile app for advanced features  
**Solution:** Companion app (optional, voice still works without it)

**Features:**

- GPS check-in (for agencies that need it)
- View upcoming schedule
- Swap shifts with other caregivers
- Chat with office (HIPAA-compliant)
- Still supports voice EVV (call number from app)

**Impact:**

- Enables enterprise upsell ($1,200-2,000/mo)
- Competitive parity (EMRs have apps)
- Younger caregivers prefer apps

**Effort:** 8-12 weeks (native iOS + Android)

---

#### 6. Automated Shift Swapping (Sep)

**Problem:** When caregiver can't make shift, finding backup is manual  
**Solution:** AI recommends + contacts backup automatically

**How It Works:**

1. Caregiver calls: "I can't make my 2pm shift"
2. AI analyzes: Who's available? Who's nearby? Who's reliable?
3. AI ranks top 3 backup options
4. AI calls #1: "Hi Maria, can you cover Sarah's 2pm visit?"
5. If yes → Update EMR, notify agency + client
6. If no → Try #2, then #3
7. If all no → Alert agency immediately

**Impact:**

- Reduces admin time by 70% (automated backup finding)
- Faster response (minutes vs hours)
- Higher fill rate (more options explored)
- Premium feature ($400/mo add-on)

**Effort:** 3-4 weeks (logic + integrations)

---

#### 7. Patient Satisfaction Surveys (Oct)

**Problem:** Agencies don't know if clients are happy until they complain  
**Solution:** Automated post-visit surveys via voice call

**How It Works:**

1. After caregiver clocks out, AI calls patient/family
2. "Hi, this is ABC Home Health. How was Sarah's visit today?"
3. Ask 3-5 questions (quality, punctuality, professionalism)
4. Record feedback + sentiment score (1-10)
5. Flag low scores (< 7) for immediate follow-up
6. Weekly satisfaction reports

**Impact:**

- Catch issues before they escalate
- Improve caregiver training (identify weaknesses)
- Retention (happy clients = longer relationships)
- Upsell opportunity ($200/mo add-on)

**Effort:** 2-3 weeks (voice flows + analytics)

---

### Milestones

**Week 25-28 (Aug):**

- [ ] Launch caregiver mobile app (iOS + Android)
- [ ] Close Axxess partnership (similar to WellSky)
- [ ] Recruit 30 agencies (via partnerships)
- [ ] Revenue: $42,000 MRR (70 agencies @ $600 avg)

**Week 29-32 (Sep):**

- [ ] Launch automated shift swapping
- [ ] Attend Home Care Association conference (booth)
- [ ] Recruit 40 agencies (conference + partnerships)
- [ ] Revenue: $66,000 MRR (110 agencies @ $600 avg)

**Week 33-36 (Oct):**

- [ ] Launch patient satisfaction surveys
- [ ] Publish "State of No-Shows" industry report
- [ ] Recruit 50 agencies (inbound from report)
- [ ] Revenue: $96,000 MRR (160 agencies @ $600 avg)

**Q3 Revenue Target:** $96,000 MRR | $1.15M ARR

---

## Q4 2026 (Nov-Dec): Expansion & Scale

### Goals

- 🌎 Multi-market expansion
- 🏢 Enterprise tier launch
- 💵 $150k+ MRR

### Features to Build

#### 8. Multi-Location Support (Nov)

**Problem:** Large agencies have 5-20 locations, want centralized management  
**Solution:** Enterprise tier with multi-location dashboard

**Features:**

- Centralized admin panel (all locations in one view)
- Compare performance across locations
- Shared caregiver pool (work at multiple locations)
- Location-specific settings (different confirmation timing)
- White-label option (rebrand as agency's own tool)

**Impact:**

- Enables enterprise sales (10-50 locations × $2,000-5,000/mo)
- Locks in large customers (harder to switch)
- Higher LTV (lifetime value)

**Effort:** 4-6 weeks (architecture refactor + UI)

---

#### 9. Integration Marketplace (Dec)

**Problem:** Agencies use 5-10 tools (payroll, HR, benefits, etc.)  
**Solution:** Plugin marketplace for 3rd-party integrations

**Launch Partners:**

- Payroll: Gusto, ADP
- HR: BambooHR, Rippling
- Communication: Slack, Microsoft Teams
- Analytics: Tableau, Looker
- More: Zapier (500+ apps)

**Impact:**

- Increases stickiness (hub of agency's tech stack)
- Enables app ecosystem (other devs build on our platform)
- Revenue share opportunities

**Effort:** 6-8 weeks (API + marketplace UI)

---

#### 10. Predictive Staffing (Dec)

**Problem:** Agencies struggle with staffing (too many or too few caregivers)  
**Solution:** AI forecasts demand + recommends hiring/reducing hours

**How It Works:**

1. Analyze historical data (visit patterns, growth, seasonality)
2. Predict demand for next 30-90 days
3. Compare to current staffing levels
4. Recommend: "Hire 3 caregivers by March" or "Reduce hours 10%"
5. Predict ROI of recommendation

**Impact:**

- Solves a different (but related) problem (staffing)
- Opens new market (workforce planning tools)
- Premium feature ($500/mo add-on)

**Effort:** 4-6 weeks (ML model + UI)

---

### Milestones

**Week 37-40 (Nov):**

- [ ] Launch multi-location support
- [ ] Close 5 enterprise deals ($2,000-5,000/mo each)
- [ ] Recruit 30 SMB agencies
- [ ] Revenue: $120,000 MRR (180 agencies @ $667 avg)

**Week 41-44 (Dec):**

- [ ] Launch integration marketplace
- [ ] Launch predictive staffing
- [ ] Recruit 20 agencies (holiday slowdown)
- [ ] Revenue: $150,000 MRR (200 agencies @ $750 avg)

**Q4 Revenue Target:** $150,000 MRR | $1.8M ARR

---

## 2027 Outlook

### Goals

- 1,000 agencies (5x growth)
- $500k MRR ($6M ARR)
- Series A funding ($5-10M)
- Expand beyond home health (hospice, senior living, etc.)

### Big Bets

**1. Vertical Expansion**

- Hospice agencies (similar workflow, 5,000+ agencies)
- Senior living facilities (assisted living, memory care)
- Private duty (non-medical care)

**2. Geographic Expansion**

- Canada (5,000+ agencies)
- UK (10,000+ agencies)
- Australia (3,000+ agencies)

**3. Platform Play**

- Open API (let others build on Copper AI)
- Agency app marketplace (agencies sell their custom features)
- Data insights marketplace (anonymized benchmarking)

---

## Resource Planning

### Team Needs (2026)

**Current:** Arvind (founder) + Nike (AI assistant)

**Q1-Q2 Hires:**

- Customer Success Manager (Jun) - $60k-80k
  - Onboard pilots, collect feedback, drive adoption
  - Critical for scaling beyond 20 agencies

**Q3-Q4 Hires:**

- Full-Stack Engineer (Aug) - $120k-150k
  - Build mobile app, dashboard, integrations
  - Arvind can't code everything solo
- Sales/BDR (Oct) - $50k + commission
  - Outbound to agencies, book demos
  - Frees Arvind to focus on product + partnerships

**2027 Hires:**

- VP Engineering (Q1) - $150k-200k
- 2-3 Engineers (Q1-Q2) - $120k-150k each
- VP Sales (Q2) - $150k + equity
- Marketing Manager (Q3) - $80k-100k

---

## Budget (2026)

### Revenue Forecast

- Q1: $2,400 MRR (3 customers)
- Q2: $24,000 MRR (40 customers)
- Q3: $96,000 MRR (160 customers)
- Q4: $150,000 MRR (200 customers)

**Total 2026 Revenue:** ~$500k

### Costs

- **Infrastructure:** $10-50/mo (Railway), $100-500/mo (voice minutes) = $150-600/mo
- **Tools:** $200/mo (Retell, ElevenLabs, Zapier, etc.)
- **Salaries:** $0 (Q1-Q2), $100k (Q3), $200k (Q4)
- **Marketing:** $2k/mo (ads, conferences, content)
- **Ops:** $1k/mo (legal, accounting, misc)

**Total 2026 Costs:** ~$300k

**Net Profit:** ~$200k (40% margin)

---

## Risks & Mitigation

### Risk 1: Pilots don't convert to paid

**Probability:** Medium  
**Impact:** High (kills momentum)

**Mitigation:**

- Set clear expectations during pilot (this is a 60-day trial)
- Show ROI weekly (don't wait until end)
- Get executive sponsor buy-in early
- Offer discount for early adopters ($500/mo → $400/mo first 6 months)

---

### Risk 2: Competitors move faster

**Probability:** Low-Medium  
**Impact:** High (market share loss)

**Mitigation:**

- First-mover advantage (launch NOW, perfect later)
- Patent no-show predictor algorithm
- Lock in EMR partnerships (exclusive deals)
- Build switching costs (agencies rely on our data)

---

### Risk 3: Scaling breaks the system

**Probability:** Medium  
**Impact:** Medium (churn if quality drops)

**Mitigation:**

- Monitor performance metrics (latency, uptime)
- Set up alerts (Sentry, PagerDuty)
- Load test before hitting 100 agencies
- Build auto-scaling (Railway handles this)

---

### Risk 4: Churn exceeds growth

**Probability:** Low  
**Impact:** High (death spiral)

**Mitigation:**

- Measure NPS monthly (target 8+/10)
- Proactive customer success (weekly check-ins first 90 days)
- Fast support (respond within 4 hours)
- Product-led retention (agencies see value = they stay)

---

## Success Metrics

### North Star Metric

**No-shows prevented per month** (across all agencies)

**Why:** This is the core value we deliver. More no-shows prevented = happier agencies = more revenue.

### Secondary Metrics

- **Revenue:** MRR, ARR, growth rate
- **Agencies:** Total, new, churned, net retention
- **Adoption:** % caregivers using, calls per caregiver
- **Quality:** No-show reduction %, prediction accuracy
- **Efficiency:** Time to onboard, support tickets, NPS

### Monthly Dashboard

| Metric                 | Q1 Target | Q2 Target | Q3 Target | Q4 Target |
| ---------------------- | --------- | --------- | --------- | --------- |
| **Agencies**           | 10        | 40        | 160       | 200       |
| **MRR**                | $2.4k     | $24k      | $96k      | $150k     |
| **No-Shows Prevented** | 500/mo    | 2k/mo     | 8k/mo     | 12k/mo    |
| **NPS**                | 8+        | 8+        | 9+        | 9+        |
| **Churn**              | 0%        | <5%       | <5%       | <3%       |

---

## Conclusion

Copper AI has product-market fit potential. The no-show problem is real, expensive, and unsolved. Our solution is differentiated (voice + prediction), fast to deploy (3 days), and delivers clear ROI (9.6:1).

**The opportunity:**

- 33,000 agencies in US (TAM: $198M ARR at $500/mo)
- 11,500 agencies using ClearCare/Axxess (SAM: $69M ARR)
- Path to $6M ARR in 2 years is realistic

**The plan:**

- Prove it (Q1): 10 pilots → case studies
- Scale it (Q2-Q3): 200 agencies via partnerships
- Dominate it (Q4-2027): Category leader, expand verticals

**What we need:**

- Focus (say no to distractions)
- Speed (ship fast, iterate based on feedback)
- Resilience (some pilots will fail, some features will flop)

**Let's build this. 🚀**

---

_Roadmap by Nike 🐾 | February 2026 | Review monthly, revise quarterly_
