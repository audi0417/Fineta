## 範例
假設有一個包含股票代號的 DataFrame stock_df，您可以使用以下代碼獲取指標：
```python
from Fineta.stock import Stock,Portfolio
from Fineta.crawler import StockPriceFetcher
from Fineta.indicators import TechnicalIndicators

portfolio = Portfolio(Stock(["2330"]))
fetcher_single = StockPriceFetcher(portfolio, "2022-01-01", "2023-12-31")

stock_data_single = fetcher_single.fetch_stock_data()
df_single = fetcher_single.to_dataframe()
print("轉換後的單個股票數據 DataFrame:\n", df_single)

technical_indicators = TechnicalIndicators(df_single)
# 計算 SMA
sma = technical_indicators.calculate_sma(window=20)
print("SMA:\n", sma)

# 計算 RSI
rsi = technical_indicators.calculate_rsi(window=14)
print("RSI:\n", rsi)

# 計算 Bollinger Bands
bollinger_bands = technical_indicators.calculate_bollinger_bands(window=20)
print("Bollinger Bands:\n", bollinger_bands)

# 計算 MACD
macd = technical_indicators.calculate_macd()
print("MACD:\n", macd)
```
