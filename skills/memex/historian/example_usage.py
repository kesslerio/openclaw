"""
Example usage of MemexVectorStore

Demonstrates:
- Adding transcript segments
- Adding journal entries
- Semantic search with recency weighting
- Getting context windows for LLM prompts
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from vector_store import MemexVectorStore
from models import TranscriptSegment


async def main():
    """Run example usage."""
    # Initialize vector store
    persist_dir = Path(__file__).parent.parent / "data" / "chromadb_example"
    store = MemexVectorStore(persist_directory=str(persist_dir))

    print("\n=== MemexVectorStore Example Usage ===\n")

    # Example 1: Add transcript segments
    print("1. Adding transcript segments...")
    segments = [
        TranscriptSegment(
            text="We need to improve the search functionality in our app.",
            speaker="Alice",
            start_time_ms=0,
            end_time_ms=3000
        ),
        TranscriptSegment(
            text="I agree. Users are having trouble finding relevant documents.",
            speaker="Bob",
            start_time_ms=3000,
            end_time_ms=6000
        ),
        TranscriptSegment(
            text="Let's implement semantic search using vector embeddings.",
            speaker="Alice",
            start_time_ms=6000,
            end_time_ms=9000
        ),
    ]

    today = datetime.now().strftime("%Y-%m-%d")
    num_added = await store.add_transcript(
        transcript_id="meeting_001",
        segments=segments,
        metadata={
            "date": today,
            "title": "Product Planning Meeting",
            "duration": 9000,
        }
    )
    print(f"   Added {num_added} segments\n")

    # Example 2: Add journal entry
    print("2. Adding journal entry...")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    paragraphs = [
        "Today I learned about vector databases and how they enable semantic search.",
        "ChromaDB seems like a good choice for our use case. It's simple and fast.",
        "Next week I'll prototype the integration with our existing codebase.",
    ]

    num_added = await store.add_journal_entry(
        journal_id="journal_2026_02_02",
        date=yesterday,
        paragraphs=paragraphs,
        metadata={"tags": ["learning", "databases"]}
    )
    print(f"   Added {num_added} paragraphs\n")

    # Example 3: Semantic search
    print("3. Searching for 'vector database'...")
    results = await store.search(
        query="vector database",
        n_results=5,
        recency_weight=0.3  # 30% weight on recency, 70% on similarity
    )

    for i, result in enumerate(results, 1):
        print(f"\n   Result {i}:")
        print(f"   Collection: {result.collection}")
        print(f"   Similarity: {result.similarity:.3f}")
        print(f"   Recency: {result.recency_score:.3f}")
        print(f"   Final Score: {result.final_score:.3f}")
        print(f"   Date: {result.date}")
        print(f"   Content: {result.content[:80]}...")

    # Example 4: Get context window
    print("\n\n4. Getting context window for LLM prompt...")
    context = await store.get_context_window(
        query="search and databases",
        max_tokens=1000
    )
    print(f"   Context ({len(context)} chars):")
    print(f"   {context[:200]}...\n")

    # Example 5: Get statistics
    print("5. Vector store statistics:")
    stats = store.get_stats()
    for collection_name, collection_stats in stats.items():
        print(f"   {collection_name}: {collection_stats['count']} documents")

    print("\n=== Example Complete ===\n")


if __name__ == "__main__":
    asyncio.run(main())
