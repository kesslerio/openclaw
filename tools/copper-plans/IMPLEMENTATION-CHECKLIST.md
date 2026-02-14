# Implementation Checklist with Dependencies

**Document Version:** 1.0
**Created:** February 1, 2026
**Author:** Nike (AI Companion)

---

## Dependency Graph Overview

```
                     ┌──────────────────┐
                     │   FOUNDATION     │
                     │  (Week 1-2)      │
                     └────────┬─────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Plaud Scraper  │  │   ChromaDB     │  │  PostgreSQL    │
│ (EXODUS)       │  │   (HISTORIAN)  │  │   (Database)   │
└───────┬────────┘  └───────┬────────┘  └───────┬────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │  Memex API     │
                   │  (Unification) │
                   └───────┬────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│   JOURNALIST   │ │    PARTNER     │ │  Integrations  │
│ (Auto-Journal) │ │  (Chat UI)     │ │ (Gmail, Cal)   │
└────────────────┘ └────────────────┘ └────────────────┘
```

---

## Phase 1: Foundation (Week 1-2)

### 1.1 Development Environment

**Priority:** P0 (Critical Path)
**Depends On:** None
**Blocks:** Everything else

| Task                  | Status | Dependencies | Command/Action                    |
| --------------------- | ------ | ------------ | --------------------------------- |
| Install Python 3.11+  | [ ]    | None         | `brew install python@3.11`        |
| Create virtualenv     | [ ]    | Python       | `python -m venv venv`             |
| Install pip packages  | [ ]    | virtualenv   | `pip install -r requirements.txt` |
| Install Playwright    | [ ]    | pip packages | `playwright install chromium`     |
| Set up PostgreSQL     | [ ]    | Homebrew     | `brew install postgresql@15`      |
| Install ChromaDB      | [ ]    | pip packages | `pip install chromadb`            |
| Configure environment | [ ]    | All above    | Create `.env` file                |

**Verification:**

```bash
# Run this script to verify environment
python --version  # Should be 3.11+
which playwright  # Should return path
psql --version    # Should be 15+
python -c "import chromadb; print('ChromaDB OK')"
```

---

### 1.2 Project Structure

**Priority:** P0 (Critical Path)
**Depends On:** 1.1 Development Environment
**Blocks:** All code implementation

| Task                     | Status | File/Directory              |
| ------------------------ | ------ | --------------------------- |
| Create memex/scraper/    | [ ]    | `mkdir -p memex/scraper`    |
| Create memex/historian/  | [ ]    | `mkdir -p memex/historian`  |
| Create memex/journalist/ | [ ]    | `mkdir -p memex/journalist` |
| Create memex/partner/    | [ ]    | `mkdir -p memex/partner`    |
| Create memex/api/        | [ ]    | `mkdir -p memex/api`        |
| Create memex/config/     | [ ]    | `mkdir -p memex/config`     |
| Create memex/models/     | [ ]    | `mkdir -p memex/models`     |
| Create memex/schema/     | [ ]    | `mkdir -p memex/schema`     |
| Create memex/tests/      | [ ]    | `mkdir -p memex/tests`      |
| Create memex/data/       | [ ]    | `mkdir -p memex/data`       |
| Create **init**.py files | [ ]    | All directories             |
| Create requirements.txt  | [ ]    | `memex/requirements.txt`    |
| Create pyproject.toml    | [ ]    | `memex/pyproject.toml`      |

**Complete Structure:**

```
memex/
├── __init__.py
├── requirements.txt
├── pyproject.toml
├── scraper/
│   ├── __init__.py
│   ├── plaud_scraper.py
│   ├── session_store.py
│   ├── rate_limiter.py
│   └── models.py
├── historian/
│   ├── __init__.py
│   ├── vector_store.py
│   ├── embeddings.py
│   └── indexer.py
├── journalist/
│   ├── __init__.py
│   ├── generator.py
│   └── templates.py
├── partner/
│   ├── __init__.py
│   └── chat.py
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   ├── middleware/
│   └── schemas/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── scraper_config.yaml
├── models/
│   ├── __init__.py
│   └── database.py
├── schema/
│   └── 001_initial_schema.sql
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_scraper.py
│   ├── test_vector_store.py
│   └── test_api.py
└── data/
    ├── chromadb/
    ├── transcripts/
    └── exports/
```

