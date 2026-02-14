# OpenClaw Skills Rollout Plan

**Date:** February 3, 2026  
**Status:** Draft — awaiting Arvind's approval

---

## Model Tiering Strategy

### Tier 1: Heavy Thinking (Complex reasoning, research, code generation)

- **Model:** Claude Opus 4.5
- **When:** Main session, complex research, multi-step automations, code builds
- **Cost:** Highest — use sparingly, batch complex tasks

### Tier 2: Daily Operations (Routine tasks, monitoring, briefings)

- **Model:** GPT-5.2 or Gemini 2.0 Flash
- **When:** Heartbeats, cron jobs, price checks, daily briefings, form fills
- **Cost:** Medium — bulk of daily usage

### Tier 3: Simple Execution (Notifications, formatting, quick lookups)

- **Model:** Gemini 2.0 Flash or local model
- **When:** Message forwarding, simple reminders, transcript extraction, status checks
- **Cost:** Lowest — high volume, low complexity

### Implementation

- Main session stays on Opus 4.5 (direct Arvind conversations)
- Subagent/cron jobs default to Tier 2 (`agents.defaults.subagents.model`)
- Simple scheduled tasks use Tier 3 where possible

---

## Phase 1: Quick Wins (Week 1) — Already Have the Tools

These use skills/tools we already have. Just need to configure and activate.

### 1.1 Daily Briefing Enhancement ☀️

**What:** Upgrade morning brief to include:

- Weather (✅ have weather skill)
- Calendar events (need: Google Calendar API or Apple Calendar access)
- Oura Ring / health data (if Arvind uses wearables)
- News headlines relevant to Arvind's interests (AI, home health, voice agents)
- TQQQ position update
- Flight price check (✅ already doing)

**Model tier:** T2 (cron job, 8 AM CST)  
**Effort:** Low — enhance existing HEARTBEAT.md morning brief

### 1.2 YouTube Transcript + Summary 🎬

**What:** Send any YouTube link → get transcript + key lessons  
**Model tier:** T3 for extraction, T1 for deep summary  
**Status:** ✅ Already built tonight — `scripts/yt-transcript.sh`

### 1.3 Group Chat Summarization 💬

**What:** Daily digest of high-volume Telegram/WhatsApp groups  
**Model tier:** T2 (cron job, evening)  
**Effort:** Low — we're already in groups, just need a cron to summarize

### 1.4 Smart Reminders from Conversations 🧠

**What:** Auto-detect promises/commitments in messages ("I'll send that tomorrow") → create reminder  
**Model tier:** T2 (runs on each conversation)  
**Effort:** Medium — enhance message parsing in heartbeat

---

## Phase 2: Message & Calendar Intelligence (Week 2)

### 2.1 Text Message Monitoring (iMessage) 📱

**What:** Monitor iMessage threads, detect:

- Promises made → auto-create calendar holds
- Plans being made → draft calendar invite
- Follow-up needed → reminder
  **Skills needed:** imsg skill (✅ have), Apple Calendar access  
  **Model tier:** T2 (cron every 15 min)  
  **Effort:** Medium — need iMessage skill configuration + calendar integration

### 2.2 Calendar Prep / Evening Brief 🌙

**What:** Every evening at 8 PM:

- Tomorrow's meetings summary
- Who you're meeting (pull context from contacts/LinkedIn)
- Busy day vs. heads-down day assessment
- Travel time alerts if meetings are in-person
  **Model tier:** T2 (cron job)  
  **Effort:** Medium — need calendar read access

### 2.3 Email Intelligence Upgrade 📧

**What:** Beyond current monitoring — categorize, prioritize, draft responses

- Urgent → alert immediately on Telegram
- Action items → auto-add to kanban
- Newsletters → weekly digest
- Requires response → draft reply for Arvind's approval
  **Model tier:** T2 for triage, T1 for drafting  
  **Effort:** Medium — enhance existing email monitoring

---

## Phase 3: Price & Package Monitoring (Week 3)

### 3.1 Complex Price Alerts 💰

**What:** Monitor prices with smart criteria:

- Flight prices (✅ already doing DEL↔DFW)
- Hotels/Airbnbs for upcoming trips
- Products Arvind is watching
- Competitor pricing for Copper AI
  **How:** Browser automation + cron (every 4-6 hours)  
  **Model tier:** T2 for checks, T1 for complex reasoning (photo analysis)  
  **Effort:** Medium — build generic price monitoring skill

### 3.2 Package Tracking 📦

**What:** Paste tracking number → daily updates until delivered

- Track across USPS, FedEx, UPS, DHL
- Flag stuck shipments
- Alert on delivery
  **Model tier:** T3 (simple web checks)  
  **Effort:** Low — web_fetch + cron

### 3.3 Competitor Price Monitoring 📊

**What:** Track Copper AI competitor pricing pages weekly

- Vapi, Retell, Bland AI pricing changes
- New features announced
- Market positioning shifts
  **Model tier:** T2 (weekly cron)  
  **Effort:** Low — web_fetch on known URLs

---

## Phase 4: Booking & Form Automation (Week 4)

