"""
数据处理模块
计算收益率、年化统计量和数据对齐
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """数据处理类"""
    
    def __init__(self, trading_days: int = 252):
        """
        初始化数据处理器
        
        Args:
            trading_days: 年交易天数，默认252
        """
        self.trading_days = trading_days
    
    def process_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
        """
        处理原始数据，计算收益率和统计量
        
        Args:
            data: 原始数据DataFrame，包含trade_date和各ETF价格列
            
        Returns:
            returns: 日收益率DataFrame
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
        """
        logger.info("🔄 开始处理数据...")
        
        # 验证输入数据
        self._validate_input_data(data)
        
        # 提取价格数据（排除trade_date列）
        price_data = data.iloc[:, 1:]
        
        # 计算日收益率
        returns = self.calculate_returns(price_data)
        
        # 计算年化统计量
        annual_mean, cov_matrix = self.calculate_annual_stats(returns)
        
        logger.info("✅ 数据处理完成")
        return returns, annual_mean, cov_matrix
    
    def _validate_input_data(self, data: pd.DataFrame) -> None:
        """
        验证输入数据
        
        Args:
            data: 输入数据DataFrame
        """
        if data.empty:
            raise ValueError("输入数据为空")
        
        if len(data.columns) < 2:
            raise ValueError("数据列数不足，至少需要trade_date和一列价格数据")
        
        # 检查trade_date列是否存在
        if 'trade_date' not in data.columns:
            raise ValueError("数据中缺少trade_date列")
        
        # 检查价格数据是否有效
        price_columns = [col for col in data.columns if col != 'trade_date']
        for col in price_columns:
            if data[col].isnull().all():
                raise ValueError(f"价格列 {col} 全为缺失值")
            
            if (data[col] <= 0).any():
                logger.warning(f"⚠️ 价格列 {col} 包含非正值")
    
    def calculate_returns(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """
        计算日收益率
        
        Args:
            price_data: 价格数据DataFrame
            
        Returns:
            日收益率DataFrame
        """
        try:
            # 使用pct_change计算百分比变化
            returns = price_data.pct_change()
            
            # 删除第一行（NaN）
            returns = returns.dropna()
            
            # 检查收益率数据
            self._validate_returns(returns)
            
            logger.info(f"📈 收益率计算完成，共 {len(returns)} 个交易日")
            return returns
            
        except Exception as e:
            logger.error(f"❌ 收益率计算失败: {e}")
            raise
    
    def _validate_returns(self, returns: pd.DataFrame) -> None:
        """
        验证收益率数据
        
        Args:
            returns: 收益率DataFrame
        """
        if returns.empty:
            raise ValueError("收益率数据为空")
        
        # 检查异常值
        for col in returns.columns:
            col_returns = returns[col]
            
            # 检查标准差
            std_dev = col_returns.std()
            if std_dev == 0:
                logger.warning(f"⚠️ {col} 收益率标准差为0")
            
            # 检查极端值
            extreme_threshold = 0.5  # 50%的单日涨跌幅
            extreme_count = (abs(col_returns) > extreme_threshold).sum()
            if extreme_count > 0:
                logger.warning(f"⚠️ {col} 有 {extreme_count} 个极端收益率（>50%）")
    
    def calculate_annual_stats(self, returns: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        """
        计算年化统计量
        
        Args:
            returns: 日收益率DataFrame
            
        Returns:
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
        """
        try:
            # 计算年化收益率
            annual_mean = returns.mean() * self.trading_days
            
            # 计算年化协方差矩阵
            cov_matrix = returns.cov() * self.trading_days
            
            # 验证协方差矩阵
            self._validate_cov_matrix(cov_matrix)
            
            logger.info("📊 年化统计量计算完成")
            return annual_mean, cov_matrix
            
        except Exception as e:
            logger.error(f"❌ 年化统计量计算失败: {e}")
            raise
    
    def _validate_cov_matrix(self, cov_matrix: pd.DataFrame) -> None:
        """
        验证协方差矩阵
        
        Args:
            cov_matrix: 协方差矩阵
        """
        # 检查是否为对称矩阵
        if not cov_matrix.equals(cov_matrix.T):
            logger.warning("⚠️ 协方差矩阵不对称")
        
        # 检查对角线元素（方差）是否为正
        variances = np.diag(cov_matrix)
        if (variances <= 0).any():
            logger.warning("⚠️ 协方差矩阵包含非正方差")
        
        # 检查矩阵是否正定
        try:
            np.linalg.cholesky(cov_matrix)
        except np.linalg.LinAlgError:
            logger.warning("⚠️ 协方差矩阵不是正定矩阵，可能影响优化结果")
    
    def align_data(self, data_frames: list) -> pd.DataFrame:
        """
        对齐多ETF数据（备用方法）
        
        Args:
            data_frames: ETF数据列表
            
        Returns:
            对齐后的DataFrame
        """
        if not data_frames:
            raise ValueError("没有数据可对齐")
        
        # 使用第一个DataFrame作为基础
        aligned_data = data_frames[0]
        
        for df in data_frames[1:]:
            aligned_data = pd.merge(
                aligned_data, 
                df, 
                on='trade_date', 
                how='inner'
            )
        
        return aligned_data
    
    def get_data_summary(self, returns: pd.DataFrame, annual_mean: pd.Series, 
                        cov_matrix: pd.DataFrame) -> Dict[str, Any]:
        """
        获取数据摘要信息
        
        Args:
            returns: 日收益率DataFrame
            annual_mean: 年化收益率向量
            cov_matrix: 年化协方差矩阵
            
        Returns:
            数据摘要字典
        """
        summary = {
            "period": f"{len(returns)} 个交易日",
            "start_date": returns.index.min().strftime('%Y-%m-%d') if hasattr(returns.index, 'strftime') else "N/A",
            "end_date": returns.index.max().strftime('%Y-%m-%d') if hasattr(returns.index, 'strftime') else "N/A",
            "etf_count": len(annual_mean),
            "annual_returns": {etf: f"{ret:.2%}" for etf, ret in annual_mean.items()},
            "volatilities": {etf: f"{np.sqrt(cov_matrix.loc[etf, etf]):.2%}" 
                           for etf in annual_mean.index}
        }
        
        return summary


def get_data_processor(trading_days: int = 252) -> DataProcessor:
    """获取数据处理器实例"""
    return DataProcessor(trading_days)