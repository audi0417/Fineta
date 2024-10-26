## 範例
假設有一個包含股票代號的 DataFrame stock_df，您可以使用以下代碼獲取基本面指標：
```python
date = "20231001"  # 查詢日期
fundamental_metrics = calculate_fundamentals(stock_df, date)
print(fundamental_metrics)
```
