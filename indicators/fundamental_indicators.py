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
        """
        初始化 FundamentalIndicators。

        Args:
            start_date (str): 開始日期（格式：YYYY-MM-DD）
            end_date (str): 結束日期（格式：YYYY-MM-DD）
        """
        self.start_date = self._convert_date_format(start_date)
        self.end_date = self._convert_date_format(end_date)
        self.context = ssl._create_unverified_context()

    def _convert_date_format(self, date_str: str) -> str:
        """
        將 YYYY-MM-DD 格式轉換為 YYYYMMDD 格式

        Args:
            date_str (str): YYYY-MM-DD 格式的日期

        Returns:
            str: YYYYMMDD 格式的日期
        """
        return date_str.replace('-', '')


    def _convert_to_float(self, value):
        """
        將字串轉換為浮點數，處理特殊字元。

        Args:
            value: 要轉換的值

        Returns:
            float 或 None: 轉換後的數值，如果無法轉換則返回 None
        """
        if isinstance(value, str):
            # 移除千分位逗號和空白
            value = value.replace(',', '').strip()
            # 處理特殊字元
            if value in ['-', '', 'N/A']:
                return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _generate_month_range(self) -> List[str]:
        """生成月份範圍內的日期列表（每月的第一天）"""
        start = datetime.strptime(self.start_date, '%Y%m%d')
        end = datetime.strptime(self.end_date, '%Y%m%d')
        date_list = []
        while start <= end:
            date_list.append(start.strftime('%Y%m%d'))
            start = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        return date_list

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
        計算股票的基本面指標。

        Args:
            portfolio: Portfolio 對象
            max_workers: 最大執行緒數

        Returns:
            Dict[str, pd.DataFrame]: 股票代號對應的基本面指標 DataFrame
        """
        date_range = self._generate_month_range()
        stock_ids = portfolio.get_all_stock_ids()
        results = {stock: [] for stock in stock_ids}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for date in date_range:
                for stock in stock_ids:
                    futures.append(executor.submit(self._fetch_financial_metrics, date, stock))

            for future in as_completed(futures):
                stock_data = future.result()
                if not stock_data.empty:
                    stock_no = stock_data['Stock'].values[0]
                    try:
                        results[stock_no].append({
                            'Date': stock_data['Date'].values[0],
                            'Dividend Yield': self._convert_to_float(stock_data['殖利率(%)'].values[0]),
                            'P/E': self._convert_to_float(stock_data['本益比'].values[0]),
                            'P/B': self._convert_to_float(stock_data['股價淨值比'].values[0]),
                        })
                    except (IndexError, KeyError) as e:
                        print(f"Error processing data for stock {stock_no}: {e}")
                        continue

        # 整理結果
        result_dfs = {}
        for stock, data in results.items():
            if data:  # 只處理有資料的股票
                df = pd.DataFrame(data)
                df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
                df = df.sort_values(by='Date').reset_index(drop=True)
                result_dfs[stock] = df

        return result_dfs
