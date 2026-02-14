"""
Unit tests for MemexVectorStore

Tests the complete implementation including:
- Collection initialization
- Embedding generation
- Transcript and journal ingestion
- Semantic search with recency weighting
- Context window generation
"""

import pytest
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

from vector_store import MemexVectorStore
from models import TranscriptSegment, SearchResult


@pytest.fixture
def temp_store():
    """Create a temporary vector store for testing."""
    temp_dir = tempfile.mkdtemp()
    store = MemexVectorStore(persist_directory=temp_dir)
    yield store
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_initialization(temp_store):
    """Test that MemexVectorStore initializes correctly."""
    assert temp_store.client is not None
    assert temp_store.openai is not None
    assert len(temp_store.collections) == 5
    assert "transcripts" in temp_store.collections
    assert "journals" in temp_store.collections


@pytest.mark.asyncio
async def test_embed_text(temp_store):
    """Test single text embedding."""
    text = "This is a test sentence."
    embedding = await temp_store.embed_text(text)

    assert isinstance(embedding, list)
    assert len(embedding) == 1536  # text-embedding-3-small dimensions
    assert all(isinstance(x, float) for x in embedding)


@pytest.mark.asyncio
async def test_embed_batch(temp_store):
    """Test batch embedding."""
    texts = [
        "First sentence.",
        "Second sentence.",
        "Third sentence.",
    ]
    embeddings = await temp_store.embed_batch(texts)

    assert len(embeddings) == 3
    assert all(len(emb) == 1536 for emb in embeddings)


@pytest.mark.asyncio
async def test_add_transcript(temp_store):
    """Test adding transcript segments."""
    segments = [
        TranscriptSegment(
            text="Hello, this is the first segment.",
            speaker="Alice",
            start_time_ms=0,
            end_time_ms=3000
        ),
        TranscriptSegment(
            text="This is the second segment.",
            speaker="Bob",
            start_time_ms=3000,
            end_time_ms=6000
        ),
    ]

    num_added = await temp_store.add_transcript(
        transcript_id="test_transcript_1",
        segments=segments,
        metadata={
            "date": "2026-02-03",
            "title": "Test Meeting",
        }
    )

    assert num_added == 2
    stats = temp_store.get_stats()
    assert stats["transcripts"]["count"] == 2


@pytest.mark.asyncio
async def test_add_journal_entry(temp_store):
    """Test adding journal entry."""
    paragraphs = [
        "Today was a productive day.",
        "I learned about vector databases.",
        "Tomorrow I'll work on the implementation.",
    ]

    num_added = await temp_store.add_journal_entry(
        journal_id="journal_test_1",
        date="2026-02-03",
        paragraphs=paragraphs,
        metadata={"mood": "productive"}
    )

    assert num_added == 3
    stats = temp_store.get_stats()
    assert stats["journals"]["count"] == 3


@pytest.mark.asyncio
async def test_search_semantic_similarity(temp_store):
    """Test semantic search returns relevant results."""
    # Add some test data
    segments = [
        TranscriptSegment(
            text="We need to implement vector search for better results.",
            speaker="Alice",
            start_time_ms=0,
            end_time_ms=3000
        ),
        TranscriptSegment(
            text="I agree, semantic search is much better than keyword search.",
            speaker="Bob",
            start_time_ms=3000,
            end_time_ms=6000
        ),
        TranscriptSegment(
            text="Let's go out for lunch today.",
            speaker="Alice",
            start_time_ms=6000,
            end_time_ms=9000
        ),
    ]

    await temp_store.add_transcript(
        transcript_id="test_search_1",
        segments=segments,
        metadata={"date": "2026-02-03", "title": "Test"}
    )

    # Search for semantic search topic
    results = await temp_store.search(
        query="vector database search",
        n_results=3,
        recency_weight=0.0  # Pure semantic search
    )

    assert len(results) > 0
    # First two results should be about search, not lunch
    assert "search" in results[0].content.lower() or "vector" in results[0].content.lower()


