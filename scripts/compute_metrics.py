"""
compute_metrics.py - Quantitative Performance & Risk Analytics Engine

Computes:
- 1yr, 3yr, 5yr CAGR using trading day annualization (252 / n_trading_days)
- Annualized Return & Volatility
- Sharpe Ratio (Rf = 6.5%) & Sortino Ratio
- Alpha & Beta OLS Regression vs NIFTY 100
- Maximum Drawdown (with peak and trough dates)
- 95% Historical Value at Risk (VaR) and Conditional VaR (CVaR)
- Composite 0-100 Fund Scorecard across 40 AMFI schemes

Usage:
    python scripts/compute_metrics.py
"""

import logging
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"
if not DB_PATH.exists():
    DB_PATH = BASE_DIR / "bluestock_mf.db"

PROCESSED_DIR = BASE_DIR / "data" / "processed"


def compute_all_metrics():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    logging.info(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    
    df_fund = pd.read_sql("SELECT * FROM dim_fund", conn)
    df_nav = pd.read_sql("SELECT * FROM fact_nav", conn)
    df_bm = pd.read_sql("SELECT * FROM fact_benchmark_indices", conn)
    conn.close()

    df_nav["date"] = pd.to_datetime(df_nav["date"])
    df_bm["date"] = pd.to_datetime(df_bm["date"])
    df_nav = df_nav.sort_values(["amfi_code", "date"])

    # Prepare Benchmark Return (NIFTY 100)
    n100 = df_bm[df_bm["index_name"] == "NIFTY100"].sort_values("date").copy()
    n100["bm100_return"] = n100["close_value"].pct_change()
    df_n100 = n100[["date", "bm100_return"]].dropna()

    rf_annual = 0.065
    metrics_list = []
    var_list = []

    end_date = df_nav["date"].max()

    for amfi, group in df_nav.groupby("amfi_code"):
        group = group.sort_values("date").copy()
        group["daily_return"] = group["nav"].pct_change()
        
        fund_info = df_fund[df_fund["amfi_code"] == amfi].iloc[0]
        rets = group["daily_return"].dropna()
        
        if len(rets) < 30:
            continue
        
        # 1. Trading-day annualized returns & volatility
        n_trading_days = len(rets)
        ret_ann = rets.mean() * 252
        vol_ann = rets.std() * np.sqrt(252)
        
        # 2. Sharpe Ratio
        sharpe = (ret_ann - rf_annual) / vol_ann if vol_ann > 0 else 0
        
        # 3. Sortino Ratio
        downside_diff = np.minimum(0, rets - (rf_annual / 252))
        downside_vol = np.sqrt(np.mean(downside_diff ** 2)) * np.sqrt(252)
        sortino = (ret_ann - rf_annual) / downside_vol if downside_vol > 0 else 0
        
        # 4. CAGR using 252 trading days annualization
        # 1-Year (last 252 trading days)
        if len(group) >= 252:
            nav_1yr_start = group["nav"].iloc[-252]
            nav_end = group["nav"].iloc[-1]
            cagr_1yr = (nav_end / nav_1yr_start) ** (252 / 252) - 1
        else:
            cagr_1yr = np.nan
            
        # 3-Year (last 756 trading days)
        if len(group) >= 756:
            nav_3yr_start = group["nav"].iloc[-756]
            nav_end = group["nav"].iloc[-1]
            cagr_3yr = (nav_end / nav_3yr_start) ** (252 / 756) - 1
        else:
            cagr_3yr = np.nan
            
        # 5-Year / Total period
        nav_start = group["nav"].iloc[0]
        nav_end = group["nav"].iloc[-1]
        cagr_5yr = (nav_end / nav_start) ** (252 / n_trading_days) - 1 if n_trading_days > 0 else np.nan
        
        # 5. OLS Alpha & Beta vs NIFTY 100
        merged = pd.merge(group[["date", "daily_return"]], df_n100, on="date").dropna()
        if len(merged) > 30:
            slope, intercept, r_val, p_val, std_err = stats.linregress(merged["bm100_return"], merged["daily_return"])
            beta = slope
            alpha_ann = intercept * 252
            r_squared = r_val ** 2
        else:
            beta, alpha_ann, r_squared, p_val = np.nan, np.nan, np.nan, np.nan
            
        # 6. Max Drawdown & Dates
        group["running_max"] = group["nav"].cummax()
        group["drawdown"] = group["nav"] / group["running_max"] - 1
        min_dd = group["drawdown"].min()
        trough_row = group[group["drawdown"] == min_dd].iloc[0]
        trough_date = trough_row["date"]
        peak_date = group[(group["date"] <= trough_date) & (group["nav"] == trough_row["running_max"])]["date"].max()
        
        # 7. Historical VaR & CVaR (95%)
        var_95 = np.percentile(rets, 5)
        cvar_95 = rets[rets <= var_95].mean()
        
        metrics_list.append({
            "amfi_code": amfi,
            "scheme_name": fund_info["scheme_name"],
            "fund_house": fund_info["fund_house"],
            "category": fund_info["category"],
            "sub_category": fund_info["sub_category"],
            "risk_category": fund_info["risk_category"],
            "expense_ratio_pct": fund_info["expense_ratio_pct"],
            "cagr_1yr_pct": cagr_1yr * 100 if pd.notnull(cagr_1yr) else np.nan,
            "cagr_3yr_pct": cagr_3yr * 100 if pd.notnull(cagr_3yr) else np.nan,
            "cagr_5yr_pct": cagr_5yr * 100 if pd.notnull(cagr_5yr) else np.nan,
            "ret_ann_pct": ret_ann * 100,
            "vol_ann_pct": vol_ann * 100,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "alpha_annualized": alpha_ann,
            "alpha_pct": alpha_ann * 100 if pd.notnull(alpha_ann) else np.nan,
            "beta": beta,
            "r_squared": r_squared,
            "p_value": p_val,
            "max_drawdown_pct": min_dd * 100,
            "peak_date": peak_date.strftime("%Y-%m-%d"),
            "trough_date": trough_date.strftime("%Y-%m-%d")
        })
        
        var_list.append({
            "amfi_code": amfi,
            "scheme_name": fund_info["scheme_name"],
            "sub_category": fund_info["sub_category"],
            "var_95_pct": abs(var_95) * 100,
            "cvar_95_pct": abs(cvar_95) * 100
        })

    df_metrics = pd.DataFrame(metrics_list)
    df_var = pd.DataFrame(var_list)

    # 8. Composite Fund Scorecard (0-100)
    N = len(df_metrics)
    df_metrics["score_3yr"] = (df_metrics["cagr_3yr_pct"].rank(ascending=True) - 1) / (N - 1) * 100
    df_metrics["score_sharpe"] = (df_metrics["sharpe_ratio"].rank(ascending=True) - 1) / (N - 1) * 100
    df_metrics["score_alpha"] = (df_metrics["alpha_pct"].rank(ascending=True) - 1) / (N - 1) * 100
    df_metrics["score_expense"] = (df_metrics["expense_ratio_pct"].rank(ascending=False) - 1) / (N - 1) * 100
    df_metrics["score_max_dd"] = (df_metrics["max_drawdown_pct"].rank(ascending=True) - 1) / (N - 1) * 100

    df_metrics["composite_score"] = (
        0.30 * df_metrics["score_3yr"].fillna(df_metrics["score_3yr"].median()) +
        0.25 * df_metrics["score_sharpe"] +
        0.20 * df_metrics["score_alpha"].fillna(df_metrics["score_alpha"].median()) +
        0.15 * df_metrics["score_expense"] +
        0.10 * df_metrics["score_max_dd"]
    ).round(2)

    df_metrics["fund_rank"] = df_metrics["composite_score"].rank(ascending=False, method="min").astype(int)
    df_metrics = df_metrics.sort_values("fund_rank")

    # Export CSV files
    df_metrics.to_csv(PROCESSED_DIR / "fund_scorecard.csv", index=False)
    
    df_ab = df_metrics[["amfi_code", "scheme_name", "category", "sub_category", "alpha_annualized", "alpha_pct", "beta", "r_squared", "p_value"]]
    df_ab.to_csv(PROCESSED_DIR / "alpha_beta.csv", index=False)
    
    df_var.to_csv(PROCESSED_DIR / "var_cvar_report.csv", index=False)

    logging.info("Metrics calculation complete. Generated CSV files in data/processed/.")
    return df_metrics


if __name__ == "__main__":
    compute_all_metrics()
