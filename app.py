"""
deStale - Interactive Streamlit Dashboard
Real-time AI Freshness & Fact-Checking Engine
Detects outdated, superseded, and contradicted information in AI answers
via MaximHQ Bifrost AI Gateway and Tavily Live Internet Search.
"""
import streamlit as st
import os
import json
import textwrap
import uuid
import logging
from datetime import datetime, date, timezone

try:
    import pandas as pd
except ImportError:
    pd = None

from config import config
from models import (
    FactualClaim,
    EvidenceSource,
    VerificationStatus,
    ClaimVerificationResult,
    FreshnessSummary,
    DeStaleReport,
    StaleGuardReport,
)
from bifrost_client import BifrostClient
from tavily_search import TavilySearchClient
from claim_extractor import ClaimExtractor
from fact_verifier import FactVerifier
from freshness_scorer import FreshnessScorer
from report_generator import ReportGenerator
from demo_data import DEMO_SCENARIOS, build_demo_report

# Configure Streamlit page settings
st.set_page_config(
    page_title="deStale | AI Freshness & Fact-Checking Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom User-Friendly & Modern Dark Theme CSS
CUSTOM_CSS = """
<style>
    /* Global Styles */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #111827 0%, #090d16 100%);
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Headers & Brand Typography */
    h1, h2, h3, h4 {
        color: #f8fafc !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    .destale-logo-container {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 0.4rem;
    }
    
    .destale-logo-badge {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
        color: white;
        font-weight: 900;
        font-size: 1.6rem;
        padding: 0.35rem 0.85rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.35);
        display: inline-block;
    }
    
    .destale-brand-title {
        background: linear-gradient(135deg, #ffffff 0%, #93c5fd 60%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin: 0;
    }
    
    .destale-brand-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 400;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    
    /* Cards and Glassmorphism */
    .glass-card {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.4rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(56, 189, 248, 0.35);
    }
    
    /* Freshness Score Highlight Box */
    .score-banner {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    }
    
    .stat-pill {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 1.1rem;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .stat-pill:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    
    /* Claim Cards */
    .claim-item-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(51, 65, 85, 0.8);
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    }
    
    /* Status Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 0.3rem 0.75rem;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-verified {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .badge-outdated {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    .badge-contradicted {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .badge-uncertain {
        background-color: rgba(139, 92, 246, 0.15);
        color: #c084fc;
        border: 1px solid rgba(139, 92, 246, 0.4);
    }
    .badge-insufficient {
        background-color: rgba(107, 114, 128, 0.15);
        color: #9ca3af;
        border: 1px solid rgba(107, 114, 128, 0.4);
    }
    
    /* Correction Box */
    .truth-box {
        background: rgba(6, 182, 212, 0.08);
        border: 1px solid rgba(6, 182, 212, 0.35);
        border-left: 5px solid #06b6d4;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-top: 0.9rem;
        color: #f0fdfa;
        font-size: 0.95rem;
    }
    
    /* Preset pill buttons */
    .preset-pill {
        display: inline-block;
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 8px;
        padding: 0.4rem 0.8rem;
        font-size: 0.85rem;
        color: #e2e8f0;
        cursor: pointer;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    .preset-pill:hover {
        background: rgba(56, 189, 248, 0.2);
        border-color: #38bdf8;
    }
    
    /* Textarea & Inputs */
    .stTextArea textarea {
        background-color: #0b1120 !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        font-size: 0.98rem !important;
        line-height: 1.5 !important;
    }
    .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #090e17;
        border-right: 1px solid rgba(255, 255, 255, 0.07);
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "input_text" not in st.session_state:
    st.session_state.input_text = ""


# Sidebar Configuration (Clean, User-Friendly, No Hackathon Clutter)
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
            <span style="font-size: 1.8rem;">🛡️</span>
            <div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.02em;">deStale</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">AI Freshness & Verification Engine</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Mode Selector
    st.markdown("### ⚙️ Engine Settings")
    mode_selection = st.radio(
        "Execution Mode:",
        ["Live API Mode (Bifrost + Tavily)", "Interactive Demo Mode (Pre-cached)"],
        index=0 if (config.has_tavily_credentials or config.has_bifrost_credentials) else 1,
        help="Choose between live web querying or curated offline test datasets."
    )
    is_live_mode = "Live API" in mode_selection

    # Collapsible API Settings
    with st.expander("🔌 AI Gateway & Live Search Config", expanded=False):
        st.caption("Configure Bifrost AI Gateway & Tavily credentials:")
        bifrost_url = st.text_input(
            "Bifrost Gateway Endpoint:",
            value=config.BIFROST_BASE_URL,
            help="OpenAI-compatible routing gateway endpoint (https://github.com/maximhq/bifrost)",
            )
        bifrost_model = st.selectbox(
        "Target AI Model:",
            [
        "gemini/gemini-3.8-flash",
        "gemini/gemini-3.5-flash",
        "gemini/gemini-3.5-flash-lite",
        "openai/gpt-oss-20b",
    ],
    index=3,

            )
        bifrost_api_key = st.text_input(
            "Gateway API Key:",
            value=config.BIFROST_API_KEY,
            type="password",
            help="Optional if local Bifrost gateway runs without authentication",
        )

        tavily_key = st.text_input(
            "Tavily Search API Key:",
            value=config.TAVILY_API_KEY,
            type="password",
            help="Get your key at https://app.tavily.com",
        )

        if st.button("🔄 Test Gateway Connection", use_container_width=True):
            temp_bifrost = BifrostClient(base_url=bifrost_url, api_key=bifrost_api_key, model=bifrost_model)
            health = temp_bifrost.check_health()
            if health.get("online"):
                st.success(f"Connected to Bifrost at {health.get('url')}")
            else:
                st.info(f"Gateway is offline. Smart heuristic fallback is active.")

    # Status indicators
    tavily_configured = bool(tavily_key and tavily_key.strip())
    st.markdown("---")
    st.markdown("### 📡 System Status")
    if tavily_configured:
        st.success("🟢 Tavily Search API: Configured")
    elif is_live_mode:
        st.error("🔴 Tavily Search API: Not configured — live evidence search is unavailable")
    else:
        st.info("💡 Tavily Search API: Not required in Demo Mode")

    if is_live_mode:
        st.success("🟢 Mode: Live Internet Verification")
    else:
        st.info("💡 Mode: Interactive Demo Benchmarks")

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.8rem; color: #64748b; line-height: 1.4;">
            <b>About deStale:</b><br>
            deStale detects stale, superseded, or hallucinated facts in AI outputs by cross-referencing multi-source live web evidence and computing a transparent freshness score.
        </div>
        """,
        unsafe_allow_html=True,
    )


