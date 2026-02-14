# 🚀 START HERE: Home Health Agency Campaign Launch Checklist

## Phase 1: Pre-Launch Setup (Feb 14, 2026)

### ✅ Infrastructure Complete

- [x] Directory structure created
- [x] Email templates written (4 personas, 4 follow-ups)
- [x] Python scripts built (send-email, check-responses)
- [x] Automation configured (2x daily: 8 AM, 2 PM)
- [x] Hooks installed (pre-send validation, post-send update)
- [x] State management system ready

### 🔲 Pre-Launch Tasks (Do These Now)

1. **Update Demo Links** ⚠️ CRITICAL

   ```bash
   # Edit scripts/send-email.py
   # Replace these placeholder values:
   DEMO_VIDEO_LINK = "[INSERT_DEMO_VIDEO_LINK]"
   CALENDAR_LINK = "[INSERT_CAL_COM_LINK]"
   ```

2. **Find and Clean Texas Agency List**
   - User mentioned: "I already have a list of the Texas agencies there's duplicates"
   - Located at: `/Users/arvindsarin/Cursor/Claude-2026/openclaw/Campaigns/texas-outreach-tracker.csv` (currently empty)
   - **Action**: Find the 199-lead list, deduplicate, enrich with contact info
   - Target: 50 agencies for Wave 1 (DFW, Austin, Houston)

3. **Research Wave 1 Agencies (50 Total)**

   **Tier 1 Criteria:**
   - Location: DFW, Austin, Houston metro areas
   - Size: 50-200 patients (medium agencies)
   - Contact: Administrator or Owner with email
   - EHR: Using WellSky, Axxess, PointClickCare, etc.

   **Data to Collect:**
   - Agency name
   - Contact name (first + last)
   - Contact title (Administrator, Owner, Clinical Director)
   - Email (direct email preferred, not info@)
   - Phone
   - City, State
   - Agency size (small/medium/large)
   - Patient volume (if available)
   - EHR system (if known)

4. **Create Wave 1 CSV**

   ```bash
   cp data/agencies-template.csv data/wave1-agencies.csv
   # Then fill with 50 researched agencies
   ```

5. **Verify Gmail App Password**

   ```bash
   echo $GMAIL_APP_PASSWORD
   # Should output: cgnzofbqkqqcvycm
   ```

6. **Test Email Send (Dry Run)**

   ```bash
   cd scripts/

   python3 send-email.py \
     --agency-id 1 \
     --agency-name "Test Agency" \
     --contact-name "Arvind Sarin" \
     --first-name "Arvind" \
     --email "arvind@copperdigital.com" \
     --persona administrator \
     --test
   ```

## Phase 2: Launch Wave 1 (Feb 15, 2026)

### Morning Launch (Target: 10 agencies)

```bash
cd /Users/arvindsarin/Cursor/Claude-2026/openclaw/Campaigns/hha-outreach-2026/scripts

# Send to first 10 agencies
for i in {1..10}; do
  # Extract data from CSV for agency #$i
  # Run: python3 send-email.py --agency-id $i ...
done
```

### Afternoon Review (2 PM)

- Check responses: `python3 check-responses.py`
- Monitor for demo requests
- Respond within 2 hours to interested replies

### Evening Send (Target: 10 more)

- Send to agencies 11-20
- Update state.json

## Phase 3: Week 1 Operations (Feb 15-21)

### Daily Routine

- **8 AM**: Automation checks responses, sends Day 3/7/14 follow-ups
- **10 AM**: Manual review of any demo requests
- **2 PM**: Automation checks responses again
- **4 PM**: Send new batch if available

### Response Handling

1. **Demo Request** → Send Cal.com link immediately
2. **Question** → Answer within 2 hours, offer demo
3. **Not Interested** → Mark in state.json, no further follow-up
4. **Out of Office** → Wait for return, continue follow-ups
5. **Referral** → Thank them, reach out to referred contact

### Metrics to Track

- Emails sent: Target 50 by Feb 21
- Open rate: Monitor via Gmail read receipts
- Demo requests: Target 10-20% (5-10 demos)
- Response rate: Track in state.json

## Phase 4: Follow-Up Automation (Ongoing)

### Automatic Follow-Ups

- **Day 3**: Quick nudge ("Did you watch the video?")
- **Day 7**: Social proof (pilot case study)
- **Day 14**: Final urgency (OASIS-E2 deadline)

### Manual Overrides

- If agency responds positively, pause automated follow-ups
- Update state.json with `"status": "in_conversation"`
- Handle manually from that point

## 🚨 Critical Success Factors

1. **Demo Video Link**: Must be working before first send
2. **Cal.com Link**: Must be set up and available 24/7
3. **Response Time**: 2-hour target for demo requests
4. **Email Quality**: Personalize first name, agency name
5. **Follow-Up Discipline**: Let automation handle follow-ups
6. **Pilot Readiness**: Have 2-week pilot onboarding ready

## 📊 Success Metrics

### Week 1 (Feb 15-21)

- 50 emails sent
- 5-10 demo requests
- 2-3 demos booked

### Week 2 (Feb 22-28)

- Day 3 follow-ups sent automatically
- 5-10 additional demo requests
- 3-5 demos completed

### Week 3 (Mar 1-7)

- Day 7 follow-ups sent
- 2-3 pilots started
- Wave 2 prep (next 50 agencies)

### Q1 End (Mar 31)

- 150 agencies contacted (3 waves)
- 20+ demos completed
- 10 pilots in progress
- 3-5 pilots converting to paid

## ⚠️ Blockers to Resolve

1. ❌ Demo video link (INSERT_DEMO_VIDEO_LINK)
2. ❌ Cal.com link (INSERT_CAL_COM_LINK)
3. ❌ Wave 1 agency list (50 researched agencies)
4. ❌ Texas lead list location (find the 199-lead list)

## 🎯 Next Immediate Actions

1. **User**: Provide demo video URL and Cal.com URL
2. **User**: Locate the Texas agency list with 199 leads
3. **Claude**: Clean and deduplicate the agency list
4. **Claude**: Research top 50 agencies (DFW, Austin, Houston)
5. **Claude**: Update send-email.py with real links
6. **User**: Approve Wave 1 agency list
7. **Claude**: Launch Wave 1 (10 agencies at a time)

---

**Status**: Infrastructure complete, ready for pre-launch tasks
**Next Step**: Update demo links and research Wave 1 agencies
**Target Launch**: Feb 15, 2026 (2 days away)
