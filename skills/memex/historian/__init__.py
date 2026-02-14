"""
Memex HISTORIAN - Memory System Package
"""

__version__ = "1.0.0"

# Only import the transcript indexer (FAISS-based, no ChromaDB)
# Other modules have broken dependencies (ChromaDB + pydantic v1 on Python 3.14)
from .transcript_indexer import TranscriptIndexer

__all__ = [
    "TranscriptIndexer",
]
