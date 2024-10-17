**抓取財務報表**
```python
# 抓取並解析資產負債表
balance_sheet = scraper.get_financial_statements(statement_type="資產負債表")

# 抓取並解析綜合損益表
income_statement = scraper.get_financial_statements(statement_type="綜合損益表")

# 抓取並解析現金流量表
cash_flow_statement = scraper.get_financial_statements(statement_type="現金流量表")
```

## 範例
```python
from Fineta.stock import Stock,Portfolio
from Fineta.crawler import FinancialScraper

portfolio = Portfolio(Stock(["2330","1101"]))
scraper = FinancialScraper(portfolio, "2022-01-01", "2023-12-31")
financial_statements = scraper.get_portfolio_financial_statements("資產負債表")

# 現在 financial_statements 是一個字典，其中包含了每個股票的財務報表
for stock_id, statement in financial_statements.items():
    print(f"Financial statement for stock {stock_id}:")
    print(statement)
    print("\n")
```
## 例外處理
本程式庫內部定義了一些自訂例外，如 InvalidTypeError，當傳入不支援的報表類型時，會引發此錯誤。
