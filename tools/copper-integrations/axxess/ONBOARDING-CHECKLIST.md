# Agency Onboarding Checklist - Axxess Integration

**Time Required:** 10-15 minutes per agency (FASTER than ClearCare!)  
**Best Done:** Over video call or async (Axxess agencies are tech-savvy)

---

## Pre-Onboarding (Before Contact)

### ✅ Agency Qualifications

- [ ] Active Axxess account (Home Health or Home Care)
- [ ] 10+ caregivers (MVP works best with 10-50 caregivers)
- [ ] Has API access OR willing to request it (1-2 day turnaround from Axxess support)
- [ ] Signed pilot agreement (see `sales/pilot-agreement-template.md`)
- [ ] Uses Axxess EVV currently (mobile app)

### ✅ Copper AI Setup

- [ ] Test Axxess API credentials (client ID + secret)
- [ ] Agency created in database (see SQL below)
- [ ] Unique API configuration per agency

**SQL to create agency:**

```sql
INSERT INTO agencies (name, owner_name, owner_phone, owner_email, plan, monthly_price, platform, axxess_agency_id)
VALUES ('XYZ Home Health', 'Jane Doe', '+14695555678', 'jane@xyzhomehealth.com', 'beta', 0.00, 'axxess', 'AG-12345')
RETURNING id;
```

---

## Onboarding Call/Email (10-15 Minutes)

### Part 1: Introduction (3 min)

**Say:**

> "Hi [Name]! Thanks for joining the Copper AI beta. Since you're already using Axxess EVV via mobile app, we're adding a VOICE option for caregivers who don't have smartphones (or prefer calling).
>
> Today we'll:
>
> 1. Get your Axxess API credentials (5 min)
> 2. Sync your caregivers (2 min)
> 3. Test voice EVV (3 min)
> 4. Enable no-show prevention (2 min)
>
> Ready to get started?"

**Check:**

- [ ] Agency understands Copper AI works ALONGSIDE Axxess (not replacing it)
- [ ] Agency has 40%+ caregivers without smartphones (our target market)
- [ ] Agency commits to weekly check-ins during pilot

### Part 2: Axxess API Access (5 min)

#### Option A: Agency Already Has API Access

**Say:**

> "Do you already have Axxess API credentials (client ID + secret)? If yes, can you share them securely?"

**Agency Actions:**

1. Log into Axxess Admin Portal
2. Go to **Settings** → **API Access** → **Client Credentials**
3. Copy `client_id` and `client_secret`
4. Send via secure method (not email! Use password-protected file or phone)

#### Option B: Agency Needs to Request API Access

**Say:**

> "You'll need to contact Axxess support to enable API access. This usually takes 1-2 business days. Here's exactly what to say:"

**Email Template for Agency:**

```
To: support@axxess.com
Subject: API Access Request for Third-Party Integration

Hi Axxess Support,

We would like to enable API access for our agency ([Agency Name], Agency ID: [AG-12345]) to integrate with a third-party voice AI system (Copper AI) for EVV and scheduling.

We need the following scopes:
- read:schedule
- write:evv
- read:caregivers

Please provide us with:
1. OAuth Client ID
2. OAuth Client Secret
3. API documentation link

Thank you!
[Your Name]
[Agency Owner/Admin]
```

**Turnaround:** 1-2 business days (Axxess support is fast)

**Check:**

- [ ] Agency has submitted request OR already has credentials
- [ ] Nike adds agency to "pending API access" list
- [ ] Follow up in 2 days if no response

### Part 3: Nike Configuration (2 min - While Agency Waits)

**Nike Actions:**

```bash
# Store credentials securely in database
cd /home/ubuntu/openclaw/tools/copper-integrations/axxess

# Update agency record
psql $DATABASE_URL -c "
UPDATE agencies
SET axxess_client_id = 'CLIENT_ID_HERE',
    axxess_client_secret = 'CLIENT_SECRET_HERE',
    axxess_agency_id = 'AG-12345'
WHERE id = 1;
"

# Test API connection
node axxess-api-client.js
# Should output: "✅ Connection successful. Found X active caregivers."
```

