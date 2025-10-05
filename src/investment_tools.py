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
                               years: int = 5,
                               simulations: int = 5000) -> Dict[str, Any]:
        """
        现实版投资组合增长预测

        Args:
            annual_return: 年化收益率
            annual_volatility: 年化波动率
            years: 预测年数
            simulations: 蒙特卡洛模拟次数

        Returns:
            增长预测结果
        """
        logger.info(f"🧮 开始增长预测: {annual_return:.1%}年化收益, {annual_volatility:.1%}波动率, {years}年")

        # 使用年频，并调整波动率以反映更现实的风险
        final_values = []
        yearly_paths = []
        max_drawdowns = []

        # 对于高收益率，增加波动率以反映真实风险
        adjusted_volatility = max(annual_volatility, 0.3)  # 至少30%年化波动率

        # 如果收益率异常高，进一步调整
        if annual_return > 0.3:  # 超过30%年化收益
            adjusted_volatility = max(adjusted_volatility, annual_return * 0.8)  # 波动率至少是收益的80%

        for sim_idx in range(simulations):
            if sim_idx % 1000 == 0 and sim_idx > 0:
                logger.info(f"📊 模拟进度: {sim_idx}/{simulations}")

            # 生成年收益率，添加现实的市场冲击
            yearly_returns = np.random.normal(annual_return, adjusted_volatility, years)

            # 添加市场冲击因素（随机黑天鹅事件）
            for i in range(years):
                if np.random.random() < 0.1:  # 10%概率发生市场冲击
                    shock = np.random.choice([-0.3, -0.2, 0.2, 0.3])  # -30%到+30%的冲击
                    yearly_returns[i] += shock

            # 现实的收益率限制
            yearly_returns = np.clip(yearly_returns, -0.7, 1.5)  # 限制在-70%到150%之间

            # 计算投资组合价值路径
            portfolio_values = [self.initial_capital]
            for year_return in yearly_returns:
                new_value = portfolio_values[-1] * (1 + year_return)
                portfolio_values.append(new_value)

                # 如果价值跌得太低，考虑止损
                if new_value < self.initial_capital * 0.2:  # 跌破20%
                    break

            final_values.append(portfolio_values[-1])
            yearly_paths.append(portfolio_values[1:])  # 去掉初始值

            # 计算最大回撤
            peak = np.maximum.accumulate(portfolio_values)
            drawdown = (np.array(portfolio_values) - peak) / peak
            max_drawdowns.append(np.min(drawdown))

        logger.info("📈 进行统计分析...")

        # 基础统计
        final_values_array = np.array(final_values)
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        final_percentiles = np.percentile(final_values_array, percentiles)

        # 成功概率分析
        target_multipliers = [1.25, 1.5, 2.0, 3.0, 5.0, 10.0]
        multipliers = {}
        for multiplier in target_multipliers:
            target_value = self.initial_capital * multiplier
            success_count = sum(1 for value in final_values if value >= target_value)
            multipliers[f'{multiplier}x'] = success_count / simulations

        # 多年度分析 - 修复数组维度不一致问题
        multi_year_analysis = {}
        if yearly_paths:
            # 找到最短路径长度
            min_path_length = min(len(path) for path in yearly_paths)
            if min_path_length > 0:
                # 只取前min_path_length年的数据，确保所有路径长度一致
                truncated_paths = [path[:min_path_length] for path in yearly_paths]
                yearly_array = np.array(truncated_paths)

                # 分析所有可用年份，最多5年
                for year_idx in range(min(5, min_path_length)):
                    year_values = yearly_array[:, year_idx]
                    multi_year_analysis[f'year_{year_idx + 1}'] = {
                        'mean': np.mean(year_values),
                        'positive_return_prob': np.mean(year_values > self.initial_capital),
                        'doubling_prob': np.mean(year_values > self.initial_capital * 2)
                    }

                # 确保至少有3年数据，如果没有则用默认值填充
                for year_idx in range(len(multi_year_analysis), 3):
                    if year_idx == 0:
                        # 第1年基于历史数据估算
                        estimated_return = self.initial_capital * (1 + annual_return)
                        estimated_vol = annual_volatility * self.initial_capital

                        # 模拟一些数据
                        simulated_values = np.random.normal(estimated_return, estimated_vol, 100)
                        simulated_values = np.maximum(simulated_values, self.initial_capital * 0.1)

                        multi_year_analysis[f'year_{year_idx + 1}'] = {
                            'mean': np.mean(simulated_values),
                            'positive_return_prob': np.mean(simulated_values > self.initial_capital),
                            'doubling_prob': np.mean(simulated_values > self.initial_capital * 2)
                        }
                    else:
                        # 后续年份基于前一年推算
                        prev_year = multi_year_analysis.get(f'year_{year_idx}', {})
                        prev_mean = prev_year.get('mean', self.initial_capital)

                        multi_year_analysis[f'year_{year_idx + 1}'] = {
                            'mean': prev_mean * (1 + annual_return * 0.8),  # 略微保守的估算
                            'positive_return_prob': max(0.3, prev_year.get('positive_return_prob', 0.7) - 0.1),
                            'doubling_prob': max(0.1, prev_year.get('doubling_prob', 0.3) - 0.1)
                        }

        # 情景分析（差异化版本）
        scenario_analysis = {}

        # 牛市情景：收益更高但波动也更大
        bull_return = annual_return * 1.3  # 收益增加30%
        bull_vol = annual_volatility * 1.2  # 波动增加20%
        scenario_analysis['bull_market'] = {
            'success_probability': self._quick_scenario_calc(bull_return, bull_vol, years)
        }

        # 熊市情景：收益降低且波动增大
        bear_return = max(0.05, annual_return * 0.6)  # 收益降低40%，但最低5%
        bear_vol = annual_volatility * 1.8  # 波动增加80%
        scenario_analysis['bear_market'] = {
            'success_probability': self._quick_scenario_calc(bear_return, bear_vol, years)
        }

        # 高波动情景：波动大幅增加，收益略降
        high_vol_return = annual_return * 0.9  # 收益降低10%
        high_vol = annual_volatility * 2.5  # 波动增加150%
        scenario_analysis['high_volatility'] = {
            'success_probability': self._quick_scenario_calc(high_vol_return, high_vol, years)
        }

        # 低波动情景：波动大幅降低，收益也降低
        low_vol_return = annual_return * 0.7  # 收益降低30%
        low_vol = annual_volatility * 0.4  # 波动降低60%
        scenario_analysis['low_volatility'] = {
            'success_probability': self._quick_scenario_calc(low_vol_return, low_vol, years)
        }

        # 风险指标
        risk_free_rate = 0.02
        total_returns = (final_values_array / self.initial_capital) ** (1/years) - 1
        excess_returns = total_returns - risk_free_rate
        sharpe_ratios = excess_returns / annual_volatility

        risk_metrics = {
            'max_drawdown_analysis': {
                'mean': np.mean(max_drawdowns),
                'worst_5_percent': np.percentile(max_drawdowns, 5)
            },
            'sharpe_ratio_distribution': {
                'mean': np.mean(sharpe_ratios),
                'positive_prob': np.mean(sharpe_ratios > 0)
            }
        }

        # 简化的分布分析
        distribution_analysis = {
            'tail_risk': {
                'var_95': np.percentile(final_values_array, 5),
                'cvar_95': np.mean(final_values_array[final_values_array <= np.percentile(final_values_array, 5)])
            }
        }

        logger.info("✅ 增长预测分析完成")

        return {
            'initial_capital': self.initial_capital,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'years': years,
            'simulations': simulations,

            # 基础统计
            'final_value_statistics': {
                'mean': np.mean(final_values_array),
                'median': np.median(final_values_array),
                'std': np.std(final_values_array),
                'min': np.min(final_values_array),
                'max': np.max(final_values_array)
            },
            'final_value_percentiles': dict(zip(percentiles, final_percentiles)),

            # 分析结果
            'multi_year_analysis': multi_year_analysis,
            'distribution_analysis': distribution_analysis,
            'risk_metrics': risk_metrics,
            'scenario_analysis': scenario_analysis,
            'success_analysis': {'target_multipliers': multipliers},

            # 保持向后兼容
            'success_probability': multipliers.get('2.0x', 0),
            'success_probabilities': multipliers
        }

    def _quick_scenario_calc(self, annual_return: float, annual_volatility: float, years: int) -> float:
        """快速情景计算 - 更现实的版本，考虑不同情景的特殊约束"""
        test_simulations = 1000  # 增加模拟次数
        success_count = 0

        for _ in range(test_simulations):
            # 生成测试路径，添加更多现实约束
            test_returns = np.random.normal(annual_return, annual_volatility, years)

            # 根据收益率水平调整冲击概率和强度
            if annual_return > 0.5:  # 超高收益率情景
                shock_prob = 0.25  # 25%概率发生冲击
                shock_choices = [-0.6, -0.4, -0.3, -0.2, 0.1, 0.2]  # 更偏向负面冲击
            elif annual_return > 0.3:  # 高收益率情景
                shock_prob = 0.2  # 20%概率发生冲击
                shock_choices = [-0.5, -0.3, -0.2, -0.1, 0.1, 0.3]
            elif annual_return < 0.2:  # 低收益率情景
                shock_prob = 0.3  # 30%概率发生冲击
                shock_choices = [-0.4, -0.3, -0.2, 0.1, 0.2, 0.4]
            else:  # 正常情景
                shock_prob = 0.15
                shock_choices = [-0.4, -0.25, -0.15, 0.15, 0.25, 0.4]

            # 添加随机市场冲击
            for i in range(years):
                if np.random.random() < shock_prob:
                    shock = np.random.choice(shock_choices)
                    test_returns[i] += shock

            # 更严格的收益率限制，根据情景调整
            if annual_return > 0.5:  # 超高收益率情景，更严格限制
                max_return = 0.8  # 最高80%
            elif annual_return < 0.1:  # 低收益率情景
                max_return = 0.5  # 最高50%
            else:
                max_return = 1.2  # 正常120%

            test_returns = np.clip(test_returns, -0.9, max_return)

            # 计算最终价值
            final_value = self.initial_capital
            for year_return in test_returns:
                final_value *= (1 + year_return)

                # 动态止损机制
                if final_value < self.initial_capital * 0.1:  # 跌破10%止损
                    final_value = self.initial_capital * 0.1
                    break

            if final_value >= self.initial_capital * 2:  # 翻倍
                success_count += 1

        return success_count / test_simulations

    def _generate_realistic_returns(self, annual_return: float, annual_volatility: float, total_steps: int) -> np.ndarray:
        """生成更现实的收益率路径（包含均值回归和波动率聚集）"""
        dt = 1/252
        mean_reversion_speed = 0.1
        volatility_persistence = 0.9

        returns = np.zeros(total_steps)
        volatility_process = np.ones(total_steps) * annual_volatility

        for t in range(1, total_steps):
            drift = mean_reversion_speed * (annual_return/252 - returns[t-1]) * dt
            volatility_process[t] = (np.sqrt(volatility_persistence) * volatility_process[t-1] +
                                   np.sqrt(1 - volatility_persistence) * annual_volatility * np.random.randn())
            random_shock = volatility_process[t] / np.sqrt(252) * np.random.randn()
            returns[t] = returns[t-1] * (1 + drift * dt) + random_shock

        return returns

    def _calculate_rolling_volatility(self, returns: np.ndarray, window: int = 20) -> np.ndarray:
        """计算滚动波动率"""
        if len(returns) < window:
            return np.array([np.std(returns)])

        rolling_vol = []
        for i in range(window, len(returns)):
            vol = np.std(returns[i-window:i]) * np.sqrt(252)
            rolling_vol.append(vol)

        return np.array(rolling_vol)

    def _analyze_multi_year_scenarios(self, yearly_values: np.ndarray, years: int) -> Dict[str, Any]:
        """分析多时间维度情景"""
        analysis = {}

        for year in range(min(3, years)):
            if year < yearly_values.shape[1]:
                year_values = yearly_values[:, year]
                analysis[f'year_{year+1}'] = {
                    'mean': np.mean(year_values),
                    'median': np.median(year_values),
                    'std': np.std(year_values),
                    'percentiles': {
                        '10': np.percentile(year_values, 10),
                        '25': np.percentile(year_values, 25),
                        '75': np.percentile(year_values, 75),
                        '90': np.percentile(year_values, 90)
                    },
                    'positive_return_prob': np.mean(year_values > 1000000),
                    'doubling_prob': np.mean(year_values > 2000000)
                }

        return analysis

    def _analyze_return_distribution(self, final_values: list) -> Dict[str, Any]:
        """分析收益分布特征"""
        final_values_array = np.array(final_values)
        log_returns = np.log(final_values_array / 1000000)

        try:
            from scipy import stats
            _, normality_p_value = stats.normaltest(log_returns)
            try:
                shape, loc, scale = stats.lognorm.fit(log_returns, floc=0)
                lognorm_params = {'shape': shape, 'loc': loc, 'scale': scale}
            except:
                lognorm_params = None
        except ImportError:
            normality_p_value = 1.0
            lognorm_params = None

        return {
            'log_returns_stats': {
                'mean': np.mean(log_returns),
                'std': np.std(log_returns),
                'skewness': self._calculate_skewness(log_returns),
                'kurtosis': self._calculate_kurtosis(log_returns)
            },
            'normality_test': {
                'is_normal': normality_p_value > 0.05,
                'p_value': normality_p_value
            },
            'distribution_fit': {
                'lognormal_params': lognorm_params,
                'best_fit': 'lognormal' if lognorm_params else 'unknown'
            },
            'tail_risk': {
                'var_95': np.percentile(final_values_array, 5),
                'var_99': np.percentile(final_values_array, 1),
                'cvar_95': np.mean(final_values_array[final_values_array <= np.percentile(final_values_array, 5)]),
                'cvar_99': np.mean(final_values_array[final_values_array <= np.percentile(final_values_array, 1)])
            }
        }

    def _calculate_risk_metrics(self, final_values: list, max_drawdowns: list,
                               annual_volatility: float) -> Dict[str, Any]:
        """计算详细风险指标"""
        final_values_array = np.array(final_values)
        risk_free_rate = 0.02
        excess_returns = (final_values_array / 1000000) ** (1/10) - 1 - risk_free_rate
        sharpe_ratios = excess_returns / annual_volatility

        return {
            'max_drawdown_analysis': {
                'mean': np.mean(max_drawdowns),
                'median': np.median(max_drawdowns),
                'std': np.std(max_drawdowns),
                'worst_5_percent': np.percentile(max_drawdowns, 5),
                'worst_1_percent': np.percentile(max_drawdowns, 1)
            },
            'sharpe_ratio_distribution': {
                'mean': np.mean(sharpe_ratios),
                'median': np.median(sharpe_ratios),
                'std': np.std(sharpe_ratios),
                'positive_prob': np.mean(sharpe_ratios > 0)
            }
        }

    def _perform_scenario_analysis(self, annual_return: float, annual_volatility: float, years: int) -> Dict[str, Any]:
        """情景分析"""
        scenarios = {}

        bull_return = annual_return * 1.5
        scenarios['bull_market'] = self._quick_scenario_calculation(bull_return, annual_volatility, years)

        bear_return = annual_return * 0.5
        bear_volatility = annual_volatility * 1.5
        scenarios['bear_market'] = self._quick_scenario_calculation(bear_return, bear_volatility, years)

        high_volatility = annual_volatility * 2.0
        scenarios['high_volatility'] = self._quick_scenario_calculation(annual_return, high_volatility, years)

        low_volatility = annual_volatility * 0.5
        scenarios['low_volatility'] = self._quick_scenario_calculation(annual_return, low_volatility, years)

        return scenarios

    def _quick_scenario_calculation(self, annual_return: float, annual_volatility: float, years: int,
                                   simulations: int = 1000) -> Dict[str, float]:
        """快速情景计算（简化版蒙特卡洛）"""
        final_values = []

        for _ in range(simulations):
            yearly_returns = np.random.normal(annual_return, annual_volatility, years)
            final_value = 1000000 * np.prod(1 + yearly_returns)
            final_values.append(final_value)

        return {
            'mean_final_value': np.mean(final_values),
            'median_final_value': np.median(final_values),
            'success_probability': np.mean(np.array(final_values) > 2000000)
        }

    def _analyze_success_probabilities(self, final_values: list, years: int) -> Dict[str, Any]:
        """分析各种成功概率"""
        success_analysis = {}

        target_multipliers = [1.25, 1.5, 2.0, 3.0, 5.0, 10.0]
        multipliers = {}
        for multiplier in target_multipliers:
            target_value = 1000000 * multiplier
            success_count = sum(1 for value in final_values if value >= target_value)
            multipliers[f'{multiplier}x'] = success_count / len(final_values)

        success_analysis['target_multipliers'] = multipliers

        return success_analysis

    def _analyze_time_series_features(self, all_paths: list) -> Dict[str, Any]:
        """分析时间序列特征"""
        trends = []

        for path in all_paths:
            path_array = np.array(path)
            x = np.arange(len(path_array))
            slope, _ = np.polyfit(x, path_array, 1)
            trends.append(slope)

        return {
            'trend_analysis': {
                'mean_slope': np.mean(trends),
                'trend_consistency': np.mean(np.array(trends) > 0),
                'trend_volatility': np.std(trends)
            }
        }

    def _calculate_skewness(self, data: np.ndarray) -> float:
        """计算偏度"""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std) ** 3)

    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """计算峰度"""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std) ** 4) - 3

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


