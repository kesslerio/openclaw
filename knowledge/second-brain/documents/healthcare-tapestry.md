# 🏥 Healthcare Documentation Tapestry

**Created:** January 29, 2026  
**Purpose:** Interlinked knowledge network of all Copper AI / iCare healthcare documentation

---

## 🕸️ Knowledge Map

```
                    ┌─────────────────────┐
                    │   COPPER DIGITAL    │
                    │   (Parent Company)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │       iCARE         │
                    │  AI Voice Agents    │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼───────┐    ┌────────▼────────┐    ┌───────▼───────┐
│  TARGET MKT   │    │   TECHNOLOGY    │    │   MARKETING   │
│ Home Health   │    │   Voice AI +    │    │   Pamphlet +  │
│   Agencies    │    │   Telephony     │    │   Pilots      │
└───────────────┘    └─────────────────┘    └───────────────┘
```

---

## 📚 Document Inventory

| Document                     | Type           | Purpose                              | Link                                         |
| ---------------------------- | -------------- | ------------------------------------ | -------------------------------------------- |
| **copper-ai-icare.md**       | Knowledge Base | Product overview, tech stack, status | [→ View](copper-ai-icare.md)                 |
| **copper-ai-pamphlet-v1.md** | Marketing      | Sales pamphlet draft                 | [→ View](../drafts/copper-ai-pamphlet-v1.md) |
| **clawdbot-5-usecases.md**   | Operations     | Nike automation setup                | [→ View](clawdbot-5-usecases.md)             |
| **arvind-todo-jan28.md**     | Tasks          | Active to-do items                   | [→ View](../memory/arvind-todo-jan28.md)     |

---

## 🎯 Core Product: iCare

### What It Is

AI-powered voice agents that handle inbound calls for home health agencies — 24/7, with zero hold times.

### Problem → Solution Matrix

| Agency Pain Point             | iCare Solution             |
| ----------------------------- | -------------------------- |
| Missed after-hours referrals  | 24/7 AI answering          |
| Staff burnout on intake calls | Automated intake flow      |
| Manual EMR data entry         | Direct EMR integration     |
| Inconsistent call quality     | Standardized AI responses  |
| Scalability constraints       | Unlimited concurrent calls |

### Key Differentiators

1. **Built for home health** — Not generic AI adapted to healthcare
2. **EMR Integration** — Axxess, WellSky, MatrixCare compatible
3. **HIPAA-Compliant** — Healthcare-first security
4. **Human-like voice** — ElevenLabs TTS technology
5. **15+ years enterprise experience** — Copper Digital's track record

---

## 🏢 Target Market Deep Dive

### Primary: Home Health Agencies

- **Size:** 10-200 employees
- **Pain:** Phone volume, referral capture, admin burden
- **Buyer:** Agency owners, administrators, ops directors

### Use Cases (Pilot Focus)

1. **Inbound Referral Capture** — Main value prop
2. **After-Hours Support** — Competitive differentiator
3. **Intake Automation** — Efficiency play

### Industry Context

- **Conferences attended:** NAHC 2025, HCAOA
- **Geography focus:** Texas, Oklahoma (initial)
- **Competitive landscape:** To be researched

---

## 🔧 Technical Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Telephony  │────▶│   Voice AI  │────▶│     LLM     │
│   (TBD)     │     │ (ElevenLabs)│     │  (Claude?)  │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                    ┌─────────────────────────────────┐
                    │         EMR Integration         │
                    │  Axxess | WellSky | MatrixCare  │
                    └─────────────────────────────────┘
```

### Known Components

- **TTS:** ElevenLabs (confirmed in Clawdbot config)
- **STT:** Deepgram (configured)
- **LLM:** Claude/GPT (conversation handling)
- **Telephony:** TBD (Twilio/Vonage likely)

---

## 📊 Key Metrics (From Pamphlet)

| Metric                   | Before iCare | After iCare        |
| ------------------------ | ------------ | ------------------ |
| After-hours missed calls | 23%          | 0%                 |
| Average intake call time | 8+ min       | 3 min              |
| Staff cost (data entry)  | $45/hr       | Redirected to care |

---

## 📅 Current Status & Pipeline

### Active Work

- **Pilots:** Multiple healthcare clients (names TBD)
- **Meeting:** Vivin Ramamoorthy — Feb 3, 2026
- **Team:** Manas Mallik, Michael McGowan (PT/OT docs)

### Marketing Status

- ✅ Pamphlet draft v1 complete
- ⏳ Needs Arvind review
- ⏳ Design/visuals pending

### Nike Support Tasks

- Morning briefs (8am CST)
- Research reports (2pm CST)
- Overnight vibe coding (11pm CST)

---

## 🔗 Cross-References

### Related To-Do Items

From `arvind-todo-jan28.md`:

- Create marketing pamphlet (done — needs review)
- Prepare for Vivin meeting
- Research competitor landscape

### Automation Connections

From `clawdbot-5-usecases.md`:

- Daily research includes home health AI trends
- Second brain captures Copper AI knowledge
- Last30days skill for market research

---

## 📈 Growth Opportunities

### Immediate (Q1 2026)

1. Close pilot clients → case studies
2. EMR integration depth
3. Geographic expansion beyond TX/OK

### Near-term

1. Additional use cases (scheduling, follow-up)
2. Outbound calling capabilities
3. Multi-language support

### Research Needed

- [ ] Competitor analysis (AI voice in home health)
- [ ] Pricing benchmarks
- [ ] Integration requirements by EMR

---

## 🗣️ Key Messaging

### Elevator Pitch

> "iCare is an AI voice agent that answers your agency's calls 24/7, captures every referral, and puts the data directly in your EMR — so your team can focus on patient care instead of phone tag."

### Tagline Options

- "Never Miss Another Referral"
- "AI Voice Agents Built for Home Health"
- "Your 24/7 Intake Specialist"

---

## 📝 Notes & Observations

- Strong product-market fit signal (agency pain is real)
- Pamphlet is well-written, needs visual design
- Technical architecture partially documented
- Need more competitor intel for positioning

---

_Tapestry maintained by Nike 🐾_  
_Last updated: January 29, 2026_
