# -*- coding: utf-8 -*-
"""授信報告產生模組：套用 templates/credit_memo_template.md 產出授信審查報告初稿。"""

from pathlib import Path

from . import financial_analysis as fa
from . import loan_monitoring as lm

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "credit_memo_template.md"


def _risk_flags_text(data, analysis):
    """風險評估段落：引用貸後監控之預警結果作為初稿要點。"""
    alerts = lm.builtin_alerts(data, analysis)
    if not alerts:
        return "- 依最近年度財務資料，未觸發內建財務預警規則。"
    lines = ["依財務資料自動檢查，下列事項宜於報告中評估："]
    for a in alerts:
        lines.append(f"- （{a['level']}燈）{a['message']}")
    return "\n".join(lines)


def generate(data, analysis, generated_date, template_path=None):
    """產生授信報告初稿（Markdown 字串）。"""
    template = Path(template_path or TEMPLATE_PATH).read_text(encoding="utf-8")
    company = data["company"]
    app = data.get("application", {})
    unit = data["financials"].get("unit", "")
    latest = analysis["years"][-1]
    latest_ocf = data["financials"]["years"][latest].get("operating_cash_flow")

    commentary = "\n".join(f"- {n}" for n in analysis["commentary"]) or "- （無自動評述）"

    ctx = {
        "company_name": company.get("name", "N/A"),
        "tax_id": company.get("tax_id", "N/A"),
        "established": company.get("established", "N/A"),
        "chairman": company.get("chairman", "N/A"),
        "capital_fmt": f"{fa.fmt_amount(company.get('capital'))} {unit}" if company.get("capital") else "N/A",
        "employees": company.get("employees", "N/A"),
        "industry": company.get("industry", "N/A"),
        "relationship_since": company.get("relationship_since", "N/A"),
        "rating": company.get("credit_rating_internal", "N/A"),
        "business_description": company.get("business_description", "【請分析師補充】"),
        "facility_type": app.get("facility_type", "【請分析師補充】"),
        "amount_fmt": f"{fa.fmt_amount(app.get('amount'))} {unit}" if app.get("amount") else "【請分析師補充】",
        "tenor": app.get("tenor", "【請分析師補充】"),
        "purpose": app.get("purpose", "【請分析師補充】"),
        "collateral": app.get("collateral", "【請分析師補充】"),
        "guarantors": app.get("guarantors", "【請分析師補充】"),
        "pricing": app.get("pricing", "【請分析師補充】"),
        "financial_unit": unit,
        "financial_summary_table": fa.render_financial_summary_table(data, analysis),
        "financial_ratio_table": fa.render_ratio_table(analysis),
        "financial_commentary": commentary,
        "latest_year": latest,
        "latest_ocf": f"{fa.fmt_amount(latest_ocf)} {unit}" if latest_ocf is not None else "N/A",
        "risk_flags": _risk_flags_text(data, analysis),
        "generated_date": generated_date,
    }
    return template.format(**ctx)
