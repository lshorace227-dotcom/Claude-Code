"""
亞朵生活控股 (ATAT) — 2026 年第一季度業績更新報告
生成 10 張專業圖表
輸出：300 DPI PNG 圖檔，存於 ./charts/ 目錄
"""

import os, warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

OUT = os.path.join(os.path.dirname(__file__), 'charts')
os.makedirs(OUT, exist_ok=True)

# ─── 全局樣式 ────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': ['Heiti TC', 'PingFang HK', 'Arial Unicode MS', 'DejaVu Sans'],
    'font.size': 10,
    'axes.unicode_minus': False,
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

SRC_FIN  = "資料來源：亞朵生活控股 2026 Q1 業績公告（2026-05-13）；SEC Form 6-K"
SRC_EST  = "資料來源：Bloomberg / FactSet 一致預期；亞朵 2026 Q1 業績公告（2026-05-13）"
SRC_OPS  = "資料來源：亞朵生活控股 2026 Q1 業績公告；管理層業績說明會（2026-05-13）"


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    kb = os.path.getsize(path) / 1024
    print(f"  ✓  {name}  ({kb:.0f} KB)")


def add_source(fig, text):
    fig.text(0.01, 0.005, text, fontsize=7, color='#7F8C8D', style='italic')


# ═══════════════════════════════════════════════════════════════════
# 數據
# ═══════════════════════════════════════════════════════════════════

QUARTERS = ['Q1\n2024', 'Q2\n2024', 'Q3\n2024', 'Q4\n2024',
            'Q1\n2025', 'Q2\n2025', 'Q3\n2025', 'Q4\n2025',
            'Q1\n2026']

# 季度營收 (RMB 百萬) — 歷史數據結合公告披露
REVENUE_RMB_M = [1212, 1577, 1797, 1825, 1906, 1928, 2247, 2381, 2811]

# 季度淨利潤 (RMB 百萬)
NET_INCOME_RMB_M = [157, 269, 379, 251, 244, 366, 384, 446, 463]

# 季度 RevPAR (RMB)
REVPAR = [296, 348, 369, 318, 304, 343, 354, 336, 312]

# 季度 ADR (RMB)
ADR = [421, 442, 458, 432, 418, 437, 445, 438, 427]

# 季度入住率 (%)
OCC = [70.3, 78.7, 80.7, 73.6, 70.2, 78.5, 79.5, 76.1, 70.6]

# 酒店家數
HOTEL_COUNT = [1326, 1412, 1533, 1727, 1750, 1808, 1933, 2015, 2088]


# ═══════════════════════════════════════════════════════════════════
# 圖 1：季度營收走勢
# ═══════════════════════════════════════════════════════════════════
def chart_01_quarterly_revenue():
    fig, ax = plt.subplots(figsize=(11, 5.5))
    x = np.arange(len(QUARTERS))
    bars = ax.bar(x, REVENUE_RMB_M, color=[C['gray']]*8 + [C['orange']],
                  edgecolor='white', linewidth=1.5, width=0.65)
    bars[-1].set_color(C['orange'])

    for i, v in enumerate(REVENUE_RMB_M):
        ax.text(i, v + 40, f'{v:,}', ha='center', va='bottom',
                fontweight='bold', fontsize=9,
                color=C['navy'] if i < 8 else C['orange'])

    yoy_q1_26 = (REVENUE_RMB_M[-1] / REVENUE_RMB_M[4] - 1) * 100
    ax.annotate(f'年增 +{yoy_q1_26:.1f}%\n本季營收',
                xy=(8, REVENUE_RMB_M[-1]), xytext=(6.3, 3300),
                fontsize=11, fontweight='bold', color=C['orange'],
                ha='center',
                arrowprops=dict(arrowstyle='->', color=C['orange'], lw=1.8))

    ax.set_xticks(x); ax.set_xticklabels(QUARTERS)
    ax.set_ylabel('季度淨營收（人民幣 百萬元）', fontweight='bold')
    ax.set_title('圖 1：亞朵季度營收走勢——Q1 2026 創歷史單季新高',
                 loc='left', pad=14)
    ax.set_ylim(0, 3500)
    add_source(fig, SRC_FIN)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    save(fig, 'chart_01_quarterly_revenue.png')


