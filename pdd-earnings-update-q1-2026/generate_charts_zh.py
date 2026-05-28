"""
PDD Holdings — Q1 2026 盈利更新報告（繁體中文版）
生成 10 張專業圖表，輸出 PNG 格式，300 DPI
"""

import os, warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
warnings.filterwarnings('ignore')

# ─── 設定中文字體 ────────────────────────────────────────────
# macOS 上使用 PingFang TC（蘋方-繁）
CHINESE_FONT = '/System/Library/Fonts/STHeiti Medium.ttc'
if os.path.exists(CHINESE_FONT):
    font_manager.fontManager.addfont(CHINESE_FONT)
    zh_font = font_manager.FontProperties(fname=CHINESE_FONT)
else:
    zh_font = font_manager.FontProperties(family='sans-serif')

plt.rcParams['font.family'] = ['Heiti TC', 'PingFang TC', 'STHeiti', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

OUT = os.path.join(os.path.dirname(__file__), 'charts_zh')
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
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

SRC_FIN  = "資料來源：PDD Holdings 2026 年第一季度業績發布（2026年5月27日）；SEC Form 6-K"
SRC_EST  = "資料來源：Bloomberg 市場共識預估；PDD Holdings 2026 年第一季度業績發布"
SRC_MKTG = "資料來源：PDD Holdings 2026 年第一季度業績發布；分析師估算（2026年5月）"


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    kb = os.path.getsize(path) / 1024
    print(f"  ✓  {name}  ({kb:.0f} KB)")


def add_source(fig, text):
    fig.text(0.01, 0.005, text, fontsize=7, color='#7F8C8D', style='italic')


# ═══════════════════════════════════════════════════════════════════
# 資料
# ═══════════════════════════════════════════════════════════════════

QUARTERS = ['Q1\n2024', 'Q2\n2024', 'Q3\n2024', 'Q4\n2024',
            'Q1\n2025', 'Q2\n2025', 'Q3\n2025', 'Q4\n2025',
            'Q1\n2026']

# 季度營收（人民幣十億元）
total_rev  = [86.8, 97.1, 99.4, 120.8, 95.7, 104.2, 107.6, 113.4, 106.2]
oms_rev    = [47.0, 52.5, 53.0, 63.0, 48.7, 51.2, 52.8, 55.9, 49.9]
ts_rev     = [37.8, 42.5, 44.3, 55.8, 47.0, 51.0, 53.2, 55.8, 56.3]

# 利潤率（%）
gross_mgn  = [59.2, 57.8, 57.1, 55.4, 57.2, 56.8, 56.5, 55.9, 55.8]
op_mgn     = [24.2, 23.8, 22.5, 24.1, 16.8, 17.5, 18.2, 18.7, 18.5]
net_mgn    = [20.1, 20.5, 19.8, 20.3, 15.4, 14.8, 15.1, 14.9, 11.8]

# 非通用會計準則攤薄每股盈利（人民幣元）
nongaap_eps = [22.5, 23.8, 21.0, 22.4, 11.41, 11.80, 12.50, 12.80, 9.51]
gaap_eps    = [19.8, 21.2, 18.4, 19.8,  9.94, 10.20, 10.80, 11.00, 8.48]

# 營運開支拆解（人民幣十億元）
opex_labels = ['銷售\n成本', '銷售與\n行銷費用', '管理\n費用', '研發\n費用', '營業\n利潤']
opex_q1_25  = [40.9, 20.5,  3.8, 14.3, 16.1]
opex_q1_26  = [46.9, 22.4,  4.1, 13.2, 19.6]

# 共識預估 vs 實際
metrics_beatmiss   = ['營業收入\n（十億美元）', '非GAAP每股盈利\n（美元）']
consensus_vals     = [15.94, 2.13]
actual_vals        = [15.40, 1.38]
pct_diff           = [(a - c) / c * 100 for a, c in zip(actual_vals, consensus_vals)]

# 估算修訂
est_periods = ['Q2\n2026E', 'Q3\n2026E', 'Q4\n2026E', 'FY2026E', 'FY2027E']
rev_old = [109.0, 112.5, 127.0, 450.0, 510.0]
rev_new = [105.5, 108.0, 119.8, 432.0, 498.0]
eps_old = [12.8, 13.5, 15.2, 57.0, 72.0]
eps_new = [10.2, 11.0, 12.8, 45.0, 58.0]

# 同業估值比較
peers       = ['PDD\n（業績前）', 'PDD\n（業績後）', '阿里巴巴', '京東', '亞馬遜', 'Sea']
pe_fwd      = [16.7, 20.3, 9.8, 11.2, 35.4, 22.1]
ev_ebitda   = [11.2, 13.8,  6.5,  7.8, 18.2, 14.3]


# ═══════════════════════════════════════════════════════════════════
# 圖一：季度營收走勢
# ═══════════════════════════════════════════════════════════════════
def chart_01():
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
    ax.set_ylabel('營業收入（人民幣十億元）')
    ax.set_title('PDD Holdings — 季度營收走勢\n2024 年第一季度至 2026 年第一季度')
    ax.set_ylim(0, 145)
    ax.axvline(x=7.5, color=C['gray'], lw=1, ls='--', alpha=0.7)
    ax.text(7.6, 138, '本季實際 →', fontsize=8, color=C['orange'], fontweight='bold')

    hist_patch  = mpatches.Patch(color=C['blue'],   alpha=0.85, label='歷史實際/估算')
    actq_patch  = mpatches.Patch(color=C['orange'], alpha=0.85, label='Q1 2026 實際')
    ax.legend(handles=[hist_patch, actq_patch], loc='upper left')
    add_source(fig, SRC_FIN)
    save(fig, 'chart_01_季度營收走勢.png')


# ═══════════════════════════════════════════════════════════════════
# 圖二：分部營收拆解
# ═══════════════════════════════════════════════════════════════════
def chart_02():
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(QUARTERS))
    w = 0.65

    b1 = ax.bar(x, oms_rev, width=w, label='線上行銷服務收入',
                color=C['blue'], alpha=0.85)
    b2 = ax.bar(x, ts_rev, width=w, bottom=oms_rev, label='交易服務收入',
                color=C['orange'], alpha=0.85)

    for patch in [b1[-1], b2[-1]]:
        patch.set_edgecolor(C['navy'])
        patch.set_linewidth(2)

    ax.set_xticks(x)
    ax.set_xticklabels(QUARTERS)
    ax.set_ylabel('營業收入（人民幣十億元）')
    ax.set_title('PDD Holdings — 季度分部營收拆解\n交易服務收入佔比攀升至 53%')
    ax.set_ylim(0, 145)
    ax.axvline(x=7.5, color=C['gray'], lw=1, ls='--', alpha=0.7)

    ax.annotate('交易服務佔比：53%\n（年增 400 個基點）',
                xy=(8, 106.2), xytext=(6.5, 128),
                arrowprops=dict(arrowstyle='->', color=C['navy'], lw=1.5),
                fontsize=9, color=C['navy'], fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF9C4', edgecolor=C['gold']))

    ax.legend(loc='upper left')
    add_source(fig, SRC_FIN)
    save(fig, 'chart_02_分部營收拆解.png')


# ═══════════════════════════════════════════════════════════════════
# 圖三：每股盈利走勢
# ═══════════════════════════════════════════════════════════════════
def chart_03():
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(QUARTERS))

    ax.plot(x, nongaap_eps, 'o-', color=C['blue'], linewidth=2.5, markersize=7,
            label='非GAAP 攤薄每股盈利（人民幣元/每股ADS）', zorder=3)
    ax.plot(x, gaap_eps, 's--', color=C['orange'], linewidth=2, markersize=6,
            label='GAAP 攤薄每股盈利（人民幣元/每股ADS）', alpha=0.8, zorder=3)

    ax.scatter([8], [nongaap_eps[-1]], color=C['red'], s=100, zorder=5)
    ax.scatter([8], [gaap_eps[-1]],    color=C['red'], s=80,  zorder=5)

    ax.annotate(f'2026 Q1：人民幣 {nongaap_eps[-1]} 元\n年減 17%\n（遜共識預估 35%）',
                xy=(8, nongaap_eps[-1]),
                xytext=(6.0, 16),
                arrowprops=dict(arrowstyle='->', color=C['red'], lw=1.5),
                fontsize=9, color=C['red'], fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FDECEA', edgecolor=C['red']))

    ax.axvline(x=7.5, color=C['gray'], lw=1, ls='--', alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(QUARTERS)
    ax.set_ylabel('每股盈利（人民幣元/每股ADS）')
    ax.set_title('PDD Holdings — 季度每股盈利走勢（GAAP 與非GAAP）\n本季每股盈利大幅遜預期，反映管理層刻意加大投資力度')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 30)
    add_source(fig, SRC_FIN + '；Bloomberg 共識預估')
    save(fig, 'chart_03_每股盈利走勢.png')


# ═══════════════════════════════════════════════════════════════════
# 圖四：利潤率走勢
# ═══════════════════════════════════════════════════════════════════
def chart_04():
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(QUARTERS))

    ax.plot(x, gross_mgn, 'o-', color=C['blue'],   lw=2.5, ms=7, label='毛利率')
    ax.plot(x, op_mgn,   's-', color=C['orange'],  lw=2.5, ms=7, label='營業利潤率')
    ax.plot(x, net_mgn,  '^-', color=C['green'],   lw=2.5, ms=7, label='淨利率')

    for val, y_off, col in [(gross_mgn[-1], 1.5, C['blue']),
                             (op_mgn[-1],   1.5, C['orange']),
                             (net_mgn[-1], -2.5, C['green'])]:
        ax.annotate(f'{val:.1f}%', xy=(8, val), xytext=(8.15, val + y_off),
                    fontsize=9, color=col, fontweight='bold')

    ax.fill_between(x[4:], net_mgn[4:], net_mgn[4], alpha=0.1, color=C['red'])
    ax.annotate('淨利率\n年減 350 個基點',
                xy=(8, 11.8), xytext=(6.0, 7.5),
                arrowprops=dict(arrowstyle='->', color=C['red'], lw=1.2),
                fontsize=8.5, color=C['red'],
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FDECEA', edgecolor=C['red']))

    ax.axvline(x=7.5, color=C['gray'], lw=1, ls='--', alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(QUARTERS)
    ax.set_ylabel('利潤率（%）')
    ax.set_title('PDD Holdings — 季度利潤率走勢\n毛利率穩健；淨利率因投資加大而壓縮')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 70)
    add_source(fig, SRC_FIN)
    save(fig, 'chart_04_利潤率走勢.png')


# ═══════════════════════════════════════════════════════════════════
# 圖五：超預期/遜預期分析
# ═══════════════════════════════════════════════════════════════════
def chart_05():
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    for i, (ax, metric, cons, actual, pct) in enumerate(
            zip(axes, metrics_beatmiss, consensus_vals, actual_vals, pct_diff)):
        col = C['beat'] if pct >= 0 else C['miss']
        categories = ['市場共識\n預估', '實際\n結果']
        vals = [cons, actual]
        bar_cols = [C['gray'], col]
        bars = ax.bar(categories, vals, color=bar_cols, alpha=0.85, width=0.5)

        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02 * max(vals),
                    f'${val:.2f}',
                    ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.annotate('', xy=(1, actual), xytext=(1, cons),
                    arrowprops=dict(arrowstyle='->', color=col, lw=3))

        ax.text(1.25, (cons + actual) / 2,
                f'{pct:+.1f}%',
                ha='left', va='center', fontsize=16, fontweight='bold', color=col)

        ax.set_title(f'{metric}\n2026 Q1 實際 vs Bloomberg 共識', fontweight='bold')
        ax.set_ylim(0, max(vals) * 1.35)
        ax.set_ylabel('美元')
        ax.grid(axis='y', alpha=0.4)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        label = '超預期' if pct >= 0 else '遜預期'
        ax.text(0.5, 0.92, label, transform=ax.transAxes,
                ha='center', fontsize=18, fontweight='bold', color=col,
                bbox=dict(boxstyle='round,pad=0.4', facecolor=col + '22', edgecolor=col, lw=2))

    fig.suptitle('PDD Holdings 2026 年第一季度 — 超預期/遜預期摘要', fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    add_source(fig, SRC_EST)
    save(fig, 'chart_05_超預期遜預期摘要.png')


# ═══════════════════════════════════════════════════════════════════
# 圖六：營收年增率
# ═══════════════════════════════════════════════════════════════════
def chart_06():
    fig, ax = plt.subplots(figsize=(12, 6))
    growth_qtrs = QUARTERS[4:]
    growth_vals = [10.3, 7.3, 8.2, -6.1, 11.0]
    cols = [C['green'] if v >= 0 else C['red'] for v in growth_vals]
    bars = ax.bar(growth_qtrs, growth_vals, color=cols, alpha=0.85)
    bars[-1].set_edgecolor(C['navy'])
    bars[-1].set_linewidth(2.5)

    for bar, val in zip(bars, growth_vals):
        va = 'bottom' if val >= 0 else 'top'
        offset = 0.3 if val >= 0 else -0.3
        ax.text(bar.get_x() + bar.get_width()/2, val + offset,
                f'{val:+.1f}%', ha='center', va=va, fontsize=10, fontweight='bold')

    ax.axhline(0, color='black', lw=0.8)
    ax.set_ylabel('營收年增率（%）')
    ax.set_title('PDD Holdings — 季度營收年增率走勢\n2025 Q1 至 2026 Q1（先減速後回升）')
    ax.set_ylim(-12, 20)

    ax.annotate('共識預估：+21%\n實際達成：+11%',
                xy=(4, 11.0), xytext=(2.5, 17),
                arrowprops=dict(arrowstyle='->', color=C['red'], lw=1.5),
                fontsize=9, color=C['red'], fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FDECEA', edgecolor=C['red']))

    add_source(fig, SRC_FIN + '；Bloomberg 共識預估')
    save(fig, 'chart_06_營收年增率.png')


# ═══════════════════════════════════════════════════════════════════
# 圖七：營運開支對比
# ═══════════════════════════════════════════════════════════════════
def chart_07():
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(opex_labels))
    w = 0.35

    bars1 = ax.bar(x - w/2, opex_q1_25, width=w, label='2025 Q1', color=C['blue'],   alpha=0.75)
    bars2 = ax.bar(x + w/2, opex_q1_26, width=w, label='2026 Q1', color=C['orange'], alpha=0.85)

    for bar in bars2:
        bar.set_edgecolor(C['navy'])
        bar.set_linewidth(1.5)

    for bars, vals in [(bars1, opex_q1_25), (bars2, opex_q1_26)]:
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    for i, (v25, v26) in enumerate(zip(opex_q1_25, opex_q1_26)):
        chg = (v26 - v25) / v25 * 100
        col = C['red'] if (i < 4 and chg > 0) else C['green']
        if i == 4:
            col = C['green'] if chg > 0 else C['red']
        ax.text(i, max(v25, v26) + 1.5, f'{chg:+.0f}%',
                ha='center', fontsize=9, color=col, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(opex_labels)
    ax.set_ylabel('人民幣十億元')
    ax.set_title('PDD Holdings — 損益表瀑布圖：2025 Q1 vs 2026 Q1\n成本通膨高於營收增速，但營業利潤仍年增 22%')
    ax.legend()
    ax.set_ylim(0, 58)
    add_source(fig, SRC_FIN)
    save(fig, 'chart_07_營運開支對比.png')


# ═══════════════════════════════════════════════════════════════════
# 圖八：估算修訂
# ═══════════════════════════════════════════════════════════════════
def chart_08():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    x = np.arange(len(est_periods))
    w = 0.35

    b1 = ax1.bar(x - w/2, rev_old, width=w, label='原估算', color=C['blue'],  alpha=0.75)
    b2 = ax1.bar(x + w/2, rev_new, width=w, label='新估算', color=C['orange'], alpha=0.85)
    for bars, vals in [(b1, rev_old), (b2, rev_new)]:
        for bar, val in zip(bars, vals):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                     f'{val:.0f}', ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(est_periods)
    ax1.set_ylabel('營收（人民幣十億元）')
    ax1.set_title('營收估算修訂\n（人民幣十億元）', fontweight='bold')
    ax1.legend()
    ax1.set_ylim(0, 620)

    for i, (old, new) in enumerate(zip(rev_old, rev_new)):
        chg = (new - old) / old * 100
        ax1.text(i, max(old, new) + 12, f'{chg:+.1f}%',
                 ha='center', fontsize=9, color=C['red'], fontweight='bold')

    b3 = ax2.bar(x - w/2, eps_old, width=w, label='原估算', color=C['blue'],   alpha=0.75)
    b4 = ax2.bar(x + w/2, eps_new, width=w, label='新估算', color=C['orange'], alpha=0.85)
    for bars, vals in [(b3, eps_old), (b4, eps_new)]:
        for bar, val in zip(bars, vals):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                     f'{val:.0f}', ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(est_periods)
    ax2.set_ylabel('非GAAP攤薄每股盈利（人民幣元/每股ADS）')
    ax2.set_title('非GAAP 每股盈利估算修訂\n（人民幣元/每股ADS）', fontweight='bold')
    ax2.legend()
    ax2.set_ylim(0, 88)

    for i, (old, new) in enumerate(zip(eps_old, eps_new)):
        chg = (new - old) / old * 100
        ax2.text(i, max(old, new) + 1.5, f'{chg:+.1f}%',
                 ha='center', fontsize=9, color=C['red'], fontweight='bold')

    fig.suptitle('PDD Holdings — 2026 Q1 業績後估算修訂', fontsize=13, fontweight='bold')
    plt.tight_layout()
    add_source(fig, SRC_MKTG)
    save(fig, 'chart_08_估算修訂.png')


# ═══════════════════════════════════════════════════════════════════
# 圖九：同業估值比較
# ═══════════════════════════════════════════════════════════════════
def chart_09():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    x = np.arange(len(peers))
    bar_cols = [C['gray'], C['orange'], C['blue'], C['teal'], C['purple'], C['green']]

    bars1 = ax1.bar(x, pe_fwd, color=bar_cols, alpha=0.85, zorder=2)
    bars1[1].set_edgecolor(C['navy'])
    bars1[1].set_linewidth(2)

    for bar, val in zip(bars1, pe_fwd):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.3,
                 f'{val:.1f}倍', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax1.set_xticks(x)
    ax1.set_xticklabels(peers, fontsize=9)
    ax1.set_ylabel('預期本益比（2026 財年估算）')
    ax1.set_title('預期本益比：PDD 與同業比較\n業績後估值水平')
    ax1.set_ylim(0, 45)

    bars2 = ax2.bar(x, ev_ebitda, color=bar_cols, alpha=0.85, zorder=2)
    bars2[1].set_edgecolor(C['navy'])
    bars2[1].set_linewidth(2)

    for bar, val in zip(bars2, ev_ebitda):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.2,
                 f'{val:.1f}倍', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax2.set_xticks(x)
    ax2.set_xticklabels(peers, fontsize=9)
    ax2.set_ylabel('企業價值/息稅折舊攤銷前盈利（2026E）')
    ax2.set_title('EV/EBITDA：PDD 與同業比較\n短期盈利受抑導致估值折讓擴大')
    ax2.set_ylim(0, 25)

    fig.suptitle('PDD Holdings — 業績後同業估值比較', fontsize=13, fontweight='bold')
    plt.tight_layout()
    add_source(fig, '資料來源：Bloomberg；分析師估算（2026年5月）；PDD Holdings 2026 Q1 業績發布')
    save(fig, 'chart_09_同業估值比較.png')


# ═══════════════════════════════════════════════════════════════════
# 圖十：目標股價情境分析
# ═══════════════════════════════════════════════════════════════════
def chart_10():
    fig, ax = plt.subplots(figsize=(11, 6))

    scenarios  = ['悲觀情境', '基本情境\n（新目標股價）', '樂觀情境', '原目標股價\n（業績前）']
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

    ax.axvline(x=86, color=C['blue'], lw=2.5, ls='--', label='現價（約 $86）')
    ax.text(87, 3.6, '現價\n約 $86', fontsize=8.5, color=C['blue'], fontweight='bold')

    ax.set_yticks(y)
    ax.set_yticklabels(scenarios, fontsize=11)
    ax.set_xlabel('目標股價（美元/每股ADS）')
    ax.set_title('PDD Holdings — 目標股價情境分析\n新基本情境目標股價：$125（由 $165 下修）；維持買入評級',
                 fontweight='bold')
    ax.set_xlim(0, 200)

    descs = [
        '每股盈利持續遜預期；\nTemu 關稅逆風加劇',
        '投資週期見頂；\nFY2027E 復甦',
        '利潤率復甦快於預期',
        '業績前估算\n（原首次覆蓋目標股價）'
    ]
    for i, desc in enumerate(descs):
        ax.text(2, i, desc, va='center', fontsize=7.5,
                color='white' if i != 3 else C['gray'],
                fontweight='bold' if i == 1 else 'normal')

    upside = ((125 - 86) / 86) * 100
    ax.text(127, 1, f'+{upside:.0f}% 潛在升幅\n（至基本情境目標股價）',
            fontsize=9, color=C['orange'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF3CD', edgecolor=C['gold']))

    ax.legend(loc='lower right')
    add_source(fig, '資料來源：分析師估算；PDD Holdings 2026 Q1 業績發布（2026年5月27日）')
    save(fig, 'chart_10_目標股價情境分析.png')


if __name__ == '__main__':
    print("開始生成 PDD Holdings 2026 Q1 盈利更新報告圖表（繁體中文版）...")
    chart_01()
    chart_02()
    chart_03()
    chart_04()
    chart_05()
    chart_06()
    chart_07()
    chart_08()
    chart_09()
    chart_10()
    print("\n10 張繁中圖表全部生成完畢。")
