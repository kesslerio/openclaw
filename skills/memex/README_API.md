# Memex HISTORIAN Search API

Background service for semantic search across Plaud transcripts. Enables programmatic access for the memex skill and other tools.

## Overview

This API provides:

- Semantic search across indexed transcripts
- Speaker-based filtering
- Recency-aware ranking
- Fast local embeddings (no API costs)
- Auto-restart background service
- Simple HTTP interface

## Installation

```bash
# 1. Install dependencies
cd ~/clawd/memex
poetry install

# 2. Install as background service
make install

# 3. Verify it's running
make status
```

That's it! The API is now running at `http://localhost:8765`

## Quick Test

```bash
# Health check
curl http://localhost:8765/

# Search
curl "http://localhost:8765/search?q=patient%20care&limit=5"

# Stats
curl http://localhost:8765/stats
```

## Commands

```bash
make install    # Install service (one-time)
make start      # Start service
make stop       # Stop service
make restart    # Restart service
make status     # Check status
make test       # Run tests
make logs       # View logs
make uninstall  # Remove service
```

## API Endpoints

### GET /

Health check and status

**Request:**

```bash
curl http://localhost:8765/
```

**Response:**

```json
{
  "status": "healthy",
  "service": "memex-historian",
  "indexed_chunks": 1234
}
```

### GET /search

Semantic search with optional filters

**Request:**

```bash
curl "http://localhost:8765/search?q=patient%20care&limit=5&speaker=Dr.%20Smith"
```

**Parameters:**

- `q` (required): Search query (natural language)
- `limit` (optional): Number of results (1-50, default 10)
- `speaker` (optional): Filter by speaker name

**Response:**

```json
{
  "query": "patient care",
  "results": [
    {
      "text": "We discussed patient care protocols...",
      "speaker": "Dr. Smith",
      "transcript_id": "20240115_meeting",
      "date": "2024-01-15",
      "title": "Morning Rounds",
      "score": 0.8523
    }
  ],
  "total": 5
}
```

### GET /stats

Index statistics

**Request:**

```bash
curl http://localhost:8765/stats
```

**Response:**

```json
{
  "total_chunks": 1234,
  "embedding_model": "all-MiniLM-L6-v2",
  "collection": "plaud_transcripts"
}
```

## Python Integration

```python
import requests

class MemexClient:
    def __init__(self, base_url="http://localhost:8765"):
        self.base_url = base_url

    def search(self, query, limit=10):
        response = requests.get(
            f"{self.base_url}/search",
            params={"q": query, "limit": limit}
        )
        return response.json()

# Usage
client = MemexClient()
results = client.search("patient documentation", limit=5)

for r in results['results']:
    print(f"{r['score']:.2f} - {r['text'][:100]}...")
```

## Documentation

| File                     | Description                 |
| ------------------------ | --------------------------- |
| **QUICKSTART.md**        | Fast setup guide            |
| **API_SERVICE.md**       | Complete API documentation  |
| **SKILL_INTEGRATION.md** | Python integration examples |
| **ARCHITECTURE.md**      | System architecture details |
| **SETUP_SUMMARY.md**     | Setup summary and reference |

## Troubleshooting

### Service won't start

```bash
# Check logs
cat ~/Library/Logs/memex-api-error.log

# Install dependencies
cd ~/clawd/memex
poetry install

# Try manual start
poetry run python -m memex.historian.search_api
```

### No search results

```bash
# Index transcripts first
cd ~/clawd/memex
poetry run python -m memex.historian.transcript_indexer
```

### Port in use

```bash
# Find process
lsof -i :8765

# Kill it
kill -9 <PID>
```

## Configuration

Edit `~/clawd/memex/historian/config.py`:

```python
API_PORT = 8765           # Change port
DEFAULT_RESULTS = 10      # Default result count
MAX_RESULTS = 50          # Maximum results
```

## Files

```
~/clawd/memex/
├── scripts/
│   ├── install_service.sh    # Install LaunchAgent
│   ├── start_api.sh          # Start script
│   ├── stop_api.sh           # Stop script
│   ├── status_api.sh         # Status check
│   ├── test_api.sh           # Test endpoints (bash)
│   └── test_api.py           # Test endpoints (Python)
├── historian/
│   ├── search_api.py         # API server
│   ├── config.py             # Configuration
│   └── ...                   # Other modules
├── Makefile                  # Convenient commands
└── README_API.md             # This file

~/Library/LaunchAgents/
└── com.copperdigital.memex-api.plist  # Service config

~/Library/Logs/
├── memex-api.log             # Standard output
└── memex-api-error.log       # Error output
```

## Features

- **Local & Free**: No API costs, runs entirely locally
- **Fast**: <100ms search latency for typical indexes
- **Auto-start**: Runs on login via LaunchAgent
- **Fault-tolerant**: Auto-restarts on crash
- **Simple**: HTTP REST API, no complex setup
- **Semantic**: Understands meaning, not just keywords
- **Time-aware**: Recency ranking (newer = higher)
- **Filterable**: Search by speaker

## Architecture

```
User/Skill → HTTP API → Vector Store → ChromaDB
                ↓
         Embeddings (local)
```

## Support

1. Check logs: `make logs`
2. Test API: `make test`
3. Restart: `make restart`
4. See docs: `QUICKSTART.md`, `API_SERVICE.md`

## License

Part of Memex HISTORIAN project.
