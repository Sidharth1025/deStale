"""
Unit tests for TavilySearchClient module.
Tests live search mocking, session caching (deduplication), and domain authority heuristics.
"""

import pytest
from unittest.mock import patch, MagicMock
from models import EvidenceSource
from tavily_search import TavilySearchClient
from utils import is_authoritative_domain, extract_domain


def test_domain_extraction_and_authority():
    assert extract_domain("https://docs.python.org/3/whatsnew/3.12.html") == "docs.python.org"
    assert extract_domain("https://www.reuters.com/technology/article") == "reuters.com"
    assert extract_domain("https://random-unverified-blog.xyz/post") == "random-unverified-blog.xyz"

    assert is_authoritative_domain("https://docs.python.org/3/") is True
    assert is_authoritative_domain("https://openai.com/api/pricing/") is True
    assert is_authoritative_domain("https://harvard.edu/research") is True
    assert is_authoritative_domain("https://unverified-forum.com") is False


@patch("requests.post")
def test_tavily_search_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "title": "OpenAI Pricing",
                "url": "https://openai.com/api/pricing/",
                "content": "GPT-4o costs $2.50 per 1M input tokens.",
                "score": 0.95,
                "published_date": "2024-10-01",
            }
        ]
    }
    mock_post.return_value = mock_response

    client = TavilySearchClient(api_key="tvly-mock-key-123")
    results = client.search_claim("OpenAI GPT-4 pricing")

    assert len(results) == 1
    assert results[0].domain == "openai.com"
    assert results[0].is_authoritative is True
    assert "GPT-4o" in results[0].snippet


@patch("requests.post")
def test_tavily_caching_deduplication(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [{"title": "Cached Title", "url": "https://python.org", "content": "Python 3.12", "score": 0.9}]
    }
    mock_post.return_value = mock_response

    client = TavilySearchClient(api_key="tvly-mock-key-123")
    # First search triggers network call
    res1 = client.search_claim("python latest version")
    # Second search with same query should hit cache without calling requests.post again
    res2 = client.search_claim("python latest version")

    assert len(res1) == 1
    assert len(res2) == 1
    assert mock_post.call_count == 1  # Only called once due to cache