# ═══════════════════════════════════════════════════════════════════
# 圖 2：分部營收結構
# ═══════════════════════════════════════════════════════════════════
def chart_02_segment_revenue():
    segs = ['加盟管理\n酒店', '租賃及自營\n酒店', '零售業務', '其他']
    q1_25 = [1032, 129, 694, 51]
    q1_26 = [1568, 118, 1071, 54]
    yoy = [(b/a - 1) * 100 for a, b in zip(q1_25, q1_26)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5),
                                    gridspec_kw={'width_ratios': [1.3, 1]})

    x = np.arange(len(segs)); w = 0.36
    b1 = ax1.bar(x - w/2, q1_25, w, label='2025 Q1', color=C['gray'], edgecolor='white')
    b2 = ax1.bar(x + w/2, q1_26, w, label='2026 Q1', color=C['orange'], edgecolor='white')
    for i, (a, b) in enumerate(zip(q1_25, q1_26)):
        ax1.text(i - w/2, a + 30, f'{a:,}', ha='center', fontsize=8, color=C['gray'])
        ax1.text(i + w/2, b + 30, f'{b:,}', ha='center', fontsize=9,
                 fontweight='bold', color=C['orange'])
    ax1.set_xticks(x); ax1.set_xticklabels(segs, fontsize=10)
    ax1.set_ylabel('營收（人民幣 百萬元）', fontweight='bold')
    ax1.set_title('分部營收：Q1 2026 vs Q1 2025', loc='left', pad=10)
    ax1.legend(loc='upper right', frameon=False)
    ax1.set_ylim(0, 1900)

    colors = [C['green'] if v >= 0 else C['red'] for v in yoy]
    ax2.barh(segs, yoy, color=colors, edgecolor='white', height=0.55)
    for i, v in enumerate(yoy):
        ax2.text(v + (1.5 if v >= 0 else -1.5), i, f'{v:+.1f}%',
                 ha='left' if v >= 0 else 'right', va='center',
                 fontweight='bold', fontsize=10, color=colors[i])
    ax2.axvline(0, color='black', lw=0.8)
    ax2.set_xlabel('年增率 (%)', fontweight='bold')
    ax2.set_title('分部年增率', loc='left', pad=10)
    ax2.set_xlim(-15, 65)

    fig.suptitle('圖 2：分部營收結構——零售與加盟管理酒店業務雙引擎驅動',
                 fontsize=13, fontweight='bold', y=1.00, x=0.05, ha='left')
    add_source(fig, SRC_FIN)
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    save(fig, 'chart_02_segment_revenue.png')


# ═══════════════════════════════════════════════════════════════════
# 圖 3：淨利潤與獲利能力
# ═══════════════════════════════════════════════════════════════════
def chart_03_profitability():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    x = np.arange(len(QUARTERS))
    bars = ax1.bar(x, NET_INCOME_RMB_M, color=[C['gray']]*8 + [C['blue']],
                   edgecolor='white', width=0.65)
    bars[-1].set_color(C['blue'])
    for i, v in enumerate(NET_INCOME_RMB_M):
        ax1.text(i, v + 8, f'{v}', ha='center', fontsize=8,
                 fontweight='bold' if i == 8 else 'normal',
                 color=C['blue'] if i == 8 else C['navy'])
    ax1.set_xticks(x); ax1.set_xticklabels(QUARTERS, fontsize=8)
    ax1.set_ylabel('淨利潤（人民幣 百萬元）', fontweight='bold')
    ax1.set_title('季度淨利潤——Q1 2026 年增 +90.3%',
                  loc='left', pad=10)
    ax1.set_ylim(0, 540)

    metrics = ['GAAP\n淨利率', '經調整\n淨利率', 'EBITDA\n利潤率', '經調整\nEBITDA 利潤率']
    q1_25_m = [12.8, 18.1, 19.5, 24.9]
    q1_26_m = [16.5, 17.4, 24.5, 25.5]
    x2 = np.arange(len(metrics)); w = 0.36
    ax2.bar(x2 - w/2, q1_25_m, w, label='2025 Q1', color=C['gray'], edgecolor='white')
    ax2.bar(x2 + w/2, q1_26_m, w, label='2026 Q1', color=C['blue'], edgecolor='white')
    for i, (a, b) in enumerate(zip(q1_25_m, q1_26_m)):
        ax2.text(i - w/2, a + 0.3, f'{a:.1f}%', ha='center', fontsize=8.5, color=C['gray'])
        ax2.text(i + w/2, b + 0.3, f'{b:.1f}%', ha='center', fontsize=8.5,
                 fontweight='bold', color=C['blue'])
    ax2.set_xticks(x2); ax2.set_xticklabels(metrics, fontsize=9)
    ax2.set_ylabel('利潤率 (%)', fontweight='bold')
    ax2.set_title('利潤率對比：經調整 EBITDA 利潤率擴張 +60bps',
                  loc='left', pad=10)
    ax2.legend(loc='upper left', frameon=False)
    ax2.set_ylim(0, 32)

    fig.suptitle('圖 3：淨利潤與利潤率——GAAP 淨利率擴張 370bps，但經調整淨利率小幅收縮',
                 fontsize=12.5, fontweight='bold', y=1.00, x=0.05, ha='left')
    add_source(fig, SRC_FIN)
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    save(fig, 'chart_03_profitability.png')