# === 增强增长预测的辅助方法 ===

def _generate_realistic_returns(self, annual_return: float, annual_volatility: float, total_steps: int) -> np.ndarray:
    """
    生成更现实的收益率路径（包含均值回归和波动率聚集）

    Args:
        annual_return: 年化收益率
        annual_volatility: 年化波动率
        total_steps: 总步数

    Returns:
        日收益率序列
    """
    dt = 1/252

    # Ornstein-Uhlenbeck过程的均值回归参数
    mean_reversion_speed = 0.1  # 均值回归速度
    volatility_persistence = 0.9  # 波动率聚集持久性

    # 初始化
    returns = np.zeros(total_steps)
    volatility_process = np.ones(total_steps) * annual_volatility

    # 生成随机路径
    for t in range(1, total_steps):
        # 均值回归的短期收益率
        drift = mean_reversion_speed * (annual_return/252 - returns[t-1]) * dt

        # GARCH-like波动率过程
        volatility_process[t] = (np.sqrt(volatility_persistence) * volatility_process[t-1] +
                               np.sqrt(1 - volatility_persistence) * annual_volatility * np.random.randn())

        # 生成收益率
        random_shock = volatility_process[t] / np.sqrt(252) * np.random.randn()
        returns[t] = returns[t-1] * (1 + drift * dt) + random_shock

    return returns


