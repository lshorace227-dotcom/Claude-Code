# -*- coding: utf-8 -*-
"""財務報表分析模組：計算授信常用財務比率並產生自動評述。

輸入資料格式見 data/sample_company.json，金額單位由資料檔 financials.unit 指定。
"""

# 各年度財務資料必填欄位（缺漏時該比率顯示 N/A，不會中斷）
REQUIRED_FIELDS = {
    "revenue": "營業收入",
    "cogs": "營業成本",
    "operating_expenses": "營業費用",
    "interest_expense": "利息費用",
    "pretax_income": "稅前淨利",
    "net_income": "稅後淨利",
    "cash": "現金及約當現金",
    "accounts_receivable": "應收帳款",
    "inventory": "存貨",
    "current_assets": "流動資產",
    "total_assets": "資產總額",
    "current_liabilities": "流動負債",
    "total_liabilities": "負債總額",
    "short_term_debt": "短期借款",
    "long_term_debt": "長期借款",
    "accounts_payable": "應付帳款",
    "equity": "股東權益",
    "operating_cash_flow": "營業活動現金流量",
}

# 比率定義：key、中文名稱、單位、分類（依授信報告慣用順序排列）
RATIO_DEFS = [
    ("debt_ratio", "負債比率", "%", "財務結構"),
    ("borrowing_dependence", "借款依存度", "%", "財務結構"),
    ("current_ratio", "流動比率", "倍", "償債能力"),
    ("quick_ratio", "速動比率", "倍", "償債能力"),
    ("interest_coverage", "利息保障倍數", "倍", "償債能力"),
    ("dso", "應收帳款週轉天數", "天", "經營效率"),
    ("dio", "存貨週轉天數", "天", "經營效率"),
    ("dpo", "應付帳款週轉天數", "天", "經營效率"),
    ("ccc", "現金轉換循環", "天", "經營效率"),
    ("asset_turnover", "總資產週轉率", "次", "經營效率"),
    ("gross_margin", "毛利率", "%", "獲利能力"),
    ("operating_margin", "營業利益率", "%", "獲利能力"),
    ("net_margin", "純益率", "%", "獲利能力"),
    ("roa", "資產報酬率(ROA)", "%", "獲利能力"),
    ("roe", "股東權益報酬率(ROE)", "%", "獲利能力"),
    ("ocf_to_current_liab", "營業現金流量對流動負債比", "%", "現金流量"),
    ("ocf_to_debt", "營業現金流量對借款比", "%", "現金流量"),
    ("revenue_growth", "營收成長率", "%", "成長性"),
    ("net_income_growth", "淨利成長率", "%", "成長性"),
]


def safe_div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def compute_ratios(cur, prev=None):
    """計算單一年度的全部比率。cur/prev 為該年度財務資料 dict。"""
    g = cur.get
    revenue = g("revenue")
    cogs = g("cogs")
    opex = g("operating_expenses")
    gross = revenue - cogs if None not in (revenue, cogs) else None
    op_income = gross - opex if None not in (gross, opex) else None
    borrowings = (g("short_term_debt") or 0) + (g("long_term_debt") or 0)

    r = {}
    r["debt_ratio"] = pct(safe_div(g("total_liabilities"), g("total_assets")))
    r["borrowing_dependence"] = pct(safe_div(borrowings, g("total_assets")))
    r["current_ratio"] = safe_div(g("current_assets"), g("current_liabilities"))
    quick_assets = None
    if None not in (g("current_assets"), g("inventory")):
        quick_assets = g("current_assets") - g("inventory")
    r["quick_ratio"] = safe_div(quick_assets, g("current_liabilities"))
    ebit = None
    if None not in (g("pretax_income"), g("interest_expense")):
        ebit = g("pretax_income") + g("interest_expense")
    r["interest_coverage"] = safe_div(ebit, g("interest_expense"))
    r["dso"] = days(safe_div(g("accounts_receivable"), revenue))
    r["dio"] = days(safe_div(g("inventory"), cogs))
    r["dpo"] = days(safe_div(g("accounts_payable"), cogs))
    if None not in (r["dso"], r["dio"], r["dpo"]):
        r["ccc"] = r["dso"] + r["dio"] - r["dpo"]
    else:
        r["ccc"] = None
    r["asset_turnover"] = safe_div(revenue, g("total_assets"))
    r["gross_margin"] = pct(safe_div(gross, revenue))
    r["operating_margin"] = pct(safe_div(op_income, revenue))
    r["net_margin"] = pct(safe_div(g("net_income"), revenue))
    r["roa"] = pct(safe_div(g("net_income"), g("total_assets")))
    r["roe"] = pct(safe_div(g("net_income"), g("equity")))
    r["ocf_to_current_liab"] = pct(safe_div(g("operating_cash_flow"), g("current_liabilities")))
    r["ocf_to_debt"] = pct(safe_div(g("operating_cash_flow"), borrowings))
    if prev:
        r["revenue_growth"] = growth(revenue, prev.get("revenue"))
        r["net_income_growth"] = growth(g("net_income"), prev.get("net_income"))
    else:
        r["revenue_growth"] = None
        r["net_income_growth"] = None
    return r


def pct(x):
    return x * 100 if x is not None else None


def days(x):
    return x * 365 if x is not None else None


def growth(cur, prev):
    if cur is None or prev is None or prev == 0:
        return None
    return (cur - prev) / abs(prev) * 100


def analyze(data):
    """對客戶資料進行完整分析。回傳 {years, ratios, commentary}。"""
    fin = data["financials"]["years"]
    years = sorted(fin.keys())
    ratios = {}
    prev = None
    for y in years:
        ratios[y] = compute_ratios(fin[y], prev)
        prev = fin[y]
    commentary = build_commentary(years, fin, ratios)
    return {"years": years, "ratios": ratios, "commentary": commentary}


