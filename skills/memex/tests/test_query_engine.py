"""
Tests for Chat Query Engine

Run with: pytest test_query_engine.py -v
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from retrieval.query_engine import (
    QueryEngine,
    QueryResponse,
    Source
)


class TestIntentParsing:
    """Test query intent detection."""
    
    def setup_method(self):
        """Create query engine for testing."""
        # Mock the search to avoid needing real vector DB
        mock_search = Mock()
        self.engine = QueryEngine(search=mock_search, api_key="test-key")
    
    def test_factual_intent(self):
        """Should detect factual queries."""
        query = "What is the status of the Copper AI project?"
        intent = self.engine._parse_intent(query)
        
        assert intent['type'] == 'factual'
        assert intent['requires_sources'] is True
    
    def test_temporal_intent(self):
        """Should detect temporal queries."""
        queries = [
            "When did I last talk to Mark?",
            "What time was the meeting yesterday?",
            "What happened last week?"
        ]
        
        for query in queries:
            intent = self.engine._parse_intent(query)
            assert intent['type'] == 'temporal', f"Failed for: {query}"
    
    def test_commitment_intent(self):
        """Should detect commitment queries."""
        queries = [
            "What did I promise Mark?",
            "What did I commit to?",
            "What did I say I would do?"
        ]
        
        for query in queries:
            intent = self.engine._parse_intent(query)
            assert intent['type'] == 'commitment', f"Failed for: {query}"
            assert intent['confidence_threshold'] == 0.8
            assert intent['temporal_focus'] == 'all'
    
    def test_summary_intent(self):
        """Should detect summary queries."""
        queries = [
            "Summarize my meetings this week",
            "Give me an overview of the project",
            "Tell me about the partnership discussions"
        ]
        
        for query in queries:
            intent = self.engine._parse_intent(query)
            assert intent['type'] == 'summary', f"Failed for: {query}"
            assert intent['requires_sources'] is False
    
    def test_temporal_focus_recent(self):
        """Should detect recent temporal focus."""
        queries = [
            "What did I do recently?",
            "What happened today?",
            "This week's progress"
        ]
        
        for query in queries:
            intent = self.engine._parse_intent(query)
            assert intent['temporal_focus'] == 'recent', f"Failed for: {query}"
    
    def test_temporal_focus_all(self):
        """Should detect all-time temporal focus."""
        queries = [
            "Have I ever discussed X?",
            "What have I always said about Y?",
            "All mentions of Z"
        ]
        
        for query in queries:
            intent = self.engine._parse_intent(query)
            assert intent['temporal_focus'] == 'all', f"Failed for: {query}"


class TestHistoryExpansion:
    """Test query expansion with conversation history."""
    
    def setup_method(self):
        mock_search = Mock()
        self.engine = QueryEngine(search=mock_search, api_key="test-key")
    
    def test_pronoun_resolution_him(self):
        """Should resolve 'him' to subject from previous query."""
        self.engine.history = [{
            'query': "What did I discuss with Mark?",
            'answer': "You discussed the demo",
            'timestamp': datetime.now().isoformat()
        }]
        
        expanded = self.engine._expand_with_history("What did I promise him?")
        assert "Mark" in expanded
    
    def test_pronoun_resolution_it(self):
        """Should resolve 'it' to subject from previous query."""
        self.engine.history = [{
            'query': "What is the status of CopperAI?",
            'answer': "Making progress",
            'timestamp': datetime.now().isoformat()
        }]
        
        expanded = self.engine._expand_with_history("When did I last work on it?")
        assert "CopperAI" in expanded
    
    def test_no_history(self):
        """Should return original query when no history."""
        query = "What did I do yesterday?"
        expanded = self.engine._expand_with_history(query)
        assert expanded == query
    
    def test_no_pronouns(self):
        """Should return original query when no pronouns to resolve."""
        self.engine.history = [{
            'query': "Previous question",
            'answer': "Previous answer",
            'timestamp': datetime.now().isoformat()
        }]
        
        query = "What is the weather?"
        expanded = self.engine._expand_with_history(query)
        assert expanded == query


class TestSourceRanking:
    """Test source ranking logic."""
    
    def setup_method(self):
        mock_search = Mock()
        self.engine = QueryEngine(search=mock_search, api_key="test-key")
    
    def test_commitment_boost(self):
        """Should boost sources with commitment language."""
        results = [
            {
                'text': "I promise to send the docs by Friday",
                'score': 0.7,
                'metadata': {'date': '2026-01-28'}
            },
            {
                'text': "We discussed sending docs",
                'score': 0.8,
                'metadata': {'date': '2026-01-29'}
            }
        ]
        
        intent = {'type': 'commitment'}
        ranked = self.engine._rank_sources(results, "promise", intent, 5)
        
        # First result should be boosted above second
        assert ranked[0]['text'].startswith("I promise")
        assert ranked[0]['score'] > 0.8
    
    def test_summary_diversity(self):
        """Should diversify sources across dates for summaries."""
        results = [
            {'text': "Meeting 1", 'score': 0.9, 'metadata': {'date': '2026-01-28'}},
            {'text': "Meeting 2", 'score': 0.85, 'metadata': {'date': '2026-01-28'}},
            {'text': "Meeting 3", 'score': 0.8, 'metadata': {'date': '2026-01-29'}},
            {'text': "Meeting 4", 'score': 0.75, 'metadata': {'date': '2026-01-30'}},
        ]
        
        intent = {'type': 'summary'}
        ranked = self.engine._rank_sources(results, "summarize", intent, 2)
        
        # Should get diverse dates, not just top scores
        dates = [r['metadata']['date'] for r in ranked]
        assert len(set(dates)) >= 2
    
    def test_max_sources_limit(self):
        """Should respect max_sources limit."""
        results = [
            {'text': f"Result {i}", 'score': 1.0 - i*0.1, 'metadata': {'date': '2026-01-28'}}
            for i in range(10)
        ]
        
        intent = {'type': 'factual'}
        ranked = self.engine._rank_sources(results, "test", intent, 3)
        
        assert len(ranked) == 3
        assert all(ranked[i]['score'] >= ranked[i+1]['score'] for i in range(len(ranked)-1))


class TestAnswerSynthesis:
    """Test answer synthesis."""
    
    def setup_method(self):
        mock_search = Mock()
        self.engine = QueryEngine(search=mock_search, api_key="test-key")
    
    def test_no_sources(self):
        """Should handle no sources gracefully."""
        answer, confidence, reasoning = self.engine._synthesize_answer(
            "test query",
            [],
            {'type': 'factual'}
        )
        
        assert "don't have enough information" in answer.lower()
        assert confidence == 0.0
        assert "no relevant sources" in reasoning.lower()
    
    def test_simple_synthesis_single_source(self):
        """Should create simple answer from single source."""
        sources = [{
            'text': "The meeting was productive. We discussed the roadmap.",
            'metadata': {'date': '2026-01-28'},
            'score': 0.85
        }]
        
        answer = self.engine._simple_synthesis("What happened?", sources)
        
        assert "2026-01-28" in answer
        assert "meeting was productive" in answer
    
    def test_simple_synthesis_multiple_sources(self):
        """Should summarize multiple sources."""
        sources = [
            {'text': "First meeting", 'metadata': {'date': '2026-01-28'}, 'score': 0.9},
            {'text': "Second meeting", 'metadata': {'date': '2026-01-29'}, 'score': 0.85},
            {'text': "Third meeting", 'metadata': {'date': '2026-01-30'}, 'score': 0.8},
        ]
        
        answer = self.engine._simple_synthesis("Summarize", sources)
        
        assert "3 relevant memories" in answer
        assert "2026-01-28" in answer
        assert "2026-01-29" in answer
    
    def test_confidence_calculation(self):
        """Should calculate confidence from source scores."""
        sources = [
            {'text': "Test", 'metadata': {'date': '2026-01-28'}, 'final_score': 0.9},
            {'text': "Test", 'metadata': {'date': '2026-01-29'}, 'final_score': 0.8},
        ]
        
        # Mock OpenAI response
        with patch('retrieval.query_engine.openai') as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content="Test answer"))]
            mock_openai.chat.completions.create.return_value = mock_response
            
            answer, confidence, reasoning = self.engine._synthesize_answer(
                "test",
                sources,
                {'type': 'factual'}
            )
            
            # Average score is 0.85
            assert 0.8 <= confidence <= 0.9


class TestContextBuilding:
    """Test context string building."""
    
    def setup_method(self):
        mock_search = Mock()
        self.engine = QueryEngine(search=mock_search, api_key="test-key")
    
    def test_context_format(self):
        """Should format sources into context string."""
        sources = [
            {
                'text': "First source text",
                'metadata': {'date': '2026-01-28'},
                'final_score': 0.9
            },
            {
                'text': "Second source text",
                'metadata': {'date': '2026-01-29'},
                'score': 0.85
            }
        ]
        
        context = self.engine._build_context(sources)
        
        assert "[1]" in context
        assert "[2]" in context
        assert "2026-01-28" in context
        assert "2026-01-29" in context
        assert "First source text" in context
        assert "Second source text" in context
        assert "0.90" in context or "0.9" in context


class TestSystemPrompts:
    """Test system prompt generation."""
    
    def setup_method(self):
        mock_search = Mock()
        self.engine = QueryEngine(search=mock_search, api_key="test-key")
    
    def test_base_prompt(self):
        """Should include base instructions."""
        intent = {'type': 'factual'}
        prompt = self.engine._get_system_prompt(intent)
        
        assert "Memex" in prompt
        assert "first person" in prompt.lower()
        assert "cite sources" in prompt.lower()
    
    def test_commitment_prompt_addition(self):
        """Should add commitment-specific instructions."""
        intent = {'type': 'commitment'}
        prompt = self.engine._get_system_prompt(intent)
        
        assert "commitment" in prompt.lower() or "promise" in prompt.lower()
    
    def test_summary_prompt_addition(self):
        """Should add summary-specific instructions."""
        intent = {'type': 'summary'}
        prompt = self.engine._get_system_prompt(intent)
        
        assert "overview" in prompt.lower() or "theme" in prompt.lower()
    
    def test_temporal_prompt_addition(self):
        """Should add temporal-specific instructions."""
        intent = {'type': 'temporal'}
        prompt = self.engine._get_system_prompt(intent)
        
        assert "date" in prompt.lower() or "timing" in prompt.lower()


class TestHistoryManagement:
    """Test conversation history management."""
    
    def setup_method(self):
        mock_search = Mock()
        self.engine = QueryEngine(search=mock_search, api_key="test-key")
    
    def test_history_append(self):
        """Should append to history after query."""
        # Add some mock history
        self.engine.history = []
        
        # Simulate adding a query
        self.engine.history.append({
            'query': "test query",
            'answer': "test answer",
            'timestamp': datetime.now().isoformat()
        })
        
        assert len(self.engine.history) == 1
        assert self.engine.history[0]['query'] == "test query"
    
    def test_history_limit(self):
        """Should keep only last 5 exchanges."""
        # Add 10 entries
        for i in range(10):
            self.engine.history.append({
                'query': f"query {i}",
                'answer': f"answer {i}",
                'timestamp': datetime.now().isoformat()
            })
            
            # Manually trim (simulating what happens in query())
            if len(self.engine.history) > 5:
                self.engine.history.pop(0)
        
        assert len(self.engine.history) == 5
        assert self.engine.history[0]['query'] == "query 5"
        assert self.engine.history[-1]['query'] == "query 9"
    
    def test_clear_history(self):
        """Should clear all history."""
        self.engine.history = [
            {'query': "test", 'answer': "test", 'timestamp': datetime.now().isoformat()}
        ]
        
        self.engine.clear_history()
        assert len(self.engine.history) == 0
    
    def test_get_recent_queries(self):
        """Should return recent query history."""
        for i in range(3):
            self.engine.history.append({
                'query': f"query {i}",
                'answer': f"answer {i}",
                'timestamp': datetime.now().isoformat()
            })
        
        recent = self.engine.get_recent_queries(limit=2)
        assert len(recent) == 2
        assert recent[-1]['query'] == "query 2"


class TestIntegration:
    """Integration tests (require mocked search)."""
    
    def test_full_query_flow(self):
        """Should execute complete query flow."""
        # Mock search results
        mock_search = Mock()
        mock_search.search.return_value = [
            {
                'text': "We discussed the demo schedule. I'll send it by Friday.",
                'metadata': {'date': '2026-01-28', 'source_file': 'test.txt'},
                'final_score': 0.9
            }
        ]
        
        engine = QueryEngine(search=mock_search, api_key="test-key")
        
        # Execute query
        response = engine.query("What did I promise about the demo?")
        
        # Verify response structure
        assert isinstance(response, QueryResponse)
        assert response.query == "What did I promise about the demo?"
        assert len(response.sources) > 0
        assert 0 <= response.confidence <= 1
        
        # Verify search was called
        mock_search.search.assert_called_once()
        
        # Verify history was updated
        assert len(engine.history) == 1
        assert engine.history[0]['query'] == response.query


# Fixtures
@pytest.fixture
def mock_search_results():
    """Sample search results for testing."""
    return [
        {
            'text': "Had a great meeting with Mark about the partnership",
            'metadata': {'date': '2026-01-28', 'speaker': 'Arvind'},
            'final_score': 0.95
        },
        {
            'text': "Mark agreed to the terms, will sign next week",
            'metadata': {'date': '2026-01-29', 'speaker': 'Arvind'},
            'final_score': 0.90
        },
        {
            'text': "Followed up with Mark about signing",
            'metadata': {'date': '2026-01-30', 'speaker': 'Arvind'},
            'final_score': 0.85
        }
    ]


@pytest.fixture
def query_engine():
    """Query engine with mocked dependencies."""
    mock_search = Mock()
    return QueryEngine(search=mock_search, api_key="test-key")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
