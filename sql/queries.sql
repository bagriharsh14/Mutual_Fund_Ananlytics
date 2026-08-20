-- Day 2: Mutual Fund Analytics SQL Queries with Results

-- ==========================================
-- Query 1: Top 5 Funds by AUM
-- ==========================================
SELECT 
    amfi_code,
    scheme_name,
    fund_house,
    category,
    aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- Execution Results:
-- amfi_code                                           scheme_name        fund_house        category  aum_crore
--    148568 Mirae Asset Emerging Bluechip Fund - Regular - Growth    Mirae Asset MF Large & Mid Cap    49046.0
--    120842         Kotak Emerging Equity Fund - Regular - Growth Kotak Mahindra MF         Mid Cap    47469.0
--    118634        Nippon India Small Cap Fund - Regular - Growth   Nippon India MF       Small Cap    43630.0
--    149322            DSP Top 100 Equity Fund - Regular - Growth   DSP Mutual Fund       Large Cap    41828.0
--    102886                   UTI Mid Cap Fund - Regular - Growth   UTI Mutual Fund         Mid Cap    41728.0



-- ==========================================
-- Query 2: Average NAV per Month across Schemes
-- ==========================================
SELECT 
    d.year,
    d.month,
    d.month_name,
    ROUND(AVG(n.nav), 4) AS avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date = d.date
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month
LIMIT 12;

-- Execution Results:
--  year  month month_name  avg_nav
--  2022      1    January 207.0614
--  2022      2   February 207.7178
--  2022      3      March 209.6926
--  2022      4      April 211.8335
--  2022      5        May 212.7315
--  2022      6       June 213.8609
--  2022      7       July 213.9561
--  2022      8     August 215.6840
--  2022      9  September 218.4943
--  2022     10    October 219.5296
--  2022     11   November 223.4707
--  2022     12   December 226.7606



-- ==========================================
-- Query 3: SIP Inflow YoY Growth Analysis
-- ==========================================
SELECT 
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    yoy_growth_pct
FROM fact_monthly_sip
WHERE yoy_growth_pct IS NOT NULL
ORDER BY month;

-- Execution Results:
--   month  sip_inflow_crore  active_sip_accounts_crore  yoy_growth_pct
-- 2023-01           13856.0                       6.13           20.31
-- 2023-02           13687.0                       6.19           19.66
-- 2023-03           14276.0                       6.32           15.80
-- 2023-04           14749.0                       6.41           24.33
-- 2023-05           14749.0                       6.50           20.05
-- 2023-06           14734.0                       6.55           20.02
-- 2023-07           15245.0                       6.65           25.58
-- 2023-08           15814.0                       6.73           24.58
-- 2023-09           16042.0                       6.82           23.63
-- 2023-10           16928.0                       6.91           29.82
-- 2023-11           17073.0                       7.00           28.31
-- 2023-12           17610.0                       7.10           29.74
-- 2024-01           18838.0                       7.20           35.96
-- 2024-02           19187.0                       7.30           40.18
-- 2024-03           20371.0                       7.40           42.69
-- 2024-04           20371.0                       7.60           38.12
-- 2024-05           21262.0                       7.78           44.16
-- 2024-06           21262.0                       7.90           44.31
-- 2024-07           23332.0                       8.00           53.05
-- 2024-08           23547.0                       8.11           48.90
-- 2024-09           24509.0                       8.22           52.78
-- 2024-10           25323.0                       8.30           49.59
-- 2024-11           25320.0                       8.40           48.30
-- 2024-12           26459.0                       8.50           50.25
-- 2025-01           26400.0                       8.22           40.14
-- 2025-02           25999.0                       8.30           35.50
-- 2025-03           25926.0                       8.11           27.27
-- 2025-04           26632.0                       8.38           30.73
-- 2025-05           26688.0                       8.50           25.52
-- 2025-06           27274.0                       8.62           28.28
-- 2025-07           28464.0                       8.75           22.00
-- 2025-08           28265.0                       8.85           20.04
-- 2025-09           29361.0                       9.00           19.80
-- 2025-10           29529.0                       9.10           16.61
-- 2025-11           30200.0                       9.20           19.27
-- 2025-12           31002.0                       9.35           17.17



