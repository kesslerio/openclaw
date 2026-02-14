"""
Tests for Recency Ranker - THE SECRET SAUCE!
"""

import pytest
from datetime import datetime, timedelta
import math

from historian.recency_ranker import RecencyRanker


class TestRecencyRanker:
    """Test the recency ranking algorithm"""
    
    @pytest.fixture
    def ranker(self):
        """Default ranker with 70/30 split"""
        return RecencyRanker(
            similarity_weight=0.7,
            recency_weight=0.3,
            decay_rate=0.05,
        )
    
    def test_initialization(self, ranker):
        """Test ranker initializes with correct weights"""
        assert ranker.similarity_weight == 0.7
        assert ranker.recency_weight == 0.3
        assert ranker.decay_rate == 0.05
    
    def test_weights_must_sum_to_one(self):
        """Test that weights must sum to 1.0"""
        with pytest.raises(ValueError):
            RecencyRanker(similarity_weight=0.6, recency_weight=0.3)
    
    def test_recency_score_today(self, ranker):
        """Test that today's date gets recency score = 1.0"""
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        
        score = ranker.calculate_recency_score(date_str, reference_date=today)
        assert score == pytest.approx(1.0, abs=0.001)
    
    def test_recency_score_yesterday(self, ranker):
        """Test recency decay for yesterday"""
        today = datetime.now()
        yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        
        score = ranker.calculate_recency_score(yesterday, reference_date=today)
        
        # e^(-0.05 * 1) ≈ 0.951
        expected = math.exp(-0.05 * 1)
        assert score == pytest.approx(expected, abs=0.01)
    
    def test_recency_score_7_days_ago(self, ranker):
        """Test recency decay for 1 week ago"""
        today = datetime.now()
        week_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        
        score = ranker.calculate_recency_score(week_ago, reference_date=today)
        
        # e^(-0.05 * 7) ≈ 0.705
        expected = math.exp(-0.05 * 7)
        assert score == pytest.approx(expected, abs=0.01)
    
    def test_recency_score_30_days_ago(self, ranker):
        """Test recency decay for 1 month ago"""
        today = datetime.now()
        month_ago = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        
        score = ranker.calculate_recency_score(month_ago, reference_date=today)
        
        # e^(-0.05 * 30) ≈ 0.223
        expected = math.exp(-0.05 * 30)
        assert score == pytest.approx(expected, abs=0.01)
    
    def test_recency_score_90_days_ago(self, ranker):
        """Test recency decay for 3 months ago"""
        today = datetime.now()
        three_months_ago = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        
        score = ranker.calculate_recency_score(three_months_ago, reference_date=today)
        
        # e^(-0.05 * 90) ≈ 0.011
        expected = math.exp(-0.05 * 90)
        assert score == pytest.approx(expected, abs=0.01)
    
    def test_similarity_score_from_distance(self, ranker):
        """Test conversion from L2 distance to similarity"""
        # Distance = 0 → similarity = 1.0
        assert ranker.calculate_similarity_score(0.0) == pytest.approx(1.0)
        
        # Distance = 1 → similarity = 0.5
        assert ranker.calculate_similarity_score(1.0) == pytest.approx(0.5)
        
        # Distance = 4 → similarity = 0.2
        assert ranker.calculate_similarity_score(4.0) == pytest.approx(0.2)
    
    def test_final_score_calculation(self, ranker):
        """Test weighted combination of similarity and recency"""
        # Perfect match today: sim=1.0, rec=1.0 → final = (1.0*0.7) + (1.0*0.3) = 1.0
        final = ranker.calculate_final_score(similarity=1.0, recency=1.0)
        assert final == pytest.approx(1.0)
        
        # Perfect match 30 days ago: sim=1.0, rec=0.223 → final = 0.7 + 0.067 = 0.767
        final = ranker.calculate_final_score(similarity=1.0, recency=0.223)
        assert final == pytest.approx(0.767, abs=0.01)
        
        # Weak match today: sim=0.3, rec=1.0 → final = 0.21 + 0.3 = 0.51
        final = ranker.calculate_final_score(similarity=0.3, recency=1.0)
        assert final == pytest.approx(0.51)
    
    def test_recent_beats_old_with_same_similarity(self, ranker):
        """Test that recent memory ranks higher than old with same similarity"""
        # Today's memory
        recent_score = ranker.calculate_final_score(similarity=0.8, recency=1.0)
        
        # 30 days ago
        old_score = ranker.calculate_final_score(similarity=0.8, recency=0.223)
        
        # Recent should rank higher
        assert recent_score > old_score
    
    def test_highly_relevant_old_beats_mediocre_recent(self, ranker):
        """Test that highly relevant old memory can beat mediocre recent one"""
        # Perfect match 30 days ago: sim=1.0, rec=0.223
        old_perfect = ranker.calculate_final_score(similarity=1.0, recency=0.223)
        
        # Weak match today: sim=0.4, rec=1.0
        recent_weak = ranker.calculate_final_score(similarity=0.4, recency=1.0)
        
        # Old perfect should win: 0.767 > 0.58
        assert old_perfect > recent_weak
    
    def test_rerank_results_sorting(self, ranker):
        """Test that rerank_results sorts by final score"""
        # Mock ChromaDB results
        results = {
            'ids': [['doc1', 'doc2', 'doc3']],
            'documents': [['Text 1', 'Text 2', 'Text 3']],
            'metadatas': [[
                {'date': '2026-01-15', 'title': 'Old but relevant'},
                {'date': '2026-01-31', 'title': 'Recent and weak'},
                {'date': '2026-02-01', 'title': 'Recent and relevant'},
            ]],
            'distances': [[0.2, 2.0, 0.3]],  # doc1=high sim, doc2=low sim, doc3=high sim
        }
        
        reference_date = datetime(2026, 2, 1)
        reranked = ranker.rerank_results(results, reference_date)
        
        # doc3 should be first (recent + relevant)
        # doc1 should be second (old but very relevant)
        # doc2 should be last (recent but not relevant)
        assert reranked['ids'][0][0] == 'doc3'
        assert reranked['ids'][0][2] == 'doc2'
    
    def test_explain_ranking(self, ranker):
        """Test that explain_ranking generates readable output"""
        results = {
            'ids': [['doc1']],
            'metadatas': [[{'date': '2026-02-01', 'title': 'Test Document'}]],
            'scores': [[0.85]],
            'similarity_scores': [[0.9]],
            'recency_scores': [[0.75]],
        }
        
        explanation = ranker.explain_ranking(results, top_n=1)
        
        assert "Test Document" in explanation
        assert "2026-02-01" in explanation
        assert "0.850" in explanation  # Final score
        assert "0.900" in explanation  # Similarity
        assert "0.750" in explanation  # Recency