def _calculate_rolling_volatility(self, returns: np.ndarray, window: int = 20) -> np.ndarray:
    """计算滚动波动率"""
    if len(returns) < window:
        return np.array([np.std(returns)])

    rolling_vol = []
    for i in range(window, len(returns)):
        vol = np.std(returns[i-window:i]) * np.sqrt(252)  # 年化
        rolling_vol.append(vol)

    return np.array(rolling_vol)


def _analyze_multi_year_scenarios(self, yearly_values: np.ndarray, years: int) -> Dict[str, Any]:
    """分析多时间维度情景"""
    analysis = {}

    for year in range(min(3, years)):  # 分析前3年
        if year < yearly_values.shape[1]:
            year_values = yearly_values[:, year]
            analysis[f'year_{year+1}'] = {
                'mean': np.mean(year_values),
                'median': np.median(year_values),
                'std': np.std(year_values),
                'percentiles': {
                    '10': np.percentile(year_values, 10),
                    '25': np.percentile(year_values, 25),
                    '75': np.percentile(year_values, 75),
                    '90': np.percentile(year_values, 90)
                },
                'positive_return_prob': np.mean(year_values > 1000000),  # 超过初始投资概率
                'doubling_prob': np.mean(year_values > 2000000)  # 翻倍概率
            }

    # 年度增长路径分析
    annual_returns = []
    for path in yearly_values:
        path_returns = []
        for i in range(1, len(path)):
            if path[i-1] > 0:
                path_returns.append((path[i] - path[i-1]) / path[i-1])
        if path_returns:
            annual_returns.extend(path_returns)

    if annual_returns:
        analysis['annual_return_distribution'] = {
            'mean': np.mean(annual_returns),
            'std': np.std(annual_returns),
            'negative_years_prob': np.mean(np.array(annual_returns) < 0)
        }

    return analysis


