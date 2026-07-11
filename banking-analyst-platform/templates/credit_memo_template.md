# 授信審查報告（初稿）

> 本報告由自動化平台產生初稿，標示【請分析師補充】處需人工完成，全文請覆核後始得引用。

- 借款戶：{company_name}（統一編號：{tax_id}）
- 報告日期：{generated_date}
- 承辦分析師：＿＿＿＿＿＿

## 一、案由

申請 {facility_type} 額度 {amount_fmt}，期間 {tenor}，資金用途為{purpose}。

## 二、借款戶概況

| 項目 | 內容 |
|---|---|
| 公司名稱 | {company_name} |
| 統一編號 | {tax_id} |
| 設立日期 | {established} |
| 負責人 | {chairman} |
| 實收資本額 | {capital_fmt} |
| 員工人數 | {employees} 人 |
| 產業別 | {industry} |
| 往來起始 | {relationship_since} |
| 行內信用評等 | {rating} |

主要業務：{business_description}

## 三、產業概況

【請分析師補充：產業景氣、供需狀況、借款戶市場地位與同業比較。可請 Claude 以 deep-research 協助蒐集產業資料。】

## 四、財務分析

（金額單位：{financial_unit}）

### 4.1 主要財務數字

{financial_summary_table}

### 4.2 財務比率

{financial_ratio_table}

### 4.3 財務評述

{financial_commentary}

【請分析師補充：異常科目說明、會計師查核意見、關係人交易等。】

## 五、償還來源與還款能力

- 第一還款來源：營業活動現金流量（{latest_year} 年度為 {latest_ocf}）。
- 第二還款來源：擔保品處分價值。

【請分析師補充：還款來源充足性之量化分析。】

## 六、擔保條件

- 擔保品：{collateral}
- 保證人：{guarantors}

## 七、風險評估

{risk_flags}

【請分析師補充：產業風險、經營風險、其他非財務風險與風險緩釋措施。】

## 八、綜合評述與建議

【請分析師補充：綜合前述分析之核貸建議、額度條件（利率 {pricing}）、管控條件。】

---
（本初稿由 banking-analyst-platform 自動產生於 {generated_date}）
