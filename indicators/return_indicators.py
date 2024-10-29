# indicators/return_indicators.py

import pandas as pd
import yfinance as yf
from typing import Optional, Dict, Tuple

class ReturnIndicators:
    """計算回報率的類別"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def calculate_returns(self, trading_days: int = 252) -> Dict[str, float]:
        """
        計算個股的年化報酬率。

        Args:
            trading_days (int): 年化交易日數，預設252天

        Returns:
            Dict[str, float]: 股票代號對應的年化報酬率
        """
        returns = {}
        for stock_id in self.df.index.get_level_values('Stock').unique():
            stock_data = self.df.loc[stock_id]['Close']
            daily_returns = stock_data.pct_change().dropna()
            if len(daily_returns) > 0:
                annual_return = daily_returns.mean() * trading_days
                returns[stock_id] = annual_return
            else:
                returns[stock_id] = None
        return returns

    @staticmethod
    def calculate_market_return(market_index: str, start_date: Optional[str] = None, 
                              end_date: Optional[str] = None, 
                              trading_days: int = 252) -> float:
        """
        計算市場指數的年化報酬率。

        Args:
            market_index (str): 市場指數代碼
            start_date (str, optional): 開始日期
            end_date (str, optional): 結束日期
            trading_days (int): 年化交易日數，預設252天

        Returns:
            float: 市場年化報酬率
        """
        try:
            market_data = yf.download(market_index, start=start_date, end=end_date)
            market_returns = market_data['Close'].pct_change().dropna()
            if len(market_returns) > 0:
                return market_returns.mean() * trading_days
            return None
        except Exception as e:
            print(f"計算市場報酬率時發生錯誤: {e}")
            return None