# ═══════════════════════════════════════════════════════════════════
# 圖 4：RevPAR / ADR / 入住率走勢
# ═══════════════════════════════════════════════════════════════════
def chart_04_revpar_trends():
    fig, ax1 = plt.subplots(figsize=(11.5, 5.5))
    x = np.arange(len(QUARTERS))

    ax1.bar(x, REVPAR, color=[C['light']]*8 + [C['blue']],
            edgecolor='white', width=0.5, alpha=0.85, label='RevPAR (RMB)')
    for i, v in enumerate(REVPAR):
        ax1.text(i, v + 5, f'{v}', ha='center', fontsize=8.5,
                 fontweight='bold' if i == 8 else 'normal',
                 color=C['blue'] if i == 8 else C['navy'])
    ax1.set_xticks(x); ax1.set_xticklabels(QUARTERS)
    ax1.set_ylabel('RevPAR (RMB)', fontweight='bold', color=C['blue'])
    ax1.tick_params(axis='y', labelcolor=C['blue'])
    ax1.set_ylim(0, 420)

    ax2 = ax1.twinx()
    ax2.plot(x, OCC, color=C['orange'], marker='o', lw=2.2,
             markersize=7, label='入住率 (%)', markerfacecolor='white',
             markeredgewidth=1.8)
    for i, v in enumerate(OCC):
        ax2.text(i, v + 1.5, f'{v:.1f}%', ha='center', fontsize=8, color=C['orange'])
    ax2.set_ylabel('入住率 (%)', fontweight='bold', color=C['orange'])
    ax2.tick_params(axis='y', labelcolor=C['orange'])
    ax2.set_ylim(60, 92)
    ax2.grid(False)

    ax1.set_title('圖 4：RevPAR / ADR / 入住率——同店成熟酒店仍承壓，整體 RevPAR 同比 +2.4%',
                  loc='left', pad=12)

    ax1.annotate('Q4 2025 季節性\n高點 (RMB 336)',
                 xy=(7, REVPAR[7]), xytext=(5.5, 400),
                 fontsize=9, color=C['gray'],
                 arrowprops=dict(arrowstyle='->', color=C['gray'], lw=1))
    ax1.annotate('Q1 2026 RMB 312\n同比 +2.4%',
                 xy=(8, REVPAR[-1]), xytext=(6.5, 200),
                 fontsize=9, color=C['blue'], fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color=C['blue'], lw=1.2))

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper right', frameon=True,
               facecolor='white', edgecolor=C['gray'])

    add_source(fig, SRC_OPS)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    save(fig, 'chart_04_revpar_trends.png')


