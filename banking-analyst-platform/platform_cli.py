#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""對公分析師自動化工作平台 CLI。

用法：
    python3 platform_cli.py analyze data/sample_company.json      # 財務比率分析
    python3 platform_cli.py memo data/sample_company.json         # 授信報告初稿
    python3 platform_cli.py monitor data/sample_company.json      # 貸後監控檢核
    python3 platform_cli.py all data/sample_company.json          # 以上全部
    python3 platform_cli.py init-template data/new_client.json    # 產生空白客戶資料檔

輸出檔案預設寫入 output/，可用 -o 指定其他目錄。
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from modules import credit_memo, financial_analysis, loan_monitoring


def load_data(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_report(out_dir, filename, content):
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def short_name(data):
    """取公司名稱前 8 個字作為輸出檔名前綴，避免檔名過長。"""
    return data["company"]["name"][:8].replace("／", "-").replace("/", "-")


def cmd_analyze(data, out_dir, today):
    analysis = financial_analysis.analyze(data)
    report = financial_analysis.render_markdown(data, analysis, today)
    path = write_report(out_dir, f"{short_name(data)}_財務分析_{today}.md", report)
    print(f"✅ 財務分析報告：{path}")
    print("\n重點評述：")
    for note in analysis["commentary"]:
        print(f"  - {note}")
    return analysis


def cmd_memo(data, out_dir, today, analysis=None):
    analysis = analysis or financial_analysis.analyze(data)
    memo = credit_memo.generate(data, analysis, today)
    path = write_report(out_dir, f"{short_name(data)}_授信報告初稿_{today}.md", memo)
    print(f"✅ 授信報告初稿：{path}")
    print("   （標示【請分析師補充】處需人工完成）")
    return analysis


def cmd_monitor(data, out_dir, today, analysis=None):
    analysis = analysis or financial_analysis.analyze(data)
    covenants = loan_monitoring.check_covenants(data, analysis)
    alerts = loan_monitoring.builtin_alerts(data, analysis)
    level = loan_monitoring.overall_level(covenants, alerts)
    report = loan_monitoring.render_markdown(data, analysis, covenants, alerts, today)
    path = write_report(out_dir, f"{short_name(data)}_貸後監控_{today}.md", report)
    icon = {"紅": "🔴", "黃": "🟡", "綠": "🟢"}[level]
    print(f"✅ 貸後監控報告：{path}")
    print(f"   綜合燈號：{icon} {level}燈"
          f"（covenant {sum(1 for c in covenants if c['passed'])}/{len(covenants)} 符合、"
          f"預警 {len(alerts)} 項）")
    for a in alerts:
        print(f"   - {a['level']}燈：{a['message']}")
    return analysis


def cmd_init_template(target):
    """產生空白客戶資料檔，欄位與範例檔相同、數字留空。"""
    sample_path = Path(__file__).resolve().parent / "data" / "sample_company.json"
    sample = load_data(sample_path)
    blank = {
        "company": {k: ("" if not isinstance(v, (int, float)) else None)
                    for k, v in sample["company"].items()},
        "application": {k: "" for k in sample["application"]},
        "financials": {
            "unit": "新台幣仟元",
            "years": {
                "YYYY": {k: None for k in financial_analysis.REQUIRED_FIELDS}
            },
        },
        "covenants": [],
    }
    target = Path(target)
    if target.exists():
        print(f"❌ {target} 已存在，不覆蓋。")
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(blank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ 已產生空白客戶資料檔：{target}")
    print("   請填入財務數字（欄位說明見 README.md），年度鍵值 YYYY 改為實際年度，可自行增加多個年度。")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="對公分析師自動化工作平台")
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text in [
        ("analyze", "財務比率分析報告"),
        ("memo", "授信報告初稿"),
        ("monitor", "貸後監控檢核報告"),
        ("all", "一次產出全部報告"),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("data_file", help="客戶資料 JSON 檔路徑")
        p.add_argument("-o", "--output", default=None, help="輸出目錄（預設為平台目錄下 output/）")

    p_init = sub.add_parser("init-template", help="產生空白客戶資料檔")
    p_init.add_argument("target", help="要建立的 JSON 檔路徑，例如 data/new_client.json")

    args = parser.parse_args(argv)

    if args.command == "init-template":
        return cmd_init_template(args.target)

    data = load_data(args.data_file)
    out_dir = Path(args.output) if args.output else Path(__file__).resolve().parent / "output"
    today = datetime.date.today().isoformat()

    print(f"客戶：{data['company']['name']}")
    if args.command == "analyze":
        cmd_analyze(data, out_dir, today)
    elif args.command == "memo":
        cmd_memo(data, out_dir, today)
    elif args.command == "monitor":
        cmd_monitor(data, out_dir, today)
    elif args.command == "all":
        analysis = cmd_analyze(data, out_dir, today)
        cmd_memo(data, out_dir, today, analysis)
        cmd_monitor(data, out_dir, today, analysis)
    return 0


if __name__ == "__main__":
    sys.exit(main())
