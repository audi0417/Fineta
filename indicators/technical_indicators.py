import pandas as pd
from typing import Union, List

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

    def calculate_rsi(self, window: Union[int, List[int]] = [6, 12, 24]) -> pd.DataFrame:
        """
        計算相對強弱指數 (RSI)。
        
        Args:
            window (Union[int, List[int]]): 回顧期間，可為單一數值或列表，預設[6, 12, 24]天
            
        Returns:
            pd.DataFrame: 包含不同週期的RSI值的DataFrame
        """
        # 統一處理單值和列表輸入
        if isinstance(window, int):
            windows_list = [window]
        else:
            windows_list = window
            
        rsi_dict = {}
        
        for w in windows_list:
            delta = self.df['Close'].groupby(level='Stock').transform(lambda x: x.diff())
            gain = (delta.where(delta > 0, 0)).groupby(level='Stock').transform(
                lambda x: x.rolling(window=w).mean()
            )
            loss = (-delta.where(delta < 0, 0)).groupby(level='Stock').transform(
                lambda x: x.rolling(window=w).mean()
            )
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_dict[f'RSI_{w}'] = rsi
        
        return pd.DataFrame(rsi_dict)

    def calculate_bollinger_bands(self, window: Union[int, List[int]] = [5, 20, 60]) -> Union[pd.DataFrame, pd.DataFrame]:
        """
        計算布林帶 (Bollinger Bands)。
        
        Args:
            window (Union[int, List[int]]): 回顧期間，可為單一數值或列表，預設[5, 20, 60]天
            
        Returns:
            pd.DataFrame: 包含不同週期的布林帶值的DataFrame
        """
        # 統一處理單值和列表輸入
        if isinstance(window, int):
            windows_list = [window]
        else:
            windows_list = window
            
        bb_dict = {}
        
        for w in windows_list:
            middle_band = self.df['Close'].groupby(level='Stock').transform(
                lambda x: x.rolling(window=w).mean()
            )
            std_dev = self.df['Close'].groupby(level='Stock').transform(
                lambda x: x.rolling(window=w).std()
            )
            upper_band = middle_band + (2 * std_dev)
            lower_band = middle_band - (2 * std_dev)
            
            bb_dict[f'Middle_Band_{w}'] = middle_band
            bb_dict[f'Upper_Band_{w}'] = upper_band
            bb_dict[f'Lower_Band_{w}'] = lower_band
        
        return pd.DataFrame(bb_dict)

    def calculate_macd(self, fast_spans: list = [12], slow_spans: list = [26], signal_spans: list = [9]) -> pd.DataFrame:
        """
        計算移動平均收斂/發散 (MACD)。
        
        Args:
            fast_spans (list): 快線週期列表，預設[12]天
            slow_spans (list): 慢線週期列表，預設[26]天
            signal_spans (list): 訊號線週期列表，預設[9]天
            
        Returns:
            pd.DataFrame: 包含不同週期組合的MACD值的DataFrame
        """
        macd_dict = {}
        
        for fast_span in fast_spans:
            for slow_span in slow_spans:
                ema_fast = self.calculate_ema(span=fast_span)
                ema_slow = self.calculate_ema(span=slow_span)
                macd = ema_fast - ema_slow
                
                for signal_span in signal_spans:
                    signal = macd.groupby(level='Stock').transform(
                        lambda x: x.ewm(span=signal_span, adjust=False).mean()
                    )
                    
                    key_prefix = f'MACD_{fast_span}_{slow_span}_{signal_span}'
                    macd_dict[f'{key_prefix}_MACD'] = macd
                    macd_dict[f'{key_prefix}_Signal'] = signal
                    macd_dict[f'{key_prefix}_Hist'] = macd - signal
        
        return pd.DataFrame(macd_dict)
    def calculate_stochastic(self, window: Union[int, List[int]] = [9, 14], smooth_k: int = 3, smooth_d: int = 3) -> pd.DataFrame:
        """
        計算KD指標 (Stochastic Oscillator)。
        
        Args:
            window (Union[int, List[int]]): 回顧期間，可為單一數值或列表，預設[9, 14]天
            smooth_k (int): %K的平滑期間，預設3天
            smooth_d (int): %D的平滑期間，預設3天
            
        Returns:
            pd.DataFrame: 包含不同週期的%K和%D值的DataFrame
        """
        # 統一處理單值和列表輸入
        if isinstance(window, int):
            windows_list = [window]
        else:
            windows_list = window
            
        kd_dict = {}
        
        for w in windows_list:
            # 計算基本值
            low_min = self.df['Low'].groupby(level='Stock').transform(
                lambda x: x.rolling(window=w).min()
            )
            high_max = self.df['High'].groupby(level='Stock').transform(
                lambda x: x.rolling(window=w).max()
            )
            
            # 計算%K (Fast Stochastic)
            k_fast = 100 * ((self.df['Close'] - low_min) / (high_max - low_min))
            
            # 計算平滑後的%K
            k = k_fast.groupby(level='Stock').transform(
                lambda x: x.rolling(smooth_k).mean()
            )
            
            # 計算%D (K的移動平均)
            d = k.groupby(level='Stock').transform(
                lambda x: x.rolling(smooth_d).mean()
            )
            
            # 儲存結果
            kd_dict[f'K_{w}'] = k
            kd_dict[f'D_{w}'] = d
        
        return pd.DataFrame(kd_dict)

    def calculate_williams_r(self, window: Union[int, List[int]] = [5, 10, 14]) -> pd.DataFrame:
        """
        計算威廉指標 (Williams %R)。
        
        計算公式：
        W%R = (N日最高價 - 收盤價) ÷ (N日最高價 - N日最低價) × 100% × (-1)
        
        與KD中的RSV相反：
        RSV = (收盤價 - N日最低價) ÷ (N日最高價 - N日最低價) × 100%
        
        Args:
            window (Union[int, List[int]]): 回顧期間，可為單一數值或列表，預設[5, 10, 14]天
            
        Returns:
            pd.DataFrame: 包含不同週期的Williams %R值，範圍為0到-100
                        數值越接近0代表超買
                        數值越接近-100代表超賣
        """
        # 統一處理單值和列表輸入
        if isinstance(window, int):
            windows_list = [window]
        else:
            windows_list = window
            
        williams_dict = {}
        
        for w in windows_list:
            # 計算N日週期內的最高價和最低價
            highest_high = self.df['High'].groupby(level='Stock').transform(
                lambda x: x.rolling(window=w).max()
            )
            lowest_low = self.df['Low'].groupby(level='Stock').transform(
                lambda x: x.rolling(window=w).min()
            )
            
            # 計算威廉指標
            williams_r = ((highest_high - self.df['Close']) / 
                        (highest_high - lowest_low) * 100 * (-1))
            
            williams_dict[f'WR_{w}'] = williams_r
        
        return pd.DataFrame(williams_dict)



    def calculate_dmi(self, window: int = 14) -> pd.DataFrame:
        """
        計算動向指標 (DMI - Directional Movement Index)。
        
        Args:
            window (int): 回顧期間，預設14天
            
        Returns:
            pd.DataFrame: 包含+DI、-DI和ADX值的DataFrame
        """
        # 計算True Range
        high = self.df['High']
        low = self.df['Low']
        close = self.df['Close']
        prev_close = self.df.groupby(level='Stock')['Close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # 計算Directional Movement
        up_move = high - high.groupby(level='Stock').shift(1)
        down_move = low.groupby(level='Stock').shift(1) - low
        
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
        
        # 計算指標值
        tr_ewm = tr.groupby(level='Stock').transform(lambda x: x.ewm(span=window, adjust=False).mean())
        plus_di = 100 * (plus_dm.groupby(level='Stock').transform(lambda x: 
            x.ewm(span=window, adjust=False).mean()) / tr_ewm)
        minus_di = 100 * (minus_dm.groupby(level='Stock').transform(lambda x: 
            x.ewm(span=window, adjust=False).mean()) / tr_ewm)
        
        # 計算ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.groupby(level='Stock').transform(lambda x: x.ewm(span=window, adjust=False).mean())
        
        return pd.DataFrame({
            'Plus_DI': plus_di,
            'Minus_DI': minus_di,
            'ADX': adx
        })

    def calculate_cci(self, window: Union[int, List[int]] = [14], constant: float = 0.015) -> pd.DataFrame:
        """
        計算商品通道指標 (CCI - Commodity Channel Index)。
        
        計算公式：
        CCI（N日）=（TP－MA）/（0.015 X MD）
        其中：
        - TP =（最高價＋最低價＋收盤價）÷ 3
        - MA = 近N日收盤價的累計之和 ÷ N
        - MD = 近N日（MA－收盤價）的累計之和 ÷ N
        
        Args:
            window (Union[int, List[int]]): 回顧期間，可為單一數值或列表，預設[14]天
            constant (float): 計算係數，預設0.015
            
        Returns:
            pd.DataFrame: 不同時間週期的CCI值，約75%會落在-100到+100之間
        """    
        # 統一處理單值和列表輸入
        if isinstance(window, int):
            windows_list = [window]
        else:
            windows_list = window
            
        # 計算典型價格 (TP)
        tp = (self.df['High'] + self.df['Low'] + self.df['Close']) / 3
        
        cci_dict = {}
        
        for w in windows_list:
            # 計算MA (收盤價的N日簡單移動平均)
            ma = self.df['Close'].groupby(level='Stock').transform(
                lambda x: x.rolling(window=w).mean()
            )
            
            # 計算MD (MA與收盤價差的N日平均)
            md = (abs(ma - self.df['Close'])).groupby(level='Stock').transform(
                lambda x: x.rolling(window=w).mean()
            )
            
            # 計算CCI
            cci = (tp - ma) / (constant * md)
            cci_dict[f'CCI_{w}'] = cci
        
        return pd.DataFrame(cci_dict)
