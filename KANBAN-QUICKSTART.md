# 🎯 Kanban Mission Control - Quick Start

## Access URLs

**Local**: http://localhost:8888
**iPad/Mobile**: http://100.99.190.40:8888

## Quick Commands

### Server Management

```bash
# Check if running
lsof -ti:8888

# View logs
tail -f ~/Cursor/Claude-2026/openclaw/clawd/logs/server.log

# Restart
lsof -ti:8888 | xargs kill -9
cd ~/Cursor/Claude-2026/openclaw/clawd/server && nohup node server.js > ../logs/server.log 2>&1 &
```

### CLI Usage

```bash
cd ~/Cursor/Claude-2026/openclaw

# Add task
node scripts/update-kanban.cjs add "Fix bug" --priority high --category Work

# Move task
node scripts/update-kanban.cjs move task-123 doing

# List all
node scripts/update-kanban.cjs list
```

## Mission Control Metrics

- 🟢 **Gateway**: OpenClaw health (port 18789)
- 💰 **Tokens**: Daily AI cost tracking
- ⚡ **Sprint**: Active tasks, todo count, completed today
- 🎯 **Focus**: Highest priority task

## Tips

- Auto-refresh every 30 seconds
- Drag & drop between columns
- Use filters to focus on priorities
- Quick move buttons on each card
- Add to iPad Home Screen for app-like experience

## Data Location

`~/Cursor/Claude-2026/openclaw/clawd/data/kanban.json`
