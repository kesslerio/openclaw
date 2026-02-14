# Memex HISTORIAN API - Quick Start

## 1. Install Dependencies

```bash
cd ~/clawd/memex
poetry install
```

## 2. Install Service

```bash
cd ~/clawd/memex/scripts
./install_service.sh
```

## 3. Verify It's Running

```bash
# Check service status
./status_api.sh

# Or test the API
curl http://localhost:8765/
```

## 4. Test Search

```bash
# Run test suite
python scripts/test_api.py

# Or manual search
curl "http://localhost:8765/search?q=your_query&limit=5"
```

## Common Commands

```bash
# Start service
launchctl start com.copperdigital.memex-api

# Stop service
launchctl stop com.copperdigital.memex-api

# View logs
tail -f ~/Library/Logs/memex-api.log

# Restart service
launchctl stop com.copperdigital.memex-api && launchctl start com.copperdigital.memex-api

# Uninstall
./uninstall_service.sh
```

## API Endpoints

### Health Check

```bash
curl http://localhost:8765/
```

### Search

```bash
curl "http://localhost:8765/search?q=patient%20care&limit=10"
```

### Stats

```bash
curl http://localhost:8765/stats
```

## Troubleshooting

### Service won't start

1. Check dependencies:

```bash
cd ~/clawd/memex
poetry install
```

2. Check logs:

```bash
cat ~/Library/Logs/memex-api-error.log
```

3. Try manual start:

```bash
cd ~/clawd/memex
poetry run python -m memex.historian.search_api
```

### No search results

Index your transcripts first:

```bash
cd ~/clawd/memex
poetry run python -m memex.historian.transcript_indexer
```

### Port already in use

Find what's using port 8765:

```bash
lsof -i :8765
```

Kill it:

```bash
kill -9 <PID>
```

## File Locations

| Item        | Location                                                   |
| ----------- | ---------------------------------------------------------- |
| Scripts     | `~/clawd/memex/scripts/`                                   |
| LaunchAgent | `~/Library/LaunchAgents/com.copperdigital.memex-api.plist` |
| Logs        | `~/Library/Logs/memex-api*.log`                            |
| Data        | `~/clawd/memex/data/`                                      |
| Config      | `~/clawd/memex/historian/config.py`                        |

## Next Steps

- See [API_SERVICE.md](API_SERVICE.md) for full documentation
- Integrate with memex skill for programmatic access
- Set up transcript indexing automation
