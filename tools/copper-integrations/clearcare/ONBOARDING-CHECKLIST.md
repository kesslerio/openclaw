# Agency Onboarding Checklist - ClearCare Integration

**Time Required:** 15-30 minutes per agency  
**Best Done:** Over video call (Zoom/Google Meet) with agency owner or operations manager

---

## Pre-Onboarding (Before Call)

### ✅ Agency Qualifications

- [ ] Active ClearCare account (verify account ID)
- [ ] 10+ caregivers (MVP works best with 10-50 caregivers)
- [ ] Email notifications enabled in ClearCare
- [ ] Has Google Drive or Dropbox (for schedule exports)
- [ ] Signed pilot agreement (see `sales/pilot-agreement-template.md`)

### ✅ Copper AI Setup

- [ ] Agency created in database (see SQL below)
- [ ] Unique webhook URL assigned: `copper.ai/webhook/{agency_id}`
- [ ] Google Sheets row created (caregiver directory, agency contacts)
- [ ] Zapier workflows tested (EVV, schedule sync, alerts)

**SQL to create agency:**

```sql
INSERT INTO agencies (name, owner_name, owner_phone, owner_email, plan, monthly_price, trial_end_date)
VALUES ('ABC Home Care', 'John Smith', '+14695551234', 'john@abchomecare.com', 'beta', 0.00, CURRENT_DATE + INTERVAL '90 days')
RETURNING id;
```

---

## Onboarding Call (15-30 Minutes)

### Part 1: Introduction (5 min)

**Say:**

> "Hi [Name]! Thanks for joining the Copper AI beta. Today we'll:
>
> 1. Configure ClearCare to talk to Copper AI (5 min)
> 2. Import your caregiver list (5 min)
> 3. Test with one caregiver (5 min)
> 4. Answer questions
>
> You should be up and running in 15-20 minutes. Sound good?"

**Check:**

- [ ] Agency understands 3-month free beta (no credit card required)
- [ ] Agency commits to weekly check-ins during pilot
- [ ] Agency will provide feedback & testimonial if successful

### Part 2: ClearCare Configuration (5 min)

#### Step 1: Enable Email Notifications

**Say:**

> "First, let's make sure ClearCare sends us schedule updates. In ClearCare, go to Settings → Notifications."

**Agency Actions:**

1. Log into ClearCare
2. Go to **Settings** → **Notifications**
3. Enable these notifications:
   - ✅ "New Visit Assigned" → Email to agency owner
   - ✅ "Visit Updated" → Email to agency owner
   - ✅ "Caregiver Schedule Changed" → Email to agency owner
4. Set notification email to agency owner's email

**Check:**

- [ ] Email notifications enabled
- [ ] Test email received (have them assign a fake visit)

#### Step 2: Forward ClearCare Emails

**Say:**

> "Now, let's forward ClearCare emails to Copper AI so we can trigger calls automatically."

**Agency Actions:**

1. Set up email forwarding rule in Gmail/Outlook:
   - From: `noreply@clearcareonline.com`
   - Forward to: `parse+{agency_id}@copper.ai`
   - Keep a copy: Yes
2. Test forwarding (send test email)

