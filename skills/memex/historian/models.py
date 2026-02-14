"""
Memex HISTORIAN - Data Models
Type definitions for vector store operations
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class TranscriptSegment:
    """
    Represents a single segment (speaker turn) in a transcript.

    Used for chunking transcripts at the speaker level to enable
    speaker-specific retrieval and better context preservation.
    """
    text: str
    speaker: str
    start_time_ms: int
    end_time_ms: int

    @property
    def duration_ms(self) -> int:
        """Duration of the segment in milliseconds."""
        return self.end_time_ms - self.start_time_ms

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "text": self.text,
            "speaker": self.speaker,
            "start_time_ms": self.start_time_ms,
            "end_time_ms": self.end_time_ms,
            "duration_ms": self.duration_ms,
        }


@dataclass
class SearchResult:
    """
    Represents a single search result from the vector store.

    Includes both semantic similarity score and recency-weighted final score
    to enable hybrid ranking strategies.
    """
    content: str
    collection: str
    similarity: float  # Cosine similarity (0-1)
    recency_score: float  # Recency score with exponential decay (0-1)
    final_score: float  # Combined weighted score
    metadata: Dict[str, Any]

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"SearchResult(collection={self.collection}, "
            f"similarity={self.similarity:.3f}, "
            f"recency={self.recency_score:.3f}, "
            f"final={self.final_score:.3f})"
        )

    @property
    def date(self) -> Optional[str]:
        """Extract date from metadata if available."""
        return self.metadata.get("date")

    @property
    def title(self) -> Optional[str]:
        """Extract title from metadata if available."""
        return self.metadata.get("title")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "collection": self.collection,
            "similarity": self.similarity,
            "recency_score": self.recency_score,
            "final_score": self.final_score,
            "metadata": self.metadata,
        }


@dataclass
class EmbeddingResult:
    """
    Represents the result of an embedding operation.

    Includes timing and token count for cost tracking and performance monitoring.
    """
    embedding: list[float]
    model: str
    dimensions: int
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[float] = None

    def estimate_cost(self) -> float:
        """
        Estimate cost for OpenAI embeddings.

        text-embedding-3-small: $0.00002 per 1K tokens
        """
        if self.model == "text-embedding-3-small" and self.tokens_used:
            return (self.tokens_used / 1000) * 0.00002
        return 0.0


@dataclass
class VectorStoreStats:
    """
    Statistics about the vector store collections.

    Used for monitoring and debugging the memory system.
    """
    collection_name: str
    document_count: int
    embedding_model: str
    embedding_dimensions: int
    created_at: Optional[str] = None
    last_updated: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "collection_name": self.collection_name,
            "document_count": self.document_count,
            "embedding_model": self.embedding_model,
            "embedding_dimensions": self.embedding_dimensions,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
        }
