"""
数据可视化模块
生成投资组合分析图表
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List, Tuple
import os
import logging

# 导入字体配置
from src.font_config import setup_chinese_font

# 设置中文字体
setup_chinese_font()

logger = logging.getLogger(__name__)


class Visualizer:
    """可视化类"""
    
    def __init__(self, output_dir: str = "outputs"):
        """
        初始化可视化器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self._create_output_dir()
    
    def _create_output_dir(self) -> None:
        """创建输出目录"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def plot_cumulative_returns(self, returns: pd.DataFrame,
                              optimal_weights: np.ndarray,
                              etf_names: dict = None,
                              save_path: str = None) -> None:
        """
        绘制累计收益对比图

        Args:
            returns: 各ETF日收益率DataFrame
            optimal_weights: 最优权重向量
            etf_names: ETF代码到中文名称的映射字典
            save_path: 保存路径，默认为None
        """
        logger.info("📈 生成累计收益对比图...")

        try:
            # 强制设置中文字体
            from matplotlib.font_manager import FontProperties
            chinese_font = FontProperties(family='AR PL UMing CN')

            # 计算投资组合收益率
            portfolio_returns = (returns * optimal_weights).sum(axis=1)

            # 计算累计收益
            portfolio_cumulative = (1 + portfolio_returns).cumprod()

            # 创建图表
            plt.figure(figsize=(12, 8))
            
            # 绘制各ETF累计收益
            for col in returns.columns:
                etf_cumulative = (1 + returns[col]).cumprod()
                # 使用ETF中文名称作为标签，如果没有则使用代码
                display_name = etf_names.get(col, col) if etf_names else col
                plt.plot(returns.index, etf_cumulative,
                        label=f'{display_name}\n({col})', alpha=0.7, linewidth=1.5)
            
            # 绘制最优组合累计收益
            plt.plot(returns.index, portfolio_cumulative, 
                    label='最优组合', linewidth=3, color='black')
            
            # 设置图表属性
            plt.title('累计收益对比', fontsize=16, fontweight='bold', fontproperties=chinese_font)
            plt.xlabel('日期', fontsize=12, fontproperties=chinese_font)
            plt.ylabel('累计收益倍数', fontsize=12, fontproperties=chinese_font)
            plt.legend(loc='best', fontsize=10, prop=chinese_font)
            plt.grid(True, alpha=0.3)

            # 设置y轴格式
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}x'))
            
            # 自动调整日期显示
            plt.gcf().autofmt_xdate()
            
            # 保存或显示图表
            if save_path:
                full_path = os.path.join(self.output_dir, save_path)
                plt.savefig(full_path, dpi=300, bbox_inches='tight')
                logger.info(f"✅ 累计收益图已保存: {full_path}")
            else:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ 生成累计收益图失败: {e}")
            raise
    
    def plot_efficient_frontier(self, risks: List[float], 
                              returns_list: List[float],
                              optimal_risk: float,
                              optimal_return: float,
                              save_path: str = None) -> None:
        """
        绘制有效前沿
        
        Args:
            risks: 风险列表
            returns_list: 收益列表
            optimal_risk: 最优组合风险
            optimal_return: 最优组合收益
            save_path: 保存路径，默认为None
        """
        logger.info("📊 生成有效前沿图...")

        try:
            # 强制设置中文字体
            from matplotlib.font_manager import FontProperties
            chinese_font = FontProperties(family='AR PL UMing CN')

            plt.figure(figsize=(10, 8))
            
            # 绘制有效前沿
            plt.plot(risks, returns_list, 'b-', linewidth=2, label='有效前沿')
            
            # 标记最优组合点
            plt.scatter(optimal_risk, optimal_return, 
                       color='red', s=100, zorder=5, 
                       label='最优组合（最大夏普比率）')
            
            # 设置图表属性
            plt.title('有效前沿', fontsize=16, fontweight='bold', fontproperties=chinese_font)
            plt.xlabel('年化波动率', fontsize=12, fontproperties=chinese_font)
            plt.ylabel('年化收益率', fontsize=12, fontproperties=chinese_font)
            plt.legend(loc='best', fontsize=10, prop=chinese_font)
            plt.grid(True, alpha=0.3)
            
            # 设置坐标轴格式
            plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2%}'))
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2%}'))
            
            # 保存或显示图表
            if save_path:
                full_path = os.path.join(self.output_dir, save_path)
                plt.savefig(full_path, dpi=300, bbox_inches='tight')
                logger.info(f"✅ 有效前沿图已保存: {full_path}")
            else:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ 生成有效前沿图失败: {e}")
            raise
    
    def plot_portfolio_weights(self, weights: np.ndarray,
                             etf_codes: List[str],
                             etf_names: dict = None,
                             save_path: str = None) -> None:
        """
        绘制权重饼图

        Args:
            weights: 权重向量
            etf_codes: ETF代码列表
            etf_names: ETF代码到中文名称的映射字典
            save_path: 保存路径，默认为None
        """
        logger.info("🥧 生成权重饼图...")

        try:
            # 强制设置中文字体
            from matplotlib.font_manager import FontProperties
            chinese_font = FontProperties(family='AR PL UMing CN')
            # 确保权重数组和ETF代码列表长度匹配
            if len(weights) != len(etf_codes):
                logger.warning(f"⚠️ 权重数组长度({len(weights)})与ETF代码列表长度({len(etf_codes)})不匹配")
                # 使用较短的长度来避免索引越界
                min_length = min(len(weights), len(etf_codes))
                weights = weights[:min_length]
                etf_codes = etf_codes[:min_length]

            # 过滤掉权重为0的ETF
            non_zero_indices = weights > 0.001  # 忽略小于0.1%的权重
            plot_weights = weights[non_zero_indices]
            plot_codes = [etf_codes[i] for i in range(len(etf_codes)) if non_zero_indices[i]]

            # 创建显示标签：中文名称（代码）
            plot_labels = []
            for code in plot_codes:
                display_name = etf_names.get(code, code) if etf_names else code
                plot_labels.append(f'{display_name}\n({code})')
            
            if len(plot_weights) == 0:
                logger.warning("⚠️ 没有有效的权重数据可绘制")
                return
            
            # 创建饼图
            plt.figure(figsize=(10, 8))
            
            # 设置颜色
            colors = plt.cm.Set3(np.linspace(0, 1, len(plot_weights)))
            
            # 绘制饼图
            wedges, texts, autotexts = plt.pie(
                plot_weights,
                labels=plot_labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                textprops={'fontsize': 10, 'fontproperties': chinese_font}
            )
            
            # 设置百分比文本样式
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.title('最优组合权重分配', fontsize=16, fontweight='bold', fontproperties=chinese_font)

            # 添加图例
            plt.legend(wedges, [f'{code}: {weight:.2%}'
                              for code, weight in zip(plot_codes, plot_weights)],
                      title="ETF权重",
                      title_fontproperties=chinese_font,
                      prop=chinese_font,
                      loc="center left",
                      bbox_to_anchor=(1, 0, 0.5, 1))
            
            # 保存或显示图表
            if save_path:
                full_path = os.path.join(self.output_dir, save_path)
                plt.savefig(full_path, dpi=300, bbox_inches='tight')
                logger.info(f"✅ 权重饼图已保存: {full_path}")
            else:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ 生成权重饼图失败: {e}")
            raise
    
    def plot_returns_distribution(self, portfolio_returns: pd.Series,
                                save_path: str = None) -> None:
        """
        绘制收益率分布直方图
        
        Args:
            portfolio_returns: 投资组合日收益率序列
            save_path: 保存路径，默认为None
        """
        logger.info("📊 生成收益率分布图...")

        try:
            # 强制设置中文字体
            from matplotlib.font_manager import FontProperties
            chinese_font = FontProperties(family='AR PL UMing CN')

            plt.figure(figsize=(10, 6))
            
            # 绘制直方图
            n, bins, patches = plt.hist(portfolio_returns, 
                                      bins=50, 
                                      alpha=0.7, 
                                      color='skyblue',
                                      edgecolor='black')
            
            # 添加正态分布曲线
            from scipy.stats import norm
            mu, std = norm.fit(portfolio_returns)
            x = np.linspace(portfolio_returns.min(), portfolio_returns.max(), 100)
            p = norm.pdf(x, mu, std)
            plt.plot(x, p * len(portfolio_returns) * (bins[1] - bins[0]), 
                    'r-', linewidth=2, label=f'正态分布 (μ={mu:.4f}, σ={std:.4f})')
            
            # 设置图表属性
            plt.title('投资组合收益率分布', fontsize=16, fontweight='bold', fontproperties=chinese_font)
            plt.xlabel('日收益率', fontsize=12, fontproperties=chinese_font)
            plt.ylabel('频数', fontsize=12, fontproperties=chinese_font)
            plt.legend(fontsize=10, prop=chinese_font)
            plt.grid(True, alpha=0.3)
            
            # 设置x轴格式
            plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2%}'))
            
            # 保存或显示图表
            if save_path:
                full_path = os.path.join(self.output_dir, save_path)
                plt.savefig(full_path, dpi=300, bbox_inches='tight')
                logger.info(f"✅ 收益率分布图已保存: {full_path}")
            else:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ 生成收益率分布图失败: {e}")
            raise
    
    def generate_all_charts(self, returns: pd.DataFrame,
                          optimal_weights: np.ndarray,
                          etf_codes: List[str],
                          risks: List[float],
                          returns_list: List[float],
                          optimal_risk: float,
                          optimal_return: float,
                          portfolio_returns: pd.Series,
                          etf_names: dict = None) -> None:
        """
        生成所有图表

        Args:
            returns: 各ETF日收益率DataFrame
            optimal_weights: 最优权重向量
            etf_codes: ETF代码列表
            risks: 有效前沿风险列表
            returns_list: 有效前沿收益列表
            optimal_risk: 最优组合风险
            optimal_return: 最优组合收益
            portfolio_returns: 投资组合日收益率序列
            etf_names: ETF代码到中文名称的映射字典
        """
        logger.info("🎨 开始生成所有可视化图表...")
        
        try:
            # 1. 累计收益对比图
            self.plot_cumulative_returns(
                returns, optimal_weights, etf_names,
                'cumulative_returns.png'
            )

            # 2. 有效前沿图
            self.plot_efficient_frontier(
                risks, returns_list, optimal_risk, optimal_return,
                'efficient_frontier.png'
            )

            # 3. 权重饼图
            self.plot_portfolio_weights(
                optimal_weights, etf_codes, etf_names,
                'portfolio_weights.png'
            )

            # 4. 收益率分布图
            self.plot_returns_distribution(
                portfolio_returns,
                'returns_distribution.png'
            )
            
            logger.info("✅ 所有图表生成完成")
            
        except Exception as e:
            logger.error(f"❌ 图表生成失败: {e}")
            raise


def get_visualizer(output_dir: str = "outputs") -> Visualizer:
    """获取可视化器实例"""
    return Visualizer(output_dir)