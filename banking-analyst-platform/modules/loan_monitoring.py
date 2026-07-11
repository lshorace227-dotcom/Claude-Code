# -*- coding: utf-8 -*-
"""貸後監控模組：財務契約條款（covenant）檢核 + 內建財務預警規則。

- covenant 檢核：依客戶資料檔 covenants 欄位逐條檢查最近年度數值
- 內建預警：不需設定，依通用授信經驗規則對最近年度與趨勢做紅／黃燈檢查
"""

from . import financial_analysis as fa

OPERATORS = {
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
}

RATIO_UNITS = {key: unit for key, _, unit, _ in fa.RATIO_DEFS}
RATIO_LABELS = {key: label for key, label, _, _ in fa.RATIO_DEFS}


def check_covenants(data, analysis):
    """逐條檢核契約財務條款，回傳 [{name, actual, threshold, operator, passed}]。"""
    latest = analysis["years"][-1]
    ratios = analysis["ratios"][latest]
    results = []
    for cov in data.get("covenants", []):
        metric = cov["metric"]
        actual = ratios.get(metric)
        op = cov["operator"]
        threshold = cov["threshold"]
        passed = None
        if actual is not None and op in OPERATORS:
            passed = OPERATORS[op](actual, threshold)
        results.append({
            "name": cov.get("name") or RATIO_LABELS.get(metric, metric),
            "metric": metric,
            "actual": actual,
            "operator": op,
            "threshold": threshold,
            "passed": passed,
        })
    return results


def builtin_alerts(data, analysis):
    """內建紅／黃燈預警規則，回傳 [{level, message}]，level 為「紅」或「黃」。"""
    years = analysis["years"]
    fin = data["financials"]["years"]
    latest = years[-1]
    prev = years[-2] if len(years) >= 2 else None
    r_last = analysis["ratios"][latest]
    alerts = []

    def add(level, message):
        alerts.append({"level": level, "message": message})

    ni_last = fin[latest].get("net_income")
    ni_prev = fin[prev].get("net_income") if prev else None
    if ni_last is not None and ni_last < 0:
        if ni_prev is not None and ni_prev < 0:
            add("紅", f"連續兩年稅後虧損（{prev} 年 {fa.fmt_amount(ni_prev)}、{latest} 年 {fa.fmt_amount(ni_last)}）。")
        else:
            add("黃", f"最近年度稅後虧損 {fa.fmt_amount(ni_last)}。")

    ic = r_last.get("interest_coverage")
    if ic is not None:
        if ic < 1:
            add("紅", f"利息保障倍數 {ic:.2f} 倍，低於 1 倍，獲利不足以支應利息。")
        elif ic < 2:
            add("黃", f"利息保障倍數 {ic:.2f} 倍，低於 2 倍，付息能力偏弱。")

    cr = r_last.get("current_ratio")
    if cr is not None and cr < 1:
        add("紅", f"流動比率 {cr:.2f} 倍，低於 1 倍，短期償債能力不足。")

    dr = r_last.get("debt_ratio")
    if dr is not None and dr > 65:
        add("黃", f"負債比率 {dr:.1f}%，高於 65%，財務槓桿偏高。")

    rg = r_last.get("revenue_growth")
    if rg is not None and rg < -10:
        add("黃", f"最近年度營收衰退 {rg:.1f}%，衰退幅度逾 10%。")

    ocf_last = fin[latest].get("operating_cash_flow")
    ocf_prev = fin[prev].get("operating_cash_flow") if prev else None
    if ocf_last is not None and ocf_last < 0:
        if ocf_prev is not None and ocf_prev < 0:
            add("紅", "連續兩年營業活動現金流量為負數，營運高度依賴外部資金。")
        else:
            add("黃", "最近年度營業活動現金流量為負數。")

    ocf_cl = r_last.get("ocf_to_current_liab")
    if ocf_cl is not None and 0 <= ocf_cl < 10:
        add("黃", f"營業現金流量對流動負債比 {ocf_cl:.1f}%，低於 10%，現金流量對短期債務的覆蓋偏低。")

    if prev:
        r_prev = analysis["ratios"][prev]
        for key, label in (("dso", "應收帳款週轉天數"), ("dio", "存貨週轉天數")):
            cur_v, prev_v = r_last.get(key), r_prev.get(key)
            if cur_v is not None and prev_v and cur_v > prev_v * 1.2:
                add("黃", f"{label}由 {prev_v:.0f} 天增至 {cur_v:.0f} 天，年增逾 20%，宜查明原因。")

    if len(years) >= 3:
        margins = [analysis["ratios"][y].get("operating_margin") for y in years[-3:]]
        if all(m is not None for m in margins) and margins[0] > margins[1] > margins[2]:
            add("黃", f"營業利益率連續兩年下滑（{margins[0]:.1f}% → {margins[1]:.1f}% → {margins[2]:.1f}%）。")

    return alerts


def overall_level(covenant_results, alerts):
    """綜合燈號：紅（有紅燈或違約條款）＞黃（有黃燈）＞綠。"""
    if any(c["passed"] is False for c in covenant_results) or any(a["level"] == "紅" for a in alerts):
        return "紅"
    if any(a["level"] == "黃" for a in alerts):
        return "黃"
    return "綠"


def render_markdown(data, analysis, covenant_results, alerts, generated_date):
    """貸後監控檢核報告（Markdown）。"""
    company = data["company"]
    latest = analysis["years"][-1]
    level = overall_level(covenant_results, alerts)
    icon = {"紅": "🔴", "黃": "🟡", "綠": "🟢"}[level]

    parts = [
        f"# 貸後監控檢核報告：{company['name']}",
        "",
        f"- 檢核基準年度：{latest}",
        f"- 報告產生日期：{generated_date}",
        f"- **綜合燈號：{icon} {level}燈**",
        "",
        "## 一、財務契約條款（Covenant）檢核",
        "",
    ]
    if covenant_results:
        parts.append("| 條款 | 約定 | 實際值 | 結果 |")
        parts.append("|---|---|---|---|")
        for c in covenant_results:
            unit = RATIO_UNITS.get(c["metric"], "")
            actual = fa.fmt_ratio(c["actual"], unit)
            threshold = fa.fmt_ratio(c["threshold"], unit)
            if c["passed"] is None:
                result = "⚪ 無法檢核（缺資料）"
            elif c["passed"]:
                result = "✅ 符合"
            else:
                result = "❌ 違反"
            parts.append(f"| {c['name']} | {c['operator']} {threshold} | {actual} | {result} |")
    else:
        parts.append("（本客戶未設定財務契約條款）")
    parts += ["", "## 二、內建財務預警檢查", ""]
    if alerts:
        for a in alerts:
            icon_a = "🔴" if a["level"] == "紅" else "🟡"
            parts.append(f"- {icon_a} **{a['level']}燈**：{a['message']}")
    else:
        parts.append("- 🟢 未觸發任何內建預警規則。")
    parts += [
        "",
        "## 三、後續處理建議",
        "",
        _suggestion(level),
        "",
    ]
    return "\n".join(parts)


def _suggestion(level):
    if level == "紅":
        return ("觸發紅燈警訊：建議即刻洽借款戶了解狀況，評估是否提列觀察名單、"
                "調整額度或增提擔保，並依行內規定陳報主管。")
    if level == "黃":
        return ("觸發黃燈警訊：建議於例行貸後檢視時向借款戶查證原因，"
                "並於下次覆審報告中敘明追蹤情形。")
    return "各項檢核均正常，維持例行貸後管理頻率即可。"
