import pandas as pd
import numpy as np
from typing import Optional
import yfinance as yf
from .return_indicators import ReturnIndicators

class RiskIndicators:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.return_calculator = ReturnIndicators(df)

    def calculate_beta_alpha(self, market_index: str, 
                           risk_free_rate: Optional[float] = None,
                           trading_days: int = 252,
                           start_date: Optional[str] = None, 
                           end_date: Optional[str] = None) -> pd.DataFrame:
        """
        計算Beta值和Alpha值。
        
        Args:
            market_index (str): 市場指數代碼，例如 '^TWII' 或 '^DJI'
            risk_free_rate (float, optional): 年化無風險利率，例如0.02表示2%
            trading_days (int): 年化交易日數，預設252天
            start_date (str, optional): 開始日期，格式為 'YYYY-MM-DD'
            end_date (str, optional): 結束日期，格式為 'YYYY-MM-DD'
        
        Returns:
            pd.DataFrame: 包含Beta值和Alpha值的DataFrame
        """
        try:
            # 設定預設無風險利率
            if risk_free_rate is None:
                risk_free_rate = 0.02

            # 獲取市場指數數據
            market_data = yf.download(market_index, start=start_date, end=end_date)
            market_returns = market_data['Close'].pct_change().dropna()

            # 使用ReturnIndicators計算回報率
            stock_returns = self.return_calculator.calculate_returns(trading_days)
            market_return = ReturnIndicators.calculate_market_return(
                market_index, start_date, end_date, trading_days
            )

            metrics = {}
            for stock_id in self.df.index.get_level_values('Stock').unique():
                stock_data = self.df.loc[stock_id]['Close']
                stock_daily_returns = stock_data.pct_change().dropna()

                # 確保日期對齊
                aligned_data = pd.concat([stock_daily_returns, market_returns], axis=1).dropna()
                aligned_data.columns = ['stock', 'market']

                if len(aligned_data) > 0:
                    # 計算Beta值
                    covariance = aligned_data['stock'].cov(aligned_data['market'])
                    market_variance = aligned_data['market'].var()
                    beta = covariance / market_variance

                    # 使用預先計算的回報率計算Alpha值
                    stock_return = stock_returns[stock_id]
                    alpha = stock_return - (risk_free_rate + beta * (market_return - risk_free_rate))

                    metrics[stock_id] = {
                        'Beta': beta,
                        'Alpha': alpha,
                        'Stock_Return': stock_return,
                        'Market_Return': market_return
                    }
                else:
                    metrics[stock_id] = {
                        'Beta': None,
                        'Alpha': None,
                        'Stock_Return': None,
                        'Market_Return': None
                    }

            return pd.DataFrame.from_dict(metrics, orient='index')

        except Exception as e:
            print(f"計算Beta和Alpha值時發生錯誤: {e}")
            return pd.DataFrame()
        

    def calculate_volatility_and_risk(self, metrics: list = None) -> pd.DataFrame:
        """
        計算指定的風險指標並返回結果。

        Args:
            metrics (list, optional): 使用者希望返回的指標名稱列表。
                支援的選項包括 'Daily_Return', 'Annual_Volatility', 'Cumulative_Return', 'Drawdown', 'Max_Drawdown'。
                若未指定，預設返回全部指標。

        Returns:
            pd.DataFrame: 包含所選指標的 DataFrame。
        """
        df = self.df.copy()
        
        # 計算每日回報率
        df['Daily_Return'] = df.groupby(level='Stock')['Close'].pct_change()
        
        # 計算年度歷史波動率
        df['Annual_Volatility'] = df.groupby(level='Stock')['Daily_Return'].transform(
            lambda x: x.rolling(window=252, min_periods=1).std() * np.sqrt(252)
        )
        
        # 計算累積回報率
        df['Cumulative_Return'] = (1 + df['Daily_Return']).groupby(level='Stock').cumprod()
        
        # 計算最大回撤
        df['Cumulative_Max'] = df.groupby(level='Stock')['Cumulative_Return'].cummax()
        df['Drawdown'] = df['Cumulative_Return'] / df['Cumulative_Max'] - 1
        df['Max_Drawdown'] = df.groupby(level='Stock')['Drawdown'].cummin()
        
        # 可選指標
        available_metrics = {
            'Daily_Return': df['Daily_Return'],
            'Annual_Volatility': df['Annual_Volatility'],
            'Cumulative_Return': df['Cumulative_Return'],
            'Drawdown': df['Drawdown'],
            'Max_Drawdown': df['Max_Drawdown']
        }
        
        # 若使用者未指定 metrics，預設返回全部指標
        if metrics is None:
            metrics = list(available_metrics.keys())
        
        # 根據使用者選擇的指標構建結果 DataFrame
        selected_metrics = {metric: available_metrics[metric] for metric in metrics if metric in available_metrics}
        risk_metrics = pd.DataFrame(selected_metrics).dropna()

        return risk_metrics
