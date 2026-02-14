# iCare Customer Onboarding Playbook

**Version:** 1.0  
**Date:** January 31, 2026  
**For:** New home health agency customers  
**Goal:** Get agencies from "signed contract" to "live operations" in 14 days

---

## 📋 Overview

This playbook outlines the complete iCare onboarding process for new home health agency customers. Following this process ensures smooth implementation, minimal disruption, and maximum ROI.

**Timeline:** 14 days from contract signing to go-live  
**Success Rate Target:** 95% of agencies live within 14 days  
**Customer Satisfaction Target:** 4.5/5 stars post-onboarding

---

## 🎯 Onboarding Goals

By the end of 14 days, the agency will have:

1. ✅ iCare voice AI answering 100% of calls
2. ✅ Integration with their home health software (AxisCare, ClearCare, etc.)
3. ✅ Caregiver shift confirmations automated
4. ✅ Patient intake workflow configured
5. ✅ After-hours call handling active
6. ✅ EVV compliance automation enabled
7. ✅ Team trained on iCare dashboard
8. ✅ First 50+ calls successfully handled

---

## 📅 14-Day Implementation Timeline

### **Phase 1: Discovery & Setup (Days 1-3)**

#### Day 1: Kickoff Call (60 min)

**Attendees:**

- Agency owner or office manager
- iCare implementation specialist (you)
- Optional: DON (Director of Nursing)

**Agenda:**

1. Welcome & introductions (5 min)
2. Review contract & deliverables (10 min)
3. Discovery questions (30 min):
   - What home health software do you use?
   - What's your current call volume?
   - What are your biggest pain points?
   - What workflows do you want to automate?
   - What's your EVV system?
   - Do you have multiple locations?
   - What languages do your clients speak?
4. Set expectations (10 min):
   - Timeline: 14 days to go-live
   - Your role vs. our role
   - Communication plan (Slack channel, weekly check-ins)
5. Assign homework (5 min):
   - Send us sample call scripts
   - Provide login to home health software (read-only access)
   - Share EVV system details

**Deliverables:**

- [ ] Discovery questionnaire completed
- [ ] Agency assigned a dedicated Slack channel
- [ ] Implementation plan customized to their needs

#### Day 2: Technical Setup (Internal)

**Tasks:**

- [ ] Create agency account in iCare platform
- [ ] Set up phone number forwarding (or new number if requested)
- [ ] Configure timezone (CST, PST, etc.)
- [ ] Set business hours (8am-5pm typical, or custom)
- [ ] Upload logo and branding assets (if white-label)

**Deliverables:**

- [ ] Agency account provisioned
- [ ] Phone number assigned
- [ ] Branding applied (if applicable)

#### Day 3: Software Integration Setup

**Tasks:**

- [ ] Request API keys for home health software (AxisCare, ClearCare, WellSky, AlayaCare)
- [ ] Test API connection
- [ ] Configure data sync:
  - Patient list (name, phone, address, care plan)
  - Caregiver list (name, phone, availability, certifications)
  - Visit schedule (upcoming shifts)
- [ ] Test read/write permissions

**Common Integrations:**
| Software | Integration Method | Setup Time |
|----------|-------------------|------------|
| AxisCare | REST API | 2 hours |
| ClearCare | Zapier + API | 3 hours |
| WellSky | SFTP + API | 4 hours |
| AlayaCare | REST API | 2 hours |
| Sandata (EVV) | REST API | 2 hours |

**Deliverables:**

- [ ] API integration tested and working
- [ ] Data sync confirmed (patients, caregivers, visits)
- [ ] Error handling configured

---

### **Phase 2: Workflow Configuration (Days 4-7)**

#### Day 4: Call Flow Design

**Tasks:**

- [ ] Design inbound call flow:
  1. Greeting: "Thank you for calling [Agency Name]. How can I help you today?"
  2. Intent detection: New patient? Existing patient? Caregiver? Family member?
  3. Routing: Transfer to human or handle via AI?
  4. Data capture: Name, phone, callback number, reason for call
