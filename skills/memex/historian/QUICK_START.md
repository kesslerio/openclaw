# MemexVectorStore Quick Start

## 30-Second Setup

```bash
# 1. Install dependencies
pip install chromadb openai numpy

# 2. Set API key
export OPENAI_API_KEY=sk-...

# 3. Run example
python /Users/arvindsarin/Cursor/Claude-2026/clawd/memex/historian/example_usage.py
```

## Basic Usage (Copy-Paste Ready)

```python
import asyncio
from memex.historian import MemexVectorStore, TranscriptSegment

async def main():
    # Initialize
    store = MemexVectorStore()

    # Add transcript
    segments = [
        TranscriptSegment(
            text="We discussed the new feature.",
            speaker="Alice",
            start_time_ms=0,
            end_time_ms=3000
        )
    ]
    await store.add_transcript(
        transcript_id="meeting_001",
        segments=segments,
        metadata={"date": "2026-02-03", "title": "Planning"}
    )

    # Add journal
    await store.add_journal_entry(
        journal_id="journal_001",
        date="2026-02-03",
        paragraphs=["Today I learned about vector search."]
    )

    # Search
    results = await store.search(
        query="new feature discussion",
        n_results=5,
        recency_weight=0.3  # 30% recency, 70% similarity
    )

    for r in results:
        print(f"Score: {r.final_score:.3f} | {r.content[:80]}")

    # Get LLM context
    context = await store.get_context_window(
        query="what did we discuss?",
        max_tokens=4000
    )
    print(f"\nContext for LLM:\n{context}")

asyncio.run(main())
```

## Recency Weighting Cheat Sheet

```python
# Pure semantic search
results = await store.search(query, recency_weight=0.0)

# Balanced (DEFAULT)
results = await store.search(query, recency_weight=0.3)

# Favor recent content
results = await store.search(query, recency_weight=0.7)

# Pure recency (newest first)
results = await store.search(query, recency_weight=1.0)
```

## Recency Score Reference

| Time Ago | Score |
| -------- | ----- |
| Today    | 1.00  |
| 7 days   | 0.79  |
| 14 days  | 0.62  |
| 30 days  | 0.37  |
| 60 days  | 0.14  |
| 90 days  | 0.05  |

Formula: `exp(-days_old / 30)`

## Metadata Filtering

```python
# Date range
results = await store.search(
    query="search term",
    where={"date": {"$gte": "2026-02-01"}}
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

## Common Patterns

### Pattern 1: Recent Meetings Search

```python
from datetime import datetime, timedelta

week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

results = await store.search(
    query="project timeline",
    collections=["transcripts"],
    where={"date": {"$gte": week_ago}},
    recency_weight=0.5
)
```

### Pattern 2: Journal Memory Lookup

```python
results = await store.search(
    query="what did I learn about databases?",
    collections=["journals"],
    n_results=10,
    recency_weight=0.3
)
```

### Pattern 3: Build LLM Context

```python
context = await store.get_context_window(
    query="summarize my week",
    max_tokens=8000,  # Claude's context window
    collections=["transcripts", "journals", "emails"]
)

prompt = f"""Based on this context, summarize the key events:

{context}

Please provide a brief summary."""
```

## Cost Estimation

```python
# text-embedding-3-small: $0.00002 per 1K tokens

# Examples:
# - 1 hour meeting (~10K tokens): $0.0002
# - Daily journal (~500 tokens): $0.00001
# - 100 emails (~50K tokens): $0.001

# Monthly estimate for heavy usage:
# - 20 meetings: $0.004
# - 30 journals: $0.0003
# - 500 emails: $0.01
# Total: ~$0.015/month
```

## File Locations

```
/Users/arvindsarin/Cursor/Claude-2026/clawd/memex/historian/
├── vector_store.py           # Main implementation
├── models.py                 # Data models
├── example_usage.py          # Full examples
├── test_memex_vector_store.py # Unit tests
├── MEMEX_VECTOR_STORE.md     # Complete docs
└── QUICK_START.md            # This file
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'openai'"**

```bash
pip install openai
```

**"OpenAI API key not found"**

```bash
export OPENAI_API_KEY=sk-...
# Or add to .env file
```

**"Collection already exists"**

```python
store.reset_collection("collection_name")
```

**Slow performance?**

- Use `embed_batch()` instead of loops
- Increase batch size (up to 100)
- Check network latency to OpenAI API

## Next Steps

1. Read full docs: `MEMEX_VECTOR_STORE.md`
2. Run example: `python example_usage.py`
3. Run tests: `pytest test_memex_vector_store.py -v`
4. Integrate into your workflow

## Key Features

- ✅ ChromaDB persistent storage
- ✅ OpenAI embeddings (1536 dims)
- ✅ 5 collections (transcripts, journals, emails, documents, conversations)
- ✅ Recency-weighted hybrid search
- ✅ Metadata filtering
- ✅ Batch optimization
- ✅ LLM context generation
- ✅ Token budget management
- ✅ Type hints and async/await
- ✅ Comprehensive tests

## Support

For issues, check:

1. `IMPLEMENTATION_SUMMARY.md` - What was built
2. `MEMEX_VECTOR_STORE.md` - Complete documentation
3. `test_memex_vector_store.py` - Working examples
