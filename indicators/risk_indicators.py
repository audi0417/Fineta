# FINPLUS/indicators/risk_indicators.py

import pandas as pd
import numpy as np

def calculate_volatility_and_risk(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # 計算每日回報率
    df['Daily_Return'] = df.groupby(level='Stock')['Close'].pct_change()

    # 計算年度歷史波動率
    df['Annual_Volatility'] = df.groupby(level='Stock')['Daily_Return'].transform(lambda x: x.rolling(window=252, min_periods=1).std() * np.sqrt(252))
    
    # 計算累積回報率
    df['Cumulative_Return'] = (1 + df['Daily_Return']).groupby(level='Stock').cumprod()

    # 計算最大回撤
    df['Cumulative_Max'] = df.groupby(level='Stock')['Cumulative_Return'].cummax()
    df['Drawdown'] = df['Cumulative_Return'] / df['Cumulative_Max'] - 1
    df['Max_Drawdown'] = df.groupby(level='Stock')['Drawdown'].cummin()

    risk_metrics = df[['Daily_Return', 'Annual_Volatility', 'Max_Drawdown']].dropna()

    return risk_metrics
