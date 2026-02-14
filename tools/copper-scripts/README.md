# Copper AI Automation Scripts

_Built by Nike during overnight vibe coding session | Feb 1, 2026_

---

## 🎯 Purpose

These scripts automate repetitive marketing and sales tasks for Copper AI, saving time and ensuring consistency across campaigns.

---

## 📋 Available Scripts (6 Tools)

### 1. `linkedin-post-generator.js`

**Purpose:** Generate ready-to-post LinkedIn content based on themes

**Usage:**

```bash
# Generate all posts
node scripts/linkedin-post-generator.js all

# Generate specific theme
node scripts/linkedin-post-generator.js no-shows
node scripts/linkedin-post-generator.js time-savings
node scripts/linkedin-post-generator.js cost-comparison
```

**Available Themes:**

- `no-shows` - Focus on reducing no-show rates
- `time-savings` - Emphasize hours saved on admin
- `evv-integration` - Highlight EVV system integration
- `cost-comparison` - Compare to answering services
- `compliance` - State audit and compliance angle
- `caregiver-experience` - Improve caregiver retention
- `founder-story` - Personal narrative from Arvind
- `industry-trends` - Workforce shortage context

**Output:**

- Full LinkedIn post with hook, body, CTA, hashtags
- Character count (LinkedIn limit: 3,000)
- Ready to copy/paste

**Example:**

```bash
$ node scripts/linkedin-post-generator.js no-shows

20% no-show rate is costing your home health agency $20k-30k per month.

Here's the math:
• 100 shifts/week × 20% no-show = 20 lost shifts
[...]

Ready to stop losing money to no-shows? Let's talk.

#HomeHealth #HealthcareAI #VoiceAI #CareCoordination #HealthTech

Character count: 487 ✅
```

---

### 2. `email-campaign-generator.js`

**Purpose:** Generate personalized email sequences for different customer segments

**Usage:**

```bash
# Generate full sequence
node scripts/email-campaign-generator.js cold-outreach

# List emails in a sequence
node scripts/email-campaign-generator.js demo-follow-up --list

# Generate all sequences
node scripts/email-campaign-generator.js all
```

**Available Segments:**

- `cold-outreach` - Initial outreach to home health agencies (4 emails)
- `demo-follow-up` - Post-demo nurture sequence (3 emails)
- `trial-nurture` - Trial customer check-ins (3 emails)
- `customer-success` - Ongoing customer engagement (2 emails)

**Features:**

- Merge field support ({{firstName}}, {{agencyName}}, etc.)
- Timing recommendations (Day 0, Day 3, Day 7, etc.)
- Subject lines + body copy
- List of merge fields needed for each email

**Example:**

```bash
$ node scripts/email-campaign-generator.js cold-outreach --list

Cold Outreach - Home Health Agencies - 4 emails
  1. Day 0: Quick question about [Agency Name]'s shift confirmations
  2. Day 3: Re: Shift confirmations at [Agency Name]
  3. Day 7: [Agency Name] + Copper AI = 60% fewer no-shows?
  4. Day 14: Breakup email (for real this time)
```

---

### 3. `competitor-monitor.js`

**Purpose:** Track competitor pricing, features, and positioning

**Usage:**

```bash
# Quick pricing check
node scripts/competitor-monitor.js check

# Generate full competitive intelligence report
node scripts/competitor-monitor.js report

# Save report to second-brain/
node scripts/competitor-monitor.js save
```

**Competitors Tracked:**

- Vapi AI (MEDIUM threat)
- Retell AI (MEDIUM threat)
- Dialora AI (HIGH threat - closest competitor)
- Bland AI (MEDIUM threat)
- Aircall AI (MEDIUM threat)

**Output:**

- Pricing comparison table
- Strengths/weaknesses analysis
- Threat level assessment
- Counter-strategies for each competitor
- Recommended actions

**Example:**

