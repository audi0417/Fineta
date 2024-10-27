# Fineta/pricing/export_to_excel.py

import pandas as pd
from Fineta.crawler import StockPriceFetcher
from Fineta.indicators.technical_indicators import (
    calculate_sma, calculate_ema, calculate_rsi, calculate_bollinger_bands, calculate_macd
)
from FINPLUS.indicators.fundamental_indicators import calculate_fundamentals
from FINPLUS.indicators.risk_indicators import calculate_volatility_and_risk

class ExportToExcel:
    def __init__(self, fetcher: StockPriceFetcher):
        self.fetcher = fetcher
        self.df = self.fetcher.to_dataframe()

    def calculate_technical_indicators(self):
        df = self.df.copy()
        df['SMA_10'] = calculate_sma(df, window=10)
        df['SMA_50'] = calculate_sma(df, window=50)
        df['SMA_200'] = calculate_sma(df, window=200)
        df['EMA_12'] = calculate_ema(df, span=12)
        df['EMA_26'] = calculate_ema(df, span=26)
        df['RSI_14'] = calculate_rsi(df, window=14)
        bollinger_bands = calculate_bollinger_bands(df)
        df['BB_Middle'], df['BB_Upper'], df['BB_Lower'] = bollinger_bands['Middle_Band'], bollinger_bands['Upper_Band'], bollinger_bands['Lower_Band']
        macd_data = calculate_macd(df)
        df['MACD'], df['Signal_Line'] = macd_data['MACD'], macd_data['Signal_Line']
        return df

    def export(self, file_path: str):
        with pd.ExcelWriter(file_path) as writer:
            self.df.to_excel(writer, sheet_name='Price Data')
            technical_df = self.calculate_technical_indicators()
            technical_df.to_excel(writer, sheet_name='Technical Indicators')
            fundamental_df = calculate_fundamentals(self.df)
            fundamental_df.to_excel(writer, sheet_name='Fundamental Analysis')
            risk_df = calculate_volatility_and_risk(self.df)
            risk_df.to_excel(writer, sheet_name='Volatility & Risk')
