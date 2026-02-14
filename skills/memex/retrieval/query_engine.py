"""
Chat Query Engine for Memex

Handles conversational queries against the vector database with intelligent
query parsing, recency-biased search, and source-attributed responses.

Usage:
    from retrieval import QueryEngine
    
    engine = QueryEngine()
    response = engine.query("What did I promise Mark about the demo?")
    print(response.answer)
    for source in response.sources:
        print(f"  📅 {source.date}: {source.snippet}")
"""

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# Will use OpenAI for query understanding and response generation
try:
    import openai
except ImportError:
    openai = None

# Import from historian package
import sys
sys.path.append(str(Path(__file__).parent.parent))
from historian.search import MemorySearch
from historian.recency_ranker import RecencyRanker


@dataclass
class Source:
    """A source document that supports an answer."""
    date: str
    snippet: str
    score: float
    metadata: Dict = field(default_factory=dict)
    transcript_path: Optional[str] = None
    

@dataclass
class QueryResponse:
    """Response from the query engine."""
    query: str
    answer: str
    sources: List[Source]
    confidence: float  # 0-1
    reasoning: Optional[str] = None  # Why this answer?
    

class QueryEngine:
    """
    Intelligent conversational query engine.
    
    Features:
    - Natural language query parsing
    - Intent detection (factual, temporal, relationship, etc.)
    - Recency-biased search
    - Source attribution
    - Confidence scoring
    """
    
    def __init__(
        self,
        search: Optional[MemorySearch] = None,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize query engine.
        
        Args:
            search: MemorySearch instance (created if None)
            api_key: OpenAI API key (from env if None)
            model: OpenAI model for query understanding and synthesis
        """
        self.search = search or MemorySearch()
        self.model = model
        
        # Set up OpenAI
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if openai and self.api_key:
            openai.api_key = self.api_key
        
        # Query history for context
        self.history: List[Dict] = []
        
    def query(
        self,
        query_text: str,
        max_sources: int = 5,
        date_filter: Optional[Tuple[str, str]] = None,
        use_history: bool = True
    ) -> QueryResponse:
        """
        Execute a conversational query.
        
        Args:
            query_text: Natural language query
            max_sources: Maximum sources to return
            date_filter: Optional (start_date, end_date) tuple
            use_history: Whether to use conversation history
            
        Returns:
            QueryResponse with answer and sources
        """
        # 1. Parse query intent
        intent = self._parse_intent(query_text)
        
        # 2. Expand query with context from history
        if use_history and self.history:
            expanded_query = self._expand_with_history(query_text)
        else:
            expanded_query = query_text
            
        # 3. Search with recency bias
        search_results = self.search.search(
            expanded_query,
            limit=max_sources * 2,  # Get more, filter later
            date_range=date_filter
        )
        
        # 4. Filter and rank by relevance to original query
        top_sources = self._rank_sources(
            search_results,
            query_text,
            intent,
            max_sources
        )
        
        # 5. Synthesize answer from sources
        answer, confidence, reasoning = self._synthesize_answer(
            query_text,
            top_sources,
            intent
        )
        
        # 6. Build response
        sources = [
            Source(
                date=result['metadata'].get('date', 'Unknown'),
                snippet=result['text'][:200] + "...",
                score=result.get('final_score', result.get('score', 0)),
                metadata=result['metadata'],
                transcript_path=result['metadata'].get('source_file')
            )
            for result in top_sources
        ]
        
        response = QueryResponse(
            query=query_text,
            answer=answer,
            sources=sources,
            confidence=confidence,
            reasoning=reasoning
        )
        
        # 7. Update history
        self.history.append({
            'query': query_text,
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep last 5 exchanges
        if len(self.history) > 5:
            self.history.pop(0)
            
        return response
    
    def _parse_intent(self, query: str) -> Dict:
        """
        Parse query intent to guide search and synthesis.
        
        Intent types:
        - factual: "What is X?"
        - temporal: "When did I...?"
        - commitment: "What did I promise...?"
        - relationship: "How are X and Y related?"
        - summary: "Summarize my work on X"
        """
        query_lower = query.lower()
        
        intent = {
            'type': 'factual',
            'temporal_focus': 'recent',  # recent, historical, all
            'requires_sources': True,
            'confidence_threshold': 0.6
        }
        
        # Temporal patterns
        if any(word in query_lower for word in ['when', 'date', 'time', 'yesterday', 'last week']):
            intent['type'] = 'temporal'
            intent['requires_sources'] = True
            
        # Commitment patterns
        if any(phrase in query_lower for phrase in ['promise', 'commit', 'said i would', 'agreed to']):
            intent['type'] = 'commitment'
            intent['confidence_threshold'] = 0.8  # High bar for commitments
            intent['temporal_focus'] = 'all'
            
        # Summary patterns
        if any(word in query_lower for word in ['summarize', 'overview', 'tell me about']):
            intent['type'] = 'summary'
            intent['requires_sources'] = False
            
        # Detect time focus
        if any(word in query_lower for word in ['recently', 'lately', 'today', 'this week']):
            intent['temporal_focus'] = 'recent'
        elif any(word in query_lower for word in ['ever', 'always', 'all time', 'history']):
            intent['temporal_focus'] = 'all'
            
        return intent
    
    def _expand_with_history(self, query: str) -> str:
        """
        Expand query with context from conversation history.
        
        Example:
            History: "What did I discuss with Mark?"
            New query: "And what did I promise him?"
            Expanded: "What did I promise Mark?"
        """
        if not self.history:
            return query
            
        # Simple pronoun resolution
        last_query = self.history[-1]['query']
        
        # Replace "him/her/them" with subject from last query
        pronouns = ['him', 'her', 'them', 'it']
        for pronoun in pronouns:
            if pronoun in query.lower():
                # Extract proper nouns from last query
                words = last_query.split()
                proper_nouns = [w for w in words if w[0].isupper() and len(w) > 1]
                if proper_nouns:
                    query = query.lower().replace(pronoun, proper_nouns[0])
                    
        return query
    
    def _rank_sources(
        self,
        search_results: List[Dict],
        query: str,
        intent: Dict,
        max_sources: int
    ) -> List[Dict]:
        """
        Rank and filter sources based on query intent.
        
        For commitments: prioritize exact matches
        For summaries: diversify across time
        For factual: prioritize recency
        """
        if intent['type'] == 'commitment':
            # For commitments, look for explicit promise language
            commitment_keywords = ['promise', 'will', "i'll", 'commit', 'agree', 'plan to']
            for result in search_results:
                text_lower = result['text'].lower()
                has_commitment = any(kw in text_lower for kw in commitment_keywords)
                if has_commitment:
                    result['score'] = result.get('score', 0) * 1.5
                    
        elif intent['type'] == 'summary':
            # For summaries, diversify sources across dates
            dates_seen = set()
            filtered = []
            for result in search_results:
                date = result['metadata'].get('date')
                if date not in dates_seen or len(filtered) < max_sources:
                    filtered.append(result)
                    dates_seen.add(date)
            search_results = filtered
            
        # Sort by score and take top N
        sorted_results = sorted(
            search_results,
            key=lambda x: x.get('final_score', x.get('score', 0)),
            reverse=True
        )
        
        return sorted_results[:max_sources]
    
    def _synthesize_answer(
        self,
        query: str,
        sources: List[Dict],
        intent: Dict
    ) -> Tuple[str, float, str]:
        """
        Synthesize an answer from sources using GPT.
        
        Returns:
            (answer, confidence, reasoning)
        """
        if not sources:
            return (
                "I don't have enough information to answer that confidently.",
                0.0,
                "No relevant sources found in memory."
            )
        
        # If no OpenAI, return simple answer
        if not openai or not self.api_key:
            answer = self._simple_synthesis(query, sources)
            return answer, 0.5, "Simple synthesis (no GPT)"
        
        # Build context from sources
        context = self._build_context(sources)
        
        # Create prompt based on intent
        system_prompt = self._get_system_prompt(intent)
        user_prompt = f"""Query: {query}

Context from memory:
{context}

Answer the query based ONLY on the provided context. If the context doesn't contain enough information, say so. Always cite which source (by date) supports each claim."""
        
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Low temperature for factual accuracy
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Calculate confidence based on source scores
            avg_score = sum(s.get('final_score', s.get('score', 0)) for s in sources) / len(sources)
            confidence = min(avg_score, 0.95)  # Cap at 95%
            
            reasoning = f"Synthesized from {len(sources)} sources (avg score: {avg_score:.2f})"
            
            return answer, confidence, reasoning
            
        except Exception as e:
            fallback = self._simple_synthesis(query, sources)
            return fallback, 0.4, f"GPT synthesis failed: {str(e)}"
    
    def _build_context(self, sources: List[Dict]) -> str:
        """Build context string from sources."""
        context_parts = []
        for i, source in enumerate(sources, 1):
            date = source['metadata'].get('date', 'Unknown')
            text = source['text']
            score = source.get('final_score', source.get('score', 0))
            
            context_parts.append(
                f"[{i}] Date: {date} (relevance: {score:.2f})\n{text}\n"
            )
            
        return "\n".join(context_parts)
    
    def _get_system_prompt(self, intent: Dict) -> str:
        """Get system prompt based on query intent."""
        base = """You are Memex, Arvind's AI memory assistant. Your job is to answer questions based on his past voice transcripts.

Rules:
1. Answer in first person ("You discussed..." not "Arvind discussed...")
2. Be concise but complete
3. Always cite sources by date
4. If unsure, say so - don't make things up
5. For commitments, be very precise about what was promised"""
        
        if intent['type'] == 'commitment':
            base += "\n6. For commitments, look for explicit promises or agreements, not just discussions"
        elif intent['type'] == 'summary':
            base += "\n6. Provide a high-level overview, organizing by theme rather than chronologically"
        elif intent['type'] == 'temporal':
            base += "\n6. Focus on dates and timing - be specific about when things happened"
            
        return base
    
    def _simple_synthesis(self, query: str, sources: List[Dict]) -> str:
        """Simple synthesis without GPT (fallback)."""
        if len(sources) == 1:
            date = sources[0]['metadata'].get('date', 'Unknown')
            return f"On {date}: {sources[0]['text'][:200]}..."
        else:
            summary = f"Found {len(sources)} relevant memories:\n\n"
            for source in sources[:3]:
                date = source['metadata'].get('date', 'Unknown')
                summary += f"• {date}: {source['text'][:100]}...\n"
            return summary
    
    def clear_history(self):
        """Clear conversation history."""
        self.history = []
    
    def get_recent_queries(self, limit: int = 5) -> List[Dict]:
        """Get recent query history."""
        return self.history[-limit:]


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Query your Memex memory")
    parser.add_argument("query", help="Your question")
    parser.add_argument("--max-sources", type=int, default=5)
    parser.add_argument("--no-history", action="store_true")
    
    args = parser.parse_args()
    
    engine = QueryEngine()
    response = engine.query(
        args.query,
        max_sources=args.max_sources,
        use_history=not args.no_history
    )
    
    print(f"\n🤔 Query: {response.query}")
    print(f"\n💭 Answer (confidence: {response.confidence:.0%}):")
    print(response.answer)
    print(f"\n📚 Sources ({len(response.sources)}):")
    for i, source in enumerate(response.sources, 1):
        print(f"  [{i}] {source.date} (score: {source.score:.2f})")
        print(f"      {source.snippet}")
    print(f"\n🧠 Reasoning: {response.reasoning}\n")
