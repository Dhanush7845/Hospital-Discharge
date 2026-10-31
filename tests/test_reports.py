import pytest
import pandas as pd
from modules.report_generator import generate_pdf_report, generate_kpi_excel
from modules.kpi_calculations import calculate_core_kpis
from modules.bottleneck_detection import detect_bottlenecks
from modules.analytics import compute_research_statistics

def test_pdf_report_generation():
    """Verify that ReportLab generates valid, non-empty binary PDF streams."""
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=10),
        "apprehensions": [20] * 10,
        "cbp_custody": [30] * 10,
        "transfers": [18] * 10,
        "hhs_care": [500] * 10,
        "discharges": [15] * 10
    })
    
    kpis = calculate_core_kpis(df)
    bottlenecks = detect_bottlenecks(df)
    stats_dict = compute_research_statistics(df)
    
    # Test all 3 PDF variants
    for r_type in ["Executive Summary", "Detailed Analytical Report", "Research Findings"]:
        pdf_bytes = generate_pdf_report(df, kpis, r_type, bottlenecks=bottlenecks, stats_dict=stats_dict)
        assert isinstance(pdf_bytes, bytes), f"PDF output should be bytes for {r_type}"
        assert len(pdf_bytes) > 1000, f"PDF file size too small for {r_type}"
        # PDF files start with %PDF
        assert pdf_bytes.startswith(b"%PDF"), f"PDF header missing for {r_type}"

def test_excel_report_generation():
    """Verify that OpenPyXL generates valid Excel binary workbook."""
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=5),
        "apprehensions": [25] * 5,
        "cbp_custody": [35] * 5,
        "transfers": [22] * 5,
        "hhs_care": [600] * 5,
        "discharges": [19] * 5
    })
    kpis = calculate_core_kpis(df)
    excel_bytes = generate_kpi_excel(df, kpis)
    
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 2000
    # ZIP signature for .xlsx
    assert excel_bytes.startswith(b"PK")
