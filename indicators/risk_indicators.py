import pandas as pd
import numpy as np

class RiskIndicators:
    def __init__(self, df: pd.DataFrame):
        """
        初始化 RiskIndicators 類別。

        Args:
            df (pd.DataFrame): 包含股票數據的 DataFrame，應包含 'Close' 列
        """
        self.df = df.copy()

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