### Part 4: Sync Caregivers (2 min - Automated!)

**Nike Actions:**

```bash
# Sync caregivers from Axxess API
node scripts/sync-axxess-caregivers.js --agency-id=1

# Output: "✅ Synced 47 caregivers from Axxess"

# Verify sync
psql $DATABASE_URL -c "SELECT COUNT(*) FROM caregivers WHERE agency_id = 1;"
```

**No manual CSV import needed!** (unlike ClearCare)

### Part 5: Test Voice EVV (3 min)

**Say:**

> "Perfect! Let's test the voice EVV. [Caregiver name], can you call (469) 420-CARE right now?"

**Test Caregiver Actions:**

1. Call hotline: `(469) 420-CARE`
2. Say: "Hi, this is [Name]. I'm clocking in for [Client]."
3. Wait for AI confirmation

**Expected Outcome:**

- Voice AI: "Thanks [Name], you're clocked in for [Client] at [Time]!"
- **Check Axxess:** Visit status updated to "In Progress" (via API)
- **Check Copper AI database:** EVV log created

**Nike Checks:**

```bash
# Check EVV log in database
psql $DATABASE_URL -c "SELECT * FROM evv_logs ORDER BY id DESC LIMIT 1;"

# Check Axxess API
node -e "
const AxxessAPI = require('./axxess-api-client.js');
const api = new AxxessAPI(process.env.AXXESS_CLIENT_ID, process.env.AXXESS_CLIENT_SECRET, 'AG-12345');
api.getEVVLogs('VISIT_ID_HERE').then(console.log);
"
```

**If it fails:**

- Check caregiver phone number matches Axxess
- Check visit exists in Axxess for today
- Check API permissions (write:evv scope)
- Review webhook logs for errors

### Part 6: Enable No-Show Prevention (2 min)

**Say:**

> "Great! Now let's enable the no-show prevention feature. This will call caregivers 2 hours before each visit to confirm they're still coming."

**Nike Actions:**

```bash
# Enable no-show prevention for agency
node scripts/enable-no-show-prevention.js --agency-id=1

# Output: "✅ No-show prevention enabled. First confirmation calls will go out at [TIME]."
```

**Agency Owner Alert:**

```
📢 NO-SHOW PREVENTION ENABLED

Copper AI will now call your caregivers 2 hours before each visit to confirm.

If they don't answer or say they can't make it, you'll receive an alert via:
- SMS to [your phone]
- Telegram (if configured)

Expected result: 30-50% no-show reduction 🎯

Questions? Text Arvind: +1 469 742 1095
```

---

## Post-Onboarding (After Call)

### ✅ Send Confirmation Email

**Template:**

```
Subject: Copper AI + Axxess Integration Live! 🎉

Hi [Name],

Your Copper AI integration with Axxess is now LIVE! Here's what's enabled:

✅ Voice EVV: Caregivers can call (469) 420-CARE to clock in/out
✅ No-Show Prevention: 2-hour confirmation calls (starts today)
✅ Auto-Sync: Schedule syncs from Axxess every hour

WHAT YOUR CAREGIVERS NEED TO KNOW:
- They can STILL use the Axxess mobile app (nothing changes)
- NEW OPTION: Call (469) 420-CARE if they don't have their phone or prefer voice
- It takes 15 seconds vs 2 minutes on the app

NO-SHOW PREVENTION:
- Caregivers will receive a call 2 hours before each visit
- If they confirm, no further action
- If they don't answer or say "I can't make it" → You get alerted immediately

NEXT STEPS:
1. Share the hotline number with your team: (469) 420-CARE
2. Print this quick reference card: [attached PDF]
3. We'll check in next [Day] at [Time] to review your no-show rates

QUESTIONS?
Text/call: +1 469 742 1095
Telegram: @SarinAI_bot

Excited to reduce your no-shows by 30-50%! 🚀

Arvind
Copper AI
arvind@copperdigital.com
```

**Attachments:**

- [ ] Quick Reference Card (PDF): "How to Use Voice EVV"
- [ ] FAQ doc: "Copper AI + Axxess FAQ"

