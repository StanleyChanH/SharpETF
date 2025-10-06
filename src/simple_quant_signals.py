"""
简化量化信号生成器
专门用于生成清晰有效的投资信号
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class SimpleQuantSignals:
    """简化量化信号生成器"""

    def __init__(self, trading_days: int = 252):
        """
        初始化简化量化信号生成器

        Args:
            trading_days: 年交易天数
        """
        self.trading_days = trading_days

    def calculate_simple_momentum_signals(self, returns: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        计算简单的动量信号

        Args:
            returns: 收益率DataFrame

        Returns:
            动量信号字典
        """
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
            signals = {}

        return signals

    def calculate_simple_volatility_signals(self, returns: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        计算波动率相关信号

        Args:
            returns: 收益率DataFrame

        Returns:
            波动率信号字典
        """
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

            # 波动率比率 (下行波动率/总波动率)
            vol_ratio = downside_vol.iloc[-1] / volatility.iloc[-1]
            signals['volatility_ratio'] = vol_ratio

            # 夏普比率信号
            mean_return = returns.rolling(window=60).mean() * self.trading_days
            sharpe_signal = mean_return.iloc[-1] / volatility.iloc[-1]
            signals['sharpe_signal'] = sharpe_signal

        except Exception as e:
            logger.error(f"计算波动率信号失败: {e}")
            signals = {}

        return signals

    def calculate_simple_trend_signals(self, returns: pd.DataFrame, prices: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        计算趋势信号

        Args:
            returns: 收益率DataFrame
            prices: 价格DataFrame

        Returns:
            趋势信号字典
        """
        signals = {}

        try:
            # 价格相对位置 (相对于最高点的位置)
            # 根据实际数据长度调整窗口期
            window = min(120, len(prices) // 2) if len(prices) >= 20 else len(prices)
            if window >= 10:
                price_high = prices.rolling(window=window).max()
                price_position = prices.iloc[-1] / price_high.iloc[-1]
                # 处理可能的NaN值
                price_position = price_position.fillna(0.5)  # 默认中间位置
                signals['price_position'] = price_position
            else:
                # 数据不足，使用默认值
                signals['price_position'] = pd.Series([0.5] * len(prices.columns), index=prices.columns)

            # 移动平均信号
            ma_short = prices.rolling(window=20).mean()
            ma_long = prices.rolling(window=60).mean()
            ma_signal = (ma_short.iloc[-1] / ma_long.iloc[-1] - 1)
            signals['ma_signal'] = ma_signal

            # 趋势强度 (基于收益率的线性回归)
            trend_strength = {}
            for etf in returns.columns:
                if len(returns) >= 20:
                    recent_returns = returns[etf].tail(20)
                    if len(recent_returns.dropna()) >= 10:
                        # 简单的趋势计算：正值的比例
                        positive_ratio = (recent_returns > 0).mean()
                        trend_strength[etf] = positive_ratio
                    else:
                        trend_strength[etf] = 0.5
                else:
                    trend_strength[etf] = 0.5

            signals['trend_strength'] = pd.Series(trend_strength)

        except Exception as e:
            logger.error(f"计算趋势信号失败: {e}")
            signals = {}

        return signals

    def calculate_simple_quality_signals(self, returns: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        计算质量信号

        Args:
            returns: 收益率DataFrame

        Returns:
            质量信号字典
        """
        signals = {}

        try:
            # 收益稳定性 (收益的标准差，越小越稳定)
            return_stability = returns.rolling(window=60).std()
            # 转换为稳定性评分 (标准差的倒数)
            stability_score = 1 / (return_stability.iloc[-1] + 1e-8)
            signals['stability_score'] = stability_score

            # 正收益比率
            positive_ratio = (returns > 0).rolling(window=60).mean()
            signals['positive_ratio'] = positive_ratio.iloc[-1]

            # 最大回撤信号
            cumulative_returns = (1 + returns).cumprod()
            window = min(120, len(returns) // 2) if len(returns) >= 20 else len(returns)
            if window >= 10:
                rolling_max = cumulative_returns.rolling(window=window).max()
                drawdown = (cumulative_returns - rolling_max) / rolling_max
                max_drawdown = drawdown.rolling(window=min(window, 60)).min()
                # 回撤越小越好，所以用负数作为信号
                drawdown_signal = -max_drawdown.iloc[-1]
                # 处理可能的NaN值
                drawdown_signal = drawdown_signal.fillna(0)  # 默认无回撤
                signals['drawdown_signal'] = drawdown_signal
            else:
                # 数据不足，使用默认值
                signals['drawdown_signal'] = pd.Series([0] * len(returns.columns), index=returns.columns)

        except Exception as e:
            logger.error(f"计算质量信号失败: {e}")
            signals = {}

        return signals

    def generate_composite_signals(self, returns: pd.DataFrame, prices: pd.DataFrame) -> Dict[str, Any]:
        """
        生成综合信号

        Args:
            returns: 收益率DataFrame
            prices: 价格DataFrame

        Returns:
            综合信号字典
        """
        logger.info("🔬 开始生成简化量化信号...")

        try:
            # 计算各类信号
            momentum_signals = self.calculate_simple_momentum_signals(returns)
            volatility_signals = self.calculate_simple_volatility_signals(returns)
            trend_signals = self.calculate_simple_trend_signals(returns, prices)
            quality_signals = self.calculate_simple_quality_signals(returns)

            # 合并所有信号
            all_signals = {}
            all_signals.update(momentum_signals)
            all_signals.update(volatility_signals)
            all_signals.update(trend_signals)
            all_signals.update(quality_signals)

            # 计算综合信号
            if all_signals:
                # 标准化所有信号
                signal_df = pd.DataFrame(all_signals)
                signal_normalized = signal_df.apply(lambda x: (x - x.mean()) / x.std() if x.std() > 0 else x)

                # 计算综合信号 (等权重平均)
                composite_signal = signal_normalized.mean(axis=1)
                signal_ranking = composite_signal.sort_values(ascending=False)

                # 信号分析
                signal_analysis = {
                    'top_performers': signal_ranking.head(3).to_dict(),
                    'bottom_performers': signal_ranking.tail(3).to_dict(),
                    'signal_count': len(all_signals),
                    'signal_names': list(all_signals.keys())
                }

                # 返回结果
                result = {
                    'composite_signal': composite_signal,
                    'signal_normalized': signal_normalized,
                    'individual_signals': all_signals,
                    'signal_analysis': signal_analysis
                }

                logger.info("✅ 简化量化信号生成完成")
                return result
            else:
                logger.warning("⚠️ 未能生成任何信号")
                return {}

        except Exception as e:
            logger.error(f"❌ 生成综合信号失败: {e}")
            return {}

    def get_signal_recommendations(self, signals: Dict[str, Any]) -> List[str]:
        """
        基于信号生成投资建议

        Args:
            signals: 信号字典

        Returns:
            投资建议列表
        """
        recommendations = []

        try:
            if not signals or 'signal_analysis' not in signals:
                return ["量化信号分析暂不可用，建议基于基础分析进行投资决策"]

            analysis = signals['signal_analysis']
            top_performers = analysis['top_performers']

            # 生成建议
            if top_performers:
                best_etf = list(top_performers.keys())[0]
                best_score = list(top_performers.values())[0]

                if best_score > 0.5:
                    recommendations.append(f"📈 {best_etf} 在量化信号中表现最佳，建议重点关注")
                elif best_score > 0:
                    recommendations.append(f"➡️ {best_etf} 表现相对较好，可考虑适当配置")
                else:
                    recommendations.append("📉 当前信号显示市场情绪较为谨慎，建议控制风险")

                # 基于信号数量的建议
                signal_count = analysis['signal_count']
                if signal_count >= 8:
                    recommendations.append("🔬 综合多个维度信号分析，建议结果较为可靠")
                elif signal_count >= 4:
                    recommendations.append("📊 基于中等维度信号分析，建议结合其他指标")
                else:
                    recommendations.append("⚠️ 信号维度较少，建议谨慎参考")

            recommendations.append("💡 建议定期监控量化信号变化，及时调整投资策略")

        except Exception as e:
            logger.error(f"生成信号建议失败: {e}")
            recommendations = ["量化建议生成失败，请基于基础分析进行决策"]

        return recommendations


def get_simple_quant_signals(trading_days: int = 252) -> SimpleQuantSignals:
    """获取简化量化信号生成器实例"""
    return SimpleQuantSignals(trading_days)