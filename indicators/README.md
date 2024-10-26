## 範例
假設有一個包含股票代號的 DataFrame stock_df，您可以使用以下代碼獲取基本面指標：
```python
# 導入類別
from FINPLUS.indicators.fundamental_indicators import FundamentalIndicators

# 設定查詢日期
date = "20231001"

# 初始化基本面指標計算類別
fundamentals = FundamentalIndicators(date)

# 假設 stock_df 是包含股票代號的 DataFrame
fundamental_metrics = fundamentals.calculate_fundamentals(stock_df)
print(fundamental_metrics)
```
