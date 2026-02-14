"""
Memex HISTORIAN - Vector Store Manager
ChromaDB-based vector database for semantic search across Nike's memory.

Architecture:
- ChromaDB for persistent vector storage
- OpenAI text-embedding-3-small for embeddings
- Hierarchical collections for different content types
- Recency-weighted retrieval
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

import chromadb
from chromadb.config import Settings
import numpy as np
from openai import OpenAI

from .models import TranscriptSegment, SearchResult


logger = logging.getLogger(__name__)


class MemexVectorStore:
    """
    Vector database for semantic search across Nike's memory.

    Collections:
    - transcripts: Meeting transcripts (segment-level)
    - journals: Daily journal entries (paragraph-level)
    - emails: Email content (message-level)
    - documents: Files and documents (chunk-level)
    - conversations: Chat history (message-level)
    """

    def __init__(
        self,
        persist_directory: str = "./data/chromadb",
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        Initialize the vector store.

        Args:
            persist_directory: Path to ChromaDB persistence directory
            embedding_model: OpenAI embedding model to use
        """
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.openai = OpenAI()
        self.embedding_model = embedding_model
        self._init_collections()

        logger.info(f"Initialized MemexVectorStore with model: {embedding_model}")
        logger.info(f"Persist directory: {persist_directory}")

    def _init_collections(self) -> None:
        """Initialize all memory collections with appropriate metadata."""
        collection_configs = {
            "transcripts": {
                "metadata": {"hnsw:space": "cosine"},
                "description": "Meeting transcript segments"
            },
            "journals": {
                "metadata": {"hnsw:space": "cosine"},
                "description": "Daily journal paragraphs"
            },
            "emails": {
                "metadata": {"hnsw:space": "cosine"},
                "description": "Email messages"
            },
            "documents": {
                "metadata": {"hnsw:space": "cosine"},
                "description": "Document chunks"
            },
            "conversations": {
                "metadata": {"hnsw:space": "cosine"},
                "description": "Chat messages"
            }
        }

        self.collections = {}
        for name, config in collection_configs.items():
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata=config["metadata"]
            )
            logger.info(
                f"Collection '{name}': {self.collections[name].count()} documents"
            )

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI.

        Cost: ~$0.00002 per 1K tokens
        Dimensions: 1536

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        try:
            response = await self.openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Batch embed multiple texts efficiently.

        Batching reduces API calls and cost.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch (max 100 for OpenAI)

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = await self.openai.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                embeddings.extend([d.embedding for d in response.data])
                logger.debug(f"Embedded batch {i//batch_size + 1}: {len(batch)} texts")
            except Exception as e:
                logger.error(f"Error in batch embedding: {e}")
                raise

        logger.info(f"Embedded {len(embeddings)} texts in total")
        return embeddings

    async def add_transcript(
        self,
        transcript_id: str,
        segments: List[TranscriptSegment],
        metadata: Dict[str, Any]
    ) -> int:
        """
        Add transcript segments to vector store.

        Chunking strategy:
        - Each segment (speaker turn) is stored separately
        - Metadata includes timestamp, speaker, transcript_id
        - Enables speaker-specific retrieval

        Args:
            transcript_id: Unique identifier for the transcript
            segments: List of transcript segments
            metadata: Additional metadata (date, title, etc.)

        Returns:
            Number of segments added
        """
        if not segments:
            logger.warning(f"No segments provided for transcript {transcript_id}")
            return 0

        texts = [seg.text for seg in segments]
        embeddings = await self.embed_batch(texts)

        ids = [f"{transcript_id}_{i}" for i in range(len(segments))]
        metadatas = [
            {
                "transcript_id": transcript_id,
                "segment_index": i,
                "speaker": seg.speaker,
                "start_time_ms": seg.start_time_ms,
                "end_time_ms": seg.end_time_ms,
                "date": metadata.get("date", ""),
                "title": metadata.get("title", ""),
                **metadata
            }
            for i, seg in enumerate(segments)
        ]

        self.collections["transcripts"].add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

        logger.info(
            f"Added {len(segments)} segments from transcript '{transcript_id}'"
        )
        return len(segments)

    async def add_journal_entry(
        self,
        journal_id: str,
        date: str,
        paragraphs: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add journal entry paragraphs to vector store.

        Chunking strategy:
        - Each paragraph stored separately
        - Enables fine-grained retrieval

        Args:
            journal_id: Unique identifier for the journal entry
            date: Date of the entry (YYYY-MM-DD format)
            paragraphs: List of paragraphs from the entry
            metadata: Additional metadata

        Returns:
            Number of paragraphs added
        """
        if not paragraphs:
            logger.warning(f"No paragraphs provided for journal {journal_id}")
            return 0

        if metadata is None:
            metadata = {}

        embeddings = await self.embed_batch(paragraphs)

        ids = [f"{journal_id}_{i}" for i in range(len(paragraphs))]
        metadatas = [
            {
                "journal_id": journal_id,
                "paragraph_index": i,
                "date": date,
                **metadata
            }
            for i in range(len(paragraphs))
        ]

        self.collections["journals"].add(
            ids=ids,
            embeddings=embeddings,
            documents=paragraphs,
            metadatas=metadatas
        )

        logger.info(
            f"Added {len(paragraphs)} paragraphs from journal '{journal_id}'"
        )
        return len(paragraphs)

    async def search(
        self,
        query: str,
        collections: Optional[List[str]] = None,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        recency_weight: float = 0.3
    ) -> List[SearchResult]:
        """
        Semantic search across memory with recency weighting.

        Algorithm:
        1. Embed query
        2. Search each collection
        3. Combine results
        4. Apply recency weighting
        5. Re-rank by combined score

        Recency weighting formula:
        final_score = (1 - recency_weight) * similarity + recency_weight * recency_score

        Where recency_score = exp(-days_old / 30) for exponential decay

        Args:
            query: Search query text
            collections: List of collections to search (None = all)
            n_results: Number of results to return
            where: Filter criteria (ChromaDB where clause)
            recency_weight: Weight for recency (0-1, default 0.3)

        Returns:
            List of SearchResult objects sorted by combined score
        """
        query_embedding = await self.embed_text(query)

        if collections is None:
            collections = list(self.collections.keys())

        all_results = []

        for collection_name in collections:
            collection = self.collections[collection_name]

            try:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results * 2,  # Fetch more for re-ranking
                    where=where,
                    include=["documents", "metadatas", "distances"]
                )

                for i, doc in enumerate(results["documents"][0]):
                    distance = results["distances"][0][i]
                    similarity = 1 - distance  # Cosine distance to similarity
                    metadata = results["metadatas"][0][i]

                    # Calculate recency score
                    date_str = metadata.get("date", "")
                    recency_score = self._calculate_recency_score(date_str)

                    # Combined score
                    final_score = (
                        (1 - recency_weight) * similarity +
                        recency_weight * recency_score
                    )

                    all_results.append(SearchResult(
                        content=doc,
                        collection=collection_name,
                        similarity=similarity,
                        recency_score=recency_score,
                        final_score=final_score,
                        metadata=metadata
                    ))

                logger.debug(
                    f"Collection '{collection_name}': {len(results['documents'][0])} results"
                )

            except Exception as e:
                logger.error(f"Error searching collection '{collection_name}': {e}")
                continue

        # Sort by final score and return top n
        all_results.sort(key=lambda x: x.final_score, reverse=True)
        logger.info(f"Search completed: {len(all_results)} total results")
        return all_results[:n_results]

    def _calculate_recency_score(self, date_str: str) -> float:
        """
        Calculate recency score with exponential decay.

        Score = exp(-days_old / 30)

        Examples:
        - Today: 1.0
        - 7 days ago: 0.79
        - 30 days ago: 0.37
        - 90 days ago: 0.05

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            Recency score (0-1)
        """
        if not date_str:
            return 0.5  # Unknown date gets neutral score

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            days_old = (datetime.now() - date).days
            return float(np.exp(-days_old / 30))
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid date format '{date_str}': {e}")
            return 0.5

    async def get_context_window(
        self,
        query: str,
        max_tokens: int = 4000,
        collections: Optional[List[str]] = None
    ) -> str:
        """
        Get relevant context for LLM prompt construction.

        Strategy:
        1. Search for relevant content
        2. Deduplicate and merge adjacent segments
        3. Truncate to fit token budget
        4. Format for LLM consumption

        Args:
            query: Search query
            max_tokens: Maximum tokens to include
            collections: Collections to search (None = all)

        Returns:
            Formatted context string for LLM prompt
        """
        results = await self.search(
            query=query,
            collections=collections,
            n_results=20,
            recency_weight=0.3
        )

        # Group by source and format
        context_parts = []
        current_tokens = 0

        for result in results:
            formatted = self._format_result(result)
            tokens = self._estimate_tokens(formatted)

            if current_tokens + tokens > max_tokens:
                break

            context_parts.append(formatted)
            current_tokens += tokens

        logger.info(f"Context window: {len(context_parts)} results, ~{current_tokens} tokens")
        return "\n\n---\n\n".join(context_parts)

    def _format_result(self, result: SearchResult) -> str:
        """
        Format a search result for LLM context.

        Args:
            result: Search result to format

        Returns:
            Formatted string for LLM consumption
        """
        metadata = result.metadata

        if result.collection == "transcripts":
            return f"""**Meeting: {metadata.get('title', 'Unknown')}** ({metadata.get('date', 'Unknown date')})
Speaker: {metadata.get('speaker', 'Unknown')}

{result.content}"""

        elif result.collection == "journals":
            return f"""**Journal Entry** ({metadata.get('date', 'Unknown date')})

{result.content}"""

        elif result.collection == "emails":
            return f"""**Email** ({metadata.get('date', 'Unknown date')})
From: {metadata.get('from', 'Unknown')}
Subject: {metadata.get('subject', 'Unknown')}

{result.content}"""

        else:
            return f"""**{result.collection.title()}** ({metadata.get('date', 'Unknown date')})

{result.content}"""

    def _estimate_tokens(self, text: str) -> int:
        """
        Rough token estimation (4 chars per token).

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored content.

        Returns:
            Dictionary with stats for each collection
        """
        stats = {}
        for name, collection in self.collections.items():
            stats[name] = {
                "count": collection.count(),
                "metadata": collection.metadata
            }
        return stats

    def reset_collection(self, collection_name: str) -> None:
        """
        Reset a specific collection (delete all documents).

        Args:
            collection_name: Name of collection to reset
        """
        if collection_name not in self.collections:
            raise ValueError(f"Unknown collection: {collection_name}")

        logger.warning(f"Resetting collection '{collection_name}' - all data will be lost!")
        self.client.delete_collection(name=collection_name)
        self.collections[collection_name] = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Collection '{collection_name}' reset complete")

    def reset_all(self) -> None:
        """
        ⚠️ DANGER: Reset all collections (delete all documents).
        """
        logger.warning("Resetting ALL collections - all data will be lost!")
        for collection_name in list(self.collections.keys()):
            self.reset_collection(collection_name)
        logger.info("All collections reset complete")
