"""
End-to-end integration test for StaleGuard pipeline.
Validates extraction -> search -> verification -> report generation -> export (CSV/Markdown/PDF).
"""

import pytest
from unittest.mock import MagicMock
from demo_data import build_demo_report
from report_generator import ReportGenerator
from models import VerificationStatus


def test_end_to_end_demo_scenario():
    # Build demo report for AI pricing scenario
    report = build_demo_report("AI Model Pricing & Cutoff (High Stale Risk)")

    assert report.report_id.startswith("DESTALE-")
    assert len(report.claim_results) == 3
    assert report.summary.overall_score < 50.0  # Stale pricing should produce high risk score
    assert report.summary.outdated_count >= 2

    # Verify CSV generation
    csv_text = ReportGenerator.generate_csv(report)
    assert "deStale Fact Verification" in csv_text
    assert "OpenAI's flagship model GPT-4" in csv_text

    # Verify Markdown generation
    md_text = ReportGenerator.generate_markdown(report)
    assert "# 🛡️ deStale Freshness Audit Report" in md_text
    assert "Executive Summary" in md_text

    # Verify PDF bytes generation
    pdf_bytes = ReportGenerator.generate_pdf_bytes(report)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 100