-- ==========================================
-- Query 4: Transactions and Total Amount by State
-- ==========================================
SELECT 
    state,
    COUNT(transaction_id) AS total_transactions,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS avg_transaction_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC
LIMIT 10;

-- Execution Results:
--          state  total_transactions  total_amount_inr  avg_transaction_amount
--         Punjab                2965       315780459.0               106502.68
--     Tamil Nadu                2806       315177237.0               112322.61
-- Madhya Pradesh                2931       308312493.0               105190.21
--      Rajasthan                2577       298645822.0               115888.95
--        Gujarat                2780       298358940.0               107323.36
--    West Bengal                2748       297182514.0               108145.02
--      Telangana                2718       290219284.0               106776.78
--          Delhi                2677       289633404.0               108193.28
--  Uttar Pradesh                2695       285368873.0               105888.26
--        Haryana                2736       279634354.0               102205.54



-- ==========================================
-- Query 5: Funds with Expense Ratio < 1.0%
-- ==========================================
SELECT 
    amfi_code,
    scheme_name,
    fund_house,
    category,
    expense_ratio_pct,
    return_3yr_pct
FROM fact_performance
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- Execution Results:
-- amfi_code                                          scheme_name               fund_house       category  expense_ratio_pct  return_3yr_pct
--    118636 Nippon India Gilt Securities Fund - Regular - Growth          Nippon India MF           Gilt               0.55            5.31
--    100025         HDFC Short Term Debt Fund - Regular - Growth         HDFC Mutual Fund Short Duration               0.56            7.37
--    120844                 Kotak Liquid Fund - Regular - Growth        Kotak Mahindra MF         Liquid               0.60            6.18
--    119552             SBI Bluechip Fund - Direct Plan - Growth          SBI Mutual Fund      Large Cap               0.66           11.30
--    119599            SBI Small Cap Fund - Direct Plan - Growth          SBI Mutual Fund      Small Cap               0.72           23.14
--    118633        Nippon India Large Cap Fund - Direct - Growth          Nippon India MF      Large Cap               0.72           12.33
--    120507             ICICI Pru Liquid Fund - Regular - Growth      ICICI Prudential MF         Liquid               0.74            7.68
--    119093                 Axis Bluechip Fund - Direct - Growth         Axis Mutual Fund      Large Cap               0.75           12.14
--    119120         SBI Magnum Gilt Fund - Regular Plan - Growth          SBI Mutual Fund           Gilt               0.77            6.07
--    125498    HDFC Mid-Cap Opportunities Fund - Direct - Growth         HDFC Mutual Fund        Mid Cap               0.78           15.29
--    101208                  ABSL Liquid Fund - Regular - Growth Aditya Birla Sun Life MF         Liquid               0.79            5.14
--    120504            ICICI Pru Bluechip Fund - Direct - Growth      ICICI Prudential MF      Large Cap               0.80           14.41
--    118635                       Nippon India ETF Nifty 50 BeES          Nippon India MF      Index/ETF               0.89           11.77
--    125497             HDFC Top 100 Fund - Direct Plan - Growth         HDFC Mutual Fund      Large Cap               0.92           13.38



-- ==========================================
-- Query 6: Top 5 Funds by 3-Year Return
-- ==========================================
SELECT 
    amfi_code,
    scheme_name,
    fund_house,
    category,
    return_3yr_pct,
    benchmark_3yr_pct,
    alpha
FROM fact_performance
ORDER BY return_3yr_pct DESC
LIMIT 5;

