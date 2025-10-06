"""
高级量化指标模块
集成多种量化分析指标来增强投资组合优化和夏普比率最大化
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class AdvancedQuantIndicators:
    """高级量化指标计算类"""

    def __init__(self, trading_days: int = 252):
        """
        初始化高级量化指标计算器

        Args:
            trading_days: 年交易天数
        """
        self.trading_days = trading_days

    def calculate_momentum_indicators(self, returns: pd.DataFrame,
                                    windows: List[int] = [5, 20, 60]) -> Dict[str, pd.DataFrame]:
        """
        计算动量指标

        Args:
            returns: 收益率DataFrame
            windows: 计算窗口列表

        Returns:
            各种动量指标的字典
        """
        momentum_data = {}

        for window in windows:
            # 动量因子
            momentum = returns.rolling(window=window).mean()
            momentum_data[f'momentum_{window}d'] = momentum

            # 动量强度
            momentum_strength = momentum / returns.rolling(window=window).std()
            momentum_data[f'momentum_strength_{window}d'] = momentum_strength

            # 价格动量
            price_momentum = (returns > 0).rolling(window=window).mean()
            momentum_data[f'price_momentum_{window}d'] = price_momentum

        return momentum_data

    def calculate_reversal_indicators(self, returns: pd.DataFrame,
                                    windows: List[int] = [5, 20]) -> Dict[str, pd.DataFrame]:
        """
        计算反转指标

        Args:
            returns: 收益率DataFrame
            windows: 计算窗口列表

        Returns:
            各种反转指标的字典
        """
        reversal_data = {}

        for window in windows:
            # 短期反转
            short_term_reversal = -returns.rolling(window=window).mean()
            reversal_data[f'short_term_reversal_{window}d'] = short_term_reversal

            # 长期反转
            long_term_reversal = returns.rolling(window=window).sum()
            reversal_data[f'long_term_reversal_{window}d'] = long_term_reversal

        return reversal_data

    def calculate_quality_indicators(self, returns: pd.DataFrame,
                                   prices: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        计算质量指标

        Args:
            returns: 收益率DataFrame
            prices: 价格DataFrame

        Returns:
            质量指标字典
        """
        quality_data = {}

        # 1. 盈利质量 - 夏普比率的稳定性
        rolling_sharpe = returns.rolling(window=60).apply(
            lambda x: np.sqrt(self.trading_days) * x.mean() / x.std() if x.std() > 0 else 0
        )
        quality_data['sharpe_stability'] = rolling_sharpe.std()

        # 2. 盈利一致性 - 正收益比例
        positive_returns_ratio = (returns > 0).rolling(window=60).mean()
        quality_data['return_consistency'] = positive_returns_ratio.mean()

        # 3. 波动率质量 - 下行波动率占比
        downside_vol = returns[returns < 0].std() * np.sqrt(self.trading_days)
        total_vol = returns.std() * np.sqrt(self.trading_days)
        quality_data['volatility_quality'] = 1 - (downside_vol / total_vol) if total_vol > 0 else 0

        # 4. 价格质量 - 相对强弱指数(RSI)
        def calculate_rsi(prices_series, period=14):
            delta = prices_series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        rsi_values = prices.apply(calculate_rsi)
        quality_data['rsi_score'] = rsi_values.mean()

        return quality_data

    def calculate_value_indicators(self, prices: pd.DataFrame,
                                 fundamentals: Optional[Dict] = None) -> Dict[str, pd.Series]:
        """
        计算价值指标

        Args:
            prices: 价格DataFrame
            fundamentals: 基本面数据字典（可选）

        Returns:
            价值指标字典
        """
        value_data = {}

        # 1. 相对价格强度
        price_momentum_20d = prices.pct_change(20)
        price_momentum_60d = prices.pct_change(60)
        value_data['relative_strength'] = price_momentum_20d / price_momentum_60d

        # 2. 价格相对位置
        price_rank = prices.rolling(window=252).rank(pct=True)
        value_data['price_percentile'] = price_rank.iloc[-1]

        # 3. 移动平均比率
        ma_20d = prices.rolling(window=20).mean()
        ma_60d = prices.rolling(window=60).mean()
        value_data['ma_ratio'] = ma_20d / ma_60d

        return value_data

    def calculate_technical_indicators(self, prices: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        计算技术指标

        Args:
            prices: 价格DataFrame

        Returns:
            技术指标字典
        """
        technical_data = {}

        # 1. 移动平均线
        for window in [5, 10, 20, 50, 200]:
            technical_data[f'ma_{window}d'] = prices.rolling(window=window).mean()

        # 2. 指数移动平均线
        for span in [12, 26]:
            technical_data[f'ema_{span}d'] = prices.ewm(span=span).mean()

        # 3. MACD
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        technical_data['macd'] = ema_12 - ema_26
        technical_data['macd_signal'] = technical_data['macd'].ewm(span=9).mean()
        technical_data['macd_histogram'] = technical_data['macd'] - technical_data['macd_signal']

        # 4. 布林带
        ma_20 = prices.rolling(window=20).mean()
        std_20 = prices.rolling(window=20).std()
        technical_data['bollinger_upper'] = ma_20 + 2 * std_20
        technical_data['bollinger_lower'] = ma_20 - 2 * std_20
        technical_data['bollinger_position'] = (prices - technical_data['bollinger_lower']) / (technical_data['bollinger_upper'] - technical_data['bollinger_lower'])

        return technical_data

    def calculate_risk_adjusted_indicators(self, returns: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        计算风险调整指标

        Args:
            returns: 收益率DataFrame

        Returns:
            风险调整指标字典
        """
        risk_data = {}

        # 1. 信息比率 - 相对基准的超额收益
        benchmark_return = returns.mean(axis=1)  # 使用等权重组合作为基准
        excess_returns = returns.sub(benchmark_return, axis=0)
        tracking_error = excess_returns.std() * np.sqrt(self.trading_days)
        information_ratio = excess_returns.mean() * self.trading_days / tracking_error
        risk_data['information_ratio'] = information_ratio

        # 2. Treynor比率 - 市场风险调整收益
        market_return = returns.mean(axis=1)
        betas = {}
        treynor_ratios = {}
        for etf in returns.columns:
            if market_return.var() > 0:
                beta = returns[etf].cov(market_return) / market_return.var()
                treynor = (returns[etf].mean() * self.trading_days) / beta if beta != 0 else 0
                betas[etf] = beta
                treynor_ratios[etf] = treynor

        risk_data['beta'] = pd.Series(betas)
        risk_data['treynor_ratio'] = pd.Series(treynor_ratios)

        # 3. 詹森阿尔法
        jensen_alphas = {}
        for etf in returns.columns:
            if etf in betas and market_return.var() > 0:
                expected_return = 0.02 + betas[etf] * (market_return.mean() * self.trading_days - 0.02)
                actual_return = returns[etf].mean() * self.trading_days
                jensen_alpha = actual_return - expected_return
                jensen_alphas[etf] = jensen_alpha

        risk_data['jensen_alpha'] = pd.Series(jensen_alphas)

        return risk_data

    def calculate_market_regime_indicators(self, returns: pd.DataFrame,
                                         prices: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        计算市场状态指标

        Args:
            returns: 收益率DataFrame
            prices: 价格DataFrame

        Returns:
            市场状态指标字典
        """
        regime_data = {}

        # 1. 趋势强度
        def calculate_trend_strength(prices_series, window=60):
            if len(prices_series) < window:
                return 0
            x = np.arange(len(prices_series[-window:]))
            y = prices_series[-window:].values
            slope, _, r_value, _, _ = stats.linregress(x, y)
            return abs(slope) * r_value

        trend_strength = prices.apply(calculate_trend_strength)
        regime_data['trend_strength'] = trend_strength

        # 2. 波动率状态
        rolling_vol = returns.rolling(window=20).std() * np.sqrt(self.trading_days)
        vol_regime = pd.cut(rolling_vol.iloc[-1],
                          bins=[0, 0.1, 0.2, 0.3, float('inf')],
                          labels=['Low', 'Normal', 'High', 'Extreme'])
        regime_data['volatility_regime'] = vol_regime

        # 3. 相关性状态
        correlation_matrix = returns.rolling(window=60).corr()
        avg_correlation = correlation_matrix.mean().mean()
        regime_data['average_correlation'] = pd.Series(avg_correlation, index=returns.columns)

        return regime_data

    def calculate_factor_exposures(self, returns: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        计算因子暴露度

        Args:
            returns: 收益率DataFrame

        Returns:
            因子暴露度字典
        """
        factor_data = {}

        # 1. 主成分分析 - 提取主要风险因子
        try:
            returns_clean = returns.dropna()
            if len(returns_clean) > 10:
                scaler = StandardScaler()
                returns_scaled = scaler.fit_transform(returns_clean)

                pca = PCA(n_components=min(5, len(returns.columns)))
                factor_loadings = pca.fit_transform(returns_scaled.T)

                factor_exposures = pd.DataFrame(
                    factor_loadings,
                    index=returns.columns,
                    columns=[f'PC_{i+1}' for i in range(factor_loadings.shape[1])]
                )
                factor_data['factor_exposures'] = factor_exposures
        except Exception as e:
            logger.warning(f"因子分析失败: {e}")

        # 2. 风格因子暴露度
        # 市场因子
        market_factor = returns.mean(axis=1)
        market_exposures = returns.apply(lambda x: x.cov(market_factor) / market_factor.var()
                                       if market_factor.var() > 0 else 0)

        # 规模因子 (基于收益率波动)
        size_factor = returns.std()
        size_exposures = (returns.std() - size_factor.mean()) / size_factor.std()

        # 价值因子 (基于收益率均值)
        value_factor = returns.mean()
        value_exposures = (returns.mean() - value_factor.mean()) / value_factor.std()

        factor_data['style_exposures'] = pd.DataFrame({
            'market': market_exposures,
            'size': size_exposures,
            'value': value_exposures
        })

        return factor_data

    def calculate_alpha_prediction_indicators(self, returns: pd.DataFrame,
                                            prices: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        计算阿尔法预测指标

        Args:
            returns: 收益率DataFrame
            prices: 价格DataFrame

        Returns:
            阿尔法预测指标字典
        """
        alpha_data = {}

        # 1. 滚动阿尔法预测
        def rolling_alpha_prediction(returns_series, window=60):
            if len(returns_series) < window:
                return 0
            recent_returns = returns_series[-window:]
            # 使用简单动量作为阿尔法预测
            alpha_prediction = recent_returns.mean() * np.sqrt(self.trading_days)
            return alpha_prediction

        alpha_predictions = returns.apply(rolling_alpha_prediction)
        alpha_data['alpha_prediction'] = alpha_predictions

        # 2. 相对强度指标
        def relative_strength_index(returns_series, window=20):
            if len(returns_series) < window:
                return 50
            gains = returns_series[-window:][returns_series[-window:] > 0].mean()
            losses = -returns_series[-window:][returns_series[-window:] < 0].mean()
            if losses == 0:
                return 100
            rs = gains / losses
            rsi = 100 - (100 / (1 + rs))
            return rsi

        rsi_values = returns.apply(relative_strength_index)
        alpha_data['rsi_alpha_signal'] = (rsi_values - 50) / 50  # 标准化到[-1, 1]

        # 3. 动量反转信号
        short_momentum = returns.rolling(window=5).mean()
        long_momentum = returns.rolling(window=20).mean()
        momentum_reversal_signal = short_momentum.iloc[-1] / long_momentum.iloc[-1] - 1
        alpha_data['momentum_reversal'] = momentum_reversal_signal

        return alpha_data

    def generate_enhanced_signals(self, returns: pd.DataFrame,
                                prices: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        生成增强的综合信号

        Args:
            returns: 收益率DataFrame
            prices: 价格DataFrame

        Returns:
            增强信号字典
        """
        logger.info("开始生成增强量化信号...")

        signals = {}

        try:
            # 1. 动量信号
            momentum_signals = self.calculate_momentum_indicators(returns)
            if momentum_signals:
                signals['momentum_signal'] = momentum_signals['momentum_20d'].iloc[-1]

            # 2. 质量信号
            quality_signals = self.calculate_quality_indicators(returns, prices)
            signals['quality_signal'] = pd.Series(quality_signals)

            # 3. 技术信号
            technical_signals = self.calculate_technical_indicators(prices)
            if 'bollinger_position' in technical_signals:
                signals['technical_signal'] = technical_signals['bollinger_position'].iloc[-1]

            # 4. 风险调整信号
            risk_signals = self.calculate_risk_adjusted_indicators(returns)
            if 'information_ratio' in risk_signals:
                signals['risk_adjusted_signal'] = risk_signals['information_ratio']

            # 5. 阿尔法预测信号
            alpha_signals = self.calculate_alpha_prediction_indicators(returns, prices)
            if 'alpha_prediction' in alpha_signals:
                signals['alpha_signal'] = alpha_signals['alpha_prediction']

            # 6. 综合信号
            signal_df = pd.DataFrame(signals)

            # 标准化信号
            signal_normalized = (signal_df - signal_df.mean()) / signal_df.std()

            # 加权综合信号 (可以根据历史表现调整权重)
            signal_weights = {
                'momentum_signal': 0.25,
                'quality_signal': 0.20,
                'technical_signal': 0.15,
                'risk_adjusted_signal': 0.20,
                'alpha_signal': 0.20
            }

            composite_signal = sum(signal_normalized[signal] * weight
                                 for signal, weight in signal_weights.items()
                                 if signal in signal_normalized.columns)

            signals['composite_signal'] = composite_signal
            signals['signal_normalized'] = signal_normalized

            logger.info("增强量化信号生成完成")

        except Exception as e:
            logger.error(f"生成增强信号失败: {e}")
            signals = {}

        return signals

    def calculate_signal_performance(self, signals: Dict[str, pd.Series],
                                  returns: pd.DataFrame,
                                  forward_days: int = 20) -> Dict[str, float]:
        """
        计算信号的历史表现

        Args:
            signals: 信号字典
            returns: 历史收益率
            forward_days: 前向天数

        Returns:
            信号表现指标
        """
        performance = {}

        for signal_name, signal_values in signals.items():
            if isinstance(signal_values, pd.Series) and len(signal_values) == len(returns):
                try:
                    # 计算信号分组的前向收益
                    signal_quantiles = pd.qcut(signal_values, q=5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])

                    # 计算各分位数的前向收益
                    quantile_returns = {}
                    for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
                        mask = signal_quantiles == q
                        if mask.any():
                            # 计算每个ETF在该分位数组的平均前向收益
                            if isinstance(returns, pd.DataFrame):
                                forward_return = returns[mask].mean().mean() * forward_days
                            else:
                                forward_return = returns[mask].mean() * forward_days
                            quantile_returns[q] = forward_return

                    # 计算多空收益
                    if 'Q5' in quantile_returns and 'Q1' in quantile_returns:
                        long_short_return = quantile_returns['Q5'] - quantile_returns['Q1']
                        performance[f'{signal_name}_long_short'] = long_short_return

                    # 计算信息系数
                    if len(signal_values.dropna()) > 10:
                        ic = signal_values.corr(returns)
                        performance[f'{signal_name}_ic'] = ic if not np.isnan(ic) else 0

                except Exception as e:
                    logger.warning(f"计算 {signal_name} 表现失败: {e}")

        return performance


def get_advanced_quant_indicators(trading_days: int = 252) -> AdvancedQuantIndicators:
    """获取高级量化指标计算器实例"""
    return AdvancedQuantIndicators(trading_days)