### ✅ Internal Setup

- [ ] Add agency to Monday CRM
- [ ] Create Slack channel: #copper-xyz-home-health
- [ ] Set up Telegram group (agency owner + Arvind + Nike)
- [ ] Schedule weekly check-in (Google Calendar)
- [ ] Add to analytics dashboard

### ✅ Monitor First Week

**Daily (Days 1-7):**

- [ ] Check Voice EVV call volume (should be 5-20 calls/day)
- [ ] Check Axxess API sync success rate (100% target)
- [ ] Monitor confirmation call outcomes (80%+ answer rate)
- [ ] Watch for API rate limit warnings (<1,000 calls/day)

**Week 1 Report:**

```
📊 WEEK 1 SUMMARY - [Agency Name] (Axxess)

Voice EVV:
- [X] calls (clock-ins: [Y], clock-outs: [Z])
- Mobile App: [A] calls (still working normally)
- Voice adoption rate: [B]%

No-Show Prevention:
- Confirmation calls sent: [C]
- Answer rate: [D]%
- No-shows prevented: [E]

Axxess API:
- Total API calls: [F] (out of 1,000 daily limit)
- Sync success rate: [G]%
- Errors: [H]

Next Week Goals:
- Increase voice EVV adoption to 30%
- Achieve 85%+ confirmation call answer rate
- Measure no-show reduction vs baseline

Great start! 🚀
```

---

## Troubleshooting Common Issues

### "Axxess API authentication failed"

**Diagnosis:**

- Check client ID and secret are correct
- Check API permissions (scopes)
- Check Axxess account status (expired, suspended)

**Fix:**

- Re-authenticate: `node axxess-api-client.js`
- Verify credentials with agency
- Contact Axxess support if account issue

### "Caregiver not found in Axxess"

**Diagnosis:**

- Caregiver was added to Copper AI manually (not synced from Axxess)
- Caregiver phone number doesn't match Axxess

**Fix:**

- Re-sync caregivers: `node scripts/sync-axxess-caregivers.js --agency-id=1`
- Update phone number in Axxess to match
- Manual mapping if phone number changed

### "EVV not updating in Axxess"

**Diagnosis:**

- API error (check logs)
- Visit ID doesn't exist in Axxess
- write:evv scope not granted

**Fix:**

- Check Axxess API logs: `node scripts/check-api-logs.js --agency-id=1`
- Verify visit exists in Axxess
- Re-request API access with correct scopes

### "Rate limit exceeded (429 error)"

**Diagnosis:**

- Exceeded 1,000 API calls/day
- Too many caregivers/visits for standard tier

**Fix:**

- Check current usage: `SELECT * FROM axxess_rate_limits WHERE agency_id = 1;`
- Optimize sync frequency (hourly → every 2 hours)
- Contact Axxess to upgrade to enterprise tier (10,000 calls/day)

---

## Success Metrics (Track Weekly)

### Week 1

- [ ] Voice EVV working for 20%+ of caregivers
- [ ] 80%+ confirmation call answer rate
- [ ] 0 Axxess API errors

### Week 4

- [ ] Voice EVV adoption: 40%+
- [ ] 30-50% no-show reduction (vs baseline)
- [ ] 95%+ EVV compliance (Axxess + Copper AI combined)

### Week 8

- [ ] Agency wants to continue after beta
- [ ] Written testimonial or video case study
- [ ] Referral to 1-2 other Axxess agencies

---

## Offboarding (If Agency Churns)

**Exit Interview Questions:**

1. Why didn't voice EVV work for your team?
2. Did no-show prevention reduce no-shows? (get data)
3. What would make you reconsider?
4. Would you recommend us to other Axxess agencies?

**Actions:**

- [ ] Export agency data (for their records)
- [ ] Revoke Axxess API access (delete credentials)
- [ ] Update status in database: `status = 'churned'`
- [ ] Send thank you email + request feedback
- [ ] Add learnings to `memory/axxess-churn-learnings.md`

---

_Built with 🐾 by Nike | Questions? Telegram @SarinAI_bot_
