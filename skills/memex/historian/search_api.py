"""
Memex HISTORIAN - Semantic Search API
FastAPI server for searching indexed transcripts
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging

from .vector_store import VectorStore
from .embeddings import EmbeddingsManager
from .config import API_HOST, API_PORT, DEFAULT_RESULTS, MAX_RESULTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Memex HISTORIAN",
    description="Semantic search API for Plaud transcripts",
    version="1.0.0"
)

# CORS - restricted to localhost for security
import os
ALLOWED_ORIGINS = os.getenv("MEMEX_CORS_ORIGINS", "http://localhost:3000,http://localhost:8888,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize services
store = VectorStore()
embedder = EmbeddingsManager()


class SearchResult(BaseModel):
    text: str
    speaker: str
    transcript_id: str
    date: str
    title: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int


@app.get("/")
def health():
    """Health check endpoint"""
    count = store.count()
    return {
        "status": "healthy",
        "service": "memex-historian",
        "indexed_chunks": count
    }


@app.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(DEFAULT_RESULTS, ge=1, le=MAX_RESULTS, description="Number of results"),
    speaker: Optional[str] = Query(None, description="Filter by speaker name")
):
    """
    Semantic search across indexed transcripts.

    Returns the most relevant transcript segments based on meaning, not just keywords.
    """
    # Build metadata filter if speaker specified
    where_filter = None
    if speaker:
        where_filter = {"speaker": speaker}

    # Generate query embedding
    query_embedding = embedder.generate_embedding(q)

    # Search vector store
    results = store.collection.query(
        query_embeddings=[query_embedding],
        n_results=limit,
        where=where_filter
    )

    # Format results
    search_results = []
    for i, (doc, meta, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        # Convert distance to similarity score (lower distance = higher similarity)
        # ChromaDB uses L2 distance by default
        score = 1 / (1 + distance)

        search_results.append(SearchResult(
            text=doc,
            speaker=meta.get('speaker', 'Unknown'),
            transcript_id=meta.get('transcript_id', ''),
            date=meta.get('date', ''),
            title=meta.get('title', ''),
            score=round(score, 4)
        ))

    return SearchResponse(
        query=q,
        results=search_results,
        total=len(search_results)
    )


@app.get("/stats")
def stats():
    """Get index statistics"""
    return {
        "total_chunks": store.count(),
        "embedding_model": embedder.model_name,
        "collection": store.collection.name
    }


def main():
    """Run the API server"""
    import uvicorn
    logger.info(f"Starting Memex HISTORIAN API on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)


if __name__ == "__main__":
    main()
