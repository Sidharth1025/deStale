"""
StaleGuard - Tavily Live Internet Search Module
Integrates with the official Tavily Search API (https://docs.tavily.com/)
to retrieve live, authoritative web evidence for factual claims.
"""

import time
import logging
import requests
from typing import List, Dict, Any, Optional
from config import config
from models import EvidenceSource
from utils import extract_domain, is_authoritative_domain, clean_snippet

logger = logging.getLogger("deStale.TavilySearch")

TAVILY_API_ENDPOINT = "https://api.tavily.com/search"


class TavilySearchError(Exception):
    """Custom exception for Tavily Search API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class TavilySearchClient:
    """
    Client for performing live internet searches via Tavily's official API.
    Collects web snippets, source URLs, page titles, and available publication dates.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        search_depth: Optional[str] = None,
        max_results: Optional[int] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        self.api_key = config.TAVILY_API_KEY if api_key is None else api_key
        self.search_depth = search_depth or config.TAVILY_SEARCH_DEPTH
        self.max_results = max_results or config.TAVILY_MAX_RESULTS
        self.timeout = timeout or config.TAVILY_TIMEOUT
        self.max_retries = max_retries or config.TAVILY_MAX_RETRIES

        # In-memory query deduplication cache to avoid wasting API credits
        self._cache: Dict[str, List[EvidenceSource]] = {}

    @property
    def is_configured(self) -> bool:
        """Checks whether a non-empty Tavily API key is present."""
        return bool(self.api_key and self.api_key.strip())

    def search_claim(self, query: str, max_results: Optional[int] = None) -> List[EvidenceSource]:
        """
        Executes a live web search for a claim query using Tavily API.

        Args:
            query: The targeted search query.
            max_results: Maximum sources to return (defaults to configured setting).

        Returns:
            List of EvidenceSource models.
        """
        clean_q = query.strip()
        if not clean_q:
            return []

        # Check in-memory session cache first (deduplication)
        cache_key = clean_q.lower()
        if cache_key in self._cache:
            logger.info("Retrieved Tavily search results from session cache for query: '%s'", clean_q)
            return self._cache[cache_key]

        if not self.is_configured:
            logger.error("Tavily API key is not configured; refusing to fabricate live search evidence.")
            return []

        limit = max_results or self.max_results
       # Prioritize official sources for better evidence quality.
        official_domains = [
            "python.org",
            "docs.python.org",
            "peps.python.org",
        ]

        payload = {
            "api_key": self.api_key,
            "query": clean_q,
            "search_depth": self.search_depth,
            "include_answer": False,
            "include_images": False,
            "include_raw_content": False,
            "max_results": limit,
            "include_domains": official_domains,
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "deStale-TavilyClient/1.1",
        }

        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info("Executing Tavily live search (Attempt %d/%d) for: '%s'", attempt, self.max_retries, clean_q)
                response = requests.post(
                    TAVILY_API_ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    data = response.json()
                    raw_results = data.get("results", [])
                    evidence_list: List[EvidenceSource] = []

                    for res in raw_results:
                        url = res.get("url", "")
                        domain = extract_domain(url)
                        authoritative = is_authoritative_domain(url)
                        snippet = clean_snippet(res.get("content", ""))

                        item = EvidenceSource(
                            title=res.get("title", "Untitled Source").strip(),
                            url=url,
                            snippet=snippet,
                            score=float(res.get("score", 0.75)),
                            published_date=res.get("published_date"),
                            domain=domain,
                            is_authoritative=authoritative,
                        )
                        evidence_list.append(item)

                    # Store in cache
                    self._cache[cache_key] = evidence_list
                    return evidence_list

                elif response.status_code == 401:
                    logger.error("Tavily API returned 401 Unauthorized. Key is invalid or expired.")
                    raise TavilySearchError(
                        "Tavily API Authentication failed: Invalid or missing TAVILY_API_KEY. "
                        "Please verify your API key in .env or switch to Demo Mode.",
                        status_code=401,
                    )

                elif response.status_code == 429:
                    logger.warning("Tavily Rate Limit reached (HTTP 429). Retrying after backoff...")
                    time.sleep(2 * attempt)
                    continue

                else:
                    logger.warning("Tavily API returned status %d: %s", response.status_code, response.text[:200])
                    time.sleep(1.5 * attempt)
                    continue

            except requests.exceptions.Timeout as e:
                logger.warning("Tavily search timed out for query '%s' (Attempt %d)", clean_q, attempt)
                last_error = e
                time.sleep(1)
            except requests.exceptions.ConnectionError as e:
                logger.warning("Connection error connecting to Tavily: %s", e)
                last_error = e
                time.sleep(1)
            except TavilySearchError:
                raise
            except Exception as e:
                logger.error("Unexpected error in Tavily search: %s", e)
                last_error = e

        # Never present simulated examples as live web evidence. An empty result
        # lets the verifier return INSUFFICIENT_EVIDENCE instead of a false verdict.
        logger.error("Tavily search failed after retries: %s. No evidence will be fabricated.", last_error)
        return []
