# Business-Critical Script Priorities

Scripts that directly impact sales, customer success, and revenue

## Tier 1: Sales & Revenue Tools (Use These Daily)

### 1. sales-call-prep.js - Sales Preparation

**Status**: WORKING
**Business Impact**: Direct sales support

```bash
# Before every sales call
node sales-call-prep.js --agency "ABC Home Health" --evv "WellSky" --pain "no-shows"
node sales-call-prep.js --evv "Axxess" --pain "time-savings" --size "medium-agency"
node sales-call-prep.js --competitor "dialora" --pain "no-shows"
```

**Output**:

- Customized talking points
- EVV integration specifics
- Pain point messaging
- Objection handling
- Competitor positioning

**Use When**:

- Pre-call prep (15 min before)
- Creating sales decks
- Writing personalized emails

---

### 2. roi-calculator-cli.js - Sales Closing Tool

**Status**: WORKING
**Business Impact**: Quantifies value proposition

```bash
# During demo or proposal stage
node roi-calculator-cli.js --calls 1000 --caregivers 30
node roi-calculator-cli.js --calls 500 --compare manual-process
node roi-calculator-cli.js --calls 2000 --caregivers 50 --compare vapi-ai
```

**Output**:

- Cost savings vs alternatives
- Time savings calculation
- ROI timeline
- Break-even analysis

**Use When**:

- Creating proposals
- Answering "how much will we save?" questions
- Justifying price objections
- Competitive comparisons

---

### 3. competitor-monitor.js - Competitive Intelligence

**Status**: WORKING
**Business Impact**: Stay ahead of competition

```bash
# Weekly competitive review
node competitor-monitor.js check        # Quick overview
node competitor-monitor.js report       # Full analysis
node competitor-monitor.js save         # Save to second-brain/
```

**Output**:

- Competitor pricing
- Feature comparison
- Market positioning
- Differentiation points

**Use When**:

- Weekly sales meetings
- Updating battlecards
- Responding to "what about [competitor]?"
- Strategic planning

---

### 4. email-campaign-generator.js - Email Sequences

**Status**: WORKING (needs UX fix)
**Business Impact**: Automated nurture sequences

```bash
# Generate email sequences
node email-campaign-generator.js cold-outreach
node email-campaign-generator.js demo-follow-up
node email-campaign-generator.js trial-nurture
node email-campaign-generator.js customer-success
```

**Sequences Available**:

1. **Cold Outreach** (4 emails, Days 0/3/7/14)
   - Initial value prop
   - Pain point focus
   - Breakup email

2. **Demo Follow-Up** (3 emails, Days 0/2/7)
   - Recap and resources
   - Check-in with FAQ
   - Decision checkpoint

3. **Trial Nurture** (3 emails, Days 7/14/21)
   - Week 1 check-in
   - 2-week results
   - Conversion push

4. **Customer Success** (2 emails, Days 30/90)
   - 30-day impact report
   - Quarterly business review

**Use When**:

- Setting up new lead sequences
- Following up after demos
- Nurturing trial customers
- Customer onboarding

---

### 5. linkedin-post-generator.js - Content Marketing

**Status**: WORKING (needs UX fix)
**Business Impact**: Social media lead generation

```bash
# Generate LinkedIn posts
node linkedin-post-generator.js no-shows
node linkedin-post-generator.js time-savings
node linkedin-post-generator.js evv-integration
node linkedin-post-generator.js cost-comparison
node linkedin-post-generator.js compliance
node linkedin-post-generator.js caregiver-experience
node linkedin-post-generator.js founder-story
node linkedin-post-generator.js industry-trends
```

**8 Themes**:

1. **no-shows** - Pain point: 20% no-show rate costs
2. **time-savings** - 15 hours/week savings
3. **evv-integration** - Seamless EVV workflow
4. **cost-comparison** - 70% cheaper than answering services
5. **compliance** - Automatic audit trail
6. **caregiver-experience** - Retention through communication
7. **founder-story** - Why we built Copper AI
8. **industry-trends** - Workforce shortage + automation

**Content Calendar**:

- Monday: Pain point (no-shows, time-savings)
- Wednesday: Value prop (cost-comparison, evv-integration)
- Friday: Thought leadership (industry-trends, founder-story)

---

### 6. copper-metrics-tracker.js - Business Metrics

**Status**: WORKING
**Business Impact**: Track growth, report progress

```bash
# Track business metrics
node copper-metrics-tracker.js add customers 52
node copper-metrics-tracker.js add revenue 24500
node copper-metrics-tracker.js add calls 50000
node copper-metrics-tracker.js note "Launched partnership with WellSky"
node copper-metrics-tracker.js report
node copper-metrics-tracker.js goals
```

**Metrics Tracked**:

- Customer count
- Monthly recurring revenue
- Calls processed
- Milestones/notes
- Progress to 2026 goals

**Use When**:

- Weekly team standups
- Investor updates
- Board meetings
- Goal tracking

---

## Tier 2: Customer Success Tools

### 7. reach-out-recommendations.py - Relationship Management

**Status**: WORKING
**Business Impact**: Proactive customer outreach

```bash
# Daily relationship check
python3 reach-out-recommendations.py
```

**Output**:

- Dormant contacts to re-engage
- Business vs personal categorization
- Suggested outreach messages

**Use When**:

- Monday morning planning
- Customer success check-ins
- Network maintenance

---

## Tier 3: Research & Intelligence Tools

### 8. get-youtube-transcript.js - Competitive Research

**Status**: BROKEN (easy fix - 5 min)
**Business Impact**: Extract competitor content, testimonials

```bash
# Extract video transcripts
node get-youtube-transcript.js "https://youtube.com/watch?v=VIDEO_ID"
```

**Use Cases**:

- Analyze competitor demos
- Extract testimonial quotes
- Research industry content
- Study messaging strategies

**Fix Required**: `npx playwright install`

---

### 9. prospect-research.sh - Lead Qualification

**Status**: WORKING
**Business Impact**: Structured prospect research

```bash
# Start researching new prospect
./prospect-research.sh "ABC Home Health"
```

**Output**:

- Creates markdown file in prospects/
- Template for agency info
- Contact research checklist
- Next steps

**Use When**:

- New inbound lead
- Cold outreach preparation
- Pre-call research

---

## Tier 4: NEEDS IMPLEMENTATION (High Business Value)

### 10. analyze-emails.js - Email Intelligence

**Status**: STUB (needs AI integration)
**Business Impact**: Automated lead qualification from inbox

**Intended Function**:

- Parse daily email summary
- Extract urgent leads
- Identify action items
- Create kanban tasks automatically
- Flag hot prospects

**Implementation Needed**:

- Integrate Claude API
- Parse email summary markdown
- Extract entities (company names, pain points)
- Create structured todos
- Priority scoring

**Estimated Time**: 2-4 hours
**ROI**: Very High - automates daily email triage

**Use Cases**:

- Morning email review
- Lead qualification
- Opportunity tracking
- Follow-up reminders

---

## Weekly Workflow (Recommended)

### Monday Morning (30 min)

```bash
# 1. Check business metrics
node copper-metrics-tracker.js report

# 2. Review relationship health
python3 reach-out-recommendations.py

# 3. Competitive intelligence check
node competitor-monitor.js check
```

### Before Each Sales Call (15 min)

```bash
# 1. Prep call materials
node sales-call-prep.js --agency "Agency Name" --evv "WellSky" --pain "no-shows"

# 2. Calculate ROI for this prospect
node roi-calculator-cli.js --calls 1000 --caregivers 30

# 3. Research prospect (if new)
./prospect-research.sh "Agency Name"
```

### After Each Demo (10 min)

```bash
# 1. Send follow-up email
node email-campaign-generator.js demo-follow-up
# Copy Email 1 (Day 0) and personalize

# 2. Update metrics
node copper-metrics-tracker.js note "Demo with ABC Home Health - strong interest"
```

### Wednesday Content Day (30 min)

```bash
# 1. Generate LinkedIn post
node linkedin-post-generator.js no-shows

# 2. Review and post to LinkedIn
# Add personal touch, tag relevant people
```

### Friday Wrap-Up (15 min)

```bash
# 1. Update metrics for the week
node copper-metrics-tracker.js add customers X
node copper-metrics-tracker.js add revenue Y

# 2. Generate weekly competitive report
node competitor-monitor.js save
```

---

## Quick Reference Card

### Sales Call Prep

```bash
node sales-call-prep.js --agency "NAME" --evv "SYSTEM" --pain "ISSUE"
```

### ROI Calculation

```bash
node roi-calculator-cli.js --calls NUMBER --caregivers NUMBER
```

### Email Sequence

```bash
node email-campaign-generator.js [cold-outreach|demo-follow-up|trial-nurture]
```

### LinkedIn Post

```bash
node linkedin-post-generator.js [no-shows|time-savings|cost-comparison]
```

### Metrics Update

```bash
node copper-metrics-tracker.js add [customers|revenue|calls] VALUE
node copper-metrics-tracker.js report
```

### Competitive Intel

```bash
node competitor-monitor.js [check|report|save]
```

---

## Next Steps

1. **This Week**: Fix 3 quick UX issues (70 minutes total)
   - Install Playwright
   - Fix email-campaign-generator.js --help
   - Fix linkedin-post-generator.js --help

2. **This Month**: Implement analyze-emails.js (2-4 hours)
   - High ROI: automated email intelligence
   - Reduces daily email triage from 30 min to 5 min

3. **This Quarter**: Build script dashboard
   - Web UI for all business scripts
   - Scheduled runs (weekly competitive reports)
   - Metrics visualization

---

## Success Metrics

Track script usage and business impact:

| Script                      | Usage Goal | Success Metric                 |
| --------------------------- | ---------- | ------------------------------ |
| sales-call-prep.js          | Daily      | 5+ calls/week prepared         |
| roi-calculator-cli.js       | Per demo   | Used in 100% of proposals      |
| email-campaign-generator.js | Weekly     | 10+ emails sent from templates |
| linkedin-post-generator.js  | 3x/week    | 12 posts/month published       |
| competitor-monitor.js       | Weekly     | Updated battlecards monthly    |
| copper-metrics-tracker.js   | Daily      | All metrics current            |

**Goal**: Scripts save 10+ hours/week in sales operations
**Target ROI**: 2 hours/week = 100 hours/year = $10k+ value