# ═══════════════════════════════════════════════════════════════════
# 圖 5：酒店家數與管道
# ═══════════════════════════════════════════════════════════════════
def chart_05_hotel_network():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5),
                                    gridspec_kw={'width_ratios': [1.4, 1]})
    x = np.arange(len(QUARTERS))
    ax1.fill_between(x, HOTEL_COUNT, alpha=0.18, color=C['teal'])
    ax1.plot(x, HOTEL_COUNT, color=C['teal'], lw=2.5, marker='o',
             markersize=7, markerfacecolor='white', markeredgewidth=2)
    for i, v in enumerate(HOTEL_COUNT):
        ax1.text(i, v + 35, f'{v:,}', ha='center', fontsize=8.5,
                 fontweight='bold' if i == 8 else 'normal',
                 color=C['teal'] if i == 8 else C['navy'])
    ax1.set_xticks(x); ax1.set_xticklabels(QUARTERS, fontsize=9)
    ax1.set_ylabel('在營酒店家數', fontweight='bold')
    ax1.set_title('在營酒店家數——年增 +20.9%',
                  loc='left', pad=10)
    ax1.set_ylim(1100, 2300)

    cats = ['Q1 新開業\n酒店', 'Q1 關閉\n酒店', '淨增加\n酒店', '在建\n管道']
    vals = [110, -37, 73, 751]
    colors = [C['green'], C['red'], C['blue'], C['orange']]
    bars = ax2.bar(cats, vals, color=colors, edgecolor='white', width=0.6)
    for b, v in zip(bars, vals):
        ax2.text(b.get_x() + b.get_width()/2,
                 v + (15 if v >= 0 else -25), f'{v:+,}' if v != 751 else f'{v:,}',
                 ha='center', fontsize=11, fontweight='bold',
                 color=b.get_facecolor())
    ax2.axhline(0, color='black', lw=0.8)
    ax2.set_ylabel('家數', fontweight='bold')
    ax2.set_title('Q1 2026 酒店組合動態', loc='left', pad=10)
    ax2.set_ylim(-100, 850)

    fig.suptitle('圖 5：酒店網絡——管道蓄水達 751 家，全年開業目標維持不變',
                 fontsize=13, fontweight='bold', y=1.00, x=0.05, ha='left')
    add_source(fig, SRC_OPS)
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    save(fig, 'chart_05_hotel_network.png')


# ═══════════════════════════════════════════════════════════════════
# 圖 6：業績預期超預期分析（Beat/Miss）
# ═══════════════════════════════════════════════════════════════════
def chart_06_beat_miss():
    metrics = ['營收\n(US$M)', 'EPS\n(US$/ADS)', '經調整\nEBITDA\n(US$M)',
               '淨利潤\n(US$M)']
    consensus = [375.6, 0.37, 92.0, 49.0]
    actual = [413.97, 0.52, 104.0, 67.0]
    diff_pct = [(a/c - 1) * 100 for a, c in zip(consensus, actual)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5),
                                    gridspec_kw={'width_ratios': [1.3, 1]})

    x = np.arange(len(metrics)); w = 0.36
    ax1.bar(x - w/2, consensus, w, label='市場一致預期', color=C['gray'], edgecolor='white')
    ax1.bar(x + w/2, actual, w, label='實際公告', color=C['green'], edgecolor='white')
    for i, (c, a) in enumerate(zip(consensus, actual)):
        fmt = '${:.2f}' if i == 1 else '${:,.0f}'
        ax1.text(i - w/2, c + max(actual)*0.015,
                 fmt.format(c), ha='center', fontsize=8.5, color=C['gray'])
        ax1.text(i + w/2, a + max(actual)*0.015,
                 fmt.format(a), ha='center', fontsize=9,
                 fontweight='bold', color=C['green'])
    ax1.set_xticks(x); ax1.set_xticklabels(metrics, fontsize=9)
    ax1.set_ylabel('美元（百萬元 / 每 ADS）', fontweight='bold')
    ax1.set_title('預期 vs 實際——四項核心指標全面超預期',
                  loc='left', pad=10)
    ax1.legend(loc='upper right', frameon=False)

    colors2 = [C['green']] * len(diff_pct)
    bars = ax2.barh(metrics, diff_pct, color=colors2, edgecolor='white', height=0.55)
    for i, v in enumerate(diff_pct):
        ax2.text(v + 0.5, i, f'+{v:.1f}%',
                 ha='left', va='center',
                 fontweight='bold', fontsize=10.5, color=C['green'])
    ax2.axvline(0, color='black', lw=0.8)
    ax2.set_xlabel('超預期幅度 (%)', fontweight='bold')
    ax2.set_title('超預期幅度', loc='left', pad=10)
    ax2.set_xlim(0, 50)

    fig.suptitle('圖 6：業績全面超預期——EPS 超預期 +40.5%，淨利潤超預期 +36.7%',
                 fontsize=12.5, fontweight='bold', y=1.00, x=0.05, ha='left')
    add_source(fig, SRC_EST)
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    save(fig, 'chart_06_beat_miss.png')