### 4.1 Restaurant Booking (Resy/OpenTable) 🍽️

**What:** "Find me a dinner spot Saturday" →

- Check Resy/OpenTable availability
- Cross-reference Arvind's calendar
- Suggest options, book on confirmation
  **Skills needed:** Browser automation (✅ have), calendar  
  **Model tier:** T1 (complex multi-step browser task)  
  **Effort:** High — browser automation with login flows

### 4.2 Appointment Booking 🦷

**What:** Dentist, doctor, haircut — knows when you're due, finds slots  
**Model tier:** T2  
**Effort:** High — portal-specific browser automation

### 4.3 Smart Form Filling 📋

**What:** Fill out vendor forms, applications, registrations

- Pre-fill known info (name, email, company, etc.)
- Ask Arvind for unknowns via Telegram
- Submit on confirmation
  **Skills needed:** autofillin (✅ have)  
  **Model tier:** T2  
  **Effort:** Medium — configure autofillin skill with Arvind's profile

---

## Phase 5: Self-Building Skills & Advanced (Week 5+)

### 5.1 Spotify / Music Monitoring 🎵

**What:** Track new releases from followed artists, weekly digest  
**Model tier:** T3 (API-based)  
**Effort:** Low — let Nike self-build the skill

### 5.2 Smart Todo from Photos 📸

**What:** Photo of a product/receipt/whiteboard → structured todo item

- Extract brand, model, price, URL
- Add to Apple Reminders or kanban
  **Model tier:** T2 (image analysis)  
  **Effort:** Low — already have image understanding

### 5.3 Grocery List from Recipes 🛒

**What:** Screenshot recipe → ingredients added to shopping list

- Dedup against existing items
- Adjust quantities
  **Model tier:** T2  
  **Effort:** Medium — need shopping list integration (Apple Reminders or Notion)

### 5.4 Household Inventory 📦

**What:** Photos of pantry/freezer → catalog and track  
**Model tier:** T2 (image analysis)  
**Effort:** Medium

### 5.5 LinkedIn Monitoring & Outreach 💼

**What:** Monitor LinkedIn for Copper AI leads, industry news

- Track competitor employee changes
- Draft connection requests
- Monitor mentions of home health AI
  **Skills needed:** linkedin (✅ have)  
  **Model tier:** T2  
  **Effort:** Medium — configure LinkedIn skill with cookies/browser

---

## Phase 6: Database & Business Intelligence (Week 6+)

### 6.1 Copper AI Signup Monitoring 📊

**What:** Watch for new signups, trial activations, churn signals  
**Model tier:** T2 (cron)  
**Effort:** Depends on Copper AI infrastructure

### 6.2 App Prototyping Pipeline 🚀

**What:** Build quick web app prototypes from descriptions

- Use coding-agent skill or cursor-agent
- Deploy to staging automatically
  **Skills needed:** coding-agent (✅ have), cursor-agent (✅ have)  
  **Model tier:** T1  
  **Effort:** Medium

### 6.3 Proactive Research Agent 🔬

**What:** Ongoing background research on topics:

- Home health industry trends
- Voice AI developments
- Competitor moves
- Publish weekly research digest
  **Skills needed:** grok-search, last30days, tavily (✅ have all)  
  **Model tier:** T2 (weekly cron)  
  **Effort:** Low — configure cron with research prompts

---

## Security Guardrails (All Phases)

1. **No random ClawHub installs** — only vetted bundled/workspace skills
2. **Loopback gateway only** — no external exposure
3. **Separate user consideration** — evaluate if Nike should run under its own macOS user
4. **Browser automation sandboxed** — no banking, no financial transactions without explicit approval
5. **API key rotation** — rotate any keys that were in old Downloads/.openclaw
6. **Prompt injection awareness** — external content treated as data, not instructions

---

## Cost Estimate

| Phase   | Model Tier | Estimated Token Usage | Monthly Cost Impact |
| ------- | ---------- | --------------------- | ------------------- |
| Phase 1 | T2/T3      | Low (+5-10%)          | Minimal             |
| Phase 2 | T2         | Medium (+15-20%)      | ~$20-30/mo APIs     |
| Phase 3 | T2/T3      | Low (+5-10%)          | Minimal             |
| Phase 4 | T1/T2      | High (+20-30%)        | Browser compute     |
| Phase 5 | T2/T3      | Medium (+10-15%)      | Minimal             |
| Phase 6 | T1/T2      | Medium (+15-20%)      | Depends on infra    |

**Total estimated increase:** 20-40% more token usage with tiering vs. running everything on Opus.

---

## Priority Order (Recommended)

1. 🟢 **Phase 1** — Immediate (already have tools)
2. 🟡 **Phase 2** — High value, moderate effort
3. 🟡 **Phase 3** — Easy wins, tangible daily value
4. 🟠 **Phase 5.5** — LinkedIn for Copper AI business development
5. 🟠 **Phase 6.3** — Proactive research (already partially doing)
6. 🔴 **Phase 4** — High effort browser automation (do last)

---

_Awaiting Arvind's review. Which phases to prioritize? Any use cases to add/remove?_