- [ ] Design after-hours flow:
  - "We're closed right now. Our office hours are [hours]. Would you like to leave a message or schedule a callback?"
  - Emergency escalation: "If this is a medical emergency, please hang up and dial 911."
- [ ] Design caregiver shift confirmation flow:
  - "Hi [Caregiver Name], this is [Agency Name]. You have a shift tomorrow at [time] with [Patient Name] at [address]. Can you confirm you'll be there?"
  - Response handling: Yes → Log confirmation. No → Alert office, find replacement.

**Deliverables:**

- [ ] Inbound call flow diagram approved by agency
- [ ] After-hours flow configured
- [ ] Shift confirmation flow configured

#### Day 5: Voice & Language Customization

**Tasks:**

- [ ] Select voice profile:
  - Male or female voice?
  - Accent: Neutral American, Southern, Hispanic, Filipino, etc.
  - Tone: Warm and friendly vs. professional and efficient
- [ ] Configure multilingual support (if needed):
  - Spanish (most common)
  - Tagalog (Filipino agencies)
  - Vietnamese
  - Mandarin
- [ ] Test voice quality on sample calls

**Deliverables:**

- [ ] Voice profile selected and approved
- [ ] Multilingual support enabled (if needed)
- [ ] 5 test calls completed by agency owner (feedback incorporated)

#### Day 6: EVV & Compliance Automation

**Tasks:**

- [ ] Configure EVV integration (Sandata, HHAeXchange, CareSmartz, etc.)
- [ ] Set up automated visit confirmations:
  - Call caregiver 24 hours before shift
  - Call caregiver 1 hour before shift (reminder)
  - Call patient to confirm visit
- [ ] Configure EVV data capture:
  - Date/time of visit
  - Caregiver ID
  - Patient ID
  - Services performed
  - Location (GPS if applicable)
- [ ] Set up Medicaid compliance alerts:
  - Missing EVV = alert to office
  - Late visit = alert to office

**Deliverables:**

- [ ] EVV integration tested
- [ ] Automated visit confirmations active
- [ ] Compliance alerts configured

#### Day 7: Dashboard & Reporting Setup

**Tasks:**

- [ ] Create agency admin accounts (owner, office manager, DON)
- [ ] Set up role-based permissions:
  - Owner: Full access
  - Office manager: Call logs, scheduling, caregiver management
  - DON: Patient care plans, clinical alerts
- [ ] Configure reports:
  - Daily call summary (emailed at 5pm)
  - Weekly caregiver no-show report
  - Monthly EVV compliance report
- [ ] Set up real-time alerts:
  - Caregiver no-show → SMS to office manager
  - Patient emergency call → SMS + phone call to on-call nurse
  - EVV missing → Email to compliance officer

**Deliverables:**

- [ ] Admin accounts created
- [ ] Reports configured and delivered on schedule
- [ ] Alerts tested (test no-show, test emergency call)

---

### **Phase 3: Testing & Training (Days 8-11)**

#### Day 8: Internal Testing

**Tasks:**

- [ ] iCare team performs 20 test calls:
  - 10 inbound patient calls (new patient, existing patient, family member)
  - 5 outbound caregiver confirmations
  - 5 after-hours calls
- [ ] Identify and fix issues:
  - Voice recognition errors
  - Incorrect routing
  - Data sync failures
  - Integration bugs
- [ ] Run stress test:
  - 10 concurrent calls
  - Verify latency <500ms
  - Verify no dropped calls

**Deliverables:**

- [ ] All test calls passed (95% success rate minimum)
- [ ] Bugs identified and fixed
- [ ] System ready for agency testing

#### Day 9: Agency Team Training (90 min session)

**Attendees:**

- Office manager
- Front desk staff
- DON
- Owner

**Agenda:**

1. **Dashboard Overview (20 min)**
   - How to view live calls
   - How to listen to call recordings
   - How to read transcripts
   - How to view analytics (call volume, resolution rate, no-show rate)

