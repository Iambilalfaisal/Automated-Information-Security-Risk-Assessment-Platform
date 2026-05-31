"""
report_generator.py — ReportLab PDF generation for risk register, CBA, and compliance.
"""

import io
from datetime import datetime
from typing import Any, Optional

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

CRITICALITY_COLORS = {
    "Critical": colors.HexColor("#DC2626"),
    "High": colors.HexColor("#EA580C"),
    "Medium": colors.HexColor("#CA8A04"),
    "Low": colors.HexColor("#16A34A"),
}

BIBLIOGRAPHY = (
    "[1] Rahman, M. M., et al. (2024). AssessITS: Automated Information Security "
    "Threat Assessment. arXiv:2410.01750.<br/>"
    "[2] NIST. (2012). SP 800-30 Rev. 1, Guide for Conducting Risk Assessments."
)


def _footer(canvas, doc):
    """Page footer with confidentiality notice and page number."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(
        inch,
        0.5 * inch,
        f"CONFIDENTIAL — Risk Assessment Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    )
    canvas.drawRightString(letter[0] - inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCustom",
            parent=styles["Title"],
            fontSize=18,
            spaceAfter=12,
        )
    )
    return styles


def _risk_row_color(criticality: str):
    return CRITICALITY_COLORS.get(criticality, colors.white)


def _make_pie_chart(register: list[dict]) -> Drawing:
    """Pie chart of risk distribution by criticality."""
    d = Drawing(300, 150)
    pie = Pie()
    pie.x = 65
    pie.y = 15
    pie.width = 120
    pie.height = 120
    counts: dict[str, int] = {}
    for r in register:
        c = r.get("risk_criticality", "Low")
        counts[c] = counts.get(c, 0) + 1
    if not counts:
        counts = {"Low": 1}
    pie.data = list(counts.values())
    pie.labels = list(counts.keys())
    d.add(pie)
    return d


def _make_bar_chart(register: list[dict]) -> Drawing:
    """Bar chart of top 10 risks by impact rating."""
    d = Drawing(400, 180)
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.height = 100
    chart.width = 300
    top = register[:10]
    chart.data = [[r.get("risk_impact_rating", 0) for r in top]]
    chart.categoryAxis.categoryNames = [
        (r.get("asset_name", "")[:8] + "…") if len(r.get("asset_name", "")) > 8 else r.get("asset_name", "A")
        for r in top
    ]
    d.add(chart)
    return d


def generate_risk_register_pdf(
    register: list[dict[str, Any]],
    org_name: str = "Organisation",
    executive_summary: str = "",
) -> bytes:
    """
    Generate Risk Register PDF with tables and charts.

    Returns:
        PDF file bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=inch, bottomMargin=inch)
    styles = _styles()
    story = []

    story.append(Paragraph(f"<b>{org_name}</b> — Information Security Risk Register", styles["TitleCustom"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    summary = executive_summary or (
        "This report summarises quantitative risk analysis per NIST SP 800-30 and "
        "AssessITS methodology (Rahman et al., 2024)."
    )
    story.append(Paragraph("<b>Executive Summary</b>", styles["Heading2"]))
    story.append(Paragraph(summary, styles["Normal"]))
    story.append(Spacer(1, 12))

    headers = ["Asset", "Threat", "SLE", "ALE", "R Score", "Criticality", "CBA Rec."]
    rows = [headers]
    for r in register:
        rows.append(
            [
                str(r.get("asset_name", ""))[:20],
                str(r.get("threat_name", ""))[:20],
                f"${r.get('sle', 0):,.0f}",
                f"${r.get('ale', 0):,.0f}",
                str(r.get("risk_score", "")),
                r.get("risk_criticality", ""),
                "Yes" if r.get("control_recommended") else "No",
            ]
        )
    table = Table(rows, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]
    for i, r in enumerate(register, start=1):
        crit = r.get("risk_criticality", "Low")
        style_cmds.append(("BACKGROUND", (5, i), (5, i), _risk_row_color(crit)))
    table.setStyle(TableStyle(style_cmds))
    story.append(table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("<b>Risk Distribution</b>", styles["Heading2"]))
    story.append(_make_pie_chart(register))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Top 10 Risks by Impact Rating</b>", styles["Heading2"]))
    story.append(_make_bar_chart(register))
    story.append(PageBreak())

    story.append(Paragraph("<b>Cost-Benefit Analysis</b>", styles["Heading2"]))
    cba_headers = ["Threat", "Control Cost", "ALE Before", "ALE After", "Net CBA"]
    cba_rows = [cba_headers]
    for r in register[:15]:
        cba_rows.append(
            [
                str(r.get("threat_name", ""))[:25],
                f"${r.get('control_cost', 0):,.0f}",
                f"${r.get('ale_before', 0):,.0f}",
                f"${r.get('ale_after', 0):,.0f}",
                f"${r.get('cba', 0):,.0f}",
            ]
        )
    cba_table = Table(cba_rows, repeatRows=1)
    cba_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(cba_table)
    story.append(Spacer(1, 24))
    story.append(Paragraph("<b>References</b>", styles["Heading2"]))
    story.append(Paragraph(BIBLIOGRAPHY, styles["Normal"]))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()


def generate_cba_pdf(register: list[dict[str, Any]], org_name: str = "Organisation") -> bytes:
    """Generate standalone CBA report PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = _styles()
    story = [
        Paragraph(f"<b>{org_name}</b> — Cost-Benefit Analysis Report", styles["TitleCustom"]),
        Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), styles["Normal"]),
        Spacer(1, 16),
    ]
    headers = ["Control / Threat", "Cost", "ALE Before", "ALE After", "Net Benefit", "Recommended"]
    rows = [headers]
    for r in register:
        rows.append(
            [
                str(r.get("threat_name", "")),
                f"${r.get('control_cost', 0):,.0f}",
                f"${r.get('ale_before', 0):,.0f}",
                f"${r.get('ale_after', 0):,.0f}",
                f"${r.get('cba', 0):,.0f}",
                "Yes" if r.get("control_recommended") else "No",
            ]
        )
    t = Table(rows, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 24))
    story.append(Paragraph(BIBLIOGRAPHY, styles["Normal"]))
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()


def generate_compliance_pdf(
    compliance_items: list[dict[str, Any]],
    org_name: str = "Organisation",
    score_pct: float = 0.0,
) -> bytes:
    """Generate NIST 800-30 compliance checklist PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = _styles()
    story = [
        Paragraph(f"<b>{org_name}</b> — NIST SP 800-30 Compliance Checklist", styles["TitleCustom"]),
        Paragraph(f"Compliance Score: {score_pct:.1f}%", styles["Heading2"]),
        Spacer(1, 12),
    ]
    headers = ["Control ID", "Control Name", "Status", "Notes"]
    rows = [headers]
    for item in compliance_items:
        rows.append(
            [
                item.get("control_id", ""),
                item.get("control_name", ""),
                item.get("status", "not_implemented"),
                (item.get("notes") or "")[:40],
            ]
        )
    t = Table(rows, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 24))
    story.append(Paragraph(BIBLIOGRAPHY, styles["Normal"]))
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()