---

## Phase 2: Memex EXODUS (Week 1-2)

### 2.1 Plaud Scraper Core

**Priority:** P1 (High)
**Depends On:** 1.1, 1.2
**Blocks:** 2.2, 2.3, 2.4

| Task                      | Status | File                       | Dependencies |
| ------------------------- | ------ | -------------------------- | ------------ |
| Define data models        | [ ]    | `scraper/models.py`        | None         |
| Implement RateLimiter     | [ ]    | `scraper/rate_limiter.py`  | None         |
| Implement SessionStore    | [ ]    | `scraper/session_store.py` | None         |
| Create PlaudScraper class | [ ]    | `scraper/plaud_scraper.py` | models.py    |
| Implement login method    | [ ]    | `scraper/plaud_scraper.py` | SessionStore |
| Write login tests         | [ ]    | `tests/test_scraper.py`    | PlaudScraper |

**Data Models Required:**

```python
# scraper/models.py
@dataclass
class PlaudCredentials:
    email: str
    password: str
    two_factor_secret: Optional[str] = None

@dataclass
class TranscriptMetadata:
    id: str
    title: str
    date: datetime
    duration_seconds: int
    participants: List[str]
    download_url: str

@dataclass
class TranscriptContent:
    raw_text: str
    format: str
    segments: Optional[List[dict]] = None
    speakers: Optional[List[str]] = None

@dataclass
class BatchExportResult:
    success_count: int = 0
    failure_count: int = 0
    skipped_count: int = 0
    failures: List[tuple] = field(default_factory=list)
```

---

### 2.2 Transcript Fetching

**Priority:** P1 (High)
**Depends On:** 2.1 Plaud Scraper Core
**Blocks:** 2.3 Batch Export

| Task                            | Status | Method                                 | Dependencies  |
| ------------------------------- | ------ | -------------------------------------- | ------------- |
| Implement fetch_transcript_list | [ ]    | `PlaudScraper.fetch_transcript_list()` | login         |
| Handle pagination               | [ ]    | Internal to fetch                      | RateLimiter   |
| Implement download_transcript   | [ ]    | `PlaudScraper.download_transcript()`   | login         |
| Handle retry logic              | [ ]    | Internal                               | None          |
| Write fetch tests               | [ ]    | `tests/test_scraper.py`                | fetch methods |

**API Endpoint Research Required:**

- [ ] Navigate to Plaud.AI logged in
- [ ] Open Network tab in DevTools
- [ ] Note API endpoints for:
  - [ ] Transcript list endpoint
  - [ ] Transcript detail endpoint
  - [ ] Transcript download endpoint

---

### 2.3 Batch Export

**Priority:** P1 (High)
**Depends On:** 2.1, 2.2
**Blocks:** Phase 3 (HISTORIAN)

| Task                    | Status | Method                                 | Dependencies    |
| ----------------------- | ------ | -------------------------------------- | --------------- |
| Create manifest system  | [ ]    | `_load_manifest()`, `_save_manifest()` | None            |
| Implement batch_export  | [ ]    | `PlaudScraper.batch_export()`          | fetch, download |
| Create output structure | [ ]    | Internal                               | None            |
| Add progress callback   | [ ]    | Parameter                              | None            |
| Generate export report  | [ ]    | `_generate_report()`                   | batch_export    |
| Write batch tests       | [ ]    | `tests/test_scraper.py`                | batch_export    |

**Output Structure Verification:**

```bash
# After batch export, verify:
ls -la memex/data/transcripts/
ls -la memex/data/transcripts/2026-02-01/
cat memex/data/transcripts/manifest.json
```

