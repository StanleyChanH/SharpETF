"""
相关性分析模块
分析ETF间相关性及对投资组合风险的影响
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional
import logging
import os

# 导入字体配置
from src.font_config import setup_chinese_font

# 设置中文字体
setup_chinese_font()

logger = logging.getLogger(__name__)


class CorrelationAnalyzer:
    """相关性分析器"""

    def __init__(self, high_correlation_threshold: float = 0.7,
                 moderate_correlation_threshold: float = 0.5):
        """
        初始化相关性分析器

        Args:
            high_correlation_threshold: 高相关性阈值，默认0.7
            moderate_correlation_threshold: 中等相关性阈值，默认0.5
        """
        self.high_threshold = high_correlation_threshold
        self.moderate_threshold = moderate_correlation_threshold
        self.correlation_matrix = None
        self.high_correlation_pairs = []
        self.moderate_correlation_pairs = []

    def calculate_correlation_matrix(self, returns: pd.DataFrame) -> pd.DataFrame:
        """
        计算ETF间相关性矩阵

        Args:
            returns: 各ETF日收益率DataFrame

        Returns:
            相关性矩阵DataFrame
        """
        logger.info("🔗 计算ETF间相关性矩阵...")

        try:
            # 计算Pearson相关系数
            self.correlation_matrix = returns.corr(method='pearson')

            logger.info("✅ 相关性矩阵计算完成")
            return self.correlation_matrix

        except Exception as e:
            logger.error(f"❌ 相关性矩阵计算失败: {e}")
            raise

    def identify_correlation_risks(self) -> Dict[str, Any]:
        """
        识别相关性风险

        Returns:
            相关性风险分析结果
        """
        if self.correlation_matrix is None:
            raise ValueError("请先计算相关性矩阵")

        logger.info("⚠️ 识别相关性风险...")

        risk_analysis = {
            'high_correlation_pairs': [],
            'moderate_correlation_pairs': [],
            'average_correlation': 0,
            'max_correlation': 0,
            'correlation_distribution': {},
            'risk_assessment': {},
            'diversification_score': 0
        }

        try:
            # 识别高相关性和中等相关性ETF对
            for i in range(len(self.correlation_matrix.columns)):
                for j in range(i + 1, len(self.correlation_matrix.columns)):
                    etf1 = self.correlation_matrix.columns[i]
                    etf2 = self.correlation_matrix.columns[j]
                    correlation = self.correlation_matrix.iloc[i, j]

                    if abs(correlation) >= self.high_threshold:
                        risk_analysis['high_correlation_pairs'].append({
                            'etf1': etf1,
                            'etf2': etf2,
                            'correlation': correlation,
                            'risk_level': '高风险'
                        })
                    elif abs(correlation) >= self.moderate_threshold:
                        risk_analysis['moderate_correlation_pairs'].append({
                            'etf1': etf1,
                            'etf2': etf2,
                            'correlation': correlation,
                            'risk_level': '中等风险'
                        })

            # 计算统计指标
            upper_triangle = self.correlation_matrix.where(
                np.triu(np.ones(self.correlation_matrix.shape), k=1).astype(bool)
            ).stack()

            risk_analysis['average_correlation'] = upper_triangle.mean()
            risk_analysis['max_correlation'] = upper_triangle.abs().max()

            # 相关性分布统计
            risk_analysis['correlation_distribution'] = {
                'high_correlation_count': len([x for x in upper_triangle if abs(x) >= self.high_threshold]),
                'moderate_correlation_count': len([x for x in upper_triangle if self.moderate_threshold <= abs(x) < self.high_threshold]),
                'low_correlation_count': len([x for x in upper_triangle if abs(x) < self.moderate_threshold]),
                'total_pairs': len(upper_triangle)
            }

            # 风险评估
            risk_analysis['risk_assessment'] = self._assess_correlation_risk(risk_analysis)

            # 分散化评分（0-100分）
            risk_analysis['diversification_score'] = self._calculate_diversification_score(upper_triangle)

            logger.info("✅ 相关性风险识别完成")
            return risk_analysis

        except Exception as e:
            logger.error(f"❌ 相关性风险识别失败: {e}")
            raise

    def _assess_correlation_risk(self, risk_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估相关性风险等级

        Args:
            risk_analysis: 风险分析数据

        Returns:
            风险评估结果
        """
        high_count = len(risk_analysis['high_correlation_pairs'])
        moderate_count = len(risk_analysis['moderate_correlation_pairs'])
        avg_corr = risk_analysis['average_correlation']

        if high_count >= 3 or avg_corr >= 0.6:
            risk_level = "高风险"
            risk_color = "red"
            risk_score = 80 + min(20, high_count * 5)
        elif high_count >= 1 or moderate_count >= 3 or avg_corr >= 0.4:
            risk_level = "中等风险"
            risk_color = "orange"
            risk_score = 40 + min(40, high_count * 10 + moderate_count * 5)
        else:
            risk_level = "低风险"
            risk_color = "green"
            risk_score = min(40, moderate_count * 8)

        return {
            'risk_level': risk_level,
            'risk_color': risk_color,
            'risk_score': risk_score,
            'description': self._get_risk_description(risk_level, high_count, moderate_count, avg_corr)
        }

    def _get_risk_description(self, risk_level: str, high_count: int,
                            moderate_count: int, avg_corr: float) -> str:
        """获取风险描述"""
        if risk_level == "高风险":
            return f"投资组合存在{high_count}对高相关性ETF，平均相关性{avg_corr:.2f}，分散化程度严重不足，建议重新评估配置。"
        elif risk_level == "中等风险":
            return f"投资组合存在{high_count}对高相关性和{moderate_count}对中等相关性ETF，平均相关性{avg_corr:.2f}，具有一定集中风险，建议适度分散。"
        else:
            return f"投资组合相关性较低，平均相关性{avg_corr:.2f}，分散化程度良好。"

    def _calculate_diversification_score(self, correlations: pd.Series) -> float:
        """
        计算分散化评分

        Args:
            correlations: 相关性系数Series

        Returns:
            分散化评分（0-100）
        """
        # 分散化评分 = 100 * (1 - 平均绝对相关性)
        avg_abs_corr = correlations.abs().mean()
        score = 100 * (1 - avg_abs_corr)
        return max(0, min(100, score))

    def generate_correlation_heatmap(self, save_path: str = None,
                                   output_dir: str = "outputs") -> str:
        """
        生成相关性热力图

        Args:
            save_path: 保存文件名
            output_dir: 输出目录

        Returns:
            保存的文件路径
        """
        if self.correlation_matrix is None:
            raise ValueError("请先计算相关性矩阵")

        logger.info("🔥 生成相关性热力图...")

        try:
            # 强制设置中文字体
            from matplotlib.font_manager import FontProperties
            chinese_font = FontProperties(family='AR PL UMing CN')

            plt.figure(figsize=(12, 10))

            # 创建热力图
            mask = np.triu(np.ones_like(self.correlation_matrix, dtype=bool))

            # 使用自定义颜色映射
            cmap = sns.diverging_palette(240, 10, as_cmap=True)

            sns.heatmap(
                self.correlation_matrix,
                mask=mask,
                annot=True,
                cmap=cmap,
                center=0,
                square=True,
                linewidths=0.5,
                cbar_kws={"shrink": 0.8},
                fmt='.3f',
                annot_kws={'size': 10}
            )

            plt.title('ETF相关性矩阵热力图', fontsize=16, fontweight='bold', pad=20, fontproperties=chinese_font)
            plt.xlabel('ETF代码', fontsize=12, fontproperties=chinese_font)
            plt.ylabel('ETF代码', fontsize=12, fontproperties=chinese_font)
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)

            # 调整布局
            plt.tight_layout()

            # 保存图表
            if save_path is None:
                save_path = 'correlation_heatmap.png'

            full_path = os.path.join(output_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"✅ 相关性热力图已保存: {full_path}")
            return full_path

        except Exception as e:
            logger.error(f"❌ 相关性热力图生成失败: {e}")
            raise

    def generate_correlation_report(self, returns: pd.DataFrame,
                                  optimal_weights: np.ndarray,
                                  etf_codes: List[str]) -> Dict[str, Any]:
        """
        生成完整的相关性分析报告

        Args:
            returns: 各ETF日收益率DataFrame
            optimal_weights: 最优权重向量
            etf_codes: ETF代码列表

        Returns:
            相关性分析报告
        """
        logger.info("📊 生成相关性分析报告...")

        try:
            # 计算相关性矩阵
            self.calculate_correlation_matrix(returns)

            # 识别相关性风险
            risk_analysis = self.identify_correlation_risks()

            # 分析权重与相关性的关系
            weight_correlation_analysis = self._analyze_weights_with_correlation(
                optimal_weights, etf_codes
            )

            # 生成优化建议
            optimization_suggestions = self._generate_optimization_suggestions(
                risk_analysis, weight_correlation_analysis
            )

            # 生成热力图
            heatmap_path = self.generate_correlation_heatmap()

            report = {
                'correlation_matrix': self.correlation_matrix.to_dict(),
                'risk_analysis': risk_analysis,
                'weight_correlation_analysis': weight_correlation_analysis,
                'optimization_suggestions': optimization_suggestions,
                'heatmap_path': heatmap_path,
                'analysis_summary': self._generate_analysis_summary(risk_analysis)
            }

            logger.info("✅ 相关性分析报告生成完成")
            return report

        except Exception as e:
            logger.error(f"❌ 相关性分析报告生成失败: {e}")
            raise

    def _analyze_weights_with_correlation(self, optimal_weights: np.ndarray,
                                        etf_codes: List[str]) -> Dict[str, Any]:
        """
        分析权重配置与相关性的关系

        Args:
            optimal_weights: 最优权重向量
            etf_codes: ETF代码列表

        Returns:
            权重相关性分析结果
        """
        weight_dict = dict(zip(etf_codes, optimal_weights))

        # 找出权重最大的ETF
        top_weighted_etfs = sorted(
            [(etf, weight) for etf, weight in weight_dict.items() if weight > 0.01],
            key=lambda x: x[1], reverse=True
        )[:5]

        # 分析权重最大ETF与其他高相关性ETF的组合
        high_weight_high_correlation = []
        for etf, weight in top_weighted_etfs:
            if etf in self.correlation_matrix.columns:
                # 找出与该ETF高相关的其他ETF
                correlated_etfs = []
                for other_etf in self.correlation_matrix.columns:
                    if other_etf != etf:
                        correlation = self.correlation_matrix.loc[etf, other_etf]
                        if abs(correlation) >= self.moderate_threshold:
                            other_weight = weight_dict.get(other_etf, 0)
                            if other_weight > 0.01:
                                correlated_etfs.append({
                                    'etf': other_etf,
                                    'correlation': correlation,
                                    'weight': other_weight,
                                    'combined_weight': weight + other_weight
                                })

                if correlated_etfs:
                    high_weight_high_correlation.append({
                        'primary_etf': etf,
                        'primary_weight': weight,
                        'correlated_etfs': correlated_etfs
                    })

        return {
            'top_weighted_etfs': top_weighted_etfs,
            'high_weight_high_correlation': high_weight_high_correlation,
            'concentration_risk': len(high_weight_high_correlation) > 0
        }

    def _generate_optimization_suggestions(self, risk_analysis: Dict[str, Any],
                                         weight_analysis: Dict[str, Any]) -> List[str]:
        """
        生成优化建议

        Args:
            risk_analysis: 风险分析结果
            weight_analysis: 权重分析结果

        Returns:
            优化建议列表
        """
        suggestions = []

        high_corr_count = len(risk_analysis['high_correlation_pairs'])
        moderate_corr_count = len(risk_analysis['moderate_correlation_pairs'])
        diversification_score = risk_analysis['diversification_score']

        # 基于风险等级的建议
        if risk_analysis['risk_assessment']['risk_level'] == "高风险":
            suggestions.append("⚠️ 投资组合相关性过高，强烈建议重新配置以降低集中风险")

            if high_corr_count > 0:
                suggestions.append(f"🔄 发现{high_corr_count}对高相关性ETF，建议考虑替换其中部分标的")

            if diversification_score < 30:
                suggestions.append("📊 分散化评分过低，建议增加不同行业或风格的ETF")

        elif risk_analysis['risk_assessment']['risk_level'] == "中等风险":
            suggestions.append("⚖️ 投资组合存在一定相关性风险，可考虑适度分散")

            if moderate_corr_count > 2:
                suggestions.append("📈 建议关注中等相关性ETF的配置比例")

        # 基于权重的建议
        if weight_analysis['concentration_risk']:
            suggestions.append("💰 高权重ETF与其他持仓存在较高相关性，建议分散权重")

        # 通用建议
        if diversification_score < 50:
            suggestions.append("🎯 建议加入不同板块或资产类别的ETF以提高分散化程度")

        suggestions.append("📊 定期监控ETF相关性变化，及时调整投资组合")
        suggestions.append("🔍 在市场极端行情下，相关性可能上升，需加强风险管理")

        return suggestions

    def _generate_analysis_summary(self, risk_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成分析摘要

        Args:
            risk_analysis: 风险分析结果

        Returns:
            分析摘要
        """
        return {
            'total_etf_pairs': risk_analysis['correlation_distribution']['total_pairs'],
            'high_correlation_pairs': risk_analysis['correlation_distribution']['high_correlation_count'],
            'moderate_correlation_pairs': risk_analysis['correlation_distribution']['moderate_correlation_count'],
            'average_correlation': risk_analysis['average_correlation'],
            'maximum_correlation': risk_analysis['max_correlation'],
            'diversification_score': risk_analysis['diversification_score'],
            'risk_level': risk_analysis['risk_assessment']['risk_level'],
            'risk_score': risk_analysis['risk_assessment']['risk_score']
        }


def get_correlation_analyzer(high_correlation_threshold: float = 0.7,
                           moderate_correlation_threshold: float = 0.5) -> CorrelationAnalyzer:
    """获取相关性分析器实例"""
    return CorrelationAnalyzer(high_correlation_threshold, moderate_correlation_threshold)