# ═══════════════════════════════════════════════════════════════════
# 圖 7：成本與費用結構
# ═══════════════════════════════════════════════════════════════════
def chart_07_opex_structure():
    cats = ['酒店\n營運成本', '零售\n商品成本', '銷售與行銷', '一般及行政', '研發費用']
    q1_25 = [820, 348, 207, 110, 36]
    q1_26 = [1136, 507, 401, 140, 50]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    x = np.arange(len(cats)); w = 0.36
    ax1.bar(x - w/2, q1_25, w, label='2025 Q1', color=C['gray'], edgecolor='white')
    ax1.bar(x + w/2, q1_26, w, label='2026 Q1', color=C['purple'], edgecolor='white')
    for i, (a, b) in enumerate(zip(q1_25, q1_26)):
        ax1.text(i - w/2, a + 20, f'{a:,}', ha='center', fontsize=8, color=C['gray'])
        ax1.text(i + w/2, b + 20, f'{b:,}', ha='center', fontsize=9,
                 fontweight='bold', color=C['purple'])
    ax1.set_xticks(x); ax1.set_xticklabels(cats, fontsize=9)
    ax1.set_ylabel('費用（人民幣 百萬元）', fontweight='bold')
    ax1.set_title('費用結構：Q1 2026 vs Q1 2025', loc='left', pad=10)
    ax1.legend(loc='upper right', frameon=False)
    ax1.set_ylim(0, 1300)

    yoy = [(b/a - 1) * 100 for a, b in zip(q1_25, q1_26)]
    rev_yoy = 47.5
    colors = [C['red'] if v > rev_yoy else C['green'] for v in yoy]
    ax2.barh(cats, yoy, color=colors, edgecolor='white', height=0.55)
    ax2.axvline(rev_yoy, color=C['orange'], ls='--', lw=2, label=f'營收年增 +{rev_yoy:.1f}%')
    for i, v in enumerate(yoy):
        ax2.text(v + 2, i, f'+{v:.1f}%', ha='left', va='center',
                 fontweight='bold', fontsize=10, color=colors[i])
    ax2.set_xlabel('年增率 (%)', fontweight='bold')
    ax2.set_title('費用年增率 vs 營收增速', loc='left', pad=10)
    ax2.legend(loc='lower right', frameon=False)
    ax2.set_xlim(0, 110)

    fig.suptitle('圖 7：營運費用結構——銷售與行銷費用增速最快 (+93.7%)，主要源於零售業務擴張',
                 fontsize=12, fontweight='bold', y=1.00, x=0.05, ha='left')
    add_source(fig, SRC_FIN)
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    save(fig, 'chart_07_opex_structure.png')


