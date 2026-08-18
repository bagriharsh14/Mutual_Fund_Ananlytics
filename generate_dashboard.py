"""
Bluestock Mutual Fund Dashboard - 4 Page PNG + PDF Generator
Generates publication-quality dashboard pages matching Power BI specifications.
"""
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings('ignore')

# ===============================================================
# GLOBAL CONFIG
# ===============================================================
BRAND_DARK   = '#0A1628'
BRAND_PRIMARY = '#1A73E8'
BRAND_ACCENT  = '#00C9A7'
BRAND_WARN    = '#FF6B6B'
BRAND_ORANGE  = '#FFA726'
BRAND_PURPLE  = '#AB47BC'
BRAND_LIGHT   = '#E8F0FE'
BRAND_CARD_BG = '#112240'
BRAND_TEXT    = '#FFFFFF'
BRAND_SUBTEXT = '#8892B0'
PAGE_W, PAGE_H = 19.2, 10.8  # 1920x1080 at 100dpi

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Segoe UI', 'Arial', 'Helvetica'],
    'font.size': 10,
    'text.color': BRAND_TEXT,
    'axes.labelcolor': BRAND_TEXT,
    'axes.edgecolor': '#233554',
    'xtick.color': BRAND_SUBTEXT,
    'ytick.color': BRAND_SUBTEXT,
    'figure.facecolor': BRAND_DARK,
    'axes.facecolor': BRAND_CARD_BG,
    'savefig.facecolor': BRAND_DARK,
})

# ===============================================================
# DATA LOADING
# ===============================================================
conn = sqlite3.connect('bluestock_mf.db')

df_fund    = pd.read_sql('SELECT * FROM dim_fund', conn)
df_nav     = pd.read_sql('SELECT * FROM fact_nav', conn)
df_perf    = pd.read_sql('SELECT * FROM fact_performance', conn)
df_aum     = pd.read_sql('SELECT * FROM fact_aum', conn)
df_sip     = pd.read_sql('SELECT * FROM fact_monthly_sip', conn)
df_folio   = pd.read_sql('SELECT * FROM fact_industry_folio', conn)
df_txn     = pd.read_sql('SELECT * FROM fact_transactions', conn)
df_cat     = pd.read_sql('SELECT * FROM fact_category_inflows', conn)
df_bm      = pd.read_sql('SELECT * FROM fact_benchmark_indices', conn)
df_score   = pd.read_csv('fund_scorecard.csv')

df_nav['date'] = pd.to_datetime(df_nav['date'])
df_aum['date'] = pd.to_datetime(df_aum['date'])
df_bm['date']  = pd.to_datetime(df_bm['date'])
df_txn['transaction_date'] = pd.to_datetime(df_txn['transaction_date'])

conn.close()

# ===============================================================
# HELPER FUNCTIONS
# ===============================================================
def add_header(fig, title, subtitle=""):
    fig.text(0.02, 0.96, "BLUESTOCK", fontsize=22, fontweight='bold',
             color=BRAND_PRIMARY, va='top', fontfamily='sans-serif')
    fig.text(0.12, 0.96, title, fontsize=18, fontweight='bold',
             color=BRAND_TEXT, va='top')
    if subtitle:
        fig.text(0.12, 0.925, subtitle, fontsize=10, color=BRAND_SUBTEXT, va='top')

def draw_kpi_card(ax, value, label, color=BRAND_PRIMARY, prefix="", suffix=""):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor(BRAND_CARD_BG)
    # Top accent bar
    ax.axhline(y=0.95, xmin=0.1, xmax=0.9, color=color, linewidth=4)
    ax.text(0.5, 0.55, f"{prefix}{value}{suffix}", fontsize=22, fontweight='bold',
            color=BRAND_TEXT, ha='center', va='center')
    ax.text(0.5, 0.2, label, fontsize=9, color=BRAND_SUBTEXT, ha='center', va='center')