```bash
$ node scripts/competitor-monitor.js check

COPPER AI - COMPETITIVE PRICING MONITOR

Vapi AI
----------------------------------------
Pricing Model: usage-based + multi-vendor stack
Advertised: $0.05/min
Actual: $0.18-0.33/min (with all services)
Threat Level: MEDIUM
Last Updated: 2026-01-31

[...]
```

---

### 5. `sales-call-prep.js`

**Purpose:** Generate customized sales call prep sheets based on prospect info

**Usage:**

```bash
# Full prep sheet
node scripts/sales-call-prep.js --agency "ABC Home Health" --evv "WellSky" --pain "no-shows" --size "medium-agency"

# Quick prep
node scripts/sales-call-prep.js --evv "Axxess" --pain "time-savings"

# Competitor comparison
node scripts/sales-call-prep.js --competitor "dialora" --pain "no-shows"
```

**Parameters:**

- `--agency` - Agency name
- `--evv` - EVV system (WellSky, Axxess, ClearCare, Sandata, Other)
- `--pain` - Pain point (no-shows, time-savings, evv-integration, compliance)
- `--size` - Agency size (small-agency, medium-agency, large-agency)
- `--competitor` - What they're comparing against (answering-service, vapi-retell, dialora)

**Output:**

- Prospect profile and challenges
- Discovery questions to ask
- Value proposition tailored to pain point
- Demo flow (15-minute structure)
- EVV integration talking points
- Competitor positioning
- Pricing presentation strategy
- Objection handlers
- Closing techniques
- Post-call follow-up plan

**Example:**

```bash
$ node scripts/sales-call-prep.js --agency "iCare Home Health" --evv "ClearCare" --pain "no-shows" --size "medium-agency"

===============================================================================
SALES CALL PREP SHEET
===============================================================================

Agency: iCare Home Health
EVV System: ClearCare
Primary Pain Point: no-shows
Agency Size: medium-agency

[...complete prep sheet generated...]
```

---

### 6. `roi-calculator-cli.js`

**Purpose:** Calculate ROI and cost savings vs alternatives (command-line version of HTML calculator)

**Usage:**

```bash
# Basic calculation
node scripts/roi-calculator-cli.js --calls 1000 --caregivers 30

# Compare to specific alternative
node scripts/roi-calculator-cli.js --calls 500 --compare manual-process

# Large agency comparison
node scripts/roi-calculator-cli.js --calls 2500 --caregivers 60 --compare vapi-ai
```

**Parameters:**

- `--calls` - Number of calls per month
- `--caregivers` - Number of caregivers
- `--compare` - What to compare against:
  - `answering-service` (default)
  - `manual-process`
  - `vapi-ai`
  - `retell-ai`
  - `dialora-ai`

**Output:**

- Copper AI recommended tier and pricing
- Alternative solution cost breakdown
- Monthly and annual savings
- Time savings (hours and dollar value)
- No-show reduction impact
- Total value calculation
- Payback period
- Recommendation

**Example:**

```bash
$ node scripts/roi-calculator-cli.js --calls 1000 --caregivers 30 --compare answering-service

COPPER AI ROI CALCULATOR

Copper AI Growth: $497/month
Answering Service: $2,500/month

SAVINGS:
• Monthly: $2,003
• Annual: $24,036
• ROI: 404%
• Payback: Less than 1 month

[...detailed breakdown...]
```

---

## 🚀 Quick Start

### Generate LinkedIn post for today:

```bash
node scripts/linkedin-post-generator.js no-shows
```

### Prep for a sales call:

```bash
node scripts/sales-call-prep.js --agency "Prospect Name" --evv "WellSky" --pain "no-shows"
```

### Calculate ROI for a prospect:

```bash
node scripts/roi-calculator-cli.js --calls 800 --caregivers 25
```

### Copy a LinkedIn post for today (old method):

```bash
node scripts/linkedin-post-generator.js no-shows | pbcopy
# Paste into LinkedIn!
```

### Generate a cold outreach campaign:

