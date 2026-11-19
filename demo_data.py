"""
deStale - Demo Scenarios & Offline Fallback Dataset
Provides curated real-world examples of stale, outdated, contradicted,
and verified AI-generated text for instant demonstration.
Clearly labelled as Demonstration Mode.
"""

from typing import Dict, Any, List
from models import (
    FactualClaim,
    EvidenceSource,
    VerificationStatus,
    ClaimVerificationResult,
    FreshnessSummary,
    DeStaleReport,
    StaleGuardReport,
)

DEMO_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "AI Model Pricing & Cutoff (High Stale Risk)": {
        "description": "Demonstrates classic LLM knowledge cutoff errors regarding rapidly changing AI pricing and model releases.",
        "input_text": (
            "OpenAI's flagship model GPT-4 costs $30.00 per 1M input tokens and $60.00 per 1M output tokens for developers. "
            "Anthropic's newest and most capable AI model is Claude 2, which offers a 100k token context window. "
            "Meanwhile, Meta's Llama 2 remains the most current open-source foundation model available for commercial deployment."
        ),
        "claims_data": [
            {
                "id": 1,
                "claim_text": "OpenAI's flagship model GPT-4 costs $30.00 per 1M input tokens and $60.00 per 1M output tokens.",
                "time_sensitive": True,
                "temporal_context": "Current developer API pricing",
                "search_query": "OpenAI API pricing GPT-4 GPT-4o cost per million tokens",
                "status": VerificationStatus.OUTDATED,
                "freshness_score": 10.0,
                "explanation": "Official OpenAI pricing shows GPT-4o ($2.50/1M input) and GPT-4o mini ($0.15/1M input) have superseded legacy GPT-4 pricing. The $30/1M rate is severely outdated.",
                "suggested_correction": "OpenAI's current flagship GPT-4o costs $2.50 per 1M input tokens and $10.00 per 1M output tokens (a ~92% reduction). GPT-4o mini costs $0.15 / $0.60 per 1M tokens.",
                "sources": [
                    {
                        "title": "OpenAI API Official Pricing",
                        "url": "https://openai.com/api/pricing/",
                        "snippet": "GPT-4o is our flagship model, costing $2.50 per 1M input tokens and $10.00 per 1M output tokens. Legacy GPT-4 8k context was previously $30/1M input tokens.",
                        "published_date": "2024-10-01",
                        "domain": "openai.com",
                        "is_authoritative": True,
                        "score": 0.98,
                    },
                    {
                        "title": "OpenAI Models Overview - Official Documentation",
                        "url": "https://platform.openai.com/docs/models",
                        "snippet": "GPT-4o and GPT-4o mini are our latest flagship models, replacing older GPT-4 checkpoints for standard developer deployments.",
                        "published_date": "2024-09-15",
                        "domain": "openai.com",
                        "is_authoritative": True,
                        "score": 0.94,
                    },
                ],
            },
            {
                "id": 2,
                "claim_text": "Anthropic's newest and most capable AI model is Claude 2 with a 100k token context window.",
                "time_sensitive": True,
                "temporal_context": "Current Anthropic model generation",
                "search_query": "Anthropic Claude latest model release Claude 3.5 Sonnet context window",
                "status": VerificationStatus.OUTDATED,
                "freshness_score": 15.0,
                "explanation": "Anthropic has released the Claude 3 and 3.5 family (Claude 3.5 Sonnet, Claude 3 Opus, Haiku) featuring a 200k token context window, rendering Claude 2 obsolete.",
                "suggested_correction": "Anthropic's flagship model is Claude 3.5 Sonnet with a 200,000-token context window and enhanced coding benchmarks.",
                "sources": [
                    {
                        "title": "Anthropic Claude 3.5 Sonnet Release Announcement",
                        "url": "https://www.anthropic.com/news/claude-3-5-sonnet",
                        "snippet": "Claude 3.5 Sonnet raises the industry bar for intelligence, outperforming competitor models and Claude 3 Opus at 2x the speed with a 200k context window.",
                        "published_date": "2024-06-20",
                        "domain": "anthropic.com",
                        "is_authoritative": True,
                        "score": 0.96,
                    },
                ],
            },
            {
                "id": 3,
                "claim_text": "Meta's Llama 2 remains the most current open-source foundation model available for commercial deployment.",
                "time_sensitive": True,
                "temporal_context": "Current Meta open weights generation",
                "search_query": "Meta AI Llama latest model release Llama 3 3.1 3.2",
                "status": VerificationStatus.OUTDATED,
                "freshness_score": 15.0,
                "explanation": "Meta released Llama 3 and Llama 3.1 (including 8B, 70B, and 405B parameter models) followed by Llama 3.2 lightweight vision models under updated community licenses.",
                "suggested_correction": "Meta's latest open-weights model families are Llama 3.1 (up to 405B) and Llama 3.2, which succeed Llama 2.",
                "sources": [
                    {
                        "title": "Meta AI: Introducing Llama 3.1",
                        "url": "https://ai.meta.com/blog/meta-llama-3-1/",
                        "snippet": "We are releasing Llama 3.1 405B, the world's first open-source frontier-class AI model, alongside upgraded 70B and 8B models.",
                        "published_date": "2024-07-23",
                        "domain": "ai.meta.com",
                        "is_authoritative": True,
                        "score": 0.95,
                    },
                ],
            },
        ],
    },
    "Tech Leadership & Governance (Contradicted / Outdated)": {
        "description": "Tests identification of executive leadership changes and corporate restructuring.",
        "input_text": (
            "Twitter (now X) is currently led by Chief Executive Officer Jack Dorsey who manages daily platform operations. "
            "OpenAI is strictly an exclusive 501(c)(3) non-profit research institution with no commercial or profit-capped subsidiaries."
        ),
        "claims_data": [
            {
                "id": 1,
                "claim_text": "Twitter is currently led by Chief Executive Officer Jack Dorsey who manages daily platform operations.",
                "time_sensitive": True,
                "temporal_context": "Current CEO of X / Twitter",
                "search_query": "Current CEO of Twitter X Linda Yaccarino Jack Dorsey Elon Musk",
                "status": VerificationStatus.CONTRADICTED,
                "freshness_score": 0.0,
                "explanation": "Jack Dorsey stepped down as CEO of Twitter in November 2021. Linda Yaccarino took over as CEO of X (formerly Twitter) in June 2023 under owner Elon Musk.",
                "suggested_correction": "Linda Yaccarino is the Chief Executive Officer of X (formerly Twitter); Jack Dorsey resigned as Twitter CEO in late 2021.",
                "sources": [
                    {
                        "title": "Reuters: Linda Yaccarino takes over as Twitter CEO",
                        "url": "https://www.reuters.com/technology/linda-yaccarino-takes-over-twitter-x-ceo-2023-06/",
                        "snippet": "Linda Yaccarino, former advertising chief at NBCUniversal, has taken over as the CEO of Twitter, succeeding Elon Musk.",
                        "published_date": "2023-06-05",
                        "domain": "reuters.com",
                        "is_authoritative": True,
                        "score": 0.97,
                    },
                ],
            },
            {
                "id": 2,
                "claim_text": "OpenAI is strictly an exclusive 501(c)(3) non-profit research institution with no commercial or profit-capped subsidiaries.",
                "time_sensitive": True,
                "temporal_context": "Corporate organizational structure",
                "search_query": "OpenAI corporate structure capped profit subsidiary 501c3",
                "status": VerificationStatus.CONTRADICTED,
                "freshness_score": 0.0,
                "explanation": "In 2019, OpenAI created OpenAI Global LLC, a capped-profit commercial subsidiary governed by the non-profit board, to attract capital and talent.",
                "suggested_correction": "OpenAI operates as a hybrid entity: OpenAI Nonprofit controls a capped-profit subsidiary (OpenAI Global LLC) formed in 2019.",
                "sources": [
                    {
                        "title": "OpenAI: Our Structure",
                        "url": "https://openai.com/our-structure/",
                        "snippet": "In 2019, we created a capped-profit company, OpenAI Global LLC, to allow us to raise capital and hire top talent while remaining aligned with our non-profit charter.",
                        "published_date": "2023-06-28",
                        "domain": "openai.com",
                        "is_authoritative": True,
                        "score": 0.99,
                    },
                ],
            },
        ],
    },
    "Software & Framework Versions (Moderate Stale Risk)": {
        "description": "Tests software version recency vs historical software releases.",
        "input_text": (
            "Next.js 13 is the latest major release of Vercel's React web framework with the App Router. "
            "Python 3.9 is the most recent stable version of Python recommended for active production deployments. "
            "Python was originally created by Dutch programmer Guido van Rossum in 1991."
        ),
        "claims_data": [
            {
                "id": 1,
                "claim_text": "Next.js 13 is the latest major release of Vercel's React web framework with the App Router.",
                "time_sensitive": True,
                "temporal_context": "Current Next.js framework release",
                "search_query": "Next.js latest major release Next 14 Next 15 Vercel",
                "status": VerificationStatus.OUTDATED,
                "freshness_score": 15.0,
                "explanation": "Next.js 15 has been officially released as GA by Vercel, bringing React 19 support and Turbopack compiler enhancements. Next.js 13 was released in 2022.",
                "suggested_correction": "Next.js 15 is the current major production release of Next.js.",
                "sources": [
                    {
                        "title": "Next.js 15 Release Notes - Vercel Official Blog",
                        "url": "https://nextjs.org/blog/next-15",
                        "snippet": "We are thrilled to announce Next.js 15 is now generally available. This release builds on the App Router foundation with React 19 support and faster builds.",
                        "published_date": "2024-10-21",
                        "domain": "nextjs.org",
                        "is_authoritative": True,
                        "score": 0.98,
                    },
                ],
            },
            {
                "id": 2,
                "claim_text": "Python 3.9 is the most recent stable version of Python recommended for active production deployments.",
                "time_sensitive": True,
                "temporal_context": "Current stable Python release",
                "search_query": "Python current latest stable release version Python 3.12 3.13",
                "status": VerificationStatus.OUTDATED,
                "freshness_score": 10.0,
                "explanation": "According to the Python Software Foundation, Python 3.12 and 3.13 are the current active stable feature releases. Python 3.9 is in security-fixes-only maintenance mode.",
                "suggested_correction": "Python 3.12 and Python 3.13 are the current active production releases of Python.",
                "sources": [
                    {
                        "title": "Python Developer's Guide - Active Python Releases",
                        "url": "https://devguide.python.org/versions/",
                        "snippet": "Python 3.13 and 3.12 are the currently active branches receiving bugfix and security updates. Python 3.9 entered maintenance status in 2021.",
                        "published_date": "2024-10-07",
                        "domain": "python.org",
                        "is_authoritative": True,
                        "score": 0.99,
                    },
                ],
            },
            {
                "id": 3,
                "claim_text": "Python was originally created by Dutch programmer Guido van Rossum in 1991.",
                "time_sensitive": False,
                "temporal_context": "Historical origin of Python",
                "search_query": "Python origin Guido van Rossum release date 1991",
                "status": VerificationStatus.VERIFIED,
                "freshness_score": 100.0,
                "explanation": "Confirmed by multiple authoritative computer science repositories and the Python Software Foundation: Guido van Rossum conceived Python in the late 1980s and released 0.9.0 in 1991.",
                "suggested_correction": None,
                "sources": [
                    {
                        "title": "General Python FAQ - History of Python",
                        "url": "https://docs.python.org/3/faq/general.html",
                        "snippet": "Python was conceived in the late 1980s by Guido van Rossum at CWI in the Netherlands and released in February 1991.",
                        "published_date": "2024-05-01",
                        "domain": "docs.python.org",
                        "is_authoritative": True,
                        "score": 0.99,
                    },
                ],
            },
        ],
    },
    "Verified Evergreen Facts (100% Freshness Baseline)": {
        "description": "Baseline control scenario demonstrating 100% verified factual accuracy.",
        "input_text": (
            "Git is a distributed version control system designed by Linus Torvalds in 2005. "
            "The ISO 8601 standard describes an internationally accepted way to represent dates and times using numbers. "
            "HTTP stands for Hypertext Transfer Protocol and is an application-layer protocol for transmitting hypermedia documents."
        ),
        "claims_data": [
            {
                "id": 1,
                "claim_text": "Git is a distributed version control system designed by Linus Torvalds in 2005.",
                "time_sensitive": False,
                "temporal_context": "Historical release of Git",
                "search_query": "Git version control system Linus Torvalds 2005",
                "status": VerificationStatus.VERIFIED,
                "freshness_score": 100.0,
                "explanation": "Multiple authoritative sources corroborate that Git was authored by Linus Torvalds in 2005 to manage Linux kernel development.",
                "suggested_correction": None,
                "sources": [
                    {
                        "title": "Git - A Short History of Git",
                        "url": "https://git-scm.com/book/en/v2/Getting-Started-A-Short-History-of-Git",
                        "snippet": "As with many great things in life, Git began with a bit of creative destruction and fiery controversy. Linus Torvalds began development in 2005.",
                        "published_date": "2024-01-10",
                        "domain": "git-scm.com",
                        "is_authoritative": True,
                        "score": 0.98,
                    },
                ],
            },
            {
                "id": 2,
                "claim_text": "The ISO 8601 standard describes an internationally accepted way to represent dates and times using numbers.",
                "time_sensitive": False,
                "temporal_context": "ISO standard specification",
                "search_query": "ISO 8601 date and time representation standard",
                "status": VerificationStatus.VERIFIED,
                "freshness_score": 100.0,
                "explanation": "Corroborated by the International Organization for Standardization (ISO); ISO 8601 specifies numeric date and time representation (YYYY-MM-DD).",
                "suggested_correction": None,
                "sources": [
                    {
                        "title": "ISO 8601: Date and time format standard",
                        "url": "https://www.iso.org/iso-8601-date-and-time-format.html",
                        "snippet": "ISO 8601 is the internationally accepted way to represent dates and times using numbers to avoid confusion caused by international differences.",
                        "published_date": "2023-11-20",
                        "domain": "iso.org",
                        "is_authoritative": True,
                        "score": 0.99,
                    },
                ],
            },
            {
                "id": 3,
                "claim_text": "HTTP stands for Hypertext Transfer Protocol and is an application-layer protocol for transmitting hypermedia documents.",
                "time_sensitive": False,
                "temporal_context": "Networking protocol definition",
                "search_query": "HTTP Hypertext Transfer Protocol application layer MDN RFC",
                "status": VerificationStatus.VERIFIED,
                "freshness_score": 100.0,
                "explanation": "Supported by MDN Web Docs and IETF RFC standards. HTTP is foundational application-layer networking.",
                "suggested_correction": None,
                "sources": [
                    {
                        "title": "MDN Web Docs: An overview of HTTP",
                        "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview",
                        "snippet": "HTTP is an extensible protocol that fetches resources such as HTML documents. It is the foundation of data exchange on the Web.",
                        "published_date": "2024-04-18",
                        "domain": "developer.mozilla.org",
                        "is_authoritative": True,
                        "score": 0.99,
                    },
                ],
            },
        ],
    },
}