# Main Hero Header
col_header_title, col_header_badge = st.columns([4, 1])
with col_header_title:
    st.markdown(
        """
        <div class="destale-logo-container">
            <span class="destale-logo-badge">de</span>
            <span class="destale-brand-title">STALE</span>
        </div>
        <div class="destale-brand-subtitle">
            Autonomous Fact-Checking & Freshness Firewall for Generative AI Applications
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_header_badge:
    if st.session_state.current_report and st.session_state.current_report.is_demo_mode:
        st.info("Demo Mode Active", icon="💡")
    else:
        st.success("Live Engine Active", icon="⚡")


# Main Navigation Tabs
tab_audit, tab_diff, tab_history, tab_about = st.tabs([
    "🔍 Fact-Check & Audit",
    "⚖️ Stale vs. Fresh Diff",
    "📜 Scan History",
    "ℹ️ How deStale Works",
])


# ==============================================================================
# TAB 1: FACT-CHECK & AUDIT
# ==============================================================================
with tab_audit:
    # Quick Examples Bar for effortless testing
    st.markdown("##### ⚡ Quick-Load Example Answers")
    col_preset1, col_preset2, col_preset3, col_preset4 = st.columns(4)

    with col_preset1:
        if st.button("💸 AI Pricing Cutoff", use_container_width=True, help="Test stale pricing: GPT-4 $30/1M vs modern GPT-4o $2.50"):
            st.session_state.input_text = DEMO_SCENARIOS["AI Model Pricing & Cutoff (High Stale Risk)"]["input_text"]
            st.rerun()

    with col_preset2:
        if st.button("⚙️ Software Versions", use_container_width=True, help="Test stale framework versions: Next.js 13 & Python 3.9"):
            st.session_state.input_text = DEMO_SCENARIOS["Software & Framework Versions (Moderate Stale Risk)"]["input_text"]
            st.rerun()

    with col_preset3:
        if st.button("👔 Tech Leadership", use_container_width=True, help="Test outdated executive leadership: Twitter CEO Jack Dorsey"):
            st.session_state.input_text = DEMO_SCENARIOS["Tech Leadership & Governance (Contradicted / Outdated)"]["input_text"]
            st.rerun()

    with col_preset4:
        if st.button("✅ Evergreen Facts", use_container_width=True, help="Test 100% verified computer science & ISO facts"):
            st.session_state.input_text = DEMO_SCENARIOS["Verified Evergreen Facts (100% Freshness Baseline)"]["input_text"]
            st.rerun()

    # Input Area
    user_input = st.text_area(
        "Paste the AI-generated answer or paragraph to verify:",
        value=st.session_state.input_text,
        height=130,
        placeholder="e.g. OpenAI's flagship model GPT-4 costs $30.00 per 1M input tokens. Next.js 13 is the latest version. Twitter is led by CEO Jack Dorsey...",
    )

    # Character count and Action Buttons
    col_actions_left, col_actions_clear, col_actions_spacer = st.columns([2, 1, 4])
    with col_actions_left:
        analyze_clicked = st.button("🚀 Audit Freshness", type="primary", use_container_width=True)
    with col_actions_clear:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.input_text = ""
            st.rerun()

    # Pipeline Execution
    if analyze_clicked:
        if not user_input or len(user_input.strip()) < config.MIN_INPUT_LENGTH:
            st.error(f"Please provide at least {config.MIN_INPUT_LENGTH} characters of text to evaluate.")
        else:
            # Check if input matches a known demo scenario in Demo Mode
            matched_scenario = None
            for name, sc in DEMO_SCENARIOS.items():
                if sc["input_text"].strip() == user_input.strip():
                    matched_scenario = name
                    break

            if not is_live_mode and matched_scenario:
                with st.spinner("Analyzing claims and loading verified evidence..."):
                    report = build_demo_report(matched_scenario)
                    st.session_state.current_report = report
                    st.session_state.history.append(report)
                    st.success("Verification complete!")
            else:
                # Live Execution
                progress_container = st.empty()
                progress_bar = progress_container.progress(0, text="Initializing deStale pipeline...")

                b_client = BifrostClient(base_url=bifrost_url, api_key=bifrost_api_key, model=bifrost_model)
                t_client = TavilySearchClient(api_key=tavily_key)
                extractor = ClaimExtractor(bifrost_client=b_client)
                verifier = FactVerifier(bifrost_client=b_client)
                scorer = FreshnessScorer()

                try:
                    # Stage 1: Extraction
                    progress_bar.progress(25, text="Extracting atomic factual propositions via Bifrost Gateway...")
                    claims = extractor.extract_claims(user_input)

                    if not claims:
                        st.warning("No factual assertions could be extracted from the submitted text.")
                    else:
                        claim_results: list[ClaimVerificationResult] = []
                        total_c = len(claims)

                        # Stage 2 & 3: Search & Verification
                        for idx, claim in enumerate(claims, 1):
                            pct = 25 + int((idx / total_c) * 55)
                            progress_bar.progress(
                                pct,
                                text=f"Querying Tavily & cross-referencing claim {idx}/{total_c}: '{claim.search_query[:35]}...'",
                            )

                            evidence = t_client.search_claim(claim.search_query)
                            verification_result = verifier.verify_claim(claim, evidence)

                            claim_score, _ = scorer.calculate_claim_score(
                                verification_result.status,
                                claim,
                                evidence,
                                confidence=verification_result.confidence,
                            )
                            verification_result.freshness_score = claim_score
                            claim_results.append(verification_result)

                        # Stage 4: Scoring
                        progress_bar.progress(90, text="Computing evidence-based freshness score...")
                        summary = scorer.calculate_aggregate_summary(claim_results)

                        # Build Report
                        report = DeStaleReport(
                            report_id=f"DESTALE-{uuid.uuid4().hex[:8].upper()}",
                            created_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                            original_text=user_input,
                            summary=summary,
                            claim_results=claim_results,
                            is_demo_mode=not is_live_mode,
                            ai_model_name=f"Bifrost Gateway ({bifrost_model})",
                            search_engine="Tavily Live Web Search",
                        )
                        st.session_state.current_report = report
                        st.session_state.history.append(report)
                        st.success("Verification complete!")
                        progress_bar.progress(100, text="Audit completed successfully!")
                        st.rerun()

                except Exception as e:
                    st.error(f"Analysis error: {str(e)}")
                    logging.exception("deStale pipeline error")

        # Display Current Audit Results
    if st.session_state.current_report:
        report: DeStaleReport = st.session_state.current_report
        st.markdown("---")
    else:
        st.stop()

    
    score = report.summary.overall_score

    summary = report.summary

    # Check actual claim statuses
    verified = summary.verified_count
    outdated = summary.outdated_count
    contradicted = summary.contradicted_count
    insufficient = summary.insufficient_count
    uncertain = summary.uncertain_count

    # If no claim is verified, outdated, or contradicted,
    # do not classify the information as stale.
    if verified + outdated + contradicted == 0:
        score_color = "#94a3b8"
        score_glow = "rgba(148, 163, 184, 0.15)"
        score_status_title = "Insufficient Evidence"
        score_desc = (
            "Not enough authoritative evidence was found "
            "to determine whether the information is accurate or outdated."
        )

    elif score >= 80.0:
        score_color = "#34d399"
        score_glow = "rgba(16, 185, 129, 0.25)"
        score_status_title = "Fresh & Accurate"
        score_desc = (
            "All evaluated statements are corroborated "
            "by current authoritative web sources."
        )

    elif score >= 50.0:
        score_color = "#fbbf24"
        score_glow = "rgba(251, 191, 36, 0.20)"
        score_status_title = "Moderate Stale Risk"
        score_desc = (
            "Certain claims may have evolved or been "
            "superseded by recent updates."
        )

    else:
        score_color = "#f87171"
        score_glow = "rgba(239, 68, 68, 0.25)"
        score_status_title = "Critical Stale / Outdated Information"
        score_desc = (
            "Significant outdated or contradicted claims "
            "were identified. Review suggested corrections below."
        )



    st.html(
    textwrap.dedent(f"""
        <div class="score-banner"
            style="box-shadow: 0 4px 25px {score_glow};">
            <div style="display:flex; justify-content:space-between;
                        align-items:center; flex-wrap:wrap; gap:20px;">

                <div style="display:flex; align-items:center; gap:24px;">
                    <div style="background:rgba(15,23,42,0.8);
                                border:2px solid {score_color};
                                border-radius:50%; width:95px; height:95px;
                                min-width:95px; display:flex;
                                flex-direction:column; align-items:center;
                                justify-content:center; text-align:center;">
                        <span style="font-size:2.1rem; font-weight:800;
                                    color:{score_color}; line-height:1;">
                            {int(score)}
                        </span>
                        <span style="font-size:0.7rem; color:#94a3b8;">
                            / 100
                        </span>
                    </div>

                    <div>
                        <div style="font-size:0.85rem; font-weight:600;
                                    color:#94a3b8; letter-spacing:0.05em;">
                            FRESHNESS AUDIT VERDICT
                        </div>
                        <div style="font-size:1.6rem; font-weight:800;
                                    color:{score_color}; margin:6px 0;">
                            {score_status_title}
                        </div>
                        <div style="font-size:0.92rem; color:#cbd5e1;">
                            {score_desc}
                        </div>
                    </div>
                </div>

                <div style="text-align:right; font-size:0.82rem;
                            color:#94a3b8;">
                    Audit ID: <code>{report.report_id}</code><br>
                    Timestamp: {report.created_at}
                </div>

            </div>
        </div>
              """)
    )


    

    # 4 Clean Metric Stat Pills

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    with col_s1:
        st.markdown(
            f"""
            <div class="stat-pill">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 600;">VERIFIED ACCURATE</div>
                <div style="font-size: 2rem; font-weight: 800; color: #34d399; margin: 4px 0;">{report.summary.verified_count}</div>
                <div style="font-size: 0.75rem; color: #64748b;">Current & corroborated</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_s2:
        st.markdown(
            f"""
            <div class="stat-pill">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 600;">OUTDATED CLAIMS</div>
                <div style="font-size: 2rem; font-weight: 800; color: #fbbf24; margin: 4px 0;">{report.summary.outdated_count}</div>
                <div style="font-size: 0.75rem; color: #64748b;">Superseded by updates</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_s3:
        st.markdown(
            f"""
            <div class="stat-pill">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 600;">CONTRADICTED</div>
                <div style="font-size: 2rem; font-weight: 800; color: #f87171; margin: 4px 0;">{report.summary.contradicted_count}</div>
                <div style="font-size: 0.75rem; color: #64748b;">Refuted by live sources</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_s4:
        unresolved = report.summary.uncertain_count + report.summary.insufficient_count
        st.markdown(
            f"""
            <div class="stat-pill">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 600;">UNCERTAIN / UNPROVEN</div>
                <div style="font-size: 2rem; font-weight: 800; color: #94a3b8; margin: 4px 0;">{unresolved}</div>
                <div style="font-size: 0.75rem; color: #64748b;">Requires further evidence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    # Summary Note
    st.info(f"**Executive Insight:** {report.summary.summary_narrative}")

    # Individual Claims List
    st.markdown("### 🔍 Verified Claims Breakdown")

    for res in report.claim_results:
                badge_class = {
                    VerificationStatus.VERIFIED: "badge-verified",
                    VerificationStatus.OUTDATED: "badge-outdated",
                    VerificationStatus.CONTRADICTED: "badge-contradicted",
                    VerificationStatus.UNCERTAIN: "badge-uncertain",
                    VerificationStatus.INSUFFICIENT_EVIDENCE: "badge-insufficient",
                }.get(res.status, "badge-insufficient")

                time_tag = "⏱️ Time-Sensitive" if res.claim.time_sensitive else "📌 Static Fact"

                st.markdown(
                    f"""
                    <div class="claim-item-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                            <div>
                                <span class="badge {badge_class}">{res.status.icon} {res.status.value}</span>
                                <span style="font-size: 0.8rem; color: #94a3b8; margin-left: 0.8rem;">{time_tag}</span>
                            </div>
                            <div style="font-weight: 700; font-size: 1.1rem; color: #38bdf8;">
                                Freshness: {res.freshness_score} / 100
                            </div>
                        </div>
                        <div style="font-size: 1.15rem; font-weight: 600; color: #f8fafc; margin-bottom: 0.6rem;">
                            "{res.claim.claim_text}"
                        </div>
                        <div style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.5;">
                            <b>Verification Rationale:</b> {res.explanation}
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Highlighted Suggested Correction
                if res.suggested_correction:
                    st.markdown(
                        f"""
                        <div class="truth-box">
                            <b>💡 Current Ground Truth & Suggested Correction:</b><br>
                            {res.suggested_correction}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Web Citations Drawer
                with st.expander(f"🌐 Inspect Live Evidence Sources ({len(res.evidence_sources)} sources retrieved)", expanded=False):
                    if not res.evidence_sources:
                        st.caption("No authoritative external sources retrieved.")
                    for ev in res.evidence_sources:
                        auth_badge = "🏛️ Authoritative Domain" if ev.is_authoritative else "🌐 Web Source"
                        date_info = f" • Published: {ev.published_date}" if ev.published_date else ""
                        st.markdown(
                            f"""
                            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #334155; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.6rem;">
                                <div style="font-weight: 600; font-size: 0.95rem;">
                                    <a href="{ev.url}" target="_blank" style="color: #38bdf8; text-decoration: none;">{ev.title} ↗</a>
                                </div>
                                <div style="font-size: 0.78rem; color: #94a3b8; margin: 0.2rem 0;">
                                    {auth_badge} • Domain: <code>{ev.domain}</code>{date_info} • Relevance: {int(ev.score * 100)}%
                                </div>
                                <div style="font-size: 0.85rem; color: #cbd5e1; font-style: italic;">
                                    "{ev.snippet}"
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                st.markdown("</div>", unsafe_allow_html=True)

        
    # Export Actions
    st.markdown("---")
    st.markdown("### 📥 Download Audit Reports")

    col_dl1, col_dl2, col_dl3 = st.columns(3)

    with col_dl1:
        pdf_bytes = ReportGenerator.generate_pdf_bytes(report)
        st.download_button(
            label="📄 Download PDF Audit Report",
            data=pdf_bytes,
            file_name=f"deStale_Audit_{report.report_id}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with col_dl2:
        csv_data = ReportGenerator.generate_csv(report)
        st.download_button(
            label="📊 Download CSV Data",
            data=csv_data,
            file_name=f"deStale_Audit_{report.report_id}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_dl3:
        md_data = ReportGenerator.generate_markdown(report)
        st.download_button(
            label="📝 Download Markdown Report",
            data=md_data,
            file_name=f"deStale_Audit_{report.report_id}.md",
            mime="text/markdown",
            use_container_width=True,
        )


# ==============================================================================
# TAB 2: STALE VS. FRESH DIFF (COMPARISON VIEW)
# ==============================================================================
with tab_diff:
    st.markdown("### ⚖️ Side-by-Side Comparison: Stale AI Claims vs. Modern Ground Truth")
    if not st.session_state.current_report:
        st.info("Run an audit in the 'Fact-Check & Audit' tab to view side-by-side corrections.")
    else:
        curr_report = st.session_state.current_report
        diff_data = []

        for r in curr_report.claim_results:
            diff_data.append({
                "ID": r.claim.id,
                "Status": f"{r.status.icon} {r.status.value}",
                "Original AI Claim": r.claim.claim_text,
                "Current Verified Ground Truth / Correction": r.suggested_correction or "Statement verified as current & accurate.",
                "Score": f"{r.freshness_score} / 100",
            })

        if pd is not None:
            df_diff = pd.DataFrame(diff_data)
            st.dataframe(df_diff, use_container_width=True, hide_index=True)
        else:
            st.dataframe(diff_data, use_container_width=True)


# ==============================================================================
# TAB 3: SCAN HISTORY
# ==============================================================================
with tab_history:
    st.markdown("### 📜 Session Scan History")
    if not st.session_state.history:
        st.info("No prior scans in this session yet.")
    else:
        for idx, h_report in enumerate(reversed(st.session_state.history), 1):
            with st.expander(f"Audit #{h_report.report_id} — Freshness: {h_report.summary.overall_score}/100 ({h_report.created_at})"):
                st.write(f"**Submitted Input:** *\"{h_report.original_text[:200]}...\"*")
                st.write(f"**Summary:** {h_report.summary.summary_narrative}")
                st.write(f"**Claims Audited:** {len(h_report.claim_results)}")


# ==============================================================================
# TAB 4: HOW DESTALE WORKS
# ==============================================================================
with tab_about:
    st.markdown("### ℹ️ How deStale Evaluates Freshness")
    st.markdown(
        """
        Large Language Models (LLMs) often generate obsolete information because their internal training data is frozen at cutoff dates.
        **deStale** provides a live, zero-trust verification layer:
        """
    )

    st.markdown(
        """
        ```mermaid
        graph LR
            Input[AI Output Text] --> Split[1. Claim Extractor]
            Split -->|Atomic Claims| Search[2. Tavily Live Search]
            Search -->|Evidence Snippets| Verifier[3. Fact Verifier]
            Verifier -->|Classifications| Scorer[4. Freshness Scorer]
            Scorer --> Report[5. Audited Report & Corrections]
        ```
        """
    )

    st.markdown(
        """
        #### 🧮 Freshness Scoring Heuristic
        deStale uses an **evidence-based empirical index (0 to 100)** rather than pseudo-scientific probabilities:
        
        1. **Base Classification Baseline**:
           - **Verified / Supported:** `100.0`
           - **Outdated (Superseded):** `15.0` (Severe penalty for stale historical facts)
           - **Contradicted (Refuted):** `0.0`
           - **Uncertain:** `45.0`
           - **Insufficient Evidence:** `50.0`
        
        2. **Multi-Source Guardrail**:
           - A claim is **never verified** on a single random website. Corroboration by multiple sources or high-authority domains (`.gov`, `.edu`, official documentation) is required.
        
        3. **Time-Sensitivity Weighting**:
           - Facts with prices, releases, versions, or dates receive **1.5x weight** in the overall index to immediately flag high-risk stale information.
        """
    )
