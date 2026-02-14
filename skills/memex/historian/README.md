# Memex HISTORIAN - AI Memory System

**Status:** ✅ Phase 2 Complete (Vector Database & Search)

The HISTORIAN is the core memory system for Memex. It stores, indexes, and retrieves Plaud.AI transcripts using semantic search with **recency ranking** — making recent memories surface higher than old ones.

## 🌟 Key Features

### 1. **Recency-Aware Search** (THE SECRET SAUCE)

- Combines semantic similarity (70%) + recency (30%)
- Recent memories automatically rank higher
- Exponential time decay (5% per day)
- Mimics how human memory works

### 2. **Semantic Vector Search**

- Powered by ChromaDB + OpenAI embeddings
- Find memories by meaning, not keywords
- "What did I promise Mark?" → finds relevant conversations

### 3. **Smart Chunking**

- Breaks long transcripts into 500-char chunks
- 50-char overlap for context preservation
- Preserves metadata across chunks

### 4. **REST API**

- FastAPI server for search queries
- Date range filtering
- Speaker filtering
- Explanation mode (see how results were ranked)

## 📦 Architecture

```
historian/
├── config.py           # Settings & paths
├── vector_store.py     # ChromaDB wrapper
├── embeddings.py       # OpenAI embeddings
├── text_processor.py   # Parse & chunk transcripts
├── recency_ranker.py   # 🌟 Recency ranking algorithm
├── ingest.py           # Ingestion pipeline
├── search.py           # Search engine
├── api.py              # FastAPI server
└── __init__.py
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/ubuntu/openclaw/skills/memex/historian
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your-api-key"
```

### 3. Ingest Transcripts

```python
from historian import IngestionPipeline

pipeline = IngestionPipeline()

# Ingest all transcripts from data/transcripts/
stats = pipeline.ingest_directory()

print(f"Ingested {stats['total_chunks']} chunks from {stats['successful']} files")
```

### 4. Search Your Memories

```python
from historian import SearchEngine

search = SearchEngine()

# Search with recency ranking
results = search.search(
    query="What did I discuss about AI?",
    n_results=10,
    use_recency=True,
    explain=True,  # Get ranking explanation
)

for result in results['results']:
    print(f"{result['metadata']['date']}: {result['metadata']['title']}")
    print(f"Score: {result['score']:.3f} (sim: {result['similarity_score']:.3f}, recency: {result['recency_score']:.3f})")
    print(result['document'][:200])
    print()
```

### 5. Start API Server

```bash
cd /home/ubuntu/openclaw/skills/memex
python -m historian.api
```

API will be available at http://localhost:8765

**Try it:**

```bash
curl "http://localhost:8765/search?q=AI+discussion&n=5&use_recency=true"
```

## 📊 Recency Ranking Algorithm

The **key innovation** that makes Memex useful:

```python
final_score = (similarity_score × 0.7) + (recency_score × 0.3)

where:
  similarity_score = 1 / (1 + L2_distance)  # From vector search
  recency_score = exp(-0.05 × days_ago)     # Exponential decay
```

**Example:**

| Memory                  | Days Ago | Similarity | Recency | Final Score |
| ----------------------- | -------- | ---------- | ------- | ----------- |
| Today's perfect match   | 0        | 1.0        | 1.0     | **1.000**   |
| Week-old perfect match  | 7        | 1.0        | 0.70    | **0.910**   |
| Month-old perfect match | 30       | 1.0        | 0.22    | **0.766**   |
| Today's weak match      | 0        | 0.4        | 1.0     | **0.580**   |

**Insight:** A perfect match from 30 days ago (0.766) beats a weak match from today (0.580). But a strong match from today (1.0) beats everything.

## 🧪 Testing

All components have TDD tests:

```bash
cd /home/ubuntu/openclaw/skills/memex
pytest tests/test_recency_ranker.py -v
pytest tests/test_vector_store.py -v
pytest tests/test_text_processor.py -v
```

**Test Coverage:**

- ✅ Recency ranking algorithm (15 tests)
- ✅ Vector store CRUD operations (10 tests)
- ✅ Text processing & chunking (9 tests)
- ✅ Embeddings generation
- ✅ Ingestion pipeline
- ✅ Search engine

## 💰 Cost Estimates

**Initial Indexing (2,500 transcripts):**

- ~1M tokens to embed
- Cost: ~$20 (text-embedding-3-small @ $0.02/1M tokens)
- One-time cost

**Ongoing Usage:**

- Queries: FREE (no embedding needed)
- New transcripts: ~$0.001 per transcript
- Monthly: ~$3-5 for daily transcripts

**Total:** ~$20 setup + ~$5/month ongoing

## 🔧 Configuration

Edit `historian/config.py`:

```python
# Chunking
CHUNK_SIZE = 500  # Increase for longer context
CHUNK_OVERLAP = 50  # Increase for better continuity

# Recency Ranking
SIMILARITY_WEIGHT = 0.7  # Adjust semantic vs recency balance
RECENCY_WEIGHT = 0.3
DECAY_RATE = 0.05  # Higher = faster decay (more emphasis on recent)

# Embedding Model
EMBEDDING_MODEL = "text-embedding-3-small"  # Or "text-embedding-3-large" for quality
```

## 📝 Usage Examples

### Date Range Search

```python
# Find memories from last week
results = search.search_by_date_range(
    query="meetings",
    days_back=7,
    n_results=10,
)
```

### Speaker Filter

```python
# Find conversations with specific person
results = search.search(
    query="project discussion",
    speaker="John Smith",
    n_results=5,
)
```

### Get Recent Memories

```python
# Get all memories from last 7 days
recent = search.get_recent_memories(days=7, n_results=20)
```

### Explain Rankings

```python
# See why results ranked the way they did
results = search.search(
    query="AI",
    n_results=5,
    explain=True,
)

print(results['explanation'])
```

## 🐛 Troubleshooting

**Error: `OPENAI_API_KEY not found`**

```bash
export OPENAI_API_KEY="sk-..."
```

**Error: ChromaDB collection not found**

- Run ingestion first: `IngestionPipeline().ingest_directory()`

**Slow searches**

- Reduce `n_results`
- Use date filters to narrow search
- Consider upgrading to larger embedding model

**Poor results**

- Adjust `SIMILARITY_WEIGHT` / `RECENCY_WEIGHT` in config
- Increase `CHUNK_SIZE` for more context
- Try different queries (be specific!)

## 🎯 Next Steps

**Phase 3 (JOURNALIST):** Auto-generate daily journals from transcripts
**Phase 4 (PARTNER):** Chat interface for conversational queries

See: `/home/ubuntu/openclaw/skills/memex/second-brain/memex-visual-plan.md` for full roadmap

---

**Built with:**

- ChromaDB (vector database)
- OpenAI Embeddings (text-embedding-3-small)
- LangChain (document processing)
- FastAPI (REST API)
- pytest (testing)

**Status:** ✅ Production-ready for Phase 2
