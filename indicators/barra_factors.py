import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
import yfinance as yf


class BarraFactors:
    """
    Barra 風格多因子模型，計算股票的因子暴露度、因子報酬率及風險分解。

    支援的風格因子：
    - Size: 市值因子 (以股價 × 成交量為代理變數)
    - Beta: 市場敏感度因子
    - Momentum: 動量因子 (過去N日累積報酬)
    - Volatility: 波動率因子 (歷史波動率)
    - Liquidity: 流動性因子 (成交量周轉率)
    - Value: 價值因子 (需外部提供淨值比資料)

    使用方式：
        barra = BarraFactors(df)
        exposures = barra.calculate_factor_exposures(market_index='^TWII')
        factor_returns = barra.estimate_factor_returns(market_index='^TWII')
        decomposition = barra.decompose_risk(market_index='^TWII')
    """

    STYLE_FACTORS = ['Size', 'Beta', 'Momentum', 'Volatility', 'Liquidity']

    def __init__(self, df: pd.DataFrame):
        """
        初始化 BarraFactors。

        Args:
            df (pd.DataFrame): 含有 MultiIndex (Stock, Date) 的 DataFrame，
                               需包含 'Close' 和 'Volume' 欄位。
        """
        self.df = df.copy()
        self._market_cache: Dict[str, pd.Series] = {}

    def _get_market_returns(self, market_index: str,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> pd.Series:
        """取得市場指數日報酬率（帶快取）。"""
        cache_key = f"{market_index}_{start_date}_{end_date}"
        if cache_key not in self._market_cache:
            market_data = yf.download(
                market_index, start=start_date, end=end_date,
                progress=False
            )
            if isinstance(market_data.columns, pd.MultiIndex):
                market_data.columns = market_data.columns.get_level_values(0)
            self._market_cache[cache_key] = market_data['Close'].pct_change().dropna()
        return self._market_cache[cache_key]

    @staticmethod
    def _zscore(series: pd.Series) -> pd.Series:
        """將序列標準化為 Z-score (截面標準化)。"""
        mean = series.mean()
        std = series.std()
        if std == 0 or np.isnan(std):
            return pd.Series(0.0, index=series.index)
        return (series - mean) / std

    @staticmethod
    def _winsorize(series: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
        """對序列做 Winsorize 處理，防止極端值影響。"""
        q_low = series.quantile(lower)
        q_high = series.quantile(upper)
        return series.clip(lower=q_low, upper=q_high)

    def _compute_size_factor(self) -> pd.Series:
        """計算 Size 因子：以 log(Close × Volume) 作為市值代理。"""
        df = self.df.copy()
        df['_market_cap_proxy'] = np.log(df['Close'] * df['Volume'] + 1)
        # 使用 transform 保留原始 MultiIndex 結構，避免 groupby.apply 產生額外索引層
        result = df.groupby(level='Date')['_market_cap_proxy'].transform(
            lambda x: self._zscore(self._winsorize(x))
        )
        return result.rename('Size')

    def _compute_beta_factor(self, market_index: str,
                             window: int = 60,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> pd.Series:
        """計算 Beta 因子：滾動窗口迴歸 Beta。"""
        market_returns = self._get_market_returns(market_index, start_date, end_date)

        betas = {}
        for stock_id in self.df.index.get_level_values('Stock').unique():
            stock_close = self.df.loc[stock_id, 'Close']
            stock_returns = stock_close.pct_change().dropna()

            aligned = pd.concat(
                [stock_returns.rename('stock'), market_returns.rename('market')],
                axis=1
            ).dropna()

            if len(aligned) < window:
                rolling_beta = pd.Series(np.nan, index=aligned.index)
            else:
                cov = aligned['stock'].rolling(window).cov(aligned['market'])
                var = aligned['market'].rolling(window).var()
                rolling_beta = cov / var

            for date, beta_val in rolling_beta.items():
                betas[(stock_id, date)] = beta_val

        beta_series = pd.Series(betas, name='Beta')
        beta_series.index = pd.MultiIndex.from_tuples(beta_series.index, names=['Stock', 'Date'])

        # 截面標準化
        beta_df = beta_series.reset_index()
        beta_df.columns = ['Stock', 'Date', 'Beta']
        beta_df['Beta'] = beta_df.groupby('Date')['Beta'].transform(
            lambda x: self._zscore(self._winsorize(x))
        )
        beta_df = beta_df.set_index(['Stock', 'Date'])
        return beta_df['Beta']

    def _compute_momentum_factor(self, lookback: int = 120, skip: int = 20) -> pd.Series:
        """
        計算 Momentum 因子：過去 lookback 日累積報酬，跳過最近 skip 日。

        Args:
            lookback: 回看天數 (預設 120 日，約半年)
            skip: 跳過最近天數 (預設 20 日，避免短期反轉效應)
        """
        momentum_values = {}
        for stock_id in self.df.index.get_level_values('Stock').unique():
            stock_close = self.df.loc[stock_id, 'Close']
            returns = stock_close.pct_change()
            # 累積報酬: 從 t-lookback 到 t-skip
            cum_return = (1 + returns).rolling(lookback).apply(
                lambda x: np.prod(x[:len(x) - skip]) - 1 if len(x) > skip else np.nan,
                raw=False
            )
            for date, val in cum_return.items():
                momentum_values[(stock_id, date)] = val

        mom_series = pd.Series(momentum_values, name='Momentum')
        mom_series.index = pd.MultiIndex.from_tuples(mom_series.index, names=['Stock', 'Date'])

        mom_df = mom_series.reset_index()
        mom_df.columns = ['Stock', 'Date', 'Momentum']
        mom_df['Momentum'] = mom_df.groupby('Date')['Momentum'].transform(
            lambda x: self._zscore(self._winsorize(x))
        )
        mom_df = mom_df.set_index(['Stock', 'Date'])
        return mom_df['Momentum']

    def _compute_volatility_factor(self, window: int = 60) -> pd.Series:
        """計算 Volatility 因子：滾動窗口年化波動率。"""
        vol_values = {}
        for stock_id in self.df.index.get_level_values('Stock').unique():
            stock_close = self.df.loc[stock_id, 'Close']
            daily_returns = stock_close.pct_change()
            rolling_vol = daily_returns.rolling(window).std() * np.sqrt(252)
            for date, val in rolling_vol.items():
                vol_values[(stock_id, date)] = val

        vol_series = pd.Series(vol_values, name='Volatility')
        vol_series.index = pd.MultiIndex.from_tuples(vol_series.index, names=['Stock', 'Date'])

        vol_df = vol_series.reset_index()
        vol_df.columns = ['Stock', 'Date', 'Volatility']
        vol_df['Volatility'] = vol_df.groupby('Date')['Volatility'].transform(
            lambda x: self._zscore(self._winsorize(x))
        )
        vol_df = vol_df.set_index(['Stock', 'Date'])
        return vol_df['Volatility']

    def _compute_liquidity_factor(self, window: int = 20) -> pd.Series:
        """計算 Liquidity 因子：滾動平均成交量對數。"""
        liq_values = {}
        for stock_id in self.df.index.get_level_values('Stock').unique():
            stock_volume = self.df.loc[stock_id, 'Volume']
            rolling_avg_vol = np.log(stock_volume.rolling(window).mean() + 1)
            for date, val in rolling_avg_vol.items():
                liq_values[(stock_id, date)] = val

        liq_series = pd.Series(liq_values, name='Liquidity')
        liq_series.index = pd.MultiIndex.from_tuples(liq_series.index, names=['Stock', 'Date'])

        liq_df = liq_series.reset_index()
        liq_df.columns = ['Stock', 'Date', 'Liquidity']
        liq_df['Liquidity'] = liq_df.groupby('Date')['Liquidity'].transform(
            lambda x: self._zscore(self._winsorize(x))
        )
        liq_df = liq_df.set_index(['Stock', 'Date'])
        return liq_df['Liquidity']

    def calculate_factor_exposures(
        self,
        market_index: str = '^TWII',
        factors: Optional[List[str]] = None,
        beta_window: int = 60,
        momentum_lookback: int = 120,
        momentum_skip: int = 20,
        volatility_window: int = 60,
        liquidity_window: int = 20,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        計算各股票在各因子上的暴露度 (Z-score 標準化)。

        Args:
            market_index: 市場指數代碼，預設台灣加權指數
            factors: 要計算的因子列表，預設全部
            beta_window: Beta 計算的滾動窗口天數
            momentum_lookback: Momentum 回看天數
            momentum_skip: Momentum 跳過近期天數
            volatility_window: Volatility 滾動窗口天數
            liquidity_window: Liquidity 滾動窗口天數
            start_date: 市場資料開始日期
            end_date: 市場資料結束日期

        Returns:
            pd.DataFrame: MultiIndex (Stock, Date)，欄位為各因子暴露度
        """
        if factors is None:
            factors = self.STYLE_FACTORS

        factor_series = {}

        if 'Size' in factors:
            factor_series['Size'] = self._compute_size_factor()
        if 'Beta' in factors:
            factor_series['Beta'] = self._compute_beta_factor(
                market_index, beta_window, start_date, end_date
            )
        if 'Momentum' in factors:
            factor_series['Momentum'] = self._compute_momentum_factor(
                momentum_lookback, momentum_skip
            )
        if 'Volatility' in factors:
            factor_series['Volatility'] = self._compute_volatility_factor(volatility_window)
        if 'Liquidity' in factors:
            factor_series['Liquidity'] = self._compute_liquidity_factor(liquidity_window)

        exposures = pd.DataFrame(factor_series)
        exposures.index.names = ['Stock', 'Date']
        return exposures

    def estimate_factor_returns(
        self,
        market_index: str = '^TWII',
        factors: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        使用截面迴歸 (Cross-Sectional Regression) 估計因子報酬率。

        對每個交易日 t，以個股報酬率為應變數、因子暴露度為自變數，
        進行 OLS 迴歸：r_i,t = Σ(f_k,t × X_i,k,t) + ε_i,t

        Args:
            market_index: 市場指數代碼
            factors: 要包含的因子列表
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            pd.DataFrame: index=Date，欄位為各因子報酬率
        """
        exposures = self.calculate_factor_exposures(
            market_index=market_index, factors=factors,
            start_date=start_date, end_date=end_date
        )

        # 計算個股日報酬率
        daily_returns = self.df.groupby(level='Stock')['Close'].pct_change()
        daily_returns.name = 'Return'

        merged = exposures.join(daily_returns, how='inner').dropna()

        factor_cols = [c for c in exposures.columns if c in merged.columns]
        n_factors = len(factor_cols)
        factor_returns_list = []

        for date in merged.index.get_level_values('Date').unique():
            day_data = merged.xs(date, level='Date').dropna()
            if len(day_data) < 2:
                continue

            X = day_data[factor_cols].values
            y = day_data['Return'].values
            n_obs = len(day_data)

            # Ridge 正規化回歸：f = (X'X + λI)^{-1} X'y
            # 當 n_obs >= n_factors 時 λ 很小（近似 OLS）；欠定時加大正規化強度
            lambda_ridge = 1e-4 if n_obs >= n_factors else 1e-2
            try:
                XtX = X.T @ X
                Xty = X.T @ y
                f_hat = np.linalg.solve(XtX + lambda_ridge * np.eye(n_factors), Xty)
                factor_returns_list.append(
                    dict(zip(['Date'] + factor_cols, [date] + f_hat.tolist()))
                )
            except np.linalg.LinAlgError:
                continue

        if not factor_returns_list:
            return pd.DataFrame()

        factor_returns_df = pd.DataFrame(factor_returns_list).set_index('Date').sort_index()
        return factor_returns_df

    def decompose_risk(
        self,
        market_index: str = '^TWII',
        factors: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        風險分解：將個股總風險拆解為因子風險與特定風險。

        計算方式：
        - 因子報酬率協方差矩陣 F
        - 個股因子暴露 X_i
        - 因子風險 = X_i' F X_i
        - 特定風險 = 總方差 - 因子風險
        - R² = 因子風險 / 總風險

        Args:
            market_index: 市場指數代碼
            factors: 要包含的因子列表
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            pd.DataFrame: 每支股票的 Total_Risk, Factor_Risk, Specific_Risk, R_Squared
        """
        factor_returns = self.estimate_factor_returns(
            market_index=market_index, factors=factors,
            start_date=start_date, end_date=end_date
        )

        if factor_returns.empty:
            return pd.DataFrame()

        exposures = self.calculate_factor_exposures(
            market_index=market_index, factors=factors,
            start_date=start_date, end_date=end_date
        )

        factor_cols = factor_returns.columns.tolist()
        # 因子報酬率協方差矩陣 (年化)
        F = factor_returns[factor_cols].cov() * 252

        daily_returns = self.df.groupby(level='Stock')['Close'].pct_change()

        results = {}
        for stock_id in self.df.index.get_level_values('Stock').unique():
            # 個股平均因子暴露
            try:
                stock_exp = exposures.loc[stock_id][factor_cols].mean()
            except KeyError:
                continue

            x = stock_exp.values
            factor_risk = float(x @ F.values @ x)

            stock_ret = daily_returns.loc[stock_id].dropna()
            total_risk = float(stock_ret.var() * 252)

            specific_risk = max(total_risk - factor_risk, 0.0)
            r_squared = factor_risk / total_risk if total_risk > 0 else 0.0

            results[stock_id] = {
                'Total_Risk': total_risk,
                'Factor_Risk': factor_risk,
                'Specific_Risk': specific_risk,
                'R_Squared': min(r_squared, 1.0),
            }

        return pd.DataFrame.from_dict(results, orient='index')

    def get_factor_correlation(
        self,
        market_index: str = '^TWII',
        factors: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        計算因子報酬率之間的相關性矩陣。

        Args:
            market_index: 市場指數代碼
            factors: 因子列表
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            pd.DataFrame: 因子報酬率相關性矩陣
        """
        factor_returns = self.estimate_factor_returns(
            market_index=market_index, factors=factors,
            start_date=start_date, end_date=end_date
        )
        if factor_returns.empty:
            return pd.DataFrame()
        return factor_returns.corr()

    def get_cumulative_factor_returns(
        self,
        market_index: str = '^TWII',
        factors: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        計算因子累積報酬率時序。

        Args:
            market_index: 市場指數代碼
            factors: 因子列表
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            pd.DataFrame: 各因子的累積報酬率
        """
        factor_returns = self.estimate_factor_returns(
            market_index=market_index, factors=factors,
            start_date=start_date, end_date=end_date
        )
        if factor_returns.empty:
            return pd.DataFrame()
        return (1 + factor_returns).cumprod()
