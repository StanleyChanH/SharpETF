"""
投资组合评估模块
计算各项金融评估指标
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class PortfolioEvaluator:
    """投资组合评估类"""
    
    def __init__(self, trading_days: int = 252, risk_free_rate: float = 0.02):
        """
        初始化评估器
        
        Args:
            trading_days: 年交易天数，默认252
            risk_free_rate: 无风险利率，默认2%
        """
        self.trading_days = trading_days
        self.risk_free_rate = risk_free_rate
    
    def calculate_portfolio_metrics(self, portfolio_returns: pd.Series) -> Dict[str, float]:
        """
        计算投资组合评估指标
        
        Args:
            portfolio_returns: 投资组合日收益率序列
            
        Returns:
            评估指标字典
        """
        logger.info("📊 开始计算投资组合评估指标...")
        
        # 验证输入数据
        self._validate_returns(portfolio_returns)
        
        metrics = {}
        
        try:
            # 1. 年化收益率
            metrics['annual_return'] = self._calculate_annual_return(portfolio_returns)
            
            # 2. 年化波动率
            metrics['annual_volatility'] = self._calculate_annual_volatility(portfolio_returns)
            
            # 3. 夏普比率
            metrics['sharpe_ratio'] = self._calculate_sharpe_ratio(
                metrics['annual_return'], 
                metrics['annual_volatility']
            )
            
            # 4. 最大回撤
            metrics['max_drawdown'] = self._calculate_max_drawdown(portfolio_returns)
            
            # 5. Calmar比率
            metrics['calmar_ratio'] = self._calculate_calmar_ratio(
                metrics['annual_return'], 
                metrics['max_drawdown']
            )
            
            # 6. 索提诺比率
            metrics['sortino_ratio'] = self._calculate_sortino_ratio(portfolio_returns)
            
            # 7. 偏度和峰度
            metrics['skewness'], metrics['kurtosis'] = self._calculate_skewness_kurtosis(portfolio_returns)
            
            logger.info("✅ 评估指标计算完成")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ 评估指标计算失败: {e}")
            raise
    
    def _validate_returns(self, returns: pd.Series) -> None:
        """
        验证收益率数据
        
        Args:
            returns: 收益率序列
        """
        if returns.empty:
            raise ValueError("收益率数据为空")
        
        if len(returns) < 10:
            logger.warning("⚠️ 收益率数据量较少，可能影响指标准确性")
        
        # 检查收益率是否包含异常值
        if (abs(returns) > 1).any():
            logger.warning("⚠️ 收益率数据包含极端值（>100%）")
    
    def _calculate_annual_return(self, returns: pd.Series) -> float:
        """
        计算年化收益率
        
        Args:
            returns: 日收益率序列
            
        Returns:
            年化收益率
        """
        # 使用几何平均计算年化收益率
        cumulative_return = (1 + returns).prod() - 1
        annual_return = (1 + cumulative_return) ** (self.trading_days / len(returns)) - 1
        
        return annual_return
    
    def _calculate_annual_volatility(self, returns: pd.Series) -> float:
        """
        计算年化波动率
        
        Args:
            returns: 日收益率序列
            
        Returns:
            年化波动率
        """
        return returns.std() * np.sqrt(self.trading_days)
    
    def _calculate_sharpe_ratio(self, annual_return: float, annual_volatility: float) -> float:
        """
        计算夏普比率
        
        Args:
            annual_return: 年化收益率
            annual_volatility: 年化波动率
            
        Returns:
            夏普比率
        """
        if annual_volatility == 0:
            return float('inf') if annual_return > self.risk_free_rate else float('-inf')
        
        return (annual_return - self.risk_free_rate) / annual_volatility
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """
        计算最大回撤
        
        Args:
            returns: 日收益率序列
            
        Returns:
            最大回撤（负值）
        """
        # 计算累计收益
        cumulative_returns = (1 + returns).cumprod()
        
        # 计算运行最大值
        running_max = cumulative_returns.cummax()
        
        # 计算回撤
        drawdown = (cumulative_returns - running_max) / running_max
        
        # 最大回撤
        max_drawdown = drawdown.min()
        
        return max_drawdown
    
    def _calculate_calmar_ratio(self, annual_return: float, max_drawdown: float) -> float:
        """
        计算Calmar比率
        
        Args:
            annual_return: 年化收益率
            max_drawdown: 最大回撤
            
        Returns:
            Calmar比率
        """
        if max_drawdown == 0:
            return float('inf') if annual_return > 0 else float('-inf')
        
        return annual_return / abs(max_drawdown)
    
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """
        计算索提诺比率（只考虑下行风险）
        
        Args:
            returns: 日收益率序列
            
        Returns:
            索提诺比率
        """
        # 计算下行偏差（只考虑负收益率）
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf')
        
        downside_volatility = downside_returns.std() * np.sqrt(self.trading_days)
        
        if downside_volatility == 0:
            return float('inf')
        
        annual_return = self._calculate_annual_return(returns)
        sortino_ratio = (annual_return - self.risk_free_rate) / downside_volatility
        
        return sortino_ratio
    
    def _calculate_skewness_kurtosis(self, returns: pd.Series) -> Tuple[float, float]:
        """
        计算偏度和峰度
        
        Args:
            returns: 日收益率序列
            
        Returns:
            (偏度, 峰度)
        """
        skewness = returns.skew()
        kurtosis = returns.kurtosis()
        
        return skewness, kurtosis
    
    def calculate_individual_etf_metrics(self, returns: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        计算各ETF的评估指标
        
        Args:
            returns: 各ETF日收益率DataFrame
            
        Returns:
            各ETF评估指标字典
        """
        etf_metrics = {}
        
        for etf in returns.columns:
            try:
                etf_returns = returns[etf]
                metrics = self.calculate_portfolio_metrics(etf_returns)
                etf_metrics[etf] = metrics
            except Exception as e:
                logger.warning(f"计算 {etf} 指标失败: {e}")
                etf_metrics[etf] = {}
        
        return etf_metrics
    
    def get_evaluation_summary(self, metrics: Dict[str, float], 
                             optimal_weights: np.ndarray,
                             etf_codes: list) -> Dict[str, Any]:
        """
        获取评估结果摘要
        
        Args:
            metrics: 评估指标字典
            optimal_weights: 最优权重向量
            etf_codes: ETF代码列表
            
        Returns:
            评估结果摘要字典
        """
        summary = {
            "performance_metrics": {
                "年化收益率": f"{metrics.get('annual_return', 0):.2%}",
                "年化波动率": f"{metrics.get('annual_volatility', 0):.2%}",
                "夏普比率": f"{metrics.get('sharpe_ratio', 0):.4f}",
                "最大回撤": f"{metrics.get('max_drawdown', 0):.2%}",
                "Calmar比率": f"{metrics.get('calmar_ratio', 0):.4f}",
                "索提诺比率": f"{metrics.get('sortino_ratio', 0):.4f}",
                "偏度": f"{metrics.get('skewness', 0):.4f}",
                "峰度": f"{metrics.get('kurtosis', 0):.4f}"
            },
            "portfolio_weights": {
                etf: f"{weight:.2%}" 
                for etf, weight in zip(etf_codes, optimal_weights)
            },
            "risk_free_rate": f"{self.risk_free_rate:.2%}",
            "trading_days": self.trading_days
        }
        
        return summary
    
    def print_evaluation_report(self, metrics: Dict[str, float], 
                              optimal_weights: np.ndarray,
                              etf_codes: list) -> None:
        """
        打印评估报告
        
        Args:
            metrics: 评估指标字典
            optimal_weights: 最优权重向量
            etf_codes: ETF代码列表
        """
        print("\n" + "="*50)
        print("📊 投资组合评估报告")
        print("="*50)
        
        print(f"\n🎯 绩效指标:")
        print(f"{'指标':<15} {'值':<15} {'说明':<20}")
        print("-" * 50)
        print(f"{'年化收益率':<15} {metrics.get('annual_return', 0):.2%} {'越高越好':<20}")
        print(f"{'年化波动率':<15} {metrics.get('annual_volatility', 0):.2%} {'越低越好':<20}")
        print(f"{'夏普比率':<15} {metrics.get('sharpe_ratio', 0):.4f} {'越高越好':<20}")
        print(f"{'最大回撤':<15} {metrics.get('max_drawdown', 0):.2%} {'越小越好':<20}")
        print(f"{'Calmar比率':<15} {metrics.get('calmar_ratio', 0):.4f} {'越高越好':<20}")
        print(f"{'索提诺比率':<15} {metrics.get('sortino_ratio', 0):.4f} {'越高越好':<20}")
        
        print(f"\n📈 分布特征:")
        print(f"{'偏度':<15} {metrics.get('skewness', 0):.4f} {'>0右偏, <0左偏':<20}")
        print(f"{'峰度':<15} {metrics.get('kurtosis', 0):.4f} {'>3尖峰, <3低峰':<20}")
        
        print(f"\n⚖️ 最优权重分配:")
        for etf, weight in zip(etf_codes, optimal_weights):
            print(f"  {etf}: {weight:.2%}")
        
        print(f"\n📅 参数设置:")
        print(f"  无风险利率: {self.risk_free_rate:.2%}")
        print(f"  年交易天数: {self.trading_days}")
        print("="*50)


def get_portfolio_evaluator(trading_days: int = 252, risk_free_rate: float = 0.02) -> PortfolioEvaluator:
    """获取投资组合评估器实例"""
    return PortfolioEvaluator(trading_days, risk_free_rate)