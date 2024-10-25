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

        if isinstance(df.index, pd.MultiIndex):
            new_levels = []
            for level in df.index.levels:
                if level.dtype.kind == 'M':
                    level = level.tz_localize(None).normalize() 
                    level = level.date  
                new_levels.append(level)
            df.index = df.index.set_levels(new_levels)
        else:
            df.index = df.index.tz_localize(None).normalize()
            df.index = df.index.date  
                
        return df
