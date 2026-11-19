# deStale Verification Improvements

This update strengthens the verification pipeline while preserving the existing Streamlit interface and project structure.

## What changed

- The Bifrost verification prompt now requires support for the complete claim, including numbers, dates, and comparative terms such as `latest`, `newest`, `current`, and `most capable`.
- A deterministic post-verification guardrail downgrades unsupported `Verified / Supported` results when authoritative evidence is absent, when current claims lack recent dated sources, or when a superlative is not actually established by the evidence.
- The offline verifier no longer treats generic search results as proof. It prefers `Insufficient Evidence` or `Uncertain` when it cannot safely establish a result.
- Tavily failures and missing API keys now return no evidence instead of synthetic results that could be mistaken for live web evidence.
- Freshness scoring uses actual publication dates and penalizes undated or old authoritative sources for time-sensitive claims.
- Aggregate summaries now explicitly count insufficient-evidence claims.
- The Streamlit status panel distinguishes a configured live search API from Demo Mode.
- README setup instructions recommend Python 3.12 for Windows and explain the live/demo distinction.

## Validation

Run the automated tests from the project root:

```powershell
python -m pytest -q
```

The updated test suite currently passes **16 tests**.

## Important limitations

- A freshness score is a heuristic index, not a calibrated probability of truth.
- A source being classified as authoritative does not guarantee that every sentence on that source is correct or relevant.
- Search snippets may omit context. For important decisions, open and inspect the cited source pages.
- Live verification requires working Bifrost and Tavily credentials. Demo Mode uses pre-cached examples and is not live fact-checking.
