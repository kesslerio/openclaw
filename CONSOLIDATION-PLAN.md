# Consolidation Plan: clawd/ -> openclaw/

**Created:** February 8, 2026
**Status:** PROPOSED (Pending architect review)
**Requested by:** Arvind Sarin

---

## The Problem

Currently there are **two separate systems** that should be one:

1. **`openclaw/`** - The AI gateway (upstream open-source project)
2. **`clawd/`** - A separate repo with Kanban, Memex, Second Brain, sales tools, memory logs, and an autonomous agent personality called "Nike"

Arvind's position: **Everything should live inside `openclaw/`.** The split is confusing, creates duplicate concepts, and makes onboarding harder.

### Specific Pain Points

| Issue             | Current State                                       | Desired State                                 |
| ----------------- | --------------------------------------------------- | --------------------------------------------- |
| Two repos         | `openclaw/` + `clawd/`                              | Single `openclaw/` repo                       |
| Two personalities | "Nike" (clawd) + Claude (openclaw)                  | One unified agent                             |
| Duplicate kanban  | `openclaw/clawd/data/kanban.json` + `clawd/kanban/` | Single task system                            |
| Memex location    | `clawd/memex/`                                      | `openclaw/skills/memex/` or `openclaw/memex/` |
| Second brain      | `clawd/second-brain/`                               | `openclaw/knowledge/` or similar              |
| Memory logs       | `clawd/memory/` (45 daily logs)                     | OpenClaw's built-in memory system             |

---

## Pros and Cons

### Option A: Move Everything Into openclaw/ (Arvind's Preference)

**Pros:**

- Single repo, single mental model
- One agent personality, no confusion
- Easier onboarding for new team members
- Git history in one place
- Simpler deployment and CI/CD
- OpenClaw already has skills, memory, and plugin systems that can host this

**Cons:**

- openclaw/ is a fork of an upstream open-source project - custom additions create merge conflicts
- `clawd/` contains personal/business data (finances, taxes, contacts) that should NOT be in a code repo
- Large migration effort (140+ memex files, 34 second-brain docs, 45 memory logs, 630+ scripts)
- Risk of breaking the Kanban server, Memex API, and automations during migration

### Option B: Keep Separate But Clean Up References

**Pros:**

- No migration risk
- Personal data stays separate from code
- Upstream merges stay clean

**Cons:**

- Two repos remain confusing
- Doesn't address Arvind's core concern

### Option C: Hybrid - Move Code Into openclaw/, Keep Data External (RECOMMENDED)

**Pros:**

- Code consolidation (one repo for all code)
- Personal/business data stays separate (not in git)
- OpenClaw skills system already supports this pattern
- Minimal upstream merge conflicts (additions only, no core changes)
- Clean separation of concerns

**Cons:**

- Some complexity in data symlinks
- Need to update all path references

---

## Recommended Migration Plan (Option C)

### Phase 1: Memex -> OpenClaw Skill (Week 1)

Memex is already partially set up as an OpenClaw skill at `~/.openclaw/skills/memex/`. Complete the migration:

```
BEFORE:                              AFTER:
clawd/memex/                         openclaw/skills/memex/
  scraper/                             scraper/
  historian/                           historian/
  journalist/                          journalist/
  retrieval/                           retrieval/
  api/                                 api/
  frontend/                            frontend/
  tests/                               tests/
  scripts/                             scripts/

clawd/memex/data/                    ~/memex-data/  (symlinked, NOT in git)
```

**Steps:**

1. Copy all memex Python code into `openclaw/skills/memex/`
2. Move data directory to `~/memex-data/` with symlink
3. Update all path references
4. Test: `memex status`, `memex backfill --max 1`, search API
5. Remove `clawd/memex/` after verification

### Phase 2: Kanban -> OpenClaw Extension (Week 1-2)

The Kanban system is already inside `openclaw/clawd/`. Promote it to a proper location:

```
BEFORE:                              AFTER:
openclaw/clawd/                      openclaw/tools/kanban/
  server/                              server/
  frontend/                            frontend/
  data/                                data/ -> ~/kanban-data/ (symlink)
```

**Steps:**

1. Move `openclaw/clawd/server/` and `openclaw/clawd/frontend/` to `openclaw/tools/kanban/`
2. Move kanban data to `~/kanban-data/` with symlink
3. Update server paths and frontend API URLs
4. Test: http://localhost:8888 still works
5. Clean up old `openclaw/clawd/` directory

### Phase 3: Second Brain -> OpenClaw Knowledge (Week 2)

```
BEFORE:                              AFTER:
clawd/second-brain/                  openclaw/knowledge/
  (34 markdown docs)                   second-brain/
                                       (34 markdown docs)
```

**Steps:**

1. Copy second-brain docs to `openclaw/knowledge/second-brain/`
2. Verify all docs present
3. Remove from `clawd/`

### Phase 4: Retire "Nike" Personality (Week 2-3)

The "Nike" agent is defined by several files in `clawd/`:

- `SOUL.md` - Core values
- `IDENTITY.md` - Personality
- `USER.md` - Arvind's profile
- `AGENTS.md` - Operating rules
- `HEARTBEAT.md` - Autonomous task management

