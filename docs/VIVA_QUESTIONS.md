# 🛡️ StaleGuard: Viva & Hackathon Judge Q&A Guide (25 Questions)

---

### Category 1: Concept & Problem Statement

#### Q1: What is the primary problem that StaleGuard solves?
**Answer:** Foundation Large Language Models (LLMs) suffer from static parametric knowledge cutoffs. They do not know about real-time changes such as updated software versions, dynamic API pricing, corporate leadership shifts, or new legal regulations. StaleGuard autonomously extracts factual claims, gathers live internet evidence via Tavily, synthesizes consensus via Bifrost AI Gateway, and outputs a 0–100 Freshness Index with verified corrections.

#### Q2: How does StaleGuard differ from standard Retrieval-Augmented Generation (RAG)?
**Answer:** Standard RAG injects top search snippets into the prompt *before* generation, which often leads to context clutter, hallucinated source attribution, and high token costs. StaleGuard is a **post-generation verification and auditing firewall**. It decomposes already-generated answers into testable propositions, independently cross-references them across multi-source web evidence, and quantifies the freshness risk.

#### Q3: Why is a binary "True/False" fact-checker inadequate for AI freshness?
**Answer:** Real-world knowledge has a temporal dimension. For instance, *"GPT-4 costs $30/1M tokens"* was completely true in 2023, but is now outdated due to GPT-4o. A naive binary classifier calling it "False" fails to recognize that the statement was historically accurate but has since been superseded. StaleGuard explicitly distinguishes between **Outdated (Superseded)**, **Contradicted (False)**, and **Verified (Current)**.

---

### Category 2: Bifrost AI Gateway Integration

#### Q4: What is MaximHQ Bifrost, and why did you choose it over direct LLM API calls?
**Answer:** Bifrost (`https://github.com/maximhq/bifrost`) is an open-source, ultra-fast AI gateway created in Go. It provides unified OpenAI-compatible routing across multiple model providers (OpenAI, Anthropic, Gemini, Mistral). By using Bifrost, StaleGuard achieves model decoupling, automated failover, request retries, unified caching, and telemetry without changing application code.

#### Q5: How is Bifrost configured in StaleGuard?
**Answer:** StaleGuard connects to Bifrost via environment variables: `BIFROST_BASE_URL` (defaulting to `http://localhost:8080/v1`), `BIFROST_API_KEY`, and `BIFROST_MODEL`. All requests are sent to the `/chat/completions` REST endpoint with structured JSON response formatting.

#### Q6: How does StaleGuard handle Bifrost connection failures or timeouts?
**Answer:** The `BifrostClient` implements an exponential backoff retry loop (default 3 retries) with a configurable timeout. If the gateway remains unreachable, the system gracefully falls back to deterministic heuristic parsing or curated demo mode, logging the failure without crashing the user interface.

---

### Category 3: Tavily Live Search Integration

#### Q7: What is Tavily, and why is it preferred over Google or Bing search APIs?
**Answer:** Tavily is a search engine built specifically for autonomous AI agents. Unlike standard search APIs that return messy advertising links and raw HTML, Tavily extracts clean, dense factual content snippets, removes navigation boilerplate, and provides publication timestamps and relevance scores directly in JSON.

#### Q8: How does StaleGuard optimize Tavily API usage to prevent quota exhaustion?
**Answer:** 
1. **Query Optimization:** The ClaimExtractor condenses complex statements into concise 3–6 word keyword queries.
2. **Session Deduplication Cache:** `TavilySearchClient` caches query results in memory. If two claims share an identical search topic, the second query is served from cache with zero API calls.
3. **Claim Capping:** Analysis runs are capped by default to the top 10 key claims.

#### Q9: What happens if Tavily encounters rate limits (HTTP 429)?
**Answer:** The client catches HTTP 429, logs a warning, and pauses using quadratic exponential backoff before retrying up to 3 times.

---

### Category 4: Claim Extraction & Fact Verification

#### Q10: How does ClaimExtractor separate factual claims from opinions?
**Answer:** The prompt instruct the LLM to enforce atomicity and discard conversational fluff, introductory greetings, rhetorical statements, and subjective qualifiers ("in our opinion", "it is exciting that"). Only statements with objective truth value (numbers, versions, entities, dates) are extracted.

#### Q11: Explain the rule: "Never claim a fact is verified because one website mentions it."
**Answer:** This is a vital guardrail against hallucinated web pages, SEO spam, or unverified blog posts. StaleGuard requires either:
1. At least two independent sources confirming the statement, or
2. Corroboration from an authoritative domain (`.gov`, `.edu`, official product documentation, or major news wires).
A claim supported by only a single non-authoritative site incurs a 25-point confidence penalty.

