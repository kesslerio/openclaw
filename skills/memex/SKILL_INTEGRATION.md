# Memex Skill Integration with Search API

This guide shows how to integrate the Memex HISTORIAN Search API with the memex skill for programmatic access.

## Architecture

```
┌──────────────┐         HTTP          ┌──────────────────┐
│ Memex Skill  │ ───────────────────> │  Search API      │
│  (Claude)    │   localhost:8765      │  (FastAPI)       │
└──────────────┘                       └──────────────────┘
                                               │
                                               ▼
                                       ┌──────────────────┐
                                       │  ChromaDB        │
                                       │  Vector Store    │
                                       └──────────────────┘
```

## Python Client Example

```python
import requests
from typing import List, Dict, Optional

class MemexClient:
    """Client for Memex HISTORIAN Search API"""

    def __init__(self, base_url: str = "http://localhost:8765"):
        self.base_url = base_url

    def health_check(self) -> Dict:
        """Check if API is healthy"""
        response = requests.get(f"{self.base_url}/")
        response.raise_for_status()
        return response.json()

    def search(
        self,
        query: str,
        limit: int = 10,
        speaker: Optional[str] = None
    ) -> Dict:
        """
        Search transcripts semantically

        Args:
            query: Search query (natural language)
            limit: Number of results (1-50)
            speaker: Optional speaker filter

        Returns:
            Dictionary with query, results, and total count
        """
        params = {"q": query, "limit": limit}
        if speaker:
            params["speaker"] = speaker

        response = requests.get(f"{self.base_url}/search", params=params)
        response.raise_for_status()
        return response.json()

    def get_stats(self) -> Dict:
        """Get index statistics"""
        response = requests.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()


# Usage Example
if __name__ == "__main__":
    client = MemexClient()

    # Check health
    health = client.health_check()
    print(f"Status: {health['status']}")
    print(f"Indexed chunks: {health['indexed_chunks']}")

    # Search
    results = client.search("patient documentation", limit=5)
    print(f"\nFound {results['total']} results for '{results['query']}'")

    for i, result in enumerate(results['results'], 1):
        print(f"\n{i}. Score: {result['score']:.4f}")
        print(f"   Speaker: {result['speaker']}")
        print(f"   Date: {result['date']}")
        print(f"   Text: {result['text'][:100]}...")
```

## Skill Integration Points

### 1. Search Command

Add a search capability to the memex skill:

```python
@skill_command("search")
async def search_transcripts(query: str, limit: int = 10):
    """Search across all indexed transcripts"""
    client = MemexClient()
    results = client.search(query, limit)

    # Format results for display
    output = [f"Found {results['total']} results for '{results['query']}'\n"]

    for i, result in enumerate(results['results'], 1):
        output.append(f"\n{i}. [{result['score']:.2f}] {result['date']} - {result['speaker']}")
        output.append(f"   {result['text'][:200]}...")

    return "\n".join(output)
```

### 2. Context Retrieval

Automatically retrieve relevant context for queries:

```python
def get_context_for_topic(topic: str, max_chunks: int = 5) -> str:
    """Retrieve relevant transcript chunks for a topic"""
    client = MemexClient()
    results = client.search(topic, limit=max_chunks)

    context_chunks = []
    for result in results['results']:
        chunk = f"[{result['date']} - {result['speaker']}]\n{result['text']}"
        context_chunks.append(chunk)

    return "\n\n---\n\n".join(context_chunks)
```

### 3. Speaker-Specific Search

Search within a specific speaker's transcripts:

```python
def search_by_speaker(speaker: str, query: str, limit: int = 10):
    """Search within a specific speaker's transcripts"""
    client = MemexClient()
    results = client.search(query, limit=limit, speaker=speaker)
    return results
```

## Error Handling

