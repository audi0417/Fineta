# Fineta

Fineta 是一個Python 程式庫，用於從台灣證券交易所（TWSE）網站抓取公司財務報表資料，並將其轉換為便於分析的 pandas DataFrame 格式。您可以輕鬆地指定股票代號及時間範圍，獲取不同季的資產負債表、綜合損益表、現金流量表，以及相關的指標計算工具。


## 目錄

- [簡介](#簡介)
- [功能](#功能)
- [檔案結構](#檔案結構)
- [安裝](#安裝)
- [使用方法](#使用方法)


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
├── stock.py                          # 股票核心邏輯
└── requirements.txt                  # 所需套件
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
Fineta 可以用於抓取財務報表數據並進行分析:
導入核心模組： 首先，從 Fineta.crawler 中導入 FinancialScraper 類別。
```python
from Fineta.stock import Stock,Portfolio
from Fineta.crawler import FinancialScraper

portfolio = Portfolio(Stock(["2330","1101"]))
scraper = FinancialScraper(portfolio, "2023-01-01", "2023-04-30")
financial_statements = scraper.get_portfolio_financial_statements("資產負債表")

# 現在 financial_statements 是一個字典，其中包含了每個股票的財務報表
for stock_id, statement in financial_statements.items():
    print(f"Financial statement for stock {stock_id}:")
    print(statement)
    print("\n")
```
