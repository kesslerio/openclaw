#!/usr/bin/env python
"""
Test script for Memex HISTORIAN Search API
Verifies all endpoints are working correctly
"""

import requests
import sys
from typing import Dict, Any

API_URL = "http://localhost:8765"


def test_health() -> bool:
    """Test health check endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/")
        response.raise_for_status()
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "indexed_chunks" in data

        print(f"  ✓ Health check passed")
        print(f"    - Status: {data['status']}")
        print(f"    - Indexed chunks: {data['indexed_chunks']}")
        return True
    except Exception as e:
        print(f"  ✗ Health check failed: {e}")
        return False


def test_stats() -> bool:
    """Test statistics endpoint"""
    print("\nTesting stats endpoint...")
    try:
        response = requests.get(f"{API_URL}/stats")
        response.raise_for_status()
        data = response.json()

        assert "total_chunks" in data
        assert "embedding_model" in data
        assert "collection" in data

        print(f"  ✓ Stats endpoint passed")
        print(f"    - Total chunks: {data['total_chunks']}")
        print(f"    - Model: {data['embedding_model']}")
        print(f"    - Collection: {data['collection']}")
        return True
    except Exception as e:
        print(f"  ✗ Stats endpoint failed: {e}")
        return False


def test_search() -> bool:
    """Test search endpoint"""
    print("\nTesting search endpoint...")

    # Test basic search
    try:
        params = {"q": "meeting", "limit": 3}
        response = requests.get(f"{API_URL}/search", params=params)
        response.raise_for_status()
        data = response.json()

        assert "query" in data
        assert "results" in data
        assert "total" in data
        assert data["query"] == "meeting"
        assert isinstance(data["results"], list)
        assert len(data["results"]) <= 3

        print(f"  ✓ Basic search passed")
        print(f"    - Query: {data['query']}")
        print(f"    - Results returned: {data['total']}")

        if data["results"]:
            result = data["results"][0]
            print(f"    - Top result score: {result['score']:.4f}")
            print(f"    - Text preview: {result['text'][:80]}...")

        return True
    except Exception as e:
        print(f"  ✗ Search endpoint failed: {e}")
        return False


def test_search_with_filter() -> bool:
    """Test search with speaker filter"""
    print("\nTesting search with speaker filter...")

    try:
        params = {"q": "discussion", "limit": 5, "speaker": "TestSpeaker"}
        response = requests.get(f"{API_URL}/search", params=params)
        response.raise_for_status()
        data = response.json()

        print(f"  ✓ Filtered search passed")
        print(f"    - Results: {data['total']}")
        return True
    except Exception as e:
        print(f"  ✗ Filtered search failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Memex HISTORIAN Search API Test Suite")
    print("=" * 60)

    tests = [
        ("Health Check", test_health),
        ("Statistics", test_stats),
        ("Search", test_search),
        ("Filtered Search", test_search_with_filter),
    ]

    results = []
    for name, test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"\n✗ {name} crashed: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    for i, (name, _) in enumerate(tests):
        status = "✓ PASS" if results[i] else "✗ FAIL"
        print(f"{status} - {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
