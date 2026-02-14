# Senior Architect Onboarding Guide

**Created:** February 8, 2026
**Purpose:** Complete system overview for new team members joining the project
**Owner:** Arvind Sarin, Copper Digital

---

## Quick Orientation

You are looking at **three interconnected systems** running on a Mac Mini (Tailscale: `100.99.190.40`):

| System                     | Port  | What It Does                            | Location                 |
| -------------------------- | ----- | --------------------------------------- | ------------------------ |
| **OpenClaw Gateway**       | 18789 | Multi-channel AI messaging gateway      | `openclaw/`              |
| **Kanban Mission Control** | 8888  | Task management dashboard (85 tasks)    | `openclaw/tools/kanban/` |
| **Memex Search API**       | 8765  | Semantic search over emails/transcripts | `openclaw/skills/memex/` |

> **NOTE:** The `clawd/` repo has been consolidated into `openclaw/`. Kanban lives at `tools/kanban/`, Memex at `skills/memex/`, and scripts at `tools/copper-scripts/`.

---

## 1. OpenClaw - The AI Gateway

**What:** Open-source personal AI assistant platform. One AI brain, many messaging channels.
**Repo:** https://github.com/openclaw/openclaw (upstream) + Arvind's fork
**Version:** v2026.2.3 (Feb 3, 2026)
**Tech:** TypeScript (ESM), Node.js 22+, pnpm monorepo

### Scale

- 2,557 TypeScript files, 445,412 lines of code
- 31 extension plugins
- 54 bundled skills
- 600+ documentation files (Mintlify-hosted at docs.openclaw.ai)
- Native apps: macOS, iOS, Android

### Active Messaging Channels

All connected and operational:

- WhatsApp (+14697421095)
- Telegram (@SarinAI_bot)
- Discord (@Nike SarinAI)
- Slack (socket mode)
- iMessage (BlueBubbles)
- Signal (paired)

### Key Commands

```bash
# Check gateway status
pnpm openclaw channels status --probe

# Build
pnpm build          # TypeScript compile + UI bundle (3.7s)

# Test
pnpm test           # Vitest, 70% coverage threshold

# Lint
pnpm check          # Oxlint + Oxfmt

# Run dev
pnpm openclaw ...   # Any CLI command
```

### Project Conventions

Read `AGENTS.md` (symlinked as `CLAUDE.md`) for all coding standards. Key points:

- TypeScript strict, ESM only
- Tests colocated as `*.test.ts`
- Commits via `scripts/committer "<msg>" <file...>`
- Changelog: latest version at top, no "Unreleased" section
- PR flow: temp branch from main, squash/rebase, merge back

### Directory Map

```
openclaw/
├── src/                    # Core source (2,557 .ts files)
│   ├── agents/             # AI agent tools, sessions, sub-agents
│   ├── channels/           # Channel routing and delivery
│   ├── cli/                # CLI commands
│   ├── config/             # Config schema and types
│   ├── discord/            # Discord integration
│   ├── gateway/            # Gateway server
│   ├── imessage/           # iMessage (BlueBubbles)
│   ├── infra/              # Infrastructure (ports, env, errors)
│   ├── memory/             # Memory management and search
│   ├── plugins/            # Plugin SDK and runtime
│   ├── providers/          # LLM providers
│   └── routing/            # Message routing
├── extensions/             # 31 plugin packages (messaging, auth, memory)
├── skills/                 # 54 skill modules
├── apps/                   # macOS, iOS, Android native apps
├── docs/                   # 600 docs (Mintlify)
├── tools/                  # Kanban, copper-scripts, integrations, marketing
├── scripts/                # 74 build/deploy scripts
├── test/                   # Test configs
└── ui/                     # Control UI + WebChat frontend
```

---

## 2. Kanban Mission Control

**What:** React + Express task management board with AI analysis
**Access:** http://localhost:8888 or http://100.99.190.40:8888
**Built:** Feb 4, 2026 (single session, 15,888 lines)

### Current State

- 85 tasks migrated from old format
- 10 tasks AI-analyzed (automation classification)
- 75 tasks pending analysis
- Categories: CopperAI (16), Personal (29), General (40)
- Priority: 11 High, 46 Medium, 28 Low

### API Endpoints

```
GET    /api/kanban              # Full board data
GET    /api/tasks               # All tasks (filterable by status, priority)
POST   /api/tasks               # Create task
PUT    /api/tasks/:id           # Update task
DELETE /api/tasks/:id           # Delete task
POST   /api/tasks/:id/move      # Quick status change
GET    /api/status              # Mission Control metrics
```

### Server Management

```bash
# Check if running
lsof -ti:8888

# View logs
tail -f ~/Cursor/Claude-2026/openclaw/tools/kanban/logs/server.log

# Restart
lsof -ti:8888 | xargs kill -9
cd ~/Cursor/Claude-2026/openclaw/tools/kanban/server
nohup node server.js > ../logs/server.log 2>&1 &
```

