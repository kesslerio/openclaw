# Q1 2026 Immediate Action Items

**Document Version:** 1.0
**Created:** February 1, 2026
**Author:** Nike (AI Companion)
**Reference:** [ONE-YEAR-ROADMAP-2026.md](./ONE-YEAR-ROADMAP-2026.md)

---

## Executive Summary

This document provides **specific, executable action items** for Q1 2026, derived from the comprehensive one-year roadmap. Each item includes:

- Exact file paths and locations
- Command sequences to execute
- Dependencies and prerequisites
- Acceptance criteria
- Estimated effort

---

## Week 1-2: Memex EXODUS Completion (Feb 1-14)

### Action Item 1.1: Set Up Plaud.AI Scraper Project Structure

**Objective:** Create the scaffolding for the Plaud.AI transcript scraper

**Files to Create:**

```
memex/
├── scraper/
│   ├── __init__.py
│   ├── plaud_scraper.py      # Main scraper class
│   ├── session_store.py       # Cookie/session persistence
│   ├── rate_limiter.py        # Rate limiting utilities
│   └── models.py              # Data models (TranscriptMetadata, etc.)
├── config/
│   └── scraper_config.yaml    # Scraper configuration
└── tests/
    └── test_plaud_scraper.py  # Scraper tests
```

**Commands to Execute:**

```bash
cd /Users/arvindsarin/clawd/memex
mkdir -p scraper config
touch scraper/__init__.py
touch scraper/plaud_scraper.py
touch scraper/session_store.py
touch scraper/rate_limiter.py
touch scraper/models.py
touch config/scraper_config.yaml
```

**Dependencies:**

```bash
pip install playwright aiohttp pyyaml python-dateutil
playwright install chromium
```

**Acceptance Criteria:**

- [ ] All files created with proper imports
- [ ] PlaudScraper class skeleton implemented
- [ ] Tests file has at least 5 test stubs
- [ ] Config file has all required settings

---

### Action Item 1.2: Implement Plaud.AI Login Flow

**Objective:** Create working authentication with Plaud.AI

**File:** `memex/scraper/plaud_scraper.py`

**Implementation Steps:**

1. **Identify Plaud.AI login selectors** (REQUIRES ARVIND)
   - Navigate to https://plaud.ai/login
   - Open browser DevTools (F12)
   - Note selectors for:
     - Email input field
     - Password input field
     - Submit button
     - 2FA input (if present)
     - Success indicator (dashboard element)

2. **Create login method:**

   ```python
   async def login(self, credentials: PlaudCredentials) -> bool:
       await self.page.goto("https://plaud.ai/login")
       await self.page.fill("input[name='email']", credentials.email)  # UPDATE SELECTOR
       await self.page.fill("input[name='password']", credentials.password)  # UPDATE
       await self.page.click("button[type='submit']")  # UPDATE SELECTOR
       await self.page.wait_for_selector(".dashboard")  # UPDATE SELECTOR
       return True
   ```

3. **Store session cookies:**
   ```python
   async def save_session(self, path: str):
       cookies = await self.context.cookies()
       with open(path, 'w') as f:
           json.dump(cookies, f)
   ```

**Blocker:** Need Arvind to provide actual Plaud.AI selectors from browser inspection

**Acceptance Criteria:**

- [ ] Login succeeds with valid credentials
- [ ] Login fails gracefully with invalid credentials
- [ ] Session cookies are persisted
- [ ] Session can be restored from cookies

---

### Action Item 1.3: Implement Transcript List Fetching

**Objective:** Fetch list of available transcripts from Plaud.AI

**File:** `memex/scraper/plaud_scraper.py`

**Implementation Steps:**

1. **Identify transcript list API endpoint:**
   - After login, monitor Network tab
   - Look for XHR requests to transcript endpoints
   - Note: `/api/transcripts`, `/api/recordings`, or similar

