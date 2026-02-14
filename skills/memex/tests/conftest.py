"""
Pytest configuration and shared fixtures for Memex tests.

This module provides:
- Temporary directories for test isolation
- Sample data fixtures (transcripts, journals, metadata)
- Mock API responses
- Common test utilities
"""

import pytest
import tempfile
import shutil
import asyncio
from pathlib import Path
from typing import Generator, Dict, List, Any
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
import numpy as np


# ============================================================
# Session-level Configuration
# ============================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests requiring actual credentials or external services"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests that are slow to run"
    )
    config.addinivalue_line(
        "markers", "asyncio: marks async tests"
    )


# ============================================================
# Event Loop Fixture (for async tests)
# ============================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================
# Temporary Directory Fixtures
# ============================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def data_dir(temp_dir) -> Path:
    """Create a data directory structure for tests."""
    data_path = temp_dir / "data"
    data_path.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (data_path / "raw").mkdir(exist_ok=True)
    (data_path / "processed").mkdir(exist_ok=True)
    (data_path / "vector_store").mkdir(exist_ok=True)

    return data_path


# ============================================================
# Sample Transcript Fixtures
# ============================================================

@pytest.fixture
def sample_transcript() -> str:
    """Sample meeting transcript for testing."""
    return """
[2026-02-01 10:00 AM]
Arvind: Let's discuss the Copper AI roadmap for Q1.
Mark: I'm interested, but I need to see HIPAA compliance documentation first.
Arvind: No problem, I'll send those over by Friday.
Mark: Also, can you introduce me to one of your existing clients?
Arvind: Absolutely. I'll connect you with our LarCare pilot.
Mark: Perfect. Let's schedule a follow-up for next Tuesday.
Arvind: Sounds good. I'll send a calendar invite.
"""


@pytest.fixture
def sample_transcript_segments() -> List[Dict[str, Any]]:
    """Sample transcript broken into segments."""
    return [
        {
            "text": "Let's discuss the Copper AI roadmap for Q1.",
            "speaker": "Arvind",
            "start_time_ms": 0,
            "end_time_ms": 3000
        },
        {
            "text": "I'm interested, but I need to see HIPAA compliance documentation first.",
            "speaker": "Mark",
            "start_time_ms": 3000,
            "end_time_ms": 8000
        },
        {
            "text": "No problem, I'll send those over by Friday.",
            "speaker": "Arvind",
            "start_time_ms": 8000,
            "end_time_ms": 11000
        },
        {
            "text": "Also, can you introduce me to one of your existing clients?",
            "speaker": "Mark",
            "start_time_ms": 11000,
            "end_time_ms": 14000
        },
        {
            "text": "Absolutely. I'll connect you with our LarCare pilot.",
            "speaker": "Arvind",
            "start_time_ms": 14000,
            "end_time_ms": 17000
        }
    ]


@pytest.fixture
def sample_metadata() -> Dict[str, Any]:
    """Sample recording metadata."""
    return {
        "id": "rec_123456",
        "title": "Sales Call with Mark",
        "date": "2026-02-01",
        "duration": 900,  # 15 minutes in seconds
        "speakers": ["Arvind", "Mark"],
        "file_path": "data/raw/2026-02-01_sales_call_mark.txt",
        "tags": ["sales", "HIPAA", "client_intro"]
    }


@pytest.fixture
def sample_journal_entry() -> Dict[str, Any]:
    """Sample journal entry for testing."""
    return {
        "id": "journal_20260201",
        "date": "2026-02-01",
        "paragraphs": [
            "Had a productive sales call with Mark today.",
            "He's interested in Copper AI but needs to see HIPAA compliance docs.",
            "Promised to send those by Friday and connect him with LarCare pilot.",
            "Follow-up scheduled for next Tuesday."
        ],
        "metadata": {
            "mood": "positive",
            "category": "work",
            "tags": ["sales", "follow_up"]
        }
    }


# ============================================================
# Mock API Response Fixtures
# ============================================================

@pytest.fixture
def mock_plaud_api_response() -> Dict[str, Any]:
    """Mock response from Plaud API listing recordings."""
    return {
        "recordings": [
            {
                "id": "rec_001",
                "title": "Team Standup",
                "created_at": "2026-01-28T10:00:00Z",
                "duration": 900,
                "status": "completed",
            },
            {
                "id": "rec_002",
                "title": "Client Demo",
                "created_at": "2026-01-28T14:00:00Z",
                "duration": 2700,
                "status": "completed",
            },
            {
                "id": "rec_003",
                "title": "Engineering Review",
                "created_at": "2026-01-29T11:00:00Z",
                "duration": 1800,
                "status": "completed",
            }
        ],
        "total": 3,
        "page": 1,
        "per_page": 10,
    }


@pytest.fixture
def mock_plaud_transcript_response() -> Dict[str, Any]:
    """Mock transcript content from Plaud API."""
    return {
        "transcript_id": "rec_001",
        "segments": [
            {
                "speaker": "Alice",
                "text": "Good morning everyone, let's start the standup.",
                "timestamp": "00:00"
            },
            {
                "speaker": "Bob",
                "text": "I completed the user authentication feature yesterday.",
                "timestamp": "00:15"
            },
            {
                "speaker": "Charlie",
                "text": "Working on database migrations today.",
                "timestamp": "00:30"
            }
        ],
        "metadata": {
            "title": "Team Standup",
            "date": "2026-01-28",
            "duration": "15:00"
        }
    }


# ============================================================
# Vector Store Fixtures
# ============================================================