```python
import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError

def safe_search(query: str) -> Optional[Dict]:
    """Search with error handling"""
    client = MemexClient()

    try:
        return client.search(query)
    except ConnectionError:
        print("Error: API service not running. Start with 'make start'")
        return None
    except Timeout:
        print("Error: API request timed out")
        return None
    except HTTPError as e:
        print(f"Error: API returned {e.response.status_code}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## Response Formatting

### Console Output

```python
def format_search_results(results: Dict) -> str:
    """Format results for console display"""
    lines = [
        f"Query: {results['query']}",
        f"Results: {results['total']}\n"
    ]

    for i, r in enumerate(results['results'], 1):
        lines.append(f"{i}. [{r['score']:.2f}] {r['title']}")
        lines.append(f"   Date: {r['date']} | Speaker: {r['speaker']}")
        lines.append(f"   {r['text'][:150]}...\n")

    return "\n".join(lines)
```

### Markdown Output

```python
def format_as_markdown(results: Dict) -> str:
    """Format results as Markdown"""
    lines = [
        f"# Search Results: {results['query']}",
        f"*Found {results['total']} results*\n"
    ]

    for i, r in enumerate(results['results'], 1):
        lines.append(f"## {i}. {r['title']} `{r['score']:.2f}`")
        lines.append(f"**{r['speaker']}** • {r['date']}\n")
        lines.append(f"{r['text']}\n")
        lines.append("---\n")

    return "\n".join(lines)
```

## Caching Strategy

For better performance, cache recent searches:

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedMemexClient(MemexClient):
    """Client with caching"""

    def __init__(self, *args, cache_ttl: int = 300, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_ttl = cache_ttl  # seconds
        self._cache = {}

    def search(self, query: str, limit: int = 10, speaker: Optional[str] = None) -> Dict:
        """Search with caching"""
        cache_key = f"{query}:{limit}:{speaker}"
        now = datetime.now()

        # Check cache
        if cache_key in self._cache:
            cached_time, cached_result = self._cache[cache_key]
            if now - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_result

        # Call API
        result = super().search(query, limit, speaker)

        # Store in cache
        self._cache[cache_key] = (now, result)

        return result
```

## Batch Operations

For processing multiple queries:

```python
def batch_search(queries: List[str], limit: int = 10) -> Dict[str, Dict]:
    """Search multiple queries"""
    client = MemexClient()
    results = {}

    for query in queries:
        try:
            results[query] = client.search(query, limit)
        except Exception as e:
            results[query] = {"error": str(e)}

    return results
```

## Testing Integration

```python
import pytest

def test_api_connection():
    """Test that API is reachable"""
    client = MemexClient()
    health = client.health_check()
    assert health['status'] == 'healthy'

def test_search_returns_results():
    """Test search returns expected format"""
    client = MemexClient()
    results = client.search("test query", limit=5)

    assert 'query' in results
    assert 'results' in results
    assert 'total' in results
    assert isinstance(results['results'], list)
    assert len(results['results']) <= 5

def test_speaker_filter():
    """Test speaker filtering"""
    client = MemexClient()
    results = client.search("test", speaker="John")

    # All results should be from specified speaker
    for result in results['results']:
        assert result['speaker'] == "John"
```

## Environment Variables

Set API URL via environment:

```python
import os

class MemexClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv(
            "MEMEX_API_URL",
            "http://localhost:8765"
        )
```

Then use:

```bash
export MEMEX_API_URL=http://localhost:8765
python your_script.py
```

## Async Support

For async applications:

```python
import aiohttp
from typing import Dict, Optional

class AsyncMemexClient:
    """Async client for Memex API"""

    def __init__(self, base_url: str = "http://localhost:8765"):
        self.base_url = base_url

    async def search(
        self,
        query: str,
        limit: int = 10,
        speaker: Optional[str] = None
    ) -> Dict:
        """Async search"""
        params = {"q": query, "limit": limit}
        if speaker:
            params["speaker"] = speaker

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/search",
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()

# Usage
async def main():
    client = AsyncMemexClient()
    results = await client.search("patient care")
    print(f"Found {results['total']} results")
```

## Webhook/Callback Integration

For real-time indexing notifications:

```python
def register_index_webhook(callback_url: str):
    """Register webhook for index updates"""
    # Future enhancement - notify when new transcripts are indexed
    pass
```

## Next Steps

1. Add client to memex skill package
2. Create skill commands for search operations
3. Implement context retrieval for chat enhancement
4. Set up periodic cache invalidation
5. Add monitoring/logging for API calls