2. **Implement fetch method:**
   ```python
   async def fetch_transcript_list(
       self,
       start_date: datetime,
       end_date: datetime,
       limit: int = 100
   ) -> List[TranscriptMetadata]:
       # Use intercepted API or page scraping
       response = await self.page.evaluate("""
           async () => {
               const resp = await fetch('/api/transcripts?start=...');
               return resp.json();
           }
       """)
       return [TranscriptMetadata(**t) for t in response]
   ```

**Acceptance Criteria:**

- [ ] Returns list of TranscriptMetadata objects
- [ ] Respects date range filters
- [ ] Handles pagination correctly
- [ ] Rate limiting is enforced

---

### Action Item 1.4: Implement Transcript Download

**Objective:** Download individual transcript content

**File:** `memex/scraper/plaud_scraper.py`

**Implementation Steps:**

1. **Identify download mechanism:**
   - Click on a transcript in Plaud.AI UI
   - Monitor network for content fetch
   - Note endpoint pattern

2. **Implement download:**

   ```python
   async def download_transcript(
       self,
       transcript_id: str,
       output_format: str = "json"
   ) -> TranscriptContent:
       await self.rate_limiter.acquire()

       # Navigate or API call
       response = await self.page.evaluate(f"""
           async () => {{
               const resp = await fetch('/api/transcript/{transcript_id}');
               return resp.json();
           }}
       """)

       return TranscriptContent(
           raw_text=response['text'],
           segments=response.get('segments', []),
           speakers=response.get('speakers', [])
       )
   ```

**Acceptance Criteria:**

- [ ] Downloads transcript content in requested format
- [ ] Includes speaker diarization if available
- [ ] Includes timestamps if available
- [ ] Retries on transient failures

---

### Action Item 1.5: Implement Batch Export

**Objective:** Export all transcripts within a date range

**File:** `memex/scraper/plaud_scraper.py`

**Implementation Steps:**

1. **Create batch export method:**

   ```python
   async def batch_export(
       self,
       start_date: datetime,
       end_date: datetime,
       output_dir: Path,
       progress_callback: Optional[Callable] = None
   ) -> BatchExportResult:
       output_dir.mkdir(parents=True, exist_ok=True)
       manifest_path = output_dir / "manifest.json"

       # Load existing manifest
       manifest = self._load_manifest(manifest_path)

       # Fetch transcript list
       transcripts = await self.fetch_transcript_list(start_date, end_date)

       # Filter out already downloaded
       to_download = [t for t in transcripts if t.id not in manifest['downloaded']]

       results = BatchExportResult()
       for i, transcript in enumerate(to_download):
           try:
               content = await self.download_transcript(transcript.id)
               self._save_transcript(output_dir, transcript, content)
               manifest['downloaded'].append(transcript.id)
               results.success_count += 1
           except Exception as e:
               results.failures.append((transcript.id, str(e)))
               results.failure_count += 1

           if progress_callback:
               progress_callback(i + 1, len(to_download), transcript.id)

       self._save_manifest(manifest_path, manifest)
       return results
   ```

**Output Directory Structure:**

```
output_dir/
├── manifest.json              # Tracks downloaded transcripts
├── 2026-02-01/
│   ├── meeting-001.json       # Full transcript data
│   ├── meeting-001.txt        # Plain text version
│   └── meeting-001-meta.json  # Metadata only
├── 2026-02-02/
│   └── ...
└── export-report.md           # Summary of export
```

**Acceptance Criteria:**

- [ ] Creates proper directory structure
- [ ] Maintains manifest for incremental exports
- [ ] Progress callback works correctly
- [ ] Generates summary report

---

## Week 3-4: Memex HISTORIAN (Feb 15-28)

### Action Item 2.1: Set Up ChromaDB Infrastructure

**Objective:** Install and configure ChromaDB for vector storage

**Commands to Execute:**

```bash
cd /Users/arvindsarin/clawd/memex

# Install ChromaDB
pip install chromadb openai numpy

# Create data directory
mkdir -p data/chromadb

# Create historian module
mkdir -p historian
touch historian/__init__.py
touch historian/vector_store.py
touch historian/embeddings.py
touch historian/indexer.py
```