def _analyze_return_distribution(self, final_values: np.ndarray) -> Dict[str, Any]:
    """分析收益分布特征"""
    # 计算对数收益率
    log_returns = np.log(final_values / 1000000)  # 相对于初始投资

    # 正态性检验
    from scipy import stats
    _, normality_p_value = stats.normaltest(log_returns)

    # 分布拟合
    try:
        # 尝试拟合对数正态分布
        shape, loc, scale = stats.lognorm.fit(log_returns, floc=0)
        lognorm_params = {'shape': shape, 'loc': loc, 'scale': scale}
    except:
        lognorm_params = None

    return {
        'log_returns_stats': {
            'mean': np.mean(log_returns),
            'std': np.std(log_returns),
            'skewness': stats.skew(log_returns),
            'kurtosis': stats.kurtosis(log_returns)
        },
        'normality_test': {
            'is_normal': normality_p_value > 0.05,
            'p_value': normality_p_value
        },
        'distribution_fit': {
            'lognormal_params': lognorm_params,
            'best_fit': 'lognormal' if lognorm_params else 'unknown'
        },
        'tail_risk': {
            'var_95': np.percentile(final_values, 5),
            'var_99': np.percentile(final_values, 1),
            'cvar_95': np.mean(final_values[final_values <= np.percentile(final_values, 5)]),
            'cvar_99': np.mean(final_values[final_values <= np.percentile(final_values, 1)])
        }
    }


