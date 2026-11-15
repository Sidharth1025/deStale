"""
Unit tests for FactVerifier module.
Tests classification (Verified, Outdated, Contradicted), guardrail enforcement, and corrections.
"""

import pytest
from unittest.mock import MagicMock
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
            published_date="2024-10-21",
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
    assert result.status == VerificationStatus.CONTRADICTED
    assert "Linda Yaccarino" in (result.suggested_correction or result.explanation)