**Configuration File:** `memex/config/chromadb_config.yaml`

```yaml
persist_directory: "./data/chromadb"
embedding_model: "text-embedding-3-small"
embedding_dimensions: 1536
collections:
  transcripts:
    description: "Meeting transcript segments"
    chunk_size: 500
    chunk_overlap: 50
  journals:
    description: "Daily journal paragraphs"
    chunk_size: 300
    chunk_overlap: 30
  emails:
    description: "Email messages"
    chunk_size: 400
    chunk_overlap: 40
  documents:
    description: "Document chunks"
    chunk_size: 500
    chunk_overlap: 50
  conversations:
    description: "Chat messages"
    chunk_size: 200
    chunk_overlap: 20
```

**Acceptance Criteria:**

- [ ] ChromaDB installed and importable
- [ ] Data directory created with write permissions
- [ ] Configuration file created
- [ ] Test connection works

---

### Action Item 2.2: Implement MemexVectorStore Core

**Objective:** Create the main vector store class with CRUD operations

**File:** `memex/historian/vector_store.py`

**Implementation Steps:**

1. **Initialize ChromaDB client:**

   ```python
   from typing import List, Optional
   import chromadb
   from chromadb.config import Settings

   class MemexVectorStore:
       def __init__(self, persist_directory: str = "./data/chromadb"):
           self.client = chromadb.PersistentClient(
               path=persist_directory,
               settings=Settings(anonymized_telemetry=False)
           )
           self._init_collections()
   ```

2. **Create collection initialization:**

   ```python
   def _init_collections(self):
       self.collections = {}
       for name in ["transcripts", "journals", "emails", "documents", "conversations"]:
           self.collections[name] = self.client.get_or_create_collection(
               name=name,
               metadata={"hnsw:space": "cosine"}
           )
   ```

3. **Implement add methods for each content type**

4. **Implement search with recency weighting**

**Acceptance Criteria:**

- [ ] All 5 collections initialized
- [ ] Add methods work for each type
- [ ] Search returns relevant results
- [ ] Recency weighting affects rankings

---

### Action Item 2.3: Implement Embedding Pipeline

**Objective:** Create efficient batch embedding with OpenAI

**File:** `memex/historian/embeddings.py`

**Implementation:**

```python
from openai import OpenAI
from typing import List
import asyncio

class EmbeddingPipeline:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.client = OpenAI()
        self.model = model
        self.dimensions = 1536
        self.batch_size = 100
        self.rate_limit = 3000  # requests per minute

    async def embed_single(self, text: str) -> List[float]:
        response = await asyncio.to_thread(
            self.client.embeddings.create,
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            response = await asyncio.to_thread(
                self.client.embeddings.create,
                model=self.model,
                input=batch
            )
            embeddings.extend([d.embedding for d in response.data])
            await asyncio.sleep(0.02)  # Rate limiting
        return embeddings
```

**Environment Variable Required:**

```bash
export OPENAI_API_KEY="sk-..."
```

**Acceptance Criteria:**

- [ ] Single text embedding works
- [ ] Batch embedding works efficiently
- [ ] Rate limiting prevents API errors
- [ ] Embeddings have correct dimensions (1536)

---

### Action Item 2.4: Create Transcript Indexer

**Objective:** Index downloaded transcripts into vector store

**File:** `memex/historian/indexer.py`

**Implementation:**

