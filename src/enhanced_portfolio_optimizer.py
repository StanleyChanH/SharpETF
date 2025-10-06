"""
增强投资组合优化器
集成高级量化指标来最大化夏普比率
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional, Any
import logging
from .quant_signals import QuantSignals
from .evaluator import PortfolioEvaluator

logger = logging.getLogger(__name__)


class EnhancedPortfolioOptimizer:
    """增强投资组合优化器"""

    def __init__(self, risk_free_rate: float = 0.02, trading_days: int = 252):
        """
        初始化增强优化器

        Args:
            risk_free_rate: 无风险利率
            trading_days: 年交易天数
        """
        self.risk_free_rate = risk_free_rate
        self.trading_days = trading_days
        self.quant_indicators = QuantSignals(trading_days, mode='advanced')
        self.evaluator = PortfolioEvaluator(trading_days, risk_free_rate)

    def optimize_with_enhanced_signals(self, returns: pd.DataFrame,
                                     prices: pd.DataFrame,
                                     signals: Dict[str, pd.Series],
                                     signal_weights: Optional[Dict[str, float]] = None) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        使用增强信号进行投资组合优化

        Args:
            returns: 历史收益率数据
            prices: 价格数据
            signals: 量化信号字典
            signal_weights: 信号权重字典

        Returns:
            (最优权重, 优化结果指标)
        """
        logger.info("开始增强信号投资组合优化...")

        # 计算年化收益率和协方差矩阵
        annual_mean = returns.mean() * self.trading_days
        annual_cov = returns.cov() * self.trading_days

        # 处理信号权重
        if signal_weights is None:
            signal_weights = {
                'momentum_signal': 0.2,
                'quality_signal': 0.25,
                'technical_signal': 0.15,
                'risk_adjusted_signal': 0.2,
                'alpha_signal': 0.2
            }

        # 计算信号调整后的预期收益
        enhanced_expected_returns = self._calculate_enhanced_expected_returns(
            annual_mean, signals, signal_weights, returns
        )

        # 计算信号调整后的风险模型
        enhanced_cov_matrix = self._calculate_enhanced_cov_matrix(
            annual_cov, signals, signal_weights
        )

        # 执行优化
        optimal_weights, metrics = self._optimize_with_enhanced_inputs(
            enhanced_expected_returns, enhanced_cov_matrix
        )

        # 添加信号分析到结果中
        metrics['signal_analysis'] = self._analyze_signal_contributions(
            signals, signal_weights, optimal_weights
        )

        logger.info("增强信号投资组合优化完成")
        return optimal_weights, metrics

    def _calculate_enhanced_expected_returns(self, annual_mean: pd.Series,
                                           signals: Dict[str, pd.Series],
                                           signal_weights: Dict[str, float],
                                           returns: pd.DataFrame) -> pd.Series:
        """
        计算信号增强的预期收益

        Args:
            annual_mean: 原始年化收益率
            signals: 量化信号
            signal_weights: 信号权重
            returns: 历史收益率

        Returns:
            增强后的预期收益率
        """
        enhanced_returns = annual_mean.copy()

        for signal_name, signal_values in signals.items():
            if signal_name in signal_weights and isinstance(signal_values, pd.Series):
                weight = signal_weights[signal_name]

                # 标准化信号
                signal_normalized = (signal_values - signal_values.mean()) / signal_values.std()

                # 计算信号的收益贡献
                signal_return_impact = signal_normalized * annual_mean.std() * weight * 0.1  # 调整信号影响强度

                # 累积信号影响
                enhanced_returns += signal_return_impact

        return enhanced_returns

    def _calculate_enhanced_cov_matrix(self, annual_cov: pd.DataFrame,
                                     signals: Dict[str, pd.Series],
                                     signal_weights: Dict[str, float]) -> pd.DataFrame:
        """
        计算信号增强的协方差矩阵

        Args:
            annual_cov: 原始年化协方差矩阵
            signals: 量化信号
            signal_weights: 信号权重

        Returns:
            增强后的协方差矩阵
        """
        enhanced_cov = annual_cov.copy()

        # 基于信号相关性调整协方差
        signal_correlations = {}
        for signal_name, signal_values in signals.items():
            if signal_name in signal_weights and isinstance(signal_values, pd.Series):
                weight = signal_weights[signal_name]

                # 计算信号与收益的相关性
                signal_corr = {}
                for etf in annual_cov.index:
                    if etf in signal_values.index:
                        correlation = signal_values[etf]
                        signal_corr[etf] = correlation * weight * 0.05  # 调整协方差调整强度

                signal_correlations[signal_name] = signal_corr

        # 应用信号协方差调整
        for i, etf1 in enumerate(annual_cov.index):
            for j, etf2 in enumerate(annual_cov.columns):
                if i != j:
                    # 基于信号相关性调整协方差
                    correlation_adjustment = 0
                    for signal_corr in signal_correlations.values():
                        if etf1 in signal_corr and etf2 in signal_corr:
                            correlation_adjustment += signal_corr[etf1] * signal_corr[etf2]

                    enhanced_cov.iloc[i, j] *= (1 + correlation_adjustment)

        # 确保协方差矩阵正定
        eigenvalues = np.linalg.eigvals(enhanced_cov)
        min_eigenvalue = np.min(eigenvalues)
        if min_eigenvalue <= 0:
            enhanced_cov += np.eye(len(enhanced_cov)) * abs(min_eigenvalue) * 1.1

        return enhanced_cov

    def _optimize_with_enhanced_inputs(self, enhanced_returns: pd.Series,
                                     enhanced_cov: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        使用增强输入进行优化

        Args:
            enhanced_returns: 增强预期收益
            enhanced_cov: 增强协方差矩阵

        Returns:
            (最优权重, 优化指标)
        """
        n = len(enhanced_returns)

        # 定义目标函数：最大化夏普比率
        def negative_sharpe_ratio(weights):
            portfolio_return = np.dot(weights, enhanced_returns.values)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(enhanced.values, weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe_ratio

        # 约束条件
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # 权重和为1
        ]

        # 风险控制约束
        def risk_constraint(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(enhanced_cov.values, weights)))
            return 0.20 - portfolio_vol  # 最大波动率约束

        constraints.append({'type': 'ineq', 'fun': risk_constraint})

        # 集中度约束
        def concentration_constraint(weights):
            max_weight = np.max(weights)
            return 0.40 - max_weight  # 最大单ETF权重限制

        constraints.append({'type': 'ineq', 'fun': concentration_constraint})

        # 边界条件
        bounds = tuple((0, 1) for _ in range(n))

        # 初始猜测
        initial_weights = np.ones(n) / n

        try:
            result = minimize(
                negative_sharpe_ratio,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'ftol': 1e-9, 'disp': False}
            )

            if result.success:
                optimal_weights = result.x
                metrics = self._calculate_enhanced_portfolio_metrics(
                    optimal_weights, enhanced_returns, enhanced_cov
                )
                return optimal_weights, metrics
            else:
                logger.warning(f"增强优化失败: {result.message}")
                return self._fallback_enhanced_optimization(enhanced_returns, enhanced_cov)

        except Exception as e:
            logger.error(f"增强优化异常: {e}")
            return self._fallback_enhanced_optimization(enhanced_returns, enhanced_cov)

    def _calculate_enhanced_portfolio_metrics(self, weights: np.ndarray,
                                            enhanced_returns: pd.Series,
                                            enhanced_cov: pd.DataFrame) -> Dict[str, float]:
        """
        计算增强投资组合指标

        Args:
            weights: 投资组合权重
            enhanced_returns: 增强预期收益
            enhanced_cov: 增强协方差矩阵

        Returns:
            投资组合指标
        """
        # 基础指标
        portfolio_return = np.dot(weights, enhanced_returns.values)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(enhanced_cov.values, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol

        metrics = {
            'portfolio_return': portfolio_return,
            'portfolio_volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio,
            'enhanced_optimization': True
        }

        # 风险指标
        weights_array = np.array(weights)

        # 集中度指标
        hhi = np.sum(weights_array ** 2) * 10000  # 赫芬达尔-赫希曼指数
        metrics['concentration_hhi'] = hhi

        # 有效资产数量
        effective_assets = 1 / np.sum(weights_array ** 2)
        metrics['effective_assets'] = effective_assets

        # 分散化比率
        weighted_vol = np.sum(weights_array * np.sqrt(np.diag(enhanced_cov)))
        diversification_ratio = weighted_vol / portfolio_vol
        metrics['diversification_ratio'] = diversification_ratio

        return metrics

    def _analyze_signal_contributions(self, signals: Dict[str, pd.Series],
                                    signal_weights: Dict[str, float],
                                    optimal_weights: np.ndarray) -> Dict[str, Any]:
        """
        分析信号对优化结果的贡献

        Args:
            signals: 量化信号
            signal_weights: 信号权重
            optimal_weights: 最优权重

        Returns:
            信号贡献分析
        """
        analysis = {}

        # 计算各信号的加权表现
        signal_performance = {}
        for signal_name, signal_values in signals.items():
            if signal_name in signal_weights and isinstance(signal_values, pd.Series):
                weight = signal_weights[signal_name]
                # 计算信号与权重的相关性
                signal_weight_corr = signal_values.corr(pd.Series(optimal_weights, index=signal_values.index))
                signal_performance[signal_name] = {
                    'weight': weight,
                    'correlation_with_weights': signal_weight_corr if not np.isnan(signal_weight_corr) else 0,
                    'signal_strength': signal_values.std()
                }

        analysis['signal_performance'] = signal_performance

        # 计算信号综合评分
        composite_score = sum(
            perf['weight'] * abs(perf['correlation_with_weights']) * perf['signal_strength']
            for perf in signal_performance.values()
        )
        analysis['composite_signal_score'] = composite_score

        # 识别主导信号
        dominant_signal = max(signal_performance.items(),
                            key=lambda x: abs(x[1]['correlation_with_weights']) * x[1]['signal_strength'])
        analysis['dominant_signal'] = dominant_signal[0]

        return analysis

    def _fallback_enhanced_optimization(self, enhanced_returns: pd.Series,
                                      enhanced_cov: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        备用增强优化方法

        Args:
            enhanced_returns: 增强预期收益
            enhanced_cov: 增强协方差矩阵

        Returns:
            (备用权重, 备用指标)
        """
        logger.info("使用备用增强优化方法...")

        n = len(enhanced_returns)

        # 方法1: 等风险贡献组合
        try:
            risk_parity_weights = self._calculate_risk_parity_weights(enhanced_cov)
            metrics = self._calculate_enhanced_portfolio_metrics(
                risk_parity_weights, enhanced_returns, enhanced_cov
            )
            return risk_parity_weights, metrics
        except Exception as e:
            logger.warning(f"风险平价备用方法失败: {e}")

        # 方法2: 等权重组合
        equal_weights = np.ones(n) / n
        metrics = self._calculate_enhanced_portfolio_metrics(
            equal_weights, enhanced_returns, enhanced_cov
        )

        return equal_weights, metrics

    def _calculate_risk_parity_weights(self, cov_matrix: pd.DataFrame) -> np.ndarray:
        """
        计算风险平价权重

        Args:
            cov_matrix: 协方差矩阵

        Returns:
            风险平价权重
        """
        n = cov_matrix.shape[0]

        def risk_budget_objective(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
            marginal_contrib = np.dot(cov_matrix.values, weights) / portfolio_vol
            contrib = weights * marginal_contrib
            target_contrib = 1 / n
            return np.sum((contrib - target_contrib) ** 2)

        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = tuple((0, 1) for _ in range(n))
        initial_weights = np.ones(n) / n

        result = minimize(
            risk_budget_objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return result.x if result.success else initial_weights

    def compare_enhanced_vs_traditional(self, returns: pd.DataFrame,
                                      prices: pd.DataFrame) -> Dict[str, Any]:
        """
        比较增强优化与传统优化的结果

        Args:
            returns: 历史收益率
            prices: 价格数据

        Returns:
            比较结果
        """
        logger.info("开始比较增强优化与传统优化...")

        comparison = {}

        try:
            # 生成增强信号
            signals = self.quant_indicators.generate_signals(returns, prices)

            # 传统优化
            annual_mean_traditional = returns.mean() * self.trading_days
            annual_cov_traditional = returns.cov() * self.trading_days

            traditional_weights, traditional_metrics = self._optimize_with_enhanced_inputs(
                annual_mean_traditional, annual_cov_traditional
            )

            # 增强优化
            if signals:
                enhanced_weights, enhanced_metrics = self.optimize_with_enhanced_signals(
                    returns, prices, signals
                )

                comparison['traditional'] = {
                    'weights': traditional_weights,
                    'metrics': traditional_metrics,
                    'method': 'Traditional Optimization'
                }

                comparison['enhanced'] = {
                    'weights': enhanced_weights,
                    'metrics': enhanced_metrics,
                    'method': 'Enhanced Signal Optimization'
                }

                # 计算改进指标
                sharpe_improvement = enhanced_metrics['sharpe_ratio'] - traditional_metrics['sharpe_ratio']
                comparison['improvement'] = {
                    'sharpe_ratio_improvement': sharpe_improvement,
                    'sharpe_improvement_pct': (sharpe_improvement / traditional_metrics['sharpe_ratio']) * 100 if traditional_metrics['sharpe_ratio'] != 0 else 0,
                    'volatility_change': enhanced_metrics['portfolio_volatility'] - traditional_metrics['portfolio_volatility'],
                    'return_change': enhanced_metrics['portfolio_return'] - traditional_metrics['portfolio_return']
                }

                # 信号分析
                comparison['signal_analysis'] = enhanced_metrics.get('signal_analysis', {})

            logger.info("优化比较完成")

        except Exception as e:
            logger.error(f"优化比较失败: {e}")
            comparison = {'error': str(e)}

        return comparison

    def get_optimization_recommendations(self, comparison: Dict[str, Any]) -> List[str]:
        """
        基于比较结果生成优化建议

        Args:
            comparison: 比较结果

        Returns:
            优化建议列表
        """
        recommendations = []

        if 'error' in comparison:
            recommendations.append("优化过程中出现错误，建议检查数据质量")
            return recommendations

        if 'improvement' in comparison:
            improvement = comparison['improvement']

            # 夏普比率改进建议
            if improvement['sharpe_ratio_improvement'] > 0.1:
                recommendations.append("✅ 增强信号优化显著提升了夏普比率，建议采用")
            elif improvement['sharpe_ratio_improvement'] > 0:
                recommendations.append("✅ 增强信号优化略微提升了夏普比率")
            else:
                recommendations.append("⚠️ 增强信号优化未能提升夏普比率，建议检查信号质量")

            # 风险调整建议
            if improvement['volatility_change'] > 0.01:
                recommendations.append("⚠️ 增强优化增加了投资组合波动率，建议加强风险控制")
            elif improvement['volatility_change'] < -0.01:
                recommendations.append("✅ 增强优化降低了投资组合波动率")

            # 收益提升建议
            if improvement['return_change'] > 0.01:
                recommendations.append("✅ 增强优化提升了预期收益")
            elif improvement['return_change'] < -0.01:
                recommendations.append("⚠️ 增强优化降低了预期收益")

        # 信号分析建议
        if 'signal_analysis' in comparison and 'dominant_signal' in comparison['signal_analysis']:
            dominant = comparison['signal_analysis']['dominant_signal']
            recommendations.append(f"💡 {dominant} 是主导信号，建议重点关注此类指标")

        return recommendations


def get_enhanced_portfolio_optimizer(risk_free_rate: float = 0.02,
                                   trading_days: int = 252) -> EnhancedPortfolioOptimizer:
    """获取增强投资组合优化器实例"""
    return EnhancedPortfolioOptimizer(risk_free_rate, trading_days)