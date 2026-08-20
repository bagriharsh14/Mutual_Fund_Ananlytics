"""
etl_pipeline.py - Automated End-to-End ETL Pipeline for Mutual Fund Analytics

Loads raw CSV files from data/raw/, performs data validation and type enforcement,
handles missing dates/weekends via forward-fill (ffill), creates the SQLite star-schema,
and populates the database tables with error handling and logging.

Usage:
    python scripts/etl_pipeline.py
"""

import os
import glob
import sqlite3
import logging
from pathlib import Path
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_DIR = BASE_DIR / "data" / "db"
DB_PATH = DB_DIR / "bluestock_mf.db"
ROOT_DB_PATH = BASE_DIR / "bluestock_mf.db"
SQL_SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def init_database(db_path: Path, schema_path: Path):
    """Initialize SQLite database using schema.sql DDL."""
    logging.info(f"Initializing database at: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        cursor.executescript(schema_sql)
        logging.info("Schema applied successfully.")
    else:
        logging.warning(f"Schema file not found at {schema_path}, creating tables dynamically if needed.")
    
    conn.commit()
    conn.close()


def process_and_load_data(db_path: Path):
    """Load, clean, and populate all fact and dimension tables into SQLite."""
    conn = sqlite3.connect(str(db_path))
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Starting Data Ingestion & Transformation...")

    # 1. Dimension Fund
    fund_master_path = DATA_RAW_DIR / "01_fund_master.csv"
    if fund_master_path.exists():
        df_fund = pd.read_csv(fund_master_path)
        # Standardize column names
        df_fund = df_fund.rename(columns={"scheme_code": "amfi_code"})
        df_fund["amfi_code"] = df_fund["amfi_code"].astype(str)
        df_fund.to_sql("dim_fund", conn, if_exists="replace", index=False)
        df_fund.to_csv(DATA_PROCESSED_DIR / "clean_fund_master.csv", index=False)
        logging.info(f"Loaded dim_fund: {len(df_fund)} records.")

    # 2. Fact NAV with Date Reindexing & ffill for weekends/holidays
    nav_path = DATA_RAW_DIR / "02_nav_history.csv"
    if nav_path.exists():
        df_nav = pd.read_csv(nav_path)
        df_nav = df_nav.rename(columns={"scheme_code": "amfi_code"})
        df_nav["amfi_code"] = df_nav["amfi_code"].astype(str)
        df_nav["date"] = pd.to_datetime(df_nav["date"])
        
        # Handle weekends/holidays: per-scheme reindex with full date range & ffill
        nav_cleaned_list = []
        for amfi, group in df_nav.groupby("amfi_code"):
            group = group.sort_values("date").drop_duplicates(subset=["date"])
            full_idx = pd.date_range(start=group["date"].min(), end=group["date"].max(), freq="D")
            group_reindexed = group.set_index("date").reindex(full_idx)
            group_reindexed["amfi_code"] = amfi
            group_reindexed["nav"] = group_reindexed["nav"].ffill().bfill()
            group_reindexed = group_reindexed.reset_index().rename(columns={"index": "date"})
            nav_cleaned_list.append(group_reindexed)
        
        df_nav_clean = pd.concat(nav_cleaned_list, ignore_index=True)
        df_nav_clean["date"] = df_nav_clean["date"].dt.strftime("%Y-%m-%d")
        
        # Create dim_date
        all_dates = pd.to_datetime(df_nav_clean["date"].unique())
        df_date = pd.DataFrame({
            "date": all_dates.strftime("%Y-%m-%d"),
            "year": all_dates.year,
            "month": all_dates.month,
            "day": all_dates.day,
            "quarter": all_dates.quarter,
            "day_name": all_dates.day_name(),
            "month_name": all_dates.month_name(),
            "is_weekend": (all_dates.dayofweek >= 5).astype(int)
        })
        df_date.to_sql("dim_date", conn, if_exists="replace", index=False)
        
        df_nav_clean.to_sql("fact_nav", conn, if_exists="replace", index=False)
        df_nav_clean.to_csv(DATA_PROCESSED_DIR / "clean_nav.csv", index=False)
        logging.info(f"Loaded fact_nav: {len(df_nav_clean)} records across {df_nav_clean['amfi_code'].nunique()} schemes.")

    # 3. Fact AUM by Fund House
    aum_path = DATA_RAW_DIR / "03_aum_by_fund_house.csv"
    if aum_path.exists():
        df_aum = pd.read_csv(aum_path)
        df_aum.to_sql("fact_aum", conn, if_exists="replace", index=False)
        df_aum.to_csv(DATA_PROCESSED_DIR / "clean_aum.csv", index=False)
        logging.info(f"Loaded fact_aum: {len(df_aum)} records.")

    # 4. Fact Monthly SIP
    sip_path = DATA_RAW_DIR / "04_monthly_sip_inflows.csv"
    if sip_path.exists():
        df_sip = pd.read_csv(sip_path)
        df_sip.to_sql("fact_monthly_sip", conn, if_exists="replace", index=False)
        df_sip.to_csv(DATA_PROCESSED_DIR / "clean_sip.csv", index=False)
        logging.info(f"Loaded fact_monthly_sip: {len(df_sip)} records.")

    # 5. Fact Category Inflows
    cat_inflow_path = DATA_RAW_DIR / "05_category_inflows.csv"
    if cat_inflow_path.exists():
        df_cat = pd.read_csv(cat_inflow_path)
        df_cat.to_sql("fact_category_inflows", conn, if_exists="replace", index=False)
        df_cat.to_csv(DATA_PROCESSED_DIR / "clean_category_inflows.csv", index=False)
        logging.info(f"Loaded fact_category_inflows: {len(df_cat)} records.")

    # 6. Fact Industry Folio Count
    folio_path = DATA_RAW_DIR / "06_industry_folio_count.csv"
    if folio_path.exists():
        df_folio = pd.read_csv(folio_path)
        df_folio.to_sql("fact_industry_folio", conn, if_exists="replace", index=False)
        df_folio.to_csv(DATA_PROCESSED_DIR / "clean_folio_count.csv", index=False)
        logging.info(f"Loaded fact_industry_folio: {len(df_folio)} records.")

    # 7. Fact Scheme Performance
    perf_path = DATA_RAW_DIR / "07_scheme_performance.csv"
    if perf_path.exists():
        df_perf = pd.read_csv(perf_path)
        df_perf = df_perf.rename(columns={"scheme_code": "amfi_code"})
        df_perf["amfi_code"] = df_perf["amfi_code"].astype(str)
        df_perf.to_sql("fact_performance", conn, if_exists="replace", index=False)
        df_perf.to_csv(DATA_PROCESSED_DIR / "clean_performance.csv", index=False)
        logging.info(f"Loaded fact_performance: {len(df_perf)} records.")

    # 8. Fact Transactions
    tx_path = DATA_RAW_DIR / "08_investor_transactions.csv"
    if tx_path.exists():
        df_tx = pd.read_csv(tx_path)
        df_tx = df_tx.rename(columns={"scheme_code": "amfi_code"})
        df_tx["amfi_code"] = df_tx["amfi_code"].astype(str)
        df_tx.to_sql("fact_transactions", conn, if_exists="replace", index=False)
        df_tx.to_csv(DATA_PROCESSED_DIR / "clean_transactions.csv", index=False)
        logging.info(f"Loaded fact_transactions: {len(df_tx)} records.")

    # 9. Fact Portfolio Holdings
    holdings_path = DATA_RAW_DIR / "09_portfolio_holdings.csv"
    if holdings_path.exists():
        df_hold = pd.read_csv(holdings_path)
        df_hold = df_hold.rename(columns={"scheme_code": "amfi_code"})
        df_hold["amfi_code"] = df_hold["amfi_code"].astype(str)
        df_hold.to_sql("fact_portfolio_holdings", conn, if_exists="replace", index=False)
        df_hold.to_csv(DATA_PROCESSED_DIR / "clean_portfolio_holdings.csv", index=False)
        logging.info(f"Loaded fact_portfolio_holdings: {len(df_hold)} records.")

    # 10. Fact Benchmark Indices
    bm_path = DATA_RAW_DIR / "10_benchmark_indices.csv"
    if bm_path.exists():
        df_bm = pd.read_csv(bm_path)
        df_bm.to_sql("fact_benchmark_indices", conn, if_exists="replace", index=False)
        df_bm.to_csv(DATA_PROCESSED_DIR / "clean_benchmark_indices.csv", index=False)
        logging.info(f"Loaded fact_benchmark_indices: {len(df_bm)} records.")

    conn.commit()
    conn.close()
    logging.info("ETL Ingestion & Database Population Completed Successfully.")


def main():
    logging.info("=" * 60)
    logging.info("BLUESTOCK MUTUAL FUND ANALYTICS - ETL PIPELINE")
    logging.info("=" * 60)
    
    init_database(DB_PATH, SQL_SCHEMA_PATH)
    process_and_load_data(DB_PATH)
    
    # Also ensure root db sync for local scripts if needed
    import shutil
    shutil.copy2(str(DB_PATH), str(ROOT_DB_PATH))
    logging.info(f"Synchronized local database copies at {DB_PATH} and {ROOT_DB_PATH}.")


if __name__ == "__main__":
    main()
