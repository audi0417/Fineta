# FINPLUS/indicators/risk_indicators.py

import pandas as pd
import numpy as np

def calculate_volatility_and_risk(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 计算每日回报率
    df['Daily_Return'] = df.groupby(level='Stock')['Close'].pct_change()

    # 计算年度化的历史波动率（如果数据不足，会返回NaN）
    df['Annual_Volatility'] = df.groupby(level='Stock')['Daily_Return'].transform(lambda x: x.rolling(window=252, min_periods=1).std() * np.sqrt(252))

    # 模拟 Beta 系数（在实际中通常需要与市场指数进行回归分析）
    df['Beta'] = np.random.uniform(0.8, 1.2, size=len(df))

    # 计算累计回报率
    df['Cumulative_Return'] = (1 + df['Daily_Return']).groupby(level='Stock').cumprod()

    # 计算最大回撤
    df['Cumulative_Max'] = df.groupby(level='Stock')['Cumulative_Return'].cummax()
    df['Drawdown'] = df['Cumulative_Return'] / df['Cumulative_Max'] - 1
    df['Max_Drawdown'] = df.groupby(level='Stock')['Drawdown'].cummin()

    # 选择所需的列，去除NaN值
    risk_metrics = df[['Annual_Volatility', 'Beta', 'Max_Drawdown']].dropna()

    return risk_metrics