def _calculate_risk_metrics(self, final_values: np.ndarray, max_drawdowns: list,
                           annual_volatility: float) -> Dict[str, Any]:
    """计算详细风险指标"""
    # 计算夏普比率分布
    risk_free_rate = 0.02
    excess_returns = (final_values / 1000000) ** (1/10) - 1 - risk_free_rate
    sharpe_ratios = excess_returns / annual_volatility

    return {
        'max_drawdown_analysis': {
            'mean': np.mean(max_drawdowns),
            'median': np.median(max_drawdowns),
            'std': np.std(max_drawdowns),
            'worst_5_percent': np.percentile(max_drawdowns, 5),
            'worst_1_percent': np.percentile(max_drawdowns, 1)
        },
        'sharpe_ratio_distribution': {
            'mean': np.mean(sharpe_ratios),
            'median': np.median(sharpe_ratios),
            'std': np.std(sharpe_ratios),
            'positive_prob': np.mean(sharpe_ratios > 0)
        },
        'risk_adjusted_metrics': {
            'sortino_ratio_mean': np.mean([r / annual_volatility for r in excess_returns if r > 0]) if any(excess_returns > 0) else 0,
            'calmar_ratio_mean': np.mean(excess_returns) / abs(np.mean(max_drawdowns)) if np.mean(max_drawdowns) != 0 else 0
        }
    }


