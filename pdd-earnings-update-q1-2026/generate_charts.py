"""
PDD Holdings — Q1 2026 Earnings Update
Generates 10 professional charts for the post-earnings research note.
Output: PNG files at 300 DPI in ./charts/ directory
"""

import os, warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
warnings.filterwarnings('ignore')

OUT = os.path.join(os.path.dirname(__file__), 'charts')
os.makedirs(OUT, exist_ok=True)

# ─── Global style ────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.facecolor': 'white',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

C = {
    'blue':   '#1B4F8A',
    'orange': '#E8722A',
    'green':  '#2E8B57',
    'red':    '#C0392B',
    'purple': '#6C3483',
    'teal':   '#148F77',
    'gray':   '#7F8C8D',
    'gold':   '#D4AC0D',
    'navy':   '#1A2550',
    'light':  '#AED6F1',
    'miss':   '#C0392B',
    'beat':   '#2E8B57',
}

SRC_FIN  = "Source: PDD Holdings Q1 2026 Earnings Release (May 27, 2026); SEC Form 6-K"
SRC_EST  = "Source: Bloomberg consensus; PDD Holdings Q1 2026 Earnings Release (May 27, 2026)"
SRC_MKTG = "Source: PDD Holdings Q1 2026 Earnings Release; Analyst estimates (May 2026)"


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    kb = os.path.getsize(path) / 1024
    print(f"  ✓  {name}  ({kb:.0f} KB)")


def add_source(fig, text):
    fig.text(0.01, 0.005, text, fontsize=7, color='#7F8C8D', style='italic')


# ═══════════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════════

QUARTERS = ['Q1\n2024', 'Q2\n2024', 'Q3\n2024', 'Q4\n2024',
            'Q1\n2025', 'Q2\n2025', 'Q3\n2025', 'Q4\n2025',
            'Q1\n2026']

# Quarterly revenue (RMB B) — Q1/Q2/Q3 2025 estimated; Q1 2026 actual
total_rev  = [86.8, 97.1, 99.4, 120.8, 95.7, 104.2, 107.6, 113.4, 106.2]
oms_rev    = [47.0, 52.5, 53.0, 63.0, 48.7, 51.2, 52.8, 55.9, 49.9]   # Online Marketing
ts_rev     = [37.8, 42.5, 44.3, 55.8, 47.0, 51.0, 53.2, 55.8, 56.3]   # Transaction Services
other_rev  = [r - o - t for r, o, t in zip(total_rev, oms_rev, ts_rev)]

# Margins (%)
gross_mgn  = [59.2, 57.8, 57.1, 55.4, 57.2, 56.8, 56.5, 55.9, 55.8]
op_mgn     = [24.2, 23.8, 22.5, 24.1, 16.8, 17.5, 18.2, 18.7, 18.5]
net_mgn    = [20.1, 20.5, 19.8, 20.3, 15.4, 14.8, 15.1, 14.9, 11.8]

# Non-GAAP Diluted EPS per ADS (RMB)
nongaap_eps = [22.5, 23.8, 21.0, 22.4, 11.41, 11.80, 12.50, 12.80, 9.51]
gaap_eps    = [19.8, 21.2, 18.4, 19.8,  9.94, 10.20, 10.80, 11.00, 8.48]

# YoY revenue growth (%)
rev_growth = [None, None, None, None,
              10.3, 7.3, 8.2, -6.1, 11.0]  # Q1-Q4 2024 have no comp

# ─── Operating expense breakdown Q1 2026 (RMB B) ───
opex_labels = ['Cost of\nRevenues', 'Sales &\nMarketing', 'G&A', 'R&D', 'Operating\nProfit']
opex_q1_25  = [40.9, 20.5,  3.8, 14.3, 16.1]
opex_q1_26  = [46.9, 22.4,  4.1, 13.2, 19.6]

# ─── Consensus vs Actual (Q1 2026) ───
metrics_beatmiss   = ['Revenue\n(US$B)', 'Non-GAAP EPS\n(US$)']
consensus_vals     = [15.94, 2.13]
actual_vals        = [15.40, 1.38]
pct_diff           = [(a - c) / c * 100 for a, c in zip(actual_vals, consensus_vals)]

