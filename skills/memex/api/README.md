# 🔌 Memex API - FastAPI Backend

**REST API connecting React frontend to Memex backend**

---

## Overview

The Memex API provides three main endpoints:

1. **POST /api/chat/query** - Conversational queries (QueryEngine)
2. **GET /api/journals** - Daily journal retrieval (Journalist)
3. **POST /api/search** - Vector search (Historian)

---

## Quick Start

### Installation

```bash
cd /home/ubuntu/clawd/memex/api
pip install -r requirements.txt
```

### Run Server

```bash
# From memex/api directory
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8765
```

Server runs at: `http://localhost:8765`

API docs (Swagger): `http://localhost:8765/docs`

---

## Endpoints

### 1. Health Check

**GET /**

Response:

```json
{
  "name": "Memex API",
  "version": "0.1.0",
  "status": "running",
  "demo_mode": false,
  "endpoints": {...}
}
```

**GET /api/status**

Component health check:

```json
{
  "api": "healthy",
  "demo_mode": false,
  "components": {
    "query_engine": true,
    "memory_search": true,
    "daily_automation": true
  },
  "timestamp": "2026-02-02T02:00:00Z"
}
```

---

### 2. Chat Query

**POST /api/chat/query**

Request:

```json
{
  "query": "What did I promise Mark about the demo?",
  "max_sources": 5,
  "use_history": true
}
```

Response:

```json
{
  "query": "What did I promise Mark about the demo?",
  "answer": "You promised to send the demo materials by Friday...",
  "sources": [
    {
      "date": "2026-01-28",
      "snippet": "In the meeting with Mark, I said...",
      "score": 0.92,
      "metadata": { "speaker": "Arvind" },
      "transcript_path": "transcripts/2026-01-28.txt"
    }
  ],
  "confidence": 0.85,
  "reasoning": "Synthesized from 3 sources (avg score: 0.87)"
}
```

**Features:**

- Intent detection (factual, temporal, commitment, summary)
- Conversation history tracking
- GPT-4o-mini synthesis
- Source attribution
- Confidence scoring

**Integration:** Uses QueryEngine from Phase 4.1

---

### 3. Journals

**GET /api/journals?start_date=2026-01-01&end_date=2026-01-31**

Query Parameters:

- `start_date` (optional): ISO date (YYYY-MM-DD)
- `end_date` (optional): ISO date (YYYY-MM-DD)

Response:

```json
{
  "journals": [
    {
      "date": "2026-01-28",
      "content": "# Daily Journal - January 28, 2026\n\n## Summary\n...",
      "action_items": ["Send demo to Mark by Friday", "Follow up with Darwin"],
      "transcript_count": 5,
      "generated_at": "2026-01-29T08:00:00Z"
    }
  ],
  "count": 1
}
```

**Features:**

- Date range filtering
- Markdown content
- Action item extraction
- Metadata (transcript count, generation time)

**Integration:** Loads from `memex/data/journals/*.md`

---

### 4. Search

**POST /api/search**

Request:

```json
{
  "query": "project updates",
  "limit": 10,
  "date_range": null
}
```

Response:

```json
{
  "query": "project updates",
  "results": [
    {
      "text": "We discussed the project roadmap...",
      "metadata": {
        "date": "2026-01-28",
        "speaker": "Arvind",
        "source_file": "transcripts/2026-01-28.txt",
        "topics": ["project", "roadmap"]
      },
      "score": 0.87,
      "final_score": 0.91
    }
  ],
  "count": 1
}
```

**Features:**

- Semantic vector search
- Recency-biased ranking
- Metadata filtering
- Topic extraction

**Integration:** Uses MemorySearch from Phase 2 (Historian)

---

## Demo Mode

If backend components aren't available (missing ChromaDB, transcripts, etc.), the API runs in **Demo Mode** with mock data.

**Features in Demo Mode:**

- Health checks work
- All endpoints return mock data
- Perfect for frontend development
- Automatic fallback

**To disable demo mode:**

1. Set up ChromaDB (Phase 2)
2. Generate journals (Phase 3)
3. Ensure components importable

---

## CORS Configuration

Allowed origins:

- `http://localhost:3000` (Vite dev)
- `http://localhost:5173` (Alternative Vite port)
- `https://memex.vercel.app` (Production - update with your domain)

**To add origins:**

```python
# api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-domain.com",  # Add your domain
    ],
    ...
)
```

---

## Project Structure

```
api/
├── main.py             # FastAPI app
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Dependencies

**Production:**

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

**From Memex:**

- `retrieval.query_engine` - QueryEngine (Phase 4.1)
- `historian.search` - MemorySearch (Phase 2)
- `journalist.automation` - DailyAutomation (Phase 3)

---

## Development

### Interactive API Docs

FastAPI provides automatic interactive docs:

**Swagger UI:** http://localhost:8765/docs  
**ReDoc:** http://localhost:8765/redoc

### Testing Endpoints

**With curl:**

```bash
# Health check
curl http://localhost:8765/

# Chat query
curl -X POST http://localhost:8765/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What did I work on yesterday?"}'

# Get journals
curl "http://localhost:8765/api/journals?start_date=2026-01-01&end_date=2026-01-31"

# Search
curl -X POST http://localhost:8765/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "project updates", "limit": 5}'
```

**With HTTPie:**

```bash
# Chat query
http POST localhost:8765/api/chat/query query="What did I work on?"

# Journals
http GET "localhost:8765/api/journals?start_date=2026-01-01"

# Search
http POST localhost:8765/api/search query="meetings" limit:=5
```

---

## Deployment

### Railway (Recommended)

**Procfile:**

```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

**railway.json:**

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Deploy:**

```bash
railway login
railway init
railway up
```

### Docker

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8765

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8765"]
```

**Build & Run:**

```bash
docker build -t memex-api .
docker run -p 8765:8765 memex-api
```

### Vercel (Serverless)

**vercel.json:**

```json
{
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/main.py"
    }
  ]
}
```

---

## Performance

### Response Times

- **Health check:** <10ms
- **Chat query:** 500-2000ms (depends on GPT)
- **Journals:** <100ms (filesystem read)
- **Search:** 50-200ms (vector DB)

### Optimizations

- **Caching:** Add Redis for repeated queries
- **Async:** All endpoints are async-ready
- **Connection pooling:** ChromaDB persistent connection
- **CDN:** Static assets served by frontend

---

## Error Handling

All endpoints return standard HTTP status codes:

- **200 OK** - Success
- **400 Bad Request** - Invalid input
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

Error response format:

```json
{
  "detail": "Error message here"
}
```

---

## Monitoring

### Logs

Uvicorn logs all requests:

```
INFO:     127.0.0.1:54321 - "POST /api/chat/query HTTP/1.1" 200 OK
INFO:     127.0.0.1:54321 - "GET /api/journals HTTP/1.1" 200 OK
```

### Health Endpoint

Use `/api/status` for:

- Uptime monitoring
- Component health checks
- Load balancer health probes

---

## Security

### Current Implementation

- CORS enabled for specific origins
- Pydantic validation on all inputs
- No authentication (local use)

### Production Recommendations

1. **Add Authentication:**

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/chat/query")
async def chat_query(
    request: ChatQueryRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify token
    ...
```

2. **Rate Limiting:**

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/chat/query")
@limiter.limit("10/minute")
async def chat_query(...):
    ...
```

3. **HTTPS Only:**

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

---

## Troubleshooting

### API Won't Start

**Check Python version:**

```bash
python --version  # Should be 3.11+
```

**Check dependencies:**

```bash
pip install -r requirements.txt
```

**Check port availability:**

```bash
lsof -i :8765  # Port 8765 should be free
```

### CORS Errors

Frontend can't connect? Check:

1. Origin is in `allow_origins` list
2. API server is running
3. No firewall blocking port 8765

### Demo Mode Active

Component imports failing? Check:

1. ChromaDB installed: `pip install chromadb`
2. Transcripts exist in `memex/data/transcripts/`
3. Journals exist in `memex/data/journals/`

---

## Integration Status

### With Frontend (Phase 4.2) ✅

- Endpoints match expected API contract
- CORS configured for Vite dev server
- Response formats compatible

### With QueryEngine (Phase 4.1) ✅

- `/api/chat/query` integrates QueryEngine
- Handles conversation history
- Returns sources + confidence

### With Journalist (Phase 3) ✅

- `/api/journals` loads from filesystem
- Parses action items
- Returns metadata

### With Historian (Phase 2) ✅

- `/api/search` uses MemorySearch
- Recency ranking enabled
- Metadata included

---

## Roadmap

### v0.2.0

- [ ] WebSocket support for streaming responses
- [ ] Authentication/authorization
- [ ] Rate limiting
- [ ] Request caching (Redis)

### v0.3.0

- [ ] GraphQL API (optional)
- [ ] Batch operations
- [ ] File upload (transcript import)
- [ ] Export endpoints (PDF, JSON)

---

## License

MIT (same as Memex project)

---

## Credits

**Built by:** Nike 🐾  
**For:** Arvind's Memex  
**Date:** 2026-02-02

**Stack:**

- FastAPI 0.109
- Uvicorn (ASGI server)
- Pydantic (data validation)

---

🚀 **Connecting memory to interface!**