# ═══════════════════════════════════════════════════════════════════
# 圖 8：管理層指引上調與估算更新
# ═══════════════════════════════════════════════════════════════════
def chart_08_guidance_revisions():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    cats = ['FY2026\n總營收', 'FY2026\n零售營收']
    prev_low = [24, 25]; prev_high = [28, 30]
    new_low = [24, 30]; new_high = [28, 35]

    x = np.arange(len(cats))
    for i in range(len(cats)):
        ax1.barh(i - 0.18, prev_high[i] - prev_low[i], height=0.32,
                 left=prev_low[i], color=C['gray'], alpha=0.65,
                 label='原指引' if i == 0 else None, edgecolor='white')
        ax1.barh(i + 0.18, new_high[i] - new_low[i], height=0.32,
                 left=new_low[i], color=C['green'], alpha=0.85,
                 label='更新後指引' if i == 0 else None, edgecolor='white')
        ax1.text(prev_low[i] + (prev_high[i] - prev_low[i])/2, i - 0.18,
                 f'+{prev_low[i]}~{prev_high[i]}%', ha='center', va='center',
                 fontsize=9.5, color='white', fontweight='bold')
        ax1.text(new_low[i] + (new_high[i] - new_low[i])/2, i + 0.18,
                 f'+{new_low[i]}~{new_high[i]}%', ha='center', va='center',
                 fontsize=9.5, color='white', fontweight='bold')
    ax1.set_yticks(x); ax1.set_yticklabels(cats, fontsize=10)
    ax1.set_xlabel('年增率指引 (%)', fontweight='bold')
    ax1.set_title('管理層指引：零售業務指引上調 +5pp',
                  loc='left', pad=10)
    ax1.legend(loc='lower right', frameon=False)
    ax1.set_xlim(0, 42)
    ax1.invert_yaxis()

    metrics = ['FY2026\n營收 (RMB M)', 'FY2026\n經調整淨利 (RMB M)',
               'FY2026\n經調整 EPS (US$)']
    old_est = [9800, 1750, 2.10]
    new_est = [10400, 1860, 2.28]
    chg_pct = [(n/o - 1) * 100 for o, n in zip(old_est, new_est)]

    x2 = np.arange(len(metrics))
    bars = ax2.bar(x2, chg_pct, color=C['blue'], edgecolor='white', width=0.55)
    for i, (b, v, o, n) in enumerate(zip(bars, chg_pct, old_est, new_est)):
        ax2.text(b.get_x() + b.get_width()/2, v + 0.15, f'+{v:.1f}%',
                 ha='center', fontsize=10, fontweight='bold', color=C['blue'])
        fmt_o = f'${o:,.2f}' if i == 2 else f'{o:,}'
        fmt_n = f'${n:,.2f}' if i == 2 else f'{n:,}'
        ax2.text(b.get_x() + b.get_width()/2, v - 0.6,
                 f'{fmt_o}\n→ {fmt_n}', ha='center', fontsize=8,
                 color=C['navy'])
    ax2.set_xticks(x2); ax2.set_xticklabels(metrics, fontsize=9)
    ax2.set_ylabel('預估上修幅度 (%)', fontweight='bold')
    ax2.set_title('賣方預估上修——三大指標均向上修正',
                  loc='left', pad=10)
    ax2.set_ylim(-2, 12)
    ax2.axhline(0, color='black', lw=0.6)

    fig.suptitle('圖 8：指引與預估更新——零售指引上調，FY2026 經調整 EPS 預估上修 +8.6%',
                 fontsize=12.5, fontweight='bold', y=1.00, x=0.05, ha='left')
    add_source(fig, SRC_EST)
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    save(fig, 'chart_08_guidance_revisions.png')


# ═══════════════════════════════════════════════════════════════════
# 圖 9：同業估值比較
# ═══════════════════════════════════════════════════════════════════
def chart_09_peer_valuation():
    peers = ['亞朵\n(ATAT)', '華住集團\n(HTHT)', '錦江酒店\n(600754)',
             '首旅酒店\n(600258)', 'IHG\n(IHG)', '萬豪\n(MAR)']
    pe_fy26 = [16.5, 21.3, 25.8, 28.0, 22.4, 25.6]
    rev_growth = [26.0, 11.5, 4.2, 5.8, 6.0, 4.9]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    colors = [C['orange'] if p == '亞朵\n(ATAT)' else C['gray'] for p in peers]
    bars = ax1.bar(peers, pe_fy26, color=colors, edgecolor='white', width=0.6)
    for b, v in zip(bars, pe_fy26):
        ax1.text(b.get_x() + b.get_width()/2, v + 0.4, f'{v:.1f}x',
                 ha='center', fontsize=9.5, fontweight='bold',
                 color=b.get_facecolor())
    ax1.axhline(np.mean(pe_fy26), color=C['blue'], ls='--', lw=1.2,
                label=f'同業均值 {np.mean(pe_fy26):.1f}x')
    ax1.set_ylabel('FY2026E P/E (x)', fontweight='bold')
    ax1.set_title('FY2026E P/E 估值對比', loc='left', pad=10)
    ax1.legend(loc='upper right', frameon=False)
    ax1.set_ylim(0, 33)
    ax1.tick_params(axis='x', labelsize=8.5)

    for p, pe, g in zip(peers, pe_fy26, rev_growth):
        peg = pe / g if g > 0 else float('inf')
        color = C['orange'] if '亞朵' in p else C['gray']
        ax2.scatter(g, pe, s=200 if '亞朵' in p else 110,
                    color=color, edgecolor='white', linewidth=1.5,
                    zorder=3)
        offset_y = 1.5 if '亞朵' in p else -1.7
        ax2.annotate(p.replace('\n', ' ').strip(),
                     xy=(g, pe), xytext=(g + 0.3, pe + offset_y),
                     fontsize=8.5,
                     fontweight='bold' if '亞朵' in p else 'normal',
                     color=color)
    ax2.set_xlabel('FY2026E 營收增速 (%)', fontweight='bold')
    ax2.set_ylabel('FY2026E P/E (x)', fontweight='bold')
    ax2.set_title('成長 vs 估值——亞朵成長最快但估值最低',
                  loc='left', pad=10)
    ax2.set_xlim(0, 32)
    ax2.set_ylim(10, 32)

    fig.suptitle('圖 9：同業估值對比——亞朵估值折讓且成長性領先，PEG 僅 0.6x',
                 fontsize=12.5, fontweight='bold', y=1.00, x=0.05, ha='left')
    add_source(fig, "資料來源：Bloomberg；FactSet 一致預期；2026 年 5 月 26 日")
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    save(fig, 'chart_09_peer_valuation.png')


