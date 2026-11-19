# 🛡️ deStale: Live AI Freshness & Fact-Checking Engine

[![Python Version](https://img.shields.io/badge/Python-3.10%E2%80%933.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![AI Gateway](https://img.shields.io/badge/AI%20Gateway-Bifrost-6366F1.svg)](https://github.com/maximhq/bifrost)
[![Search Engine](https://img.shields.io/badge/Live%20Search-Tavily%20API-10B981.svg)](https://docs.tavily.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Test Suite](https://img.shields.io/badge/Tests-Pytest%20Passing-brightgreen.svg)](tests/)

> **deStale** is an autonomous AI fact-checking and freshness verification engine. It detects outdated, superseded, and contradicted information in AI-generated answers by querying live internet evidence through **Tavily**, routing multi-model cross-examinations via **MaximHQ Bifrost AI Gateway**, and computing a transparent **Freshness Score (0–100)** with suggested corrections.

---

## 📌 Problem Statement

Foundation Large Language Models (LLMs) suffer from static **knowledge cutoff dates**. The physical and digital world moves continuously, yet retraining foundation models takes months and millions of dollars. As a result, AI models often output stale or obsolete data with total confidence:

- 💸 **Outdated Pricing:** Quoting $30.00/1M tokens for legacy GPT-4 when modern GPT-4o costs $2.50/1M tokens.
- ⚙️ **Deprecated Software:** Recommending Next.js 13 or Python 3.9 as "latest stable versions" in 2024.
- 🏛️ **Corporate & Legal Changes:** Hallucinating former executives (e.g., claiming Jack Dorsey is Twitter CEO) or citing superseded regulations.
- 📉 **Obsolete Statistics:** Providing economic metrics or government policies that have been repealed or updated.

---

## 💡 The Solution: How deStale Works

deStale implements a zero-trust, 5-stage verification firewall:

```
[User AI Text] 
      │
      ▼
1. Claim Extraction  ──(Bifrost Gateway)──►  Atomic Factual Propositions
      │
      ▼
2. Live Web Search   ──(Tavily API)──────►  Authoritative Snippets & Dates
      │
      ▼
3. Fact Verification ──(Bifrost Gateway)──►  Verified | Outdated | Contradicted
      │
      ▼
4. Freshness Scoring ────────────────────►  Heuristic Score (0 - 100)
      │
      ▼
5. Audit & Reporting ────────────────────►  Interactive UI, PDF, CSV, Markdown
```

1. **Atomic Claim Extraction:** Bifrost decomposes free-form answers into isolated, verifiable factual propositions, filtering out opinions, rhetoric, and subjective prose.
2. **Live Internet Grounding:** Tavily searches the live web for each claim, retrieving canonical URLs, titles, published timestamps, and domain authority.
3. **Evidence Guardrails:** Bifrost evaluates the complete claim, including numbers, dates, and comparative words such as "latest" or "most capable". Deterministic checks downgrade unsupported verdicts rather than accepting keyword overlap.
4. **Freshness Scoring Engine:** Computes a transparent heuristic Freshness Index (0–100), weighting time-sensitive claims at 1.5x and applying date-aware recency adjustments.
5. **Evidence-Supported Corrections:** Provides a correction only when the retrieved evidence supports it. Missing or stale evidence is reported as insufficient or uncertain rather than guessed.

---

## 🚀 Key Features

- ⚡ **Real MaximHQ Bifrost Integration:** Connects to Bifrost AI Gateway (`http://localhost:8080/v1`) using OpenAI-compatible routing, fallback models, and token monitoring.
- 🌐 **Real Tavily Live Search:** Queries the live web with session deduplication caching to conserve API credits.
- 🎨 **Modern Cyberpunk UI:** Custom dark navy dashboard with glowing status badges, freshness meters, and expandable source drawers.
- ⚖️ **Side-by-Side Diff View:** Instant tabular comparison between original stale claims and verified modern truth.
- 📄 **Multi-Format Compliance Export:** One-click download of styled PDF audit reports (via ReportLab), CSV datasets, and Markdown summaries.
- 💡 **Interactive Demo Mode:** Built-in curated real-world benchmarks (AI pricing, software releases, executive governance) for instant testing without active API keys.
- 🛡️ **Prompt Injection Shielding:** Untrusted inputs and web snippets are encapsulated in `<untrusted_content>` tags with instruction override filters.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.10–3.12 recommended | Pydantic schemas and type hints; Python 3.12 is recommended for the Windows setup below |
| **Frontend** | Streamlit | Reactive UI with custom responsive CSS |
| **AI Gateway** | MaximHQ Bifrost | Multi-model routing, fallback resilience, latency tracking |
| **Search Engine** | Tavily Live Search API | Purpose-built AI web search with date extraction |
| **Data Validation** | Pydantic v2 | Robust JSON parsing and type validation |
| **Document Export** | ReportLab | Enterprise-grade PDF report generation |
| **Testing** | Pytest | mocked offline automated tests |

---

## 📁 Project Architecture & File Structure

```text
deStale/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI workflow (Python 3.10, 3.11, 3.12)
├── assets/
│   └── logo.svg               # deStale project emblem & SVG badge
├── docs/
│   ├── ARCHITECTURE.md        # Detailed system specifications & threat model
│   ├── PRESENTATION.md        # 10-Slide pitch presentation deck
│   ├── DEMO_SCRIPT.md         # 3-5 minute live demonstration script
│   └── VIVA_QUESTIONS.md      # 25 Viva/interview Q&A guide
├── tests/
│   ├── __init__.py            # Test package marker
│   ├── test_claim_extractor.py # Claim decomposition & prompt shielding tests
│   ├── test_tavily_search.py   # Tavily caching, rate-limiting & network tests
│   ├── test_fact_verifier.py   # Multi-source synthesis & classification tests
│   ├── test_freshness_scorer.py# Heuristic scoring engine & weighting tests
│   └── test_end_to_end.py     # Mocked full-pipeline integration test
├── app.py                     # Streamlit reactive dashboard & cyberpunk UI
├── config.py                  # Singleton settings & environment configuration
├── models.py                  # Pydantic v2 schemas for claims, sources, and reports
├── bifrost_client.py          # MaximHQ Bifrost AI Gateway REST client
├── tavily_search.py           # Tavily Live Web Search API client with caching
├── claim_extractor.py         # Atomic claim extraction & decomposition
├── fact_verifier.py           # Multi-source evidence cross-examiner
├── freshness_scorer.py        # Heuristic Freshness Scoring Engine (0 - 100)
├── report_generator.py        # Styled PDF, CSV, and Markdown audit report exporter
├── demo_data.py               # Pre-cached curated real-world benchmark datasets
├── utils.py                   # Domain authority heuristics & prompt sanitization
├── generate_complete_project_pdf.py # Standalone PDF documentation builder
├── deStale_Complete_Project_Documentation.pdf # Generated executive documentation PDF
├── requirements.txt           # Production & development dependencies
├── .env.example               # Template for Bifrost & Tavily credentials
├── .gitignore                 # Excludes .env, virtual environments, caches
├── LICENSE                    # MIT Open Source License
├── CONTRIBUTING.md            # Guidelines for open source contributors
├── SECURITY.md                # Security policy & responsible disclosure
└── CODE_OF_CONDUCT.md         # Contributor Covenant Code of Conduct
```

---

## ⚡ Installation & Setup

### 1. Clone or Open the Repository
```bash
git clone https://github.com/your-username/deStale.git
cd deStale
```

### 2. Create and Activate a Virtual Environment
Python 3.12 is recommended for the Windows installation. Check installed versions with `py --list`.

```powershell
# Windows PowerShell (choose Python 3.12 explicitly)
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# If PowerShell blocks activation for this session only:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Run these commands after activating the environment:
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure API Keys
Copy `.env.example` to `.env`:
```bash
# Windows PowerShell
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# Bifrost AI Gateway Configuration (https://github.com/maximhq/bifrost)
BIFROST_BASE_URL=http://localhost:8080/v1
BIFROST_API_KEY=your_bifrost_or_provider_key
BIFROST_MODEL=gpt-4o-mini

# Tavily Live Search API (https://app.tavily.com/)
TAVILY_API_KEY=tvly-your_tavily_api_key_here
TAVILY_SEARCH_DEPTH=advanced
TAVILY_MAX_RESULTS=5
```

> **Important:** Demo Mode uses pre-cached example reports and is clearly separate from live verification. Live Mode never fabricates search results: if the Tavily key is missing or a search fails, the claim receives an insufficient-evidence result. If Bifrost is unavailable, the local fallback is deliberately conservative and does not mark a claim verified based only on generic snippets.

---

## 🖥️ Running the Application

Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```

The application will be accessible at:
```
http://localhost:8501
```

---

## 🧪 Automated Testing

deStale includes a comprehensive test suite. Automated tests utilize mocked responses so that **no API credits are consumed**:

```bash
# Run all unit and integration tests
pytest -v tests/
```

---

## 📊 Freshness Scoring Heuristic Explained

deStale transparently documents that its score is an **evidence-based empirical index**, not an uncalibrated probability:

$$\text{Aggregate Freshness} = \frac{\sum_{i=1}^N (\text{Claim Score}_i \times \text{Weight}_i)}{\sum_{i=1}^N \text{Weight}_i}$$

- **Base Classifications:**
  - `Verified / Supported`: `100.0`
  - `Outdated (Superseded)`: `15.0` (Severe penalty for stale historical data)
  - `Contradicted (False)`: `0.0`
  - `Uncertain`: `45.0`
  - `Insufficient Evidence`: `45.0` for static claims and `35.0` for time-sensitive claims before other adjustments.
- **Authority Adjustment:** Verified claims receive a small deduction when only one authoritative source is present; non-authoritative-only evidence cannot support a verified result.
- **Date-Aware Recency:** Time-sensitive verified claims are penalized when their newest authoritative source is old or undated. The score uses actual publication dates, not a hard-coded year.
- **Time Sensitivity Weighting:** Time-sensitive statements (prices, releases, corporate leadership) receive **1.5x weight** in the aggregate score.
- **Interpretation:** The score is a transparent heuristic index, not a statistical probability that a claim is true.

---

## 🚢 GitHub Repository Deployment

To initialize Git and publish your repository to GitHub:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Initial commit
git commit -m "feat: initial commit of deStale AI Freshness Detector"

# Set main branch
git branch -M main

# Link to your remote GitHub repository
git remote add origin https://github.com/<your-username>/deStale.git

# Push to GitHub
git push -u origin main
```

---

## 📚 Supplementary Documentation

Detailed documentation and presentations are provided in the [`docs/`](docs/) directory:

- 🏛️ **[System Architecture & Threat Model](docs/ARCHITECTURE.md)**: In-depth technical specifications, pipeline stages, security boundaries, and sequence flows.
- 🎤 **[3–5 Minute Pitch & Live Demo Script](docs/DEMO_SCRIPT.md)**: Turnkey presenter walkthrough tailored for hackathon judges and investors.
- 📊 **[10-Slide Pitch Deck Outline](docs/PRESENTATION.md)**: Slide-by-slide structure with speaking notes and visual guidance.
- 🎓 **[25 Viva & Interview Questions](docs/VIVA_QUESTIONS.md)**: Deep technical Q&A covering LLM cutoff mechanics, scoring calibration, Bifrost gateway advantages, and adversarial edge cases.
- 📄 **[Executive Project Documentation (PDF)](deStale_Complete_Project_Documentation.pdf)**: Comprehensive offline PDF report generated via ReportLab.

---

## 🤝 Contributing & Community

Contributions are warmly welcomed! Please read our community guidelines before submitting code:
- **[Contributing Guide](CONTRIBUTING.md)**: Setup, branch rules, and PR checklist.
- **[Code of Conduct](CODE_OF_CONDUCT.md)**: Community standards and pledge.
- **[Security Policy](SECURITY.md)**: Reporting vulnerabilities and responsible disclosure.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 🔐 Security and API keys

- Never commit `.env`, API keys, tokens, or private configuration files.
- Keep `.env.example` as a template containing placeholders only.
- `.gitignore` already excludes `.env` and common Python environment files.
- If a key is accidentally pushed to a public repository, revoke it at the provider and create a replacement immediately.
- Live verification requires a reachable Bifrost gateway/model provider and a valid Tavily API key. Without them, the app may use fallback/demo behavior; check the UI and logs before describing a result as live.

## 🧩 Mandatory hackathon integrations

This implementation uses both technologies named in the problem statement:

| Required technology | Where it is used | Purpose |
|---|---|---|
| Tavily | `tavily_search.py` | Searches the live web for claim-related evidence and returns source metadata |
| Bifrost by Maxim AI | `bifrost_client.py` | Routes LLM requests for claim extraction and evidence-based verification |

The app's main flow is: user answer → claim extraction → Tavily evidence search → Bifrost-assisted verification → freshness scoring → downloadable audit report.

## 🧪 Current verification status

The included automated test suite was run locally during repository preparation: **12 tests passed**. These tests use mocked/offline behavior; this does not prove that external API credentials, a live Bifrost gateway, or live Tavily requests are configured on another machine.
