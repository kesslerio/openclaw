"""
Memex HISTORIAN - FastAPI Server
REST API for searching and querying the memory system
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from .search import SearchEngine
from .vector_store import VectorStore
from .config import DEFAULT_RESULTS, MAX_RESULTS

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Memex HISTORIAN API",
    description="AI-powered personal memory search with recency ranking",
    version="1.0.0",
)

# CORS middleware (allow frontend to access API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search engine
search_engine = SearchEngine()
vector_store = VectorStore()


# === Request/Response Models ===

class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query", min_length=1)
    n_results: int = Field(DEFAULT_RESULTS, ge=1, le=MAX_RESULTS, description="Number of results")
    date_from: Optional[str] = Field(None, description="Filter from date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="Filter until date (YYYY-MM-DD)")
    speaker: Optional[str] = Field(None, description="Filter by speaker name")
    use_recency: bool = Field(True, description="Apply recency ranking")
    explain: bool = Field(False, description="Include ranking explanation")


class SearchResponse(BaseModel):
    query: str
    count: int
    results: List[Dict[str, Any]]
    explanation: Optional[str] = None


class StatusResponse(BaseModel):
    status: str
    vector_store_count: int
    timestamp: str


# === API Endpoints ===

@app.get("/", response_model=StatusResponse)
async def root():
    """API status and health check"""
    return {
        "status": "online",
        "vector_store_count": vector_store.count(),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/status", response_model=StatusResponse)
async def status():
    """Detailed status information"""
    return {
        "status": "online",
        "vector_store_count": vector_store.count(),
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search transcripts with semantic similarity and recency ranking.
    
    **Example:**
    ```json
    {
        "query": "What did I discuss about AI?",
        "n_results": 10,
        "date_from": "2026-01-01",
        "use_recency": true,
        "explain": true
    }
    ```
    """
    try:
        results = search_engine.search(
            query=request.query,
            n_results=request.n_results,
            date_from=request.date_from,
            date_to=request.date_to,
            speaker=request.speaker,
            use_recency=request.use_recency,
            explain=request.explain,
        )
        return results
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search", response_model=SearchResponse)
async def search_get(
    q: str = Query(..., description="Search query"),
    n: int = Query(DEFAULT_RESULTS, ge=1, le=MAX_RESULTS, description="Number of results"),
    date_from: Optional[str] = Query(None, description="From date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="To date (YYYY-MM-DD)"),
    speaker: Optional[str] = Query(None, description="Speaker filter"),
    use_recency: bool = Query(True, description="Use recency ranking"),
    explain: bool = Query(False, description="Include explanation"),
):
    """
    Search via GET request (query parameters).
    
    **Example:** `/search?q=AI+discussion&n=5&use_recency=true`
    """
    try:
        results = search_engine.search(
            query=q,
            n_results=n,
            date_from=date_from,
            date_to=date_to,
            speaker=speaker,
            use_recency=use_recency,
            explain=explain,
        )
        return results
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recent/{days}", response_model=SearchResponse)
async def get_recent(
    days: int = Query(..., ge=1, le=365, description="Days to look back"),
    n: int = Query(20, ge=1, le=MAX_RESULTS, description="Max results"),
):
    """
    Get recent memories from last N days.
    
    **Example:** `/recent/7?n=10` (last 7 days, 10 results)
    """
    try:
        results = search_engine.get_recent_memories(days=days, n_results=n)
        return {
            "query": f"Recent {days} days",
            "count": len(results),
            "results": results,
        }
    except Exception as e:
        logger.error(f"Recent memories error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        count = vector_store.count()
        
        # Try to get date range from metadata
        # (would need to query the collection for this - simplified for now)
        
        return {
            "total_chunks": count,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Startup/Shutdown Events ===

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Memex HISTORIAN API starting...")
    logger.info(f"📚 Vector store initialized with {vector_store.count()} chunks")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Memex HISTORIAN API shutting down...")


# === Run Server ===

if __name__ == "__main__":
    import uvicorn
    from .config import API_HOST, API_PORT, API_RELOAD
    
    uvicorn.run(
        "historian.api:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD,
        log_level="info",
    )
