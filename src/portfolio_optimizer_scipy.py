"""
投资组合优化模块（使用scipy替代cvxpy）
实现夏普比率最大化和有效前沿计算
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PortfolioOptimizerScipy:
    """投资组合优化类（使用scipy）"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        初始化优化器
        
        Args:
            risk_free_rate: 无风险利率，默认2%
        """
        self.risk_free_rate = risk_free_rate
    
    def maximize_sharpe_ratio(self, annual_mean: pd.Series, 
                            cov_matrix: pd.DataFrame) -> Tuple[np.ndarray, float]:
        """
        最大化夏普比率
        
        Args:
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
            
        Returns:
            optimal_weights: 最优权重向量
            max_sharpe_ratio: 最大夏普比率
        """
        logger.info("开始夏普比率最大化优化...")
        
        # 验证输入数据
        self._validate_optimization_inputs(annual_mean, cov_matrix)
        
        n = len(annual_mean)
        
        # 定义目标函数：最小化负夏普比率
        def negative_sharpe_ratio(weights):
            portfolio_return = np.dot(weights, annual_mean.values)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe  # 最小化负夏普比率相当于最大化夏普比率
        
        # 约束条件：权重和为1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        
        # 边界条件：权重在0到1之间
        bounds = tuple((0, 1) for _ in range(n))
        
        # 初始猜测：等权重
        initial_weights = np.ones(n) / n
        
        try:
            # 求解优化问题
            result = minimize(
                negative_sharpe_ratio,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'ftol': 1e-9, 'disp': False}
            )
            
            if not result.success:
                raise ValueError(f"优化失败: {result.message}")
            
            optimal_weights = result.x
            portfolio_actual_return = np.dot(optimal_weights, annual_mean.values)
            portfolio_actual_vol = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix.values, optimal_weights)))
            max_sharpe_ratio = (portfolio_actual_return - self.risk_free_rate) / portfolio_actual_vol
            
            # 验证优化结果
            self._validate_optimization_result(optimal_weights, max_sharpe_ratio)
            
            logger.info(f"优化完成，最大夏普比率: {max_sharpe_ratio:.4f}")
            return optimal_weights, max_sharpe_ratio
            
        except Exception as e:
            logger.error(f"优化求解失败: {e}")
            # 尝试使用备用求解器
            return self._solve_with_alternative_method(annual_mean, cov_matrix)
    
    def _validate_optimization_inputs(self, annual_mean: pd.Series, 
                                    cov_matrix: pd.DataFrame) -> None:
        """
        验证优化输入数据
        
        Args:
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
        """
        if len(annual_mean) == 0:
            raise ValueError("收益率向量为空")
        
        if cov_matrix.empty:
            raise ValueError("协方差矩阵为空")
        
        if len(annual_mean) != cov_matrix.shape[0]:
            raise ValueError("收益率向量和协方差矩阵维度不匹配")
        
        # 检查收益率是否合理
        if (annual_mean < -1).any():
            logger.warning("存在异常低的年化收益率")
        
        # 检查协方差矩阵是否为对称矩阵
        if not np.allclose(cov_matrix.values, cov_matrix.values.T):
            logger.warning("协方差矩阵不对称")
    
    def _validate_optimization_result(self, weights: np.ndarray, 
                                    sharpe_ratio: float) -> None:
        """
        验证优化结果
        
        Args:
            weights: 权重向量
            sharpe_ratio: 夏普比率
        """
        if weights is None:
            raise ValueError("优化返回空权重")
        
        # 检查权重和是否为1
        weight_sum = np.sum(weights)
        if not np.isclose(weight_sum, 1.0, atol=1e-6):
            logger.warning(f"权重和不为1: {weight_sum}")
        
        # 检查权重是否在合理范围内
        if (weights < -1e-6).any():
            logger.warning("存在负权重")
        
        # 检查夏普比率是否合理
        if sharpe_ratio is None or np.isnan(sharpe_ratio):
            raise ValueError("夏普比率为NaN")
        
        if sharpe_ratio < -10:
            logger.warning("夏普比率异常低")
    
    def _solve_with_alternative_method(self, annual_mean: pd.Series,
                                     cov_matrix: pd.DataFrame) -> Tuple[np.ndarray, float]:
        """
        使用备用方法求解优化问题
        
        Args:
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
            
        Returns:
            optimal_weights: 最优权重向量
            max_sharpe_ratio: 最大夏普比率
        """
        logger.info("尝试备用优化方法...")
        
        n = len(annual_mean)
        
        # 方法1: 等权重组合
        equal_weights = np.ones(n) / n
        portfolio_return = np.dot(equal_weights, annual_mean.values)
        portfolio_vol = np.sqrt(np.dot(equal_weights.T, np.dot(cov_matrix.values, equal_weights)))
        sharpe_equal = (portfolio_return - self.risk_free_rate) / portfolio_vol
        
        # 方法2: 最大夏普比率组合（解析解，忽略约束）
        try:
            inv_cov = np.linalg.inv(cov_matrix.values)
            ones = np.ones(n)
            w_unconstrained = inv_cov @ (annual_mean.values - self.risk_free_rate)
            w_unconstrained = w_unconstrained / np.sum(w_unconstrained)
            
            # 应用非负约束
            w_unconstrained[w_unconstrained < 0] = 0
            if np.sum(w_unconstrained) > 0:
                w_unconstrained = w_unconstrained / np.sum(w_unconstrained)
            else:
                w_unconstrained = equal_weights
            
            portfolio_return_uncon = np.dot(w_unconstrained, annual_mean.values)
            portfolio_vol_uncon = np.sqrt(np.dot(w_unconstrained.T, np.dot(cov_matrix.values, w_unconstrained)))
            sharpe_uncon = (portfolio_return_uncon - self.risk_free_rate) / portfolio_vol_uncon
            
            # 选择更好的结果
            if sharpe_uncon > sharpe_equal:
                logger.info("备用方法求解成功")
                return w_unconstrained, sharpe_uncon
            else:
                logger.info("使用等权重组合作为备用方案")
                return equal_weights, sharpe_equal
                
        except Exception as e:
            logger.warning(f"备用方法失败，使用等权重组合: {e}")
            return equal_weights, sharpe_equal
    
    def calculate_efficient_frontier(self, annual_mean: pd.Series, 
                                   cov_matrix: pd.DataFrame, 
                                   num_points: int = 50) -> Tuple[List[float], List[float]]:
        """
        计算有效前沿
        
        Args:
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
            num_points: 前沿点数
            
        Returns:
            risks: 风险列表
            returns_list: 收益列表
        """
        logger.info("开始计算有效前沿...")
        
        n = len(annual_mean)
        
        risks = []
        returns_list = []
        
        # 生成目标收益率范围
        min_return = annual_mean.min()
        max_return = annual_mean.max()
        target_returns = np.linspace(min_return, max_return, num_points)
        
        for target in target_returns:
            try:
                # 定义目标函数：最小化风险
                def portfolio_volatility(weights):
                    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
                
                # 约束条件：权重和为1，目标收益率
                constraints = (
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                    {'type': 'eq', 'fun': lambda x: np.dot(x, annual_mean.values) - target}
                )
                
                # 边界条件
                bounds = tuple((0, 1) for _ in range(n))
                
                # 初始猜测
                initial_weights = np.ones(n) / n
                
                # 求解
                result = minimize(
                    portfolio_volatility,
                    initial_weights,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=constraints,
                    options={'ftol': 1e-9, 'disp': False}
                )
                
                if result.success:
                    risks.append(result.fun)
                    returns_list.append(target)
                else:
                    logger.debug(f"目标收益率 {target:.4f} 优化失败")
                    
            except Exception as e:
                logger.debug(f"目标收益率 {target:.4f} 计算失败: {e}")
                continue
        
        logger.info(f"有效前沿计算完成，共 {len(risks)} 个点")
        return risks, returns_list
    
    def get_optimization_summary(self, weights: np.ndarray, 
                               sharpe_ratio: float,
                               annual_mean: pd.Series,
                               cov_matrix: pd.DataFrame) -> Dict[str, Any]:
        """
        获取优化结果摘要
        
        Args:
            weights: 最优权重向量
            sharpe_ratio: 最大夏普比率
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
            
        Returns:
            优化结果摘要字典
        """
        # 计算组合收益和风险
        portfolio_return = np.dot(weights, annual_mean.values)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix.values, weights)))
        
        summary = {
            "optimal_weights": {etf: f"{weight:.4f}" 
                              for etf, weight in zip(annual_mean.index, weights)},
            "portfolio_return": f"{portfolio_return:.4f}",
            "portfolio_volatility": f"{portfolio_vol:.4f}",
            "sharpe_ratio": f"{sharpe_ratio:.4f}",
            "risk_free_rate": f"{self.risk_free_rate:.4f}",
            "weight_sum": f"{np.sum(weights):.6f}"
        }
        
        return summary


def get_portfolio_optimizer_scipy(risk_free_rate: float = 0.02) -> PortfolioOptimizerScipy:
    """获取投资组合优化器实例（使用scipy）"""
    return PortfolioOptimizerScipy(risk_free_rate)