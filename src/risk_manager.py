"""
高级风险管理模块
提供VaR、CVaR、压力测试等风险指标计算
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AdvancedRiskManager:
    """高级风险管理类"""

    def __init__(self, confidence_levels: List[float] = [0.95, 0.99]):
        """
        初始化风险管理器

        Args:
            confidence_levels: 置信度水平列表，默认[95%, 99%]
        """
        self.confidence_levels = confidence_levels

    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95,
                     method: str = 'historical') -> float:
        """
        计算风险价值(VaR)

        Args:
            returns: 收益率序列
            confidence_level: 置信度水平
            method: 计算方法 ('historical', 'parametric', 'monte_carlo')

        Returns:
            VaR值（负数表示损失）
        """
        if method == 'historical':
            return self._historical_var(returns, confidence_level)
        elif method == 'parametric':
            return self._parametric_var(returns, confidence_level)
        elif method == 'monte_carlo':
            return self._monte_carlo_var(returns, confidence_level)
        else:
            raise ValueError(f"未知的VaR计算方法: {method}")

    def _historical_var(self, returns: pd.Series, confidence_level: float) -> float:
        """历史模拟法计算VaR"""
        return np.percentile(returns, (1 - confidence_level) * 100)

    def _parametric_var(self, returns: pd.Series, confidence_level: float) -> float:
        """参数法计算VaR（假设正态分布）"""
        mean = returns.mean()
        std = returns.std()
        z_score = stats.norm.ppf(1 - confidence_level)
        return mean + z_score * std

    def _monte_carlo_var(self, returns: pd.Series, confidence_level: float,
                        simulations: int = 10000) -> float:
        """蒙特卡洛模拟法计算VaR"""
        mean = returns.mean()
        std = returns.std()

        # 生成随机收益率
        simulated_returns = np.random.normal(mean, std, simulations)
        return np.percentile(simulated_returns, (1 - confidence_level) * 100)

    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95,
                      method: str = 'historical') -> float:
        """
        计算条件风险价值(CVaR/Expected Shortfall)

        Args:
            returns: 收益率序列
            confidence_level: 置信度水平
            method: 计算方法

        Returns:
            CVaR值（负数表示损失）
        """
        var = self.calculate_var(returns, confidence_level, method)

        if method == 'historical':
            # 历史法：计算超过VaR的平均损失
            tail_losses = returns[returns <= var]
            return tail_losses.mean() if len(tail_losses) > 0 else var
        else:
            # 参数法：使用正态分布的期望值
            mean = returns.mean()
            std = returns.std()
            z_var = stats.norm.ppf(1 - confidence_level)
            phi_z_var = stats.norm.pdf(z_var)
            cvar = mean - std * phi_z_var / (1 - confidence_level)
            return cvar

    def calculate_var_cvar_summary(self, returns: pd.Series) -> Dict[str, Dict[str, float]]:
        """
        计算多个置信度水平的VaR和CVaR摘要

        Args:
            returns: 收益率序列

        Returns:
            VaR和CVaR摘要字典
        """
        summary = {}

        for conf_level in self.confidence_levels:
            summary[conf_level] = {}

            for method in ['historical', 'parametric']:
                var = self.calculate_var(returns, conf_level, method)
                cvar = self.calculate_cvar(returns, conf_level, method)

                summary[conf_level][f'var_{method}'] = var
                summary[conf_level][f'cvar_{method}'] = cvar

        return summary

    def stress_test(self, returns: pd.Series, scenarios: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        压力测试

        Args:
            returns: 历史收益率序列
            scenarios: 压力情景字典，格式：{'情景名': {'shock': 冲击幅度, 'duration': 持续天数}}

        Returns:
            压力测试结果
        """
        results = {}
        current_price = 100  # 假设当前价格为100

        for scenario_name, params in scenarios.items():
            shock = params['shock']  # 负数表示下跌
            duration = params['duration']

            # 计算压力情景下的价格变化
            stressed_price = current_price * (1 + shock)
            portfolio_return = (stressed_price - current_price) / current_price

            # 计算历史同期分位数
            historical_percentile = stats.percentileofscore(returns, portfolio_return)

            results[scenario_name] = {
                'portfolio_return': portfolio_return,
                'price_impact': f"{shock:.1%}",
                'historical_percentile': historical_percentile,
                'stress_duration': duration
            }

        return results

    def calculate_correlation_matrix(self, returns: pd.DataFrame) -> pd.DataFrame:
        """
        计算相关性矩阵

        Args:
            returns: 多资产收益率DataFrame

        Returns:
            相关性矩阵
        """
        return returns.corr()

    def calculate_concentration_risk(self, weights: np.ndarray,
                                   etf_codes: List[str]) -> Dict[str, Any]:
        """
        计算集中度风险

        Args:
            weights: 投资组合权重
            etf_codes: ETF代码列表

        Returns:
            集中度风险指标
        """
        # 前N大持仓权重
        top_weights_idx = np.argsort(weights)[::-1]
        top_5_weight = weights[top_weights_idx[:5]].sum() if len(weights) >= 5 else weights.sum()
        top_3_weight = weights[top_weights_idx[:3]].sum() if len(weights) >= 3 else weights.sum()

        # Herfindahl-Hirschman Index (HHI)
        hhi = np.sum(weights ** 2) * 10000  # 乘以10000避免过小数值

        # 有效持仓数量
        effective_n = 1 / np.sum(weights ** 2)

        return {
            'top_5_concentration': top_5_weight,
            'top_3_concentration': top_3_weight,
            'hhi': hhi,
            'effective_holdings': effective_n,
            'max_single_weight': weights.max(),
            'min_weight': weights[weights > 0.001].min() if (weights > 0.001).any() else 0
        }

    def calculate_drawdown_risk_metrics(self, cumulative_returns: pd.Series) -> Dict[str, float]:
        """
        计算回撤相关风险指标

        Args:
            cumulative_returns: 累计收益率序列

        Returns:
            回撤风险指标
        """
        # 计算回撤
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max

        # 最大回撤
        max_drawdown = drawdown.min()

        # 平均回撤
        avg_drawdown = drawdown[drawdown < 0].mean() if (drawdown < 0).any() else 0

        # 回撤持续时间
        drawdown_periods = []
        in_drawdown = False
        current_duration = 0

        for dd in drawdown:
            if dd < 0:
                if not in_drawdown:
                    in_drawdown = True
                    current_duration = 1
                else:
                    current_duration += 1
            else:
                if in_drawdown:
                    drawdown_periods.append(current_duration)
                    in_drawdown = False
                    current_duration = 0

        if in_drawdown:
            drawdown_periods.append(current_duration)

        avg_drawdown_duration = np.mean(drawdown_periods) if drawdown_periods else 0
        max_drawdown_duration = max(drawdown_periods) if drawdown_periods else 0

        # 回撤频率
        drawdown_count = len(drawdown_periods)
        total_periods = len(drawdown)
        drawdown_frequency = drawdown_count / total_periods if total_periods > 0 else 0

        return {
            'max_drawdown': max_drawdown,
            'avg_drawdown': avg_drawdown,
            'max_drawdown_duration': max_drawdown_duration,
            'avg_drawdown_duration': avg_drawdown_duration,
            'drawdown_frequency': drawdown_frequency,
            'drawdown_count': drawdown_count
        }

    def generate_risk_report(self, portfolio_returns: pd.Series,
                           weights: np.ndarray, etf_codes: List[str],
                           all_returns: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        生成综合风险报告

        Args:
            portfolio_returns: 投资组合收益率
            weights: 投资组合权重
            etf_codes: ETF代码列表
            all_returns: 所有ETF收益率数据（用于相关性分析）

        Returns:
            综合风险报告
        """
        risk_report = {}

        # 1. VaR和CVaR分析
        var_cvar_summary = self.calculate_var_cvar_summary(portfolio_returns)
        risk_report['var_cvar_analysis'] = var_cvar_summary

        # 2. 集中度风险
        concentration_risk = self.calculate_concentration_risk(weights, etf_codes)
        risk_report['concentration_risk'] = concentration_risk

        # 3. 回撤风险分析
        cumulative_returns = (1 + portfolio_returns).cumprod()
        drawdown_risks = self.calculate_drawdown_risk_metrics(cumulative_returns)
        risk_report['drawdown_risks'] = drawdown_risks

        # 4. 相关性风险（如果提供了多资产数据）
        if all_returns is not None:
            correlation_matrix = self.calculate_correlation_matrix(all_returns)
            # 计算平均相关性
            mask = np.ones(correlation_matrix.shape, dtype=bool)
            np.fill_diagonal(mask, False)
            avg_correlation = correlation_matrix.values[mask].mean()
            max_correlation = correlation_matrix.values[mask].max()

            risk_report['correlation_risk'] = {
                'average_correlation': avg_correlation,
                'max_correlation': max_correlation,
                'correlation_matrix': correlation_matrix.to_dict()
            }

        # 5. 压力测试情景
        stress_scenarios = {
            'market_crash': {'shock': -0.30, 'duration': 22},  # 30%下跌，持续1个月
            'moderate_decline': {'shock': -0.15, 'duration': 15},  # 15%下跌，持续3周
            'flash_crash': {'shock': -0.10, 'duration': 1},  # 10%下跌，1天
            'bear_market': {'shock': -0.40, 'duration': 126}  # 40%下跌，持续6个月
        }

        stress_results = self.stress_test(portfolio_returns, stress_scenarios)
        risk_report['stress_test'] = stress_results

        # 6. 风险评级
        risk_rating = self._calculate_risk_rating(risk_report)
        risk_report['risk_rating'] = risk_rating

        return risk_report

    def _calculate_risk_rating(self, risk_report: Dict[str, Any]) -> Dict[str, str]:
        """
        计算风险评级

        Args:
            risk_report: 风险报告

        Returns:
            风险评级
        """
        ratings = {}

        # 基于VaR的风险评级
        var_95 = risk_report['var_cvar_analysis'][0.95]['var_historical']
        if var_95 > -0.02:
            ratings['var_risk'] = '低'
        elif var_95 > -0.05:
            ratings['var_risk'] = '中'
        else:
            ratings['var_risk'] = '高'

        # 基于集中度的风险评级
        hhi = risk_report['concentration_risk']['hhi']
        if hhi < 2000:
            ratings['concentration_risk'] = '低'
        elif hhi < 3500:
            ratings['concentration_risk'] = '中'
        else:
            ratings['concentration_risk'] = '高'

        # 基于最大回撤的风险评级
        max_dd = risk_report['drawdown_risks']['max_drawdown']
        if max_dd > -0.10:
            ratings['drawdown_risk'] = '低'
        elif max_dd > -0.25:
            ratings['drawdown_risk'] = '中'
        else:
            ratings['drawdown_risk'] = '高'

        # 综合风险评级
        risk_scores = {'低': 1, '中': 2, '高': 3}
        total_score = sum(risk_scores[rating] for rating in ratings.values())

        if total_score <= 4:
            ratings['overall_risk'] = '低风险'
        elif total_score <= 7:
            ratings['overall_risk'] = '中风险'
        else:
            ratings['overall_risk'] = '高风险'

        return ratings


def get_advanced_risk_manager(confidence_levels: List[float] = [0.95, 0.99]) -> AdvancedRiskManager:
    """获取高级风险管理器实例"""
    return AdvancedRiskManager(confidence_levels)