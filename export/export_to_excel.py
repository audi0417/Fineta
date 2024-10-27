import pandas as pd
from Fineta.crawler.stock_price_fetcher import StockPriceFetcher
from Fineta.indicators.technical_indicators import TechnicalIndicators
from Fineta.indicators.fundamental_indicators import FundamentalIndicators
from Fineta.indicators.risk_indicators import RiskIndicators
from Fineta.stock import Portfolio

class ExportToExcel:
    def __init__(self, fetcher: StockPriceFetcher, start_date: str, end_date: str, portfolio: Portfolio):
        """
        初始化 ExportToExcel 實例。

        Args:
            fetcher (StockPriceFetcher): 用於取得股價資料的實例
            start_date (str): 開始日期（格式：YYYY-MM-DD）
            end_date (str): 結束日期（格式：YYYY-MM-DD）
            portfolio (Portfolio): 投資組合實例
        """
        self.fetcher = fetcher
        self.df = self.fetcher.to_dataframe()
        self.start_date = self._convert_date_format(start_date)
        self.end_date = self._convert_date_format(end_date)
        self.portfolio = portfolio
        self.technical_indicators = TechnicalIndicators(self.df)

    def _convert_date_format(self, date_str: str) -> str:
        """
        將 YYYY-MM-DD 格式轉換為 YYYYMMDD 格式（用於 API 請求）

        Args:
            date_str (str): YYYY-MM-DD 格式的日期

        Returns:
            str: YYYYMMDD 格式的日期
        """
        return date_str.replace('-', '')

    def calculate_technical_indicators(self):
        """計算技術指標"""
        df = self.df.copy()
        
        # 計算技術指標
        df['SMA_10'] = self.technical_indicators.calculate_sma(window=10)
        df['SMA_50'] = self.technical_indicators.calculate_sma(window=50)
        df['SMA_200'] = self.technical_indicators.calculate_sma(window=200)
        df['EMA_12'] = self.technical_indicators.calculate_ema(span=12)
        df['EMA_26'] = self.technical_indicators.calculate_ema(span=26)
        df['RSI_14'] = self.technical_indicators.calculate_rsi(window=14)

        # 計算布林帶
        bollinger_bands = self.technical_indicators.calculate_bollinger_bands(window=20)
        df['BB_Middle'] = bollinger_bands['Middle_Band']
        df['BB_Upper'] = bollinger_bands['Upper_Band']
        df['BB_Lower'] = bollinger_bands['Lower_Band']

        # 計算 MACD 和信號線
        macd_data = self.technical_indicators.calculate_macd()
        df['MACD'] = macd_data['MACD']
        df['Signal_Line'] = macd_data['Signal_Line']
        
        return df

    def calculate_fundamentals(self):
        """計算基本面指標"""
        fundamental_indicator = FundamentalIndicators(self.start_date, self.end_date)
        return fundamental_indicator.calculate_fundamentals(self.portfolio)

    def calculate_risk_indicators(self):
        """計算風險指標"""
        metrics = ['Daily_Return', 'Annual_Volatility', 'Cumulative_Return', 'Drawdown', 'Max_Drawdown']
        risk_calculator = RiskIndicators(self.df)
        return risk_calculator.calculate_volatility_and_risk(metrics)

    def export(self, file_path: str):
        """
        將所有分析結果匯出至 Excel 檔案。

        Args:
            file_path (str): Excel 檔案的儲存路徑
        """
        with pd.ExcelWriter(file_path) as writer:
            # 股價數據
            self.df.to_excel(writer, sheet_name='Price Data')

            # 技術指標
            technical_df = self.calculate_technical_indicators()
            technical_df.to_excel(writer, sheet_name='Technical Indicators')

            # 基本面指標
            fundamental_dfs = self.calculate_fundamentals()
            for stock_id, df in fundamental_dfs.items():
                df.to_excel(writer, sheet_name=f'Fundamental_{stock_id}')

            # 風險指標
            risk_df = self.calculate_risk_indicators()
            risk_df.to_excel(writer, sheet_name='Volatility & Risk')
