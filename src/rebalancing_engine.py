"""
动态再平衡引擎
提供多种再平衡策略和执行机制
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RebalancingEngine:
    """动态再平衡引擎"""

    def __init__(self, transaction_cost: float = 0.001, min_trade_amount: float = 1000):
        """
        初始化再平衡引擎

        Args:
            transaction_cost: 交易成本率，默认0.1%
            min_trade_amount: 最小交易金额，默认1000元
        """
        self.transaction_cost = transaction_cost
        self.min_trade_amount = min_trade_amount

    def time_based_rebalancing(self, current_weights: np.ndarray,
                             target_weights: np.ndarray,
                             rebalancing_frequency: str = 'monthly') -> bool:
        """
        基于时间的再平衡信号

        Args:
            current_weights: 当前权重
            target_weights: 目标权重
            rebalancing_frequency: 再平衡频率 ('daily', 'weekly', 'monthly', 'quarterly')

        Returns:
            是否需要再平衡
        """
        # 简化版本：在实际应用中需要结合实际日期判断
        # 这里假设每次调用都符合时间条件
        return True

    def threshold_based_rebalancing(self, current_weights: np.ndarray,
                                  target_weights: np.ndarray,
                                  threshold: float = 0.05) -> Tuple[bool, np.ndarray]:
        """
        基于阈值的再平衡信号

        Args:
            current_weights: 当前权重
            target_weights: 目标权重
            threshold: 权重偏离阈值，默认5%

        Returns:
            (是否需要再平衡, 权重偏离度)
        """
        weight_deviation = np.abs(current_weights - target_weights)
        max_deviation = np.max(weight_deviation)

        needs_rebalancing = max_deviation > threshold
        return needs_rebalancing, weight_deviation

    def volatility_based_rebalancing(self, returns: pd.Series,
                                   current_volatility: float,
                                   target_volatility: float,
                                   volatility_band: float = 0.2) -> bool:
        """
        基于波动率的再平衡信号

        Args:
            returns: 历史收益率
            current_volatility: 当前组合波动率
            target_volatility: 目标波动率
            volatility_band: 波动率容忍带，默认20%

        Returns:
            是否需要再平衡
        """
        upper_bound = target_volatility * (1 + volatility_band)
        lower_bound = target_volatility * (1 - volatility_band)

        return current_volatility > upper_bound or current_volatility < lower_bound

    def calculate_rebalancing_trades(self, current_weights: np.ndarray,
                                   target_weights: np.ndarray,
                                   portfolio_value: float) -> Dict[str, Dict[str, float]]:
        """
        计算再平衡交易指令

        Args:
            current_weights: 当前权重
            target_weights: 目标权重
            portfolio_value: 投资组合总价值

        Returns:
            交易指令字典
        """
        weight_changes = target_weights - current_weights

        trades = {}
        total_trading_cost = 0

        for i, weight_change in enumerate(weight_changes):
            trade_value = weight_change * portfolio_value

            # 计算交易成本
            trading_cost = abs(trade_value) * self.transaction_cost

            # 跳过交易金额过小的交易
            if abs(trade_value) < self.min_trade_amount:
                continue

            trades[f'ETF_{i}'] = {
                'weight_change': weight_change,
                'trade_value': trade_value,
                'trading_cost': trading_cost,
                'action': 'BUY' if weight_change > 0 else 'SELL'
            }

            total_trading_cost += trading_cost

        # 计算净交易成本
        trades['summary'] = {
            'total_trading_cost': total_trading_cost,
            'total_trading_cost_pct': total_trading_cost / portfolio_value,
            'total_turnover': np.sum(np.abs(weight_changes)) / 2
        }

        return trades

    def optimize_rebalancing_timing(self, returns: pd.DataFrame,
                                  target_weights: np.ndarray,
                                  lookback_days: int = 20) -> Dict[str, Any]:
        """
        优化再平衡时机（基于历史数据）

        Args:
            returns: 历史收益率数据
            target_weights: 目标权重
            lookback_days: 回看天数

        Returns:
            再平衡时机优化结果
        """
        # 计算滚动相关性变化
        rolling_corr = returns.rolling(window=lookback_days).corr()

        # 计算权重稳定性
        rolling_weights_volatility = returns.rolling(window=lookback_days).std()

        # 寻找相关性稳定且波动率较低的时期
        avg_corr_stability = rolling_corr.groupby(level=0).std().mean(axis=1)
        avg_volatility = rolling_weights_volatility.mean(axis=1)

        # 优化评分：低相关性变化 + 低波动率
        optimization_score = 1 / (avg_corr_stability * avg_volatility)

        best_rebalancing_days = optimization_score.nlargest(5).index.tolist()

        return {
            'best_rebalancing_days': best_rebalancing_days,
            'optimization_scores': optimization_score.to_dict(),
            'avg_correlation_stability': avg_corr_stability.mean(),
            'avg_volatility': avg_volatility.mean()
        }

    def tax_loss_harvesting(self, current_weights: np.ndarray,
                          cost_basis: np.ndarray,
                          current_prices: np.ndarray,
                          tax_rate: float = 0.2) -> Dict[str, Any]:
        """
        税务亏损收获策略

        Args:
            current_weights: 当前权重
            cost_basis: 成本基准
            current_prices: 当前价格
            tax_rate: 税率

        Returns:
            税务优化建议
        """
        # 计算未实现损益
        unrealized_gains_losses = (current_prices - cost_basis) / cost_basis

        tax_harvesting_opportunities = {}
        potential_tax_savings = 0

        for i, (weight, gain_loss) in enumerate(zip(current_weights, unrealized_gains_losses)):
            if gain_loss < -0.05:  # 亏损超过5%
                tax_saving = abs(gain_loss) * weight * tax_rate
                tax_harvesting_opportunities[f'ETF_{i}'] = {
                    'unrealized_loss_pct': gain_loss,
                    'weight': weight,
                    'potential_tax_saving': tax_saving,
                    'recommendation': 'CONSIDER_SELLING'
                }
                potential_tax_savings += tax_saving

        return {
            'opportunities': tax_harvesting_opportunities,
            'total_potential_tax_savings': potential_tax_savings,
            'tax_rate': tax_rate
        }

    def cash_flow_rebalancing(self, current_weights: np.ndarray,
                            target_weights: np.ndarray,
                            cash_flow: float) -> Dict[str, float]:
        """
        现金流再平衡（新增投资或提取现金）

        Args:
            current_weights: 当前权重
            target_weights: 目标权重
            cash_flow: 现金流（正数为流入，负数为流出）

        Returns:
            再平衡后的权重变化
        """
        if cash_flow > 0:
            # 新增投资：按目标权重分配
            new_investments = target_weights * cash_flow
            return {'new_investments': new_investments}
        else:
            # 提取现金：按当前权重 proportionally 提取
            withdrawals = current_weights * abs(cash_flow)
            return {'withdrawals': withdrawals}

    def generate_rebalancing_report(self, current_weights: np.ndarray,
                                  target_weights: np.ndarray,
                                  portfolio_value: float,
                                  returns: pd.Series,
                                  etf_codes: List[str],
                                  all_returns: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        生成再平衡报告

        Args:
            current_weights: 当前权重
            target_weights: 目标权重
            portfolio_value: 投资组合价值
            returns: 收益率序列
            etf_codes: ETF代码列表

        Returns:
            再平衡报告
        """
        report = {}

        # 1. 权重偏离分析
        needs_rebalancing, weight_deviation = self.threshold_based_rebalancing(
            current_weights, target_weights
        )

        report['weight_analysis'] = {
            'needs_rebalancing': needs_rebalancing,
            'max_deviation': np.max(weight_deviation),
            'avg_deviation': np.mean(weight_deviation),
            'deviation_by_etf': dict(zip(etf_codes, weight_deviation))
        }

        # 2. 交易指令计算
        if needs_rebalancing:
            trades = self.calculate_rebalancing_trades(
                current_weights, target_weights, portfolio_value
            )
            report['trades'] = trades

        # 3. 波动率分析
        current_volatility = returns.std() * np.sqrt(252)

        if all_returns is not None:
            target_volatility = np.sqrt(np.dot(target_weights.T,
                                              np.dot(all_returns.cov() * 252, target_weights)))
        else:
            # 如果没有提供多资产数据，使用简化计算
            target_volatility = current_volatility  # 简化处理

        volatility_rebalance = self.volatility_based_rebalancing(
            returns, current_volatility, target_volatility
        )

        report['volatility_analysis'] = {
            'current_volatility': current_volatility,
            'target_volatility': target_volatility,
            'needs_rebalancing': volatility_rebalance,
            'volatility_ratio': current_volatility / target_volatility
        }

        # 4. 预期影响分析
        if needs_rebalancing:
            # 估算再平衡后的组合表现
            if all_returns is not None:
                expected_return = np.dot(target_weights, all_returns.mean() * 252)
                expected_volatility = np.sqrt(np.dot(target_weights.T,
                                                   np.dot(all_returns.cov() * 252, target_weights)))
            else:
                # 简化处理：使用当前组合的收益和波动率
                expected_return = returns.mean() * 252
                expected_volatility = current_volatility

            expected_sharpe = expected_return / expected_volatility

            report['expected_impact'] = {
                'expected_annual_return': expected_return,
                'expected_volatility': expected_volatility,
                'expected_sharpe_ratio': expected_sharpe
            }

        # 5. 再平衡建议
        report['recommendations'] = self._generate_rebalancing_recommendations(
            needs_rebalancing, weight_deviation, current_volatility, target_volatility
        )

        return report

    def _generate_rebalancing_recommendations(self, needs_rebalancing: bool,
                                            weight_deviation: np.ndarray,
                                            current_vol: float,
                                            target_vol: float) -> List[str]:
        """
        生成再平衡建议

        Args:
            needs_rebalancing: 是否需要再平衡
            weight_deviation: 权重偏离度
            current_vol: 当前波动率
            target_vol: 目标波动率

        Returns:
            建议列表
        """
        recommendations = []

        if needs_rebalancing:
            max_dev_etf = np.argmax(weight_deviation)
            recommendations.append(f"建议立即再平衡，最大偏离度为 {weight_deviation[max_dev_etf]:.2%}")

            if np.sum(weight_deviation > 0.1) > 0:
                recommendations.append("多个ETF权重偏离超过10%，建议优先再平衡这些ETF")
        else:
            recommendations.append("当前权重偏离在可接受范围内，暂无需再平衡")

        if current_vol > target_vol * 1.2:
            recommendations.append("组合波动率过高，考虑降低风险敞口")
        elif current_vol < target_vol * 0.8:
            recommendations.append("组合波动率过低，考虑增加风险敞口以提高收益")

        return recommendations


def get_rebalancing_engine(transaction_cost: float = 0.001,
                         min_trade_amount: float = 1000) -> RebalancingEngine:
    """获取再平衡引擎实例"""
    return RebalancingEngine(transaction_cost, min_trade_amount)