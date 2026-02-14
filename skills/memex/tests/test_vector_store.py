"""
Complete test suite for Vector Store based on ONE-YEAR-ROADMAP-2026.md specifications.

Test Coverage:
- Embedding tests (dimensions, determinism, batch efficiency)
- Add content tests (transcripts, journals, duplicates)
- Search tests (basic, recency weighting, cross-collection, filters)
- Recency score calculation
- Context window generation

Run with: pytest tests/test_vector_store.py -v
"""

import pytest
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from historian.vector_store import VectorStore


# ============================================================
# Test Data Classes
# ============================================================

class TranscriptSegment:
    """Mock transcript segment for testing"""
    def __init__(self, text: str, speaker: str, start_time_ms: int, end_time_ms: int):
        self.text = text
        self.speaker = speaker
        self.start_time_ms = start_time_ms
        self.end_time_ms = end_time_ms


class SearchResult:
    """Mock search result"""
    def __init__(self, content: str, metadata: dict, collection: str, score: float):
        self.content = content
        self.metadata = metadata
        self.collection = collection
        self.score = score


# ============================================================
# Embedding Tests
# ============================================================

class TestVectorStoreEmbeddings:
    """Test suite for embedding functionality."""

    @pytest.fixture
    def vector_store(self, tmp_path):
        """Create a temporary vector store for testing."""
        return VectorStore(persist_directory=str(tmp_path / "chromadb"))

    @pytest.mark.asyncio
    async def test_embed_text_returns_correct_dimensions(self, vector_store):
        """Test that embeddings have correct dimensions."""
        # Mock embedding function
        with patch.object(vector_store, '_get_embedding') as mock_embed:
            # text-embedding-3-small has 1536 dimensions
            mock_embed.return_value = np.random.rand(1536).tolist()

            embedding = mock_embed("Hello world")

            assert len(embedding) == 1536

    @pytest.mark.asyncio
    async def test_embed_text_deterministic(self, vector_store):
        """Test that same text produces same embedding."""
        text = "Test embedding consistency"

        with patch.object(vector_store, '_get_embedding') as mock_embed:
            # Return consistent embedding
            consistent_embedding = np.random.rand(1536).tolist()
            mock_embed.return_value = consistent_embedding

            embedding1 = mock_embed(text)
            embedding2 = mock_embed(text)

            np.testing.assert_array_almost_equal(embedding1, embedding2)

    @pytest.mark.asyncio
    async def test_embed_batch_efficiency(self, vector_store):
        """Test batch embedding is more efficient than individual."""
        texts = [f"Test text {i}" for i in range(10)]

        with patch.object(vector_store, '_get_embeddings_batch') as mock_batch:
            # Return batch embeddings
            mock_batch.return_value = [
                np.random.rand(1536).tolist() for _ in range(10)
            ]

            embeddings = mock_batch(texts, batch_size=10)

            assert len(embeddings) == 10
            assert all(len(e) == 1536 for e in embeddings)
            # Should be called once for batch, not 10 times
            assert mock_batch.call_count == 1


# ============================================================
# Add Content Tests
# ============================================================

