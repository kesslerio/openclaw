# Memex Architecture Decision: Integration Strategy

## Current State Analysis

### What's Already in OpenClaw

```
OpenClaw Infrastructure:
├── Job Scheduler (jobs.json)
│   ├── memex-sync (6 PM)
│   ├── memex-daily-ingest (7 AM)
│   └── memex-build-journal (9 PM)
├── Scripts (~/.openclaw/scripts/)
│   ├── memex-sync.sh
│   ├── memex-daily-ingest.sh
│   ├── memex-build-journal.sh
│   └── start-memex-api.sh
├── Authentication
│   └── Nike agent with Anthropic OAuth
├── Notifications
│   └── Telegram integration
└── Logging
    └── ~/.openclaw/logs/
```

### What's Standalone

```
Memex Codebase:
├── ~/Cursor/Claude-2026/clawd/memex/
│   ├── scripts/ (Python scripts)
│   ├── journalist/ (journal generator)
│   ├── retrieval/ (query engine)
│   ├── integrations/ (Gmail, Calendar)
│   └── data/ (emails, journals, ChromaDB)
└── Requires: ANTHROPIC_API_KEY
```

---

## Three Options Evaluated

### Option 1: API Key (Current Approach)

**Keep Memex standalone, add API key**

**Pros:**

- ✅ Clean separation of concerns
- ✅ Memex can run independently
- ✅ Easy to debug and test
- ✅ No coupling to OpenClaw

**Cons:**

- ❌ Duplicate authentication (OpenClaw + Memex)
- ❌ User needs to manage API key
- ❌ Two separate systems to maintain

**Effort:** 2 minutes (just add API key)

---

### Option 2: Wrapper/Proxy

**Create a wrapper that routes Memex through OpenClaw's auth**

**Implementation:**

```python
# memex/config/openclaw_client.py
import subprocess
import json

class OpenClawClient:
    """Routes Claude API calls through OpenClaw Nike agent"""

    def messages_create(self, model, max_tokens, messages):
        # Call OpenClaw agent with the prompt
        cmd = [
            'openclaw', 'agent', 'nike',
            '--prompt', json.dumps(messages),
            '--model', model,
            '--max-tokens', str(max_tokens)
        ]
        result = subprocess.run(cmd, capture_output=True)
        return parse_response(result.stdout)
```

**Pros:**

- ✅ Uses existing OpenClaw auth
- ✅ No API key needed
- ✅ Minimal code changes

**Cons:**

- ❌ Adds indirection/complexity
- ❌ Slower (subprocess overhead)
- ❌ Depends on OpenClaw being running
- ❌ Harder to debug
- ❌ Error handling complexity
- ❌ Not a clean abstraction

**Effort:** 4-6 hours (write wrapper, test, handle edge cases)

---

### Option 3: Full Integration (RECOMMENDED)

**Move Memex into OpenClaw as a native skill**

**Implementation:**

```
~/.openclaw/skills/memex/
├── skill.yaml (metadata)
├── scripts/
│   ├── journal_backfill.py
│   ├── daily_ingest.py
│   └── query_memex.py
├── lib/
│   ├── journalist/
│   ├── retrieval/
│   └── integrations/
└── data/ → ~/clawd/memex/data (symlink)
```

**How it works:**

1. Memex becomes an OpenClaw skill (like usage-dashboard)
2. Uses OpenClaw's Nike agent authentication automatically
3. Jobs already registered in jobs.json
4. Logs to OpenClaw's logging system
5. Telegram notifications work out of the box

**Pros:**

- ✅ **Uses existing authentication** (no API key needed)
- ✅ **Native integration** with OpenClaw infrastructure
- ✅ **Shared logging, notifications, job scheduling**
- ✅ **Single system to maintain**
- ✅ **Can call from OpenClaw CLI**: `openclaw memex query "what meetings?"`
- ✅ **Better architecture** - Memex is a memory service, fits OpenClaw's purpose
- ✅ **Data stays in same location** (just symlinks)
- ✅ **Cron jobs already configured** in OpenClaw

**Cons:**

- ⚠️ Memex can't run without OpenClaw (acceptable trade-off)
- ⚠️ More initial refactoring (but cleaner long-term)

**Effort:** 2-3 hours (restructure as skill, update imports)

---

## Recommendation: Option 3 (Full Integration)

### Why This Is The Right Choice

**1. Architectural Fit**

- OpenClaw = Personal AI system
- Memex = Memory layer for that system
- They SHOULD be integrated, not separate

