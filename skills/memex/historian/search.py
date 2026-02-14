"""
Memex HISTORIAN - Search Engine
High-level search interface with recency ranking
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .vector_store import VectorStore
from .recency_ranker import RecencyRanker
from .config import DEFAULT_RESULTS, MAX_RESULTS

logger = logging.getLogger(__name__)


class SearchEngine:
    """
    Semantic search with recency ranking.
    
    Features:
    - Natural language queries
    - Date range filtering
    - Speaker filtering  
    - Recency-boosted results
    - Detailed explanations
    """
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        recency_ranker: Optional[RecencyRanker] = None,
    ):
        self.vector_store = vector_store or VectorStore()
        self.recency_ranker = recency_ranker or RecencyRanker()
        
        logger.info("Initialized SearchEngine")
    
    def search(
        self,
        query: str,
        n_results: int = DEFAULT_RESULTS,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        speaker: Optional[str] = None,
        use_recency: bool = True,
        explain: bool = False,
    ) -> Dict[str, Any]:
        """
        Search transcripts with optional filters.
        
        Args:
            query: Natural language search query
            n_results: Number of results to return
            date_from: Filter results from this date (YYYY-MM-DD)
            date_to: Filter results until this date (YYYY-MM-DD)
            speaker: Filter by speaker name
            use_recency: Apply recency ranking (default: True)
            explain: Include ranking explanation (default: False)
        
        Returns:
            Search results with documents, metadata, and scores
        """
        # Validate n_results
        n_results = min(n_results, MAX_RESULTS)
        
        # Build metadata filters
        where = self._build_filters(date_from, date_to, speaker)
        
        # Query vector store
        logger.info(f"Searching for: '{query}' (n={n_results}, filters={where})")
        results = self.vector_store.query(
            query_texts=[query],
            n_results=n_results * 2 if use_recency else n_results,  # Get more for reranking
            where=where,
        )
        
        # Apply recency ranking
        if use_recency and results.get('ids'):
            results = self.recency_ranker.rerank_results(results)
            # Trim to requested size after reranking
            results = self._trim_results(results, n_results)
        
        # Format response
        response = self._format_response(results, query, explain)
        
        logger.info(f"Search complete: {len(response['results'])} results")
        return response
    
    def _build_filters(
        self,
        date_from: Optional[str],
        date_to: Optional[str],
        speaker: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """Build ChromaDB metadata filters"""
        filters = {}
        
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter['$gte'] = date_from
            if date_to:
                date_filter['$lte'] = date_to
            filters['date'] = date_filter
        
        if speaker:
            filters['speaker'] = speaker
        
        return filters if filters else None
    
    def _trim_results(self, results: Dict[str, Any], n: int) -> Dict[str, Any]:
        """Trim results to n items"""
        if not results or not results.get('ids'):
            return results
        
        trimmed = {}
        for key, value in results.items():
            if isinstance(value, list) and isinstance(value[0], list):
                trimmed[key] = [value[0][:n]]
            else:
                trimmed[key] = value
        
        return trimmed
    
    def _format_response(
        self,
        results: Dict[str, Any],
        query: str,
        explain: bool,
    ) -> Dict[str, Any]:
        """Format search results for API response"""
        if not results or not results.get('ids'):
            return {
                'query': query,
                'count': 0,
                'results': [],
            }
        
        ids = results['ids'][0]
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        # Include scores if available (from recency ranker)
        scores = results.get('scores', [[]])[0]
        sim_scores = results.get('similarity_scores', [[]])[0]
        rec_scores = results.get('recency_scores', [[]])[0]
        
        formatted_results = []
        for i, (id_, doc, meta) in enumerate(zip(ids, documents, metadatas)):
            result = {
                'id': id_,
                'document': doc,
                'metadata': meta,
            }
            
            # Add scores if available
            if scores:
                result['score'] = scores[i] if i < len(scores) else None
                result['similarity_score'] = sim_scores[i] if i < len(sim_scores) else None
                result['recency_score'] = rec_scores[i] if i < len(rec_scores) else None
            
            formatted_results.append(result)
        
        response = {
            'query': query,
            'count': len(formatted_results),
            'results': formatted_results,
        }
        
        # Add explanation if requested
        if explain and scores:
            response['explanation'] = self.recency_ranker.explain_ranking(results)
        
        return response
    
    def find_similar(
        self,
        text: str,
        n_results: int = 5,
        use_recency: bool = False,
    ) -> Dict[str, Any]:
        """
        Find documents similar to given text.
        
        Args:
            text: Text to find similar documents for
            n_results: Number of results
            use_recency: Apply recency ranking
        
        Returns:
            Similar documents
        """
        return self.search(
            query=text,
            n_results=n_results,
            use_recency=use_recency,
        )
    
    def search_by_date_range(
        self,
        query: str,
        days_back: int = 7,
        n_results: int = DEFAULT_RESULTS,
    ) -> Dict[str, Any]:
        """
        Search within recent N days.
        
        Args:
            query: Search query
            days_back: Number of days to look back
            n_results: Number of results
        
        Returns:
            Search results from last N days
        """
        from datetime import timedelta
        
        today = datetime.now()
        date_from = (today - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        return self.search(
            query=query,
            date_from=date_from,
            n_results=n_results,
            use_recency=True,
        )
    
    def get_recent_memories(
        self,
        days: int = 7,
        n_results: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get all memories from last N days (no query).
        
        Args:
            days: Number of days to look back
            n_results: Maximum number of results
        
        Returns:
            Recent memories sorted by date
        """
        from datetime import timedelta
        
        today = datetime.now()
        date_from = (today - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Use a broad query to get recent items
        results = self.search(
            query="",
            date_from=date_from,
            n_results=n_results,
            use_recency=False,  # Don't need recency ranking for time-based query
        )
        
        # Sort by date (most recent first)
        if results['results']:
            results['results'].sort(
                key=lambda x: x['metadata'].get('date', ''),
                reverse=True,
            )
        
        return results['results']
