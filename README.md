# Fineta

目錄
- [簡介](#簡介)
- [功能](#功能)
- [安裝](#安裝)
- [使用方法](#使用方法)
- [範例](#範例)
- [例外處理](#例外處理)
- [貢獻](#貢獻)


## 簡介
Fineta 是一個 Python 程式庫，用於從台灣證券交易所（TWSE）網站抓取公司財務報表資料，並將其解析為 pandas DataFrame 格式。使用者可以指定股票代號及時間範圍，獲取不同季的資產負債表、綜合損益表和現金流量表。

## 功能
從 TWSE 網站抓取指定股票的財務數據
支援不同類型的財務報表（資產負債表、綜合損益表、現金流量表）
自動處理日期範圍及季報表的生成
數據自動解析為 pandas DataFrame 格式，方便進一步分析
## 安裝
先決條件
確保您的環境中已經安裝了以下軟體：

Python 3.7+
pip
安裝步驟
克隆此專案至您的本地環境：
```
git clone https://github.com/audi0417/Fineta.git
```
進入專案目錄並安裝所需套件：
```
cd Fineta
pip install -r requirements.txt
```

## 使用方法
首先，您需要導入 FinancialScraper 類別，並初始化一個實例，指定股票代號及開始和結束日期。接著，您可以使用 get_financial_statements 方法來抓取並獲取指定類型的財務報表。

```python
from Fineta.crawler import FinancialScraper
scraper = FinancialScraper(stock_id="2330", start_date="2022-01-01", end_date="2023-01-01")
```


## 貢獻
如果您有任何建議或改進，歡迎提交 Pull Request，或在 Issue 中提出您的問題與建議。

1. Fork 此專案
2. 創建您的分支 (git checkout -b feature/YourFeature)
3. 提交您的修改 (git commit -m 'Add some feature')
4. 推送至分支 (git push origin feature/YourFeature)
5. 打開一個 Pull Request
