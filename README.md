# Bluestock Mutual Fund Analytics Capstone Project

A comprehensive end-to-end quantitative analytics project for the Indian Mutual Fund industry, covering 40 AMFI-registered schemes across 10 AMCs with an automated ETL pipeline, risk modeling, fund scorecard ranking, investor behavior analytics, interactive visual dashboards, and professional reports.

---

## 📁 Repository Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/                           # Original raw CSV datasets (01 to 10)
│   ├── processed/                     # Cleaned, validated, and normalized CSVs
│   └── db/                            # bluestock_mf.db (SQLite database - generated via ETL)
├── notebooks/
│   ├── 01_data_ingestion.ipynb        # Ingestion pipeline walkthrough & verification
│   ├── 02_data_cleaning.ipynb         # Data cleaning, weekend/holiday ffill, validation
│   ├── 03_eda_analysis.ipynb          # Exploratory Data Analysis & industry insights
│   ├── 04_performance_analytics.ipynb # CAGR (252 days), Sharpe, Sortino, Alpha, Beta, Scorecard
│   └── 05_advanced_analytics.ipynb    # VaR/CVaR, Rolling Sharpe, Cohort, Churn, Monte Carlo
├── scripts/
│   ├── etl_pipeline.py                # Automated end-to-end ETL script
│   ├── live_nav_fetch.py              # Live NAV fetcher from mfapi.in & cron scheduler
│   ├── compute_metrics.py             # Quantitative performance & risk metrics engine
│   └── recommender.py                 # Risk-based fund recommendation CLI tool
├── sql/
│   ├── schema.sql                     # SQLite star-schema DDL with constraints & types
│   └── queries.sql                    # 10 business-critical analytical SQL queries with results
├── dashboard/
│   ├── Page1_Industry_Overview.png    # Dashboard Page 1 (PNG)
│   ├── Page2_Fund_Performance.png     # Dashboard Page 2 (PNG)
│   ├── Page3_Investor_Analytics.png   # Dashboard Page 3 (PNG)
│   ├── Page4_SIP_Market_Trends.png    # Dashboard Page 4 (PNG)
│   └── Dashboard.pdf                  # Combined 4-page visual dashboard PDF
├── reports/
│   ├── Final_Report.pdf               # Comprehensive 15-page final report
│   ├── Presentation.pptx              # 12-slide executive presentation
│   └── charts/                        # High-resolution analytical charts
├── generate_dashboard.py              # 4-page dashboard generation script
├── run_pipeline.py                    # Master orchestrator running end-to-end pipeline
├── requirements.txt                   # Project dependencies
├── .gitignore                         # Strict exclusion for .db, cache, and OS files
└── README.md                          # Project documentation
```

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- `pip` package manager

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

### Run Full End-to-End Pipeline (One Command)
```bash
python run_pipeline.py
```

### Run Individual Components

```bash
# 1. Execute ETL and populate SQLite database
python scripts/etl_pipeline.py

# 2. Compute Performance Metrics & Risk Statistics
python scripts/compute_metrics.py

# 3. Run Fund Recommender CLI
python scripts/recommender.py --risk High
python scripts/recommender.py --risk Moderate
python scripts/recommender.py --risk Low

# 4. Fetch Live NAV data from mfapi.in
python scripts/live_nav_fetch.py

# 5. Generate 4-Page Dashboard PNGs and Dashboard.pdf
python generate_dashboard.py
```

---

## 📊 Dataset Schema Overview

| Table Name | Entity Description | Key Columns |
|---|---|---|
| `dim_fund` | Scheme Master (40 schemes) | `amfi_code`, `fund_house`, `category`, `sub_category`, `expense_ratio_pct`, `risk_category` |
| `dim_date` | Date Dimension | `date`, `year`, `month`, `quarter`, `is_weekend` |
| `fact_nav` | Daily NAV History (2022–2026) | `amfi_code`, `date`, `nav` |
| `fact_performance` | Pre-computed Performance Metrics | `amfi_code`, `return_3yr_pct`, `sharpe_ratio`, `alpha`, `beta`, `max_drawdown_pct`, `aum_crore` |
| `fact_aum` | AMC-level Quarterly AUM | `date`, `fund_house`, `aum_lakh_crore`, `aum_crore`, `num_schemes` |
| `fact_monthly_sip` | Monthly SIP Inflows | `month`, `sip_inflow_crore`, `active_sip_accounts_crore`, `yoy_growth_pct` |
| `fact_industry_folio` | Monthly Folio Distribution | `month`, `total_folios_crore`, `equity_folios_crore`, `debt_folios_crore` |
| `fact_transactions` | Investor Transactions | `transaction_id`, `investor_id`, `transaction_date`, `amfi_code`, `amount_inr`, `state`, `kyc_status` |
| `fact_portfolio_holdings` | Stock & Sector Holdings | `holding_id`, `amfi_code`, `stock_name`, `sector`, `weight_pct`, `market_value_cr` |
| `fact_benchmark_indices` | NIFTY 50 & NIFTY 100 Index Levels | `date`, `index_name`, `close_value` |
| `fact_category_inflows` | Monthly Category Inflows | `month`, `category`, `net_inflow_crore` |

---

## 🏆 Common Mistakes Avoidance Checklist

- [x] **No hard-coded paths**: Dynamic path resolution using `pathlib.Path` across all modules.
- [x] **Weekend/holiday NAV handling**: Continuous date reindexing and forward-filling (`ffill()`).
- [x] **252-day CAGR annualization**: Formula `(NAV_end / NAV_start) ** (252 / n_trading_days) - 1`.
- [x] **Dashboard with slicers**: Every dashboard page includes multi-select interactive filter controls.
- [x] **Clear unit naming**: Explicit column units (`aum_lakh_crore`, `aum_crore`, `sip_inflow_crore`).
- [x] **No `.db` committed to GitHub**: `*.db` added to `.gitignore`, `sql/schema.sql` and `sql/queries.sql` shared for reproducibility.

