# Bluestock Mutual Fund Analytics

A comprehensive end-to-end quantitative analytics project for the Indian Mutual Fund industry, covering 40 AMFI-registered schemes with ETL pipeline, risk modeling, fund scorecard, investor behavior analysis, visual dashboards, and professional reports.

---

## Project Overview

This capstone project delivers:
- Automated SQLite ETL pipeline importing 10 raw datasets (NAV, AUM, SIP, Folios, Transactions, Holdings, Benchmarks)
- Quantitative performance metrics: CAGR (1yr/3yr/5yr), Sharpe Ratio, Sortino Ratio, Alpha, Beta, Maximum Drawdown
- Advanced risk modeling: Historical VaR (95%), CVaR (95%), Rolling 90-Day Sharpe, Sector HHI
- Composite 0-100 Fund Scorecard across all 40 schemes
- 4-page interactive visual dashboard (PNG + PDF)
- Investor cohort analysis and SIP continuity/at-risk modeling
- Fund recommender CLI tool by risk appetite (Low / Moderate / High)
- 15-page final PDF report and 12-slide PowerPoint presentation

---

## Project Structure

```
Mutual_fund/
|-- Data/
|   |-- Raw/                   # Original raw CSV files
|   |-- Processed/             # Cleaned & validated CSVs
|-- Dashboard/                 # 4-page dashboard PNGs and combined PDF
|-- Reports/                   # Final_Report.pdf, Presentation.pptx
|-- notebooks/                 # Jupyter notebook copies
|-- bluestock_mf.db            # SQLite star-schema warehouse
|-- data_ingestion.py          # ETL ingestion module
|-- live_nav_fetch.py          # Live NAV API fetcher
|-- generate_dashboard.py      # 4-page dashboard generator
|-- recommender.py             # Fund recommender CLI
|-- run_pipeline.py            # Master execution orchestrator
|-- Performance_Analytics.ipynb
|-- Advanced_Analytics.ipynb
|-- fund_scorecard.csv
|-- alpha_beta.csv
|-- var_cvar_report.csv
|-- benchmark_comparison_chart.png
|-- rolling_sharpe_chart.png
|-- Final_Report.pdf
|-- Bluestock_MF_Presentation.pptx
|-- README.md
```

---

## Setup Instructions

### 1. Prerequisites

- Python 3.10 or later
- pip package manager

### 2. Install Dependencies

```bash
pip install pandas numpy matplotlib scipy reportlab pymupdf python-pptx nbformat nbconvert requests
```

### 3. Verify Installation

```bash
python -c "import pandas, numpy, matplotlib, scipy, reportlab, pptx, nbformat; print('All packages installed.')"
```

---

## How to Run the ETL Pipeline

### Option A: Run Full Pipeline (Recommended)

```bash
python run_pipeline.py
```

This executes all stages in sequence:
1. Data ingestion into `bluestock_mf.db`
2. Performance analytics notebook execution
3. Advanced analytics notebook execution
4. Dashboard generation (4-page PNG + PDF)
5. Final PDF report generation
6. PowerPoint presentation generation

### Option B: Run Individual Stages

```bash
# Data ingestion only
python data_ingestion.py

# Dashboard generation only
python generate_dashboard.py

# Fund recommender
python recommender.py --risk High
python recommender.py --risk Moderate
python recommender.py --risk Low
```

---

## How to Open the Dashboard

The 4-page visual dashboard is available in two formats:

### PNG Screenshots
```
Dashboard/Page1_Industry_Overview.png
Dashboard/Page2_Fund_Performance.png
Dashboard/Page3_Investor_Analytics.png
Dashboard/Page4_SIP_Market_Trends.png
```

### Combined PDF
```
Dashboard/Dashboard.pdf
```

Open with any standard PDF reader (Adobe Acrobat, browser, etc.).

---

## Dataset Descriptions

| Table | Description | Key Columns |
|---|---|---|
| dim_fund | Scheme master: 40 AMFI schemes | amfi_code, fund_house, category, expense_ratio_pct |
| fact_nav | Daily NAV history (2022–2026) | amfi_code, date, nav |
| fact_performance | Pre-computed risk metrics | amfi_code, cagr_3yr_pct, sharpe_ratio, alpha, beta, max_drawdown_pct |
| fact_aum | Quarterly AUM per AMC | date, fund_house, aum_lakh_crore |
| fact_monthly_sip | Monthly SIP inflows | month, sip_inflow_crore, active_sip_accounts_crore |
| fact_industry_folio | Monthly folio counts | month, total_folios_crore, equity_folios_crore |
| fact_transactions | Investor transaction records | investor_id, transaction_date, amfi_code, transaction_type, amount_inr |
| fact_benchmark_indices | NIFTY 50 & NIFTY 100 daily close | date, index_name, close_value |
| fact_category_inflows | Monthly net inflow by fund category | month, category, net_inflow_crore |
| fact_portfolio_holdings | Stock-level sector holdings | amfi_code, stock_name, sector, weight_pct |

---

