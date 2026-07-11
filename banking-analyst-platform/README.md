# 對公分析師自動化工作平台

針對商業銀行對公（企業金融）分析師日常工作打造的自動化工具，純 Python 標準庫實作，無需安裝任何套件，`python3` 即可執行。

## 功能總覽

| 指令 | 功能 | 產出 |
|---|---|---|
| `analyze` | 財務報表分析：自動計算 19 項授信常用財務比率（財務結構、償債能力、經營效率、獲利能力、現金流量、成長性）並產生規則式評述 | 財務分析報告（Markdown） |
| `memo` | 授信報告初稿：套用範本自動填入客戶概況、申請內容、財務分析與風險要點，人工待補處以【請分析師補充】標示 | 授信審查報告初稿（Markdown） |
| `monitor` | 貸後監控：逐條檢核財務契約條款（covenant），並執行內建紅／黃燈預警規則，給出綜合燈號與處理建議 | 貸後監控檢核報告（Markdown） |
| `all` | 一次產出以上全部報告 | 三份報告 |
| `init-template` | 產生空白客戶資料檔，供建立新客戶使用 | 空白 JSON |

## 快速開始

```bash
cd banking-analyst-platform

# 用範例資料跑一次全流程
python3 platform_cli.py all data/sample_company.json

# 建立新客戶資料檔，填入財務數字後即可分析
python3 platform_cli.py init-template data/my_client.json
python3 platform_cli.py all data/my_client.json
```

報告預設輸出至 `output/`（已被 gitignore），可用 `-o 目錄` 指定其他位置。

## 客戶資料格式

一個客戶一個 JSON 檔，結構見 `data/sample_company.json`（虛構範例）。四大區塊：

- **company**：公司基本資料（名稱、統編、產業、負責人、資本額、行內評等等）
- **application**：本次授信申請內容（額度種類、金額、期間、用途、擔保、保證人）
- **financials**：各年度財務數字，`unit` 為金額單位，`years` 下每年一組，欄位如下（缺漏欄位對應比率顯示 N/A，不會中斷）：

| 欄位 | 中文 | 欄位 | 中文 |
|---|---|---|---|
| revenue | 營業收入 | current_assets | 流動資產 |
| cogs | 營業成本 | total_assets | 資產總額 |
| operating_expenses | 營業費用 | current_liabilities | 流動負債 |
| interest_expense | 利息費用 | total_liabilities | 負債總額 |
| pretax_income | 稅前淨利 | short_term_debt | 短期借款 |
| net_income | 稅後淨利 | long_term_debt | 長期借款 |
| cash | 現金及約當現金 | accounts_payable | 應付帳款 |
| accounts_receivable | 應收帳款 | equity | 股東權益 |
| inventory | 存貨 | operating_cash_flow | 營業活動現金流量 |

- **covenants**：財務契約條款清單，每條含 `metric`（比率鍵值，見 `modules/financial_analysis.py` 的 `RATIO_DEFS`）、`operator`（`>=` `<=` `>` `<`）、`threshold`、`name`。

## 內建預警規則（貸後監控）

- 🔴 紅燈：連續兩年虧損、利息保障倍數 < 1、流動比率 < 1、連續兩年營業現金流為負、任一 covenant 違反
- 🟡 黃燈：單年虧損、利息保障倍數 < 2、負債比率 > 65%、營收衰退逾 10%、單年營業現金流為負、營業現金流對流動負債比 < 10%、應收／存貨天數年增逾 20%、營業利益率連續兩年下滑

規則門檻可直接在 `modules/loan_monitoring.py` 依行內標準調整。

## 搭配 Claude Code 的建議工作流

此平台處理「可規則化」的部分；判斷與研究類工作建議直接在本 repo 開 Claude Code session 搭配使用：

1. **財報建檔**：把客戶財報（PDF／Excel／照片）給 Claude，請它依上表欄位轉成客戶 JSON 檔。
2. **產業研究**：授信報告第三節產業概況，用 `/deep-research` 請 Claude 蒐集產業景氣與同業資料後填入。
3. **批次監控**：多個客戶檔案放在 `data/` 下，請 Claude 逐一執行 `monitor` 並彙總各戶燈號成觀察名單。
4. **規則客製**：請 Claude 依行內授信準則調整比率定義、預警門檻或報告範本（`templates/credit_memo_template.md`）。

## 測試

```bash
python3 -m unittest discover tests -v
```

## ⚠️ 資料安全注意事項

- `data/sample_company.json` 為**完全虛構**的範例資料。
- 真實客戶財務資料屬銀行機密／個資，**請勿 commit 到本 repo**（尤其公開 repo）。建議真實資料檔放在 repo 外目錄，執行時以路徑帶入即可。
- 所有自動產出的報告均為**初稿**，數字與評述務必由分析師覆核後方可用於行內簽報。