---

### 2.4 Scraper Configuration

**Priority:** P2 (Medium)
**Depends On:** 2.1
**Blocks:** Production deployment

| Task                      | Status | File                         |
| ------------------------- | ------ | ---------------------------- |
| Create config schema      | [ ]    | `config/scraper_config.yaml` |
| Load config in scraper    | [ ]    | `scraper/plaud_scraper.py`   |
| Add environment overrides | [ ]    | `.env`                       |
| Document configuration    | [ ]    | `README.md`                  |

**Config Schema:**

```yaml
# config/scraper_config.yaml
plaud:
  base_url: "https://plaud.ai"
  login_url: "https://plaud.ai/login"
  api_base: "https://api.plaud.ai/v1"

scraper:
  headless: true
  timeout_ms: 30000
  rate_limit_per_second: 0.2
  retry_count: 3
  retry_delay_ms: 5000

output:
  directory: "./data/transcripts"
  formats:
    - json
    - txt
  include_metadata: true
```

---

## Phase 3: Memex HISTORIAN (Week 3-4)

### 3.1 ChromaDB Setup

**Priority:** P1 (High)
**Depends On:** 1.1 Development Environment
**Blocks:** 3.2, 3.3, 3.4

| Task                  | Status | File/Command                   |
| --------------------- | ------ | ------------------------------ |
| Install ChromaDB      | [ ]    | `pip install chromadb`         |
| Create data directory | [ ]    | `mkdir -p memex/data/chromadb` |
| Initialize client     | [ ]    | `historian/vector_store.py`    |
| Create collections    | [ ]    | `_init_collections()`          |
| Verify persistence    | [ ]    | Test script                    |

**Verification Script:**

```python
# Test ChromaDB setup
import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(
    path="./data/chromadb",
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_or_create_collection("test")
collection.add(ids=["1"], documents=["Test document"])
results = collection.query(query_texts=["test"], n_results=1)
print(f"ChromaDB working: {len(results['ids'][0]) > 0}")
```

---

### 3.2 Embedding Pipeline

**Priority:** P1 (High)
**Depends On:** 3.1 ChromaDB, OpenAI API Key
**Blocks:** 3.3 Vector Store

| Task                     | Status | File                       | Dependencies |
| ------------------------ | ------ | -------------------------- | ------------ |
| Install OpenAI SDK       | [ ]    | `pip install openai`       | None         |
| Verify API key           | [ ]    | `echo $OPENAI_API_KEY`     | API key      |
| Create EmbeddingPipeline | [ ]    | `historian/embeddings.py`  | OpenAI       |
| Implement single embed   | [ ]    | `embed_single()`           | API          |
| Implement batch embed    | [ ]    | `embed_batch()`            | API          |
| Add rate limiting        | [ ]    | Internal                   | None         |
| Write embedding tests    | [ ]    | `tests/test_embeddings.py` | Pipeline     |

**Cost Estimation:**

```
text-embedding-3-small: $0.00002 per 1K tokens
Estimated transcripts: 500
Average tokens per transcript: 5,000
Total tokens: 2,500,000
Estimated cost: $0.05 (initial indexing)
```

---

### 3.3 MemexVectorStore

**Priority:** P1 (High)
**Depends On:** 3.1, 3.2
**Blocks:** 3.4 Search API

| Task                          | Status | Method                       | Dependencies     |
| ----------------------------- | ------ | ---------------------------- | ---------------- |
| Create MemexVectorStore class | [ ]    | Class definition             | ChromaDB         |
| Initialize collections        | [ ]    | `_init_collections()`        | ChromaDB         |
| Implement add_transcript      | [ ]    | `add_transcript()`           | embeddings       |
| Implement add_journal         | [ ]    | `add_journal_entry()`        | embeddings       |
| Implement add_email           | [ ]    | `add_email()`                | embeddings       |
| Implement add_document        | [ ]    | `add_document()`             | embeddings       |
| Implement search              | [ ]    | `search()`                   | ChromaDB query   |
| Implement recency weighting   | [ ]    | `_calculate_recency_score()` | numpy            |
| Implement context window      | [ ]    | `get_context_window()`       | search           |
| Get stats                     | [ ]    | `get_stats()`                | ChromaDB         |
| Write vector store tests      | [ ]    | `tests/test_vector_store.py` | MemexVectorStore |