# ═══════════════════════════════════════════════════════════════════
# 圖 10：目標股價情境分析
# ═══════════════════════════════════════════════════════════════════
def chart_10_price_target():
    scenarios = ['熊市情境\n零售放緩\n+ RevPAR 走弱', '基準情境\n指引中位實現\n+ 同業均值估值',
                 '牛市情境\n零售加速\n+ 估值重估']
    fy27_eps = [2.45, 2.85, 3.35]
    pe_mult = [16.0, 22.0, 26.0]
    target = [e * p for e, p in zip(fy27_eps, pe_mult)]
    current = 36.50

    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    colors = [C['red'], C['blue'], C['green']]
    bars = ax.bar(scenarios, target, color=colors, edgecolor='white',
                  width=0.55, alpha=0.85)
    for b, t, e, p in zip(bars, target, fy27_eps, pe_mult):
        ax.text(b.get_x() + b.get_width()/2, t + 1.5, f'${t:.0f}',
                ha='center', fontsize=15, fontweight='bold',
                color=b.get_facecolor())
        upside = (t/current - 1) * 100
        ax.text(b.get_x() + b.get_width()/2, t - 5,
                f'上行空間\n{upside:+.0f}%', ha='center',
                fontsize=10, fontweight='bold', color='white')
        ax.text(b.get_x() + b.get_width()/2, 4,
                f'FY27E EPS ${e:.2f}\n× {p:.0f}x P/E',
                ha='center', fontsize=9, color=C['navy'])

    ax.axhline(current, color=C['orange'], ls='--', lw=2,
               label=f'現價 ${current:.2f} (2026-05-26)')
    ax.set_ylabel('目標股價（US$ / ADS）', fontweight='bold')
    ax.set_title('圖 10：12 個月目標股價情境分析——基準情境上行空間 +72%',
                 loc='left', pad=14)
    ax.legend(loc='upper left', frameon=True, facecolor='white')
    ax.set_ylim(0, 100)

    add_source(fig, "資料來源：分析師預估；現價來自 NASDAQ 收盤價 2026-05-26")
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    save(fig, 'chart_10_price_target.png')


# ═══════════════════════════════════════════════════════════════════
# 主程式
# ═══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 60)
    print("亞朵 (ATAT) Q1 2026 業績更新 — 圖表生成")
    print("=" * 60)
    chart_01_quarterly_revenue()
    chart_02_segment_revenue()
    chart_03_profitability()
    chart_04_revpar_trends()
    chart_05_hotel_network()
    chart_06_beat_miss()
    chart_07_opex_structure()
    chart_08_guidance_revisions()
    chart_09_peer_valuation()
    chart_10_price_target()
    print("=" * 60)
    print(f"✓  10 張圖表已生成，輸出目錄：{OUT}")
    print("=" * 60)