@pytest.fixture
def mock_embeddings() -> List[List[float]]:
    """Mock embeddings for testing (1536 dimensions for text-embedding-3-small)."""
    np.random.seed(42)  # Reproducible embeddings
    return [np.random.rand(1536).tolist() for _ in range(5)]


@pytest.fixture
def sample_search_results() -> List[Dict[str, Any]]:
    """Sample search results from vector store."""
    return [
        {
            "id": "trans_001_seg_0",
            "content": "Discussed quarterly earnings with the team",
            "metadata": {
                "date": "2026-01-15",
                "title": "Q1 Planning",
                "speaker": "Arvind",
                "type": "transcript"
            },
            "score": 0.92
        },
        {
            "id": "journal_20260115_para_0",
            "content": "Had a great planning session today about Q1 goals",
            "metadata": {
                "date": "2026-01-15",
                "mood": "positive",
                "type": "journal"
            },
            "score": 0.87
        },
        {
            "id": "trans_002_seg_3",
            "content": "Revenue projections look strong for Q1",
            "metadata": {
                "date": "2026-01-16",
                "title": "Finance Review",
                "speaker": "CFO",
                "type": "transcript"
            },
            "score": 0.81
        }
    ]


# ============================================================
# Time-based Fixtures
# ============================================================

@pytest.fixture
def date_range_recent() -> Dict[str, datetime]:
    """Recent date range (last 7 days)."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return {
        "start": start_date,
        "end": end_date
    }


@pytest.fixture
def date_range_month() -> Dict[str, datetime]:
    """Monthly date range (last 30 days)."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    return {
        "start": start_date,
        "end": end_date
    }


# ============================================================
# Mock Objects for Testing
# ============================================================

@pytest.fixture
def mock_playwright_page():
    """Mock Playwright page object."""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.wait_for_url = AsyncMock()
    page.fill = AsyncMock()
    page.click = AsyncMock()
    page.query_selector = AsyncMock()
    page.query_selector_all = AsyncMock(return_value=[])
    page.evaluate = AsyncMock()
    return page


@pytest.fixture
def mock_playwright_browser():
    """Mock Playwright browser object."""
    browser = AsyncMock()
    browser.new_page = AsyncMock()
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_chroma_collection():
    """Mock ChromaDB collection."""
    collection = Mock()
    collection.count = Mock(return_value=0)
    collection.add = Mock()
    collection.query = Mock(return_value={
        'ids': [[]],
        'documents': [[]],
        'metadatas': [[]],
        'distances': [[]]
    })
    collection.get = Mock(return_value={
        'ids': [],
        'documents': [],
        'metadatas': []
    })
    collection.delete = Mock()
    return collection


# ============================================================
# Test Data Generators
# ============================================================

@pytest.fixture
def generate_transcript_batch():
    """Factory for generating multiple transcripts."""
    def _generate(count: int = 10) -> List[Dict[str, Any]]:
        transcripts = []
        for i in range(count):
            date = datetime.now() - timedelta(days=i)
            transcripts.append({
                "id": f"rec_{i:03d}",
                "title": f"Meeting {i}",
                "date": date.strftime("%Y-%m-%d"),
                "duration": 900 + (i * 60),
                "segments": [
                    {
                        "speaker": "Speaker A",
                        "text": f"This is segment {j} of meeting {i}",
                        "start_time_ms": j * 3000,
                        "end_time_ms": (j + 1) * 3000
                    }
                    for j in range(3)
                ]
            })
        return transcripts
    return _generate


@pytest.fixture
def generate_journal_batch():
    """Factory for generating multiple journal entries."""
    def _generate(count: int = 10) -> List[Dict[str, Any]]:
        journals = []
        for i in range(count):
            date = datetime.now() - timedelta(days=i)
            journals.append({
                "id": f"journal_{date.strftime('%Y%m%d')}",
                "date": date.strftime("%Y-%m-%d"),
                "paragraphs": [
                    f"Paragraph {j} of journal entry {i}. Some interesting content here."
                    for j in range(3)
                ],
                "metadata": {
                    "mood": "neutral",
                    "category": "work"
                }
            })
        return journals
    return _generate


# ============================================================
# Utility Functions
# ============================================================

@pytest.fixture
def assert_valid_embedding():
    """Utility to validate embedding structure."""
    def _validate(embedding: List[float], expected_dim: int = 1536) -> bool:
        assert isinstance(embedding, list), "Embedding must be a list"
        assert len(embedding) == expected_dim, f"Embedding must have {expected_dim} dimensions"
        assert all(isinstance(x, (int, float)) for x in embedding), "All elements must be numeric"
        return True
    return _validate


@pytest.fixture
def assert_valid_metadata():
    """Utility to validate metadata structure."""
    def _validate(metadata: Dict[str, Any], required_fields: List[str] = None) -> bool:
        assert isinstance(metadata, dict), "Metadata must be a dictionary"
        if required_fields:
            for field in required_fields:
                assert field in metadata, f"Required field '{field}' missing from metadata"
        return True
    return _validate


# ============================================================
# Performance Testing Utilities
# ============================================================

@pytest.fixture
def measure_execution_time():
    """Utility to measure execution time."""
    import time

    def _measure(func, *args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        return result, elapsed

    return _measure


# ============================================================
# Environment Variables for Tests
# ============================================================

@pytest.fixture(autouse=True)
def test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("MEMEX_TEST_MODE", "true")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")  # Reduce noise in tests


# ============================================================
# Integration Test Fixtures (Gmail and Calendar)
# ============================================================

# Import integration-specific fixtures
pytest_plugins = ["memex.tests.fixtures_integrations"]