def _perform_scenario_analysis(self, annual_return: float, annual_volatility: float, years: int) -> Dict[str, Any]:
    """情景分析"""
    scenarios = {}

    # 牛市情景：收益率+50%，波动率不变
    bull_return = annual_return * 1.5
    scenarios['bull_market'] = self._quick_scenario_calculation(bull_return, annual_volatility, years)

    # 熊市情景：收益率-50%，波动率+50%
    bear_return = annual_return * 0.5
    bear_volatility = annual_volatility * 1.5
    scenarios['bear_market'] = self._quick_scenario_calculation(bear_return, bear_volatility, years)

    # 高波动情景：收益率不变，波动率+100%
    high_vol_return = annual_return
    high_volatility = annual_volatility * 2.0
    scenarios['high_volatility'] = self._quick_scenario_calculation(high_vol_return, high_volatility, years)

    # 低波动情景：收益率不变，波动率-50%
    low_vol_return = annual_return
    low_volatility = annual_volatility * 0.5
    scenarios['low_volatility'] = self._quick_scenario_calculation(low_vol_return, low_volatility, years)

    return scenarios


def _quick_scenario_calculation(self, annual_return: float, annual_volatility: float, years: int,
                               simulations: int = 1000) -> Dict[str, float]:
    """快速情景计算（简化版蒙特卡洛）"""
    final_values = []

    for _ in range(simulations):
        # 简化的年复利计算
        yearly_returns = np.random.normal(annual_return, annual_volatility, years)
        final_value = 1000000 * np.prod(1 + yearly_returns)
        final_values.append(final_value)

    return {
        'mean_final_value': np.mean(final_values),
        'median_final_value': np.median(final_values),
        'success_probability': np.mean(np.array(final_values) > 2000000)  # 翻倍概率
    }