-- Execution Results:
-- amfi_code                                    scheme_name               fund_house  category  return_3yr_pct  benchmark_3yr_pct  alpha
--    119598     SBI Small Cap Fund - Regular Plan - Growth          SBI Mutual Fund Small Cap           23.39              22.16   1.23
--    119599      SBI Small Cap Fund - Direct Plan - Growth          SBI Mutual Fund Small Cap           23.14              22.01   1.13
--    101207         ABSL Small Cap Fund - Regular - Growth Aditya Birla Sun Life MF Small Cap           22.38              20.54   1.84
--    119095         Axis Small Cap Fund - Regular - Growth         Axis Mutual Fund Small Cap           20.98              20.47   0.51
--    118634 Nippon India Small Cap Fund - Regular - Growth          Nippon India MF Small Cap           20.15              19.35   0.80



-- ==========================================
-- Query 7: Inflow and Volume Distribution by Transaction Type
-- ==========================================
SELECT 
    transaction_type,
    COUNT(transaction_id) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS avg_amount_inr
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount_inr DESC;

-- Execution Results:
-- transaction_type  transaction_count  total_amount_inr  avg_amount_inr
--          Lumpsum               8095      2059821448.0       254456.02
--       Redemption               4967      1244525491.0       250558.79
--              SIP              19716       217233491.0        11018.13



-- ==========================================
-- Query 8: Transaction Breakdown by KYC Status & Gender
-- ==========================================
SELECT 
    kyc_status,
    gender,
    COUNT(transaction_id) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_investment_inr
FROM fact_transactions
GROUP BY kyc_status, gender
ORDER BY kyc_status, total_investment_inr DESC;

-- Execution Results:
-- kyc_status gender  transaction_count  total_investment_inr
--    Pending   Male               1754           194235164.0
--    Pending Female                878            93172885.0
--   Verified   Male              20055          2150998565.0
--   Verified Female              10091          1083173816.0



-- ==========================================
-- Query 9: Monthly Performance of NIFTY50 Index
-- ==========================================
SELECT 
    d.year,
    d.month,
    d.month_name,
    b.index_name,
    ROUND(AVG(b.close_value), 2) AS avg_close_value,
    ROUND(MIN(b.close_value), 2) AS min_close_value,
    ROUND(MAX(b.close_value), 2) AS max_close_value
FROM fact_benchmark_indices b
JOIN dim_date d ON b.date = d.date
WHERE b.index_name = 'NIFTY50'
GROUP BY d.year, d.month, d.month_name, b.index_name
ORDER BY d.year, d.month
LIMIT 12;

-- Execution Results:
--  year  month month_name index_name  avg_close_value  min_close_value  max_close_value
--  2022      1    January    NIFTY50         18167.48         17492.79         18734.13
--  2022      2   February    NIFTY50         18802.85         18347.28         19151.71
--  2022      3      March    NIFTY50         19088.48         18700.26         19775.28
--  2022      4      April    NIFTY50         20186.59         19613.80         20612.20
--  2022      5        May    NIFTY50         19530.99         18816.95         20084.37
--  2022      6       June    NIFTY50         19403.89         18902.99         19798.47
--  2022      7       July    NIFTY50         19346.65         18684.56         19929.86
--  2022      8     August    NIFTY50         19683.22         19378.13         20209.61
--  2022      9  September    NIFTY50         20614.03         20398.27         20896.86
--  2022     10    October    NIFTY50         20703.76         19964.19         21464.58
--  2022     11   November    NIFTY50         21441.90         20659.57         21872.29
--  2022     12   December    NIFTY50         21959.28         21696.78         22446.34



-- ==========================================
-- Query 10: Top 5 Sectors by Total Weight in Portfolio Holdings
-- ==========================================
SELECT 
    sector,
    COUNT(holding_id) AS total_stock_holdings,
    ROUND(SUM(weight_pct), 2) AS total_portfolio_weight_pct,
    ROUND(SUM(market_value_cr), 2) AS total_market_value_cr
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY total_portfolio_weight_pct DESC
LIMIT 5;

-- Execution Results:
--     sector  total_stock_holdings  total_portfolio_weight_pct  total_market_value_cr
--    Banking                    60                      652.26               62840.29
--         IT                    40                      455.47               38477.11
--     Pharma                    38                      407.45               34606.10
-- Automobile                    33                      323.65               34296.97
--  Utilities                    24                      265.54               25108.63