2. **Call Management (20 min)**
   - How to manually transfer a call to a human
   - How to override AI for specific callers (VIP patients)
   - How to block spam calls
   - How to add notes to call logs

3. **Caregiver Management (15 min)**
   - How to add/remove caregivers
   - How to update caregiver availability
   - How to view caregiver confirmation history

4. **Patient Management (15 min)**
   - How to add/remove patients
   - How to update patient care plans
   - How to set patient preferences (language, caregiver gender, etc.)

5. **Reports & Alerts (10 min)**
   - How to customize reports
   - How to set up custom alerts
   - How to export data (CSV, Excel)

6. **Q&A (10 min)**

**Deliverables:**

- [ ] Training session recorded (for future reference)
- [ ] Training materials sent to attendees (PDF guide)
- [ ] Quiz completed by attendees (80% pass rate required)

#### Day 10: Live Testing with Agency

**Tasks:**

- [ ] Agency team makes 10 test calls to iCare:
  - 5 calls from agency owner (pretending to be patient)
  - 5 calls from office manager (pretending to be caregiver)
- [ ] iCare team observes calls in real-time
- [ ] Collect feedback:
  - Did the AI understand the request?
  - Was the response accurate?
  - Was the voice natural and friendly?
  - Did the call transfer work (if needed)?
  - Did the data sync correctly?
- [ ] Make adjustments based on feedback

**Deliverables:**

- [ ] 10 test calls completed
- [ ] Feedback incorporated (voice tweaks, flow changes, etc.)
- [ ] Agency owner signs off on readiness

#### Day 11: Soft Launch Preparation

**Tasks:**

- [ ] Set up call forwarding from agency's main number to iCare
  - Option 1: Forward ALL calls to iCare
  - Option 2: Forward only after-hours calls to iCare (gradual rollout)
  - Option 3: Forward overflow calls (if main line is busy)
- [ ] Configure escalation paths:
  - If AI can't handle call → transfer to office manager
  - If office manager unavailable → voicemail + email notification
  - If emergency → transfer to on-call nurse
- [ ] Create backup plan:
  - If iCare has downtime → calls forward to agency's original number
  - If agency wants to disable iCare temporarily → one-click toggle in dashboard

**Deliverables:**

- [ ] Call forwarding configured
- [ ] Escalation paths tested
- [ ] Backup plan documented

---

### **Phase 4: Go-Live & Support (Days 12-14)**

#### Day 12: Soft Launch (After-Hours Only)

**Strategy:** Start with low-risk after-hours calls to build confidence

**Tasks:**

- [ ] Enable call forwarding after 5pm (business hours remain manual)
- [ ] Monitor all calls in real-time for first 2 evenings
- [ ] Capture metrics:
  - Call volume
  - Resolution rate (AI resolved vs. transferred to human)
  - Average call duration
  - Caller satisfaction (if collected via post-call survey)
- [ ] Daily check-in with agency owner (15 min call)

**Deliverables:**

- [ ] First 10-20 after-hours calls handled successfully
- [ ] Feedback from agency: "Ready for full launch" or "Need more tweaks"

#### Day 13: Full Launch (All Hours)

**Tasks:**

- [ ] Enable call forwarding 24/7
- [ ] Send announcement to patients/caregivers (optional):
  - "We've upgraded our phone system with AI assistance for faster service!"
- [ ] Monitor first 50 calls closely
- [ ] Set up emergency hotline (agency can call Copper Digital if issues arise)

**Deliverables:**

- [ ] iCare handling 100% of calls
- [ ] No major issues reported
- [ ] Agency team comfortable with system

#### Day 14: Post-Launch Review

**Tasks:**

- [ ] 30-minute review call with agency owner
- [ ] Review metrics:
  - Total calls handled
  - Resolution rate
  - Caregiver no-show rate (before vs. after iCare)
  - Time saved (estimate based on call volume)
  - Cost savings (admin time freed up)