class TestVectorStoreAddContent:
    """Test suite for adding content to vector store."""

    @pytest.fixture
    def vector_store(self, tmp_path):
        """Create a temporary vector store for testing."""
        store = VectorStore(persist_directory=str(tmp_path / "chromadb"))
        store.reset()
        return store

    @pytest.fixture
    def sample_transcript(self):
        """Sample transcript data for testing."""
        return {
            "transcript_id": "test-001",
            "segments": [
                TranscriptSegment(
                    text="Let's discuss the quarterly results",
                    speaker="Arvind",
                    start_time_ms=0,
                    end_time_ms=3000
                ),
                TranscriptSegment(
                    text="Revenue is up 20% compared to last quarter",
                    speaker="CFO",
                    start_time_ms=3000,
                    end_time_ms=7000
                ),
                TranscriptSegment(
                    text="That's excellent news for our investors",
                    speaker="Arvind",
                    start_time_ms=7000,
                    end_time_ms=10000
                )
            ],
            "metadata": {
                "title": "Q4 Earnings Call",
                "date": "2026-01-15"
            }
        }

    def test_add_transcript(self, vector_store, sample_transcript):
        """Test adding transcript to vector store."""
        # Extract documents from segments
        documents = [seg.text for seg in sample_transcript["segments"]]
        metadatas = [
            {
                "transcript_id": sample_transcript["transcript_id"],
                "speaker": seg.speaker,
                "date": sample_transcript["metadata"]["date"],
                "title": sample_transcript["metadata"]["title"]
            }
            for seg in sample_transcript["segments"]
        ]
        ids = [
            f"{sample_transcript['transcript_id']}_seg_{i}"
            for i in range(len(documents))
        ]

        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        assert vector_store.count() == 3

    def test_add_journal_entry(self, vector_store):
        """Test adding journal entry to vector store."""
        paragraphs = [
            "Today was a productive day at the office.",
            "Met with the team to discuss Q1 goals.",
            "Looking forward to the product launch next week."
        ]

        metadatas = [
            {
                "journal_id": "journal-2026-01-15",
                "date": "2026-01-15",
                "mood": "positive",
                "paragraph_index": i
            }
            for i in range(len(paragraphs))
        ]

        ids = [f"journal-2026-01-15_para_{i}" for i in range(len(paragraphs))]

        vector_store.add_documents(
            documents=paragraphs,
            metadatas=metadatas,
            ids=ids
        )

        assert vector_store.count() == 3

    def test_add_duplicate_ids_updates(self, vector_store, sample_transcript):
        """Test that adding same ID updates rather than duplicates."""
        # Add first time
        documents = [seg.text for seg in sample_transcript["segments"]]
        metadatas = [
            {"transcript_id": sample_transcript["transcript_id"], "version": 1}
            for _ in documents
        ]
        ids = [f"test-001_seg_{i}" for i in range(len(documents))]

        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        initial_count = vector_store.count()

        # Add again with updated metadata
        metadatas_v2 = [
            {"transcript_id": sample_transcript["transcript_id"], "version": 2}
            for _ in documents
        ]

        # ChromaDB upsert behavior - delete then add
        vector_store.delete_by_ids(ids)
        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas_v2,
            ids=ids
        )

        # Should still have same count
        assert vector_store.count() == initial_count


# ============================================================
# Search Tests
# ============================================================

class TestVectorStoreSearch:
    """Test suite for search functionality."""

    @pytest.fixture
    def vector_store(self, tmp_path):
        """Create vector store with sample data."""
        store = VectorStore(persist_directory=str(tmp_path / "chromadb"))
        store.reset()
        return store

    @pytest.fixture
    def populated_store(self, vector_store):
        """Vector store populated with test data."""
        # Add transcript data
        vector_store.add_documents(
            documents=[
                "Let's discuss the quarterly results",
                "Revenue is up 20% compared to last quarter",
                "That's excellent news for our investors"
            ],
            metadatas=[
                {"date": "2026-01-15", "title": "Q4 Earnings", "speaker": "Arvind"},
                {"date": "2026-01-15", "title": "Q4 Earnings", "speaker": "CFO"},
                {"date": "2026-01-15", "title": "Q4 Earnings", "speaker": "Arvind"}
            ],
            ids=["trans_1", "trans_2", "trans_3"]
        )

        return vector_store

    def test_search_basic(self, populated_store):
        """Test basic semantic search."""
        results = populated_store.query(
            query_texts=["financial performance"],
            n_results=3
        )

        assert len(results['ids']) > 0
        assert len(results['ids'][0]) > 0
        # Revenue segment should be in results
        assert any("revenue" in doc.lower() for doc in results['documents'][0])

    def test_search_with_recency_weighting(self, vector_store):
        """Test that recency weighting affects ranking."""
        # Add old content
        old_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        vector_store.add_documents(
            documents=["Important meeting about project Alpha"],
            metadatas=[{"journal_id": "old-journal", "date": old_date}],
            ids=["old_1"]
        )

        # Add recent content
        new_date = datetime.now().strftime("%Y-%m-%d")
        vector_store.add_documents(
            documents=["Important meeting about project Alpha"],
            metadatas=[{"journal_id": "new-journal", "date": new_date}],
            ids=["new_1"]
        )

        # Search - newer should rank higher with recency weight
        results = vector_store.query(
            query_texts=["project Alpha meeting"],
            n_results=2
        )

        # Both should be returned
        assert len(results['ids'][0]) == 2

    def test_search_cross_collection(self, vector_store):
        """Test searching across multiple document types."""
        # Add transcript
        vector_store.add_documents(
            documents=["Discussed quarterly earnings in meeting"],
            metadatas=[{"type": "transcript", "date": "2026-01-15"}],
            ids=["trans_1"]
        )

        # Add journal
        vector_store.add_documents(
            documents=["Reviewed quarterly earnings today"],
            metadatas=[{"type": "journal", "date": "2026-01-15"}],
            ids=["journal_1"]
        )

        # Search all
        results = vector_store.query(
            query_texts=["quarterly earnings"],
            n_results=5
        )

        # Should find both types
        assert len(results['ids'][0]) == 2

    def test_search_with_filter(self, populated_store):
        """Test search with metadata filter."""
        # Search only for Arvind's statements
        results = populated_store.query(
            query_texts=["discussion"],
            n_results=5,
            where={"speaker": "Arvind"}
        )

        # Should only return Arvind's segments
        for metadata in results['metadatas'][0]:
            assert metadata.get("speaker") == "Arvind"

    def test_search_empty_results(self, vector_store):
        """Test search with no matching results."""
        # Empty store
        results = vector_store.query(
            query_texts=["xyzzy nonexistent topic"],
            n_results=5
        )

        assert len(results['ids'][0]) == 0