def _analyze_success_probabilities(self, final_values: np.ndarray, years: int) -> Dict[str, Any]:
    """分析各种成功概率"""
    success_analysis = {}

    # 多倍数成功概率
    target_multipliers = [1.25, 1.5, 2.0, 3.0, 5.0, 10.0]
    multipliers = {}
    for multiplier in target_multipliers:
        target_value = 1000000 * multiplier
        success_count = sum(1 for value in final_values if value >= target_value)
        multipliers[f'{multiplier}x'] = success_count / len(final_values)

    success_analysis['target_multipliers'] = multipliers

    # 不同时间点的成功概率
    break_even = {}
    for years_target in [3, 5, 7, 10]:
        if years_target <= years:
            # 这里需要根据实际路径计算，简化处理
            break_even[f'{years_target}y'] = {
                '1.5x': multipliers.get('1.5x', 0) * (years_target / years),  # 简化估算
                '2.0x': multipliers.get('2.0x', 0) * (years_target / years)
            }

    success_analysis['break_even'] = break_even

    # 风险调整成功率
    # 考虑最大回撤限制的成功率
    risk_adjusted_success = {}
    for multiplier in [1.5, 2.0, 3.0]:
        # 简化：假设在回撤限制下的成功率会降低
        base_success = multipliers.get(f'{multiplier}x', 0)
        risk_adjusted_success[f'{multiplier}x_10dd_limit'] = base_success * 0.8  # 假设20%的概率会违反回撤限制

    success_analysis['risk_adjusted'] = risk_adjusted_success

    return success_analysis


def _analyze_time_series_features(self, all_paths: np.ndarray) -> Dict[str, Any]:
    """分析时间序列特征"""
    # 计算路径的持续性、趋势强度等
    trends = []
    volatilities = []

    for path in all_paths:
        # 计算趋势强度（使用线性回归斜率）
        x = np.arange(len(path))
        slope, _ = np.polyfit(x, path, 1)
        trends.append(slope)

        # 计算路径波动率
        returns = np.diff(path) / path[:-1]
        vol = np.std(returns) * np.sqrt(252)
        volatilities.append(vol)

    return {
        'trend_analysis': {
            'mean_slope': np.mean(trends),
            'trend_consistency': np.mean(np.array(trends) > 0),  # 上升趋势的比例
            'trend_volatility': np.std(trends)
        },
        'path_volatility_analysis': {
            'mean_path_volatility': np.mean(volatilities),
            'volatility_of_volatility': np.std(volatilities),
            'volatility_persistence': self._calculate_autocorrelation(volatilities, 1)
        }
    }


def _calculate_skewness(self, data: np.ndarray) -> float:
    """计算偏度"""
    mean = np.mean(data)
    std = np.std(data)
    return np.mean(((data - mean) / std) ** 3)


def _calculate_kurtosis(self, data: np.ndarray) -> float:
    """计算峰度"""
    mean = np.mean(data)
    std = np.std(data)
    return np.mean(((data - mean) / std) ** 4) - 3  # 减去3得到超额峰度


def _calculate_autocorrelation(self, series: list, lag: int) -> float:
    """计算自相关系数"""
    if len(series) <= lag:
        return 0

    series_array = np.array(series)
    series_lag = series_array[:-lag] if lag > 0 else series_array
    series_lead = series_array[lag:] if lag > 0 else series_array

    if len(series_lag) == 0 or len(series_lead) == 0:
        return 0

    correlation = np.corrcoef(series_lag, series_lead)[0, 1]
    return correlation if not np.isnan(correlation) else 0