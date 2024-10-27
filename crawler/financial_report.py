# Fineta/crawler/financial_report.py

import requests
import pandas as pd
import time
from datetime import datetime
from io import StringIO
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from .exceptions import InvalidTypeError
from Fineta.stock import Stock, Portfolio

class FinancialReportScraper:
    """財務報表爬蟲類別，用於從台灣證券交易所獲取企業財務報表"""

    def __init__(self, portfolio: Portfolio, start_date: str, end_date: str):
        """
        初始化財務報表爬蟲。

        Args:
            portfolio (Portfolio): 包含多個股票的投資組合對象
            start_date (str): 開始日期，格式：YYYY-MM-DD
            end_date (str): 結束日期，格式：YYYY-MM-DD

        Raises:
            ValueError: 如果開始日期晚於結束日期
        """
        self.portfolio = portfolio
        self.start_date = self._parse_date(start_date)
        self.end_date = self._parse_date(end_date)
        self._validate_date_range()
        self.statement_types = {
            '資產負債表': 0,
            '綜合損益表': 1,
            '現金流量表': 2
        }

    def _parse_date(self, date: str) -> datetime:
        """
        將日期字符串轉換為 datetime 對象。

        Args:
            date (str): 日期字符串，格式：YYYY-MM-DD

        Returns:
            datetime: datetime 對象
        """
        return datetime.strptime(date, '%Y-%m-%d')

    def _validate_date_range(self) -> None:
        """
        驗證日期範圍的有效性。

        Raises:
            ValueError: 如果開始日期晚於結束日期
        """
        if self.start_date > self.end_date:
            raise ValueError("開始日期不能晚於結束日期")

    def _get_season(self, month: int) -> int:
        """
        根據月份確定所屬季度。

        Args:
            month (int): 月份（1-12）

        Returns:
            int: 季度（1-4）
        """
        return (month - 1) // 3 + 1

    def _advance_to_next_quarter(self, current_date: datetime, season: int) -> datetime:
        """
        將日期推進到下一季度的開始。

        Args:
            current_date (datetime): 當前日期
            season (int): 當前季度

        Returns:
            datetime: 下一季度的開始日期
        """
        return datetime(
            year=current_date.year + (season == 4),
            month=1 if season == 4 else season * 3 + 1,
            day=1
        )

    def _generate_quarters(self) -> List[Tuple[int, int]]:
        """
        生成日期範圍內的所有季度。

        Returns:
            List[Tuple[int, int]]: 包含 (年份, 季度) 的列表
        """
        quarters = []
        current_date = self.start_date

        while current_date <= self.end_date:
            year = current_date.year
            season = self._get_season(current_date.month)
            quarters.append((year, season))
            current_date = self._advance_to_next_quarter(current_date, season)

        return quarters

    def fetch_financial_data(self, stock_id: str, year: int, season: int) -> Optional[str]:
        """
        獲取指定股票、年份和季度的財務數據。

        Args:
            stock_id (str): 股票代號
            year (int): 年份
            season (int): 季度（1-4）

        Returns:
            Optional[str]: 包含財務數據的HTML字符串，若請求失敗則返回None
        """
        url = (
            f'https://mops.twse.com.tw/server-java/t164sb01?'
            f'step=1&CO_ID={stock_id}&SYEAR={year}&'
            f'SSEASON={season}&REPORT_ID=C#'
        )
        
        try:
            response = requests.post(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'big5'
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {stock_id} {year}Q{season}: {e}")
            return None

    def parse_financial_data(self, html: str, statement_type: str) -> pd.DataFrame:
        """
        解析財務報表HTML數據。

        Args:
            html (str): 財務報表HTML內容
            statement_type (str): 報表類型（'資產負債表'、'綜合損益表'或'現金流量表'）

        Returns:
            pd.DataFrame: 解析後的財務數據

        Raises:
            InvalidTypeError: 如果報表類型無效
        """
        if statement_type not in self.statement_types:
            raise InvalidTypeError(f"無效的報表類型: {statement_type}")

        try:
            df = pd.read_html(StringIO(html))[self.statement_types[statement_type]]
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel()

            df = df.iloc[:, :3].set_index(df.columns[:2].tolist())
            df.columns = ['season']
            return df
        except Exception as e:
            print(f"解析數據時發生錯誤: {e}")
            return pd.DataFrame()

    def get_financial_statements(self, stock_id: str, statement_type: str, max_workers: int = 5) -> pd.DataFrame:
        """
        獲取單一股票的財務報表數據。

        Args:
            stock_id (str): 股票代號
            statement_type (str): 報表類型
            max_workers (int): 最大線程數

        Returns:
            pd.DataFrame: 合併後的財務報表，按季度排序
        """
        quarters = self._generate_quarters()
        all_data = {}
        index_df = None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_quarter = {
                executor.submit(self.fetch_financial_data, stock_id, year, season): (year, season)
                for year, season in quarters
            }

            for future in as_completed(future_to_quarter):
                year, season = future_to_quarter[future]
                html = future.result()
                
                if html:
                    df = self.parse_financial_data(html, statement_type)
                    if not df.empty:
                        column_name = f"{year}Q{season}"
                        df.columns = [column_name]
                        
                        if index_df is None:
                            index_df = df.index
                        else:
                            index_df = index_df.union(df.index)
                        
                        all_data[column_name] = df
                        
                time.sleep(3)  # 避免請求過於頻繁

        if all_data:
            # 創建排序用的映射字典
            column_order = {}
            for year, season in quarters:
                column_name = f"{year}Q{season}"
                # 使用年份和季度創建一個可排序的鍵值
                column_order[column_name] = year * 10 + season

            # 根據年份和季度排序列名
            sorted_columns = sorted(all_data.keys(), key=lambda x: column_order[x])
            
            # 按照排序後的列名合併數據
            return pd.concat(
                [all_data[col] for col in sorted_columns],
                axis=1,
                join='outer'
            ).reindex(index_df).dropna(how='all')
        
        return pd.DataFrame()

    def get_portfolio_financial_statements(self, statement_type: str) -> Dict[str, pd.DataFrame]:
        """
        獲取投資組合中所有股票的財務報表。

        Args:
            statement_type (str): 報表類型

        Returns:
            Dict[str, pd.DataFrame]: 股票代號對應的財務報表字典
        """
        portfolio_statements = {}
        
        for stock in self.portfolio.stocks:
            for stock_id in stock.get_all_stock_ids():
                print(f"\n處理 {stock_id} 的財務報表...")
                df = self.get_financial_statements(stock_id, statement_type)
                if not df.empty:
                    portfolio_statements[stock_id] = df
                    print(f"{stock_id} 財務報表處理完成")
                else:
                    print(f"{stock_id} 沒有可用的財務報表數據")

        return portfolio_statements