```bash
node scripts/email-campaign-generator.js cold-outreach > email-campaign.txt
# Import into your CRM or email tool
```

### Check competitor pricing before a sales call:

```bash
node scripts/competitor-monitor.js check
```

---

## 📊 Integration Ideas

### With CRM (HubSpot, Salesforce, etc.):

1. Generate email sequence with `email-campaign-generator.js`
2. Copy/paste into CRM email sequences
3. Map merge fields to CRM fields ({{firstName}} → First Name)

### With LinkedIn Scheduler (Buffer, Hootsuite, etc.):

1. Generate posts for the week:
   ```bash
   node scripts/linkedin-post-generator.js all > weekly-posts.txt
   ```
2. Schedule in Buffer/Hootsuite
3. Space them out (Mon, Wed, Fri pattern)

### With Sales Team:

1. Generate competitor monitor report weekly:
   ```bash
   node scripts/competitor-monitor.js save
   ```
2. Share with sales team before demos
3. Use counter-strategies during objection handling

---

## 🔧 Customization

All scripts are editable JavaScript. To add new content:

### Add a LinkedIn theme:

Edit `linkedin-post-generator.js`, add to `themes` object:

```javascript
themes["new-theme"] = {
  hook: "Your compelling opening line",
  body: `Main content here...`,
  cta: "Call to action",
  hashtags: ["#Tag1", "#Tag2"],
};
```

### Add an email sequence:

Edit `email-campaign-generator.js`, add to `segments` object:

```javascript
segments["new-segment"] = {
  name: "Segment Name",
  emails: [
    {
      day: 0,
      subject: "Subject line",
      body: `Email body with {{mergeFields}}`,
    },
  ],
};
```

### Update competitor data:

Edit `competitor-monitor.js`, update `competitorDB` object with latest pricing/features.

---

## 📝 Best Practices

### LinkedIn Posts:

- Post 3-4x per week (Mon, Wed, Fri works well)
- Vary themes (don't repeat same angle back-to-back)
- Engage with comments within first hour
- Tag relevant people/companies when appropriate

### Email Campaigns:

- Always personalize merge fields (don't leave {{firstName}} blank!)
- Test emails before sending to full list
- Track open rates and adjust subject lines
- Respect unsubscribe requests immediately

### Competitor Monitoring:

- Run `competitor-monitor.js check` weekly
- Save full report monthly (`save` command)
- Update competitor database when you see pricing changes
- Share insights with sales team before demos

---

## 🎯 Roadmap / Future Scripts

Ideas for additional automation:

- [ ] `case-study-generator.js` - Template customer success stories
- [ ] `roi-calculator-cli.js` - Command-line ROI calculator for sales calls
- [ ] `demo-prep.js` - Generate customized demo scripts based on prospect data
- [ ] `social-media-scheduler.js` - Auto-post to LinkedIn/Twitter via APIs
- [ ] `competitor-scraper.js` - Auto-scrape competitor websites for pricing updates
- [ ] `content-calendar.js` - Generate 30-day content calendar
- [ ] `sales-battlecard-cli.js` - Interactive CLI for sales objection handling

**Want one of these? Ask Nike to build it!**

---

## 🐛 Troubleshooting

**"Command not found"**

- Make sure you're in the `/home/ubuntu/openclaw/tools/copper-scripts` directory
- Run `chmod +x scripts/*.js` to make scripts executable

**"Module not found"**

- These scripts use built-in Node.js modules only (no npm install needed)

**"Merge fields not rendering"**

- Email scripts output {{placeholders}} - replace these with actual data in your CRM

---

## 📞 Support

**Questions about these scripts?**

- Ask Nike (that's me! 🐾)
- Check script comments for inline docs
- Modify freely - they're yours!

**Want a new script?**

- Describe what you need
- Nike will build it during next overnight vibe coding session

---

_Scripts created by Nike | Feb 1, 2026 during overnight vibe coding_
_Use them. Customize them. Make Copper AI marketing awesome._
