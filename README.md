# Fineta

Fineta 是一個強大的 Python 程式庫，用於從台灣證券交易所（TWSE）網站抓取公司財務報表資料，並將其轉換為便於分析的 pandas DataFrame 格式。您可以輕鬆地指定股票代號及時間範圍，獲取不同季的資產負債表、綜合損益表、現金流量表，以及相關的指標計算工具。


## 目錄

- [簡介](#簡介)
- [功能](#功能)
- [檔案結構](#檔案結構)
- [安裝](#安裝)
- [使用方法](#使用方法)
- [範例](#範例)
- [例外處理](#例外處理)
- [貢獻](#貢獻)

---

## 簡介

Fineta 提供了從台灣證券交易所（TWSE）自動抓取公司財務資料的功能，無需手動下載報表。這個程式庫還包括技術分析、風險指標和基本面指標的計算模組，適合投資者、數據分析師和金融研究人員進行深入的股票分析。

主要功能包括：
- 從 TWSE 抓取指定股票的財務數據。
- 支援不同類型的財務報表（資產負債表、綜合損益表、現金流量表）。
- 自動處理季報數據，並支持多個季度的合併查詢。
- 將資料轉換成 pandas DataFrame 格式，便於進一步分析和匯出。
- 包含技術指標、風險指標和基本面指標的計算模組。


## 功能

- **財務資料抓取**：從台灣證券交易所網站獲取公司季報和年報數據。
- **資料解析**：自動將財務數據轉換為 pandas DataFrame 格式。
- **技術指標分析**：內建多種技術指標，如移動平均線、相對強弱指標（RSI）等。
- **風險指標分析**：提供股價波動、VaR 等風險指標的計算。
- **基本面分析**：提供如市盈率、股本回報率（ROE）等基本面指標計算。


## 檔案結構

```plaintext
/
├── crawler/                          # 核心爬蟲功能模組
│   ├── __init__.py                   # 爬蟲模組初始化
│   ├── config.py                     # 爬蟲配置文件
│   ├── esg_report.py                 # 抓取 ESG 報告
│   ├── exceptions.py                 # 自訂例外處理
│   ├── financial_report.py           # 抓取財務報表邏輯
│   └── stockPrice_yfinance.py        # 使用 yfinance 抓取股價
│
├── export/                           # 數據匯出模組
│   ├── __init__.py                   # 匯出模組初始化
│   ├── export_to_csv.py              # 匯出數據至 CSV
│   └── export_to_excel.py            # 匯出數據至 Excel
│
├── indicators/                       # 指標計算模組
│   ├── __init__.py                   # 指標模組初始化
│   ├── fundamental_indicators.py     # 基本面指標計算
│   ├── risk_indicators.py            # 風險指標計算
│   └── technical_indicators.py       # 技術指標計算
│
├── LICENSE                           # 授權文件
├── README.md                         # 專案總說明文件
└── stock.py                          # 股票核心邏輯
```

### 主要模組：

- **crawler/**: 核心資料抓取邏輯，包括財務報表、股價和 ESG 報告等。
- **export/**: 提供 CSV 和 Excel 格式的匯出功能。
- **indicators/**: 內建技術、風險和基本面指標的計算模組，為進一步分析提供支援。

---

## 安裝

### 先決條件
請先確保您的系統上已安裝以下工具：
- **Python 3.7+**
- **pip**

### 安裝步驟

1. **克隆此專案**至您的本地環境：
   ```bash
   git clone https://github.com/audi0417/Fineta.git
    ```
2. 進入專案目錄並安裝所需的套件：
  ```bash
  cd Fineta
  pip install -r requirements.txt
  ```

## 使用方法
Fineta 可以用於抓取財務報表數據並進行分析，具體步驟如下：

1. 導入核心模組： 首先，從 Fineta.crawler 中導入 FinancialScraper 類別。
```python
from Fineta.crawler import FinancialScraper
```

2. 初始化 FinancialScraper 類別： 創建 FinancialScraper 的實例，並指定股票代號 (stock_id) 以及開始和結束日期 (start_date 和 end_date)。
```python
scraper = FinancialScraper(stock_id="2330", start_date="2022-01-01", end_date="2023-01-01")
```

3. 抓取財務報表： 使用 get_financial_statements() 方法來抓取財務數據。該方法允許選擇不同類型的報表，如資產負債表、損益表等。
```python
financial_data = scraper.get_financial_statements(statement_type="balance_sheet")
print(financial_data)
```
4. 導出結果： 抓取的數據可以通過 Fineta.export 模組以 CSV 或 Excel 格式導出。
```python
from Fineta.export import export_to_csv
export_to_csv(financial_data, "financial_report.csv")
```

## 範例
以下是抓取 2330 台積電 2022 年 Q1 到 2023 年 Q1 期間的財務報表的完整範例：
```python
from Fineta.crawler import FinancialScraper
from Fineta.export import export_to_csv

# 初始化財務數據抓取器
scraper = FinancialScraper(stock_id="2330", start_date="2022-01-01", end_date="2023-01-01")

# 抓取資產負債表數據
balance_sheet = scraper.get_financial_statements(statement_type="balance_sheet")

# 將數據匯出為 CSV 檔案
export_to_csv(balance_sheet, "tsmc_balance_sheet.csv")
```

##例外處理
在使用 Fineta 進行財務數據抓取的過程中，若遇到無法抓取或網站請求失敗等情況，會自動觸發自定義例外。這些例外都在 Fineta.crawler.exceptions 模組中定義，您可以自行捕捉並處理。
```python
from Fineta.crawler import FinancialScraper
from Fineta.crawler.exceptions import ScraperError

try:
    scraper = FinancialScraper(stock_id="2330", start_date="2022-01-01", end_date="2023-01-01")
    data = scraper.get_financial_statements(statement_type="balance_sheet")
except ScraperError as e:
    print(f"抓取失敗: {e}")
```