```python
import os
import json
from pathlib import Path
from .vector_store import MemexVectorStore

class TranscriptIndexer:
    def __init__(self, vector_store: MemexVectorStore):
        self.store = vector_store
        self.indexed_file = Path("./data/indexed_transcripts.json")

    async def index_directory(self, transcript_dir: Path) -> dict:
        """Index all transcripts in a directory."""
        indexed = self._load_indexed()
        stats = {"new": 0, "skipped": 0, "errors": 0}

        for date_dir in transcript_dir.iterdir():
            if not date_dir.is_dir():
                continue

            for file in date_dir.glob("*.json"):
                if file.stem.endswith("-meta"):
                    continue

                transcript_id = file.stem
                if transcript_id in indexed:
                    stats["skipped"] += 1
                    continue

                try:
                    await self._index_transcript(file)
                    indexed.append(transcript_id)
                    stats["new"] += 1
                except Exception as e:
                    stats["errors"] += 1
                    print(f"Error indexing {file}: {e}")

        self._save_indexed(indexed)
        return stats

    async def _index_transcript(self, file: Path):
        """Index a single transcript file."""
        with open(file) as f:
            data = json.load(f)

        # Chunk into segments
        segments = self._chunk_transcript(data)

        # Add to vector store
        await self.store.add_transcript(
            transcript_id=file.stem,
            segments=segments,
            metadata={
                "date": data.get("date", ""),
                "title": data.get("title", ""),
                "source": "plaud"
            }
        )

    def _chunk_transcript(self, data: dict) -> List[dict]:
        """Chunk transcript into indexable segments."""
        if "segments" in data:
            return data["segments"]

        # Fall back to splitting by sentences
        text = data.get("text", data.get("raw_text", ""))
        sentences = text.split(". ")

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            if current_length + len(sentence) > 500:
                chunks.append({"text": ". ".join(current_chunk) + "."})
                current_chunk = [sentence]
                current_length = len(sentence)
            else:
                current_chunk.append(sentence)
                current_length += len(sentence)

        if current_chunk:
            chunks.append({"text": ". ".join(current_chunk)})

        return chunks
```

**Commands to Run:**

```bash
# Index all transcripts
cd /Users/arvindsarin/clawd/memex
python -c "
import asyncio
from historian.indexer import TranscriptIndexer
from historian.vector_store import MemexVectorStore

async def main():
    store = MemexVectorStore()
    indexer = TranscriptIndexer(store)
    stats = await indexer.index_directory(Path('./data/transcripts'))
    print(f'Indexed: {stats}')

asyncio.run(main())
"
```

**Acceptance Criteria:**

- [ ] Indexes all transcripts in directory
- [ ] Skips already-indexed transcripts
- [ ] Chunks transcripts appropriately
- [ ] Reports indexing statistics

---

### Action Item 2.5: Implement Semantic Search API

**Objective:** Create search endpoint for querying memory

**File:** `memex/historian/search_api.py`

**Implementation:**

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from .vector_store import MemexVectorStore

app = FastAPI(title="Memex Search API")
store = MemexVectorStore()

class SearchResult(BaseModel):
    content: str
    collection: str
    score: float
    date: str
    metadata: dict

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int

@app.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Search query"),
    collections: Optional[str] = Query(None, description="Comma-separated collection names"),
    limit: int = Query(10, ge=1, le=50),
    recency_weight: float = Query(0.3, ge=0, le=1)
):
    """Semantic search across Nike's memory."""
    collection_list = collections.split(",") if collections else None

    results = await store.search(
        query=q,
        collections=collection_list,
        n_results=limit,
        recency_weight=recency_weight
    )

    return SearchResponse(
        query=q,
        results=[
            SearchResult(
                content=r.content,
                collection=r.collection,
                score=r.final_score,
                date=r.metadata.get("date", ""),
                metadata=r.metadata
            )
            for r in results
        ],
        total=len(results)
    )

@app.get("/context")
async def get_context(
    q: str = Query(..., description="Query for context"),
    max_tokens: int = Query(4000, ge=100, le=8000)
):
    """Get formatted context for LLM prompt."""
    context = await store.get_context_window(query=q, max_tokens=max_tokens)
    return {"query": q, "context": context}
```

**Commands to Run:**

```bash
# Install FastAPI
pip install fastapi uvicorn

