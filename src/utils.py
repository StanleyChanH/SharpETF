"""
工具模块
包含通用工具函数和日志配置
"""

import logging
import sys
import os
from typing import Any, Dict
import json
import pandas as pd
import numpy as np
from datetime import datetime


def setup_logging(level: str = "INFO") -> None:
    """
    设置日志配置
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
    """
    log_level = getattr(logging, level.upper())
    
    # 配置日志格式
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('etf_optimizer.log', encoding='utf-8')
        ]
    )


def save_results(results: Dict[str, Any], filename: str = "optimization_results.json") -> None:
    """
    保存优化结果到JSON文件
    
    Args:
        results: 结果字典
        filename: 文件名
    """
    try:
        # 确保输出目录存在
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        # 处理numpy数组和pandas对象，使其可序列化
        def convert_to_serializable(obj: Any) -> Any:
            if isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.Series):
                return obj.to_dict()
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict()
            elif isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return obj
        
        # 转换所有可序列化对象
        serializable_results = {}
        for key, value in results.items():
            serializable_results[key] = convert_to_serializable(value)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=4, ensure_ascii=False)
        
        logging.info(f"结果已保存到: {filepath}")
        
    except Exception as e:
        logging.error(f"❌ 保存结果失败: {e}")


def print_welcome_banner() -> None:
    """打印欢迎横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              ETF夏普比率最优组合研究系统                     ║
    ║                                                              ║
    ║       基于Tushare API的量化投资组合优化工具                 ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    📋 系统功能:
    • 多ETF数据获取 (fund_daily接口)
    • 夏普比率最大化优化
    • 有效前沿计算
    • 投资组合绩效评估
    • 专业可视化图表生成
    
    ⚠️  重要提示:
    • 需要Tushare Pro账号和2000+积分
    • 请在config.json中配置您的Tushare Token
    • 支持环境变量 TUSHARE_TOKEN
    
    """
    print(banner)


def print_summary_table(data: Dict[str, Any]) -> None:
    """
    打印摘要表格
    
    Args:
        data: 摘要数据字典
    """
    print("\n" + "="*60)
    print("📊 分析摘要")
    print("="*60)
    
    for category, items in data.items():
        print(f"\n{category}:")
        print("-" * 40)
        for key, value in items.items():
            print(f"  {key:<20} {value}")
    
    print("="*60)


def format_percentage(value: float) -> str:
    """
    格式化百分比
    
    Args:
        value: 数值
        
    Returns:
        格式化后的百分比字符串
    """
    return f"{value:.2%}"


def format_float(value: float, decimals: int = 4) -> str:
    """
    格式化浮点数
    
    Args:
        value: 数值
        decimals: 小数位数
        
    Returns:
        格式化后的字符串
    """
    return f"{value:.{decimals}f}"


def validate_date_format(date_str: str) -> bool:
    """
    验证日期格式 (YYYYMMDD)
    
    Args:
        date_str: 日期字符串
        
    Returns:
        是否有效
    """
    if len(date_str) != 8:
        return False
    
    try:
        datetime.strptime(date_str, '%Y%m%d')
        return True
    except ValueError:
        return False


def calculate_correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """
    计算相关系数矩阵
    
    Args:
        returns: 收益率DataFrame
        
    Returns:
        相关系数矩阵
    """
    return returns.corr()


def calculate_rolling_statistics(returns: pd.Series, window: int = 252) -> pd.DataFrame:
    """
    计算滚动统计量
    
    Args:
        returns: 收益率序列
        window: 滚动窗口大小
        
    Returns:
        滚动统计量DataFrame
    """
    rolling_stats = pd.DataFrame()
    
    # 滚动年化收益率
    rolling_stats['rolling_return'] = returns.rolling(window).mean() * 252
    
    # 滚动年化波动率
    rolling_stats['rolling_volatility'] = returns.rolling(window).std() * np.sqrt(252)
    
    # 滚动夏普比率
    rolling_stats['rolling_sharpe'] = (
        (rolling_stats['rolling_return'] - 0.02) / rolling_stats['rolling_volatility']
    )
    
    return rolling_stats.dropna()


def check_memory_usage(data: pd.DataFrame) -> Dict[str, Any]:
    """
    检查内存使用情况
    
    Args:
        data: 数据DataFrame
        
    Returns:
        内存使用信息字典
    """
    memory_info = {
        "total_memory_mb": data.memory_usage(deep=True).sum() / 1024**2,
        "row_count": len(data),
        "column_count": len(data.columns),
        "data_types": data.dtypes.to_dict()
    }
    
    return memory_info


def create_output_directory() -> str:
    """
    创建输出目录
    
    Returns:
        输出目录路径
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"outputs/analysis_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir


def handle_exception(func):
    """
    异常处理装饰器
    
    Args:
        func: 被装饰的函数
        
    Returns:
        包装后的函数
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"函数 {func.__name__} 执行失败: {e}")
            raise
    
    return wrapper


class Timer:
    """计时器类"""
    
    def __init__(self, name: str = "操作"):
        """
        初始化计时器
        
        Args:
            name: 操作名称
        """
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        """进入上下文管理器"""
        self.start_time = datetime.now()
        logging.info(f"开始 {self.name}...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            logging.info(f"{self.name} 完成，耗时: {duration:.2f} 秒")
        else:
            logging.error(f"❌ {self.name} 失败，耗时: {duration:.2f} 秒")
    
    def elapsed_time(self) -> float:
        """
        获取已用时间
        
        Returns:
            已用时间（秒）
        """
        if self.start_time is None:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()


# 初始化日志配置
setup_logging()