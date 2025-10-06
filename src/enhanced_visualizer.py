"""
增强可视化模块
用于展示高级量化指标和增强优化结果
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path
import os

# 导入字体配置
from src.font_config import setup_chinese_font

# 设置中文字体
setup_chinese_font()

logger = logging.getLogger(__name__)


class EnhancedVisualizer:
    """增强可视化器"""

    def __init__(self, output_dir: str = "outputs"):
        """
        初始化增强可视化器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self._ensure_output_dir()

        # 设置中文字体
        try:
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
        except:
            # 如果中文字体不可用，使用默认字体
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False

        # 设置样式
        sns.set_style("whitegrid")
        plt.style.use('seaborn-v0_8')

    def _ensure_output_dir(self) -> None:
        """确保输出目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_quant_signals_heatmap(self, signals: Dict[str, pd.Series],
                                    etf_names: Optional[Dict[str, str]] = None) -> str:
        """
        生成量化信号热力图

        Args:
            signals: 量化信号字典
            etf_names: ETF中文名称映射

        Returns:
            生成的图片路径
        """
        try:
            if not signals:
                self.logger.warning("没有信号数据用于生成热力图")
                return ""

            # 强制设置中文字体
            from matplotlib.font_manager import FontProperties
            chinese_font = FontProperties(family='AR PL UMing CN')

            # 设置全局字体
            plt.rcParams['font.sans-serif'] = ['AR PL UMing CN']
            plt.rcParams['axes.unicode_minus'] = False

            # 准备数据
            # 确保signals是字典格式
            if not isinstance(signals, dict):
                self.logger.warning("signals数据格式不正确，应为字典格式")
                return ""

            # 提取实际的信号数据
            actual_signals = {}
            if 'individual_signals' in signals:
                # 使用individual_signals，它包含所有分项信号
                actual_signals = signals['individual_signals']
            elif 'signal_normalized' in signals:
                # 使用标准化后的信号数据
                actual_signals = signals['signal_normalized'].to_dict()
            elif isinstance(signals, dict) and len(signals) > 0:
                # 检查是否直接是信号字典
                first_key = list(signals.keys())[0]
                if isinstance(signals[first_key], pd.Series):
                    actual_signals = signals
                else:
                    self.logger.warning("无法识别的信号数据格式")
                    return ""

            if not actual_signals:
                self.logger.warning("没有可用的信号数据")
                return ""

            # 转换为DataFrame，确保ETF为行，信号为列
            signal_df = pd.DataFrame({k: v for k, v in actual_signals.items() if isinstance(v, (pd.Series, np.ndarray, list))})

            # 确保数据格式正确：ETF作为行，信号类型作为列
            if len(signal_df) > 0 and signal_df.shape[0] < signal_df.shape[1]:
                signal_df = signal_df.T

            # 转换ETF代码为中文名称
            if etf_names and len(signal_df) > 0:
                signal_df.index = [etf_names.get(etf, etf) for etf in signal_df.index]

            # 创建热力图
            plt.figure(figsize=(14, 8))

            # 标准化数据
            signal_normalized = (signal_df - signal_df.mean()) / signal_df.std()

            # 绘制热力图
            sns.heatmap(signal_normalized.T,
                       annot=True,
                       fmt='.2f',
                       cmap='RdBu_r',
                       center=0,
                       cbar_kws={'label': '标准化信号强度'},
                       linewidths=0.5)

            plt.title('ETF量化信号热力图', fontsize=16, fontweight='bold', pad=20, fontproperties=chinese_font)
            plt.xlabel('ETF代码', fontsize=12, fontproperties=chinese_font)
            plt.ylabel('信号类型', fontsize=12, fontproperties=chinese_font)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            # 保存图片
            output_path = os.path.join(self.output_dir, 'quant_signals_heatmap.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            self.logger.info(f"量化信号热力图已保存: {output_path}")
            return 'quant_signals_heatmap.png'

        except Exception as e:
            self.logger.error(f"生成量化信号热力图失败: {e}")
            return ""

    def generate_signal_importance_chart(self, signals: Dict[str, pd.Series],
                                       etf_names: Optional[Dict[str, str]] = None) -> str:
        """
        生成信号重要性分析图

        Args:
            signals: 量化信号字典
            etf_names: ETF中文名称映射

        Returns:
            生成的图片路径
        """
        try:
            if not signals:
                self.logger.warning("没有信号数据用于生成重要性分析图")
                return ""

            # 提取实际的信号数据（与热力图相同的逻辑）
            actual_signals = {}
            if 'individual_signals' in signals:
                actual_signals = signals['individual_signals']
            elif 'signal_normalized' in signals:
                actual_signals = signals['signal_normalized'].to_dict()
            elif isinstance(signals, dict) and len(signals) > 0:
                first_key = list(signals.keys())[0]
                if isinstance(signals[first_key], pd.Series):
                    actual_signals = signals
                else:
                    self.logger.warning("信号重要性分析：无法识别的信号数据格式")
                    return ""

            if not actual_signals:
                self.logger.warning("信号重要性分析：没有可用的信号数据")
                return ""

            # 计算信号重要性（基于标准差）
            signal_importance = {}
            for signal_name, signal_values in actual_signals.items():
                if isinstance(signal_values, pd.Series):
                    signal_importance[signal_name] = signal_values.std()

            # 创建重要性排序
            importance_df = pd.DataFrame(list(signal_importance.items()),
                                       columns=['Signal', 'Importance'])
            importance_df = importance_df.sort_values('Importance', ascending=True)

            # 强制设置中文字体
            from matplotlib.font_manager import FontProperties
            chinese_font = FontProperties(family='AR PL UMing CN')

            # 设置全局字体
            plt.rcParams['font.sans-serif'] = ['AR PL UMing CN']
            plt.rcParams['axes.unicode_minus'] = False

            # 绘制水平条形图
            plt.figure(figsize=(12, 8))

            bars = plt.barh(importance_df['Signal'], importance_df['Importance'],
                          color=plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(importance_df))))

            # 添加数值标签
            for i, (signal, importance) in enumerate(zip(importance_df['Signal'], importance_df['Importance'])):
                plt.text(importance + 0.01, i, f'{importance:.3f}',
                        va='center', fontsize=10)

            plt.title('量化信号重要性分析', fontsize=16, fontweight='bold', pad=20, fontproperties=chinese_font)
            plt.xlabel('信号标准差', fontsize=12, fontproperties=chinese_font)
            plt.ylabel('信号类型', fontsize=12, fontproperties=chinese_font)
            plt.grid(axis='x', alpha=0.3)
            plt.tight_layout()

            # 保存图片
            output_path = os.path.join(self.output_dir, 'signal_importance_chart.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            self.logger.info(f"信号重要性分析图已保存: {output_path}")
            return 'signal_importance_chart.png'

        except Exception as e:
            self.logger.error(f"生成信号重要性分析图失败: {e}")
            return ""

    def generate_optimization_comparison_chart(self, comparison: Dict[str, Any],
                                            etf_names: Optional[Dict[str, str]] = None) -> str:
        """
        生成优化结果对比图

        Args:
            comparison: 优化比较结果
            etf_names: ETF中文名称映射

        Returns:
            生成的图片路径
        """
        try:
            if not comparison or 'traditional' not in comparison or 'enhanced' not in comparison:
                self.logger.warning("没有比较数据用于生成优化对比图")
                return ""

            # 提取数据
            traditional = comparison['traditional']
            enhanced = comparison['enhanced']
            improvement = comparison.get('improvement', {})

            # 强制设置中文字体
            from matplotlib.font_manager import FontProperties
            chinese_font = FontProperties(family='AR PL UMing CN')

            # 设置全局字体
            plt.rcParams['font.sans-serif'] = ['AR PL UMing CN']
            plt.rcParams['axes.unicode_minus'] = False

            # 创建对比图表
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('传统优化 vs 增强优化对比', fontsize=16, fontweight='bold', fontproperties=chinese_font)

            # 1. 夏普比率对比
            sharpe_trad = traditional['metrics'].get('sharpe_ratio', 0)
            sharpe_enh = enhanced['metrics'].get('sharpe_ratio', 0)

            axes[0, 0].bar(['传统优化', '增强优化'], [sharpe_trad, sharpe_enh],
                          color=['lightcoral', 'lightblue'], alpha=0.7)
            axes[0, 0].set_title('夏普比率对比', fontproperties=chinese_font)
            axes[0, 0].set_ylabel('夏普比率', fontproperties=chinese_font)
            for i, v in enumerate([sharpe_trad, sharpe_enh]):
                axes[0, 0].text(i, v + 0.1, f'{v:.4f}', ha='center', va='bottom')

            # 2. 收益率对比
            return_trad = traditional['metrics'].get('portfolio_return', 0)
            return_enh = enhanced['metrics'].get('portfolio_return', 0)

            axes[0, 1].bar(['传统优化', '增强优化'], [return_trad, return_enh],
                          color=['lightcoral', 'lightblue'], alpha=0.7)
            axes[0, 1].set_title('预期收益率对比', fontproperties=chinese_font)
            axes[0, 1].set_ylabel('年化收益率', fontproperties=chinese_font)
            for i, v in enumerate([return_trad, return_enh]):
                axes[0, 1].text(i, v + 0.01, f'{v:.2%}', ha='center', va='bottom')

            # 3. 波动率对比
            vol_trad = traditional['metrics'].get('portfolio_volatility', 0)
            vol_enh = enhanced['metrics'].get('portfolio_volatility', 0)

            axes[1, 0].bar(['传统优化', '增强优化'], [vol_trad, vol_enh],
                          color=['lightcoral', 'lightblue'], alpha=0.7)
            axes[1, 0].set_title('波动率对比', fontproperties=chinese_font)
            axes[1, 0].set_ylabel('年化波动率', fontproperties=chinese_font)
            for i, v in enumerate([vol_trad, vol_enh]):
                axes[1, 0].text(i, v + 0.005, f'{v:.2%}', ha='center', va='bottom')

            # 4. 改进指标
            improvement_metrics = []
            improvement_values = []

            if 'sharpe_improvement_pct' in improvement:
                improvement_metrics.append('夏普比率\n提升(%)')
                improvement_values.append(improvement['sharpe_improvement_pct'])

            if 'return_change' in improvement:
                improvement_metrics.append('收益率\n变化(%)')
                improvement_values.append(improvement['return_change'] * 100)

            if 'volatility_change' in improvement:
                improvement_metrics.append('波动率\n变化(%)')
                improvement_values.append(improvement['volatility_change'] * 100)

            if improvement_metrics:
                colors = ['green' if v > 0 else 'red' for v in improvement_values]
                axes[1, 1].bar(improvement_metrics, improvement_values, color=colors, alpha=0.7)
                axes[1, 1].set_title('改进指标', fontproperties=chinese_font)
                axes[1, 1].set_ylabel('变化百分比', fontproperties=chinese_font)
                axes[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
                for i, v in enumerate(improvement_values):
                    axes[1, 1].text(i, v + (0.1 if v > 0 else -0.1),
                                   f'{v:+.1f}%', ha='center',
                                   va='bottom' if v > 0 else 'top')

            plt.tight_layout()

            # 保存图片
            output_path = os.path.join(self.output_dir, 'optimization_comparison_chart.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            self.logger.info(f"优化对比图已保存: {output_path}")
            return 'optimization_comparison_chart.png'

        except Exception as e:
            self.logger.error(f"生成优化对比图失败: {e}")
            return ""

    def generate_portfolio_composition_chart(self, traditional_weights: np.ndarray,
                                           enhanced_weights: np.ndarray,
                                           etf_codes: List[str],
                                           etf_names: Optional[Dict[str, str]] = None) -> str:
        """
        生成投资组合构成对比图

        Args:
            traditional_weights: 传统优化权重
            enhanced_weights: 增强优化权重
            etf_codes: ETF代码列表
            etf_names: ETF中文名称映射

        Returns:
            生成的图片路径
        """
        try:
            # 强制设置中文字体
            from matplotlib.font_manager import FontProperties
            chinese_font = FontProperties(family='AR PL UMing CN')

            # 设置全局字体
            plt.rcParams['font.sans-serif'] = ['AR PL UMing CN']
            plt.rcParams['axes.unicode_minus'] = False

            # 准备数据
            if etf_names:
                etf_labels = [f"{etf_names.get(code, code)}\n({code})" for code in etf_codes]
            else:
                etf_labels = etf_codes

            # 确保权重数据为数值类型
            try:
                # 如果权重是字典，提取值
                if isinstance(traditional_weights, dict):
                    traditional_weights = list(traditional_weights.values())
                if isinstance(enhanced_weights, dict):
                    enhanced_weights = list(enhanced_weights.values())

                traditional_weights = np.array(traditional_weights, dtype=float)
                enhanced_weights = np.array(enhanced_weights, dtype=float)
            except (ValueError, TypeError) as e:
                self.logger.error(f"权重数据转换失败: {e}")
                return ""

            # 过滤权重大于0的ETF
            significant_indices = [i for i, (t, e) in enumerate(zip(traditional_weights, enhanced_weights))
                                 if t > 0.001 or e > 0.001]

            filtered_labels = [etf_labels[i] for i in significant_indices]
            filtered_trad_weights = [traditional_weights[i] for i in significant_indices]
            filtered_enh_weights = [enhanced_weights[i] for i in significant_indices]

            # 创建对比图
            x = np.arange(len(filtered_labels))
            width = 0.35

            fig, ax = plt.subplots(figsize=(14, 8))

            bars1 = ax.bar(x - width/2, filtered_trad_weights, width,
                          label='传统优化', color='lightcoral', alpha=0.7)
            bars2 = ax.bar(x + width/2, filtered_enh_weights, width,
                          label='增强优化', color='lightblue', alpha=0.7)

            ax.set_xlabel('ETF', fontproperties=chinese_font)
            ax.set_ylabel('权重', fontproperties=chinese_font)
            ax.set_title('投资组合权重对比', fontproperties=chinese_font)
            ax.set_xticks(x)
            ax.set_xticklabels(filtered_labels, rotation=45, ha='right')
            ax.legend(prop=chinese_font)
            ax.grid(axis='y', alpha=0.3)

            # 添加数值标签
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0.01:
                        ax.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                               f'{height:.1%}', ha='center', va='bottom', fontsize=8)

            plt.tight_layout()

            # 保存图片
            output_path = os.path.join(self.output_dir, 'portfolio_composition_chart.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            self.logger.info(f"投资组合构成对比图已保存: {output_path}")
            return 'portfolio_composition_chart.png'

        except Exception as e:
            self.logger.error(f"生成投资组合构成对比图失败: {e}")
            return ""

    def generate_signal_correlation_chart(self, signals: Dict[str, pd.Series]) -> str:
        """
        生成信号相关性分析图

        Args:
            signals: 量化信号字典

        Returns:
            生成的图片路径
        """
        try:
            if not signals:
                self.logger.warning("没有信号数据用于生成相关性分析图")
                return ""

            # 强制设置中文字体
            from matplotlib.font_manager import FontProperties
            chinese_font = FontProperties(family='AR PL UMing CN')

            # 设置全局字体
            plt.rcParams['font.sans-serif'] = ['AR PL UMing CN']
            plt.rcParams['axes.unicode_minus'] = False

            # 提取实际的信号数据（与热力图相同的逻辑）
            actual_signals = {}
            if 'individual_signals' in signals:
                actual_signals = signals['individual_signals']
            elif 'signal_normalized' in signals:
                actual_signals = signals['signal_normalized'].to_dict()
            elif isinstance(signals, dict) and len(signals) > 0:
                first_key = list(signals.keys())[0]
                if isinstance(signals[first_key], pd.Series):
                    actual_signals = signals
                else:
                    self.logger.warning("信号相关性分析：无法识别的信号数据格式")
                    return ""

            if not actual_signals:
                self.logger.warning("信号相关性分析：没有可用的信号数据")
                return ""

            # 转换为DataFrame，确保ETF为行，信号为列
            signal_df = pd.DataFrame({k: v for k, v in actual_signals.items() if isinstance(v, (pd.Series, np.ndarray, list))})

            # 确保数据格式正确：ETF作为行，信号类型作为列
            if len(signal_df) > 0 and signal_df.shape[0] < signal_df.shape[1]:
                signal_df = signal_df.T

            # 计算相关性矩阵
            correlation_matrix = signal_df.corr()

            # 创建相关性热力图
            plt.figure(figsize=(10, 8))

            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))

            sns.heatmap(correlation_matrix,
                       mask=mask,
                       annot=True,
                       fmt='.2f',
                       cmap='coolwarm',
                       center=0,
                       square=True,
                       cbar_kws={'label': '相关系数'},
                       linewidths=0.5)

            plt.title('量化信号相关性分析', fontsize=16, fontweight='bold', pad=20, fontproperties=chinese_font)
            plt.tight_layout()

            # 保存图片
            output_path = os.path.join(self.output_dir, 'signal_correlation_chart.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            self.logger.info(f"信号相关性分析图已保存: {output_path}")
            return 'signal_correlation_chart.png'

        except Exception as e:
            self.logger.error(f"生成信号相关性分析图失败: {e}")
            return ""

    def generate_all_enhanced_charts(self, signals: Optional[Dict[str, pd.Series]] = None,
                                   comparison: Optional[Dict[str, Any]] = None,
                                   traditional_weights: Optional[np.ndarray] = None,
                                   enhanced_weights: Optional[np.ndarray] = None,
                                   etf_codes: Optional[List[str]] = None,
                                   etf_names: Optional[Dict[str, str]] = None) -> List[str]:
        """
        生成所有增强图表

        Args:
            signals: 量化信号
            comparison: 优化比较结果
            traditional_weights: 传统优化权重
            enhanced_weights: 增强优化权重
            etf_codes: ETF代码列表
            etf_names: ETF中文名称映射

        Returns:
            生成的图片路径列表
        """
        chart_files = []

        try:
            self.logger.info("🎨 开始生成增强可视化图表...")

            # 1. 量化信号热力图
            if signals:
                chart_file = self.generate_quant_signals_heatmap(signals, etf_names)
                if chart_file:
                    chart_files.append(chart_file)

                # 2. 信号重要性分析图
                chart_file = self.generate_signal_importance_chart(signals, etf_names)
                if chart_file:
                    chart_files.append(chart_file)

                # 3. 信号相关性分析图
                chart_file = self.generate_signal_correlation_chart(signals)
                if chart_file:
                    chart_files.append(chart_file)

            # 4. 优化结果对比图
            if comparison:
                chart_file = self.generate_optimization_comparison_chart(comparison, etf_names)
                if chart_file:
                    chart_files.append(chart_file)

            # 5. 投资组合构成对比图
            if (traditional_weights is not None and enhanced_weights is not None
                and etf_codes is not None):
                chart_file = self.generate_portfolio_composition_chart(
                    traditional_weights, enhanced_weights, etf_codes, etf_names
                )
                if chart_file:
                    chart_files.append(chart_file)

            self.logger.info(f"✅ 增强可视化图表生成完成，共生成 {len(chart_files)} 个图表")
            return chart_files

        except Exception as e:
            self.logger.error(f"❌ 增强可视化图表生成失败: {e}")
            return []


def get_enhanced_visualizer(output_dir: str = "outputs") -> EnhancedVisualizer:
    """获取增强可视化器实例"""
    return EnhancedVisualizer(output_dir)