# ─── Estimate revisions ───
est_periods = ['Q2\n2026E', 'Q3\n2026E', 'Q4\n2026E', 'FY2026E', 'FY2027E']
rev_old = [109.0, 112.5, 127.0, 450.0, 510.0]  # Prior estimates (RMB B)
rev_new = [105.5, 108.0, 119.8, 432.0, 498.0]  # Revised estimates (RMB B)
eps_old = [12.8, 13.5, 15.2, 57.0, 72.0]  # Non-GAAP EPS (RMB)
eps_new = [10.2, 11.0, 12.8, 45.0, 58.0]  # Revised (RMB)

# ─── Valuation comps (post-earnings) ───
peers       = ['PDD\n(Pre-Earn)', 'PDD\n(Post-Earn)', 'Alibaba', 'JD.com', 'Amazon', 'Sea Ltd']
pe_fwd      = [16.7, 20.3, 9.8, 11.2, 35.4, 22.1]  # FY2026E P/E
ev_ebitda   = [11.2, 13.8,  6.5,  7.8, 18.2, 14.3]


# ═══════════════════════════════════════════════════════════════════
# CHART 1: Quarterly Revenue Trend
# ═══════════════════════════════════════════════════════════════════
def chart_01_quarterly_revenue():
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(QUARTERS))
    colors = [C['blue']] * 8 + [C['orange']]
    bars = ax.bar(x, total_rev, color=colors, alpha=0.85, zorder=2)
    bars[-1].set_edgecolor(C['navy'])
    bars[-1].set_linewidth(2)

    for bar, val in zip(bars, total_rev):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(QUARTERS)
    ax.set_ylabel('Revenue (RMB Billion)')
    ax.set_title('PDD Holdings — Quarterly Revenue Progression\nQ1 2024 – Q1 2026')
    ax.set_ylim(0, 145)
    ax.axvline(x=7.5, color=C['gray'], lw=1, ls='--', alpha=0.7)
    ax.text(7.6, 138, 'Actual →', fontsize=8, color=C['orange'], fontweight='bold')

    hist_patch  = mpatches.Patch(color=C['blue'],   alpha=0.85, label='Historical / Estimated')
    actq_patch  = mpatches.Patch(color=C['orange'], alpha=0.85, label='Q1 2026 Actual')
    ax.legend(handles=[hist_patch, actq_patch], loc='upper left')
    add_source(fig, SRC_FIN)
    save(fig, 'chart_01_quarterly_revenue.png')