#### Q12: How does StaleGuard identify authoritative domains?
**Answer:** `utils.py` contains an authoritative domain heuristic that inspects canonical domain suffixes (`.gov`, `.edu`, `.org`) and matches against a curated list of top-tier registries (e.g., `docs.python.org`, `openai.com`, `reuters.com`, `github.com`).

---

### Category 5: Freshness Scoring Heuristic

#### Q13: How is the individual claim freshness score calculated?
**Answer:** 
- Base score: `Verified` = 100, `Outdated` = 15, `Contradicted` = 0, `Uncertain` = 45, `Insufficient` = 50.
- Domain Authority Adjustment: Multi-source authoritative confirmation keeps it at 100; single unverified source drops it by 25 points.
- Recency Adjustment: Presence of current year timestamps (e.g. 2024–2026) boosts confidence, while time-sensitive claims lacking recent dates face a 10-point penalty.

#### Q14: How is the overall Freshness Score aggregated?
**Answer:** It is a weighted average:
$$\text{Score} = \frac{\sum (\text{Claim Score} \times \text{Weight})}{\sum \text{Weight}}$$
Time-sensitive claims receive a weight of **1.5x**, while static evergreen claims receive **1.0x**. This ensures that stale prices or versions have a noticeable impact on the overall risk grade.

#### Q15: Why do you emphasize that this is a heuristic rather than a probability?
**Answer:** Calling a score a "probability" falsely implies that the system computed a mathematically calibrated Bayesian prior. In fact, freshness is an empirical index synthesized from evidence volume, recency signals, and domain authority. Being honest about heuristics builds trust with judges and enterprise clients.

---

### Category 6: Architecture, Security & Python Implementation

#### Q16: How does StaleGuard protect against prompt injection attacks?
**Answer:** Both user text and retrieved web snippets are sanitized in `utils.py`. Known instruction override phrases (e.g. "ignore previous instructions", "system prompt override") are filtered, and content is encapsulated inside explicit XML-like `<untrusted_content>` boundary tags.

#### Q17: What design patterns are used in the codebase?
**Answer:**
- **Repository / Client Pattern:** Decoupled `BifrostClient` and `TavilySearchClient`.
- **Strategy Pattern:** Heuristic fallbacks that trigger seamlessly if remote gateways are offline.
- **Data Transfer Objects (DTO):** Strongly typed Pydantic v2 schemas (`FactualClaim`, `EvidenceSource`, `StaleGuardReport`).
- **Singleton Configuration:** Centralized dataclass loaded via `dotenv`.

#### Q18: What formats can StaleGuard export reports in?
**Answer:**
1. **PDF:** Enterprise-styled audit document using ReportLab.
2. **CSV:** Machine-readable tabular format containing claims, timestamps, scores, and citation links.
3. **Markdown:** Formatted markdown summary suitable for GitHub or documentation repositories.

#### Q19: Why use Python 3.11?
**Answer:** Python 3.11 provides significant performance improvements (up to 25% faster runtime execution via the Faster CPython initiative), robust typing improvements, and modern asyncio capabilities.

#### Q20: How did you ensure test coverage?
**Answer:** We wrote a comprehensive Pytest test suite covering claim extraction, Tavily client caching and error handling, fact verification classifications, freshness scoring formulas, and end-to-end report generation with 100% mocked dependencies so tests run offline without consuming API credits.

#### Q21: Can StaleGuard run in an offline environment without API keys?
**Answer:** Yes. StaleGuard features an **Interactive Demo Mode** equipped with curated real-world benchmark datasets (AI model pricing, framework versions, executive leadership) that faithfully demonstrate all 5 pipeline stages and PDF export without needing network access or API keys.

#### Q22: What is the latency profile of the verification pipeline?
**Answer:** For a standard 3-claim paragraph:
- Bifrost claim extraction: ~1.2s
- Parallel Tavily search queries: ~1.5s
- Bifrost verification: ~1.8s
- Scoring & UI rendering: <0.1s
- Total wall-clock time: ~4.5 seconds.

#### Q23: How could this project scale to enterprise production?
**Answer:** By deploying Bifrost with Redis caching, offloading Tavily searches to an asynchronous Celery task queue, and saving audit reports to a PostgreSQL / Timescale database with a GraphQL querying API.

#### Q24: What is the difference between "Outdated" and "Contradicted"?
**Answer:** "Outdated" implies temporal decay: the assertion was factual at some previous point in time (e.g. Python 3.8 was once the latest release). "Contradicted" means the statement is false regardless of time, or was explicitly disproven (e.g. claiming OpenAI has no commercial subsidiaries).

#### Q25: What was the most challenging technical hurdle in building StaleGuard?
**Answer:** Preventing false positives during verification. LLMs tend to over-confidently verify statements when provided with vague web search snippets. We solved this by designing a strict verification prompt with explicit guardrails, requiring multiple authoritative corroborating sources, and implementing domain authority heuristics.
