"""
deStale - Factual Claim Extractor Module
Uses Bifrost AI Gateway to extract atomic, time-sensitive factual claims
from user-submitted AI-generated answers, filtering out subjective prose.
"""

import re
import logging
from typing import List, Optional
from config import config
from models import FactualClaim
from bifrost_client import BifrostClient, BifrostAPIError
from utils import extract_json_from_llm_response, sanitize_input_text, sanitize_for_prompt_injection

logger = logging.getLogger("deStale.ClaimExtractor")

SYSTEM_CLAIM_EXTRACTION_PROMPT = """You are an expert AI fact-checking preprocessor in the deStale verification engine.
Your task is to analyze an AI-generated answer, decompose it into individual atomic factual claims, and prepare them for web verification.

Follow these strict extraction guidelines:
1. ATOMICITY: Each claim must express a single verifiable factual proposition (e.g., a specific price, version, release date, corporate officer, rule, statistic).
2. DISCARD SUBJECTIVITY: Omit opinions, subjective evaluations, introductory pleasantries ("Sure, here is the info"), rhetorical questions, and stylistic fluff.
3. PRESERVE SPECIFICITY: Keep exact numbers, version numbers, dates, company names, and entities intact.
4. TIME-SENSITIVITY: Identify whether the claim depends on current time (e.g. current pricing, current CEO, latest software version, active law). Set "time_sensitive": true for dynamic facts.
5. TEMPORAL CONTEXT: If the text implies a specific year or timeframe, capture it in "temporal_context".
6. SEARCH QUERY OPTIMIZATION: Generate a concise, high-precision search query (3-6 words) that will retrieve authoritative live sources. Preserve the key entity, exact number/version, and the specific attribute being checked.
7. SUPERLATIVES: For claims containing latest, newest, current, still, remains, most capable, leading, or similar comparisons, make the query explicitly search for the latest/current state and newer alternatives. Do not turn a historical claim into a current claim.
8. KEYWORDS: Extract 2-5 essential search keywords.

Return ONLY a valid JSON object matching this exact structure:
{
  "claims": [
    {
      "id": 1,
      "claim_text": "Clean atomic claim statement without fluff",
      "time_sensitive": true,
      "temporal_context": "2024 or current release",
      "search_query": "specific search terms for search engine",
      "keywords": ["keyword1", "keyword2"]
    }
  ]
}
"""


class ClaimExtractor:
    """Extracts verifiable claims from text using Bifrost AI Gateway or heuristic fallback."""

    def __init__(self, bifrost_client: Optional[BifrostClient] = None):
        self.bifrost_client = bifrost_client or BifrostClient()

    def extract_claims(self, text: str, max_claims: int = config.MAX_CLAIMS_TO_PROCESS) -> List[FactualClaim]:
        """
        Extracts atomic factual claims from the provided AI text.

        Args:
            text: Raw AI-generated text.
            max_claims: Maximum number of claims to extract.

        Returns:
            List of FactualClaim models.
        """
        clean_text = sanitize_input_text(text, max_chars=config.MAX_INPUT_LENGTH)
        if len(clean_text) < config.MIN_INPUT_LENGTH:
            raise ValueError(
                f"Input text is too short ({len(clean_text)} characters). "
                f"Please provide at least {config.MIN_INPUT_LENGTH} characters."
            )

        safe_content = sanitize_for_prompt_injection(clean_text)

        messages = [
            {"role": "system", "content": SYSTEM_CLAIM_EXTRACTION_PROMPT},
            {
                "role": "user",
                "content": f"Extract all factual claims from the following text (up to {max_claims} key claims):\n\n<ai_generated_answer>\n{safe_content}\n</ai_generated_answer>",
            },
        ]

        try:
            logger.info("Extracting claims via Bifrost AI Gateway...")
            raw_response = self.bifrost_client.create_chat_completion(
                messages=messages,
                temperature=0.1,
                response_format_json=True,
            )
            parsed_json = extract_json_from_llm_response(raw_response)
            claims_data = parsed_json.get("claims", [])

            claims: List[FactualClaim] = []
            for item in claims_data[:max_claims]:
                claim = FactualClaim(
                    id=item.get("id", len(claims) + 1),
                    claim_text=item.get("claim_text", "").strip(),
                    time_sensitive=bool(item.get("time_sensitive", False)),
                    temporal_context=item.get("temporal_context"),
                    search_query=item.get("search_query", "").strip() or item.get("claim_text", "").strip(),
                    keywords=item.get("keywords", []),
                )
                if claim.claim_text:
                    claims.append(claim)

            if not claims:
                logger.warning("Bifrost returned empty claims list; falling back to heuristic extractor.")
                return self._heuristic_fallback_extraction(clean_text, max_claims)

            return claims

        except Exception as e:
            logger.warning("Bifrost extraction failed (%s). Utilizing heuristic claim extractor.", e)
            return self._heuristic_fallback_extraction(clean_text, max_claims)

    def _heuristic_fallback_extraction(self, text: str, max_claims: int) -> List[FactualClaim]:
        """
        Deterministic heuristic extractor for offline/demo mode or when AI gateway is unreachable.
        Splits sentences, filters out conversational filler, and detects time-sensitive keywords.
        """
        # Split text into sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)
        claims: List[FactualClaim] = []

        time_sensitive_keywords = {
            "latest", "current", "version", "cost", "costs", "price", "priced",
            "release", "released", "ceo", "policy", "rules", "rule", "fee",
            "percent", "%", "dollar", "$", "2020", "2021", "2022", "2023", "2024", "2025", "2026",
            "active", "now", "today", "currently"
        }

        fluff_starters = (
            "sure", "certainly", "here is", "here are", "i think", "in my opinion",
            "as an ai", "it is important to note", "overall", "in conclusion", "furthermore"
        )

        for sent in sentences:
            trimmed = sent.strip()
            # Ignore short sentences or conversational filler
            if len(trimmed) < 20 or len(trimmed.split()) < 4:
                continue

            lower_sent = trimmed.lower()
            if any(lower_sent.startswith(fluff) for fluff in fluff_starters):
                continue

            # Detect time sensitivity
            words = set(re.findall(r"\w+", lower_sent))
            is_time_sensitive = bool(words & time_sensitive_keywords)

            # Generate search query: strip punctuation and take key nouns/terms
            clean_query = re.sub(r"[^\w\s-]", "", trimmed)
            query_words = clean_query.split()
            search_query = " ".join(query_words[:7])

            # Extract 2-4 keywords
            keywords = [w for w in query_words if len(w) > 3][:4]

            claim = FactualClaim(
                id=len(claims) + 1,
                claim_text=trimmed,
                time_sensitive=is_time_sensitive,
                temporal_context="Recent / Current" if is_time_sensitive else None,
                search_query=search_query,
                keywords=keywords,
            )
            claims.append(claim)

            if len(claims) >= max_claims:
                break

        return claims