def style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_title(title, fontsize=11, fontweight='bold', color=BRAND_TEXT, pad=8)
    ax.set_xlabel(xlabel, fontsize=9, color=BRAND_SUBTEXT)
    ax.set_ylabel(ylabel, fontsize=9, color=BRAND_SUBTEXT)
    ax.grid(True, alpha=0.15, color='#8892B0', linestyle='--')
    for spine in ax.spines.values():
        spine.set_color('#233554')

# ===============================================================
# PAGE 1 - INDUSTRY OVERVIEW
# ===============================================================
print("Generating Page 1 - Industry Overview...")

fig = plt.figure(figsize=(PAGE_W, PAGE_H))
add_header(fig, "Mutual Fund Industry Overview", "India MF Industry - 2022–2025")

gs = gridspec.GridSpec(3, 4, figure=fig, left=0.04, right=0.97, top=0.88, bottom=0.06,
                       hspace=0.45, wspace=0.3)

# KPIs
latest_aum_total = df_aum.sort_values('date').groupby('fund_house')['aum_lakh_crore'].last().sum()
latest_sip = df_sip.sort_values('month').iloc[-1]['sip_inflow_crore']
latest_folio = df_folio.sort_values('month').iloc[-1]['total_folios_crore']
total_schemes = int(df_aum.sort_values('date').groupby('fund_house')['num_schemes'].last().sum())

ax_kpi1 = fig.add_subplot(gs[0, 0])
draw_kpi_card(ax_kpi1, f"Rs.{latest_aum_total:.0f}L Cr", "Total AUM", BRAND_PRIMARY)

ax_kpi2 = fig.add_subplot(gs[0, 1])
draw_kpi_card(ax_kpi2, f"Rs.{latest_sip/1000:.0f}K Cr", "SIP Inflows (Monthly)", BRAND_ACCENT)

ax_kpi3 = fig.add_subplot(gs[0, 2])
draw_kpi_card(ax_kpi3, f"{latest_folio:.2f} Cr", "Total Folios", BRAND_ORANGE)

ax_kpi4 = fig.add_subplot(gs[0, 3])
draw_kpi_card(ax_kpi4, f"{total_schemes:,}", "Total Schemes", BRAND_PURPLE)

# AUM Trend Line Chart
ax_aum_trend = fig.add_subplot(gs[1, :])
aum_trend = df_aum.groupby('date')['aum_lakh_crore'].sum().sort_index()
ax_aum_trend.fill_between(aum_trend.index, aum_trend.values, alpha=0.2, color=BRAND_PRIMARY)
ax_aum_trend.plot(aum_trend.index, aum_trend.values, color=BRAND_PRIMARY, linewidth=2.5)
style_ax(ax_aum_trend, "Industry AUM Trend (2022–2025)", "Date", "AUM (Rs. Lakh Crore)")
ax_aum_trend.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b %Y'))

# AUM by AMC Bar Chart
ax_amc = fig.add_subplot(gs[2, :])
aum_by_amc = df_aum.sort_values('date').groupby('fund_house')['aum_crore'].last().sort_values(ascending=True)
colors_bar = [BRAND_PRIMARY if v == aum_by_amc.max() else BRAND_ACCENT for v in aum_by_amc.values]
ax_amc.barh(range(len(aum_by_amc)), aum_by_amc.values, color=colors_bar, height=0.65, edgecolor='none')
ax_amc.set_yticks(range(len(aum_by_amc)))
short_names = [n.replace(' Mutual Fund', '').replace(' MF', '').replace('Aditya Birla Sun Life', 'ABSL') for n in aum_by_amc.index]
ax_amc.set_yticklabels(short_names, fontsize=8)
style_ax(ax_amc, "AUM by Asset Management Company (Latest Quarter)", "", "AUM (Rs Crore)")

plt.savefig('Dashboard/Page1_Industry_Overview.png', dpi=150, bbox_inches='tight')
plt.close()
print("  [OK] Page 1 saved.")

# ===============================================================
# PAGE 2 - FUND PERFORMANCE
# ===============================================================
print("Generating Page 2 - Fund Performance...")

