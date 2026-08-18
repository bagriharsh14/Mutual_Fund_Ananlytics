"""
run_pipeline.py — Master Execution Pipeline for Bluestock Mutual Fund Analytics.

This script orchestrates the full end-to-end pipeline in sequence:
  1. Data Ingestion (ETL) — loads raw CSVs into bluestock_mf.db
  2. Performance Analytics — computes CAGR, Sharpe, Sortino, Alpha, Beta, Max Drawdown, Scorecard
  3. Dashboard Generation — generates 4-page PNG dashboard and combined Dashboard.pdf
  4. Report Generation — generates Final_Report.pdf (15 pages)
  5. Presentation Generation — generates Bluestock_MF_Presentation.pptx (12 slides)

Usage:
    python run_pipeline.py
"""

import subprocess
import sys
import os


def run_step(description, script_path):
    """Execute a single pipeline step via subprocess and report result."""
    print(f"\n[STEP] {description}")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ERROR] {description} failed:")
        print(result.stdout[-1000:] if result.stdout else "")
        print(result.stderr[-1000:] if result.stderr else "")
        sys.exit(1)
    else:
        print(f"  [OK] {description} completed.")


def main():
    """Main orchestrator — runs all pipeline stages in sequence."""
    base = os.path.dirname(os.path.abspath(__file__))

    print("=" * 60)
    print("  BLUESTOCK MUTUAL FUND ANALYTICS — MASTER PIPELINE")
    print("=" * 60)

    # Step 1: Data ingestion
    ingestion_script = os.path.join(base, 'data_ingestion.py')
    if os.path.exists(ingestion_script):
        run_step("Data Ingestion (ETL) — Loading raw data into bluestock_mf.db", ingestion_script)
    else:
        print("  [SKIP] data_ingestion.py not found — assuming DB already populated.")

    # Step 2: Performance analytics (notebook execution)
    perf_notebook = os.path.join(base, 'Performance_Analytics.ipynb')
    if os.path.exists(perf_notebook):
        print("\n[STEP] Performance Analytics — Executing Performance_Analytics.ipynb")
        result = subprocess.run(
            [sys.executable, '-m', 'nbconvert', '--execute', '--to', 'notebook',
             '--inplace', perf_notebook],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("  [WARN] Performance Analytics notebook execution encountered warnings.")
        else:
            print("  [OK] Performance Analytics notebook executed.")

    # Step 3: Advanced analytics (notebook execution)
    adv_notebook = os.path.join(base, 'Advanced_Analytics.ipynb')
    if os.path.exists(adv_notebook):
        print("\n[STEP] Advanced Analytics — Executing Advanced_Analytics.ipynb")
        result = subprocess.run(
            [sys.executable, '-m', 'nbconvert', '--execute', '--to', 'notebook',
             '--inplace', adv_notebook],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("  [WARN] Advanced Analytics notebook execution encountered warnings.")
        else:
            print("  [OK] Advanced Analytics notebook executed.")

    # Step 4: Dashboard generation
    dashboard_script = os.path.join(base, 'generate_dashboard.py')
    if os.path.exists(dashboard_script):
        run_step("Dashboard Generation — 4-page PNG + Dashboard.pdf", dashboard_script)

    # Step 5: Final PDF report
    report_script = os.path.join(base, 'scratch', 'make_report.py')
    if os.path.exists(report_script):
        run_step("Final Report — Generating Final_Report.pdf (15 pages)", report_script)

    # Step 6: PPTX presentation
    pptx_script = os.path.join(base, 'scratch', 'make_presentation.py')
    if os.path.exists(pptx_script):
        run_step("Presentation — Generating Bluestock_MF_Presentation.pptx (12 slides)", pptx_script)

    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)
    print("\nDeliverables:")
    deliverables = [
        ('Performance_Analytics.ipynb', 'Performance Analytics Notebook'),
        ('Advanced_Analytics.ipynb', 'Advanced Risk Modeling Notebook'),
        ('fund_scorecard.csv', 'Composite Fund Scorecard (40 funds)'),
        ('alpha_beta.csv', 'OLS Alpha & Beta Report'),
        ('var_cvar_report.csv', 'Historical VaR/CVaR Risk Report'),
        ('benchmark_comparison_chart.png', 'Benchmark Comparison Chart'),
        ('rolling_sharpe_chart.png', 'Rolling 90-Day Sharpe Chart'),
        ('recommender.py', 'Fund Recommender CLI Script'),
        ('Dashboard/Page1_Industry_Overview.png', 'Dashboard Page 1 PNG'),
        ('Dashboard/Page2_Fund_Performance.png', 'Dashboard Page 2 PNG'),
        ('Dashboard/Page3_Investor_Analytics.png', 'Dashboard Page 3 PNG'),
        ('Dashboard/Page4_SIP_Market_Trends.png', 'Dashboard Page 4 PNG'),
        ('Dashboard/Dashboard.pdf', 'Dashboard Combined PDF'),
        ('Final_Report.pdf', 'Final Report PDF (15 pages)'),
        ('Bluestock_MF_Presentation.pptx', 'PowerPoint Presentation (12 slides)'),
    ]
    for fname, desc in deliverables:
        exists = os.path.exists(os.path.join(base, fname))
        status = '[OK]' if exists else '[MISSING]'
        print(f"  {status}  {fname}  ({desc})")


if __name__ == '__main__':
    main()
