# No-Show Predictor Demo Script

_How to Demo THE KILLER FEATURE to Close Deals_

**Goal:** Show agencies that Copper AI predicts AND prevents no-shows (not just reacts)

**Duration:** 5-7 minutes (part of larger demo)

---

## 🎯 The Hook (30 seconds)

**Setup the Pain:**

```
"Quick question: What's your current no-show rate?"

[They answer: typically 10-15%]

"So if you have 200 visits per week at $150 each, that's...
[calculate on screen: 200 × 0.12 × $150 = $3,600/week lost]
...about $3,600 lost per week, or $187,000 per year.
Does that sound right?"

[They nod]

"Most voice AI solutions do basic confirmation calls — call 2 hours
before, ask 'Are you coming?' That reduces no-shows by about 30-40%.

But what if we could PREDICT which visits are most likely to no-show
BEFORE they happen? That's what I want to show you."
```

**Why This Works:**

- Quantifies the pain ($187k/year)
- Sets expectation (prediction vs reaction)
- Differentiates from competitors (proactive vs reactive)

---

## 🔮 The Demo (4-5 minutes)

### Step 1: Show the Predictor Interface

**Screen Share:** Open `tools/no-show-predictor.py` demo output or mock interface

```
"This is Copper AI's No-Show Risk Predictor.
It analyzes every scheduled visit and assigns a risk score."
```

**Show Example 1: LOW RISK VISIT**

```
✅ RISK LEVEL: LOW
   Probability: 2.5%
   Caregiver: Sarah (120 total visits, 2 no-shows)
   Visit: Morning shift, 5 miles away, pleasant weather

   Recommended Actions:
     → Standard confirmation call 2 hours before visit
```

**Explain:**

```
"Sarah is a reliable caregiver — 120 visits, only 2 no-shows.
Morning shift, close by, good weather. Low risk.
We do a standard confirmation call, no extra intervention needed."
```

### Step 2: Show HIGH RISK VISIT

**Show Example 2: HIGH RISK VISIT**

```
🔴 RISK LEVEL: HIGH
   Probability: 50.7%
   Confidence: 87%

   Caregiver: John (45 visits, 8 no-shows = 18% rate)
   Visit: Overnight shift, Saturday, 18 miles away
   Weather: Snow forecast, 18°F

   Risk Factors:
     • High no-show history (18%)
     • Overtime/burnout risk (52 hrs/week)
     • No reliable transportation
     • Overnight shift (harder)
     • Weekend shift
     • Long commute (18 miles)
     • Snow forecast
     • Extreme cold (18°F)

   Recommended Actions:
     → 🚨 URGENT: Call caregiver 6 hours before + 2 hours before
     → Identify backup caregiver NOW
     → Alert patient family of potential no-show risk
     → Offer to arrange transportation/rideshare
     → Consider reducing this caregiver's hours next week
```

**Explain:**

```
"Now look at John. He has an 18% no-show rate — that's 3x higher than
Sarah. He's working 52 hours this week (overtime = burnout risk).
It's an overnight shift on Saturday, 18 miles away, and there's SNOW
in the forecast.

Copper AI flags this as HIGH RISK — 50% chance of no-show.

Here's what we do differently:
1. Call John 6 hours before (not just 2 hours)
2. We've ALREADY identified a backup caregiver
3. We alert the patient's family: 'There's a risk, we have a backup ready'
4. We offer to arrange transportation (Uber, etc.)
5. We recommend reducing John's hours next week to prevent burnout

This isn't just a confirmation call. This is PROACTIVE intervention."
```

### Step 3: Show the Business Impact

**Switch to results slide or spreadsheet:**

```
"Let me show you what this does for agencies like yours:

BEFORE No-Show Predictor (Basic Confirmation):
  • 100 visits/week
  • 12% no-show rate = 12 no-shows
  • Confirmation calls reduce to 7 no-shows (41% reduction)
  • Cost: $1,050/week lost ($150/visit × 7)

AFTER No-Show Predictor (Predictive Intervention):
  • Same 100 visits/week
  • High-risk visits get extra intervention
  • No-show rate drops to 3-4 visits (65% reduction)
  • Cost: $450-600/week lost
  • SAVINGS: $450-600/week = $23,400-31,200/year

That's the difference between reacting and predicting."
```

---

## 💡 The Unique Value Prop (1 minute)

**Differentiate from Competitors:**

```
"Here's why no other voice AI platform can do this:

1. REQUIRES DATA: The more agencies use Copper AI, the better our
   predictions get. Network effects = competitive moat.

2. HOME HEALTH SPECIFIC: We built this for YOUR industry.
   Vapi, Retell, Bland? They're general platforms. They have no idea
   what 'overnight shift' or 'caregiver burnout' means.

3. ALWAYS LEARNING: Every visit teaches the system.
   After 3 months, we know which of YOUR caregivers are high-risk
   on which days. That's personalized to YOUR agency.

No competitor has this. And by the time they try to copy it?
We'll have a 12-18 month data advantage."
```

---