---

### 3.4 Transcript Indexer

**Priority:** P1 (High)
**Depends On:** 3.3, 2.3 (Batch Export complete)
**Blocks:** Search functionality

| Task                        | Status | File                    | Dependencies |
| --------------------------- | ------ | ----------------------- | ------------ |
| Create TranscriptIndexer    | [ ]    | `historian/indexer.py`  | VectorStore  |
| Track indexed files         | [ ]    | JSON manifest           | None         |
| Implement chunking          | [ ]    | `_chunk_transcript()`   | None         |
| Implement index_directory   | [ ]    | `index_directory()`     | VectorStore  |
| Implement incremental index | [ ]    | Skip already indexed    | manifest     |
| Write indexer tests         | [ ]    | `tests/test_indexer.py` | Indexer      |

**Run Indexer:**

```bash
cd /Users/arvindsarin/clawd/memex
python -c "
import asyncio
from historian.indexer import TranscriptIndexer
from historian.vector_store import MemexVectorStore
from pathlib import Path

async def main():
    store = MemexVectorStore()
    indexer = TranscriptIndexer(store)
    stats = await indexer.index_directory(Path('./data/transcripts'))
    print(f'Indexing complete: {stats}')

asyncio.run(main())
"
```

---

## Phase 4: PostgreSQL Database (Week 5-6)

### 4.1 PostgreSQL Installation

**Priority:** P1 (High)
**Depends On:** 1.1
**Blocks:** 4.2, 4.3, 4.4

#### Mac Installation

| Task               | Status | Command                             |
| ------------------ | ------ | ----------------------------------- |
| Install PostgreSQL | [ ]    | `brew install postgresql@15`        |
| Start service      | [ ]    | `brew services start postgresql@15` |
| Create database    | [ ]    | `createdb clawd`                    |
| Create user        | [ ]    | SQL command                         |
| Install pgvector   | [ ]    | `brew install pgvector`             |
| Enable extension   | [ ]    | `CREATE EXTENSION vector;`          |
| Set DATABASE_URL   | [ ]    | Export in .env                      |

#### VPS Installation

| Task                    | Status | Command                              |
| ----------------------- | ------ | ------------------------------------ |
| Install PostgreSQL      | [ ]    | `apt install postgresql`             |
| Install pgvector        | [ ]    | `apt install postgresql-15-pgvector` |
| Create database         | [ ]    | `createdb clawd`                     |
| Create user             | [ ]    | SQL command                          |
| Enable extension        | [ ]    | `CREATE EXTENSION vector;`           |
| Configure remote access | [ ]    | pg_hba.conf                          |

**Verification:**