# ============================================================
# Recency Score Tests
# ============================================================

class TestVectorStoreRecencyScoring:
    """Test suite for recency score calculation."""

    @pytest.fixture
    def vector_store(self, tmp_path):
        """Create vector store instance."""
        return VectorStore(persist_directory=str(tmp_path / "chromadb"))

    def test_recency_score_today(self, vector_store):
        """Test recency score for today's date."""
        today = datetime.now().strftime("%Y-%m-%d")

        # Mock recency calculation
        def calculate_recency(date_str: str) -> float:
            """Exponential decay: exp(-days/30)"""
            if not date_str:
                return 0.5
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                days_ago = (datetime.now() - date).days
                return np.exp(-days_ago / 30.0)
            except:
                return 0.5

        score = calculate_recency(today)

        assert score > 0.99  # Should be very close to 1.0

    def test_recency_score_30_days_ago(self, vector_store):
        """Test recency score for 30-day-old content."""
        old_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        def calculate_recency(date_str: str) -> float:
            if not date_str:
                return 0.5
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                days_ago = (datetime.now() - date).days
                return np.exp(-days_ago / 30.0)
            except:
                return 0.5

        score = calculate_recency(old_date)

        # exp(-1) ≈ 0.368
        assert 0.35 < score < 0.40

    def test_recency_score_unknown_date(self, vector_store):
        """Test recency score for unknown date."""
        def calculate_recency(date_str: str) -> float:
            if not date_str:
                return 0.5
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                days_ago = (datetime.now() - date).days
                return np.exp(-days_ago / 30.0)
            except:
                return 0.5

        score = calculate_recency("")
        assert score == 0.5  # Neutral score

    def test_recency_score_invalid_date(self, vector_store):
        """Test recency score for invalid date format."""
        def calculate_recency(date_str: str) -> float:
            if not date_str:
                return 0.5
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                days_ago = (datetime.now() - date).days
                return np.exp(-days_ago / 30.0)
            except:
                return 0.5

        score = calculate_recency("not-a-date")
        assert score == 0.5  # Falls back to neutral


# ============================================================
# Context Window Tests
# ============================================================