- [ ] Collect testimonial (if agency is happy)
- [ ] Identify opportunities for optimization:
  - Which call types need better AI handling?
  - Which workflows can be further automated?
- [ ] Transition to ongoing support plan

**Deliverables:**

- [ ] Onboarding marked complete ✅
- [ ] Metrics dashboard shared with agency
- [ ] Testimonial collected (for marketing)
- [ ] Agency added to monthly check-in schedule

---

## 📊 Success Metrics

### **Onboarding Success Criteria**

| Metric                          | Target                                       | How to Measure                   |
| ------------------------------- | -------------------------------------------- | -------------------------------- |
| **Go-live within 14 days**      | 95% of customers                             | Track onboarding timeline        |
| **AI resolution rate**          | >70% of calls handled without human transfer | iCare analytics dashboard        |
| **Caregiver no-show reduction** | 30-40% decrease                              | Compare pre-iCare vs. post-iCare |
| **Admin time saved**            | 10+ hours/week                               | Survey agency after 30 days      |
| **Customer satisfaction**       | 4.5/5 stars                                  | Post-onboarding survey           |
| **Call quality**                | 90%+ positive sentiment                      | AI sentiment analysis            |
| **Zero critical bugs**          | No system-breaking issues during onboarding  | Bug tracker                      |

### **30-Day Post-Launch Review**

**Schedule a 30-day check-in to review:**

- Total calls handled (goal: 100+ calls/month minimum)
- AI resolution rate (goal: >70%)
- Caregiver confirmation rate (goal: >90%)
- Patient satisfaction (goal: 4/5 stars)
- ROI calculation:
  - Time saved: 10 hrs/week × $20/hr = $200/week = $867/month
  - Cost: $297/month
  - **Net ROI:** $570/month ($6,840/year)

---

## 🚨 Common Onboarding Challenges & Solutions

### Challenge 1: Agency Delays Providing API Keys

**Symptom:** Day 3 arrives, still no API access to home health software

**Solution:**

- Send reminder email with clear instructions (include screenshots)
- Offer to schedule 15-min call to walk them through it
- Escalate to agency owner if office manager is unrespive
- If delay exceeds 3 days, push back go-live date and notify agency

### Challenge 2: Voice Doesn't Sound Natural

**Symptom:** Agency owner says "AI sounds too robotic"

**Solution:**

- Offer 3 alternative voice profiles (male, female, different accents)
- Adjust speaking pace (slower for elderly patients, faster for caregivers)
- Add filler words ("um," "you know") to sound more human
- Use ElevenLabs premium voices (higher quality)

### Challenge 3: Integration Issues with Home Health Software

**Symptom:** Data sync failing between iCare and AxisCare/ClearCare

**Solution:**

- Check API keys are correct (common copy-paste error)
- Verify IP whitelisting (if required by software vendor)
- Test with sample data first, then full sync
- If vendor API is unreliable, fall back to CSV export/import (manual but works)

### Challenge 4: Agency Wants Too Much Customization

**Symptom:** Agency asks for 20 custom workflows, each highly specific

**Solution:**

- Focus on top 3 workflows first (80/20 rule)
- Explain that simple workflows = higher success rate
- Offer advanced customization as post-launch enhancement (additional fee)
- Set expectations: "We'll get you live with core features, then iterate"

### Challenge 5: Staff Resistance to AI

**Symptom:** Front desk staff worried AI will replace their jobs

**Solution:**

- Emphasize AI handles _routine_ calls, humans handle _complex_ calls
- Position as "freeing you up to do higher-value work"
- Show testimonials from other agencies where staff love iCare
- Involve staff in testing/training (makes them feel ownership)

---

## 📞 Communication Plan

### Weekly Check-Ins (During Onboarding)

**Schedule:**

- **Day 1:** Kickoff call (60 min)
- **Day 4:** Progress update call (30 min)
- **Day 7:** Mid-point review call (30 min)
- **Day 9:** Training session (90 min)
- **Day 11:** Pre-launch readiness call (30 min)
- **Day 14:** Post-launch review (30 min)