# Run search API
cd /Users/arvindsarin/clawd/memex
uvicorn historian.search_api:app --host 0.0.0.0 --port 8890 --reload
```

**Test Commands:**

```bash
# Test search
curl "http://localhost:8890/search?q=meeting+about+AI&limit=5"

# Test context generation
curl "http://localhost:8890/context?q=what+did+we+discuss+about+budget"
```

**Acceptance Criteria:**

- [ ] API starts on port 8890
- [ ] Search endpoint returns ranked results
- [ ] Context endpoint returns formatted text
- [ ] Recency weighting affects results

---

## Week 5-6: March Infrastructure (Mar 1-14)

### Action Item 3.1: Set Up PostgreSQL Database

**Objective:** Install and configure PostgreSQL for structured data

**Commands (Mac):**

```bash
# Install PostgreSQL via Homebrew
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Create database
createdb clawd

# Create user
psql clawd -c "CREATE USER nike WITH PASSWORD 'secure_password_here';"
psql clawd -c "GRANT ALL PRIVILEGES ON DATABASE clawd TO nike;"

# Install pgvector extension
brew install pgvector
psql clawd -c "CREATE EXTENSION vector;"
```

**Commands (VPS/Ubuntu):**

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Install pgvector
sudo apt install postgresql-15-pgvector

# Create database
sudo -u postgres createdb clawd
sudo -u postgres psql clawd -c "CREATE USER nike WITH PASSWORD 'secure_password_here';"
sudo -u postgres psql clawd -c "GRANT ALL PRIVILEGES ON DATABASE clawd TO nike;"
sudo -u postgres psql clawd -c "CREATE EXTENSION vector;"
```

**Environment Variables:**

```bash
export DATABASE_URL="postgresql://nike:secure_password_here@localhost:5432/clawd"
```

**Acceptance Criteria:**

- [ ] PostgreSQL running on both Mac and VPS
- [ ] Database `clawd` created
- [ ] pgvector extension installed
- [ ] User `nike` has proper permissions

---

### Action Item 3.2: Create Database Schema

**Objective:** Create all required database tables

**File:** `memex/schema/001_initial_schema.sql`

**SQL to Execute:**

```sql
-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Transcripts table
CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(255) UNIQUE NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'plaud',
    title VARCHAR(500),
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_seconds INTEGER,
    raw_text TEXT NOT NULL,
    speaker_count INTEGER,
    word_count INTEGER,
    language VARCHAR(10) DEFAULT 'en',
    processed_at TIMESTAMP WITH TIME ZONE,
    embedding_generated BOOLEAN DEFAULT FALSE,
    journal_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_transcripts_recorded_at ON transcripts(recorded_at);
CREATE INDEX idx_transcripts_source ON transcripts(source);

-- Transcript segments (for granular search)
CREATE TABLE transcript_segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transcript_id UUID REFERENCES transcripts(id) ON DELETE CASCADE,
    speaker_label VARCHAR(100),
    start_time_ms INTEGER NOT NULL,
    end_time_ms INTEGER NOT NULL,
    text TEXT NOT NULL,
    confidence FLOAT,
    embedding VECTOR(1536)
);

CREATE INDEX idx_segments_transcript ON transcript_segments(transcript_id);
CREATE INDEX idx_segments_embedding ON transcript_segments USING ivfflat (embedding vector_cosine_ops);

-- Journal entries
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL UNIQUE,
    title VARCHAR(255),
    content TEXT NOT NULL,
    summary TEXT,
    key_points JSONB,
    mood VARCHAR(50),
    energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    word_count INTEGER,
    source_transcripts JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_journal_date ON journal_entries(date);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(255),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    owner VARCHAR(100),
    tags JSONB,
    source VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_owner ON tasks(owner);

-- Contacts table
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    company VARCHAR(255),
    title VARCHAR(255),
    relationship VARCHAR(50),
    last_contacted_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    tags JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_last_contacted ON contacts(last_contacted_at);

-- Conversation history
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tokens_used INTEGER,
    model VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_created ON conversations(created_at);

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    old_value JSONB,
    new_value JSONB,
    performed_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_created ON audit_log(created_at);
```

