# Memex Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Set Your API Key (2 minutes)

1. Get your key: https://console.anthropic.com/settings/keys
2. Edit the .env file:
   ```bash
   nano ~/Cursor/Claude-2026/openclaw/skills/memex/.env
   ```
3. Replace `YOUR_KEY_HERE` with your actual key

### Step 2: Verify Setup (1 minute)

```bash
cd ~/Cursor/Claude-2026/openclaw/skills/memex
./scripts/complete_setup.sh
```

You should see: `✅ Ready to use!`

### Step 3: Test Backfill (5 minutes)

```bash
./scripts/journal_backfill.py --max 5
```

This generates 5 sample journals to verify everything works.

---

## 📅 What Runs Automatically

| Time         | What Happens                             |
| ------------ | ---------------------------------------- |
| **7:00 AM**  | Sync emails & calendar, index new data   |
| **9:00 PM**  | Generate yesterday's journal with Claude |
| **On Login** | Start API server on port 8765            |

You'll get Telegram notifications for all operations.

---

## 📁 Where Are My Journals?

```bash
~/Cursor/Claude-2026/openclaw/skills/memex/data/journals/
```

Each journal is named `YYYY-MM-DD.md` with:

- YAML frontmatter (web-ready)
- Daily summary
- Action items
- Key events and conversations

---

## 🔍 Quick Commands

```bash
# Check setup status
cd ~/Cursor/Claude-2026/openclaw/skills/memex
./scripts/complete_setup.sh

# Generate journals for all historical data
./scripts/journal_backfill.py

# Generate journal for specific date
./scripts/daily_ingest.py --journal-only --date 2026-02-01

# Check API server
curl http://localhost:8765/health

# View logs
tail -f ~/.openclaw/logs/memex-*.log
```

---

## 📚 Full Documentation

- **UPGRADE_COMPLETE.md** - Complete migration details
- **AUTOMATION_SETUP_COMPLETE.md** - Automation infrastructure
- **ARCHITECTURE.md** - System architecture
- **NEXT_STEPS.md** - Original setup guide

---

## 💡 Tips

1. **First time?** Run backfill with `--max 5` to test before full run
2. **Check logs** in `~/.openclaw/logs/` if anything fails
3. **Telegram alerts** keep you informed of all operations
4. **Cost**: ~$2-8/month after initial backfill

---

**Need help?** All scripts have `--help` flags:

```bash
./scripts/journal_backfill.py --help
./scripts/daily_ingest.py --help
```
