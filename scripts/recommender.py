"""
recommender.py - Mutual Fund Recommendation Engine

Recommends Top 3 mutual funds based on Sharpe ratio & composite scorecard
within the user's selected risk appetite (Low, Moderate, High).

Usage:
    python scripts/recommender.py --risk High
    python scripts/recommender.py --risk Moderate
    python scripts/recommender.py --risk Low
"""

import sys
import argparse
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"
if not DB_PATH.exists():
    DB_PATH = BASE_DIR / "bluestock_mf.db"


def recommend_funds(risk_appetite: str):
    risk_appetite = risk_appetite.strip().capitalize()
    
    conn = sqlite3.connect(str(DB_PATH))
    df_fund = pd.read_sql("SELECT * FROM dim_fund", conn)
    df_nav = pd.read_sql("SELECT * FROM fact_nav", conn)
    conn.close()
    
    df_nav["date"] = pd.to_datetime(df_nav["date"])
    df_nav = df_nav.sort_values(["amfi_code", "date"])
    df_nav["daily_return"] = df_nav.groupby("amfi_code")["nav"].pct_change()
    
    rf_annual = 0.065
    metrics = []
    
    for amfi, group in df_nav.groupby("amfi_code"):
        rets = group["daily_return"].dropna()
        if len(rets) < 30:
            continue
        ret_ann = rets.mean() * 252
        vol_ann = rets.std() * np.sqrt(252)
        sharpe = (ret_ann - rf_annual) / vol_ann if vol_ann > 0 else 0
        
        metrics.append({
            "amfi_code": amfi,
            "ret_ann_pct": ret_ann * 100,
            "vol_ann_pct": vol_ann * 100,
            "sharpe_ratio": sharpe
        })
        
    df_metrics = pd.DataFrame(metrics)
    df_merged = df_fund.merge(df_metrics, on="amfi_code")
    
    # Map risk appetite to risk_category
    risk_map = {
        "Low": ["Low", "Moderate"],
        "Moderate": ["Moderate", "High"],
        "High": ["High", "Very High"]
    }
    
    allowed_categories = risk_map.get(risk_appetite, ["Very High", "High", "Moderate"])
    filtered = df_merged[df_merged["risk_category"].isin(allowed_categories)].copy()
    
    if filtered.empty:
        filtered = df_merged.copy()
        
    top3 = filtered.sort_values("sharpe_ratio", ascending=False).head(3)
    
    print("\n" + "=" * 80)
    print(f"  BLUESTOCK MUTUAL FUND RECOMMENDER — Risk Appetite: {risk_appetite.upper()}")
    print("=" * 80)
    
    display_df = top3[["amfi_code", "scheme_name", "sub_category", "risk_category", "sharpe_ratio", "ret_ann_pct", "expense_ratio_pct"]].copy()
    display_df.columns = ["AMFI Code", "Scheme Name", "Category", "Risk Grade", "Sharpe Ratio", "Ann Return %", "Expense %"]
    display_df["Sharpe Ratio"] = display_df["Sharpe Ratio"].round(2)
    display_df["Ann Return %"] = display_df["Ann Return %"].round(2)
    display_df["Expense %"] = display_df["Expense %"].round(2)
    
    print(display_df.to_string(index=False))
    print("=" * 80 + "\n")
    return top3


def main():
    parser = argparse.ArgumentParser(description="Mutual Fund Recommender based on Risk Appetite")
    parser.add_argument("--risk", choices=["Low", "Moderate", "High"], help="Investor Risk Appetite (Low, Moderate, High)")
    args = parser.parse_args()
    
    if args.risk:
        recommend_funds(args.risk)
    else:
        recommend_funds("Moderate")


if __name__ == "__main__":
    main()
