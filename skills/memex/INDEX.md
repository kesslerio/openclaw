# Memex HISTORIAN Search API - File Index

Complete reference for all files created for the background service setup.

## Quick Navigation

| Document                 | Purpose                    | Audience        |
| ------------------------ | -------------------------- | --------------- |
| **README_API.md**        | Start here - main overview | Everyone        |
| **QUICKSTART.md**        | Fast installation guide    | New users       |
| **API_SERVICE.md**       | Complete API reference     | Developers      |
| **SKILL_INTEGRATION.md** | Python integration guide   | Developers      |
| **ARCHITECTURE.md**      | System design details      | Technical users |
| **SETUP_SUMMARY.md**     | Complete setup reference   | Everyone        |

## Documentation Files

### User Documentation

- **README_API.md** - Main overview and quick reference
- **QUICKSTART.md** - Fast installation and setup (5 minutes)
- **SETUP_SUMMARY.md** - Complete setup summary with troubleshooting

### Technical Documentation

- **API_SERVICE.md** - Complete API documentation with all endpoints
- **SKILL_INTEGRATION.md** - Python client examples and patterns
- **ARCHITECTURE.md** - System architecture and data flow

## Service Files

### LaunchAgent (macOS)

- **~/Library/LaunchAgents/com.copperdigital.memex-api.plist**
  - macOS service configuration
  - Auto-start on login
  - Auto-restart on crash
  - Log routing

### Systemd (Linux)

- **scripts/memex-api.service**
  - Linux systemd service file
  - Install to `/etc/systemd/system/` or `~/.config/systemd/user/`

## Scripts

All scripts located in `/Users/arvindsarin/clawd/memex/scripts/`

### Service Management

- **install_service.sh** - Install LaunchAgent (one-time setup)
- **uninstall_service.sh** - Remove LaunchAgent
- **start_api.sh** - Start API server (manual or via LaunchAgent)
- **stop_api.sh** - Stop API server
- **status_api.sh** - Check if service is running

### Testing

- **test_api.sh** - Test API endpoints (bash version)
- **test_api.py** - Test API endpoints (Python version)

## Build Tools

- **Makefile** - Convenient make commands
  ```bash
  make install    # Install service
  make start      # Start service
  make stop       # Stop service
  make restart    # Restart service
  make status     # Check status
  make test       # Run tests
  make logs       # View logs
  make clean      # Clean logs
  make uninstall  # Remove service
  ```

## Source Code

Located in `/Users/arvindsarin/clawd/memex/historian/`

### Core API

- **search_api.py** - FastAPI application
  - Health check endpoint: `GET /`
  - Search endpoint: `GET /search`
  - Stats endpoint: `GET /stats`

### Supporting Modules

- **config.py** - Configuration settings
- **vector_store.py** - ChromaDB interface
- **embeddings.py** - Local embedding generation
- **text_processor.py** - Text chunking and cleaning
- **recency_ranker.py** - Time-aware ranking

## Configuration

- **historian/config.py** - Main configuration
  ```python
  API_HOST = "0.0.0.0"
  API_PORT = 8765
  DEFAULT_RESULTS = 10
  MAX_RESULTS = 50
  EMBEDDING_MODEL = "all-MiniLM-L6-v2"
  ```

## Logs

- **~/Library/Logs/memex-api.log** - Standard output
- **~/Library/Logs/memex-api-error.log** - Error output

## Data Files

- **data/chroma/** - ChromaDB vector store
- **data/transcripts/** - Original transcript JSON files
- **data/audio/** - Original audio files (optional)

## Installation Flow

```
1. QUICKSTART.md
   └─> Install dependencies (poetry install)
   └─> Run install script (make install)
   └─> Verify status (make status)
   └─> Test API (make test)

2. For integration:
   └─> SKILL_INTEGRATION.md
       └─> Python client examples
       └─> Error handling patterns
       └─> Caching strategies

3. For troubleshooting:
   └─> SETUP_SUMMARY.md
       └─> Common issues
       └─> Solutions
       └─> Logs location
```

## Use Cases by Role

### End User

1. Read: **README_API.md**
2. Install: **QUICKSTART.md**
3. Troubleshoot: **SETUP_SUMMARY.md**

### Developer (Skill Integration)

1. Overview: **README_API.md**
2. Integration: **SKILL_INTEGRATION.md**
3. API Reference: **API_SERVICE.md**

### System Administrator

1. Architecture: **ARCHITECTURE.md**
2. Setup: **SETUP_SUMMARY.md**
3. Service Config: **com.copperdigital.memex-api.plist**

## Command Reference

### Service Commands

```bash
# Install
make install
./scripts/install_service.sh

# Start
make start
launchctl start com.copperdigital.memex-api

# Stop
make stop
launchctl stop com.copperdigital.memex-api

# Status
make status
./scripts/status_api.sh
launchctl list | grep memex-api

# Logs
make logs
tail -f ~/Library/Logs/memex-api.log

# Test
make test
python scripts/test_api.py
./scripts/test_api.sh

# Uninstall
make uninstall
./scripts/uninstall_service.sh
```

### API Commands

```bash
# Health
curl http://localhost:8765/

# Search
curl "http://localhost:8765/search?q=test&limit=5"

# Stats
curl http://localhost:8765/stats
```

## File Permissions

All scripts should be executable:

```bash
chmod +x scripts/*.sh
```

Verify:

```bash
ls -lh scripts/
```

## Dependencies

Managed via Poetry (`pyproject.toml`):

- fastapi
- uvicorn
- chromadb
- sentence-transformers
- pydantic
- python-dotenv

Install:

```bash
cd ~/clawd/memex
poetry install
```

## Environment Variables

Optional environment variables:

```bash
export MEMEX_API_URL="http://localhost:8765"
export PYTHONPATH="/Users/arvindsarin/clawd/memex"
```

## Backup Files

Important files to backup:

- `data/chroma/` - Vector database
- `data/transcripts/` - Original transcripts
- `historian/config.py` - Custom configuration
- `~/Library/LaunchAgents/com.copperdigital.memex-api.plist` - Service config

Backup command:

```bash
tar -czf memex-backup-$(date +%Y%m%d).tar.gz \
    data/chroma/ \
    data/transcripts/ \
    historian/config.py
```

## Version Control

Files tracked in git:

- All documentation (\*.md)
- All scripts (scripts/\*.sh)
- Source code (historian/\*.py)
- Makefile
- pyproject.toml

Files excluded (.gitignore):

- data/chroma/ (large, can rebuild)
- data/transcripts/ (private)
- \*.log (ephemeral)

## Documentation Updates

When making changes:

1. Update relevant .md file
2. Update SETUP_SUMMARY.md if setup changes
3. Update this INDEX.md if new files added
4. Test changes with `make test`

## Support Resources

| Issue                  | Resource                           |
| ---------------------- | ---------------------------------- |
| Installation problems  | QUICKSTART.md                      |
| API not responding     | SETUP_SUMMARY.md → Troubleshooting |
| Integration questions  | SKILL_INTEGRATION.md               |
| Architecture questions | ARCHITECTURE.md                    |
| Endpoint documentation | API_SERVICE.md                     |

## Next Steps

After installation:

1. Index transcripts: `python -m memex.historian.transcript_indexer`
2. Test search: `make test`
3. Integrate with memex skill: See SKILL_INTEGRATION.md
4. Set up monitoring: Check logs regularly
5. Schedule backups: Backup data/chroma/ weekly

## Summary

This index provides a complete reference to all files created for the Memex HISTORIAN Search API background service. Start with README_API.md for an overview, then use QUICKSTART.md for installation.