**Alternative (if they don't want to forward):**

- Use Zapier email parser directly (requires agency to give Zapier access)

**Check:**

- [ ] Email forwarding set up
- [ ] Test email received by Copper AI

### Part 3: Import Caregiver List (5 min)

**Say:**

> "Next, let's import your caregiver phone numbers so Copper AI knows who to call."

#### Option A: CSV Export (Recommended)

**Agency Actions:**

1. In ClearCare, go to **Reports** → **Caregiver List**
2. Export as CSV (should include: Name, Phone, Language, Status)
3. Upload to Google Drive folder: "Copper AI - ClearCare Data"

**Nike Actions:**

```bash
# Import CSV to database
cd /home/ubuntu/openclaw/tools/copper-integrations/clearcare
node scripts/import-caregivers.js --agency-id=1 --csv="path/to/caregivers.csv"
```

#### Option B: Manual Entry (Small Agencies)

If only 10-15 caregivers, manually add to Google Sheets:

- Sheet: "Copper AI - ClearCare Integration"
- Tab: "Caregiver Directory"
- Columns: Name, Phone, Language, Agency, Status

**SQL to import:**

```sql
INSERT INTO caregivers (phone, name, agency_id, language)
VALUES
  ('+14697421001', 'Maria Garcia', 1, 'es'),
  ('+14697421002', 'James Wilson', 1, 'en');
```

**Check:**

- [ ] All caregivers imported (verify count matches ClearCare)
- [ ] Phone numbers in E.164 format (+1...)
- [ ] Language preferences set (en/es)

### Part 4: Test Voice EVV (5 min)

**Say:**

> "Now let's test the Voice EVV. [Caregiver], can you call this number and clock in?"

**Test Caregiver Actions:**

1. Call hotline: `(469) 420-CARE` (or your number)
2. Say: "Hi, this is [Name]. I'm clocking in for [Client]."
3. Wait for AI confirmation

**Expected Outcome:**

- AI responds: "Thanks [Name], you're clocked in for [Client] at [Time]. Have a great visit!"
- Visit status updates in ClearCare to "In Progress"
- EVV log appears in Google Sheets

**Check:**

- [ ] Voice call completed successfully
- [ ] Transcript captured in database
- [ ] ClearCare visit status updated (via email or Zapier)
- [ ] Caregiver understands how to use it

**If it fails:**

- Check caregiver phone number is correct in database
- Check ClearCare visit exists for today
- Check Zapier webhook is active
- Review server logs for errors

### Part 5: Test No-Show Prevention (Optional)

**Say:**

> "Want to test the no-show prevention feature? Let's schedule a fake visit 2 hours from now."

**Agency Actions:**

1. Create test visit in ClearCare (2 hours from now)
2. Wait for Copper AI to call caregiver (automatic)
3. Caregiver confirms or declines
4. Agency receives alert if declined

**Check:**

- [ ] Confirmation call received 2 hours before visit
- [ ] Alert sent to agency owner if high risk
- [ ] Visit marked as confirmed in database

### Part 6: Training & Next Steps (5 min)

**Give Agency:**

- [ ] Training video (5 min): "How to Use Copper AI" (link in Drive)
- [ ] Quick reference card: "Caregiver Instructions" (PDF in Drive)
- [ ] Support contact: Arvind's phone/email + Telegram group
- [ ] Weekly check-in schedule (same day/time each week)

**Say:**

> "You're all set! Here's what happens next:
>
> 1. Your caregivers will start using Voice EVV immediately
> 2. Copper AI will call them 2 hours before each visit
> 3. You'll get alerts for any high-risk no-shows
> 4. We'll check in weekly to review data and make improvements
>
> Questions?"

**Schedule:**

- [ ] Weekly check-in call (same day/time)
- [ ] Week 4 review (ROI calculation)
- [ ] Week 8 testimonial (if successful)

---

## Post-Onboarding (After Call)

### ✅ Send Follow-Up Email

**Template:**

```
Subject: Welcome to Copper AI! 🎉

Hi [Name],

Thanks for joining the Copper AI beta! Here's a quick recap:

✅ ClearCare integration configured
✅ [X] caregivers imported
✅ Voice EVV tested successfully
✅ No-show prevention enabled

NEXT STEPS:
1. Share this hotline number with all caregivers: (469) 420-CARE
2. Print the attached Quick Reference Card (PDF)
3. Watch the 5-min training video: [link]
4. Join our Telegram support group: [link]

WEEKLY CHECK-IN:
We'll talk every [Day] at [Time] to review your no-show rates and make improvements.

QUESTIONS?
Text/call me anytime: +1 469 742 1095
Or Telegram: @SarinAI_bot

Excited to reduce your no-shows by 30-50%! 🚀

Arvind
Copper AI
arvind@copperdigital.com
```

**Attachments:**

- [ ] Quick Reference Card (PDF): "How to Use Voice EVV"
- [ ] Training video (link or MP4)
- [ ] Emergency support contacts

### ✅ Internal Setup

- [ ] Add agency to Monday CRM (or your CRM)
- [ ] Create Slack channel: #copper-abc-home-care
- [ ] Set up Telegram group (agency owner + Arvind + Nike)
- [ ] Schedule weekly check-in (Google Calendar invite)
- [ ] Add to Copper AI dashboard (agency metrics)

### ✅ Monitor First Week

**Daily (Days 1-7):**

- [ ] Check EVV call volume (should be 10-30 calls/day)
- [ ] Review confirmation call success rate (target: 80%+ answered)
- [ ] Watch for any caregiver confusion (update prompts if needed)
- [ ] Send daily summary to agency owner (Telegram/email)

**Week 1 Report:**

```
📊 WEEK 1 SUMMARY - [Agency Name]

EVV Calls: [X] clock-ins, [Y] clock-outs
Confirmation Calls: [Z] sent, [A]% answered
No-Show Rate: [B]% (baseline: ~20%)
Top Issue: [most common problem]

NEXT WEEK:
- [Action item 1]
- [Action item 2]

Great start! 🚀
```

---

## Troubleshooting Common Issues

### "Caregiver called but AI didn't understand"

**Diagnosis:**

- Check call transcript in database
- Likely: Caregiver didn't say client name clearly

**Fix:**

- Update voice prompt to ask: "Which client are you visiting?"
- Train caregivers to say: "I'm clocking in for [Client's First AND Last Name]"

### "ClearCare visit status not updating"

**Diagnosis:**

- Check Zapier task history for failed actions
- Likely: Email forwarding not working or Zapier disconnected

**Fix:**

- Re-authenticate Zapier connections
- Check email forwarding rule is active
- Manual workaround: Export EVV log from Google Sheets, import to ClearCare

### "Caregivers not answering confirmation calls"

**Diagnosis:**

- Check call success rate (under 50% is a problem)
- Likely: Caregivers don't recognize the number

**Fix:**

- Use agency owner's phone number as caller ID (not generic number)
- Update voice prompt to say: "This is Copper AI calling for [Agency Name]"
- Send SMS 5 minutes before calling: "Expect a call from Copper AI in 5 min"

### "Too many false alarms (high-risk alerts)"

**Diagnosis:**

- Check risk threshold settings
- Likely: Sensitivity too high (alerting on every missed call)

**Fix:**

- Adjust risk scoring algorithm (require 2+ missed calls before alerting)
- Add "grace period" (don't alert if caregiver calls back within 30 min)

---

## Success Metrics (Track Weekly)

### Week 1

- [ ] 80%+ caregivers successfully used Voice EVV
- [ ] 50%+ confirmation calls answered
- [ ] 0 critical issues (system downtime, data loss)

### Week 4

- [ ] 20-30% no-show reduction (vs baseline)
- [ ] 90%+ EVV compliance (up from 70-80%)
- [ ] 4+ NPS score from caregivers

### Week 8

- [ ] 30-50% no-show reduction
- [ ] Agency wants to continue after beta (renewal intent)
- [ ] Written testimonial or video case study

---

## Offboarding (If Agency Churns)

**Exit Interview Questions:**

1. What didn't work as expected?
2. What would make you reconsider?
3. Would you recommend us to other agencies?
4. Can we use your feedback in our case studies?

**Actions:**

- [ ] Export agency data (for their records)
- [ ] Disable webhooks (stop calls)
- [ ] Update status in database: `status = 'churned'`
- [ ] Send thank you email + request testimonial
- [ ] Add learnings to `memory/churn-learnings.md`

---

_Built with 🐾 by Nike | Questions? Telegram @SarinAI_bot_