**Between calls:**

- Daily Slack updates (iCare team posts progress)
- Agency can ask questions anytime in Slack channel
- Emergency hotline: (469) 742-1095 (Arvind's direct line for urgent issues)

### Post-Launch Communication

**Monthly check-ins (first 3 months):**

- 30-min call to review metrics
- Identify optimization opportunities
- Collect feedback for product improvements

**Quarterly business reviews (after 3 months):**

- 60-min call with agency owner + iCare leadership
- Review ROI, usage trends, expansion opportunities
- Discuss new features, integrations, or services

---

## 🛠️ Tools & Resources

### For iCare Implementation Team

- **Project Management:** Asana (onboarding checklist template)
- **Communication:** Slack (dedicated channel per agency)
- **Documentation:** Google Drive (shared folder with agency)
- **Call Monitoring:** iCare dashboard (live call view)
- **Support Ticketing:** Zendesk (for post-launch support)

### For Agency

- **Training Materials:** PDF guide, video tutorials (Loom)
- **Dashboard Access:** iCare web app (login credentials sent Day 7)
- **Support:** Slack channel, email (support@copperdigital.com), phone
- **Knowledge Base:** help.copperdigital.com (FAQ, troubleshooting guides)

---

## ✅ Onboarding Checklist (Summary)

**Phase 1: Discovery & Setup (Days 1-3)**

- [ ] Kickoff call completed
- [ ] Discovery questionnaire filled out
- [ ] Agency account created
- [ ] Phone number assigned
- [ ] API integration configured

**Phase 2: Workflow Configuration (Days 4-7)**

- [ ] Call flows designed and approved
- [ ] Voice profile selected
- [ ] EVV integration tested
- [ ] Dashboard and reports configured

**Phase 3: Testing & Training (Days 8-11)**

- [ ] Internal testing passed (20 calls)
- [ ] Agency team trained (90-min session)
- [ ] Live testing with agency (10 calls)
- [ ] Soft launch prepared (call forwarding configured)

**Phase 4: Go-Live & Support (Days 12-14)**

- [ ] Soft launch (after-hours calls)
- [ ] Full launch (24/7 calls)
- [ ] Post-launch review completed
- [ ] Onboarding marked complete ✅

---

## 📈 Post-Onboarding Optimization

### Month 1: Stabilization

**Goals:**

- Maintain >95% uptime
- Achieve >70% AI resolution rate
- Collect 10+ customer testimonials (patients/caregivers calling in)

**Tasks:**

- Weekly check-ins with agency
- Fix any bugs or issues immediately
- Optimize call flows based on real-world usage

### Month 2: Expansion

**Goals:**

- Increase AI resolution rate to >80%
- Add 1-2 new automated workflows
- Reduce caregiver no-show rate by 40%

**Tasks:**

- Analyze top 5 call types that get transferred to humans
- Build AI workflows to handle those call types
- Implement predictive scheduling (AI suggests best caregiver for each patient)

### Month 3: ROI Validation

**Goals:**

- Document quantifiable ROI (time saved, revenue increased)
- Collect video testimonial from agency owner
- Upsell to premium features (advanced analytics, white-label, etc.)

**Tasks:**

- Calculate time saved: (avg call duration) × (calls handled by AI) / 60 = hours saved
- Calculate cost savings: hours saved × $20/hr wage = monthly savings
- Compare to iCare cost ($297/mo) to show net ROI
- Use ROI story in marketing materials for other agencies

---

## 🎯 Key Takeaways for Implementation Team

1. **Speed Matters:** Get agencies live in 14 days or they lose confidence
2. **Communication is Key:** Daily Slack updates prevent surprises
3. **Training = Adoption:** Well-trained staff = happy customers
4. **Start Simple:** Launch with core features, add complexity later
5. **Measure Everything:** Metrics prove ROI and identify opportunities

---

**Prepared by Nike 🐾**  
**For Copper Digital iCare Implementation Team**  
**Use this playbook to onboard every new customer consistently and successfully!**
