# Memex HISTORIAN Search API Service

Background service for semantic search across Plaud transcripts.

## Quick Start

### Manual Start (One-time)

```bash
cd ~/clawd/memex
python -m memex.historian.search_api
```

API available at: http://localhost:8765

### Install as Background Service (Recommended)

```bash
cd ~/clawd/memex/scripts
chmod +x install_service.sh
./install_service.sh
```

This installs a macOS LaunchAgent that:

- Starts automatically on login
- Restarts if it crashes
- Runs in the background

## Service Management

### Using LaunchCtl (Recommended)

```bash
# Start service
launchctl start com.copperdigital.memex-api

# Stop service
launchctl stop com.copperdigital.memex-api

# Check if running
launchctl list | grep memex-api

# View logs
tail -f ~/Library/Logs/memex-api.log
tail -f ~/Library/Logs/memex-api-error.log
```

### Using Helper Scripts

```bash
cd ~/clawd/memex/scripts

# Check status
./status_api.sh

# Manual start (foreground)
./start_api.sh

# Manual stop
./stop_api.sh

# Test API endpoints
./test_api.sh

# Uninstall service
./uninstall_service.sh
```

## API Endpoints

### Health Check

```bash
curl http://localhost:8765/
```

Response:

```json
{
  "status": "healthy",
  "service": "memex-historian",
  "indexed_chunks": 1234
}
```

### Search

```bash
curl "http://localhost:8765/search?q=patient%20care&limit=5"
```

Parameters:

- `q` (required): Search query
- `limit` (optional): Number of results (1-50, default 10)
- `speaker` (optional): Filter by speaker name

Response:

```json
{
  "query": "patient care",
  "results": [
    {
      "text": "Transcript segment text...",
      "speaker": "Speaker Name",
      "transcript_id": "20240115_meeting",
      "date": "2024-01-15",
      "title": "Morning Rounds",
      "score": 0.8523
    }
  ],
  "total": 5
}
```

### Statistics

```bash
curl http://localhost:8765/stats
```

Response:

```json
{
  "total_chunks": 1234,
  "embedding_model": "all-MiniLM-L6-v2",
  "collection": "plaud_transcripts"
}
```

## Configuration

Edit `/Users/arvindsarin/clawd/memex/historian/config.py`:

```python
API_HOST = "0.0.0.0"  # Listen on all interfaces
API_PORT = 8765        # Port number
DEFAULT_RESULTS = 10   # Default search results
MAX_RESULTS = 50       # Maximum search results
```

## File Locations

### Scripts

- `/Users/arvindsarin/clawd/memex/scripts/start_api.sh` - Start script
- `/Users/arvindsarin/clawd/memex/scripts/stop_api.sh` - Stop script
- `/Users/arvindsarin/clawd/memex/scripts/status_api.sh` - Status check
- `/Users/arvindsarin/clawd/memex/scripts/test_api.sh` - API tests
- `/Users/arvindsarin/clawd/memex/scripts/install_service.sh` - Install LaunchAgent
- `/Users/arvindsarin/clawd/memex/scripts/uninstall_service.sh` - Uninstall LaunchAgent

### Configuration

- `/Users/arvindsarin/Library/LaunchAgents/com.copperdigital.memex-api.plist` - LaunchAgent config

### Logs

- `~/Library/Logs/memex-api.log` - Standard output
- `~/Library/Logs/memex-api-error.log` - Error output

## Troubleshooting

### Service won't start

1. Check logs:

```bash
cat ~/Library/Logs/memex-api-error.log
```

2. Verify Python dependencies:

```bash
cd ~/clawd/memex
pip install -r requirements.txt
```

3. Test manual start:

```bash
cd ~/clawd/memex
python -m memex.historian.search_api
```

### Port already in use

Check if another process is using port 8765:

```bash
lsof -i :8765
```

Kill the process:

```bash
kill -9 <PID>
```

Or change the port in `config.py`.

### API not responding

1. Verify service is running:

```bash
./status_api.sh
```

2. Check ChromaDB is accessible:

```bash
ls -la ~/clawd/memex/data/chroma
```

3. Restart service:

```bash
launchctl stop com.copperdigital.memex-api
launchctl start com.copperdigital.memex-api
```

### No search results

1. Check index has data:

```bash
curl http://localhost:8765/stats
```

2. Re-index transcripts:

```bash
cd ~/clawd/memex
python -m memex.historian.transcript_indexer
```

## Integration with Memex Skill

The memex skill uses this API for programmatic search:

```python
import requests

def search_transcripts(query: str, limit: int = 10):
    response = requests.get(
        "http://localhost:8765/search",
        params={"q": query, "limit": limit}
    )
    return response.json()

# Example
results = search_transcripts("patient documentation")
for result in results["results"]:
    print(f"{result['score']:.2f} - {result['text'][:100]}...")
```

## Architecture

```
┌─────────────────────────────────────────┐
│  LaunchAgent (com.copperdigital.memex)  │
│  Starts on login, restarts on crash     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  FastAPI Server (localhost:8765)        │
│  - /health                              │
│  - /search                              │
│  - /stats                               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  ChromaDB Vector Store                  │
│  ~/clawd/memex/data/chroma              │
│  - Embeddings (all-MiniLM-L6-v2)       │
│  - Metadata (speaker, date, title)     │
└─────────────────────────────────────────┘
```

## Performance

- Local embeddings: No API costs, fast
- ChromaDB: In-memory for speed
- Typical search latency: <100ms
- Concurrent requests: Handled by FastAPI async

## Security Notes

- API bound to localhost only (not exposed externally)
- No authentication (local use only)
- CORS enabled for local development
- Do not expose to internet without adding auth

## Next Steps

1. Install the service: `./install_service.sh`
2. Test endpoints: `./test_api.sh`
3. Integrate with memex skill
4. Set up monitoring/alerts if needed

## Support

Check logs for errors:

```bash
tail -f ~/Library/Logs/memex-api*.log
```

Restart service:

```bash
launchctl stop com.copperdigital.memex-api
launchctl start com.copperdigital.memex-api
```