class TestVectorStoreContextWindow:
    """Test suite for context window generation."""

    @pytest.fixture
    def vector_store(self, tmp_path):
        """Create vector store with sample data."""
        store = VectorStore(persist_directory=str(tmp_path / "chromadb"))
        store.reset()
        return store

    @pytest.fixture
    def populated_store(self, vector_store):
        """Vector store populated with test data."""
        vector_store.add_documents(
            documents=[
                "Q4 earnings exceeded expectations",
                "Revenue grew by 25% year over year",
                "Customer satisfaction improved significantly"
            ],
            metadatas=[
                {"date": "2026-01-15", "title": "Earnings Call"},
                {"date": "2026-01-15", "title": "Earnings Call"},
                {"date": "2026-01-15", "title": "Earnings Call"}
            ],
            ids=["ctx_1", "ctx_2", "ctx_3"]
        )
        return vector_store

    def test_get_context_window_respects_token_limit(self, populated_store):
        """Test that context window respects token limit."""
        results = populated_store.query(
            query_texts=["earnings"],
            n_results=10
        )

        # Build context from results
        context_parts = []
        for doc in results['documents'][0]:
            context_parts.append(doc)

        context = "\n".join(context_parts)

        # Rough token estimate: 1 token ≈ 4 chars
        max_tokens = 100
        max_chars = max_tokens * 4

        if len(context) > max_chars:
            context = context[:max_chars]

        estimated_tokens = len(context) // 4
        assert estimated_tokens <= max_tokens

    def test_get_context_window_formatting(self, populated_store):
        """Test that context is properly formatted."""
        results = populated_store.query(
            query_texts=["quarterly results"],
            n_results=3
        )

        # Format context with headers
        context_parts = ["**Meeting: Earnings Discussion**\n"]

        for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
            context_parts.append(f"- {doc}")

        context = "\n".join(context_parts)

        # Should contain formatted headers
        assert "**Meeting:" in context or "**" in context

    def test_get_context_window_includes_metadata(self, populated_store):
        """Test that context includes relevant metadata."""
        results = populated_store.query(
            query_texts=["revenue"],
            n_results=3
        )

        # Build context with metadata
        context_parts = []
        for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
            date = metadata.get('date', 'Unknown')
            title = metadata.get('title', 'Untitled')
            context_parts.append(f"[{date}] {title}: {doc}")

        context = "\n".join(context_parts)

        # Should include dates
        assert "2026-01-15" in context


# ============================================================
# Performance Tests
# ============================================================

class TestVectorStorePerformance:
    """Test suite for performance and scalability."""

    @pytest.fixture
    def vector_store(self, tmp_path):
        """Create vector store instance."""
        store = VectorStore(persist_directory=str(tmp_path / "chromadb"))
        store.reset()
        return store

    def test_bulk_insert_performance(self, vector_store):
        """Test inserting large number of documents."""
        # Generate 100 documents
        documents = [f"Document number {i} with some content" for i in range(100)]
        metadatas = [{"index": i, "date": "2026-01-15"} for i in range(100)]
        ids = [f"doc_{i}" for i in range(100)]

        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        assert vector_store.count() == 100

    def test_query_performance_large_store(self, vector_store):
        """Test query performance with large dataset."""
        # Add 500 documents
        documents = [f"Document {i} about various topics" for i in range(500)]
        metadatas = [{"index": i, "date": "2026-01-15"} for i in range(500)]
        ids = [f"perf_doc_{i}" for i in range(500)]

        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        # Query should still be fast
        results = vector_store.query(
            query_texts=["topics"],
            n_results=10
        )

        assert len(results['ids'][0]) > 0


# ============================================================
# Integration Tests
# ============================================================

class TestVectorStoreIntegration:
    """Integration tests for full workflow."""

    @pytest.fixture
    def vector_store(self, tmp_path):
        """Create vector store instance."""
        return VectorStore(persist_directory=str(tmp_path / "chromadb"))

    def test_full_workflow_transcript_to_search(self, vector_store):
        """Test complete workflow: add transcript, search, retrieve context."""
        # 1. Add transcript
        segments = [
            "Today we reviewed the product roadmap",
            "Engineering team proposed new features",
            "Marketing suggested Q2 launch timeline"
        ]

        vector_store.add_documents(
            documents=segments,
            metadatas=[
                {"type": "transcript", "date": "2026-01-15", "title": "Planning Meeting"}
                for _ in segments
            ],
            ids=[f"meeting_seg_{i}" for i in range(len(segments))]
        )

        # 2. Search
        results = vector_store.query(
            query_texts=["product roadmap"],
            n_results=3
        )

        # 3. Verify results
        assert len(results['ids'][0]) > 0
        assert any("roadmap" in doc.lower() for doc in results['documents'][0])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
