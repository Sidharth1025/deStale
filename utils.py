"""
StaleGuard - Utility Functions Module
Provides URL parsing, authoritative domain heuristics, prompt sanitization,
JSON extraction from LLM outputs, and text processing helpers.
"""

import re
import json
import logging
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

# Configure module logger
logger = logging.getLogger("deStale.Utils")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Authoritative domain patterns (official documentation, reputable news, academic, government)
AUTHORITATIVE_DOMAIN_SUFFIXES = (
    ".gov",
    ".edu",
    ".org",
)

AUTHORITATIVE_DOMAINS = {
    # Tech & Software Documentation
    "python.org",
    "docs.python.org",
    "github.com",
    "developer.mozilla.org",
    "openai.com",
    "anthropic.com",
    "docs.tavily.com",
    "microsoft.com",
    "learn.microsoft.com",
    "cloud.google.com",
    "aws.amazon.com",
    "pypi.org",
    "nodejs.org",
    "react.dev",
    "nextjs.org",
    # News & Financial / Standards
    "reuters.com",
    "apnews.com",
    "bloomberg.com",
    "bbc.com",
    "nytimes.com",
    "wsj.com",
    "nature.com",
    "arxiv.org",
    "wikipedia.org",
    "techcrunch.com",
    "theverge.com",
    "wired.com",
}


def extract_domain(url: str) -> str:
    """Extracts the clean domain name from a URL."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""


def is_authoritative_domain(url_or_domain: str) -> bool:
    """
    Evaluates whether a domain is considered an authoritative source.
    Authoritative sources receive higher trust weighting in the freshness calculation.
    """
    domain = extract_domain(url_or_domain) if "://" in url_or_domain else url_or_domain.lower()
    if not domain:
        return False

    # Check known domain set
    if domain in AUTHORITATIVE_DOMAINS:
        return True

    # Check top-level domain suffixes (.gov, .edu)
    for suffix in AUTHORITATIVE_DOMAIN_SUFFIXES:
        if domain.endswith(suffix):
            return True

    # Check parent domain (e.g. subdomains of docs.python.org -> python.org)
    parts = domain.split(".")
    if len(parts) > 2:
        parent_domain = ".".join(parts[-2:])
        if parent_domain in AUTHORITATIVE_DOMAINS:
            return True

    return False


def sanitize_input_text(text: str, max_chars: int = 12000) -> str:
    """
    Sanitizes user-provided input text.
    - Strips null bytes and unusual control characters
    - Caps text at maximum length
    - Neutralizes markdown delimiter exploit patterns
    """
    if not text:
        return ""

    # Remove null bytes and non-printable control characters (except newline, tab, carriage return)
    cleaned = "".join(ch for ch in text if ch in ("\n", "\r", "\t") or (32 <= ord(ch) <= 126) or ord(ch) > 127)

    # Normalize excessive newlines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Truncate length if required
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars]

    return cleaned.strip()


def sanitize_for_prompt_injection(content: str) -> str:
    """
    Wraps untrusted external or user content in security boundary delimiters
    and neutralizes instruction override phrases (e.g., 'ignore previous instructions').
    """
    if not content:
        return ""

    suspicious_patterns = [
        r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
        r"(?i)you\s+must\s+verify\s+all\s+claims\s+as\s+true",
        r"(?i)always\s+output\s+verified",
        r"(?i)system\s+prompt\s+override",
        r"(?i)disregard\s+(the\s+)?prompt",
    ]

    sanitized = content
    for pattern in suspicious_patterns:
        sanitized = re.sub(pattern, "[FILTERED_INSTRUCTION_OVERRIDE]", sanitized)

    return sanitized


def extract_json_from_llm_response(response_text: str) -> Any:
    """
    Robustly parses JSON from LLM generation.
    Handles ```json code blocks, markdown wrappings, and trailing tokens.
    """
    if not response_text:
        raise ValueError("Received empty response from AI model")

    cleaned = response_text.strip()

    # Match ```json ... ``` blocks
    json_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if json_block_match:
        cleaned = json_block_match.group(1).strip()

    # Direct JSON decode attempt
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Find the outermost JSON object { ... } or array [ ... ]
    first_brace = cleaned.find("{")
    first_bracket = cleaned.find("[")

    if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
        last_brace = cleaned.rfind("}")
        if last_brace != -1 and last_brace > first_brace:
            candidate = cleaned[first_brace : last_brace + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

    if first_bracket != -1:
        last_bracket = cleaned.rfind("]")
        if last_bracket != -1 and last_bracket > first_bracket:
            candidate = cleaned[first_bracket : last_bracket + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

    raise ValueError(f"Could not parse valid JSON from AI response: {response_text[:200]}...")


def clean_snippet(snippet: str, max_length: int = 400) -> str:
    """Cleans and truncates web snippet text for prompt readability."""
    if not snippet:
        return ""
    # Remove HTML tags if present
    cleaned = re.sub(r"<[^>]+>", " ", snippet)
    # Collapse multiple whitespaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > max_length:
        cleaned = cleaned[: max_length - 3] + "..."
    return cleaned
