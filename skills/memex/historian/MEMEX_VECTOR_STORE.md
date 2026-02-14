# MemexVectorStore Documentation

Complete implementation of the vector store system as specified in the ONE-YEAR-ROADMAP-2026.md.

## Overview

MemexVectorStore is a ChromaDB-based vector database for semantic search across Nike's personal memory. It uses OpenAI's text-embedding-3-small model for generating embeddings and supports recency-weighted hybrid ranking.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  MemexVectorStore                       │
├─────────────────────────────────────────────────────────┤
│  Collections:                                           │
│  ├─ transcripts    (speaker-level segments)            │
│  ├─ journals       (paragraph-level chunks)            │
│  ├─ emails         (message-level)                     │
│  ├─ documents      (chunk-level)                       │
│  └─ conversations  (message-level)                     │
├─────────────────────────────────────────────────────────┤
│  ChromaDB (Persistent Storage)                         │
│  └─ HNSW Index (Cosine Distance)                       │
├─────────────────────────────────────────────────────────┤
│  OpenAI Embeddings API                                 │
│  └─ text-embedding-3-small (1536 dims)                 │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Hierarchical Collections

Different content types are stored in separate collections with appropriate chunking strategies:

- **Transcripts**: Chunked at speaker turn level for speaker-specific retrieval
- **Journals**: Chunked at paragraph level for fine-grained retrieval
- **Emails**: Stored at message level with sender/subject metadata
- **Documents**: Chunked at configurable size for large files
- **Conversations**: Stored at message level for chat history

### 2. Recency-Weighted Search

Search results are ranked using a hybrid score that combines semantic similarity with recency:

```python
final_score = (1 - recency_weight) * similarity + recency_weight * recency_score
```

Where:

- `similarity`: Cosine similarity (0-1)
- `recency_score`: Exponential decay score = exp(-days_old / 30)
- `recency_weight`: Configurable weight (default: 0.3)

**Recency Score Examples:**

- Today: 1.0
- 7 days ago: 0.79
- 30 days ago: 0.37
- 90 days ago: 0.05

### 3. Batch Embedding Optimization

Embeddings are generated in batches to minimize API calls:

```python
# Batch size of 100 (OpenAI limit)
embeddings = await store.embed_batch(texts, batch_size=100)
```

### 4. LLM Context Window

Automatically constructs context for LLM prompts with token budget management:

```python
context = await store.get_context_window(
    query="search functionality",
    max_tokens=4000
)
```

## Installation

### Dependencies

```bash
pip install chromadb openai numpy python-dotenv
```

### Environment Setup

Create a `.env` file with your OpenAI API key:

```bash
OPENAI_API_KEY=sk-...
```

## Usage

### Basic Initialization

```python
from memex.historian import MemexVectorStore

store = MemexVectorStore(
    persist_directory="./data/chromadb",
    embedding_model="text-embedding-3-small"
)
```

### Adding Transcript Segments

```python
from memex.historian import TranscriptSegment

segments = [
    TranscriptSegment(
        text="Discussion about project timeline.",
        speaker="Alice",
        start_time_ms=0,
        end_time_ms=3000
    ),
    TranscriptSegment(
        text="We should aim for Q2 launch.",
        speaker="Bob",
        start_time_ms=3000,
        end_time_ms=6000
    ),
]

await store.add_transcript(
    transcript_id="meeting_2026_02_03",
    segments=segments,
    metadata={
        "date": "2026-02-03",
        "title": "Sprint Planning",
        "duration": 6000,
    }
)
```

### Adding Journal Entries

```python
paragraphs = [
    "Today I learned about vector databases.",
    "ChromaDB is fast and easy to use.",
    "Looking forward to building the search feature.",
]

await store.add_journal_entry(
    journal_id="journal_2026_02_03",
    date="2026-02-03",
    paragraphs=paragraphs,
    metadata={"mood": "productive", "tags": ["learning"]}
)
```

### Semantic Search

```python
results = await store.search(
    query="project timeline discussion",
    collections=["transcripts", "journals"],  # Optional: limit to specific collections
    n_results=10,
    where={"date": {"$gte": "2026-02-01"}},  # Optional: metadata filter
    recency_weight=0.3  # 30% recency, 70% similarity
)

for result in results:
    print(f"Score: {result.final_score:.3f}")
    print(f"Collection: {result.collection}")
    print(f"Content: {result.content}")
    print(f"Metadata: {result.metadata}")
```

### Getting Context for LLM Prompts

```python
context = await store.get_context_window(
    query="What did we discuss about timelines?",
    max_tokens=4000,
    collections=["transcripts", "journals"]
)

# Use in LLM prompt
prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: What did we discuss about timelines?
"""
```

### Statistics and Monitoring

```python
stats = store.get_stats()
for collection_name, collection_stats in stats.items():
    print(f"{collection_name}: {collection_stats['count']} documents")
```

## Data Models

### TranscriptSegment

```python
@dataclass
class TranscriptSegment:
    text: str
    speaker: str
    start_time_ms: int
    end_time_ms: int

    @property
    def duration_ms(self) -> int:
        return self.end_time_ms - self.start_time_ms
```

### SearchResult

