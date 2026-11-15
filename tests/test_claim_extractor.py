"""
Unit tests for ClaimExtractor module.
Uses mocked Bifrost Gateway to test extraction, parsing, and heuristic fallback.
"""

import pytest
from unittest.mock import MagicMock
from models import FactualClaim
from bifrost_client import BifrostClient
from claim_extractor import ClaimExtractor


@pytest.fixture
def mock_bifrost_client():
    client = MagicMock(spec=BifrostClient)
    return client


def test_claim_extractor_with_bifrost(mock_bifrost_client):
    mock_bifrost_client.create_chat_completion.return_value = """
    ```json
    {
      "claims": [
        {
          "id": 1,
          "claim_text": "OpenAI GPT-4 costs $30 per 1M input tokens.",
          "time_sensitive": true,
          "temporal_context": "2023 pricing",
          "search_query": "OpenAI GPT-4 pricing per million tokens",
          "keywords": ["OpenAI", "GPT-4", "pricing"]
        }
      ]
    }
    ```
    """
    extractor = ClaimExtractor(bifrost_client=mock_bifrost_client)
    input_text = "OpenAI GPT-4 costs $30 per 1M input tokens. It is an amazing tool."

    claims = extractor.extract_claims(input_text)
    assert len(claims) == 1
    assert claims[0].id == 1
    assert claims[0].claim_text == "OpenAI GPT-4 costs $30 per 1M input tokens."
    assert claims[0].time_sensitive is True
    assert "OpenAI" in claims[0].keywords


def test_claim_extractor_heuristic_fallback(mock_bifrost_client):
    # Simulate network or gateway failure
    mock_bifrost_client.create_chat_completion.side_effect = Exception("Gateway unreachable")
    extractor = ClaimExtractor(bifrost_client=mock_bifrost_client)

    input_text = (
        "Next.js 13 is the latest version of the framework. "
        "Python 3.9 is the current release. "
        "Guido van Rossum invented Python."
    )

    claims = extractor.extract_claims(input_text)
    assert len(claims) >= 2
    assert any("next.js" in c.claim_text.lower() for c in claims)
    # Check time sensitivity detection for version/latest
    assert any(c.time_sensitive for c in claims)


def test_claim_extractor_empty_input(mock_bifrost_client):
    extractor = ClaimExtractor(bifrost_client=mock_bifrost_client)
    with pytest.raises(ValueError):
        extractor.extract_claims("Too short")
