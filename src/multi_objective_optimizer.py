"""
多目标投资组合优化器
支持夏普比率、风险控制、收益稳定性等多个目标
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional, Any, Callable
import logging

logger = logging.getLogger(__name__)


class MultiObjectiveOptimizer:
    """多目标投资组合优化器"""

    def __init__(self, risk_free_rate: float = 0.02, trading_days: int = 252):
        """
        初始化多目标优化器

        Args:
            risk_free_rate: 无风险利率
            trading_days: 年交易天数
        """
        self.risk_free_rate = risk_free_rate
        self.trading_days = trading_days

    def maximize_sharpe_with_risk_constraint(self, annual_mean: pd.Series,
                                           cov_matrix: pd.DataFrame,
                                           max_volatility: float = 0.15,
                                           max_drawdown: float = 0.20) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        在风险约束下最大化夏普比率

        Args:
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
            max_volatility: 最大允许波动率
            max_drawdown: 最大允许回撤

        Returns:
            (最优权重, 优化结果指标)
        """
        n = len(annual_mean)

        def objective_function(weights):
            portfolio_return = np.dot(weights, annual_mean.values)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe_ratio  # 最小化负夏普比率

        # 约束条件
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # 权重和为1
            {'type': 'ineq', 'fun': lambda x: max_volatility -
             np.sqrt(np.dot(x.T, np.dot(cov_matrix.values, x)))}  # 波动率约束
        ]

        # 边界条件
        bounds = tuple((0, 1) for _ in range(n))

        # 初始猜测
        initial_weights = np.ones(n) / n

        try:
            result = minimize(
                objective_function,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'ftol': 1e-9, 'disp': False}
            )

            if result.success:
                optimal_weights = result.x
                metrics = self._calculate_portfolio_metrics(optimal_weights, annual_mean, cov_matrix)
                return optimal_weights, metrics
            else:
                logger.warning(f"风险约束优化失败: {result.message}")
                return self._fallback_optimization(annual_mean, cov_matrix)

        except Exception as e:
            logger.error(f"多目标优化失败: {e}")
            return self._fallback_optimization(annual_mean, cov_matrix)

    def optimize_for_stable_returns(self, annual_mean: pd.Series,
                                  cov_matrix: pd.DataFrame,
                                  returns: pd.DataFrame,
                                  stability_weight: float = 0.3) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        优化收益稳定性

        Args:
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
            returns: 历史收益率数据
            stability_weight: 稳定性权重（0-1）

        Returns:
            (最优权重, 优化结果指标)
        """
        n = len(annual_mean)

        # 计算收益稳定性指标（负的收益标准差）
        return_stability = -returns.std().values

        def objective_function(weights):
            # 夏普比率部分
            portfolio_return = np.dot(weights, annual_mean.values)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
            sharpe_component = (portfolio_return - self.risk_free_rate) / portfolio_vol

            # 稳定性部分
            stability_component = np.dot(weights, return_stability)

            # 加权组合目标
            combined_objective = stability_weight * stability_component + (1 - stability_weight) * sharpe_component

            return -combined_objective

        # 约束条件
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]

        # 边界条件
        bounds = tuple((0, 1) for _ in range(n))

        # 初始猜测
        initial_weights = np.ones(n) / n

        try:
            result = minimize(
                objective_function,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'ftol': 1e-9, 'disp': False}
            )

            if result.success:
                optimal_weights = result.x
                metrics = self._calculate_portfolio_metrics(optimal_weights, annual_mean, cov_matrix)
                return optimal_weights, metrics
            else:
                logger.warning(f"稳定性优化失败: {result.message}")
                return self._fallback_optimization(annual_mean, cov_matrix)

        except Exception as e:
            logger.error(f"稳定性优化失败: {e}")
            return self._fallback_optimization(annual_mean, cov_matrix)

    def risk_parity_optimization(self, annual_mean: pd.Series,
                               cov_matrix: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        风险平价优化

        Args:
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵

        Returns:
            (最优权重, 优化结果指标)
        """
        n = len(annual_mean)

        def risk_budget_objective(weights):
            """风险贡献度差异最小化"""
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))

            # 计算每个资产的风险贡献
            marginal_contrib = np.dot(cov_matrix.values, weights) / portfolio_vol
            contrib = weights * marginal_contrib

            # 目标是让所有资产的风险贡献相等
            target_contrib = 1 / n
            risk_diff = contrib - target_contrib

            return np.sum(risk_diff ** 2)

        # 约束条件
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]

        # 边界条件
        bounds = tuple((0, 1) for _ in range(n))

        # 初始猜测
        initial_weights = np.ones(n) / n

        try:
            result = minimize(
                risk_budget_objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'ftol': 1e-9, 'disp': False}
            )

            if result.success:
                optimal_weights = result.x
                metrics = self._calculate_portfolio_metrics(optimal_weights, annual_mean, cov_matrix)
                return optimal_weights, metrics
            else:
                logger.warning(f"风险平价优化失败: {result.message}")
                return self._fallback_optimization(annual_mean, cov_matrix)

        except Exception as e:
            logger.error(f"风险平价优化失败: {e}")
            return self._fallback_optimization(annual_mean, cov_matrix)

    def equal_risk_contribution_with_return_boost(self, annual_mean: pd.Series,
                                                cov_matrix: pd.DataFrame,
                                                return_boost_factor: float = 0.1) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        带收益增强的等风险贡献优化

        Args:
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
            return_boost_factor: 收益增强因子

        Returns:
            (最优权重, 优化结果指标)
        """
        n = len(annual_mean)

        def objective_function(weights):
            # 风险平价部分
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
            marginal_contrib = np.dot(cov_matrix.values, weights) / portfolio_vol
            contrib = weights * marginal_contrib
            target_contrib = 1 / n
            risk_diff = contrib - target_contrib
            risk_objective = np.sum(risk_diff ** 2)

            # 收益增强部分
            portfolio_return = np.dot(weights, annual_mean.values)
            return_objective = -portfolio_return * return_boost_factor

            # 组合目标
            return risk_objective + return_objective

        # 约束条件
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]

        # 边界条件
        bounds = tuple((0, 1) for _ in range(n))

        # 初始猜测
        initial_weights = np.ones(n) / n

        try:
            result = minimize(
                objective_function,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'ftol': 1e-9, 'disp': False}
            )

            if result.success:
                optimal_weights = result.x
                metrics = self._calculate_portfolio_metrics(optimal_weights, annual_mean, cov_matrix)
                return optimal_weights, metrics
            else:
                logger.warning(f"增强风险平价优化失败: {result.message}")
                return self._fallback_optimization(annual_mean, cov_matrix)

        except Exception as e:
            logger.error(f"增强风险平价优化失败: {e}")
            return self._fallback_optimization(annual_mean, cov_matrix)

    def hierarchical_risk_parity(self, annual_mean: pd.Series,
                                cov_matrix: pd.DataFrame,
                                correlation_threshold: float = 0.5) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        分层风险平价优化

        Args:
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
            correlation_threshold: 相关性阈值

        Returns:
            (最优权重, 优化结果指标)
        """
        n = len(annual_mean)
        correlation_matrix = cov_matrix.corr()

        # 构建分层结构
        clusters = self._build_hierarchical_clusters(correlation_matrix, correlation_threshold)

        # 为每个聚类分配风险预算
        cluster_weights = np.ones(len(clusters)) / len(clusters)

        # 在每个聚类内部分配权重
        optimal_weights = np.zeros(n)

        for i, cluster in enumerate(clusters):
            cluster_indices = list(cluster)
            cluster_size = len(cluster_indices)

            if cluster_size == 1:
                optimal_weights[cluster_indices[0]] = cluster_weights[i]
            else:
                # 在聚类内部进行风险平价
                cluster_cov = cov_matrix.iloc[cluster_indices, cluster_indices]
                cluster_weights_internal = self._intra_cluster_risk_parity(cluster_cov)
                optimal_weights[cluster_indices] = cluster_weights[i] * cluster_weights_internal

        metrics = self._calculate_portfolio_metrics(optimal_weights, annual_mean, cov_matrix)
        return optimal_weights, metrics

    def _build_hierarchical_clusters(self, correlation_matrix: pd.DataFrame,
                                   threshold: float) -> List[set]:
        """构建分层聚类"""
        n = correlation_matrix.shape[0]
        clusters = [{i} for i in range(n)]

        changed = True
        while changed:
            changed = False
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    if self._should_merge_clusters(clusters[i], clusters[j],
                                                 correlation_matrix, threshold):
                        clusters[i].update(clusters[j])
                        clusters.pop(j)
                        changed = True
                        break
                if changed:
                    break

        return clusters

    def _should_merge_clusters(self, cluster1: set, cluster2: set,
                             correlation_matrix: pd.DataFrame,
                             threshold: float) -> bool:
        """判断是否应该合并聚类"""
        max_correlation = 0
        for i in cluster1:
            for j in cluster2:
                if correlation_matrix.iloc[i, j] > max_correlation:
                    max_correlation = correlation_matrix.iloc[i, j]
        return max_correlation > threshold

    def _intra_cluster_risk_parity(self, cov_matrix: pd.DataFrame) -> np.ndarray:
        """聚类内部风险平价"""
        n = cov_matrix.shape[0]

        def objective_function(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
            marginal_contrib = np.dot(cov_matrix.values, weights) / portfolio_vol
            contrib = weights * marginal_contrib
            target_contrib = 1 / n
            return np.sum((contrib - target_contrib) ** 2)

        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = tuple((0, 1) for _ in range(n))
        initial_weights = np.ones(n) / n

        result = minimize(
            objective_function,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return result.x if result.success else initial_weights

    def _calculate_portfolio_metrics(self, weights: np.ndarray,
                                   annual_mean: pd.Series,
                                   cov_matrix: pd.DataFrame) -> Dict[str, float]:
        """计算投资组合指标"""
        portfolio_return = np.dot(weights, annual_mean.values)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol

        return {
            'portfolio_return': portfolio_return,
            'portfolio_volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio,
            'diversification_ratio': self._calculate_diversification_ratio(weights, cov_matrix)
        }

    def _calculate_diversification_ratio(self, weights: np.ndarray,
                                       cov_matrix: pd.DataFrame) -> float:
        """计算分散化比率"""
        weighted_vol = np.sum(weights * np.sqrt(np.diag(cov_matrix)))
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
        return weighted_vol / portfolio_vol

    def _fallback_optimization(self, annual_mean: pd.Series,
                              cov_matrix: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, float]]:
        """备用优化方法（等权重）"""
        n = len(annual_mean)
        equal_weights = np.ones(n) / n
        metrics = self._calculate_portfolio_metrics(equal_weights, annual_mean, cov_matrix)
        return equal_weights, metrics

    def compare_optimization_methods(self, annual_mean: pd.Series,
                                    cov_matrix: pd.DataFrame,
                                    returns: Optional[pd.DataFrame] = None) -> Dict[str, Dict[str, Any]]:
        """
        比较不同优化方法的结果

        Args:
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
            returns: 历史收益率数据

        Returns:
            各种优化方法的比较结果
        """
        methods = {}

        # 1. 最大夏普比率
        try:
            weights_sharpe, metrics_sharpe = self.maximize_sharpe_with_risk_constraint(
                annual_mean, cov_matrix
            )
            methods['max_sharpe'] = {
                'weights': weights_sharpe,
                'metrics': metrics_sharpe,
                'method': 'Maximum Sharpe Ratio'
            }
        except Exception as e:
            logger.error(f"最大夏普比率优化失败: {e}")

        # 2. 稳定收益优化
        if returns is not None:
            try:
                weights_stable, metrics_stable = self.optimize_for_stable_returns(
                    annual_mean, cov_matrix, returns
                )
                methods['stable_returns'] = {
                    'weights': weights_stable,
                    'metrics': metrics_stable,
                    'method': 'Stable Returns Optimization'
                }
            except Exception as e:
                logger.error(f"稳定收益优化失败: {e}")

        # 3. 风险平价
        try:
            weights_risk_parity, metrics_risk_parity = self.risk_parity_optimization(
                annual_mean, cov_matrix
            )
            methods['risk_parity'] = {
                'weights': weights_risk_parity,
                'metrics': metrics_risk_parity,
                'method': 'Risk Parity'
            }
        except Exception as e:
            logger.error(f"风险平价优化失败: {e}")

        # 4. 分层风险平价
        try:
            weights_hrp, metrics_hrp = self.hierarchical_risk_parity(
                annual_mean, cov_matrix
            )
            methods['hierarchical_risk_parity'] = {
                'weights': weights_hrp,
                'metrics': metrics_hrp,
                'method': 'Hierarchical Risk Parity'
            }
        except Exception as e:
            logger.error(f"分层风险平价优化失败: {e}")

        return methods


def get_multi_objective_optimizer(risk_free_rate: float = 0.02,
                                trading_days: int = 252) -> MultiObjectiveOptimizer:
    """获取多目标优化器实例"""
    return MultiObjectiveOptimizer(risk_free_rate, trading_days)