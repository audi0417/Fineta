# FINPLUS/pricing/stock_price_fetcher.py

import yfinance as yf
import pandas as pd
from FINPLUS.stock import Stock, Portfolio
from typing import Union, List

class StockPriceFetcher:
    def __init__(self, target: Union[Stock, Portfolio], start_date: str, end_date: str):
        self.target = target
        self.start_date = start_date
        self.end_date = end_date
        self.stock_data = {}

    def fetch_stock_data(self):
        stock_ids = self.target.get_all_stock_ids()

        for stock_id in stock_ids:
            ticker = yf.Ticker(f'{stock_id}.TW')
            data = ticker.history(start=self.start_date, end=self.end_date)
            self.stock_data[stock_id] = data

        return self.stock_data

    def to_dataframe(self) -> pd.DataFrame:
        if not self.stock_data:
            raise ValueError("No data fetched. Call fetch_stock_data() first.")
        
        df = pd.concat(self.stock_data.values(), keys=self.stock_data.keys(), names=['Stock', 'Date'])

        # 移除时区并将日期转换为纯日期（没有时间部分）
        if isinstance(df.index, pd.MultiIndex):
            # 处理 MultiIndex 的 Date 部分
            new_levels = []
            for level in df.index.levels:
                if level.dtype.kind == 'M':
                    level = level.tz_localize(None).normalize()  # 移除时区并保留日期
                    level = level.date  # 转换为日期
                new_levels.append(level)
            df.index = df.index.set_levels(new_levels)
        else:
            # 如果不是 MultiIndex，直接处理单个 DatetimeIndex
            df.index = df.index.tz_localize(None).normalize()
            df.index = df.index.date  # 转换为日期
                
        return df
