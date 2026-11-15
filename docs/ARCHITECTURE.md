# StaleGuard Architecture & Technical Specification

## 1. Executive Summary
StaleGuard is an autonomous AI verification pipeline designed to detect stale, superseded, or hallucinated facts in Large Language Model (LLM) outputs. It combats the fundamental limitation of static pre-training data cuts by decomposing AI text into atomic factual propositions, querying live search engines (Tavily), cross-referencing multi-source evidence via an enterprise AI gateway (Bifrost), and computing an evidence-based Freshness Index (0 - 100).

---

## 2. System Architecture Diagram

```mermaid
flowchart TD
    subgraph UI_Layer [Frontend Layer]
        A[User Input: AI Answer / Snippet] --> B[Streamlit Cyberpunk Dashboard]
        B --> C[Scenario Selector / Demo Loader]
    end

    subgraph Extraction_Layer [Claim Extraction]
        B --> D[ClaimExtractor]
        D -->|HTTP REST / OpenAI Schema| E[Bifrost AI Gateway :8080]
        E -->|Atomic Claim Decomposition| F[List of Factual Claims]
    end

    subgraph Live_Search_Layer [Live Web Retrieval]
        F --> G[TavilySearchClient]
        G -->|Tavily API Endpoint| H[(Live Internet Web)]
        H -->|Snippets, URLs, Dates, Scores| I[Gathered Evidence Sources]
        G --> J[Session Deduplication Cache]
    end

    subgraph Verification_Layer [Fact Verification]
        F --> K[FactVerifier]
        I --> K
        K -->|Multi-Source Synthesis| E
        E --> L[Classification: Verified | Outdated | Contradicted | Uncertain]
    end

    subgraph Scoring_Layer [Freshness Engine]
        L --> M[FreshnessScorer]
        M -->|Heuristic Weights + Domain Authority| N[Freshness Summary 0-100]
    end

    subgraph Export_Layer [Reporting & Compliance]
        N --> O[Interactive Visual Audit]
        N --> P[PDF ReportLab Exporter]
        N --> Q[CSV / JSON Audit Data]
    end
```

---

## 3. Core Component Breakdown

### 3.1 Claim Extractor (`claim_extractor.py`)
- **Role:** Decomposes free-form text into atomic, testable claims.
- **Filtering:** Eliminates pleasantries ("Sure, here is..."), opinions ("In my view..."), and rhetorical statements.
- **Temporal Detection:** Flags statements with dates, prices, software versions, or leadership roles as `time_sensitive = True`.
- **Query Synthesis:** Crafts focused, high-precision search strings (3–6 words) optimized for information retrieval.

### 3.2 Tavily Search Client (`tavily_search.py`)
- **Role:** Performs real-time web searches using the Tavily REST API (`https://api.tavily.com/search`).
- **Features:**
  - Automatic session deduplication caching to avoid redundant queries and save API credits.
  - Domain authority evaluation (`.gov`, `.edu`, official documentation, top news agencies).
  - Rate-limit backoff (HTTP 429) and network retry loops.
  - Publication date extraction for recency assessment.

### 3.3 Bifrost AI Gateway Client (`bifrost_client.py`)
- **Role:** Connects to MaximHQ's Bifrost AI Gateway (`https://github.com/maximhq/bifrost`).
- **Features:**
  - Standardized OpenAI-compatible `/v1/chat/completions` REST interface.
  - Multi-provider fallback and load balancing.
  - Structured JSON response parsing with prompt-shielding boundaries to defend against injection attacks.
  - Resilient exception handling and connection health checks.

### 3.4 Fact Verifier (`fact_verifier.py`)
- **Role:** Evaluates claims against retrieved live internet snippets.
- **Strict Guardrail:** A claim is **never** verified on the authority of a single random webpage. Authoritative consensus or multiple independent corroborating sources are required.
- **Classifications:**
  - `Verified / Supported`: Information is confirmed accurate as of today.
  - `Outdated`: Statement was once true, but subsequent events, releases, or policy revisions have superseded it.
  - `Contradicted`: Statement is directly disproven by live web evidence.
  - `Insufficient Evidence`: Live search results lack conclusive data.
  - `Uncertain`: Conflicting sources or unsettled developments.
- **Suggested Correction:** Extracts current factual truth for outdated or contradicted claims.

### 3.5 Freshness Scoring Engine (`freshness_scorer.py`)
- **Nature:** An evidence-based mathematical heuristic index, not an uncalibrated probability.
- **Formula:**
  $$\text{Freshness Score} = \frac{\sum (\text{Claim Score}_i \times \text{Weight}_i)}{\sum \text{Weight}_i}$$
  where:
  - $\text{Weight} = 1.5$ for time-sensitive claims, $1.0$ for static claims.
  - Base Score: Verified = 100, Outdated = 10–20, Contradicted = 0, Uncertain = 45, Insufficient = 50.
  - Authority Adjustments: $+0$ to $+5$ for authoritative multi-source agreement; $-25$ penalty for single unverified sources.

---

## 4. Threat Model & Security Controls

1. **Prompt Injection Defense:** Web snippets and user answers are isolated inside `<untrusted_content>` tags, and instruction overrides (`ignore previous instructions`) are filtered prior to inference.
2. **No Hardcoded Secrets:** All API keys are loaded via environment variables (`.env`).
3. **Input Sanitization:** Caps input text at 12,000 characters and strips non-printable control characters.