```python
@dataclass
class SearchResult:
    content: str
    collection: str
    similarity: float          # Cosine similarity (0-1)
    recency_score: float      # Exponential decay (0-1)
    final_score: float        # Combined weighted score
    metadata: Dict[str, Any]

    @property
    def date(self) -> Optional[str]:
        return self.metadata.get("date")

    @property
    def title(self) -> Optional[str]:
        return self.metadata.get("title")
```

### EmbeddingResult

```python
@dataclass
class EmbeddingResult:
    embedding: list[float]
    model: str
    dimensions: int
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[float] = None

    def estimate_cost(self) -> float:
        # text-embedding-3-small: $0.00002 per 1K tokens
        if self.model == "text-embedding-3-small" and self.tokens_used:
            return (self.tokens_used / 1000) * 0.00002
        return 0.0
```

## Performance Considerations

### Embedding Costs

Using `text-embedding-3-small`:

- Cost: $0.00002 per 1K tokens (~$0.02 per 1M tokens)
- Dimensions: 1536
- Speed: ~1000 tokens/second

**Example Costs:**

- 100 meeting transcripts (300K tokens): ~$0.006
- 365 daily journals (200K tokens): ~$0.004
- 1000 emails (500K tokens): ~$0.01

### Query Performance

ChromaDB uses HNSW (Hierarchical Navigable Small World) index:

- Query latency: <100ms for collections up to 100K documents
- Scalable to millions of vectors
- Persistent storage with fast cold-start

### Batch Optimization

Always use batch embedding for multiple texts:

```python
# Good: Batch embedding
embeddings = await store.embed_batch(texts)  # 1 API call

# Bad: Individual embedding
embeddings = [await store.embed_text(t) for t in texts]  # N API calls
```

## Advanced Features

### Metadata Filtering

ChromaDB supports powerful metadata filters:

```python
# Date range
results = await store.search(
    query="search term",
    where={"date": {"$gte": "2026-01-01", "$lte": "2026-01-31"}}
)

# Speaker filter
results = await store.search(
    query="search term",
    where={"speaker": "Alice"}
)

# Multiple conditions
results = await store.search(
    query="search term",
    where={
        "$and": [
            {"date": {"$gte": "2026-01-01"}},
            {"speaker": {"$in": ["Alice", "Bob"]}}
        ]
    }
)
```

### Custom Recency Weighting

Adjust recency weight based on use case:

```python
# Mostly semantic (recent news search)
results = await store.search(query, recency_weight=0.1)  # 10% recency

# Balanced (general search)
results = await store.search(query, recency_weight=0.3)  # 30% recency (default)

# Mostly recent (activity feed)
results = await store.search(query, recency_weight=0.7)  # 70% recency
```

### Collection Management

```python
# Reset a specific collection
store.reset_collection("transcripts")

# Reset all collections (DANGER!)
store.reset_all()
```

## File Structure

```
memex/historian/
├── __init__.py              # Package exports
├── models.py                # Data models (TranscriptSegment, SearchResult, etc.)
├── vector_store.py          # MemexVectorStore implementation
├── vector_store_old.py      # Legacy VectorStore (backup)
├── embeddings.py            # EmbeddingsManager (local sentence-transformers)
├── config.py                # Configuration
├── example_usage.py         # Usage examples
└── MEMEX_VECTOR_STORE.md    # This documentation
```

## Testing

Run the example script:

```bash
cd /Users/arvindsarin/Cursor/Claude-2026/clawd/memex/historian
python example_usage.py
```

Expected output:

```
=== MemexVectorStore Example Usage ===

1. Adding transcript segments...
   Added 3 segments

2. Adding journal entry...
   Added 3 paragraphs

3. Searching for 'vector database'...
   Result 1:
   Collection: journals
   Similarity: 0.892
   Recency: 0.788
   Final Score: 0.861
   ...
```

## Migration from Old VectorStore

If you have existing data in the old `VectorStore`:

1. The old implementation is backed up as `vector_store_old.py`
2. MemexVectorStore uses the same ChromaDB backend
3. Collections are compatible if using the same embedding model
4. Update imports: `from .vector_store import MemexVectorStore`

## Troubleshooting

### "OpenAI API key not found"

Set the `OPENAI_API_KEY` environment variable:

```bash
export OPENAI_API_KEY=sk-...
```

### "Collection already exists"

MemexVectorStore uses `get_or_create_collection`, so this should not happen. If it does, reset the collection:

```python
store.reset_collection("collection_name")
```

### Slow embedding performance

- Use batch embedding: `embed_batch()` instead of `embed_text()` in loops
- Increase batch size up to 100 (OpenAI limit)
- Consider caching embeddings for frequently used texts

## Future Enhancements

Potential improvements from the roadmap:

1. **Deduplication**: Merge adjacent transcript segments from same speaker
2. **Automatic chunking**: Smart document chunking based on semantic boundaries
3. **Multi-modal**: Support for image and audio embeddings
4. **Caching**: Local cache for frequently accessed embeddings
5. **Async optimization**: Parallel embedding generation for faster batch processing

## References

- [ONE-YEAR-ROADMAP-2026.md](../../plans/ONE-YEAR-ROADMAP-2026.md) (lines 516-887)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