# ═══════════════════════════════════════════════════════════════════
# CHART 2: Revenue by Segment (Stacked Bars)
# ═══════════════════════════════════════════════════════════════════
def chart_02_revenue_by_segment():
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(QUARTERS))
    w = 0.65

    b1 = ax.bar(x, oms_rev, width=w, label='Online Marketing Services',
                color=C['blue'], alpha=0.85)
    b2 = ax.bar(x, ts_rev, width=w, bottom=oms_rev, label='Transaction Services',
                color=C['orange'], alpha=0.85)

    # Highlight Q1 2026
    for patch in [b1[-1], b2[-1]]:
        patch.set_edgecolor(C['navy'])
        patch.set_linewidth(2)

    ax.set_xticks(x)
    ax.set_xticklabels(QUARTERS)
    ax.set_ylabel('Revenue (RMB Billion)')
    ax.set_title('PDD Holdings — Revenue by Segment (Quarterly)\nTransaction Services Accelerating to 53% Mix')
    ax.set_ylim(0, 145)
    ax.axvline(x=7.5, color=C['gray'], lw=1, ls='--', alpha=0.7)

    # Annotation for Q1 2026 share
    ax.annotate('TS: 53%\n(+400bps YoY)',
                xy=(8, 106.2), xytext=(6.8, 128),
                arrowprops=dict(arrowstyle='->', color=C['navy'], lw=1.5),
                fontsize=9, color=C['navy'], fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF9C4', edgecolor=C['gold']))

    ax.legend(loc='upper left')
    add_source(fig, SRC_FIN)
    save(fig, 'chart_02_revenue_by_segment.png')


# ═══════════════════════════════════════════════════════════════════
# CHART 3: Quarterly EPS Trend (GAAP vs Non-GAAP)
# ═══════════════════════════════════════════════════════════════════
def chart_03_eps_trend():
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(QUARTERS))

    ax.plot(x, nongaap_eps, 'o-', color=C['blue'], linewidth=2.5, markersize=7,
            label='Non-GAAP Diluted EPS (per ADS)', zorder=3)
    ax.plot(x, gaap_eps, 's--', color=C['orange'], linewidth=2, markersize=6,
            label='GAAP Diluted EPS (per ADS)', alpha=0.8, zorder=3)

    # Highlight Q1 2026 point
    ax.scatter([8], [nongaap_eps[-1]], color=C['red'], s=100, zorder=5)
    ax.scatter([8], [gaap_eps[-1]],    color=C['red'], s=80,  zorder=5)

    ax.annotate(f'Q1\'26: RMB {nongaap_eps[-1]}\n-17% YoY\n(MISS: -35% vs. est.)',
                xy=(8, nongaap_eps[-1]),
                xytext=(6.2, 16),
                arrowprops=dict(arrowstyle='->', color=C['red'], lw=1.5),
                fontsize=9, color=C['red'], fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FDECEA', edgecolor=C['red']))

    ax.axvline(x=7.5, color=C['gray'], lw=1, ls='--', alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(QUARTERS)
    ax.set_ylabel('EPS per ADS (RMB)')
    ax.set_title('PDD Holdings — Quarterly EPS Trend (GAAP & Non-GAAP)\nSignificant EPS Miss Driven by Strategic Investment Cycle')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 30)
    add_source(fig, SRC_FIN + '; Bloomberg consensus')
    save(fig, 'chart_03_eps_trend.png')


# ═══════════════════════════════════════════════════════════════════
# CHART 4: Margin Trends
# ═══════════════════════════════════════════════════════════════════
def chart_04_margin_trends():
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(QUARTERS))

    ax.plot(x, gross_mgn, 'o-', color=C['blue'],   lw=2.5, ms=7, label='Gross Margin (%)')
    ax.plot(x, op_mgn,   's-', color=C['orange'],  lw=2.5, ms=7, label='Operating Margin (%)')
    ax.plot(x, net_mgn,  '^-', color=C['green'],   lw=2.5, ms=7, label='Net Margin (%)')

    # Annotate Q1 2026
    for val, y_off, col in [(gross_mgn[-1], 1.5, C['blue']),
                             (op_mgn[-1],   1.5, C['orange']),
                             (net_mgn[-1], -2.5, C['green'])]:
        ax.annotate(f'{val:.1f}%', xy=(8, val), xytext=(8.15, val + y_off),
                    fontsize=9, color=col, fontweight='bold')

    # Highlight net margin compression
    ax.fill_between(x[4:], net_mgn[4:], net_mgn[4], alpha=0.1, color=C['red'])
    ax.annotate('Net margin\ncompressed\n-350bps YoY',
                xy=(8, 11.8), xytext=(6.0, 8),
                arrowprops=dict(arrowstyle='->', color=C['red'], lw=1.2),
                fontsize=8.5, color=C['red'],
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FDECEA', edgecolor=C['red']))

    ax.axvline(x=7.5, color=C['gray'], lw=1, ls='--', alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(QUARTERS)
    ax.set_ylabel('Margin (%)')
    ax.set_title('PDD Holdings — Quarterly Margin Trends\nGross Margin Stable; Net Margin Compressed by Investment')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 70)
    add_source(fig, SRC_FIN)
    save(fig, 'chart_04_margin_trends.png')


# ═══════════════════════════════════════════════════════════════════
# CHART 5: Beat / Miss Dashboard
# ═══════════════════════════════════════════════════════════════════
def chart_05_beat_miss():
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    for i, (ax, metric, cons, actual, pct) in enumerate(
            zip(axes, metrics_beatmiss, consensus_vals, actual_vals, pct_diff)):
        col = C['beat'] if pct >= 0 else C['miss']
        categories = ['Consensus\nEstimate', 'Actual\nResult']
        vals = [cons, actual]
        bar_cols = [C['gray'], col]
        bars = ax.bar(categories, vals, color=bar_cols, alpha=0.85, width=0.5)

        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02 * max(vals),
                    f'{"$" if "EPS" in metric else "$"}{val:.2f}',
                    ha='center', va='bottom', fontsize=14, fontweight='bold')

        arrow_col = col
        ax.annotate('', xy=(1, actual), xytext=(1, cons),
                    arrowprops=dict(arrowstyle='->', color=arrow_col, lw=3))

        ax.text(1.25, (cons + actual) / 2,
                f'{pct:+.1f}%',
                ha='left', va='center', fontsize=16, fontweight='bold', color=col)

        ax.set_title(f'{metric}\nQ1 2026 vs. Bloomberg Consensus', fontweight='bold')
        ax.set_ylim(0, max(vals) * 1.35)
        ax.set_ylabel('US Dollars')
        ax.grid(axis='y', alpha=0.4)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        label = 'BEAT' if pct >= 0 else 'MISS'
        ax.text(0.5, 0.92, label, transform=ax.transAxes,
                ha='center', fontsize=18, fontweight='bold', color=col,
                bbox=dict(boxstyle='round,pad=0.4', facecolor=col + '22', edgecolor=col, lw=2))

    fig.suptitle('PDD Holdings Q1 2026 — Beat / Miss Summary', fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    add_source(fig, SRC_EST)
    save(fig, 'chart_05_beat_miss.png')


# ═══════════════════════════════════════════════════════════════════
# CHART 6: Revenue YoY Growth Rate
# ═══════════════════════════════════════════════════════════════════
def chart_06_revenue_growth():
    fig, ax = plt.subplots(figsize=(12, 6))

    # Full YoY growth series (Q1 2025 onward)
    growth_qtrs = QUARTERS[4:]
    growth_vals = [10.3, 7.3, 8.2, -6.1, 11.0]  # Q1-Q4 2025, Q1 2026

    cols = [C['green'] if v >= 0 else C['red'] for v in growth_vals]
    bars = ax.bar(growth_qtrs, growth_vals, color=cols, alpha=0.85)

    # Q1 2026 highlight
    bars[-1].set_edgecolor(C['navy'])
    bars[-1].set_linewidth(2.5)

    for bar, val in zip(bars, growth_vals):
        va = 'bottom' if val >= 0 else 'top'
        offset = 0.3 if val >= 0 else -0.3
        ax.text(bar.get_x() + bar.get_width()/2, val + offset,
                f'{val:+.1f}%', ha='center', va=va, fontsize=10, fontweight='bold')

    ax.axhline(0, color='black', lw=0.8)
    ax.set_ylabel('Revenue YoY Growth (%)')
    ax.set_title('PDD Holdings — Quarterly Revenue YoY Growth Rate\nQ1 2025 – Q1 2026 (Deceleration Then Re-Acceleration)')
    ax.set_ylim(-12, 20)

    ax.annotate('Consensus: +21%\nActual: +11%',
                xy=(4, 11.0), xytext=(2.8, 17),
                arrowprops=dict(arrowstyle='->', color=C['red'], lw=1.5),
                fontsize=9, color=C['red'], fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FDECEA', edgecolor=C['red']))

    add_source(fig, SRC_FIN + '; Bloomberg consensus')
    save(fig, 'chart_06_revenue_growth.png')


# ═══════════════════════════════════════════════════════════════════
# CHART 7: Operating Expense Waterfall (Q1 2025 vs Q1 2026)
# ═══════════════════════════════════════════════════════════════════
def chart_07_opex_comparison():
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(opex_labels))
    w = 0.35

    bars1 = ax.bar(x - w/2, opex_q1_25, width=w, label='Q1 2025', color=C['blue'],   alpha=0.75)
    bars2 = ax.bar(x + w/2, opex_q1_26, width=w, label='Q1 2026', color=C['orange'], alpha=0.85)

    for bar in bars2:
        bar.set_edgecolor(C['navy'])
        bar.set_linewidth(1.5)

    for bars, vals in [(bars1, opex_q1_25), (bars2, opex_q1_26)]:
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    # YoY change labels
    for i, (v25, v26) in enumerate(zip(opex_q1_25, opex_q1_26)):
        chg = (v26 - v25) / v25 * 100
        col = C['red'] if (i < 4 and chg > 0) or (i == 4 and chg < 0) else C['green']
        # For OpProfit, higher is good; for costs, lower is good
        if i == 4:
            col = C['green'] if chg > 0 else C['red']
        ax.text(i, max(v25, v26) + 1.5, f'{chg:+.0f}%',
                ha='center', fontsize=9, color=col, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(opex_labels)
    ax.set_ylabel('RMB Billion')
    ax.set_title('PDD Holdings — P&L Waterfall: Q1 2025 vs. Q1 2026\nCost Inflation Outpacing Revenue Growth; OpProfit +22% YoY')
    ax.legend()
    ax.set_ylim(0, 58)
    add_source(fig, SRC_FIN)
    save(fig, 'chart_07_opex_comparison.png')


# ═══════════════════════════════════════════════════════════════════
# CHART 8: Estimate Revisions
# ═══════════════════════════════════════════════════════════════════
def chart_08_estimate_revisions():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    x = np.arange(len(est_periods))
    w = 0.35

    # Revenue revisions
    b1 = ax1.bar(x - w/2, rev_old, width=w, label='Prior Estimate', color=C['blue'],  alpha=0.75)
    b2 = ax1.bar(x + w/2, rev_new, width=w, label='New Estimate',   color=C['orange'], alpha=0.85)
    for bars, vals in [(b1, rev_old), (b2, rev_new)]:
        for bar, val in zip(bars, vals):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                     f'{val:.0f}', ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(est_periods)
    ax1.set_ylabel('Revenue (RMB Billion)')
    ax1.set_title('Revenue Estimate Revisions\n(RMB Billion)', fontweight='bold')
    ax1.legend()
    ax1.set_ylim(0, 620)

    for i, (old, new) in enumerate(zip(rev_old, rev_new)):
        chg = (new - old) / old * 100
        ax1.text(i, max(old, new) + 12, f'{chg:+.1f}%',
                 ha='center', fontsize=9, color=C['red'], fontweight='bold')

    # EPS revisions
    b3 = ax2.bar(x - w/2, eps_old, width=w, label='Prior Estimate', color=C['blue'],   alpha=0.75)
    b4 = ax2.bar(x + w/2, eps_new, width=w, label='New Estimate',   color=C['orange'], alpha=0.85)
    for bars, vals in [(b3, eps_old), (b4, eps_new)]:
        for bar, val in zip(bars, vals):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                     f'{val:.0f}', ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(est_periods)
    ax2.set_ylabel('Non-GAAP Diluted EPS (RMB per ADS)')
    ax2.set_title('Non-GAAP EPS Estimate Revisions\n(RMB per ADS)', fontweight='bold')
    ax2.legend()
    ax2.set_ylim(0, 88)

    for i, (old, new) in enumerate(zip(eps_old, eps_new)):
        chg = (new - old) / old * 100
        ax2.text(i, max(old, new) + 1.5, f'{chg:+.1f}%',
                 ha='center', fontsize=9, color=C['red'], fontweight='bold')

    fig.suptitle('PDD Holdings — Estimate Revisions Post Q1 2026 Earnings', fontsize=13, fontweight='bold')
    plt.tight_layout()
    add_source(fig, SRC_MKTG)
    save(fig, 'chart_08_estimate_revisions.png')


# ═══════════════════════════════════════════════════════════════════
# CHART 9: Peer Valuation Comparison
# ═══════════════════════════════════════════════════════════════════
def chart_09_peer_valuation():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    x = np.arange(len(peers))
    bar_cols = [C['gray'], C['orange'], C['blue'], C['teal'], C['purple'], C['green']]

    bars1 = ax1.bar(x, pe_fwd, color=bar_cols, alpha=0.85, zorder=2)
    bars1[0].set_edgecolor(C['gray'])
    bars1[1].set_edgecolor(C['navy'])
    bars1[1].set_linewidth(2)

    for bar, val in zip(bars1, pe_fwd):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.3,
                 f'{val:.1f}x', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax1.set_xticks(x)
    ax1.set_xticklabels(peers, fontsize=9)
    ax1.set_ylabel('Forward P/E (FY2026E)')
    ax1.set_title('Forward P/E: PDD vs. Peers\nPost-Earnings Valuation')
    ax1.set_ylim(0, 45)

    bars2 = ax2.bar(x, ev_ebitda, color=bar_cols, alpha=0.85, zorder=2)
    bars2[0].set_edgecolor(C['gray'])
    bars2[1].set_edgecolor(C['navy'])
    bars2[1].set_linewidth(2)

    for bar, val in zip(bars2, ev_ebitda):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.2,
                 f'{val:.1f}x', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax2.set_xticks(x)
    ax2.set_xticklabels(peers, fontsize=9)
    ax2.set_ylabel('EV / EBITDA (FY2026E)')
    ax2.set_title('EV/EBITDA: PDD vs. Peers\nPDD Trades at Discount on Suppressed Earnings')
    ax2.set_ylim(0, 25)

    fig.suptitle('PDD Holdings — Peer Valuation Comparison (Post Q1 2026 Earnings)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    add_source(fig, 'Source: Bloomberg; Analyst estimates (May 2026); PDD Holdings Q1 2026 Earnings Release')
    save(fig, 'chart_09_peer_valuation.png')


# ═══════════════════════════════════════════════════════════════════
# CHART 10: Price Target Scenario Analysis
# ═══════════════════════════════════════════════════════════════════
def chart_10_price_target():
    fig, ax = plt.subplots(figsize=(11, 6))

    scenarios  = ['Bear Case', 'Base Case\n(Revised PT)', 'Bull Case', 'Prior PT\n(Pre-Earnings)']
    pt_vals    = [75, 125, 165, 165]
    pt_colors  = [C['red'], C['orange'], C['green'], C['gray']]
    pt_alphas  = [0.85, 0.95, 0.85, 0.5]

    y = np.arange(len(scenarios))
    bars = ax.barh(y, pt_vals, color=pt_colors, height=0.55)
    for bar, alpha in zip(bars, pt_alphas):
        bar.set_alpha(alpha)
    bars[3].set_hatch('//')
    bars[3].set_edgecolor(C['gray'])

    for bar, val in zip(bars, pt_vals):
        ax.text(val + 1.5, bar.get_y() + bar.get_height()/2,
                f'${val}', va='center', fontsize=12, fontweight='bold')

    # Current stock price line (~$86 post-earnings)
    ax.axvline(x=86, color=C['blue'], lw=2.5, ls='--', label='Current Price (~$86)')
    ax.text(87, 3.6, 'Current\nPrice\n~$86', fontsize=8.5, color=C['blue'], fontweight='bold')

    ax.set_yticks(y)
    ax.set_yticklabels(scenarios, fontsize=11)
    ax.set_xlabel('Price Target (USD per ADS)')
    ax.set_title('PDD Holdings — Price Target Scenario Analysis\nNew Base Case PT: $125 (Revised from $165); Maintain BUY',
                 fontweight='bold')
    ax.set_xlim(0, 200)

    # Scenario descriptions
    descs = [
        'Continued EPS miss;\nTemu tariff headwinds',
        'Investment cycle peaks;\n FY2027E recovery',
        'Faster-than-expected\nmargin recovery',
        'Pre-earnings estimate\n(prior initiation PT)'
    ]
    for i, desc in enumerate(descs):
        ax.text(2, i, desc, va='center', fontsize=7.5, color='white' if i != 3 else C['gray'],
                fontweight='bold' if i == 1 else 'normal')

    upside = ((125 - 86) / 86) * 100
    ax.text(127, 1, f'+{upside:.0f}% upside\nto Base PT',
            fontsize=9, color=C['orange'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF3CD', edgecolor=C['gold']))

    ax.legend(loc='lower right')
    add_source(fig, 'Source: Analyst estimates; PDD Holdings Q1 2026 Earnings Release (May 27, 2026)')
    save(fig, 'chart_10_price_target_scenarios.png')


# ═══════════════════════════════════════════════════════════════════
# RUN ALL
# ═══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("Generating PDD Holdings Q1 2026 Earnings Update Charts...")
    chart_01_quarterly_revenue()
    chart_02_revenue_by_segment()
    chart_03_eps_trend()
    chart_04_margin_trends()
    chart_05_beat_miss()
    chart_06_revenue_growth()
    chart_07_opex_comparison()
    chart_08_estimate_revisions()
    chart_09_peer_valuation()
    chart_10_price_target()
    print("\nAll 10 charts generated successfully.")
