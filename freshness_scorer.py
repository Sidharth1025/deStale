"""
deStale - Freshness Scoring Engine
Produces a transparent heuristic index (not a probability) from the verdict,
source authority, and actual publication dates.
"""

import logging
from datetime import datetime, timezone, date
from typing import List, Dict, Any, Tuple

from config import config
from models import FactualClaim, EvidenceSource, VerificationStatus, ClaimVerificationResult, FreshnessSummary

logger = logging.getLogger("deStale.FreshnessScorer")


class FreshnessScorer:
    """Evidence-based 0-100 scoring with date-aware recency adjustments."""

    def calculate_claim_score(
        self,
        status: VerificationStatus,
        claim: FactualClaim,
        evidence: List[EvidenceSource],
        confidence: float = 0.85,
    ) -> Tuple[float, Dict[str, Any]]:
        base_scores = {
            VerificationStatus.VERIFIED: config.SCORE_VERIFIED_BASE,
            VerificationStatus.OUTDATED: config.SCORE_OUTDATED_BASE,
            VerificationStatus.CONTRADICTED: config.SCORE_CONTRADICTED_BASE,
            VerificationStatus.UNCERTAIN: config.SCORE_UNCERTAIN_BASE,
            VerificationStatus.INSUFFICIENT_EVIDENCE: config.SCORE_INSUFFICIENT_BASE,
        }
        raw_score = float(base_scores.get(status, 50.0))
        authority_adjustment = 0.0
        recency_adjustment = 0.0

        authoritative = [e for e in evidence if e.is_authoritative]
        domains = {e.domain.lower().removeprefix("www.") for e in authoritative if e.domain}
        if status == VerificationStatus.VERIFIED:
            if len(domains) >= 2:
                authority_adjustment = 0.0
            elif len(authoritative) == 1:
                authority_adjustment = -8.0
            else:
                authority_adjustment = -30.0
        elif status == VerificationStatus.OUTDATED:
            raw_score = 10.0 if authoritative else 20.0
        elif status == VerificationStatus.CONTRADICTED:
            raw_score = 0.0
        elif status == VerificationStatus.INSUFFICIENT_EVIDENCE:
            raw_score = 35.0 if claim.time_sensitive else 45.0

        # Use real source dates rather than a hard-coded year check. Undated
        # sources cannot establish freshness for a dynamic claim.
        dated_sources = []
        today = datetime.now(timezone.utc).date()
        for source in authoritative:
            published = self._parse_date(source.published_date)
            if published and published <= today:
                dated_sources.append((today - published).days)
        newest_age = min(dated_sources) if dated_sources else None

        if status == VerificationStatus.VERIFIED and claim.time_sensitive:
            if newest_age is None:
                recency_adjustment = -20.0
            elif newest_age <= 180:
                recency_adjustment = 0.0
            elif newest_age <= 365:
                recency_adjustment = -8.0
            elif newest_age <= 540:
                recency_adjustment = -15.0
            else:
                recency_adjustment = -25.0

        final_score = max(0.0, min(100.0, raw_score + authority_adjustment + recency_adjustment))
        breakdown = {
            "base_score": round(raw_score, 1),
            "status": status.value,
            "authoritative_sources_count": len(authoritative),
            "independent_authoritative_domains": len(domains),
            "total_sources_count": len(evidence),
            "authority_adjustment": round(authority_adjustment, 1),
            "recency_adjustment": round(recency_adjustment, 1),
            "newest_authoritative_source_age_days": newest_age,
            "is_time_sensitive": claim.time_sensitive,
            "confidence": round(max(0.0, min(1.0, confidence)), 2),
            "final_score": round(final_score, 1),
            "score_note": "Heuristic index, not a statistical probability.",
        }
        return round(final_score, 1), breakdown

    @staticmethod
    def _parse_date(value: str | None) -> date | None:
        if not value:
            return None
        try:
            return date.fromisoformat(str(value).strip()[:10])
        except ValueError:
            return None

    def calculate_aggregate_summary(self, claim_results: List[ClaimVerificationResult]) -> FreshnessSummary:
        if not claim_results:
            return FreshnessSummary(
                overall_score=0.0,
                score_label="No Claims Analyzed",
                total_claims=0,
                summary_narrative="No verifiable factual claims were found in the provided text.",
            )

        weighted_score_sum = 0.0
        total_weight = 0.0
        counts = {
            VerificationStatus.VERIFIED: 0,
            VerificationStatus.OUTDATED: 0,
            VerificationStatus.CONTRADICTED: 0,
            VerificationStatus.INSUFFICIENT_EVIDENCE: 0,
            VerificationStatus.UNCERTAIN: 0,
        }
        for result in claim_results:
            weight = 1.5 if result.claim.time_sensitive else 1.0
            weighted_score_sum += result.freshness_score * weight
            total_weight += weight
            counts[result.status] = counts.get(result.status, 0) + 1

        overall_score = round(weighted_score_sum / total_weight, 1) if total_weight else 0.0

        # Separate lack of evidence from actual stale information
        verified = counts[VerificationStatus.VERIFIED]
        outdated = counts[VerificationStatus.OUTDATED]
        contradicted = counts[VerificationStatus.CONTRADICTED]
        insufficient = counts[VerificationStatus.INSUFFICIENT_EVIDENCE]
        uncertain = counts[VerificationStatus.UNCERTAIN]

        if verified + outdated + contradicted == 0:
            label = "Insufficient Evidence"
        elif overall_score >= 80:
            label = "Fresh & Accurate"
        elif overall_score >= 50:
            label = "Moderate Stale Risk"
        else:
            label = "High Stale / Outdated Risk"

        issues = []
        if counts[VerificationStatus.OUTDATED]:
            issues.append(f"{counts[VerificationStatus.OUTDATED]} outdated claim(s) superseded by newer information")
        if counts[VerificationStatus.CONTRADICTED]:
            issues.append(f"{counts[VerificationStatus.CONTRADICTED]} claim(s) contradicted by evidence")
        if counts[VerificationStatus.UNCERTAIN]:
            issues.append(f"{counts[VerificationStatus.UNCERTAIN]} claim(s) with conflicting or inconclusive evidence")
        if counts[VerificationStatus.INSUFFICIENT_EVIDENCE]:
            issues.append(f"{counts[VerificationStatus.INSUFFICIENT_EVIDENCE]} claim(s) without enough evidence")

        verified = counts[VerificationStatus.VERIFIED]
        if issues:
            narrative = (
                f"Analysis found {', '.join(issues)}. "
                f"{verified} of {len(claim_results)} claims met the evidence threshold for verification."
            )
        else:
            narrative = (
                f"Analysis completed across {len(claim_results)} factual claims. "
                "All claims met the configured evidence threshold for verification."
            )

        breakdown = {
            "formula": "Weighted Average: Sum(Claim_Score * Weight) / Total_Weight",
            "weights": "Standard claims = 1.0x; time-sensitive claims = 1.5x",
            "score_ranges": {
                "80-100": "Fresh & Accurate",
                "50-79": "Moderate Stale Risk",
                "0-49": "High Stale / Outdated Risk",
            },
            "total_weighted_points": round(weighted_score_sum, 1),
            "total_weight_divisor": round(total_weight, 1),
            "counts": {status.value: count for status, count in counts.items()},
            "note": "The score is a transparent heuristic index, not a probability of truth.",
        }
        return FreshnessSummary(
            overall_score=overall_score,
            score_label=label,
            total_claims=len(claim_results),
            verified_count=verified,
            outdated_count=counts[VerificationStatus.OUTDATED],
            contradicted_count=counts[VerificationStatus.CONTRADICTED],
            insufficient_count=counts[VerificationStatus.INSUFFICIENT_EVIDENCE],
            uncertain_count=counts[VerificationStatus.UNCERTAIN],
            summary_narrative=narrative,
            heuristic_breakdown=breakdown,
        )
