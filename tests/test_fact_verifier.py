"""
Unit tests for FactVerifier module.
Tests classification (Verified, Outdated, Contradicted), guardrail enforcement, and corrections.
"""

import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone
from models import FactualClaim, EvidenceSource, VerificationStatus
from bifrost_client import BifrostClient
from fact_verifier import FactVerifier


@pytest.fixture
def sample_claim():
    return FactualClaim(
        id=1,
        claim_text="Next.js 13 is the latest version of the framework.",
        time_sensitive=True,
        temporal_context="Framework release",
        search_query="Next.js latest version",
        keywords=["Next.js", "version"],
    )


@pytest.fixture
def sample_evidence():
    return [
        EvidenceSource(
            title="Next.js 15 Release Notes",
            url="https://nextjs.org/blog/next-15",
            snippet="Next.js 15 is now GA with React 19 support.",
            score=0.98,
            published_date=datetime.now(timezone.utc).date().isoformat(),
            domain="nextjs.org",
            is_authoritative=True,
        )
    ]


def test_fact_verifier_outdated_classification(sample_claim, sample_evidence):
    mock_bifrost = MagicMock(spec=BifrostClient)
    mock_bifrost.create_chat_completion.return_value = """
    ```json
    {
      "status": "Outdated",
      "explanation": "Next.js 15 has been released by Vercel, making Next.js 13 outdated.",
      "suggested_correction": "Next.js 15 is the current latest major version.",
      "confidence": 0.96
    }
    ```
    """

    verifier = FactVerifier(bifrost_client=mock_bifrost)
    result = verifier.verify_claim(sample_claim, sample_evidence)

    assert result.status == VerificationStatus.OUTDATED
    assert "Next.js 15" in result.suggested_correction
    assert result.confidence == 0.96
    assert len(result.evidence_sources) == 1


def test_fact_verifier_contradicted_heuristic():
    mock_bifrost = MagicMock(spec=BifrostClient)
    mock_bifrost.create_chat_completion.side_effect = Exception("Offline gateway")

    verifier = FactVerifier(bifrost_client=mock_bifrost)
    claim = FactualClaim(
        id=2,
        claim_text="Twitter is led by CEO Jack Dorsey.",
        time_sensitive=True,
        search_query="Twitter CEO Jack Dorsey Linda Yaccarino",
    )
    evidence = [
        EvidenceSource(
            title="Reuters Twitter CEO",
            url="https://reuters.com/tech",
            snippet="Linda Yaccarino was named CEO after Jack Dorsey stepped down.",
            score=0.95,
            published_date="2023-06-05",
            domain="reuters.com",
            is_authoritative=True,
        )
    ]

    result = verifier.verify_claim(claim, evidence)
    # A 2023 leadership article cannot establish who holds the role in 2026.
    assert result.status == VerificationStatus.INSUFFICIENT_EVIDENCE
    assert result.suggested_correction is None


def test_current_superlative_is_not_verified_by_entity_mention_only():
    mock_bifrost = MagicMock(spec=BifrostClient)
    mock_bifrost.create_chat_completion.return_value = '''
    {
      "status": "Verified / Supported",
      "explanation": "The source mentions Claude 2.",
      "suggested_correction": null,
      "confidence": 0.99
    }
    '''
    claim = FactualClaim(
        id=3,
        claim_text="Claude 2 is Anthropic's newest and most capable model.",
        time_sensitive=True,
        search_query="Anthropic latest model lineup",
    )
    evidence = [EvidenceSource(
        title="Claude 2 model overview",
        url="https://www.anthropic.com/news/claude-2",
        snippet="Claude 2 has a 100k token context window.",
        score=0.99,
        published_date=datetime.now(timezone.utc).date().isoformat(),
        domain="anthropic.com",
        is_authoritative=True,
    )]
    result = FactVerifier(bifrost_client=mock_bifrost).verify_claim(claim, evidence)
    assert result.status == VerificationStatus.INSUFFICIENT_EVIDENCE
    assert "do not establish" in result.explanation


def test_empty_evidence_never_calls_model_or_verifies():
    mock_bifrost = MagicMock(spec=BifrostClient)
    claim = FactualClaim(id=4, claim_text="A static factual statement is true.", search_query="static fact")
    result = FactVerifier(bifrost_client=mock_bifrost).verify_claim(claim, [])
    assert result.status == VerificationStatus.INSUFFICIENT_EVIDENCE
    mock_bifrost.create_chat_completion.assert_not_called()