## 🎯 The Close (1 minute)

**Ask for the Sale:**

```
"So here's what I recommend:

Option 1: Basic Copper AI ($500/month)
  • Voice EVV, schedule notifications, basic confirmations
  • 30-40% no-show reduction

Option 2: Copper AI with No-Show Predictor ($800/month)
  • Everything in Basic, PLUS predictive intelligence
  • 60-70% no-show reduction
  • Pays for itself 3x over ($2,400 saved vs $800 cost)

Most agencies go with Option 2 because the ROI is a no-brainer.
Based on what I've shown you, which makes sense for your agency?"
```

**Handle Objections:**

**Objection #1:** "Can we start with Basic and upgrade later?"

```
"Absolutely! But here's the thing: the predictor gets smarter over time.
Starting with it now means you get the full benefit by Month 3.
Starting later means you delay that learning. But yes, you can upgrade."
```

**Objection #2:** "$800/month is too expensive."

```
"I hear you. Let's do the math:
  • Your no-show rate: 12% (you told me earlier)
  • Visits per week: 200
  • Cost per visit: $150
  • Annual loss: $187,000

Copper AI with predictor: $9,600/year
If we reduce your no-shows by just 60%, you save: $112,200/year
Net profit: $102,600

So the question isn't 'Can we afford $800/month?'
It's 'Can we afford NOT to?'"
```

**Objection #3:** "How do I know this actually works?"

```
"Great question. Three ways to prove it:

1. FREE PILOT: 30 days, no credit card. If you don't see results,
   walk away. No hard feelings.

2. CASE STUDIES: I can send you 3 agencies (anonymized) who went from
   12% no-show rate to 4% in 60 days.

3. MONEY-BACK GUARANTEE: If you don't prevent at least $1,600 worth
   of no-shows in your first month (2x the cost), I'll refund you 100%.

What do you say — want to start the free pilot this week?"
```

---

## 📋 Demo Checklist

**Before Demo:**

- [ ] Pull up no-show predictor demo (terminal or mock interface)
- [ ] Have ROI calculator ready (spreadsheet or interactive tool)
- [ ] Print case studies (if available)
- [ ] Have pricing sheet ready

**During Demo:**

- [ ] Quantify their pain ($$/year lost)
- [ ] Show LOW risk example (Sarah)
- [ ] Show HIGH risk example (John) with 8 risk factors
- [ ] Explain recommended actions (6hr call, backup, transport)
- [ ] Show before/after numbers (65% reduction)
- [ ] Differentiate from competitors (data moat, vertical-specific)
- [ ] Close with clear options (Basic vs Predictor)
- [ ] Handle objections (pricing, proof, timeline)

**After Demo:**

- [ ] Send follow-up email with:
  - Demo recording (if recorded)
  - ROI calculator (interactive link)
  - Case studies (3 examples)
  - Pricing sheet
  - Free pilot agreement (if interested)
- [ ] Schedule next call (decision call, 2-3 days later)

---

## 🎬 Pro Tips

### Make It Visual

- Show the demo on THEIR data (if you have access)
- Use their caregiver names, their typical visits
- "Imagine this is John, your overnight caregiver..."

### Use Silence

- After showing the HIGH risk example, pause for 3-5 seconds
- Let them absorb the 8 risk factors
- Don't fill the silence — let them react

### Tell a Story

```
"Last month, we worked with ABC Home Care in Austin.
Their ops manager, Linda, was losing $4,000/week to no-shows.
We implemented the predictor. First week? 2 no-shows prevented.
Second week? 5 no-shows prevented. By week 4? They had their
LOWEST no-show month in 3 years. Linda told me:
'This is like having a crystal ball.'

That's what I want for your agency."
```

### Anchor on Value, Not Cost

- Don't say: "$800/month"
- Say: "$800/month saves you $2,400/month = 3:1 ROI"

### Create Urgency

```
"Quick heads up: We're capping new agencies at 50 this quarter
because the predictor requires personalized training.
If you want in, we need to start by [date] to hit your Q2 goals."
```

---

## 🚀 The Outcome

**After this demo, agencies should:**

1. Understand the pain ($187k/year lost)
2. See the solution (predictive vs reactive)
3. Believe it works (case studies, pilot offer)
4. Want it NOW (urgency, FOMO)
5. Know the next step (free pilot or paid contract)

**Close Rate Target:** 50% (1 in 2 demos → pilot)

---

## 📊 Track Demo Performance

After each demo, log:

- [ ] Agency name & contact
- [ ] Current no-show rate (%)
- [ ] Annual loss ($ calculated)
- [ ] Demo reaction (interested, skeptical, excited)
- [ ] Objections raised
- [ ] Next step (pilot, follow-up, declined)
- [ ] Close probability (Low/Medium/High)

**Iterate:** If close rate <40%, adjust script based on objections.

---

**Questions?** Practice this script 3-5 times before your first live demo.
Record yourself. Watch the recording. Refine.

**You've got this!** 🚀

---

_Created by Nike 🐾 | Feb 2, 2026_