**Commands to Run:**

```bash
# Apply schema
psql $DATABASE_URL -f memex/schema/001_initial_schema.sql
```

**Acceptance Criteria:**

- [ ] All tables created successfully
- [ ] All indexes created
- [ ] pgvector extension working
- [ ] Can insert and query test data

---

### Action Item 3.3: Set Up Database Migration System

**Objective:** Use Alembic for database migrations

**Commands:**

```bash
cd /Users/arvindsarin/clawd/memex
pip install alembic psycopg2-binary sqlalchemy

# Initialize Alembic
alembic init migrations
```

**File:** `memex/alembic.ini` (update)

```ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql://nike:password@localhost/clawd
```

**File:** `memex/migrations/env.py` (update)

```python
import os
from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

# Get database URL from environment
config.set_main_option('sqlalchemy.url', os.environ.get('DATABASE_URL'))
```

**Acceptance Criteria:**

- [ ] Alembic initialized
- [ ] Can create new migrations
- [ ] Can apply migrations
- [ ] Can rollback migrations

---

### Action Item 3.4: Create Database ORM Models

**Objective:** Define SQLAlchemy models for all tables

**File:** `memex/models/database.py`

**Implementation:**

```python
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

Base = declarative_base()

class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(255), unique=True, nullable=False)
    source = Column(String(50), default="plaud")
    title = Column(String(500))
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    duration_seconds = Column(Integer)
    raw_text = Column(Text, nullable=False)
    speaker_count = Column(Integer)
    word_count = Column(Integer)
    language = Column(String(10), default="en")
    processed_at = Column(DateTime(timezone=True))
    embedding_generated = Column(Boolean, default=False)
    journal_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    segments = relationship("TranscriptSegment", back_populates="transcript", cascade="all, delete-orphan")

class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("transcripts.id", ondelete="CASCADE"))
    speaker_label = Column(String(100))
    start_time_ms = Column(Integer, nullable=False)
    end_time_ms = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    confidence = Column(Float)
    embedding = Column(Vector(1536))

    transcript = relationship("Transcript", back_populates="segments")

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime, unique=True, nullable=False)
    title = Column(String(255))
    content = Column(Text, nullable=False)
    summary = Column(Text)
    key_points = Column(JSONB)
    mood = Column(String(50))
    energy_level = Column(Integer)
    word_count = Column(Integer)
    source_transcripts = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(255))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="pending")
    priority = Column(String(20), default="medium")
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    owner = Column(String(100))
    tags = Column(JSONB)
    source = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(255))
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    company = Column(String(255))
    title = Column(String(255))
    relationship = Column(String(50))
    last_contacted_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    tags = Column(JSONB)
    metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer)
    model = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
```

**Acceptance Criteria:**

- [ ] All models defined
- [ ] Relationships configured correctly
- [ ] Can create/read/update/delete records
- [ ] Vector column works with pgvector

---

## Week 7-8: API Development (Mar 15-31)

### Action Item 4.1: Set Up FastAPI Project Structure

**Objective:** Create production-ready API structure

**Directory Structure:**

```
memex/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── search.py        # Search endpoints
│   │   ├── transcripts.py   # Transcript CRUD
│   │   ├── journals.py      # Journal CRUD
│   │   ├── tasks.py         # Task CRUD
│   │   └── health.py        # Health checks
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication
│   │   ├── logging.py       # Request logging
│   │   └── rate_limit.py    # Rate limiting
│   └── schemas/
│       ├── __init__.py
│       ├── search.py
│       ├── transcript.py
│       ├── journal.py
│       └── task.py
```

**Commands:**

```bash
cd /Users/arvindsarin/clawd/memex
mkdir -p api/routes api/middleware api/schemas
touch api/__init__.py api/main.py
touch api/routes/{__init__,search,transcripts,journals,tasks,health}.py
touch api/middleware/{__init__,auth,logging,rate_limit}.py
touch api/schemas/{__init__,search,transcript,journal,task}.py
```

