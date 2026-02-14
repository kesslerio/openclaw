"""
Memex HISTORIAN - Recency Ranker
🌟 THE SECRET SAUCE 🌟

Re-ranks search results by combining:
- Semantic similarity (70%)
- Recency (30%)

This makes recent memories surface higher than old ones,
mimicking how human memory works.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import math

from .config import SIMILARITY_WEIGHT, RECENCY_WEIGHT, DECAY_RATE

logger = logging.getLogger(__name__)


class RecencyRanker:
    """
    Re-ranks vector search results to favor recent memories.
    
    Algorithm:
        final_score = (similarity_score * 0.7) + (recency_score * 0.3)
    
    Where:
        - similarity_score: Cosine similarity from vector search (0-1)
        - recency_score: Time decay function (0-1)
        - recency_score = exp(-decay_rate * days_ago)
    
    Example:
        - Today's memory: recency_score = 1.0
        - 7 days ago: recency_score ≈ 0.70 (5% daily decay)
        - 30 days ago: recency_score ≈ 0.21
        - 90 days ago: recency_score ≈ 0.01
    """
    
    def __init__(
        self,
        similarity_weight: float = SIMILARITY_WEIGHT,
        recency_weight: float = RECENCY_WEIGHT,
        decay_rate: float = DECAY_RATE,
    ):
        self.similarity_weight = similarity_weight
        self.recency_weight = recency_weight
        self.decay_rate = decay_rate
        
        # Validate weights sum to 1.0
        if not math.isclose(similarity_weight + recency_weight, 1.0):
            raise ValueError(f"Weights must sum to 1.0 (got {similarity_weight + recency_weight})")
        
        logger.info(
            f"Initialized RecencyRanker "
            f"(sim={similarity_weight}, recency={recency_weight}, decay={decay_rate})"
        )
    
    def calculate_recency_score(self, date_str: str, reference_date: datetime = None) -> float:
        """
        Calculate recency score using exponential decay.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            reference_date: Reference date (default: today)
        
        Returns:
            Recency score between 0 and 1
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        try:
            memory_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            logger.warning(f"Invalid date format: {date_str}. Using default score 0.5")
            return 0.5
        
        # Calculate days ago
        days_ago = (reference_date - memory_date).days
        
        # Exponential decay: score = e^(-decay_rate * days)
        recency_score = math.exp(-self.decay_rate * days_ago)
        
        # Clamp to [0, 1]
        recency_score = max(0.0, min(1.0, recency_score))
        
        logger.debug(f"Date: {date_str}, Days ago: {days_ago}, Recency: {recency_score:.3f}")
        return recency_score
    
    def calculate_similarity_score(self, distance: float) -> float:
        """
        Convert ChromaDB distance to similarity score.
        
        ChromaDB returns L2 distance (lower = more similar).
        We convert to similarity: similarity = 1 / (1 + distance)
        
        Args:
            distance: L2 distance from ChromaDB
        
        Returns:
            Similarity score between 0 and 1
        """
        # Convert distance to similarity
        # For L2 distance: similarity ≈ 1 / (1 + distance)
        similarity = 1.0 / (1.0 + distance)
        return similarity
    
    def calculate_final_score(self, similarity: float, recency: float) -> float:
        """
        Combine similarity and recency scores.
        
        Args:
            similarity: Similarity score (0-1)
            recency: Recency score (0-1)
        
        Returns:
            Final weighted score (0-1)
        """
        final_score = (
            (similarity * self.similarity_weight) +
            (recency * self.recency_weight)
        )
        return final_score
    
    def rerank_results(
        self,
        results: Dict[str, Any],
        reference_date: datetime = None,
    ) -> Dict[str, Any]:
        """
        Re-rank ChromaDB query results by recency.
        
        Args:
            results: ChromaDB query results dict with keys:
                     - ids: List[List[str]]
                     - documents: List[List[str]]
                     - metadatas: List[List[Dict]]
                     - distances: List[List[float]]
            reference_date: Reference date for recency calculation
        
        Returns:
            Re-ranked results in same format
        """
        if not results or not results.get('ids'):
            logger.warning("Empty results, nothing to rerank")
            return results
        
        # Process first query result (assuming single query)
        ids = results['ids'][0]
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]
        
        # Calculate scores for each result
        scored_results = []
        
        for i, (id_, doc, meta, dist) in enumerate(zip(ids, documents, metadatas, distances)):
            # Get date from metadata
            date_str = meta.get('date', datetime.now().strftime('%Y-%m-%d'))
            
            # Calculate scores
            similarity_score = self.calculate_similarity_score(dist)
            recency_score = self.calculate_recency_score(date_str, reference_date)
            final_score = self.calculate_final_score(similarity_score, recency_score)
            
            # Store result with scores
            scored_results.append({
                'id': id_,
                'document': doc,
                'metadata': meta,
                'distance': dist,
                'similarity_score': similarity_score,
                'recency_score': recency_score,
                'final_score': final_score,
            })
        
        # Sort by final score (descending)
        scored_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Convert back to ChromaDB format
        reranked = {
            'ids': [[r['id'] for r in scored_results]],
            'documents': [[r['document'] for r in scored_results]],
            'metadatas': [[r['metadata'] for r in scored_results]],
            'distances': [[r['distance'] for r in scored_results]],
            'scores': [[r['final_score'] for r in scored_results]],  # Added!
            'similarity_scores': [[r['similarity_score'] for r in scored_results]],
            'recency_scores': [[r['recency_score'] for r in scored_results]],
        }
        
        logger.info(f"Re-ranked {len(scored_results)} results")
        return reranked
    
    def explain_ranking(self, reranked_results: Dict[str, Any], top_n: int = 5) -> str:
        """
        Generate human-readable explanation of ranking.
        
        Args:
            reranked_results: Results from rerank_results()
            top_n: Number of top results to explain
        
        Returns:
            Formatted explanation string
        """
        if not reranked_results or not reranked_results.get('ids'):
            return "No results to explain"
        
        explanation_lines = ["📊 Ranking Explanation (Top Results):\n"]
        
        ids = reranked_results['ids'][0][:top_n]
        metadatas = reranked_results['metadatas'][0][:top_n]
        scores = reranked_results['scores'][0][:top_n]
        sim_scores = reranked_results['similarity_scores'][0][:top_n]
        rec_scores = reranked_results['recency_scores'][0][:top_n]
        
        for i, (id_, meta, final, sim, rec) in enumerate(zip(ids, metadatas, scores, sim_scores, rec_scores), 1):
            date = meta.get('date', 'Unknown')
            title = meta.get('title', 'Untitled')
            
            line = (
                f"{i}. {title[:50]} ({date})\n"
                f"   Final: {final:.3f} | Similarity: {sim:.3f} ({self.similarity_weight*100:.0f}%) | "
                f"Recency: {rec:.3f} ({self.recency_weight*100:.0f}%)\n"
            )
            explanation_lines.append(line)
        
        return "\n".join(explanation_lines)