def build_demo_report(scenario_name: str) -> DeStaleReport:
    """Builds a complete, typed DeStaleReport for a demo scenario."""
    from freshness_scorer import FreshnessScorer

    scenario = DEMO_SCENARIOS.get(scenario_name)
    if not scenario:
        scenario = list(DEMO_SCENARIOS.values())[0]

    input_text = scenario["input_text"]
    claim_results: List[ClaimVerificationResult] = []
    scorer = FreshnessScorer()

    for item in scenario["claims_data"]:
        claim = FactualClaim(
            id=item["id"],
            claim_text=item["claim_text"],
            time_sensitive=item["time_sensitive"],
            temporal_context=item.get("temporal_context"),
            search_query=item.get("search_query", item["claim_text"]),
            keywords=[w for w in item["claim_text"].split() if len(w) > 4][:4],
        )

        sources: List[EvidenceSource] = []
        for s in item.get("sources", []):
            sources.append(
                EvidenceSource(
                    title=s["title"],
                    url=s["url"],
                    snippet=s["snippet"],
                    score=float(s.get("score", 0.9)),
                    published_date=s.get("published_date"),
                    domain=s.get("domain", ""),
                    is_authoritative=s.get("is_authoritative", True),
                )
            )

        status = item["status"]
        score, _ = scorer.calculate_claim_score(status, claim, sources)

        result = ClaimVerificationResult(
            claim=claim,
            status=status,
            freshness_score=score,
            explanation=item["explanation"],
            suggested_correction=item.get("suggested_correction"),
            evidence_sources=sources,
            verification_timestamp="2024-11-13T10:00:00Z",
            confidence=0.95,
        )
        claim_results.append(result)

    summary = scorer.calculate_aggregate_summary(claim_results)

    return DeStaleReport(
        report_id=f"DESTALE-{hash(scenario_name) % 10000:04d}",
        created_at="2024-11-13T10:00:00Z",
        original_text=input_text,
        summary=summary,
        claim_results=claim_results,
        is_demo_mode=True,
        ai_model_name="Bifrost AI Gateway (gpt-4o-mini / Simulated Mode)",
        search_engine="Tavily Live Web Search (Curated Demonstration)",
    )
