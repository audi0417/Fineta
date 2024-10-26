# FINPLUS/indicators/fundamental_indicators.py
import pandas as pd
import numpy as np
import json
from urllib.request import urlopen
from datetime import datetime

def fetch_financial_metrics(date: str, stock_no: str) -> pd.DataFrame:
    """
    使用台灣證券交易所 API 獲取指定股票的殖利率及本益比數據。
    
    Args:
        date (str): 查詢日期，格式為 'YYYYMMDD'。
        stock_no (str): 股票代號。
    
    Returns:
        pd.DataFrame: 包含殖利率、本益比及其他基本面指標的 DataFrame。
    """
    url = f'https://www.twse.com.tw/exchangeReport/BWIBBU?response=json&date={date}&stockNo={stock_no}'
    response = urlopen(url)
    data = json.loads(response.read())

    # 將數據轉換為 DataFrame
    df = pd.DataFrame(data['data'], columns=data['fields'])
    df['Stock'] = stock_no  # 新增股票代號欄位
    return df

def calculate_fundamentals(df: pd.DataFrame, date: str) -> pd.DataFrame:
    """
    計算股票的基本面指標，包括殖利率、本益比等，使用台灣證券交易所 API 數據。
    
    Args:
        df (pd.DataFrame): 包含股票代號的 DataFrame。
        date (str): 查詢日期，格式為 'YYYYMMDD'。
    
    Returns:
        pd.DataFrame: 包含基本面指標的 DataFrame。
    """
    fundamental_data = {
        'Stock': [],
        'Dividend Yield': [],
        'P/E': [],
        'P/B': [],
    }

    for stock in df['Stock'].unique():
        stock_data = fetch_financial_metrics(date, stock)
        
        # 解析所需數據並添加至結果字典
        fundamental_data['Stock'].append(stock)
        fundamental_data['Dividend Yield'].append(stock_data['殖利率(%)'].astype(float).values[0])
        fundamental_data['P/E'].append(stock_data['本益比'].astype(float).values[0])
        fundamental_data['P/B'].append(stock_data['股價淨值比'].astype(float).values[0])

    return pd.DataFrame(fundamental_data)
