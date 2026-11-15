"""
Unit tests for FreshnessScorer module.
Tests the evidence-based heuristic scoring engine, weights, bounds, and summary calculations.
"""

import pytest
from models import (
    FactualClaim,
    EvidenceSource,
    VerificationStatus,
    ClaimVerificationResult,
)
from freshness_scorer import FreshnessScorer


@pytest.fixture
def scorer():
    return FreshnessScorer()


def test_verified_score_calculation(scorer):
    claim = FactualClaim(
        id=1,
        claim_text="Python was created by Guido van Rossum.",
        time_sensitive=False,
        search_query="Python creator",
    )
    evidence = [
        EvidenceSource(
            title="Python FAQ",
            url="https://docs.python.org/3/faq",
            snippet="Conceived by Guido van Rossum.",
            score=0.99,
            domain="docs.python.org",
            is_authoritative=True,
            published_date="2024-01-01",
        ),
        EvidenceSource(
            title="Wikipedia Python",
            url="https://en.wikipedia.org/wiki/Python",
            snippet="Created by Guido van Rossum.",
            score=0.95,
            domain="wikipedia.org",
            is_authoritative=True,
            published_date="2024-01-01",
        ),
    ]

    score, breakdown = scorer.calculate_claim_score(VerificationStatus.VERIFIED, claim, evidence)
    assert score == 100.0
    assert breakdown["authoritative_sources_count"] == 2


def test_outdated_score_penalty(scorer):
    claim = FactualClaim(
        id=2,
        claim_text="GPT-4 costs $30 per 1M input tokens.",
        time_sensitive=True,
        search_query="GPT-4 pricing",
    )
    evidence = [
        EvidenceSource(
            title="OpenAI Pricing",
            url="https://openai.com/api/pricing",
            snippet="GPT-4o costs $2.50 per 1M input.",
            score=0.99,
            domain="openai.com",
            is_authoritative=True,
        )
    ]

    score, breakdown = scorer.calculate_claim_score(VerificationStatus.OUTDATED, claim, evidence)
    # Outdated claim should have a low score between 10 and 20
    assert 10.0 <= score <= 20.0
    assert breakdown["is_time_sensitive"] is True


def test_aggregate_summary_calculation(scorer):
    c1 = FactualClaim(id=1, claim_text="Fact 1", time_sensitive=True, search_query="q1")
    c2 = FactualClaim(id=2, claim_text="Fact 2", time_sensitive=False, search_query="q2")

    res1 = ClaimVerificationResult(
        claim=c1,
        status=VerificationStatus.OUTDATED,
        freshness_score=15.0,
        explanation="Superseded",
        verification_timestamp="2024-11-13T10:00:00Z",
    )
    res2 = ClaimVerificationResult(
        claim=c2,
        status=VerificationStatus.VERIFIED,
        freshness_score=100.0,
        explanation="Supported",
        verification_timestamp="2024-11-13T10:00:00Z",
    )

    summary = scorer.calculate_aggregate_summary([res1, res2])
    # Total weighted points = (15.0 * 1.5) + (100.0 * 1.0) = 22.5 + 100 = 122.5
    # Total weight = 1.5 + 1.0 = 2.5
    # Expected overall score = 122.5 / 2.5 = 49.0
    assert summary.overall_score == 49.0
    assert summary.total_claims == 2
    assert summary.verified_count == 1
    assert summary.outdated_count == 1
    assert "High Stale" in summary.score_label