### Data Location

Single source of truth: `openclaw/tools/kanban/data/kanban.json`

---

## 3. Memex - AI Knowledge System

**What:** Personal AI memory system. Indexes emails (and eventually Plaud.AI transcripts) into a searchable vector store, generates daily journals, and provides a chat interface for querying your own history.

**Location:** `/Users/arvindsarin/Cursor/Claude-2026/openclaw/skills/memex/`

### Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  DATA SOURCES│     │   HISTORIAN   │     │  JOURNALIST   │     │   PARTNER    │
│              │     │  (Phase 2)   │     │  (Phase 3)   │     │  (Phase 4)   │
│ Gmail 26,818│────→│ ChromaDB     │────→│ Journal Gen  │────→│ Query Engine │
│ Plaud 2,500 │     │ MiniLM embed │     │ Claude via   │     │ FastAPI      │
│ (blocked)   │     │ Search API   │     │ OpenClaw     │     │ React UI     │
│ Calendar    │     │ Port 8765    │     │ 217 journals │     │ Chat         │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### Phase Status

| Phase | Name                   | Status       | What Works                                                  |
| ----- | ---------------------- | ------------ | ----------------------------------------------------------- |
| 1     | EXODUS (Plaud scraper) | **BLOCKED**  | Code done, 0 files downloaded. CSS selectors unvalidated.   |
| 2     | HISTORIAN (indexing)   | **COMPLETE** | ChromaDB + free local embeddings (all-MiniLM-L6-v2, 384d)   |
| 3     | JOURNALIST (journals)  | **COMPLETE** | 26,818 emails indexed, 1 journal generated, 216 ready       |
| 4     | PARTNER (chat UI)      | **80%**      | Query engine + React frontend + FastAPI built, not deployed |

### What Works Right Now

```bash
# Check system status
memex status

# Generate all 216 historical journals (~3 hours, ~$6.51)
memex backfill

# Generate with limit (testing)
memex backfill --max 5

# Sync recent emails/calendar
memex sync

# Semantic search
curl http://localhost:8765/search?q=clearcare
```

### Plaud Scraper - The Bottleneck

**Problem:** 2,500 meeting transcripts locked in web.plaud.ai with no official export API.

**What exists:**

- Complete Playwright scraper (`scraper/plaud_scraper.py`, 1,164 lines)
- Session cookies file (12KB, from Feb 1 - likely expired)
- Rate limiter, retry logic, batch export
- 14 TDD test cases (not validated against real site)
- Debug tools (`capture_selectors.py`, `debug_click.py`)

**What's blocking:**

1. CSS selectors are guessed, never validated against real Plaud.AI HTML
2. Authentication not tested with real credentials
3. Never run end-to-end

**To unblock (30-60 min hands-on):**

1. Log into web.plaud.ai in Chrome
2. Open DevTools (Cmd+Opt+I), inspect the recording list
3. Update `PlaudSelectors` class in `plaud_scraper.py` with real selectors
4. Test download of 1 file
5. Scale: 10 -> 100 -> 2,500 (6-12 hours runtime with rate limiting)

**Alternative:** Check if Plaud added bulk export since Feb 1. Also check OAuth API waitlist status (form link in `scraper/DECISION.md`).

### Key Files

| What                | Path                                    |
| ------------------- | --------------------------------------- |
| Scraper code        | `memex/scraper/plaud_scraper.py`        |
| Scraper models      | `memex/scraper/models.py`               |
| Selector debug tool | `memex/scraper/capture_selectors.py`    |
| Vector store        | `memex/historian/vector_store.py`       |
| Search API          | `memex/historian/search_api.py`         |
| Journal generator   | `memex/journalist/journal_generator.py` |
| Query engine        | `memex/retrieval/query_engine.py`       |
| FastAPI backend     | `memex/api/main.py`                     |
| React frontend      | `memex/frontend/src/`                   |
| Daily automation    | `memex/scripts/daily_ingest.py`         |
| Config              | `memex/.env`                            |

---

## 4. Second Brain (Knowledge Base)

**Location:** `/Users/arvindsarin/Cursor/Claude-2026/openclaw/knowledge/second-brain/`
**Documents:** 34 files covering Copper AI business intelligence

### Categories