fig = plt.figure(figsize=(PAGE_W, PAGE_H))
add_header(fig, "Fund Performance Analytics", "Risk vs Return - Scorecard - NAV Comparison")

gs = gridspec.GridSpec(2, 2, figure=fig, left=0.05, right=0.97, top=0.88, bottom=0.06,
                       hspace=0.35, wspace=0.25)

# Scatter: Return (X) vs StdDev (Y), bubble = AUM
ax_scatter = fig.add_subplot(gs[0, 0])
merged_perf = df_perf.merge(df_fund[['amfi_code', 'sub_category']], on='amfi_code', how='left', suffixes=('', '_fund'))

cat_colors = {
    'Large Cap': BRAND_PRIMARY, 'Mid Cap': BRAND_ACCENT, 'Small Cap': BRAND_WARN,
    'Flexi Cap': BRAND_ORANGE, 'Large & Mid Cap': BRAND_PURPLE, 'Value': '#FFD54F',
    'ELSS': '#4DD0E1', 'Index/ETF': '#81C784', 'Index': '#81C784',
    'Liquid': '#B0BEC5', 'Gilt': '#CE93D8', 'Short Duration': '#90A4AE'
}

for cat in merged_perf['sub_category'].unique():
    mask = merged_perf['sub_category'] == cat
    sub = merged_perf[mask]
    color = cat_colors.get(cat, '#888888')
    sizes = sub['aum_crore'].fillna(1000).values / 200
    ax_scatter.scatter(sub['return_3yr_pct'], sub['std_dev_ann_pct'], s=sizes,
                       alpha=0.75, color=color, edgecolors='white', linewidth=0.5, label=cat)

ax_scatter.legend(fontsize=6, loc='upper left', framealpha=0.5, labelcolor=BRAND_TEXT)
style_ax(ax_scatter, "Return vs Risk (3yr CAGR vs Std Dev)", "3yr Return (%)", "Annualized Std Dev (%)")

# Fund Scorecard Table (Top 15)
ax_table = fig.add_subplot(gs[0, 1])
ax_table.axis('off')
top15 = df_score.head(15)[['fund_rank', 'scheme_name', 'sub_category', 'composite_score',
                            'cagr_3yr_pct', 'sharpe_ratio']].copy()
top15.columns = ['Rank', 'Fund Name', 'Category', 'Score', '3yr CAGR%', 'Sharpe']
top15['Fund Name'] = top15['Fund Name'].str[:35]
top15['Score'] = top15['Score'].round(1)
top15['3yr CAGR%'] = top15['3yr CAGR%'].round(1)
top15['Sharpe'] = top15['Sharpe'].round(2)

