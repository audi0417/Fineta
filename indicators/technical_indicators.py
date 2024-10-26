import pandas as pd

class TechnicalIndicators:
    """
    技術指標計算類別，提供 SMA、EMA、RSI、布林帶和 MACD 的計算功能。
    """

    def __init__(self, df: pd.DataFrame):
        """
        初始化 TechnicalIndicators 類別。

        Args:
            df (pd.DataFrame): 包含股票數據的 DataFrame，應包含 'Close' 列。
        """
        self.df = df.copy()

    def calculate_sma(self, window: int) -> pd.Series:
        """計算簡單移動平均線 (SMA)"""
        return self.df.groupby(level='Stock')['Close'].transform(lambda x: x.rolling(window=window).mean())

    def calculate_ema(self, span: int) -> pd.Series:
        """計算指數移動平均線 (EMA)"""
        return self.df.groupby(level='Stock')['Close'].transform(lambda x: x.ewm(span=span, adjust=False).mean())

    def calculate_rsi(self, window: int = 14) -> pd.Series:
        """計算相對強弱指數 (RSI)"""
        delta = self.df.groupby(level='Stock')['Close'].transform(lambda x: x.diff())
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_bollinger_bands(self, window: int = 20) -> pd.DataFrame:
        """計算布林帶 (Bollinger Bands)"""
        middle_band = self.df.groupby(level='Stock')['Close'].transform(lambda x: x.rolling(window=window).mean())
        std_dev = self.df.groupby(level='Stock')['Close'].transform(lambda x: x.rolling(window=window).std())
        upper_band = middle_band + (2 * std_dev)
        lower_band = middle_band - (2 * std_dev)
        return pd.DataFrame({'Middle_Band': middle_band, 'Upper_Band': upper_band, 'Lower_Band': lower_band})

    def calculate_macd(self) -> pd.DataFrame:
        """計算移動平均收斂/發散 (MACD)"""
        ema_12 = self.calculate_ema(span=12)
        ema_26 = self.calculate_ema(span=26)
        macd = ema_12 - ema_26
        signal = macd.groupby(level='Stock').transform(lambda x: x.ewm(span=9, adjust=False).mean())
        return pd.DataFrame({'MACD': macd, 'Signal_Line': signal})