**Acceptance Criteria:**

- [ ] All directories created
- [ ] All files have proper imports
- [ ] FastAPI app runs without errors

---

### Action Item 4.2: Implement Core API Endpoints

**Objective:** Create REST API for Memex operations

**File:** `memex/api/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import search, transcripts, journals, tasks, health

app = FastAPI(
    title="Memex API",
    description="Nike's Memory & Knowledge Base API",
    version="1.0.0"
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8888"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(transcripts.router, prefix="/transcripts", tags=["Transcripts"])
app.include_router(journals.router, prefix="/journals", tags=["Journals"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

@app.get("/")
async def root():
    return {"message": "Memex API v1.0.0", "docs": "/docs"}
```

**Commands to Run:**

```bash
# Run API server
cd /Users/arvindsarin/clawd/memex
uvicorn api.main:app --host 0.0.0.0 --port 8891 --reload
```

**Acceptance Criteria:**

- [ ] API starts on port 8891
- [ ] Swagger docs available at /docs
- [ ] All routes registered
- [ ] CORS configured correctly

---

### Action Item 4.3: Implement Search Endpoints

**File:** `memex/api/routes/search.py`

```python
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter()

class SearchResult(BaseModel):
    content: str
    collection: str
    score: float
    date: Optional[str]
    metadata: dict

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int
    processing_time_ms: float

@router.get("/", response_model=SearchResponse)
async def semantic_search(
    q: str = Query(..., min_length=3, description="Search query"),
    collections: Optional[str] = Query(None, description="Comma-separated collections"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    recency_weight: float = Query(0.3, ge=0, le=1, description="Recency weight"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)")
):
    """
    Semantic search across Nike's memory.

    Returns relevant content from transcripts, journals, emails, etc.
    Results are ranked by relevance with optional recency weighting.
    """
    # Implementation here
    pass

@router.get("/context", response_model=dict)
async def get_llm_context(
    q: str = Query(..., min_length=3, description="Query for context"),
    max_tokens: int = Query(4000, ge=100, le=8000, description="Max tokens in context")
):
    """
    Get formatted context for LLM prompt construction.

    Returns relevant memory content formatted for inclusion in an LLM prompt.
    """
    # Implementation here
    pass

@router.get("/similar/{item_id}")
async def find_similar(
    item_id: str,
    collection: str = Query(..., description="Collection name"),
    limit: int = Query(5, ge=1, le=20)
):
    """
    Find items similar to a given item.
    """
    # Implementation here
    pass
```

**Acceptance Criteria:**

- [ ] Search endpoint returns relevant results
- [ ] Context endpoint returns formatted text
- [ ] Similar endpoint works for all collections
- [ ] All query parameters validated

---

## Dependencies Checklist

### Python Packages Required

```bash
pip install \
    playwright \
    chromadb \
    openai \
    fastapi \
    uvicorn \
    sqlalchemy \
    psycopg2-binary \
    alembic \
    pgvector \
    pydantic \
    python-dateutil \
    pyyaml \
    aiohttp \
    numpy \
    pytest \
    pytest-asyncio \
    httpx
```

### System Dependencies

| Dependency | Mac Command                   | Ubuntu Command                       |
| ---------- | ----------------------------- | ------------------------------------ |
| PostgreSQL | `brew install postgresql@15`  | `apt install postgresql`             |
| pgvector   | `brew install pgvector`       | `apt install postgresql-15-pgvector` |
| Chromium   | `playwright install chromium` | `playwright install chromium`        |

### API Keys Required

| Service  | Purpose     | Environment Variable            |
| -------- | ----------- | ------------------------------- |
| OpenAI   | Embeddings  | `OPENAI_API_KEY`                |
| Plaud.AI | Credentials | `PLAUD_EMAIL`, `PLAUD_PASSWORD` |

### Ports Used