def build_commentary(years, fin, ratios):
    """依比率趨勢產生規則式自動評述（授信報告初稿用語）。"""
    notes = []
    first, last = years[0], years[-1]
    n = len(years)

    rev_f, rev_l = fin[first].get("revenue"), fin[last].get("revenue")
    if rev_f and rev_l and n >= 2:
        cagr = ((rev_l / rev_f) ** (1 / (n - 1)) - 1) * 100
        trend = "成長" if rev_l >= rev_f else "衰退"
        notes.append(
            f"近{n}年營收自 {fmt_amount(rev_f)} {trend}至 {fmt_amount(rev_l)}，"
            f"年複合成長率約 {cagr:+.1f}%。"
        )

    margins = [ratios[y].get("operating_margin") for y in years]
    if all(m is not None for m in margins) and n >= 3:
        if all(margins[i] > margins[i + 1] for i in range(n - 1)):
            notes.append(
                f"營業利益率由 {margins[0]:.1f}% 逐年下滑至 {margins[-1]:.1f}%，"
                "獲利能力呈連續下滑趨勢，宜了解成本結構或售價變化原因。"
            )
        elif all(margins[i] < margins[i + 1] for i in range(n - 1)):
            notes.append(
                f"營業利益率由 {margins[0]:.1f}% 逐年提升至 {margins[-1]:.1f}%，獲利能力持續改善。"
            )

    dr = ratios[last].get("debt_ratio")
    if dr is not None:
        if dr > 60:
            level = "偏高，財務槓桿較重"
        elif dr > 40:
            level = "尚屬適中"
        else:
            level = "穩健"
        notes.append(f"最近年度負債比率 {dr:.1f}%，財務結構{level}。")

    cr = ratios[last].get("current_ratio")
    if cr is not None:
        if cr < 1:
            level = "不足 1 倍，短期償債能力偏弱"
        elif cr < 1.5:
            level = "尚可"
        else:
            level = "良好"
        notes.append(f"流動比率 {cr:.2f} 倍，短期流動性{level}。")

    ic = ratios[last].get("interest_coverage")
    if ic is not None:
        if ic < 2:
            level = "偏弱，付息能力承壓"
        elif ic < 5:
            level = "尚可"
        else:
            level = "充裕"
        notes.append(f"利息保障倍數 {ic:.1f} 倍，付息能力{level}。")

    ocf_l = fin[last].get("operating_cash_flow")
    if ocf_l is not None and ocf_l < 0:
        notes.append("最近年度營業活動現金流量為負數，營運資金依賴外部融資，請留意。")

    dso_series = [ratios[y].get("dso") for y in years]
    if None not in dso_series and n >= 2 and dso_series[0] and dso_series[-1] > dso_series[0] * 1.15:
        notes.append(
            f"應收帳款週轉天數由 {dso_series[0]:.0f} 天延長至 {dso_series[-1]:.0f} 天，"
            "收款期間拉長，宜了解客戶收款政策或下游景氣變化。"
        )
    return notes


def fmt_amount(x):
    if x is None:
        return "N/A"
    return f"{x:,.0f}"


def fmt_ratio(value, unit):
    if value is None:
        return "N/A"
    if unit == "%":
        return f"{value:.1f}%"
    if unit == "倍":
        return f"{value:.2f}"
    if unit == "天":
        return f"{value:.0f}"
    if unit == "次":
        return f"{value:.2f}"
    return f"{value:.2f}"


def render_ratio_table(analysis):
    """比率分析 Markdown 表格（列 = 比率、欄 = 年度）。"""
    years = analysis["years"]
    lines = []
    lines.append("| 分類 | 項目 | 單位 | " + " | ".join(years) + " |")
    lines.append("|---|---|---|" + "---|" * len(years))
    for key, label, unit, category in RATIO_DEFS:
        cells = [fmt_ratio(analysis["ratios"][y].get(key), unit) for y in years]
        lines.append(f"| {category} | {label} | {unit} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_financial_summary_table(data, analysis):
    """主要財務數字摘要表。"""
    years = analysis["years"]
    fin = data["financials"]["years"]
    rows = [
        ("revenue", "營業收入"),
        ("net_income", "稅後淨利"),
        ("total_assets", "資產總額"),
        ("total_liabilities", "負債總額"),
        ("equity", "股東權益"),
        ("operating_cash_flow", "營業活動現金流量"),
    ]
    lines = []
    lines.append("| 項目 | " + " | ".join(years) + " |")
    lines.append("|---|" + "---|" * len(years))
    for key, label in rows:
        cells = [fmt_amount(fin[y].get(key)) for y in years]
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_markdown(data, analysis, generated_date):
    """完整財務分析報告（Markdown）。"""
    company = data["company"]
    unit = data["financials"].get("unit", "")
    parts = [
        f"# 財務分析報告：{company['name']}",
        "",
        f"- 產業別：{company.get('industry', 'N/A')}",
        f"- 分析年度：{analysis['years'][0]} ~ {analysis['years'][-1]}",
        f"- 金額單位：{unit}",
        f"- 報告產生日期：{generated_date}",
        "",
        "## 一、主要財務數字",
        "",
        render_financial_summary_table(data, analysis),
        "",
        "## 二、財務比率分析",
        "",
        render_ratio_table(analysis),
        "",
        "## 三、自動評述（初稿，請分析師覆核）",
        "",
    ]
    for note in analysis["commentary"]:
        parts.append(f"- {note}")
    if not analysis["commentary"]:
        parts.append("- （無自動評述）")
    parts.append("")
    return "\n".join(parts)
