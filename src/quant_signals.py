"""
统一量化信号模块
支持简单和高级两种模式，实现多维度量化指标计算
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
import logging
from scipy import stats

logger = logging.getLogger(__name__)


class QuantSignals:
    """统一量化信号生成器"""

    def __init__(self, trading_days: int = 252, mode: str = 'simple'):
        """
        初始化量化信号生成器

        Args:
            trading_days: 年交易天数
            mode: 模式 ('simple', 'advanced', 'auto')
        """
        self.trading_days = trading_days
        self.mode = mode

    def generate_signals(self, returns: pd.DataFrame,
                        prices: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        生成所有量化信号

        Args:
            returns: 收益率DataFrame
            prices: 价格DataFrame（可选）

        Returns:
            信号字典
        """
        try:
            if self.mode == 'simple':
                return self._generate_simple_signals(returns, prices)
            else:
                return self._generate_advanced_signals(returns, prices)
        except Exception as e:
            logger.error(f"生成量化信号失败: {e}")
            return {}

    def _generate_simple_signals(self, returns: pd.DataFrame,
                                prices: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """生成简化量化信号"""
        signals = {}

        # 动量信号
        momentum_signals = self._calculate_momentum_signals(returns)
        signals.update(momentum_signals)

        # 波动率信号
        volatility_signals = self._calculate_volatility_signals(returns)
        signals.update(volatility_signals)

        # 趋势信号
        if prices is not None:
            trend_signals = self._calculate_trend_signals(returns, prices)
            signals.update(trend_signals)

        # 质量信号
        quality_signals = self._calculate_quality_signals(returns)
        signals.update(quality_signals)

        # 合成综合信号
        composite_signal = self._create_composite_signal(signals)
        signals['composite_signal'] = composite_signal

        # 信号分析
        signals['signal_analysis'] = self._analyze_signals(signals)

        return signals

    def _generate_advanced_signals(self, returns: pd.DataFrame,
                                  prices: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """生成高级量化信号"""
        signals = {}

        # 高级动量信号
        momentum_signals = self._calculate_advanced_momentum_signals(returns)
        signals.update(momentum_signals)

        # 高级波动率信号
        volatility_signals = self._calculate_advanced_volatility_signals(returns)
        signals.update(volatility_signals)

        # 高级趋势信号
        if prices is not None:
            trend_signals = self._calculate_advanced_trend_signals(returns, prices)
            signals.update(trend_signals)

        # 高级质量信号
        quality_signals = self._calculate_advanced_quality_signals(returns)
        signals.update(quality_signals)

        # 技术指标信号
        if prices is not None:
            technical_signals = self._calculate_technical_signals(prices)
            signals.update(technical_signals)

        # 合成综合信号
        composite_signal = self._create_composite_signal(signals)
        signals['composite_signal'] = composite_signal

        # 标准化信号
        signals['signal_normalized'] = self._normalize_signals(signals)

        # 信号分析
        signals['signal_analysis'] = self._analyze_signals(signals)

        # 信号历史表现
        signals['signal_performance'] = self._calculate_signal_performance(signals, returns)

        return signals

    def _calculate_momentum_signals(self, returns: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算动量信号（简化版）"""
        signals = {}

        try:
            # 短期动量 (20天)
            short_momentum = returns.rolling(window=20).mean()
            signals['short_momentum'] = short_momentum.iloc[-1]

            # 中期动量 (60天)
            medium_momentum = returns.rolling(window=60).mean()
            signals['medium_momentum'] = medium_momentum.iloc[-1]

            # 长期动量 (120天)
            long_momentum = returns.rolling(window=min(120, len(returns)-1)).mean()
            signals['long_momentum'] = long_momentum.iloc[-1]

            # 动量趋势 (短期vs长期)
            momentum_trend = short_momentum.iloc[-1] / long_momentum.iloc[-1] - 1
            signals['momentum_trend'] = momentum_trend

        except Exception as e:
            logger.error(f"计算动量信号失败: {e}")

        return signals

    def _calculate_advanced_momentum_signals(self, returns: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算高级动量信号"""
        signals = {}

        try:
            # 基础动量信号
            basic_momentum = self._calculate_momentum_signals(returns)
            signals.update(basic_momentum)

            # 动量强度
            for window in [5, 20, 60]:
                momentum = returns.rolling(window=window).mean()
                momentum_strength = momentum / returns.rolling(window=window).std()
                signals[f'momentum_strength_{window}d'] = momentum_strength.iloc[-1]

            # 相对动量
            benchmark_momentum = returns.mean(axis=1).rolling(window=60).mean()
            for etf in returns.columns:
                etf_momentum = returns[etf].rolling(window=60).mean()
                relative_momentum = etf_momentum.iloc[-1] / benchmark_momentum.iloc[-1]
                signals[f'relative_momentum_{etf}'] = pd.Series([relative_momentum], index=[etf])

        except Exception as e:
            logger.error(f"计算高级动量信号失败: {e}")

        return signals

    def _calculate_volatility_signals(self, returns: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算波动率信号（简化版）"""
        signals = {}

        try:
            # 历史波动率
            volatility = returns.rolling(window=60).std() * np.sqrt(self.trading_days)
            signals['volatility'] = volatility.iloc[-1]

            # 下行波动率
            downside_returns = returns.copy()
            downside_returns[downside_returns > 0] = 0
            downside_vol = downside_returns.rolling(window=60).std() * np.sqrt(self.trading_days)
            signals['downside_volatility'] = downside_vol.iloc[-1]

            # 波动率比率
            vol_ratio = downside_vol.iloc[-1] / volatility.iloc[-1]
            signals['volatility_ratio'] = vol_ratio

            # 夏普比率信号
            mean_return = returns.rolling(window=60).mean() * self.trading_days
            sharpe_signal = mean_return.iloc[-1] / volatility.iloc[-1]
            signals['sharpe_signal'] = sharpe_signal

        except Exception as e:
            logger.error(f"计算波动率信号失败: {e}")

        return signals

    def _calculate_advanced_volatility_signals(self, returns: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算高级波动率信号"""
        signals = {}

        try:
            # 基础波动率信号
            basic_volatility = self._calculate_volatility_signals(returns)
            signals.update(basic_volatility)

            # 波动率趋势
            vol_20d = returns.rolling(window=20).std() * np.sqrt(self.trading_days)
            vol_60d = returns.rolling(window=60).std() * np.sqrt(self.trading_days)
            vol_trend = vol_20d.iloc[-1] / vol_60d.iloc[-1] - 1
            signals['volatility_trend'] = vol_trend

            # 波动率偏度
            returns_skew = returns.rolling(window=60).skew()
            signals['returns_skew'] = returns_skew.iloc[-1]

            # 波动率峰度
            returns_kurt = returns.rolling(window=60).kurt()
            signals['returns_kurtosis'] = returns_kurt.iloc[-1]

        except Exception as e:
            logger.error(f"计算高级波动率信号失败: {e}")

        return signals

    def _calculate_trend_signals(self, returns: pd.DataFrame,
                               prices: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算趋势信号（简化版）"""
        signals = {}

        try:
            # 价格相对位置
            min_price = prices.rolling(window=252).min()
            max_price = prices.rolling(window=252).max()
            price_position = (prices.iloc[-1] - min_price.iloc[-1]) / (max_price.iloc[-1] - min_price.iloc[-1])
            signals['price_position'] = price_position

            # 移动平均信号
            ma_20 = prices.rolling(window=20).mean()
            ma_60 = prices.rolling(window=60).mean()
            ma_signal = (prices.iloc[-1] - ma_20.iloc[-1]) / ma_20.iloc[-1]
            signals['ma_signal'] = ma_signal

            # 趋势强度
            trend_strength = (ma_20.iloc[-1] - ma_60.iloc[-1]) / ma_60.iloc[-1]
            signals['trend_strength'] = trend_strength

        except Exception as e:
            logger.error(f"计算趋势信号失败: {e}")

        return signals

    def _calculate_advanced_trend_signals(self, returns: pd.DataFrame,
                                        prices: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算高级趋势信号"""
        signals = {}

        try:
            # 基础趋势信号
            basic_trend = self._calculate_trend_signals(returns, prices)
            signals.update(basic_trend)

            # 多时间框架移动平均
            for window in [10, 30, 60, 120]:
                ma = prices.rolling(window=window).mean()
                ma_signal = (prices.iloc[-1] - ma.iloc[-1]) / ma.iloc[-1]
                signals[f'ma_signal_{window}d'] = ma_signal

            # 趋势一致性
            ma_signals = []
            for window in [10, 30, 60]:
                ma = prices.rolling(window=window).mean()
                signal = (prices.iloc[-1] > ma.iloc[-1]).astype(int)
                ma_signals.append(signal)

            trend_consistency = np.mean(ma_signals, axis=0)
            signals['trend_consistency'] = pd.Series(trend_consistency, index=prices.columns)

        except Exception as e:
            logger.error(f"计算高级趋势信号失败: {e}")

        return signals

    def _calculate_quality_signals(self, returns: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算质量信号（简化版）"""
        signals = {}

        try:
            # 收益稳定性
            return_stability = 1 / (returns.rolling(window=60).std() + 1e-8)
            signals['return_stability'] = return_stability.iloc[-1]

            # 正收益比率
            positive_ratio = (returns > 0).rolling(window=60).mean()
            signals['positive_return_ratio'] = positive_ratio.iloc[-1]

            # 最大回撤
            cumulative_returns = (1 + returns).cumprod()
            rolling_max = cumulative_returns.rolling(window=252).max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdown.rolling(window=252).min()
            signals['max_drawdown'] = -max_drawdown.iloc[-1]  # 转为正值

        except Exception as e:
            logger.error(f"计算质量信号失败: {e}")

        return signals

    def _calculate_advanced_quality_signals(self, returns: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算高级质量信号"""
        signals = {}

        try:
            # 基础质量信号
            basic_quality = self._calculate_quality_signals(returns)
            signals.update(basic_quality)

            # Calmar比率
            annual_return = returns.mean() * self.trading_days
            max_drawdown = -signals['max_drawdown']
            calmar_ratio = annual_return / (max_drawdown + 1e-8)
            signals['calmar_ratio'] = calmar_ratio

            # 索提诺比率
            downside_returns = returns.copy()
            downside_returns[downside_returns > 0] = 0
            downside_deviation = downside_returns.std() * np.sqrt(self.trading_days)
            sortino_ratio = annual_return / (downside_deviation + 1e-8)
            signals['sortino_ratio'] = sortino_ratio

            # 胜率
            win_rate = (returns > 0).mean()
            signals['win_rate'] = win_rate

            # 盈亏比
            winning_returns = returns[returns > 0].mean()
            losing_returns = returns[returns < 0].mean()
            profit_loss_ratio = winning_returns / abs(losing_returns + 1e-8)
            signals['profit_loss_ratio'] = profit_loss_ratio

        except Exception as e:
            logger.error(f"计算高级质量信号失败: {e}")

        return signals

    def _calculate_technical_signals(self, prices: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算技术指标信号"""
        signals = {}

        try:
            # RSI指标
            for etf in prices.columns:
                rsi = self._calculate_rsi(prices[etf])
                signals[f'rsi_{etf}'] = pd.Series([rsi], index=[etf])

            # 布林带位置
            for etf in prices.columns:
                bb_position = self._calculate_bollinger_position(prices[etf])
                signals[f'bb_position_{etf}'] = pd.Series([bb_position], index=[etf])

        except Exception as e:
            logger.error(f"计算技术指标信号失败: {e}")

        return signals

    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> float:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / (loss + 1e-8)
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def _calculate_bollinger_position(self, prices: pd.Series, window: int = 20, std_dev: int = 2) -> float:
        """计算布林带位置"""
        ma = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper_band = ma + std * std_dev
        lower_band = ma - std * std_dev

        current_price = prices.iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]

        if current_upper - current_lower > 0:
            position = (current_price - current_lower) / (current_upper - current_lower)
        else:
            position = 0.5

        return position

    def _create_composite_signal(self, signals: Dict[str, Any]) -> pd.Series:
        """创建综合信号"""
        try:
            # 收集所有数值信号
            signal_values = {}

            for key, value in signals.items():
                if isinstance(value, pd.Series):
                    signal_values[key] = value
                elif isinstance(value, (int, float)):
                    # 将标量值转换为Series
                    if hasattr(list(signals.values())[0], 'index'):
                        index = list(signals.values())[0].index
                        signal_values[key] = pd.Series([value] * len(index), index=index)

            if not signal_values:
                return pd.Series()

            # 标准化所有信号
            normalized_signals = {}
            for key, series in signal_values.items():
                if len(series) > 1:
                    # Z-score标准化
                    normalized = (series - series.mean()) / (series.std() + 1e-8)
                    normalized_signals[key] = normalized

            # 计算综合信号（简单平均）
            if normalized_signals:
                composite = pd.DataFrame(normalized_signals).mean(axis=1)
            else:
                composite = pd.Series()

            return composite

        except Exception as e:
            logger.error(f"创建综合信号失败: {e}")
            return pd.Series()

    def _normalize_signals(self, signals: Dict[str, Any]) -> pd.DataFrame:
        """标准化所有信号"""
        try:
            normalized_data = {}

            for key, value in signals.items():
                if isinstance(value, pd.Series) and len(value) > 1:
                    # Min-Max标准化到[-1, 1]
                    min_val = value.min()
                    max_val = value.max()
                    if max_val - min_val > 0:
                        normalized = 2 * (value - min_val) / (max_val - min_val) - 1
                    else:
                        normalized = pd.Series(0, index=value.index)
                    normalized_data[key] = normalized

            return pd.DataFrame(normalized_data)

        except Exception as e:
            logger.error(f"标准化信号失败: {e}")
            return pd.DataFrame()

    def _analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """分析信号特征"""
        analysis = {}

        try:
            # 信号数量
            signal_count = len([s for s in signals.values() if isinstance(s, pd.Series)])
            analysis['signal_count'] = signal_count

            # 信号名称
            signal_names = [key for key, value in signals.items()
                          if isinstance(value, pd.Series) and not key.startswith('composite')]
            analysis['signal_names'] = signal_names

            # 最佳表现ETF（基于综合信号）
            if 'composite_signal' in signals:
                composite = signals['composite_signal']
                if not composite.empty:
                    top_performers = composite.nlargest(3).index.tolist()
                    analysis['top_performers'] = {etf: composite[etf] for etf in top_performers}

        except Exception as e:
            logger.error(f"分析信号失败: {e}")

        return analysis

    def _calculate_signal_performance(self, signals: Dict[str, Any],
                                    returns: pd.DataFrame) -> Dict[str, float]:
        """计算信号历史表现"""
        performance = {}

        try:
            if 'composite_signal' in signals and not signals['composite_signal'].empty:
                composite_signal = signals['composite_signal']

                # 计算信号与未来收益的相关性
                future_returns = returns.shift(-1)  # 下一期收益
                correlations = {}

                for etf in composite_signal.index:
                    if etf in future_returns.columns:
                        corr = composite_signal[etf].corr(future_returns[etf])
                        if not np.isnan(corr):
                            correlations[etf] = corr

                if correlations:
                    performance['signal_correlation'] = np.mean(list(correlations.values()))
                    performance['signal_precision'] = len([c for c in correlations.values() if c > 0]) / len(correlations)

        except Exception as e:
            logger.error(f"计算信号表现失败: {e}")

        return performance

    def get_signal_recommendations(self, signals: Dict[str, Any]) -> List[str]:
        """获取基于信号的投资建议"""
        recommendations = []

        try:
            if 'composite_signal' in signals and not signals['composite_signal'].empty:
                composite = signals['composite_signal']

                # 强烈推荐
                strong_buy = composite[composite > 0.5].index.tolist()
                if strong_buy:
                    recommendations.append(f"强烈推荐关注: {', '.join(strong_buy)}")

                # 避免信号
                avoid = composite[composite < -0.5].index.tolist()
                if avoid:
                    recommendations.append(f"建议规避: {', '.join(avoid)}")

                # 中性信号
                neutral = composite[(composite >= -0.3) & (composite <= 0.3)].index.tolist()
                if neutral:
                    recommendations.append(f"中性观望: {', '.join(neutral)}")

        except Exception as e:
            logger.error(f"生成信号建议失败: {e}")

        return recommendations


def get_quant_signals(trading_days: int = 252, mode: str = 'simple') -> QuantSignals:
    """获取量化信号生成器实例"""
    return QuantSignals(trading_days, mode)


# 向后兼容的工厂函数
def get_simple_quant_signals(trading_days: int = 252) -> QuantSignals:
    """获取简化量化信号生成器（向后兼容）"""
    return QuantSignals(trading_days, mode='simple')


def get_advanced_quant_indicators(trading_days: int = 252) -> QuantSignals:
    """获取高级量化指标生成器（向后兼容）"""
    return QuantSignals(trading_days, mode='advanced')