"""
实用投资工具模块
提供投资金额计算、调仓信号、业绩归因等实用功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class InvestmentCalculator:
    """投资计算器"""

    def __init__(self, initial_capital: float = 1000000):
        """
        初始化投资计算器

        Args:
            initial_capital: 初始资金，默认100万
        """
        self.initial_capital = initial_capital

    def calculate_position_sizes(self, weights: np.ndarray,
                                portfolio_value: float,
                                etf_prices: np.ndarray) -> Dict[str, Dict[str, float]]:
        """
        计算具体持仓数量

        Args:
            weights: 投资组合权重
            portfolio_value: 投资组合总价值
            etf_prices: ETF价格列表

        Returns:
            持仓信息字典
        """
        positions = {}

        for i, (weight, price) in enumerate(zip(weights, etf_prices)):
            target_value = weight * portfolio_value
            shares = int(target_value / price / 100) * 100  # 按手数（100股）计算

            actual_value = shares * price
            actual_weight = actual_value / portfolio_value

            positions[f'ETF_{i}'] = {
                'target_weight': weight,
                'actual_weight': actual_weight,
                'target_value': target_value,
                'actual_value': actual_value,
                'shares': shares,
                'price': price,
                'weight_diff': actual_weight - weight
            }

        # 计算汇总信息
        total_actual_value = sum(pos['actual_value'] for pos in positions.values())
        cash_balance = portfolio_value - total_actual_value

        positions['summary'] = {
            'total_target_value': portfolio_value,
            'total_actual_value': total_actual_value,
            'cash_balance': cash_balance,
            'cash_percentage': cash_balance / portfolio_value,
            'total_shares': sum(pos['shares'] for pos in positions.values())
        }

        return positions

    def project_portfolio_growth(self, annual_return: float,
                               annual_volatility: float,
                               years: int = 10,
                               simulations: int = 1000) -> Dict[str, Any]:
        """
        投资组合增长预测

        Args:
            annual_return: 年化收益率
            annual_volatility: 年化波动率
            years: 预测年数
            simulations: 蒙特卡洛模拟次数

        Returns:
            增长预测结果
        """
        # 生成随机路径
        dt = 1/252  # 日频
        total_steps = years * 252

        all_paths = []
        final_values = []

        for _ in range(simulations):
            # 生成随机收益率
            daily_returns = np.random.normal(
                annual_return/252,
                annual_volatility/np.sqrt(252),
                total_steps
            )

            # 计算累计收益路径
            cumulative_returns = np.cumprod(1 + daily_returns)
            portfolio_values = self.initial_capital * cumulative_returns

            all_paths.append(portfolio_values)
            final_values.append(portfolio_values[-1])

        all_paths = np.array(all_paths)

        # 计算统计指标
        percentiles = [10, 25, 50, 75, 90]
        final_percentiles = np.percentile(final_values, percentiles)

        # 计算成功概率（达到目标）
        target_multipliers = [1.5, 2.0, 3.0, 5.0]
        success_probabilities = {}

        for multiplier in target_multipliers:
            target_value = self.initial_capital * multiplier
            success_count = sum(1 for value in final_values if value >= target_value)
            success_probabilities[f'{multiplier}x'] = success_count / simulations

        # 计算翻倍成功率（>100%收益）
        breakeven_success = sum(1 for value in final_values if value >= self.initial_capital * 2.0)

        return {
            'initial_capital': self.initial_capital,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'years': years,
            'simulations': simulations,
            'final_value_statistics': {
                'mean': np.mean(final_values),
                'median': np.median(final_values),
                'std': np.std(final_values),
                'min': np.min(final_values),
                'max': np.max(final_values)
            },
            'final_value_percentiles': dict(zip(percentiles, final_percentiles)),
            'success_probabilities': success_probabilities,
            'success_probability': breakeven_success / simulations,  # 翻倍成功率
            'all_paths': all_paths
        }

    def calculate_dollar_cost_averaging(self, monthly_investment: float,
                                      expected_return: float,
                                      expected_volatility: float,
                                      years: int = 10) -> Dict[str, Any]:
        """
        定投收益计算

        Args:
            monthly_investment: 每月定投金额
            expected_return: 预期年化收益率
            expected_volatility: 预期年化波动率
            years: 定投年数

        Returns:
            定投分析结果
        """
        months = years * 12
        monthly_return = expected_return / 12
        monthly_vol = expected_volatility / np.sqrt(12)

        # 模拟定投路径
        simulations = 1000
        final_values = []

        for _ in range(simulations):
            # 生成月度收益率
            monthly_returns = np.random.normal(monthly_return, monthly_vol, months)

            # 计算定投累计价值
            total_invested = 0
            portfolio_value = 0

            for i, monthly_ret in enumerate(monthly_returns):
                total_invested += monthly_investment
                portfolio_value = (portfolio_value + monthly_investment) * (1 + monthly_ret)

            final_values.append(portfolio_value)

        # 计算统计指标
        total_investment = monthly_investment * months
        avg_final_value = np.mean(final_values)
        avg_total_return = (avg_final_value - total_investment) / total_investment

        return {
            'monthly_investment': monthly_investment,
            'years': years,
            'total_months': months,
            'total_investment': total_investment,
            'expected_return': expected_return,
            'expected_volatility': expected_volatility,
            'average_final_value': avg_final_value,
            'average_total_return': avg_total_return,
            'simulations': simulations,
            'final_value_statistics': {
                'mean': np.mean(final_values),
                'median': np.median(final_values),
                'std': np.std(final_values),
                'min': np.min(final_values),
                'max': np.max(final_values)
            }
        }


class SignalGenerator:
    """投资信号生成器"""

    def __init__(self, ma_short: int = 20, ma_long: int = 60,
                 rsi_period: int = 14):
        """
        初始化信号生成器

        Args:
            ma_short: 短期移动平均线周期
            ma_long: 长期移动平均线周期
            rsi_period: RSI周期
        """
        self.ma_short = ma_short
        self.ma_long = ma_long
        self.rsi_period = rsi_period

    def generate_ma_signals(self, prices: pd.Series) -> pd.DataFrame:
        """
        生成移动平均线信号

        Args:
            prices: 价格序列

        Returns:
            信号DataFrame
        """
        signals = pd.DataFrame(index=prices.index)
        signals['price'] = prices

        # 计算移动平均线
        signals['ma_short'] = prices.rolling(window=self.ma_short).mean()
        signals['ma_long'] = prices.rolling(window=self.ma_long).mean()

        # 生成信号
        signals['signal'] = 0
        signals.loc[signals['ma_short'] > signals['ma_long'], 'signal'] = 1
        signals.loc[signals['ma_short'] < signals['ma_long'], 'signal'] = -1

        # 计算信号变化
        signals['signal_change'] = signals['signal'].diff()

        return signals

    def generate_rsi_signals(self, prices: pd.Series,
                           oversold: float = 30,
                           overbought: float = 70) -> pd.DataFrame:
        """
        生成RSI信号

        Args:
            prices: 价格序列
            oversold: 超卖线
            overbought: 超买线

        Returns:
            信号DataFrame
        """
        signals = pd.DataFrame(index=prices.index)
        signals['price'] = prices

        # 计算RSI
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        signals['rsi'] = rsi

        # 生成信号
        signals['signal'] = 0
        signals.loc[rsi < oversold, 'signal'] = 1  # 超卖买入
        signals.loc[rsi > overbought, 'signal'] = -1  # 超买卖出

        return signals

    def generate_portfolio_rebalance_signal(self, current_weights: np.ndarray,
                                         target_weights: np.ndarray,
                                         threshold: float = 0.05) -> Dict[str, Any]:
        """
        生成投资组合再平衡信号

        Args:
            current_weights: 当前权重
            target_weights: 目标权重
            threshold: 权重偏离阈值

        Returns:
            再平衡信号
        """
        weight_diff = target_weights - current_weights
        abs_diff = np.abs(weight_diff)

        max_diff = np.max(abs_diff)
        needs_rebalancing = max_diff > threshold

        signal_strength = max_diff / threshold if threshold > 0 else 0

        return {
            'needs_rebalancing': needs_rebalancing,
            'signal_strength': signal_strength,
            'max_deviation': max_diff,
            'weight_differences': weight_diff,
            'absolute_differences': abs_diff,
            'deviating_assets': np.where(abs_diff > threshold)[0].tolist()
        }


class PerformanceAttribution:
    """业绩归因分析"""

    def __init__(self, benchmark_weights: Optional[np.ndarray] = None):
        """
        初始化业绩归因分析器

        Args:
            benchmark_weights: 基准权重
        """
        self.benchmark_weights = benchmark_weights

    def calculate_attribution(self, portfolio_returns: pd.Series,
                            benchmark_returns: pd.Series,
                            asset_returns: pd.DataFrame,
                            portfolio_weights: np.ndarray,
                            benchmark_weights: np.ndarray) -> Dict[str, Any]:
        """
        计算业绩归因

        Args:
            portfolio_returns: 投资组合收益率
            benchmark_returns: 基准收益率
            asset_returns: 各资产收益率
            portfolio_weights: 投资组合权重
            benchmark_weights: 基准权重

        Returns:
            业绩归因结果
        """
        # 计算超额收益
        excess_return = portfolio_returns - benchmark_returns

        # 1. 资产配置效应
        allocation_effect = self._calculate_allocation_effect(
            asset_returns, portfolio_weights, benchmark_weights
        )

        # 2. 选股效应
        selection_effect = self._calculate_selection_effect(
            asset_returns, portfolio_weights, benchmark_weights
        )

        # 3. 交互效应
        interaction_effect = self._calculate_interaction_effect(
            asset_returns, portfolio_weights, benchmark_weights
        )

        # 4. 总效应验证
        total_effect = allocation_effect + selection_effect + interaction_effect

        return {
            'total_excess_return': excess_return.mean(),
            'allocation_effect': allocation_effect,
            'selection_effect': selection_effect,
            'interaction_effect': interaction_effect,
            'total_effect': total_effect,
            'attribution_breakdown': {
                'allocation_pct': allocation_effect / total_effect * 100 if total_effect != 0 else 0,
                'selection_pct': selection_effect / total_effect * 100 if total_effect != 0 else 0,
                'interaction_pct': interaction_effect / total_effect * 100 if total_effect != 0 else 0
            }
        }

    def _calculate_allocation_effect(self, asset_returns: pd.DataFrame,
                                   portfolio_weights: np.ndarray,
                                   benchmark_weights: np.ndarray) -> float:
        """计算资产配置效应"""
        benchmark_returns = asset_returns.mean()
        weight_diff = portfolio_weights - benchmark_weights
        return np.sum(weight_diff * benchmark_returns)

    def _calculate_selection_effect(self, asset_returns: pd.DataFrame,
                                  portfolio_weights: np.ndarray,
                                  benchmark_weights: np.ndarray) -> float:
        """计算选股效应"""
        asset_excess_returns = asset_returns.mean() - asset_returns.mean().mean()
        return np.sum(benchmark_weights * asset_excess_returns)

    def _calculate_interaction_effect(self, asset_returns: pd.DataFrame,
                                    portfolio_weights: np.ndarray,
                                    benchmark_weights: np.ndarray) -> float:
        """计算交互效应"""
        asset_excess_returns = asset_returns.mean() - asset_returns.mean().mean()
        weight_diff = portfolio_weights - benchmark_weights
        return np.sum(weight_diff * asset_excess_returns)

    def calculate_contribution_analysis(self, portfolio_returns: pd.Series,
                                      weights: np.ndarray,
                                      asset_returns: pd.DataFrame) -> Dict[str, float]:
        """
        计算各资产贡献度分析

        Args:
            portfolio_returns: 投资组合收益率
            weights: 权重
            asset_returns: 各资产收益率

        Returns:
            贡献度分析结果
        """
        contributions = {}
        total_return = portfolio_returns.mean()

        for i, (weight, asset_name) in enumerate(zip(weights, asset_returns.columns)):
            asset_contribution = weight * asset_returns[asset_name].mean()
            contribution_pct = asset_contribution / total_return * 100 if total_return != 0 else 0

            contributions[asset_name] = {
                'weight': weight,
                'asset_return': asset_returns[asset_name].mean(),
                'contribution': asset_contribution,
                'contribution_pct': contribution_pct
            }

        return contributions


class PortfolioAnalyzer:
    """投资组合分析器"""

    def __init__(self):
        """初始化投资组合分析器"""
        pass

    def analyze_sector_exposure(self, etf_codes: List[str],
                              weights: np.ndarray) -> Dict[str, Any]:
        """
        分析行业敞口（简化版本）

        Args:
            etf_codes: ETF代码列表
            weights: 权重

        Returns:
            行业敞口分析
        """
        # 这里简化处理，实际应用中需要ETF的行业分类数据
        sector_mapping = self._get_etf_sector_mapping()

        sector_exposure = {}
        for etf_code, weight in zip(etf_codes, weights):
            sector = sector_mapping.get(etf_code, '其他')
            if sector not in sector_exposure:
                sector_exposure[sector] = 0
            sector_exposure[sector] += weight

        # 计算集中度指标
        herfindahl_index = sum(exposure ** 2 for exposure in sector_exposure.values())

        return {
            'sector_exposure': sector_exposure,
            'herfindahl_index': herfindahl_index,
            'max_sector_exposure': max(sector_exposure.values()),
            'sector_count': len(sector_exposure)
        }

    def _get_etf_sector_mapping(self) -> Dict[str, str]:
        """获取ETF行业映射（简化版本）"""
        # 这里只是示例，实际应用中需要完整的ETF行业分类数据
        return {
            '159632.SZ': '新能源',
            '159670.SZ': '半导体',
            '159770.SZ': '消费',
            '159995.SZ': '芯片',
            '159871.SZ': '新能源车',
            '510210.SH': '国债'
        }

    def generate_investment_recommendations(self, risk_metrics: Dict[str, Any],
                                         performance_metrics: Dict[str, Any],
                                         market_conditions: str = 'normal') -> List[str]:
        """
        生成投资建议

        Args:
            risk_metrics: 风险指标
            performance_metrics: 绩效指标
            market_conditions: 市场条件

        Returns:
            投资建议列表
        """
        recommendations = []

        # 基于风险指标的建议
        overall_risk = risk_metrics.get('risk_rating', {}).get('overall_risk', '中风险')
        if overall_risk == '高风险':
            recommendations.append("组合风险较高，建议考虑降低仓位或增加防御性资产")
        elif overall_risk == '低风险':
            recommendations.append("组合风险较低，可适当增加成长性资产配置")

        # 基于集中度风险的建议
        concentration_risk = risk_metrics.get('concentration_risk', {})
        if concentration_risk.get('hhi', 0) > 3000:
            recommendations.append("持仓集中度过高，建议分散化投资")

        # 基于绩效指标的建议
        sharpe_ratio = performance_metrics.get('sharpe_ratio', 0)
        if sharpe_ratio < 0.5:
            recommendations.append("夏普比率偏低，建议优化资产配置以提高风险调整后收益")

        max_drawdown = performance_metrics.get('max_drawdown', 0)
        if max_drawdown < -0.20:
            recommendations.append("最大回撤较大，建议加强风险控制")

        # 基于市场条件的建议
        if market_conditions == 'bull':
            recommendations.append("市场处于上涨趋势，可适当增加权益类资产配置")
        elif market_conditions == 'bear':
            recommendations.append("市场处于下跌趋势，建议增加防御性资产或现金持有")
        elif market_conditions == 'volatile':
            recommendations.append("市场波动较大，建议保持谨慎，适当降低仓位")

        return recommendations


def get_investment_calculator(initial_capital: float = 1000000) -> InvestmentCalculator:
    """获取投资计算器实例"""
    return InvestmentCalculator(initial_capital)


def get_signal_generator(ma_short: int = 20, ma_long: int = 60,
                        rsi_period: int = 14) -> SignalGenerator:
    """获取信号生成器实例"""
    return SignalGenerator(ma_short, ma_long, rsi_period)


def get_performance_attribution(benchmark_weights: Optional[np.ndarray] = None) -> PerformanceAttribution:
    """获取业绩归因分析器实例"""
    return PerformanceAttribution(benchmark_weights)


def get_portfolio_analyzer() -> PortfolioAnalyzer:
    """获取投资组合分析器实例"""
    return PortfolioAnalyzer()