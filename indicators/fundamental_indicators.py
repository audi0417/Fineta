import pandas as pd
import json
import time
import ssl
from urllib.request import urlopen
from datetime import datetime, timedelta
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from Fineta.stock import Portfolio

class FundamentalIndicators:
    """
    使用台灣證券交易所 API 計算股票的基本面指標，包括殖利率、本益比、股價淨值比等。
    """

    def __init__(self, start_date: str, end_date: str):
        self.start_date = start_date
        self.end_date = end_date
        self.context = ssl._create_unverified_context()  # 忽略 SSL 證書驗證

    def _fetch_financial_metrics(self, date: str, stock_no: str, retries: int = 3, delay: int = 5) -> pd.DataFrame:
        url = f'https://www.twse.com.tw/exchangeReport/BWIBBU?response=json&date={date}&stockNo={stock_no}'
        attempts = 0

        while attempts < retries:
            try:
                response = urlopen(url, context=self.context)
                data = json.loads(response.read())
                df = pd.DataFrame(data['data'], columns=data['fields'])
                df['Stock'] = stock_no
                df['Date'] = date
                return df
            except Exception as e:
                attempts += 1
                print(f"Error fetching data for {stock_no} on {date}: {e}")
                if attempts < retries:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Failed to fetch data for {stock_no} on {date} after {retries} attempts.")
                    return pd.DataFrame()

    def _generate_month_range(self) -> List[str]:
        """
        生成月份範圍內的日期列表（每月的第一天）。
        
        Returns:
            List[str]: 包含所有月份的列表，格式 'YYYYMM01'。
        """
        start = datetime.strptime(self.start_date, '%Y%m%d')
        end = datetime.strptime(self.end_date, '%Y%m%d')
        date_list = []
        while start <= end:
            date_list.append(start.strftime('%Y%m01'))  # 只保留每月的第一天
            # 移動到下個月
            start = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        return date_list

    def calculate_fundamentals(self, portfolio: Portfolio, max_workers: int = 5) -> Dict[str, pd.DataFrame]:
        """
        計算股票的基本面指標，支持多日期範圍，並使用多線程加速抓取。

        Args:
            portfolio (Portfolio): 包含多個股票對象的 Portfolio 對象。
            max_workers (int): 最大線程數，默認為 5。

        Returns:
            Dict[str, pd.DataFrame]: 每支股票代號對應一個 DataFrame，包含基本面指標和日期的 dict。
        """
        date_range = self._generate_month_range()
        stock_ids = portfolio.get_all_stock_ids()
        results = {stock: [] for stock in stock_ids}  # 初始化每個股票的結果列表

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for date in date_range:
                for stock in stock_ids:
                    futures.append(executor.submit(self._fetch_financial_metrics, date, stock))

            for future in as_completed(futures):
                stock_data = future.result()
                if stock_data is not None and not stock_data.empty:
                    stock_no = stock_data['Stock'].values[0]
                    results[stock_no].append({
                        'Date': stock_data['Date'].values[0],
                        'Dividend Yield': stock_data['殖利率(%)'].astype(float).values[0],
                        'P/E': stock_data['本益比'].astype(float).values[0],
                        'P/B': stock_data['股價淨值比'].astype(float).values[0],
                    })

        # 將每支股票的結果整理為 DataFrame 並按日期排序
        result_dfs = {}
        for stock, data in results.items():
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
            df = df.sort_values(by='Date').reset_index(drop=True)
            result_dfs[stock] = df

        return result_dfs
