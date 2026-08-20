"""
run_pipeline.py — Master Execution Pipeline for Mutual Fund Capstone Project

Orchestrates the full end-to-end pipeline in sequence:
  1. Data Ingestion & ETL — loads raw CSVs into SQLite (data/db/bluestock_mf.db)
  2. Metrics Computation — calculates 252-day CAGR, Sharpe, Sortino, Alpha, Beta, Max Drawdown, VaR/CVaR, Scorecard
  3. Notebook Execution — executes performance & advanced analytics notebooks
  4. Dashboard Generation — generates 4-page PNG dashboard and combined Dashboard.pdf
  5. Fund Recommendations — tests risk-based fund recommendation CLI

Usage:
    python run_pipeline.py
"""

import sys
import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def run_step(description, cmd_args):
    """Execute a single pipeline step via subprocess and report result."""
    print(f"\n[STEP] {description}")
    result = subprocess.run(cmd_args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [WARN/ERROR] {description}:")
        if result.stdout:
            print(result.stdout[-800:])
        if result.stderr:
            print(result.stderr[-800:])
    else:
        print(f"  [OK] {description} completed.")


def main():
    print("=" * 65)
    print("  BLUESTOCK MUTUAL FUND ANALYTICS — MASTER PIPELINE")
    print("=" * 65)

    # Step 1: Data Ingestion (ETL)
    etl_script = BASE_DIR / "scripts" / "etl_pipeline.py"
    if etl_script.exists():
        run_step("Data Ingestion (ETL) — Loading raw data into SQLite DB", [sys.executable, str(etl_script)])

    # Step 2: Compute Metrics & Risk Analytics
    metrics_script = BASE_DIR / "scripts" / "compute_metrics.py"
    if metrics_script.exists():
        run_step("Metrics & Risk Modeling — Computing CAGR, Sharpe, Alpha, Beta, VaR, Scorecard", [sys.executable, str(metrics_script)])

    # Step 3: Recommender Engine Verification
    rec_script = BASE_DIR / "scripts" / "recommender.py"
    if rec_script.exists():
        run_step("Recommender Engine — Testing Risk Recommendations (High)", [sys.executable, str(rec_script), "--risk", "High"])

    # Step 4: Dashboard Generation
    dashboard_script = BASE_DIR / "generate_dashboard.py"
    if dashboard_script.exists():
        run_step("Dashboard Generation — 4-page PNG + Dashboard.pdf", [sys.executable, str(dashboard_script)])

    print("\n" + "=" * 65)
    print("  PIPELINE EXECUTION COMPLETE")
    print("=" * 65)
    print("\nDeliverables Status Verification:")
    
    deliverables = [
        ("scripts/etl_pipeline.py", "ETL Pipeline Script (D1)"),
        ("sql/schema.sql", "Database Schema DDL (D2)"),
        ("sql/queries.sql", "SQL Analytical Queries (D2)"),
        ("notebooks/01_data_ingestion.ipynb", "Data Ingestion Notebook (D3/D4)"),
        ("notebooks/02_data_cleaning.ipynb", "Data Cleaning Notebook (D3/D4)"),
        ("notebooks/03_eda_analysis.ipynb", "EDA Analysis Notebook (D3)"),
        ("notebooks/04_performance_analytics.ipynb", "Performance Analytics Notebook (D4)"),
        ("notebooks/05_advanced_analytics.ipynb", "Advanced Analytics Notebook (D6)"),
        ("dashboard/Dashboard.pdf", "Interactive Dashboard PDF (D5)"),
        ("reports/Final_Report.pdf", "Final Capstone Report (D7)"),
        ("reports/Presentation.pptx", "Presentation Slides (D7)"),
        ("scripts/live_nav_fetch.py", "Live NAV Fetcher (Bonus B1)"),
        ("scripts/compute_metrics.py", "Metrics Engine (Bonus/Core)"),
        ("scripts/recommender.py", "Fund Recommender CLI (Core/Bonus)"),
        ("README.md", "Project Documentation")
    ]
    
    for rel_path, desc in deliverables:
        target = BASE_DIR / rel_path
        status = "[OK]     " if target.exists() else "[MISSING]"
        print(f"  {status}  {rel_path:<40} ({desc})")


if __name__ == "__main__":
    main()
