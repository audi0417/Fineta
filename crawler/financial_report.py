# FINPLUS/crawler/financial_scraper.py
from FINPLUS.stock import Stock,Portfolio
import requests
import pandas as pd
import time
from datetime import datetime
from io import StringIO
from .exceptions import InvalidTypeError

class FinancialScraper:
    def __init__(self, portfolio: Portfolio, start_date, end_date):
        """
        初始化 FinancialScraper 對象，使用投資組合、開始日期和結束日期。

        Args:
            portfolio (Portfolio): 包含多個股票的投資組合對象。
            start_date (str or datetime): 爬取期間的開始日期。
            end_date (str or datetime): 爬取期間的結束日期。

        Raises:
            ValueError: 如果開始日期晚於結束日期。
        """
        self.portfolio = portfolio
        self.start_date = self._parse_date(start_date)
        self.end_date = self._parse_date(end_date)
        self._validate_date_range()

    def _parse_date(self, date):
        """Parses the input date into a datetime object."""
        return datetime.strptime(date, '%Y-%m-%d') if isinstance(date, str) else date

    def _validate_date_range(self):
        """Validates that the start date is not later than the end date."""
        if self.start_date > self.end_date:
            raise ValueError("start_date must be earlier than end_date")

    def _generate_quarters(self):
        """
        Generates a list of quarters based on the start and end dates.

        Returns:
            list: A list of tuples where each tuple represents a quarter (year, season).
        """
        quarters = []
        current_date = self.start_date

        while current_date <= self.end_date:
            year, season = current_date.year, self._get_season(current_date.month)
            quarters.append((year, season))
            current_date = self._advance_to_next_quarter(current_date, season)

        return quarters

    @staticmethod
    def _get_season(month):
        """Returns the season (1-4) based on the month."""
        return (month - 1) // 3 + 1

    @staticmethod
    def _advance_to_next_quarter(current_date, season):
        """Advances the date to the beginning of the next quarter."""
        return datetime(year=current_date.year + (season == 4), month=1 if season == 4 else season * 3 + 1, day=1)
    def get_portfolio_financial_statements(self, statement_type=None):
        """
        獲取投資組合中所有股票的財務報表。

        Args:
            statement_type (str): 要獲取的財務報表類型。

        Returns:
            dict: 一個字典，其中股票代號為鍵，對應的財務報表 DataFrame 為值。
        """
        portfolio_statements = {}

        for stock in self.portfolio.stocks:
            for stock_id in stock.get_all_stock_ids():
                print(f"Processing financial statements for stock {stock_id}")
                all_data, index_df = {}, None

                for year, season in self._generate_quarters():
                    print(f"Fetching data for {stock_id} - {year} Q{season}...")
                    html = self.fetch_financial_data(stock_id, year, season)
                    time.sleep(5)  # 延遲以避免過於頻繁的請求
                    df = self.parse_financial_data(html, statement_type)
                    df.columns = [f"{year}Q{season}"]

                    if index_df is None:
                        index_df = df.index
                    else:
                        index_df = index_df.union(df.index)

                    all_data[f"{year}Q{season}"] = df

                combined_df = pd.concat(all_data.values(), axis=1, join='outer').reindex(index_df).dropna(how='all')
                portfolio_statements[stock_id] = combined_df

        return portfolio_statements
    def fetch_financial_data(self, stock_id, year, season):
        """
        獲取指定股票、年份和季度的財務數據。

        Args:
            stock_id (str): 股票代號。
            year (int): 要獲取財務數據的年份。
            season (int): 要獲取財務數據的季度（1 代表 Q1，2 代表 Q2，等等）。

        Returns:
            str: 包含財務數據的字符串。
        """
        url = f'https://mops.twse.com.tw/server-java/t164sb01?step=1&CO_ID={stock_id}&SYEAR={year}&SSEASON={season}&REPORT_ID=C#'
        response = requests.post(url)
        response.encoding = 'big5'
        return response.text

    def parse_financial_data(self, html, statement_type):
        """
        Parses the HTML financial data into a DataFrame.

        Args:
            html (str): The HTML string of the financial data.
            statement_type (str): The type of financial statement to parse.

        Returns:
            pandas.DataFrame: A DataFrame containing the financial data with the first two columns as the index.

        Raises:
            InvalidTypeError: If the statement type is invalid.
        """
        statement_types = {'資產負債表': 0, '綜合損益表': 1, '現金流量表': 2}
        if statement_type not in statement_types:
            raise InvalidTypeError(f"Invalid statement type: {statement_type}")

        df = pd.read_html(StringIO(html))[statement_types[statement_type]]
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel()

        df = df.iloc[:, :3].set_index(df.columns[:2].tolist())
        df.columns = ['season']

        return df

    def get_financial_statements(self, statement_type=None):
        """
        Fetches and combines financial data for all quarters within the specified date range.

        Args:
            statement_type (str): The type of financial statement to fetch and parse.

        Returns:
            pandas.DataFrame: A DataFrame containing combined financial data for the specified date range.
        """
        all_data, index_df = {}, None

        for year, season in self._generate_quarters():
            print(f"Fetching data for {year} Q{season}...")
            html = self.fetch_financial_data(year, season)
            time.sleep(5)
            df = self.parse_financial_data(html, statement_type)
            df.columns = [f"{year}Q{season}"]

            if index_df is None:
                index_df = df.index
            else:
                index_df = index_df.union(df.index)

            all_data[f"{year}Q{season}"] = df

        combined_df = pd.concat(all_data.values(), axis=1, join='outer').reindex(index_df).dropna(how='all')
        return combined_df