| Category          | Count | Key Docs                                                             |
| ----------------- | ----- | -------------------------------------------------------------------- |
| Memex System      | 5     | README, QUICKSTART, visual-plan, timeline, index.html                |
| Business Strategy | 6     | Product roadmap, investor pitch, competitors, battlecard             |
| Integrations      | 7     | ClearCare (#1), Axxess (#2), EVV, AWS, Rivvi, Telegram               |
| Market Research   | 9     | $246B home health industry, Texas market, AI trends, voice AI        |
| Operations        | 1     | Customer success retention playbook (95%+ target)                    |
| Knowledge Base    | 3+1   | Clawdbot use cases, Copper AI/iCare KB, healthcare tapestry, journal |

### Key Business Numbers

- Home health market: $246B (2026) growing to $692B (2035)
- Addressable agencies: 33,000 Medicare + 21,000 private
- ClearCare/WellSky: 4,500 agencies ($27M ARR potential)
- Axxess: 7,000 agencies ($42M ARR potential)
- Copper AI pricing: $297-797/month, 85%+ gross margin
- Competitive advantage: 50-70% lower cost than Vapi/Retell, EVV integrated

---

## 5. Recent Git Activity (Last 10 Commits)

| Date  | Hash      | What                                                                 |
| ----- | --------- | -------------------------------------------------------------------- |
| Feb 6 | `7c13e11` | Universal Briefing: production hardening, API, testing (2,144 lines) |
| Feb 4 | `2be24b5` | Memory: progressive disclosure for memory_search (474 lines)         |
| Feb 4 | `9a05b36` | Kanban Mission Control v2.0 (15,888 lines, 93 files)                 |
| Feb 3 | `e4b084c` | Version bump to 2026.2.3                                             |
| Feb 3 | `3e6c623` | Policy test cleanup                                                  |
| Feb 3 | `9c4eab6` | iMessage: BlueBubbles promotion, docs refresh                        |
| Feb 3 | `9c5941b` | Legacy daemon-cli shim for updates                                   |
| Feb 3 | `41d2993` | Matrix allowlist wizard fix                                          |
| Feb 3 | `d3ba57b` | Configurable web_fetch maxChars cap                                  |
| Feb 3 | `6b4b604` | Nextcloud Talk allowlist enforcement                                 |

---

## 6. Network & Access

| What                 | Address                         |
| -------------------- | ------------------------------- |
| Mac Mini (Tailscale) | 100.99.190.40                   |
| SSH                  | `ssh arvindsarin@100.99.190.40` |
| Gateway              | http://100.99.190.40:18789      |
| Kanban Dashboard     | http://100.99.190.40:8888       |
| Memex Search API     | http://localhost:8765           |

### Background Services

- **Gateway:** LaunchD `ai.openclaw.gateway` (auto-restart)
- **Clawd Sync:** Auto-commits changes to git every 30s
- **Memex Automation:** 7AM email sync, 9PM journal generation

---

## 7. Security Considerations

### In Place

- Channel allowlists (per-user, per-channel)
- `.secrets.baseline` (detect-secrets scanning)
- Pre-commit hooks
- Prompt injection prevention
- Zero-trust for external sources

### Needs Review

- Port exposure (8765, 8888, 8889, 18789)
- Tailscale access controls
- Supabase credentials (not yet configured)
- WCAG 2.1 AA compliance deadline: May 2026
- California AB 3030 AI disclosure (active since Jan 2025)
- Texas TRAIGA AI disclosure (active since Jan 2026)

---

## 8. Known Issues & Tech Debt

1. **Consolidation complete:** The `clawd/` repo has been merged into `openclaw/`. Kanban is at `tools/kanban/`, Memex at `skills/memex/`, and scripts at `tools/copper-scripts/`.
2. **Nike identity retired:** Operating rules merged into MEMORY.md. The agent system is unified under OpenClaw.
3. **Plaud scraper stalled:** CSS selectors unvalidated, 0 files downloaded. 30-60 min of hands-on work to unblock.
4. **75 tasks need AI analysis:** Only 10/85 kanban tasks have been classified.
5. **Memex frontend not deployed:** React UI built but not served.
6. **Health monitoring cron not scheduled:** Script exists at `~/.openclaw/scripts/health-monitor.sh` but not active.

---

## 9. Quick Start Commands

```bash
# === OpenClaw ===
cd ~/Cursor/Claude-2026/openclaw
pnpm openclaw channels status --probe   # Check all channels
pnpm build                               # Build project
pnpm test                                # Run tests

# === Kanban ===
open http://localhost:8888               # Dashboard
curl http://localhost:8888/api/status    # API health

# === Memex ===
memex status                             # System status
memex backfill --max 1                   # Test: generate 1 journal
curl http://localhost:8765/search?q=test # Semantic search

# === Git ===
cd ~/Cursor/Claude-2026/openclaw
git log --oneline -10                    # Recent commits
git status                               # Working tree state

# === Remote Access ===
ssh arvindsarin@100.99.190.40            # SSH to Mac Mini
```

---

## 10. For the Architect: Priority Actions

1. **Read** `AGENTS.md` (= `CLAUDE.md`) for all project conventions
2. **Review** project structure (consolidation from clawd is complete)
3. **Review** port exposure and Tailscale access controls
4. **Decide** on Plaud scraper approach (fix selectors vs wait for API vs alternative)
5. **Run** `memex backfill` to generate the 216 pending journals (low-hanging fruit)
6. **Review** ClearCare/Axxess integration plans in `knowledge/second-brain/` before deployment

---

_This document was generated on February 8, 2026 and reflects the state of the system at that time._