@pytest.mark.asyncio
async def test_search_recency_weighting(temp_store):
    """Test that recency weighting affects ranking."""
    # Add old journal entry
    old_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    await temp_store.add_journal_entry(
        journal_id="journal_old",
        date=old_date,
        paragraphs=["This is about vector databases."],
        metadata={"age": "old"}
    )

    # Add recent journal entry
    recent_date = datetime.now().strftime("%Y-%m-%d")
    await temp_store.add_journal_entry(
        journal_id="journal_recent",
        date=recent_date,
        paragraphs=["This is also about vector databases."],
        metadata={"age": "recent"}
    )

    # Search with high recency weight
    results = await temp_store.search(
        query="vector databases",
        n_results=2,
        recency_weight=0.7  # 70% recency weight
    )

    # Recent entry should rank higher
    assert len(results) == 2
    assert results[0].metadata.get("age") == "recent"


@pytest.mark.asyncio
async def test_get_context_window(temp_store):
    """Test context window generation."""
    # Add test data
    paragraphs = [
        "Vector databases enable semantic search.",
        "ChromaDB is a great choice for embeddings.",
        "OpenAI provides embedding models.",
    ]

    await temp_store.add_journal_entry(
        journal_id="journal_context",
        date="2026-02-03",
        paragraphs=paragraphs
    )

    # Get context window
    context = await temp_store.get_context_window(
        query="vector databases",
        max_tokens=1000
    )

    assert isinstance(context, str)
    assert len(context) > 0
    assert "vector" in context.lower() or "database" in context.lower()


@pytest.mark.asyncio
async def test_search_with_metadata_filter(temp_store):
    """Test metadata filtering in search."""
    # Add entries with different dates
    await temp_store.add_journal_entry(
        journal_id="journal_jan",
        date="2026-01-15",
        paragraphs=["January entry about databases."]
    )

    await temp_store.add_journal_entry(
        journal_id="journal_feb",
        date="2026-02-03",
        paragraphs=["February entry about databases."]
    )

    # Search only February entries
    results = await temp_store.search(
        query="databases",
        where={"date": {"$gte": "2026-02-01"}},
        n_results=10
    )

    # Should only return February entry
    assert len(results) == 1
    assert results[0].metadata.get("date") == "2026-02-03"


@pytest.mark.asyncio
async def test_calculate_recency_score(temp_store):
    """Test recency score calculation."""
    # Today
    today = datetime.now().strftime("%Y-%m-%d")
    score_today = temp_store._calculate_recency_score(today)
    assert score_today > 0.99  # Should be ~1.0

    # 30 days ago
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    score_30 = temp_store._calculate_recency_score(thirty_days_ago)
    assert 0.35 < score_30 < 0.40  # Should be ~0.37 (exp(-1))

    # Invalid date
    score_invalid = temp_store._calculate_recency_score("invalid-date")
    assert score_invalid == 0.5  # Default neutral score


def test_get_stats(temp_store):
    """Test getting statistics."""
    stats = temp_store.get_stats()

    assert isinstance(stats, dict)
    assert "transcripts" in stats
    assert "journals" in stats
    assert "count" in stats["transcripts"]


@pytest.mark.asyncio
async def test_search_result_model():
    """Test SearchResult model."""
    result = SearchResult(
        content="Test content",
        collection="transcripts",
        similarity=0.85,
        recency_score=0.75,
        final_score=0.82,
        metadata={"date": "2026-02-03", "title": "Test"}
    )

    assert result.date == "2026-02-03"
    assert result.title == "Test"
    assert "similarity=0.850" in str(result)

    result_dict = result.to_dict()
    assert result_dict["similarity"] == 0.85


def test_transcript_segment_model():
    """Test TranscriptSegment model."""
    segment = TranscriptSegment(
        text="Test segment",
        speaker="Alice",
        start_time_ms=1000,
        end_time_ms=4000
    )

    assert segment.duration_ms == 3000
    segment_dict = segment.to_dict()
    assert segment_dict["duration_ms"] == 3000


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
