"""
deStale - Data Models Module
Defines Pydantic schemas for factual claims, live search evidence,
claim verification results, and aggregate freshness reports.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    """Classification status for verified factual claims."""
    VERIFIED = "Verified / Supported"
    OUTDATED = "Outdated"
    CONTRADICTED = "Contradicted"
    INSUFFICIENT_EVIDENCE = "Insufficient Evidence"
    UNCERTAIN = "Uncertain"

    @property
    def badge_color(self) -> str:
        """Hex color code corresponding to the verification status."""
        mapping = {
            VerificationStatus.VERIFIED: "#10b981",       # Emerald green
            VerificationStatus.OUTDATED: "#f59e0b",       # Amber / Orange
            VerificationStatus.CONTRADICTED: "#ef4444",   # Crimson red
            VerificationStatus.INSUFFICIENT_EVIDENCE: "#6b7280", # Slate grey
            VerificationStatus.UNCERTAIN: "#8b5cf6",      # Purple / Violet
        }
        return mapping.get(self, "#6b7280")

    @property
    def icon(self) -> str:
        """Emoji/Icon for UI display."""
        mapping = {
            VerificationStatus.VERIFIED: "✅",
            VerificationStatus.OUTDATED: "⏳",
            VerificationStatus.CONTRADICTED: "❌",
            VerificationStatus.INSUFFICIENT_EVIDENCE: "🔍",
            VerificationStatus.UNCERTAIN: "⚠️",
        }
        return mapping.get(self, "❓")


class EvidenceSource(BaseModel):
    """Evidence item gathered from live internet search via Tavily."""
    title: str = Field(..., description="Title of the webpage")
    url: str = Field(..., description="Canonical URL of the source")
    snippet: str = Field(..., description="Relevant text excerpt or snippet")
    score: float = Field(default=0.0, description="Relevance score from search engine")
    published_date: Optional[str] = Field(default=None, description="Published or crawled date if available")
    domain: str = Field(default="", description="Base domain name of the source")
    is_authoritative: bool = Field(default=False, description="Whether the domain belongs to known high-authority sources")


class FactualClaim(BaseModel):
    """An individual atomic factual claim extracted from AI-generated text."""
    id: int = Field(..., description="Sequence identifier for the claim")
    claim_text: str = Field(..., description="Atomic factual assertion stripped of subjective rhetoric")
    time_sensitive: bool = Field(default=False, description="Whether this claim involves dates, prices, versions, or dynamic rules")
    temporal_context: Optional[str] = Field(default=None, description="Identified timeframe or version context (e.g., 'as of 2023', 'v2.1')")
    search_query: str = Field(..., description="Optimized, concise web search query targeting this claim")
    keywords: List[str] = Field(default_factory=list, description="Key entity and topic keywords")


class ClaimVerificationResult(BaseModel):
    """Verification outcome and freshness evaluation for an individual claim."""
    claim: FactualClaim
    status: VerificationStatus
    freshness_score: float = Field(..., ge=0.0, le=100.0, description="Individual claim freshness score (0 - 100)")
    explanation: str = Field(..., description="Detailed AI reasoning for why the status was assigned")
    suggested_correction: Optional[str] = Field(default=None, description="Current accurate information if claim is outdated or contradicted")
    evidence_sources: List[EvidenceSource] = Field(default_factory=list, description="Authoritative sources gathered for this claim")
    verification_timestamp: str = Field(..., description="ISO timestamp of when the verification took place")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in the verification assessment")


class FreshnessSummary(BaseModel):
    """Aggregate freshness metrics across all claims."""
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Weighted freshness score (0 - 100)")
    score_label: str = Field(..., description="Human-friendly category: Fresh, Moderate Stale Risk, High Stale Risk")
    total_claims: int = Field(default=0)
    verified_count: int = Field(default=0)
    outdated_count: int = Field(default=0)
    contradicted_count: int = Field(default=0)
    insufficient_count: int = Field(default=0)
    uncertain_count: int = Field(default=0)
    summary_narrative: str = Field(default="", description="Executive summary of freshness findings")
    heuristic_breakdown: Dict[str, Any] = Field(default_factory=dict, description="Transparent explanation of scoring weights")


class DeStaleReport(BaseModel):
    """Full analysis report combining user input, claim results, and summary."""
    report_id: str
    created_at: str
    original_text: str
    summary: FreshnessSummary
    claim_results: List[ClaimVerificationResult]
    is_demo_mode: bool = False
    ai_model_name: str = "Bifrost AI Gateway (gpt-4o-mini)"
    search_engine: str = "Tavily Live Web Search"


# Backward-compatible alias
StaleGuardReport = DeStaleReport
