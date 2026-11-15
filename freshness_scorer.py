"""
StaleGuard - Freshness Scoring Engine
Calculates transparent, evidence-based freshness scores (0 - 100) for
individual claims and the aggregate AI answer.
Clearly documented heuristic: Not a calibrated probability, but an empirical evidence-based index.
"""

import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
from config import config
from models import (
    FactualClaim,
    EvidenceSource,
    VerificationStatus,
    ClaimVerificationResult,
    FreshnessSummary,
)

logger = logging.getLogger("deStale.FreshnessScorer")


class FreshnessScorer:
    """
    Evidence-based Freshness Scoring Engine.
    Evaluates verification status, domain authority, temporal freshness,
    and source consensus to compute normalized 0-100 scores.
    """

    def calculate_claim_score(
        self,
        status: VerificationStatus,
        claim: FactualClaim,
        evidence: List[EvidenceSource],
        confidence: float = 0.85,
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Computes a 0-100 freshness score for an individual factual claim.

        Returns:
            Tuple of (score, breakdown_dict)
        """
        # Step 1: Base score by verification classification
        base_scores = {
            VerificationStatus.VERIFIED: config.SCORE_VERIFIED_BASE,        # 100.0
            VerificationStatus.OUTDATED: config.SCORE_OUTDATED_BASE,        # 15.0
            VerificationStatus.CONTRADICTED: config.SCORE_CONTRADICTED_BASE, # 0.0
            VerificationStatus.UNCERTAIN: config.SCORE_UNCERTAIN_BASE,      # 45.0
            VerificationStatus.INSUFFICIENT_EVIDENCE: config.SCORE_INSUFFICIENT_BASE, # 50.0
        }
        raw_score = base_scores.get(status, 50.0)

        # Step 2: Evidence Authority Adjustment
        auth_sources = [e for e in evidence if e.is_authoritative]
        auth_count = len(auth_sources)
        total_sources = len(evidence)

        authority_adjustment = 0.0
        recency_adjustment = 0.0

        if status == VerificationStatus.VERIFIED:
            # Rule: If verified by 2+ authoritative sources, maintain top score
            if auth_count >= 2:
                authority_adjustment = 0.0  # Already 100
            elif auth_count == 1:
                # Single authoritative source: slight caution deduction
                authority_adjustment = -5.0
            elif total_sources <= 1:
                # Strict rule: Single non-authoritative source cannot produce 100% verified
                authority_adjustment = -25.0

        elif status == VerificationStatus.OUTDATED:
            # If confirmed outdated by authoritative modern documentation, score remains strictly low
            if auth_count >= 1:
                raw_score = 10.0
            else:
                raw_score = 20.0

        elif status == VerificationStatus.CONTRADICTED:
            # Completely refuted
            raw_score = 0.0

        elif status == VerificationStatus.INSUFFICIENT_EVIDENCE:
            # If time-sensitive and zero evidence was found, risk is higher
            if claim.time_sensitive:
                raw_score = 40.0

        # Step 3: Recency heuristic (detecting 2024-2026 timestamps in evidence)
        current_year_str = str(datetime.now().year)
        recent_sources = [
            e for e in evidence if e.published_date and (current_year_str in e.published_date or "2024" in e.published_date)
        ]
        if recent_sources and status == VerificationStatus.VERIFIED:
            recency_adjustment = 0.0  # confirmed fresh
        elif claim.time_sensitive and not recent_sources and status == VerificationStatus.VERIFIED:
            # Time-sensitive claim without recent date evidence
            recency_adjustment = -10.0

        # Final score bounded between 0 and 100
        final_score = max(0.0, min(100.0, raw_score + authority_adjustment + recency_adjustment))

        breakdown = {
            "base_score": raw_score,
            "status": status.value,
            "authoritative_sources_count": auth_count,
            "total_sources_count": total_sources,
            "authority_adjustment": authority_adjustment,
            "recency_adjustment": recency_adjustment,
            "is_time_sensitive": claim.time_sensitive,
            "final_score": round(final_score, 1),
        }

        return round(final_score, 1), breakdown

    def calculate_aggregate_summary(
        self, claim_results: List[ClaimVerificationResult]
    ) -> FreshnessSummary:
        """
        Computes overall freshness score, metrics distribution, and qualitative label.

        Args:
            claim_results: List of completed claim verification results.

        Returns:
            FreshnessSummary model.
        """
        if not claim_results:
            return FreshnessSummary(
                overall_score=0.0,
                score_label="No Claims Analyzed",
                total_claims=0,
                summary_narrative="No verifiable factual claims were found in the provided text.",
            )

        total_weight = 0.0
        weighted_score_sum = 0.0

        verified_cnt = 0
        outdated_cnt = 0
        contradicted_cnt = 0
        insufficient_cnt = 0
        uncertain_cnt = 0

        for res in claim_results:
            # Time-sensitive claims carry 1.5x weight in freshness calculation
            weight = 1.5 if res.claim.time_sensitive else 1.0
            weighted_score_sum += res.freshness_score * weight
            total_weight += weight

            if res.status == VerificationStatus.VERIFIED:
                verified_cnt += 1
            elif res.status == VerificationStatus.OUTDATED:
                outdated_cnt += 1
            elif res.status == VerificationStatus.CONTRADICTED:
                contradicted_cnt += 1
            elif res.status == VerificationStatus.INSUFFICIENT_EVIDENCE:
                insufficient_cnt += 1
            elif res.status == VerificationStatus.UNCERTAIN:
                uncertain_cnt += 1

        overall_score = round(weighted_score_sum / total_weight, 1) if total_weight > 0 else 0.0

        # Qualitative classification
        if overall_score >= 80.0:
            score_label = "Fresh & Accurate"
        elif overall_score >= 50.0:
            score_label = "Moderate Stale Risk"
        else:
            score_label = "High Stale / Outdated Risk"

        # Generate summary narrative
        issues = []
        if outdated_cnt > 0:
            issues.append(f"{outdated_cnt} outdated claim(s) superseded by recent developments")
        if contradicted_cnt > 0:
            issues.append(f"{contradicted_cnt} claim(s) directly contradicted by web evidence")
        if uncertain_cnt > 0:
            issues.append(f"{uncertain_cnt} claim(s) with conflicting or unverified sources")

        if not issues:
            narrative = (
                f"Analysis completed across {len(claim_results)} factual claims. "
                f"All evaluated statements are corroborated by current authoritative live internet sources."
            )
        else:
            issue_text = ", and ".join(issues)
            narrative = (
                f"Analysis detected potential reliability issues: {issue_text}. "
                f"{verified_cnt} out of {len(claim_results)} claims were fully verified as current."
            )

        heuristic_breakdown = {
            "formula": "Weighted Average: Sum(Claim_Score * Weight) / Total_Weight",
            "weights": "Standard claims = 1.0x, Time-sensitive claims (pricing/versions/dates) = 1.5x",
            "score_ranges": {
                "80-100": "Fresh & Accurate",
                "50-79": "Moderate Stale Risk",
                "0-49": "High Stale / Outdated Risk",
            },
            "total_weighted_points": round(weighted_score_sum, 1),
            "total_weight_divisor": round(total_weight, 1),
        }

        return FreshnessSummary(
            overall_score=overall_score,
            score_label=score_label,
            total_claims=len(claim_results),
            verified_count=verified_cnt,
            outdated_count=outdated_cnt,
            contradicted_count=contradicted_cnt,
            insufficient_count=insufficient_cnt,
            uncertain_count=uncertain_cnt,
            summary_narrative=narrative,
            heuristic_breakdown=heuristic_breakdown,
        )