```bash
psql clawd -c "SELECT version();"
psql clawd -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

---

### 4.2 Database Schema

**Priority:** P1 (High)
**Depends On:** 4.1
**Blocks:** 4.3 ORM Models

| Task                       | Status | Table                 |
| -------------------------- | ------ | --------------------- |
| Create transcripts table   | [ ]    | `transcripts`         |
| Create transcript_segments | [ ]    | `transcript_segments` |
| Create journal_entries     | [ ]    | `journal_entries`     |
| Create tasks               | [ ]    | `tasks`               |
| Create contacts            | [ ]    | `contacts`            |
| Create conversations       | [ ]    | `conversations`       |
| Create audit_log           | [ ]    | `audit_log`           |
| Create all indexes         | [ ]    | Various               |
| Apply schema               | [ ]    | `psql -f schema.sql`  |

**Apply Schema:**

```bash
cd /Users/arvindsarin/clawd/memex
psql $DATABASE_URL -f schema/001_initial_schema.sql
```

---

### 4.3 ORM Models

**Priority:** P1 (High)
**Depends On:** 4.2
**Blocks:** 4.4 API

| Task                     | Status | Model                         |
| ------------------------ | ------ | ----------------------------- |
| Install SQLAlchemy       | [ ]    | `pip install sqlalchemy`      |
| Install psycopg2         | [ ]    | `pip install psycopg2-binary` |
| Install pgvector         | [ ]    | `pip install pgvector`        |
| Create Base model        | [ ]    | `models/database.py`          |
| Create Transcript model  | [ ]    | `models/database.py`          |
| Create TranscriptSegment | [ ]    | `models/database.py`          |
| Create JournalEntry      | [ ]    | `models/database.py`          |
| Create Task model        | [ ]    | `models/database.py`          |
| Create Contact model     | [ ]    | `models/database.py`          |
| Create Conversation      | [ ]    | `models/database.py`          |
| Configure relationships  | [ ]    | Foreign keys                  |
| Write model tests        | [ ]    | `tests/test_models.py`        |

---

### 4.4 Database Migrations

**Priority:** P2 (Medium)
**Depends On:** 4.3
**Blocks:** Production deployment

| Task                     | Status | Command/File                      |
| ------------------------ | ------ | --------------------------------- |
| Install Alembic          | [ ]    | `pip install alembic`             |
| Initialize Alembic       | [ ]    | `alembic init migrations`         |
| Configure alembic.ini    | [ ]    | Update database URL               |
| Configure env.py         | [ ]    | Import models                     |
| Create initial migration | [ ]    | `alembic revision --autogenerate` |
| Apply migration          | [ ]    | `alembic upgrade head`            |
| Document rollback        | [ ]    | README                            |

---

## Phase 5: API Development (Week 7-8)

### 5.1 FastAPI Setup

**Priority:** P1 (High)
**Depends On:** 3.3, 4.3
**Blocks:** 5.2, 5.3, 5.4

| Task                        | Status | File                   |
| --------------------------- | ------ | ---------------------- |
| Install FastAPI             | [ ]    | `pip install fastapi`  |
| Install Uvicorn             | [ ]    | `pip install uvicorn`  |
| Create main.py              | [ ]    | `api/main.py`          |
| Configure CORS              | [ ]    | `api/main.py`          |
| Create routes directory     | [ ]    | `api/routes/`          |
| Create schemas directory    | [ ]    | `api/schemas/`         |
| Create middleware directory | [ ]    | `api/middleware/`      |
| Run server                  | [ ]    | `uvicorn api.main:app` |

---

### 5.2 Search Routes

**Priority:** P1 (High)
**Depends On:** 5.1, 3.3
**Blocks:** Partner chat

| Task                      | Status | Endpoint            |
| ------------------------- | ------ | ------------------- |
| Create search schema      | [ ]    | `schemas/search.py` |
| Implement /search         | [ ]    | GET semantic search |
| Implement /search/context | [ ]    | GET LLM context     |
| Implement /search/similar | [ ]    | GET similar items   |
| Add query validation      | [ ]    | Pydantic            |
| Write search tests        | [ ]    | `tests/test_api.py` |

---

### 5.3 CRUD Routes

**Priority:** P1 (High)
**Depends On:** 5.1, 4.3
**Blocks:** Full API

| Task                | Status | Route File                |
| ------------------- | ------ | ------------------------- |
| Transcript routes   | [ ]    | `routes/transcripts.py`   |
| Journal routes      | [ ]    | `routes/journals.py`      |
| Task routes         | [ ]    | `routes/tasks.py`         |
| Contact routes      | [ ]    | `routes/contacts.py`      |
| Conversation routes | [ ]    | `routes/conversations.py` |
| Health routes       | [ ]    | `routes/health.py`        |

**Standard CRUD for each:**

- GET / - List all
- GET /{id} - Get one
- POST / - Create
- PUT /{id} - Update
- DELETE /{id} - Delete

---

### 5.4 Middleware

**Priority:** P2 (Medium)
**Depends On:** 5.1
**Blocks:** Production

| Task                  | Status | File                       |
| --------------------- | ------ | -------------------------- |
| Auth middleware       | [ ]    | `middleware/auth.py`       |
| Logging middleware    | [ ]    | `middleware/logging.py`    |
| Rate limit middleware | [ ]    | `middleware/rate_limit.py` |
| Error handler         | [ ]    | `middleware/errors.py`     |

---

## Phase 6: Integration & Testing (Ongoing)

### 6.1 Unit Tests

**Priority:** P1 (High)
**Depends On:** All implementations
**Blocks:** Production

| Module       | Test File              | Status |
| ------------ | ---------------------- | ------ |
| Scraper      | `test_scraper.py`      | [ ]    |
| Vector Store | `test_vector_store.py` | [ ]    |
| Embeddings   | `test_embeddings.py`   | [ ]    |
| Indexer      | `test_indexer.py`      | [ ]    |
| Models       | `test_models.py`       | [ ]    |
| API Routes   | `test_api.py`          | [ ]    |
| Middleware   | `test_middleware.py`   | [ ]    |

**Run Tests:**

```bash
cd /Users/arvindsarin/clawd/memex
pytest tests/ -v --cov=. --cov-report=html
```

---

### 6.2 Integration Tests

**Priority:** P1 (High)
**Depends On:** 6.1
**Blocks:** Production

| Test             | Description              | Status |
| ---------------- | ------------------------ | ------ |
| Scraper → Index  | Full transcript pipeline | [ ]    |
| Search → Context | Search and context gen   | [ ]    |
| API → Database   | Full CRUD cycle          | [ ]    |
| End-to-end       | Complete user flow       | [ ]    |

---

## Environment Variables Checklist

| Variable         | Purpose       | Required By |
| ---------------- | ------------- | ----------- |
| `OPENAI_API_KEY` | Embeddings    | Phase 3     |
| `DATABASE_URL`   | PostgreSQL    | Phase 4     |
| `PLAUD_EMAIL`    | Scraper login | Phase 2     |
| `PLAUD_PASSWORD` | Scraper login | Phase 2     |
| `MEMEX_API_PORT` | API server    | Phase 5     |
| `CHROMADB_PATH`  | Vector store  | Phase 3     |
| `LOG_LEVEL`      | Logging       | All         |

**Sample .env:**

```bash
# memex/.env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://nike:password@localhost:5432/clawd
PLAUD_EMAIL=arvind@example.com
PLAUD_PASSWORD=secure_password
MEMEX_API_PORT=8891
CHROMADB_PATH=./data/chromadb
LOG_LEVEL=INFO
```

---

## Critical Path Summary

```
Week 1-2: Foundation → Scraper
Week 3-4: ChromaDB → Vector Store → Indexer
Week 5-6: PostgreSQL → Schema → Models
Week 7-8: API → Routes → Middleware

Critical Dependencies:
- Plaud.AI selectors (BLOCKER - needs Arvind)
- OpenAI API key (BLOCKER - needs setup)
- PostgreSQL passwords (BLOCKER - needs security)
```

---

## Daily Standup Template

```markdown
## Daily Standup - [DATE]

### Yesterday

- [ ] Task completed

### Today

- [ ] Task planned

### Blockers

- Description of blocker

### Notes

- Any relevant notes
```

---

## Weekly Review Template

```markdown
## Weekly Review - Week [N]

### Completed

- [ ] Feature/task

### In Progress

- [ ] Feature/task (X% complete)

### Blocked

- [ ] Feature/task - Reason

### Metrics

- Lines of code: X
- Tests passing: Y/Z
- Coverage: X%

### Next Week

- Priority 1
- Priority 2
- Priority 3
```

---

_Document generated by Nike on February 1, 2026_
