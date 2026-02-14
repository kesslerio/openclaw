# Memex HISTORIAN - System Architecture

## System Overview

```
┌───────────────────────────────────────────────────────────────────┐
│                         USER LAYER                                │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Memex Skill │  │  curl/HTTP  │  │   Python    │              │
│  │  (Claude)   │  │  Commands   │  │   Scripts   │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                 │                      │
│         └────────────────┴─────────────────┘                      │
│                          │                                        │
│                          │ HTTP GET/POST                          │
│                          │ localhost:8765                         │
└──────────────────────────┼────────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                                  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │            macOS LaunchAgent                               │  │
│  │  com.copperdigital.memex-api                              │  │
│  │                                                            │  │
│  │  - Auto-start on login                                    │  │
│  │  - Auto-restart on crash                                  │  │
│  │  - Throttled restarts (10s interval)                      │  │
│  │  - Logging to ~/Library/Logs/                             │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                       │
│                           │ Runs                                  │
│                           ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │           FastAPI Application                             │  │
│  │  (memex/historian/search_api.py)                         │  │
│  │                                                            │  │
│  │  Endpoints:                                               │  │
│  │  ┌──────────────────────────────────────────────┐        │  │
│  │  │ GET /                                         │        │  │
│  │  │   Health check, returns status + index count │        │  │
│  │  │                                               │        │  │
│  │  │ GET /search?q=QUERY&limit=N&speaker=NAME     │        │  │
│  │  │   Semantic search with filters                │        │  │
│  │  │   Returns: query, results[], total           │        │  │
│  │  │                                               │        │  │
│  │  │ GET /stats                                    │        │  │
│  │  │   Index statistics                            │        │  │
│  │  └──────────────────────────────────────────────┘        │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                       │
└───────────────────────────┼───────────────────────────────────────┘
                            │
                            │ Vector Operations
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              EmbeddingsManager                            │  │
│  │  (memex/historian/embeddings.py)                         │  │
│  │                                                            │  │
│  │  Model: all-MiniLM-L6-v2                                 │  │
│  │  Type: sentence-transformers (local)                     │  │
│  │  Dimensions: 384                                          │  │
│  │  Cost: FREE (no API calls)                               │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                       │
│                           │ Generates embeddings                  │
│                           ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              ChromaDB Vector Store                        │  │
│  │  (memex/historian/vector_store.py)                       │  │
│  │                                                            │  │
│  │  Location: ~/Cursor/Claude-2026/openclaw/skills/memex/data/chroma/                    │  │
│  │  Collection: plaud_transcripts                            │  │
│  │                                                            │  │
│  │  Storage:                                                 │  │
│  │  ┌──────────────────────────────────────────────┐        │  │
│  │  │ Documents (text chunks)                      │        │  │
│  │  │ Embeddings (384-dim vectors)                 │        │  │
│  │  │ Metadata:                                     │        │  │
│  │  │   - speaker                                   │        │  │
│  │  │   - date                                      │        │  │
│  │  │   - title                                     │        │  │
│  │  │   - transcript_id                             │        │  │
│  │  │   - duration                                  │        │  │
│  │  │   - source_file                               │        │  │
│  │  │   - chunk_index                               │        │  │
│  │  └──────────────────────────────────────────────┘        │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Indexing Flow (Setup)

```
┌─────────────────┐
│  Raw Transcript │
│  (JSON file)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Processor  │ Split into chunks (500 chars, 50 overlap)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Embeddings      │ Generate 384-dim vectors (local model)
│ Manager         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ChromaDB Store  │ Store: text + embedding + metadata
└─────────────────┘
```

### 2. Search Flow (Runtime)

```
┌─────────────────┐
│ User Query      │ "patient care protocols"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Embeddings      │ Convert query to 384-dim vector
│ Manager         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ChromaDB Search │ Find similar vectors (L2 distance)
│                 │ Apply metadata filters (speaker, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Recency Ranker  │ Combine similarity (70%) + recency (30%)
│                 │ Apply decay (5%/day)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Formatted       │ Return JSON with results, scores, metadata
│ Response        │
└─────────────────┘
```

## Components

### 1. Service Management

| Component      | Location                                                   | Purpose                            |
| -------------- | ---------------------------------------------------------- | ---------------------------------- |
| LaunchAgent    | `~/Library/LaunchAgents/com.copperdigital.memex-api.plist` | Auto-start, restart on crash       |
| Start Script   | `scripts/start_api.sh`                                     | Launch API server with correct env |
| Install Script | `scripts/install_service.sh`                               | Set up LaunchAgent                 |
| Status Script  | `scripts/status_api.sh`                                    | Check if service is running        |

### 2. API Server

| Component   | Location                  | Purpose                       |
| ----------- | ------------------------- | ----------------------------- |
| FastAPI App | `historian/search_api.py` | HTTP API server               |
| Config      | `historian/config.py`     | Settings (port, limits, etc.) |
| Routes      | `/`, `/search`, `/stats`  | Endpoints                     |

### 3. Search Engine

| Component      | Location                      | Purpose                    |
| -------------- | ----------------------------- | -------------------------- |
| Vector Store   | `historian/vector_store.py`   | ChromaDB interface         |
| Embeddings     | `historian/embeddings.py`     | Local embedding generation |
| Text Processor | `historian/text_processor.py` | Chunking, cleaning         |
| Recency Ranker | `historian/recency_ranker.py` | Time-aware scoring         |

### 4. Data Storage

| Component   | Location            | Purpose                    |
| ----------- | ------------------- | -------------------------- |
| ChromaDB    | `data/chroma/`      | Vector database files      |
| Transcripts | `data/transcripts/` | Original JSON files        |
| Audio       | `data/audio/`       | Original audio (if stored) |

## Configuration

### API Settings (`historian/config.py`)

```python
API_HOST = "0.0.0.0"        # Listen on all interfaces
API_PORT = 8765              # Port number
DEFAULT_RESULTS = 10         # Default search results

## Context Grid + Trails

Memex now attaches a **context grid** to Universal Briefing ingests. The grid
acts as a coordinate system for time/people/platform/channel, mirroring
hippocampal place cues. Associative trails are stored under `memex/data/trails/`
for replayable memory paths.
MAX_RESULTS = 50             # Maximum search results
```

### Embedding Settings

```python
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Local model
EMBEDDING_DIMENSIONS = 384             # Vector size
CHUNK_SIZE = 500                       # Chars per chunk
CHUNK_OVERLAP = 50                     # Overlap chars
```

### Ranking Settings

```python
SIMILARITY_WEIGHT = 0.7   # 70% semantic similarity
RECENCY_WEIGHT = 0.3      # 30% recency
DECAY_RATE = 0.05         # 5% decay per day
```

## Logging

```
~/Library/Logs/
├── memex-api.log         # Standard output
└── memex-api-error.log   # Error output
```

Logs include:

- API startup/shutdown
- Request logs (query, limit, speaker)
- Response times
- Errors and stack traces
- Index operations

## Security Model

| Aspect             | Implementation                         |
| ------------------ | -------------------------------------- |
| **Network**        | Localhost only (0.0.0.0 with firewall) |
| **Authentication** | None (local use only)                  |
| **Authorization**  | None (all data accessible)             |
| **CORS**           | Enabled for local development          |
| **Data Privacy**   | Logs may contain transcript snippets   |

**Warning**: Do not expose to internet without adding authentication.

## Performance

| Metric                  | Typical Value    | Notes                  |
| ----------------------- | ---------------- | ---------------------- |
| **Startup Time**        | 2-5 seconds      | Loads ChromaDB index   |
| **Search Latency**      | <100ms           | For <10k chunks        |
| **Memory Usage**        | 200-500MB        | Varies with index size |
| **Embedding Speed**     | ~1000 tokens/sec | Local CPU-based        |
| **Concurrent Requests** | 10+              | FastAPI async handling |

## Scaling Considerations

| Size   | Chunks   | Memory | Search Time | Notes                 |
| ------ | -------- | ------ | ----------- | --------------------- |
| Small  | <1k      | ~100MB | <50ms       | Fast, in-memory       |
| Medium | 1k-10k   | ~500MB | <100ms      | Good performance      |
| Large  | 10k-100k | ~2GB   | <500ms      | May need optimization |
| XLarge | >100k    | >5GB   | >1s         | Consider sharding     |

## Integration Patterns

### 1. Direct HTTP

```bash
curl "http://localhost:8765/search?q=QUERY&limit=10"
```

### 2. Python Client

```python
import requests
client = requests.Session()
response = client.get("http://localhost:8765/search", params={"q": "test"})
```

### 3. Async Python

```python
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get("http://localhost:8765/search?q=test") as resp:
        data = await resp.json()
```

### 4. Memex Skill

```python
# Skill integration
@skill_command("search")
def search_transcripts(query: str):
    response = requests.get(f"{API_URL}/search", params={"q": query})
    return format_results(response.json())
```

## Failure Modes

| Failure             | Cause                     | Solution                     |
| ------------------- | ------------------------- | ---------------------------- |
| Service won't start | Missing dependencies      | `poetry install`             |
| Port in use         | Another process on 8765   | Change port or kill process  |
| No results          | Empty index               | Run transcript indexer       |
| Slow searches       | Large index               | Add indexes, reduce limit    |
| High memory         | Too many chunks in memory | Restart service periodically |

## Monitoring

### Health Check

```bash
curl http://localhost:8765/ | jq .
```

### Index Stats

```bash
curl http://localhost:8765/stats | jq .
```

### Service Status

```bash
launchctl list | grep memex-api
```

### Logs

```bash
tail -f ~/Library/Logs/memex-api.log
```

## Backup & Recovery

### Backup ChromaDB

```bash
tar -czf memex-backup-$(date +%Y%m%d).tar.gz ~/Cursor/Claude-2026/openclaw/skills/memex/data/chroma/
```

### Restore ChromaDB

```bash
tar -xzf memex-backup-20240115.tar.gz -C ~/Cursor/Claude-2026/openclaw/skills/memex/data/
```

### Re-index from Transcripts

```bash
cd ~/Cursor/Claude-2026/openclaw/skills/memex
poetry run python -m memex.historian.transcript_indexer
```

## Development

### Run in Development Mode

```bash
cd ~/Cursor/Claude-2026/openclaw/skills/memex
poetry run python -m memex.historian.search_api
```

### Enable Hot Reload

```python
# In config.py
API_RELOAD = True
```

### Run Tests

```bash
cd ~/Cursor/Claude-2026/openclaw/skills/memex
poetry run pytest tests/
```

## Production Deployment

For production use:

1. Disable auto-reload: `API_RELOAD = False`
2. Add authentication middleware
3. Set up reverse proxy (nginx)
4. Add rate limiting
5. Enable HTTPS
6. Set up monitoring/alerts
7. Schedule regular backups

## Related Documentation

- **SETUP_SUMMARY.md** - Complete setup guide
- **QUICKSTART.md** - Fast installation
- **API_SERVICE.md** - API documentation
- **SKILL_INTEGRATION.md** - Integration examples