**2. Already Partially Integrated**

- Jobs in OpenClaw's jobs.json
- Scripts in OpenClaw's scripts/
- Uses OpenClaw's Telegram notifications
- **Memex is already trying to BE part of OpenClaw**

**3. Authentication Problem Solved**

- OpenClaw skill can use agent's authentication
- No separate API key management
- Works with existing OAuth token

**4. Better UX**

```bash
# Current (broken):
cd ~/Cursor/Claude-2026/clawd/memex
export ANTHROPIC_API_KEY=...
./scripts/journal_backfill.py

# After integration:
openclaw memex backfill
openclaw memex query "summarize last week"
```

**5. Follows OpenClaw Patterns**

- `usage-dashboard` is already a skill
- Morning brief already uses skill pattern
- Memex should follow same structure

---

## Implementation Plan

### Phase 1: Skill Structure (30 min)

```bash
# Create skill directory
mkdir -p ~/.openclaw/skills/memex/{scripts,lib}

# Move code
mv ~/Cursor/Claude-2026/clawd/memex/journalist ~/.openclaw/skills/memex/lib/
mv ~/Cursor/Claude-2026/clawd/memex/retrieval ~/.openclaw/skills/memex/lib/
mv ~/Cursor/Claude-2026/clawd/memex/integrations ~/.openclaw/skills/memex/lib/
mv ~/Cursor/Claude-2026/clawd/memex/scripts/*.py ~/.openclaw/skills/memex/scripts/

# Symlink data (keep in original location)
ln -s ~/clawd/memex/data ~/.openclaw/skills/memex/data
```

### Phase 2: skill.yaml (15 min)

```yaml
---
name: memex
description: Personal memory system with email, calendar, and journal generation
version: 2.0.0

commands:
  backfill:
    description: Generate journals for historical data
    script: scripts/journal_backfill.py

  query:
    description: Search your memory
    script: scripts/query_memex.py

  daily-ingest:
    description: Sync emails and calendar
    script: scripts/daily_ingest.py

dependencies:
  - anthropic
  - chromadb
  - pydantic<2.0

authentication:
  provider: anthropic
  source: agent # Use Nike agent's auth
```

### Phase 3: Update Scripts (1 hour)

```python
# In each script, replace:
from config.model_enforcer import ModelEnforcer
client = ModelEnforcer.get_client()

# With:
from openclaw.auth import get_agent_client
client = get_agent_client('nike', provider='anthropic')
```

### Phase 4: Update jobs.json (5 min)

```json
{
  "id": "memex-daily-ingest",
  "command": "openclaw skill memex daily-ingest",
  "script": "~/.openclaw/skills/memex/scripts/daily_ingest.py"
}
```

### Phase 5: Test (30 min)

```bash
openclaw skill memex backfill --max 1
openclaw skill memex query "meetings last week"
```

---

## Migration Checklist

- [ ] Create skill directory structure
- [ ] Move Python modules to lib/
- [ ] Move scripts to scripts/
- [ ] Create skill.yaml
- [ ] Update imports to use OpenClaw auth
- [ ] Update jobs.json to use skill commands
- [ ] Symlink data directory
- [ ] Test journal generation
- [ ] Test query engine
- [ ] Update cron jobs
- [ ] Document new usage

---

## Alternative: Quick Fix (If You Need It NOW)

If you need journals TODAY:

1. **Go to**: https://console.anthropic.com/settings/keys
2. **Click**: "Create Key"
3. **Copy key** (starts with `sk-ant-api03-`)
4. **Update**:
   ```bash
   nano ~/Cursor/Claude-2026/clawd/memex/.env
   # Replace the oat01 token with api03 key
   ```
5. **Test**:
   ```bash
   cd ~/Cursor/Claude-2026/clawd/memex
   ./scripts/journal_backfill.py --max 1
   ```

Takes 2 minutes. Then migrate to Option 3 later.

---

## Decision

**Recommended:** Option 3 (Full Integration)

**Timeline:**

- Quick fix now: 2 minutes (API key)
- Full integration: This week (2-3 hours)

**Rationale:**

- Memex BELONGS in OpenClaw architecturally
- Solves auth problem permanently
- Better UX and maintainability
- Already 60% integrated anyway

---

## Next Steps

**Your call:**

1. **Do it right now**: Full integration (2-3 hours, permanent solution)
2. **Quick fix first**: API key (2 min), integrate later
3. **Build wrapper**: Temporary solution (4-6 hours, not recommended)

What do you want to do?
