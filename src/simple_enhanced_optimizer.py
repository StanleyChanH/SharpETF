"""
简化增强投资组合优化器
基于量化信号进行简单但有效的投资组合优化
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class SimpleEnhancedOptimizer:
    """简化增强投资组合优化器"""

    def __init__(self, risk_free_rate: float = 0.02, trading_days: int = 252):
        """
        初始化简化增强优化器

        Args:
            risk_free_rate: 无风险利率
            trading_days: 年交易天数
        """
        self.risk_free_rate = risk_free_rate
        self.trading_days = trading_days

    def optimize_with_signals(self, returns: pd.DataFrame,
                            signals: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        基于信号进行投资组合优化

        Args:
            returns: 历史收益率数据
            signals: 量化信号数据

        Returns:
            (最优权重, 优化结果指标)
        """
        logger.info("🚀 开始基于信号的增强优化...")

        try:
            if not signals or 'composite_signal' not in signals:
                # 如果没有信号，使用传统优化
                return self._traditional_optimization(returns)

            # 获取信号调整后的预期收益
            composite_signal = signals['composite_signal']

            # 基础预期收益
            base_expected_returns = returns.mean() * self.trading_days

            # 信号调整：给高信号的ETF更高的预期收益
            signal_adjustment = composite_signal * base_expected_returns.std() * 0.3  # 调整强度
            enhanced_expected_returns = base_expected_returns + signal_adjustment

            # 确保预期收益为正
            enhanced_expected_returns = enhanced_expected_returns.clip(lower=0.01)

            # 协方差矩阵
            cov_matrix = returns.cov() * self.trading_days

            # 执行优化
            optimal_weights, metrics = self._optimize_portfolio(
                enhanced_expected_returns, cov_matrix
            )

            # 添加信号分析
            metrics['signal_analysis'] = self._analyze_signal_weights(
                composite_signal, optimal_weights, returns.columns
            )

            logger.info("✅ 基于信号的增强优化完成")
            return optimal_weights, metrics

        except Exception as e:
            logger.error(f"❌ 增强优化失败: {e}")
            return self._traditional_optimization(returns)

    def _traditional_optimization(self, returns: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        传统夏普比率优化

        Args:
            returns: 历史收益率

        Returns:
            (最优权重, 优化指标)
        """
        expected_returns = returns.mean() * self.trading_days
        cov_matrix = returns.cov() * self.trading_days

        return self._optimize_portfolio(expected_returns, cov_matrix)

    def _optimize_portfolio(self, expected_returns: pd.Series,
                          cov_matrix: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        执行投资组合优化

        Args:
            expected_returns: 预期收益率
            cov_matrix: 协方差矩阵

        Returns:
            (最优权重, 优化指标)
        """
        n = len(expected_returns)

        def negative_sharpe_ratio(weights):
            portfolio_return = np.dot(weights, expected_returns.values)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe_ratio

        # 约束条件
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # 权重和为1
        ]

        # 风险控制
        def risk_constraint(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
            return 0.25 - portfolio_vol  # 最大波动率25%

        constraints.append({'type': 'ineq', 'fun': risk_constraint})

        # 集中度约束
        def concentration_constraint(weights):
            return 0.5 - np.max(weights)  # 最大单个权重50%

        constraints.append({'type': 'ineq', 'fun': concentration_constraint})

        # 边界条件
        bounds = tuple((0, 0.5) for _ in range(n))  # 单个ETF最大50%

        # 初始猜测 - 等权重
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
                metrics = self._calculate_portfolio_metrics(
                    optimal_weights, expected_returns, cov_matrix
                )
                return optimal_weights, metrics
            else:
                # 如果优化失败，使用等权重
                equal_weights = np.ones(n) / n
                metrics = self._calculate_portfolio_metrics(
                    equal_weights, expected_returns, cov_matrix
                )
                return equal_weights, metrics

        except Exception as e:
            logger.error(f"优化过程异常: {e}")
            # 返回等权重
            equal_weights = np.ones(n) / n
            metrics = self._calculate_portfolio_metrics(
                equal_weights, expected_returns, cov_matrix
            )
            return equal_weights, metrics

    def _calculate_portfolio_metrics(self, weights: np.ndarray,
                                   expected_returns: pd.Series,
                                   cov_matrix: pd.DataFrame) -> Dict[str, float]:
        """
        计算投资组合指标

        Args:
            weights: 投资组合权重
            expected_returns: 预期收益率
            cov_matrix: 协方差矩阵

        Returns:
            投资组合指标
        """
        portfolio_return = np.dot(weights, expected_returns.values)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol

        metrics = {
            'portfolio_return': portfolio_return,
            'portfolio_volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio
        }

        # 添加额外指标
        weights_array = np.array(weights)

        # 集中度指标
        hhi = np.sum(weights_array ** 2) * 10000
        metrics['concentration_hhi'] = hhi

        # 有效资产数量
        effective_assets = 1 / np.sum(weights_array ** 2)
        metrics['effective_assets'] = effective_assets

        # 分散化比率
        weighted_vol = np.sum(weights_array * np.sqrt(np.diag(cov_matrix)))
        diversification_ratio = weighted_vol / portfolio_vol
        metrics['diversification_ratio'] = diversification_ratio

        return metrics

    def _analyze_signal_weights(self, signals: pd.Series, weights: np.ndarray,
                              etf_codes: List[str]) -> Dict[str, Any]:
        """
        分析信号与权重的关系

        Args:
            signals: 综合信号
            weights: 最优权重
            etf_codes: ETF代码列表

        Returns:
            信号权重分析
        """
        try:
            # 创建DataFrame便于分析
            analysis_df = pd.DataFrame({
                'signal': signals,
                'weight': weights,
                'etf_code': etf_codes
            })

            # 计算信号与权重的相关性
            correlation = analysis_df['signal'].corr(analysis_df['weight'])

            # 找出高信号高权重的ETF
            high_signal_threshold = signals.quantile(0.75)
            high_weight_threshold = np.percentile(weights, 75)

            top_signal_etfs = analysis_df[analysis_df['signal'] > high_signal_threshold]
            top_weight_etfs = analysis_df[analysis_df['weight'] > high_weight_threshold]

            # 信号一致性分析
            consistent_picks = set(top_signal_etfs['etf_code']) & set(top_weight_etfs['etf_code'])

            return {
                'signal_weight_correlation': correlation if not np.isnan(correlation) else 0,
                'top_signal_etfs': top_signal_etfs['etf_code'].tolist(),
                'top_weight_etfs': top_weight_etfs['etf_code'].tolist(),
                'consistent_picks': list(consistent_picks),
                'signal_effectiveness': 'high' if correlation > 0.3 else 'medium' if correlation > 0.1 else 'low'
            }

        except Exception as e:
            logger.error(f"分析信号权重关系失败: {e}")
            return {'signal_effectiveness': 'unknown'}

    def compare_with_traditional(self, returns: pd.DataFrame,
                              signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        比较增强优化与传统优化

        Args:
            returns: 历史收益率
            signals: 量化信号

        Returns:
            比较结果
        """
        try:
            # 传统优化
            traditional_weights, traditional_metrics = self._traditional_optimization(returns)

            # 增强优化
            enhanced_weights, enhanced_metrics = self.optimize_with_signals(returns, signals)

            # 计算改进指标
            sharpe_improvement = enhanced_metrics['sharpe_ratio'] - traditional_metrics['sharpe_ratio']
            return_improvement = enhanced_metrics['portfolio_return'] - traditional_metrics['portfolio_return']
            volatility_change = enhanced_metrics['portfolio_volatility'] - traditional_metrics['portfolio_volatility']

            comparison = {
                'traditional': {
                    'weights': traditional_weights,
                    'metrics': traditional_metrics
                },
                'enhanced': {
                    'weights': enhanced_weights,
                    'metrics': enhanced_metrics
                },
                'improvement': {
                    'sharpe_ratio_improvement': sharpe_improvement,
                    'sharpe_improvement_pct': (sharpe_improvement / traditional_metrics['sharpe_ratio']) * 100 if traditional_metrics['sharpe_ratio'] != 0 else 0,
                    'return_change': return_improvement,
                    'volatility_change': volatility_change
                }
            }

            return comparison

        except Exception as e:
            logger.error(f"比较优化结果失败: {e}")
            return {}

    def get_optimization_recommendations(self, comparison: Dict[str, Any]) -> List[str]:
        """
        基于比较结果生成优化建议

        Args:
            comparison: 比较结果

        Returns:
            优化建议列表
        """
        recommendations = []

        try:
            if not comparison or 'improvement' not in comparison:
                return ["优化结果比较失败，建议基于基础分析进行投资决策"]

            improvement = comparison['improvement']

            # 夏普比率改进建议
            sharpe_imp = improvement.get('sharpe_ratio_improvement', 0)
            if sharpe_imp > 0.1:
                recommendations.append("✅ 增强优化显著提升了夏普比率，建议采用信号驱动策略")
            elif sharpe_imp > 0.01:
                recommendations.append("📈 增强优化略微提升了夏普比率，可考虑采用")
            elif sharpe_imp < -0.01:
                recommendations.append("⚠️ 增强优化降低了夏普比率，建议使用传统优化")

            # 收益改进建议
            return_imp = improvement.get('return_change', 0)
            if return_imp > 0.02:
                recommendations.append("💰 增强优化提升了预期收益，建议重点关注")
            elif return_imp < -0.02:
                recommendations.append("📉 增强优化降低了预期收益，需要权衡风险收益")

            # 风险变化建议
            vol_change = improvement.get('volatility_change', 0)
            if vol_change > 0.02:
                recommendations.append("⚠️ 增强优化增加了投资组合风险，需要加强风险控制")
            elif vol_change < -0.02:
                recommendations.append("🛡️ 增强优化降低了投资组合风险，有助于风险控制")

            # 综合建议
            if sharpe_imp > 0 and return_imp > 0:
                recommendations.append("🎯 增强优化在风险调整收益方面表现优秀，建议优先考虑")
            elif sharpe_imp > 0 and vol_change < 0:
                recommendations.append("🏆 增强优化实现了更好的风险调整收益，是理想的选择")

        except Exception as e:
            logger.error(f"生成优化建议失败: {e}")
            recommendations = ["建议生成失败，请基于专业判断进行决策"]

        return recommendations


def get_simple_enhanced_optimizer(risk_free_rate: float = 0.02,
                                 trading_days: int = 252) -> SimpleEnhancedOptimizer:
    """获取简化增强优化器实例"""
    return SimpleEnhancedOptimizer(risk_free_rate, trading_days)