**Action:** Merge useful operating rules into OpenClaw's `AGENTS.md`. The personality, heartbeat, and identity files should be retired. OpenClaw's agent system handles this natively.

**Steps:**

1. Review `clawd/HEARTBEAT.md` for automation rules worth keeping
2. Merge any useful patterns into `openclaw/AGENTS.md`
3. Configure OpenClaw's built-in agent/skill system to handle:
   - Morning briefs (already a skill: `skills/universal-briefing/`)
   - Task management (kanban integration)
   - Memory (OpenClaw's `memory-core` extension)
4. Do NOT migrate personality files - let OpenClaw be OpenClaw

### Phase 5: Archive Personal Data (Week 3)

These `clawd/` directories contain personal/business data that should NOT be in any code repo:

- `clawd/contacts/` -> `~/copper-data/contacts/`
- `clawd/finance/` -> `~/copper-data/finance/`
- `clawd/taxes/` -> `~/copper-data/taxes/`
- `clawd/personal/` -> `~/copper-data/personal/`
- `clawd/memory/` (45 daily logs) -> `~/copper-data/memory/`

**Steps:**

1. Create `~/copper-data/` directory
2. Move personal data there
3. Ensure backups exist
4. Remove from `clawd/` repo

### Phase 6: Sales/Marketing Tools (Week 3)

```
BEFORE:                              AFTER:
clawd/sales/                         openclaw/tools/copper-sales/
clawd/marketing/                     openclaw/tools/copper-marketing/
clawd/integrations/                  openclaw/tools/copper-integrations/
clawd/copper-ai/                     openclaw/tools/copper-ai/
```

### Phase 7: Retire clawd/ Repo (Week 4)

Once everything is migrated and verified:

1. Final check: nothing in `clawd/` is still referenced
2. Archive `clawd/` repo (don't delete, just archive on GitHub)
3. Remove local clone
4. Update all documentation references

---

## Migration Checklist

```
[x] Phase 1: Memex -> openclaw/skills/memex/ (COMPLETED 2026-02-13)
    [x] Copy 194 code files (5.3MB, excluding data/node_modules/caches)
    [x] Move data to ~/memex-data/ (346MB: ChromaDB, FAISS, context cache)
    [x] Symlink skills/memex/data -> ~/memex-data/
    [x] Update 8 Python files with hardcoded clawd paths
    [x] Remove .env with secrets (kept .env.example)
    [ ] Test memex status/backfill/search (needs manual verification)
    [ ] Remove old location (deferred to Phase 7)

[x] Phase 2: Kanban -> openclaw/tools/kanban/ (COMPLETED 2026-02-09)
    [x] Move server + frontend
    [x] Move data (kept in-repo at tools/kanban/data/)
    [x] Update paths in all documentation
    [x] Update all 8 kanban script paths in scripts/*.cjs (2026-02-13)
    [x] Test dashboard + API (all endpoints verified)
    [x] Clean up old clawd/ directory

[x] Phase 3: Second Brain -> openclaw/knowledge/ (COMPLETED 2026-02-13)
    [x] Copy 35 files (33 markdown + 1 HTML + subdirs)
    [x] Verify completeness (35/35 files match)
    [ ] Remove old location (deferred to Phase 7)

[ ] Phase 4: Retire Nike personality
    [ ] Review HEARTBEAT.md for useful rules
    [ ] Merge into openclaw/AGENTS.md
    [ ] Configure skills for automations
    [ ] Remove personality files

[x] Phase 5: Archive personal data (COMPLETED 2026-02-13)
    [x] Create ~/copper-data/
    [x] Copy contacts (4 files), finance (1), taxes (2), personal (1), memory (51)
    [ ] Verify backups
    [ ] Remove from clawd/ repo (deferred to Phase 7)

[x] Phase 6: Sales/Marketing tools (COMPLETED 2026-02-13)
    [x] Copy sales (37 files) to tools/copper-sales/
    [x] Copy marketing (21 files) to tools/copper-marketing/
    [x] Copy integrations (35 files) to tools/copper-integrations/
    [x] Copy copper-ai (10 files) to tools/copper-ai/

[ ] Phase 7: Retire clawd/ repo
    [ ] Final verification
    [ ] Archive on GitHub
    [ ] Remove local clone
    [ ] Update all docs
```

---

## Risk Mitigation

- **Before ANY move:** Create full backup of both repos
- **Move one phase at a time:** Don't batch. Verify each phase works before starting the next.
- **Keep old paths as symlinks temporarily:** So nothing breaks during transition
- **Test automations after each phase:** Morning brief, journal gen, kanban, search API
- **Don't rush:** This is a 3-4 week project, not a weekend hack

---

## What NOT to Move

These should stay where they are:

- `~/.openclaw/` (OpenClaw config directory) - this is the standard location
- `node_modules/` - reinstall, don't move
- `.git/` - fresh history after migration
- Any `.env` files with secrets - recreate, don't copy

---

_This plan was created based on Arvind's directive on February 8, 2026. Execute only with architect approval._
