# -*- coding: utf-8 -*-
"""平台核心邏輯測試：python3 -m unittest discover tests -v"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules import credit_memo, financial_analysis as fa, loan_monitoring as lm

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_company.json"


def load_sample():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


class TestFinancialAnalysis(unittest.TestCase):
    def setUp(self):
        self.data = load_sample()
        self.analysis = fa.analyze(self.data)

    def test_ratios_2025(self):
        r = self.analysis["ratios"]["2025"]
        self.assertAlmostEqual(r["debt_ratio"], 682000 / 1150000 * 100, places=4)
        self.assertAlmostEqual(r["current_ratio"], 520000 / 388000, places=4)
        self.assertAlmostEqual(r["quick_ratio"], (520000 - 178000) / 388000, places=4)
        self.assertAlmostEqual(r["interest_coverage"], (49000 + 13500) / 13500, places=4)
        self.assertAlmostEqual(r["dso"], 232000 / 985000 * 365, places=4)
        self.assertAlmostEqual(r["gross_margin"], (985000 - 788000) / 985000 * 100, places=4)
        self.assertAlmostEqual(r["roe"], 39200 / 468000 * 100, places=4)
        self.assertAlmostEqual(r["revenue_growth"], (985000 - 920000) / 920000 * 100, places=4)

    def test_first_year_has_no_growth(self):
        self.assertIsNone(self.analysis["ratios"]["2023"]["revenue_growth"])

    def test_zero_denominator_returns_none(self):
        year = dict(self.data["financials"]["years"]["2025"], interest_expense=0)
        r = fa.compute_ratios(year)
        self.assertIsNone(r["interest_coverage"])

    def test_report_renders(self):
        report = fa.render_markdown(self.data, self.analysis, "2026-07-11")
        self.assertIn("財務分析報告", report)
        self.assertIn("負債比率", report)


class TestLoanMonitoring(unittest.TestCase):
    def setUp(self):
        self.data = load_sample()
        self.analysis = fa.analyze(self.data)

    def test_sample_covenants_all_pass(self):
        results = lm.check_covenants(self.data, self.analysis)
        self.assertEqual(len(results), 3)
        self.assertTrue(all(c["passed"] for c in results))

    def test_covenant_breach_detected(self):
        self.data["covenants"].append(
            {"metric": "debt_ratio", "operator": "<=", "threshold": 50, "name": "測試條款"}
        )
        results = lm.check_covenants(self.data, self.analysis)
        self.assertFalse(results[-1]["passed"])
        self.assertEqual(lm.overall_level(results, []), "紅")

    def test_sample_alerts_yellow(self):
        alerts = lm.builtin_alerts(self.data, self.analysis)
        levels = [a["level"] for a in alerts]
        self.assertIn("黃", levels)
        self.assertNotIn("紅", levels)
        messages = " ".join(a["message"] for a in alerts)
        self.assertIn("營業利益率連續兩年下滑", messages)
        self.assertIn("低於 10%", messages)

    def test_overall_level_green_when_clean(self):
        self.assertEqual(lm.overall_level([], []), "綠")


class TestCreditMemo(unittest.TestCase):
    def test_memo_generation(self):
        data = load_sample()
        analysis = fa.analyze(data)
        memo = credit_memo.generate(data, analysis, "2026-07-11")
        self.assertIn(data["company"]["name"], memo)
        self.assertIn("授信審查報告", memo)
        self.assertIn("150,000", memo)
        self.assertNotIn("{company_name}", memo)


if __name__ == "__main__":
    unittest.main()
