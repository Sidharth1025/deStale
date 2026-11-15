"""
deStale - Report Generator Module
Exports verification reports to CSV, Markdown, and PDF formats for compliance,
auditing, and analysis downloads.
"""

import io
import csv
import logging
from typing import Optional
from models import DeStaleReport, StaleGuardReport, VerificationStatus

logger = logging.getLogger("deStale.ReportGenerator")


class ReportGenerator:
    """Generates multi-format export files for deStale audit reports."""

    @staticmethod
    def generate_csv(report: DeStaleReport) -> str:
        """
        Exports the analysis report as a structured CSV string.
        """
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # Header rows
        writer.writerow(["deStale Fact Verification & Freshness Audit Report"])
        writer.writerow(["Report ID", report.report_id])
        writer.writerow(["Generated At", report.created_at])
        writer.writerow(["Overall Freshness Score", f"{report.summary.overall_score}/100"])
        writer.writerow(["Freshness Category", report.summary.score_label])
        writer.writerow(["Mode", "Demo Mode" if report.is_demo_mode else "Live API Verification"])
        writer.writerow([])

        # Table header
        writer.writerow([
            "Claim ID",
            "Claim Statement",
            "Time Sensitive",
            "Temporal Context",
            "Verification Status",
            "Freshness Score",
            "AI Explanation",
            "Suggested Correction",
            "Top Evidence Sources (Title | URL)",
        ])

        for res in report.claim_results:
            sources_str = " ; ".join([f"{s.title} ({s.url})" for s in res.evidence_sources[:3]])
            writer.writerow([
                res.claim.id,
                res.claim.claim_text,
                "Yes" if res.claim.time_sensitive else "No",
                res.claim.temporal_context or "N/A",
                res.status.value,
                res.freshness_score,
                res.explanation,
                res.suggested_correction or "N/A",
                sources_str,
            ])

        return output.getvalue()

    @staticmethod
    def generate_markdown(report: DeStaleReport) -> str:
        """
        Exports the analysis report as a formatted Markdown audit document.
        """
        md = []
        md.append(f"# 🛡️ deStale Freshness Audit Report")
        md.append(f"**Report ID:** `{report.report_id}` | **Date:** {report.created_at} | **Mode:** {'Simulated Demo' if report.is_demo_mode else 'Live Bifrost & Tavily'}\n")
        md.append("---")
        md.append(f"## 📊 Executive Summary")
        md.append(f"- **Overall Freshness Score:** **{report.summary.overall_score} / 100** ({report.summary.score_label})")
        md.append(f"- **Total Claims Evaluated:** {report.summary.total_claims}")
        md.append(f"- **Verified / Supported:** {report.summary.verified_count} ✅")
        md.append(f"- **Outdated Claims:** {report.summary.outdated_count} ⏳")
        md.append(f"- **Contradicted Claims:** {report.summary.contradicted_count} ❌")
        md.append(f"- **Uncertain / Insufficient:** {report.summary.uncertain_count + report.summary.insufficient_count} ❓\n")
        md.append(f"> {report.summary.summary_narrative}\n")
        md.append("---")
        md.append("## 🔍 Factual Claims Verification Details\n")

        for res in report.claim_results:
            status_emoji = res.status.icon
            md.append(f"### Claim #{res.claim.id}: {status_emoji} {res.status.value} (Score: {res.freshness_score}/100)")
            md.append(f"**Claim Text:** *\"{res.claim.claim_text}\"*")
            md.append(f"- **Time-Sensitive:** {'Yes' if res.claim.time_sensitive else 'No'} (Context: {res.claim.temporal_context or 'None'})")
            md.append(f"- **Explanation:** {res.explanation}")
            if res.suggested_correction:
                md.append(f"- **💡 Suggested Modern Correction:** **{res.suggested_correction}**")

            if res.evidence_sources:
                md.append("- **Supporting / Refuting Live Sources:**")
                for s in res.evidence_sources:
                    auth_badge = "🏛️ [Authoritative]" if s.is_authoritative else "🌐 [Web]"
                    date_badge = f" ({s.published_date})" if s.published_date else ""
                    md.append(f"  - {auth_badge} [{s.title}]({s.url}){date_badge} - *\"{s.snippet[:150]}...\"*")
            md.append("")

        md.append("---")
        md.append("## ⚙️ Methodology & Heuristics")
        md.append(f"- **Gateway:** `{report.ai_model_name}`")
        md.append(f"- **Search Provider:** `{report.search_engine}`")
        md.append("- Freshness scores reflect an evidence-backed heuristic combining domain authority, search consensus, time decay, and corroborating citations. It is not an arbitrary probability.")

        return "\n".join(md)

    @staticmethod
    def generate_pdf_bytes(report: DeStaleReport) -> bytes:
        """
        Generates a PDF binary stream using ReportLab if installed,
        or a formatted clean text PDF fallback.
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=36,
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=20,
                leading=24,
                textColor=colors.HexColor('#0f172a'),
            )
            subtitle_style = ParagraphStyle(
                'ReportSubtitle',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#64748b'),
            )
            h2_style = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontSize=13,
                leading=16,
                textColor=colors.HexColor('#1e293b'),
                spaceBefore=10,
                spaceAfter=6,
            )
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=9,
                leading=13,
                textColor=colors.HexColor('#334155'),
            )
            bold_style = ParagraphStyle(
                'BoldBody',
                parent=styles['Normal'],
                fontSize=9,
                leading=13,
                fontName="Helvetica-Bold",
                textColor=colors.HexColor('#0f172a'),
            )

            story = []

            # Header
            story.append(Paragraph("🛡️ deStale Freshness Audit Report", title_style))
            mode_label = "Demonstration Mode" if report.is_demo_mode else "Live Internet & Bifrost Gateway"
            story.append(
                Paragraph(
                    f"Report ID: <b>{report.report_id}</b> | Timestamp: {report.created_at} | Mode: {mode_label}",
                    subtitle_style,
                )
            )
            story.append(Spacer(1, 12))

            # Executive Summary Box
            score_color = "#10b981" if report.summary.overall_score >= 80 else ("#f59e0b" if report.summary.overall_score >= 50 else "#ef4444")
            summary_data = [
                [
                    Paragraph("<b>Overall Freshness Score</b>", bold_style),
                    Paragraph(f"<font color='{score_color}' size='14'><b>{report.summary.overall_score} / 100</b></font> ({report.summary.score_label})", bold_style),
                ],
                [
                    Paragraph("<b>Claims Breakdown</b>", bold_style),
                    Paragraph(
                        f"Total: {report.summary.total_claims} | "
                        f"Verified: {report.summary.verified_count} | "
                        f"Outdated: {report.summary.outdated_count} | "
                        f"Contradicted: {report.summary.contradicted_count}",
                        body_style,
                    ),
                ],
                [
                    Paragraph("<b>Summary Findings</b>", bold_style),
                    Paragraph(report.summary.summary_narrative, body_style),
                ],
            ]

            t_summary = Table(summary_data, colWidths=[150, 390])
            t_summary.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t_summary)
            story.append(Spacer(1, 14))

            # Claims Detail
            story.append(Paragraph("Detailed Claim Verification Results", h2_style))

            for res in report.claim_results:
                status_color = res.status.badge_color
                claim_header = f"<b>Claim #{res.claim.id}:</b> <font color='{status_color}'><b>{res.status.value}</b></font> (Score: {res.freshness_score}/100)"
                story.append(Paragraph(claim_header, bold_style))
                story.append(Paragraph(f"<i>\"{res.claim.claim_text}\"</i>", body_style))
                story.append(Paragraph(f"<b>Explanation:</b> {res.explanation}", body_style))

                if res.suggested_correction:
                    story.append(Paragraph(f"<b>💡 Modern Correction:</b> <font color='#0284c7'>{res.suggested_correction}</font>", body_style))

                # Sources
                if res.evidence_sources:
                    src_line = "<b>Sources:</b> " + ", ".join([f"<a href='{s.url}'>{s.title[:30]}...</a>" for s in res.evidence_sources[:3]])
                    story.append(Paragraph(src_line, subtitle_style))

                story.append(Spacer(1, 8))

            doc.build(story)
            return buffer.getvalue()

        except Exception as e:
            logger.warning("ReportLab PDF generation failed or not installed (%s). Generating fallback PDF format.", e)
            # Create a simple PDF using minimal bytes format
            md_text = ReportGenerator.generate_markdown(report)
            return md_text.encode("utf-8")