table = ax_table.table(cellText=top15.values, colLabels=top15.columns,
                        cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(7)
table.scale(1, 1.4)
for key, cell in table.get_celld().items():
    cell.set_edgecolor('#233554')
    if key[0] == 0:
        cell.set_facecolor(BRAND_PRIMARY)
        cell.set_text_props(color='white', fontweight='bold')
    else:
        cell.set_facecolor(BRAND_CARD_BG)
        cell.set_text_props(color=BRAND_TEXT)
ax_table.set_title("Fund Scorecard (Top 15)", fontsize=11, fontweight='bold',
                    color=BRAND_TEXT, pad=8)

# NAV line: Top 3 funds vs Nifty 50
ax_nav = fig.add_subplot(gs[1, :])
top3_codes = df_score.head(3)['amfi_code'].tolist()
date_3yr = df_nav['date'].max() - pd.DateOffset(years=3)

nav_colors = [BRAND_PRIMARY, BRAND_ACCENT, BRAND_ORANGE]
for i, code in enumerate(top3_codes):
    fn = df_nav[(df_nav['amfi_code'] == code) & (df_nav['date'] >= date_3yr)].sort_values('date')
    if len(fn) > 0:
        base = fn['nav'].iloc[0]
        norm = (fn['nav'] / base) * 100
        name = df_fund[df_fund['amfi_code'] == code]['scheme_name'].iloc[0].split(' - ')[0]
        ax_nav.plot(fn['date'], norm, color=nav_colors[i], linewidth=2, label=name)

# Nifty 50 benchmark
n50 = df_bm[(df_bm['index_name'] == 'NIFTY50') & (df_bm['date'] >= date_3yr)].sort_values('date')
if len(n50) > 0:
    base_n50 = n50['close_value'].iloc[0]
    norm_n50 = (n50['close_value'] / base_n50) * 100
    ax_nav.plot(n50['date'], norm_n50, color='#888888', linewidth=2, linestyle='--', label='NIFTY 50')

ax_nav.legend(fontsize=8, loc='upper left', framealpha=0.5, labelcolor=BRAND_TEXT)
style_ax(ax_nav, "NAV Performance vs Benchmark (3 Years, Rebased to 100)", "Date", "Normalized Value")

plt.savefig('Dashboard/Page2_Fund_Performance.png', dpi=150, bbox_inches='tight')
plt.close()
print("  [OK] Page 2 saved.")

# ===============================================================
# PAGE 3 - INVESTOR ANALYTICS
# ===============================================================
print("Generating Page 3 - Investor Analytics...")

fig = plt.figure(figsize=(PAGE_W, PAGE_H))
add_header(fig, "Investor Analytics", "Transaction Patterns - Demographics - Regional Insights")

gs = gridspec.GridSpec(2, 3, figure=fig, left=0.05, right=0.97, top=0.88, bottom=0.06,
                       hspace=0.4, wspace=0.3)

# Transaction Amount by State (Top 10)
ax_state = fig.add_subplot(gs[0, 0])
state_amt = df_txn.groupby('state')['amount_inr'].sum().sort_values(ascending=True).tail(10)
bars = ax_state.barh(range(len(state_amt)), state_amt.values / 1e7, color=BRAND_PRIMARY, height=0.65)
ax_state.set_yticks(range(len(state_amt)))
ax_state.set_yticklabels(state_amt.index, fontsize=8)
style_ax(ax_state, "Transaction Amount by State (Top 10)", "Amount (Rs. Crore)", "")

# Donut: SIP / Lumpsum / Redemption Split
ax_donut = fig.add_subplot(gs[0, 1])
txn_split = df_txn.groupby('transaction_type')['amount_inr'].sum()
donut_colors = [BRAND_PRIMARY, BRAND_ACCENT, BRAND_WARN]
wedges, texts, autotexts = ax_donut.pie(
    txn_split.values, labels=txn_split.index, autopct='%1.1f%%',
    colors=donut_colors, pctdistance=0.78, startangle=90,
    wedgeprops=dict(width=0.45, edgecolor=BRAND_DARK)
)
for t in texts:
    t.set_color(BRAND_TEXT)
    t.set_fontsize(9)
for t in autotexts:
    t.set_color(BRAND_TEXT)
    t.set_fontsize(8)
    t.set_fontweight('bold')
ax_donut.set_title("Transaction Type Split", fontsize=11, fontweight='bold', color=BRAND_TEXT, pad=8)

# Age Group vs Avg SIP Amount
ax_age = fig.add_subplot(gs[0, 2])
sip_txns = df_txn[df_txn['transaction_type'] == 'SIP']
age_avg = sip_txns.groupby('age_group')['amount_inr'].mean().sort_index()
age_colors = [BRAND_ACCENT, BRAND_PRIMARY, BRAND_ORANGE, BRAND_PURPLE, BRAND_WARN]
ax_age.bar(range(len(age_avg)), age_avg.values, color=age_colors[:len(age_avg)],
           width=0.55, edgecolor='none')
ax_age.set_xticks(range(len(age_avg)))
ax_age.set_xticklabels(age_avg.index, fontsize=8, rotation=30)
style_ax(ax_age, "Avg SIP Amount by Age Group", "Age Group", "Avg Amount (Rs.)")

# Monthly Transaction Volume Line
ax_vol = fig.add_subplot(gs[1, :2])
df_txn['month'] = df_txn['transaction_date'].dt.to_period('M')
monthly_vol = df_txn.groupby('month').size()
monthly_vol.index = monthly_vol.index.to_timestamp()
ax_vol.fill_between(monthly_vol.index, monthly_vol.values, alpha=0.2, color=BRAND_ACCENT)
ax_vol.plot(monthly_vol.index, monthly_vol.values, color=BRAND_ACCENT, linewidth=2)
style_ax(ax_vol, "Monthly Transaction Volume", "Month", "Number of Transactions")
ax_vol.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b %Y'))
ax_vol.tick_params(axis='x', rotation=30)

# City Tier Breakdown
ax_tier = fig.add_subplot(gs[1, 2])
tier_data = df_txn.groupby('city_tier')['amount_inr'].sum().sort_values(ascending=False)
tier_colors = [BRAND_PRIMARY, BRAND_ACCENT, BRAND_ORANGE]
ax_tier.bar(range(len(tier_data)), tier_data.values / 1e7, color=tier_colors[:len(tier_data)],
            width=0.5, edgecolor='none')
ax_tier.set_xticks(range(len(tier_data)))
ax_tier.set_xticklabels(tier_data.index, fontsize=9)
style_ax(ax_tier, "Investment by City Tier", "City Tier", "Amount (Rs. Crore)")

plt.savefig('Dashboard/Page3_Investor_Analytics.png', dpi=150, bbox_inches='tight')
plt.close()
print("  [OK] Page 3 saved.")

# ===============================================================
# PAGE 4 - SIP & MARKET TRENDS
# ===============================================================
print("Generating Page 4 - SIP & Market Trends...")

fig = plt.figure(figsize=(PAGE_W, PAGE_H))
add_header(fig, "SIP & Market Trends", "SIP Inflows - Nifty 50 Correlation - Category Net Flows")

gs = gridspec.GridSpec(2, 2, figure=fig, left=0.05, right=0.97, top=0.88, bottom=0.06,
                       hspace=0.4, wspace=0.25)

# Dual-axis: SIP Inflow (bar) + Nifty 50 (line)
ax_dual = fig.add_subplot(gs[0, :])
sip_sorted = df_sip.sort_values('month').copy()
sip_sorted['month_dt'] = pd.to_datetime(sip_sorted['month'] + '-01')
x_pos = range(len(sip_sorted))

ax_dual.bar(x_pos, sip_sorted['sip_inflow_crore'].values, color=BRAND_PRIMARY,
            alpha=0.8, width=0.65, label='SIP Inflow (Rs. Cr)')

ax2 = ax_dual.twinx()
# Align Nifty 50 monthly close to SIP months
n50_monthly = df_bm[df_bm['index_name'] == 'NIFTY50'].copy()
n50_monthly['month'] = n50_monthly['date'].dt.to_period('M')
n50_month_close = n50_monthly.groupby('month')['close_value'].last()
n50_month_close.index = n50_month_close.index.to_timestamp()

aligned_nifty = []
for m in sip_sorted['month_dt'].values:
    ts = pd.Timestamp(m)
    if ts in n50_month_close.index:
        aligned_nifty.append(n50_month_close[ts])
    else:
        aligned_nifty.append(np.nan)

ax2.plot(x_pos, aligned_nifty, color=BRAND_WARN, linewidth=2.5, label='NIFTY 50')
ax2.set_ylabel('NIFTY 50 Level', fontsize=9, color=BRAND_WARN)
ax2.tick_params(axis='y', colors=BRAND_WARN)
ax2.spines['right'].set_color(BRAND_WARN)

tick_step = max(1, len(sip_sorted) // 12)
ax_dual.set_xticks(range(0, len(sip_sorted), tick_step))
ax_dual.set_xticklabels(sip_sorted['month'].values[::tick_step], fontsize=7, rotation=45)
style_ax(ax_dual, "SIP Inflows vs NIFTY 50 (2022–2025)", "", "SIP Inflow (Rs. Crore)")

lines1, labels1 = ax_dual.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax_dual.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc='upper left',
               framealpha=0.5, labelcolor=BRAND_TEXT)

# Category Inflow Heatmap
ax_heat = fig.add_subplot(gs[1, 0])
cat_pivot = df_cat.pivot_table(index='category', columns='month', values='net_inflow_crore', aggfunc='sum')
# Keep only FY24-FY25 months for readability
cat_pivot = cat_pivot.iloc[:, -12:] if cat_pivot.shape[1] > 12 else cat_pivot

im = ax_heat.imshow(cat_pivot.values, aspect='auto', cmap='RdYlGn',
                     interpolation='nearest')
ax_heat.set_xticks(range(cat_pivot.shape[1]))
ax_heat.set_xticklabels(cat_pivot.columns, fontsize=6, rotation=45)
ax_heat.set_yticks(range(cat_pivot.shape[0]))
short_cats = [c[:18] for c in cat_pivot.index]
ax_heat.set_yticklabels(short_cats, fontsize=7)
plt.colorbar(im, ax=ax_heat, shrink=0.8, label='Net Inflow (Rs. Cr)')
style_ax(ax_heat, "Category Inflow Heatmap (Last 12 Months)", "", "")

# Top 5 Categories by Net Inflow FY25
ax_top5 = fig.add_subplot(gs[1, 1])
fy25_months = [m for m in df_cat['month'].unique() if m.startswith('2024-04') or m.startswith('2024-05') or
               m.startswith('2024-06') or m.startswith('2024-07') or m.startswith('2024-08') or
               m.startswith('2024-09') or m.startswith('2024-10') or m.startswith('2024-11') or
               m.startswith('2024-12') or m.startswith('2025-01') or m.startswith('2025-02') or
               m.startswith('2025-03')]
if len(fy25_months) == 0:
    # Use latest 12 months available
    all_months = sorted(df_cat['month'].unique())
    fy25_months = all_months[-12:]

fy25_cat = df_cat[df_cat['month'].isin(fy25_months)].groupby('category')['net_inflow_crore'].sum()
top5_cat = fy25_cat.sort_values(ascending=True).tail(5)
colors_top5 = [BRAND_PRIMARY, BRAND_ACCENT, BRAND_ORANGE, BRAND_PURPLE, BRAND_WARN]
ax_top5.barh(range(len(top5_cat)), top5_cat.values, color=colors_top5, height=0.55)
ax_top5.set_yticks(range(len(top5_cat)))
ax_top5.set_yticklabels([c[:20] for c in top5_cat.index], fontsize=8)
style_ax(ax_top5, "Top 5 Categories by Net Inflow (FY25)", "Net Inflow (Rs. Crore)", "")

plt.savefig('Dashboard/Page4_SIP_Market_Trends.png', dpi=150, bbox_inches='tight')
plt.close()
print("  [OK] Page 4 saved.")

# ===============================================================
# COMBINE INTO PDF
# ===============================================================
print("Generating Dashboard.pdf...")
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

pages = [
    'Dashboard/Page1_Industry_Overview.png',
    'Dashboard/Page2_Fund_Performance.png',
    'Dashboard/Page3_Investor_Analytics.png',
    'Dashboard/Page4_SIP_Market_Trends.png'
]

with PdfPages('Dashboard/Dashboard.pdf') as pdf:
    for page_path in pages:
        img = Image.open(page_path)
        fig_pdf, ax_pdf = plt.subplots(figsize=(PAGE_W, PAGE_H))
        ax_pdf.imshow(img)
        ax_pdf.axis('off')
        fig_pdf.subplots_adjust(left=0, right=1, top=1, bottom=0)
        pdf.savefig(fig_pdf, dpi=150)
        plt.close(fig_pdf)

print("  [OK] Dashboard.pdf saved.")
print("\n=== All deliverables generated ===")
print("  * Dashboard/Page1_Industry_Overview.png")
print("  * Dashboard/Page2_Fund_Performance.png")
print("  * Dashboard/Page3_Investor_Analytics.png")
print("  * Dashboard/Page4_SIP_Market_Trends.png")
print("  * Dashboard/Dashboard.pdf")
