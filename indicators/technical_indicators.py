# FINPLUS/indicators/technical_indicators.py

import pandas as pd

def calculate_sma(df: pd.DataFrame, window: int) -> pd.Series:
    return df.groupby(level='Stock')['Close'].transform(lambda x: x.rolling(window=window).mean())

def calculate_ema(df: pd.DataFrame, span: int) -> pd.Series:
    return df.groupby(level='Stock')['Close'].transform(lambda x: x.ewm(span=span, adjust=False).mean())

def calculate_rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    delta = df.groupby(level='Stock')['Close'].transform(lambda x: x.diff())
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_bollinger_bands(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    middle_band = df.groupby(level='Stock')['Close'].transform(lambda x: x.rolling(window=window).mean())
    std_dev = df.groupby(level='Stock')['Close'].transform(lambda x: x.rolling(window=window).std())
    upper_band = middle_band + (2 * std_dev)
    lower_band = middle_band - (2 * std_dev)
    return pd.DataFrame({'Middle_Band': middle_band, 'Upper_Band': upper_band, 'Lower_Band': lower_band})

def calculate_macd(df: pd.DataFrame) -> pd.DataFrame:
    ema_12 = calculate_ema(df, span=12)
    ema_26 = calculate_ema(df, span=26)
    macd = ema_12 - ema_26
    signal = macd.groupby(level='Stock').transform(lambda x: x.ewm(span=9, adjust=False).mean())
    return pd.DataFrame({'MACD': macd, 'Signal_Line': signal})
