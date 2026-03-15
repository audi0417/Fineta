import pandas as pd
import numpy as np
from typing import Optional, Dict
import yfinance as yf
from .return_indicators import ReturnIndicators


class RiskIndicators:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.return_calculator = ReturnIndicators(df)
        self._market_cache: Dict[str, pd.Series] = {}

    def _get_market_returns(self, market_index: str,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> pd.Series:
        """
        取得市場指數日報酬率（帶快取，避免重複下載）。

        Args:
            market_index: 市場指數代碼
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            pd.Series: 市場日報酬率
        """
        cache_key = f"{market_index}_{start_date}_{end_date}"
        if cache_key not in self._market_cache:
            market_data = yf.download(
                market_index, start=start_date, end=end_date, progress=False
            )
            if isinstance(market_data.columns, pd.MultiIndex):
                market_data.columns = market_data.columns.get_level_values(0)
            self._market_cache[cache_key] = market_data['Close'].pct_change().dropna()
        return self._market_cache[cache_key]

    def calculate_beta_alpha(self, market_index: str,
                             risk_free_rate: Optional[float] = None,
                             trading_days: int = 252,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> pd.DataFrame:
        """
        計算Beta值和Alpha值。

        Args:
            market_index (str): 市場指數代碼，例如 '^TWII' 或 '^DJI'
            risk_free_rate (float, optional): 年化無風險利率，例如0.02表示2%
            trading_days (int): 年化交易日數，預設252天
            start_date (str, optional): 開始日期，格式為 'YYYY-MM-DD'
            end_date (str, optional): 結束日期，格式為 'YYYY-MM-DD'

        Returns:
            pd.DataFrame: 包含Beta值和Alpha值的DataFrame
        """
        try:
            if risk_free_rate is None:
                risk_free_rate = 0.02

            # 使用快取取得市場報酬率
            market_returns = self._get_market_returns(market_index, start_date, end_date)

            # 計算個股與市場年化報酬率
            stock_returns = self.return_calculator.calculate_returns(trading_days)
            market_annual_return = float(market_returns.mean() * trading_days)

            metrics = {}
            for stock_id in self.df.index.get_level_values('Stock').unique():
                stock_data = self.df.loc[stock_id]['Close']
                stock_daily_returns = stock_data.pct_change().dropna()

                aligned_data = pd.concat(
                    [stock_daily_returns, market_returns], axis=1
                ).dropna()
                aligned_data.columns = ['stock', 'market']

                if len(aligned_data) > 0:
                    covariance = aligned_data['stock'].cov(aligned_data['market'])
                    market_variance = aligned_data['market'].var()
                    beta = covariance / market_variance

                    stock_return = stock_returns[stock_id]
                    alpha = stock_return - (risk_free_rate + beta * (market_annual_return - risk_free_rate))

                    metrics[stock_id] = {
                        'Beta': beta,
                        'Alpha': alpha,
                        'Stock_Return': stock_return,
                        'Market_Return': market_annual_return,
                    }
                else:
                    metrics[stock_id] = {
                        'Beta': None,
                        'Alpha': None,
                        'Stock_Return': None,
                        'Market_Return': None,
                    }

            return pd.DataFrame.from_dict(metrics, orient='index')

        except Exception as e:
            print(f"計算Beta和Alpha值時發生錯誤: {e}")
            return pd.DataFrame()

    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02,
                               trading_days: int = 252) -> pd.DataFrame:
        """
        計算各股票的 Sharpe Ratio。

        Sharpe Ratio = (年化報酬率 - 無風險利率) / 年化波動率

        Args:
            risk_free_rate: 年化無風險利率，預設 2%
            trading_days: 年化交易日數，預設 252

        Returns:
            pd.DataFrame: 包含 Sharpe_Ratio 欄位
        """
        results = {}
        for stock_id in self.df.index.get_level_values('Stock').unique():
            stock_data = self.df.loc[stock_id]['Close']
            daily_returns = stock_data.pct_change().dropna()

            if len(daily_returns) > 0:
                annual_return = daily_returns.mean() * trading_days
                annual_vol = daily_returns.std() * np.sqrt(trading_days)
                sharpe = (annual_return - risk_free_rate) / annual_vol if annual_vol > 0 else np.nan
                results[stock_id] = {'Sharpe_Ratio': sharpe}
            else:
                results[stock_id] = {'Sharpe_Ratio': None}

        return pd.DataFrame.from_dict(results, orient='index')

    def calculate_information_ratio(self, market_index: str,
                                    trading_days: int = 252,
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None) -> pd.DataFrame:
        """
        計算各股票的 Information Ratio。

        IR = (年化超額報酬) / 追蹤誤差

        Args:
            market_index: 市場指數代碼
            trading_days: 年化交易日數
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            pd.DataFrame: 包含 Information_Ratio, Tracking_Error 欄位
        """
        market_returns = self._get_market_returns(market_index, start_date, end_date)

        results = {}
        for stock_id in self.df.index.get_level_values('Stock').unique():
            stock_data = self.df.loc[stock_id]['Close']
            stock_daily_returns = stock_data.pct_change().dropna()

            aligned = pd.concat(
                [stock_daily_returns.rename('stock'), market_returns.rename('market')],
                axis=1
            ).dropna()

            if len(aligned) > 0:
                excess = aligned['stock'] - aligned['market']
                tracking_error = excess.std() * np.sqrt(trading_days)
                annual_excess = excess.mean() * trading_days
                ir = annual_excess / tracking_error if tracking_error > 0 else np.nan
                results[stock_id] = {
                    'Information_Ratio': ir,
                    'Tracking_Error': tracking_error,
                }
            else:
                results[stock_id] = {
                    'Information_Ratio': None,
                    'Tracking_Error': None,
                }

        return pd.DataFrame.from_dict(results, orient='index')

    def calculate_volatility_and_risk(self, metrics: list = None) -> pd.DataFrame:
        """
        計算指定的風險指標並返回結果。

        Args:
            metrics (list, optional): 使用者希望返回的指標名稱列表。
                支援的選項包括 'Daily_Return', 'Annual_Volatility', 'Cumulative_Return', 'Drawdown', 'Max_Drawdown'。
                若未指定，預設返回全部指標。

        Returns:
            pd.DataFrame: 包含所選指標的 DataFrame。
        """
        df = self.df.copy()

        # 計算每日回報率
        df['Daily_Return'] = df.groupby(level='Stock')['Close'].pct_change()

        # 計算年度歷史波動率
        df['Annual_Volatility'] = df.groupby(level='Stock')['Daily_Return'].transform(
            lambda x: x.rolling(window=252, min_periods=1).std() * np.sqrt(252)
        )

        # 計算累積回報率
        df['Cumulative_Return'] = (1 + df['Daily_Return']).groupby(level='Stock').cumprod()

        # 計算最大回撤
        df['Cumulative_Max'] = df.groupby(level='Stock')['Cumulative_Return'].cummax()
        df['Drawdown'] = df['Cumulative_Return'] / df['Cumulative_Max'] - 1
        df['Max_Drawdown'] = df.groupby(level='Stock')['Drawdown'].cummin()

        # 可選指標
        available_metrics = {
            'Daily_Return': df['Daily_Return'],
            'Annual_Volatility': df['Annual_Volatility'],
            'Cumulative_Return': df['Cumulative_Return'],
            'Drawdown': df['Drawdown'],
            'Max_Drawdown': df['Max_Drawdown'],
        }

        if metrics is None:
            metrics = list(available_metrics.keys())

        selected_metrics = {metric: available_metrics[metric] for metric in metrics if metric in available_metrics}
        risk_metrics = pd.DataFrame(selected_metrics).dropna()

        return risk_metrics