| Service          | Port | Purpose       |
| ---------------- | ---- | ------------- |
| Kanban Server    | 8888 | Existing      |
| Kanban Publish   | 8889 | Existing      |
| Memex Search API | 8890 | Vector search |
| Memex Main API   | 8891 | Full API      |
| PostgreSQL       | 5432 | Database      |

---

## Weekly Progress Checkpoints

### Week 1 Checkpoint (Feb 7)

- [ ] Scraper project structure created
- [ ] PlaudScraper class implemented (login stub)
- [ ] Playwright installed and working
- [ ] First test passing

### Week 2 Checkpoint (Feb 14)

- [ ] Login flow working with Plaud.AI
- [ ] Transcript list fetch working
- [ ] Download single transcript working
- [ ] Batch export functional

### Week 3 Checkpoint (Feb 21)

- [ ] ChromaDB installed and configured
- [ ] MemexVectorStore class complete
- [ ] Embedding pipeline working
- [ ] First transcripts indexed

### Week 4 Checkpoint (Feb 28)

- [ ] All downloaded transcripts indexed
- [ ] Semantic search working
- [ ] Context generation working
- [ ] Search API deployed

### Week 5 Checkpoint (Mar 7)

- [ ] PostgreSQL installed (Mac + VPS)
- [ ] Database schema applied
- [ ] Alembic migrations working
- [ ] ORM models complete

### Week 6 Checkpoint (Mar 14)

- [ ] All tables populated with test data
- [ ] CRUD operations working
- [ ] Database backup script created
- [ ] Sync between Mac and VPS tested

### Week 7 Checkpoint (Mar 21)

- [ ] FastAPI project structure complete
- [ ] All routes implemented
- [ ] Authentication middleware working
- [ ] API documentation complete

### Week 8 Checkpoint (Mar 31)

- [ ] All endpoints tested
- [ ] Rate limiting working
- [ ] Logging configured
- [ ] Production deployment ready

---

## Quick Start Commands

```bash
# Start development environment
cd /Users/arvindsarin/clawd/memex

# Terminal 1: PostgreSQL
brew services start postgresql@15

# Terminal 2: Memex Search API
uvicorn historian.search_api:app --port 8890 --reload

# Terminal 3: Memex Main API
uvicorn api.main:app --port 8891 --reload

# Terminal 4: Run tests
pytest tests/ -v

# Full test suite
./tests/run_all.sh
```

---

## Blocking Issues & Escalations

### BLOCKER 1: Plaud.AI Selectors

**Status:** Waiting on Arvind
**Action Required:** Inspect Plaud.AI login page and provide CSS selectors
**Workaround:** Manual transcript export until automated

### BLOCKER 2: OpenAI API Key

**Status:** Verify key is set
**Action Required:** Ensure `OPENAI_API_KEY` is in environment
**Cost Estimate:** ~$5-10/month for embeddings

### BLOCKER 3: Database Passwords

**Status:** Need secure passwords
**Action Required:** Generate and store secure passwords for PostgreSQL
**Recommendation:** Use 1Password or similar

---

## Risk Mitigation

| Risk                   | Probability | Impact | Mitigation                        |
| ---------------------- | ----------- | ------ | --------------------------------- |
| Plaud.AI changes UI    | Medium      | High   | Store raw HTML for re-parsing     |
| OpenAI API rate limits | Low         | Medium | Implement backoff, batch requests |
| Database corruption    | Low         | High   | Daily backups, transaction logs   |
| VPS sync failure       | Medium      | Medium | Manual sync fallback, monitoring  |

---

## Next Actions (Immediate)

1. **Today:** Create memex/scraper directory structure
2. **Today:** Install Playwright and test browser launch
3. **Tomorrow:** Ask Arvind for Plaud.AI selectors
4. **This Week:** Implement login flow stub with mock selectors

---

_Document generated by Nike on February 1, 2026_
_Reference: [ONE-YEAR-ROADMAP-2026.md](./ONE-YEAR-ROADMAP-2026.md)_
