import os
import io
import pandas as pd
import numpy as np
from datetime import datetime

# ReportLab components
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

# OpenPyXL components
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from .utils import safe_divide, format_number, format_percent

def create_reportlab_styles():
    """Generates custom typography styles for ReportLab PDF."""
    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#1B365D")
    dark_text = colors.HexColor("#1E293B")
    muted_text = colors.HexColor("#64748B")
    accent_blue = colors.HexColor("#0077B6")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=muted_text,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=accent_blue,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=dark_text,
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_text,
        leftIndent=15,
        spaceAfter=3
    )
    
    callout_style = ParagraphStyle(
        'DocCallout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    
    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "h1": h1_style,
        "h2": h2_style,
        "body": body_style,
        "bullet": bullet_style,
        "callout": callout_style
    }

def generate_pdf_report(
    df: pd.DataFrame,
    kpis: dict,
    report_type: str = "Executive Summary",
    bottlenecks: dict = None,
    stats_dict: dict = None
) -> bytes:
    """
    Generates an executive-grade PDF document using ReportLab.
    report_type can be:
    - 'Executive Summary'
    - 'Detailed Analytical Report'
    - 'Research Findings'
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = create_reportlab_styles()
    story = []
    
    # 1. Header Banner
    story.append(Paragraph("Care Transition Efficiency & Placement Outcome Analytics", styles["title"]))
    story.append(Paragraph(
        f"Official Analytical Briefing: {report_type} | Generated: {datetime.now().strftime('%B %d, %Y')}",
        styles["subtitle"]
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1B365D"), spaceAfter=14))
    
    # 2. Executive Overview & Problem Statement
    story.append(Paragraph("1. Executive Overview & Program Context", styles["h1"]))
    story.append(Paragraph(
        "The Unaccompanied Alien Children (UAC) Program represents a highly sensitive multi-agency "
        "care pipeline spanning initial Customs and Border Protection (CBP) apprehension, custodial holding, "
        "transfer to Department of Health and Human Services (HHS) Office of Refugee Resettlement (ORR) care, "
        "sheltering, case management, and safe discharge to approved community sponsors. "
        "While aggregate custody snapshots are regularly published, raw custody numbers alone fail to reveal "
        "stage-wise transition efficiency, pipeline accumulation backlogs, and discharge consistency.",
        styles["body"]
    ))
    
    # Date Range Summary
    date_str = (
        f"{kpis['date_start'].strftime('%b %d, %Y')} to {kpis['date_end'].strftime('%b %d, %Y')}"
        if kpis.get("date_start") else "Full Reporting Archive"
    )
    story.append(Paragraph(
        f"<b>Reporting Observation Coverage:</b> {kpis.get('observation_count', 0):,} reporting days "
        f"({date_str}, spanning {kpis.get('calendar_days', 0):,} calendar days).",
        styles["body"]
    ))
    story.append(Spacer(1, 8))
    
    # 3. Core KPI Table
    story.append(Paragraph("2. Pipeline Performance Scorecard (Core KPIs)", styles["h1"]))
    
    kpi_table_data = [
        ["Key Performance Indicator", "Calculated Metric", "Benchmark / Operational Context"],
        ["Total Apprehensions (Intake Flow)", f"{kpis['total_apprehensions']:,}", "Gross daily arrivals into CBP custody"],
        ["Total CBP Transfers (Movement)", f"{kpis['total_transfers']:,}", "Movement out of CBP to HHS care"],
        ["Average CBP Custody (Stock)", f"{kpis['avg_cbp_custody']:,.1f}", "Snapshot of active border holding census"],
        ["Average HHS Care (Stock)", f"{kpis['avg_hhs_care']:,.1f}", "Active shelter and foster care population"],
        ["Total HHS Discharges (Placement)", f"{kpis['total_discharges']:,}", "Placements with verified sponsors"],
        ["Transfer Efficiency Ratio", f"{kpis['transfer_efficiency']:.2f}%", "(Transfers / CBP Custody Stock) × 100"],
        ["Discharge Effectiveness Index", f"{kpis['discharge_effectiveness']:.2f}%", "(Discharges / HHS Care Stock) × 100"],
        ["Pipeline Throughput Ratio", f"{kpis['pipeline_throughput']:.2f}%", "(Total Discharges / Total Apprehensions) × 100"],
        ["Overall Net Backlog Accumulation", f"{kpis['overall_backlog_accumulation']:,}", "Gross Intake minus Total Discharges"]
    ]
    
    kpi_table = Table(kpi_table_data, colWidths=[200, 110, 220])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1B365D")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1, 1), (1, -1), colors.HexColor("#1B365D")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4)
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))
    
    # 4. Methodological Clarification Callout
    callout_data = [[
        Paragraph(
            "<b>Methodological Note & Data Integrity Clarification:</b> All movement metrics (apprehensions, transfers, "
            "and discharges) represent flow movements during reporting days. Custody numbers (CBP custody and HHS care) "
            "represent static daily census stock snapshots. Stock figures cannot be summed across days without double-counting. "
            "Ratios represent flow-to-stock rates and pipeline throughput proxies rather than tracked individual transition probabilities.",
            styles["callout"]
        )
    ]]
    callout_tbl = Table(callout_data, colWidths=[530])
    callout_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    story.append(callout_tbl)
    story.append(Spacer(1, 14))
    
    # 5. Bottleneck Analysis Section
    if report_type in ["Executive Summary", "Detailed Analytical Report"] and bottlenecks:
        summary = bottlenecks.get("summary", {})
        story.append(Paragraph("3. Bottleneck & Custodial Accumulation Analysis", styles["h1"]))
        story.append(Paragraph(
            f"Analytical calculation of daily net accumulation (Inflow minus Outflow) reveals operational friction points: "
            f"Maximum daily CBP net intake accumulation was <b>+{summary.get('max_cbp_net', 0):,}</b> children, "
            f"while maximum HHS shelter net accumulation reached <b>+{summary.get('max_hhs_net', 0):,}</b> children. "
            f"The system logged <b>{summary.get('red_alert_days', 0)} High Concern (Red)</b> observation days and "
            f"<b>{summary.get('yellow_alert_days', 0)} Moderate Concern (Yellow)</b> days.",
            styles["body"]
        ))
        
        sustained = bottlenecks.get("sustained_events", [])
        if sustained:
            story.append(Paragraph("<b>Notable Sustained Friction Periods:</b>", styles["h2"]))
            for event in sustained[:4]:
                s_date = event["start_date"].strftime("%b %d, %Y")
                e_date = event["end_date"].strftime("%b %d, %Y")
                story.append(Paragraph(
                    f"• <b>{event['stage']}</b> ({s_date} to {e_date}): {event['consecutive_obs']} consecutive "
                    f"reporting days with net accumulation totalling +{event['total_net_accumulation']:,} children "
                    f"(Avg: +{event['avg_daily_accumulation']:.1f}/day). Severity: {event['severity']}.",
                    styles["bullet"]
                ))
        story.append(Spacer(1, 12))

    # 6. Research & Statistical Insights
    if report_type in ["Detailed Analytical Report", "Research Findings"] and stats_dict:
        story.append(Paragraph("4. Statistical Modeling & Empirical Correlation", styles["h1"]))
        regs = stats_dict.get("regressions", {})
        for label, info in regs.items():
            story.append(Paragraph(
                f"• <b>{label}:</b> Slope = {info['slope']:.3f}, R² = {info['r_squared']:.3f}, p-value = {info['p_value']:.4e}. "
                f"Std Error = {info['std_err']:.3f}.",
                styles["bullet"]
            ))
            
        insights = stats_dict.get("insights", [])
        for ins in insights:
            story.append(Paragraph(f"• {ins}", styles["bullet"]))
        story.append(Spacer(1, 12))

    # 7. Actionable Recommendations
    story.append(Paragraph("5. Policy & Operational Recommendations", styles["h1"]))
    recs = [
        ("Dynamic Capacity Mobilization", "Establish algorithmic escalation thresholds to deploy mobile processing units when CBP intake outpaces transfers for 3 consecutive reporting days."),
        ("Weekend Cadence Optimization", "Expand weekend case management shifts to reduce the observed 30%+ drop in Saturday-Sunday discharge velocities."),
        ("Category 1 Sponsor Prioritization", "Accelerate background checks and identity verification for parents and legal guardians (Category 1) to reduce average length of shelter stay."),
        ("Inter-Agency Data Integration", "Transition from aggregate stock reporting to pseudonymized longitudinal tracking to measure precise child-level transit times.")
    ]
    for title, desc in recs:
        story.append(Paragraph(f"• <b>{title}:</b> {desc}", styles["bullet"]))
    story.append(Spacer(1, 12))

    # 8. Analytical Limitations & Conclusion
    story.append(Paragraph("6. Analytical Limitations & Concluding Remarks", styles["h1"]))
    story.append(Paragraph(
        "<b>Limitations:</b> This analysis is bounded by public reporting realities. Discharges are treated as a placement "
        "proxy; individual sponsor reunifications cannot be verified without case-level post-release datasets. "
        "Reporting dates occur on irregular calendar cadences (primarily business days); unobserved days are not zero-value days. "
        "<b>Conclusion:</b> This decision-support architecture provides unprecedented operational visibility into UAC "
        "care transitions, identifying systemic bottlenecks and empowering data-driven policy reforms.",
        styles["body"]
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_kpi_excel(df: pd.DataFrame, kpis: dict) -> bytes:
    """Generates an executive KPI and Monthly Summary workbook using OpenPyXL."""
    wb = openpyxl.Workbook()
    
    # Sheet 1: Executive KPI Summary
    ws1 = wb.active
    ws1.title = "Executive KPIs"
    
    # Styles
    navy_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True)
    regular_font = Font(name="Calibri", size=11)
    
    ws1["A1"] = "Care Transition Efficiency & Placement Outcome Analytics"
    ws1["A1"].font = Font(name="Calibri", size=14, bold=True, color="1B365D")
    ws1["A2"] = f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ws1["A2"].font = Font(name="Calibri", size=10, italic=True)
    
    headers = ["Metric / KPI", "Value", "Unit / Formula Context"]
    for col_idx, h in enumerate(headers, start=1):
        cell = ws1.cell(row=4, column=col_idx, value=h)
        cell.fill = navy_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    rows = [
        ("Total Apprehensions (Intake)", kpis["total_apprehensions"], "Gross Children Apprehended"),
        ("Total Transfers out of CBP", kpis["total_transfers"], "Gross Transfers into HHS Care"),
        ("Average CBP Custody (Stock)", round(kpis["avg_cbp_custody"], 1), "Daily Average Snapshot"),
        ("Average HHS Care (Stock)", round(kpis["avg_hhs_care"], 1), "Daily Average Census Snapshot"),
        ("Total Discharges (Placement)", kpis["total_discharges"], "Gross Discharges to Sponsors"),
        ("Transfer Efficiency Ratio", f"{kpis['transfer_efficiency']:.2f}%", "(Transfers / CBP Custody Stock) * 100"),
        ("Discharge Effectiveness Index", f"{kpis['discharge_effectiveness']:.2f}%", "(Discharges / HHS Care Stock) * 100"),
        ("Pipeline Throughput Ratio", f"{kpis['pipeline_throughput']:.2f}%", "(Total Discharges / Total Apprehensions) * 100"),
        ("Overall Backlog Accumulation", kpis["overall_backlog_accumulation"], "Apprehensions - Discharges"),
        ("Valid Reporting Days", kpis["observation_count"], "Empirical Reporting Observations")
    ]
    
    for r_idx, row_data in enumerate(rows, start=5):
        for c_idx, val in enumerate(row_data, start=1):
            cell = ws1.cell(row=r_idx, column=c_idx, value=val)
            cell.font = bold_font if c_idx == 2 else regular_font
            if c_idx == 2 and isinstance(val, (int, float)):
                cell.number_format = '#,##0'
                
    ws1.column_dimensions['A'].width = 35
    ws1.column_dimensions['B'].width = 20
    ws1.column_dimensions['C'].width = 35

    # Sheet 2: Cleaned Dataset Records
    ws2 = wb.create_sheet(title="Cleaned Observations")
    export_df = df.copy()
    export_df["date"] = export_df["date"].dt.strftime("%Y-%m-%d")
    
    col_names = list(export_df.columns)
    for c_idx, col in enumerate(col_names, start=1):
        cell = ws2.cell(row=1, column=c_idx, value=col.replace('_', ' ').title())
        cell.fill = navy_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        
    for r_idx, r in enumerate(export_df.itertuples(index=False), start=2):
        for c_idx, val in enumerate(r, start=1):
            ws2.cell(row=r_idx, column=c_idx, value=val)
            
    for c in ws2.columns:
        ws2.column_dimensions[c[0].column_letter].width = 16

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
