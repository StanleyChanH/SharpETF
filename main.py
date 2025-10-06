#!/usr/bin/env python3
"""
ETF夏普比率最优组合研究系统
主执行脚本

重要提示：需要Tushare Pro账号和2000+积分
"""

import sys
import os
import logging
import numpy as np

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 设置中文字体（尽早设置）
try:
    from src.font_config import setup_chinese_font
    setup_chinese_font()
except ImportError as e:
    print(f"⚠️ 字体配置模块导入失败: {e}")
except Exception as e:
    print(f"⚠️ 字体设置失败: {e}")

from src.config import get_config
from src.data_fetcher import get_data_fetcher
from src.data_processor import get_data_processor
from src.evaluator import get_portfolio_evaluator
from src.visualizer import get_visualizer
from src.utils import (
    setup_logging, save_results, print_welcome_banner,
    print_summary_table, Timer
)

# 导入新的增强模块
from src.risk_manager import get_advanced_risk_manager
from src.rebalancing_engine import get_rebalancing_engine
from src.multi_objective_optimizer import get_multi_objective_optimizer
from src.investment_tools import (
    get_investment_calculator, get_signal_generator,
    get_performance_attribution, get_portfolio_analyzer
)
from src.html_report_generator import get_html_report_generator
from src.correlation_analyzer import get_correlation_analyzer

# 导入统一的量化信号模块
from src.quant_signals import get_quant_signals, get_simple_quant_signals, get_advanced_quant_indicators

# 导入增强优化器（保留原有模块）
from src.enhanced_portfolio_optimizer import get_enhanced_portfolio_optimizer
from src.enhanced_visualizer import get_enhanced_visualizer
from src.simple_enhanced_optimizer import get_simple_enhanced_optimizer

# 导入统一优化器
from src.portfolio_optimizer import get_portfolio_optimizer
OPTIMIZER_TYPE = "unified"


class EnhancedETFSharpeOptimizer:
    """增强版ETF夏普比率最优组合研究系统"""

    def __init__(self):
        """初始化主类"""
        self.logger = logging.getLogger(__name__)
        self.config = get_config()
        self.data_fetcher = get_data_fetcher()
        self.data_processor = get_data_processor(self.config.trading_days)
        self.portfolio_optimizer = get_portfolio_optimizer(self.config.risk_free_rate)
        self.evaluator = get_portfolio_evaluator(self.config.trading_days, self.config.risk_free_rate)
        self.visualizer = get_visualizer(self.config.output_dir)
        self.html_report_generator = get_html_report_generator(self.config.output_dir)
        self.correlation_analyzer = get_correlation_analyzer()

        # 初始化新增模块
        self.risk_manager = get_advanced_risk_manager()
        self.rebalancing_engine = get_rebalancing_engine()
        self.multi_objective_optimizer = get_multi_objective_optimizer(
            self.config.risk_free_rate, self.config.trading_days
        )
        self.investment_calculator = get_investment_calculator()
        self.signal_generator = get_signal_generator()
        self.performance_attribution = get_performance_attribution()
        self.portfolio_analyzer = get_portfolio_analyzer()

        # 初始化统一的量化信号模块
        self.quant_signals = get_quant_signals(self.config.trading_days, mode='advanced')

        # 初始化增强优化器
        self.enhanced_optimizer = get_enhanced_portfolio_optimizer(
            self.config.risk_free_rate, self.config.trading_days
        )
        self.enhanced_visualizer = get_enhanced_visualizer(self.config.output_dir)

        # 初始化简化模块作为备用
        self.simple_quant_signals = get_simple_quant_signals(self.config.trading_days)
        self.simple_enhanced_optimizer = get_simple_enhanced_optimizer(
            self.config.risk_free_rate, self.config.trading_days
        )

        # 存储中间结果
        self.raw_data = None
        self.etf_names = None  # ETF中文名称映射
        self.returns = None
        self.annual_mean = None
        self.cov_matrix = None
        self.optimal_weights = None
        self.max_sharpe_ratio = None
        self.portfolio_returns = None
        self.metrics = None
        self.risk_report = None
        self.rebalancing_report = None
        self.multi_objective_results = None
        self.investment_analysis = None
        self.correlation_analysis = None
        self.enhanced_signals = None
        self.enhanced_optimization_results = None
        self.enhanced_charts = None

        # 记录使用的优化器类型
        self.logger.info(f"使用优化器: {OPTIMIZER_TYPE}")
        self.logger.info("✅ 增强版ETF优化系统初始化完成")
    
    def run_analysis(self) -> None:
        """运行完整的增强分析流程"""
        print_welcome_banner()

        try:
            with Timer("完整增强分析流程"):
                # 1. 数据获取
                self._fetch_data()

                # 2. 数据处理
                self._process_data()

                # 3. 组合优化
                self._optimize_portfolio()

                # 4. 多目标优化比较
                self._run_multi_objective_optimization()

                # 5. 计算评估指标
                self._evaluate_portfolio()

                # 6. 高级风险分析
                self._analyze_risks()

                # 7. 再平衡策略分析
                self._analyze_rebalancing()

                # 8. 高级量化指标分析
                self._analyze_enhanced_quant_signals()

                # 9. 增强投资组合优化
                self._run_enhanced_optimization()

                # 10. 投资实用工具分析（现在有增强策略数据了）
                self._analyze_investment_tools()

                # 11. 相关性分析
                self._analyze_correlations()

                # 12. 生成可视化
                self._generate_visualizations()

                # 13. 保存结果
                self._save_results()

                # 14. 生成HTML报告
                self._generate_html_report()

                # 15. 打印增强报告
                self._print_enhanced_final_report()

            self.logger.info("✅ 增强分析完成！")

        except Exception as e:
            self.logger.error(f"❌ 分析失败: {e}")
            sys.exit(1)
    
    def _fetch_data(self) -> None:
        """获取数据"""
        with Timer("数据获取"):
            # 获取ETF价格数据
            self.raw_data = self.data_fetcher.fetch_etf_data()

            # 获取ETF中文名称
            self.etf_names = self.data_fetcher.get_etf_names(self.config.etf_codes)

            self.logger.info(f"获取到 {len(self.raw_data)} 个交易日数据")
            self.logger.info(f"成功获取 {len(self.etf_names)} 个ETF名称信息")
    
    def _process_data(self) -> None:
        """处理数据"""
        with Timer("数据处理"):
            self.returns, self.annual_mean, self.cov_matrix = self.data_processor.process_data(self.raw_data)
            
            # 打印数据摘要
            data_summary = self.data_processor.get_data_summary(
                self.returns, self.annual_mean, self.cov_matrix
            )
            print_summary_table({"数据摘要": data_summary})
    
    def _optimize_portfolio(self) -> None:
        """优化投资组合"""
        with Timer("组合优化"):
            self.optimal_weights, self.max_sharpe_ratio = self.portfolio_optimizer.maximize_sharpe_ratio(
                self.annual_mean, self.cov_matrix
            )
            
            # 计算有效前沿
            risks, returns_list = self.portfolio_optimizer.calculate_efficient_frontier(
                self.annual_mean, self.cov_matrix
            )
            
            # 计算最优组合的风险和收益
            portfolio_return = self.annual_mean.values @ self.optimal_weights
            portfolio_vol = np.sqrt(self.optimal_weights.T @ self.cov_matrix.values @ self.optimal_weights)
            
            # 存储有效前沿数据
            self.efficient_frontier_data = {
                'risks': risks,
                'returns': returns_list,
                'optimal_risk': portfolio_vol,
                'optimal_return': portfolio_return
            }
            
            # 打印优化摘要
            optimization_summary = self.portfolio_optimizer.get_optimization_summary(
                self.optimal_weights, self.max_sharpe_ratio,
                self.annual_mean, self.cov_matrix
            )
            print_summary_table({"优化结果": optimization_summary})
    
    def _evaluate_portfolio(self) -> None:
        """评估投资组合"""
        with Timer("组合评估"):
            # 计算投资组合收益率
            self.portfolio_returns = (self.returns * self.optimal_weights).sum(axis=1)
            
            # 计算评估指标
            self.metrics = self.evaluator.calculate_portfolio_metrics(self.portfolio_returns)
            
            # 打印评估报告
            self.evaluator.print_evaluation_report(
                self.metrics, self.optimal_weights, self.config.etf_codes, self.etf_names
            )
    
    def _generate_visualizations(self) -> None:
        """生成可视化图表"""
        with Timer("可视化生成"):
            self.visualizer.generate_all_charts(
                returns=self.returns,
                optimal_weights=self.optimal_weights,
                etf_codes=self.config.etf_codes,
                risks=self.efficient_frontier_data['risks'],
                returns_list=self.efficient_frontier_data['returns'],
                optimal_risk=self.efficient_frontier_data['optimal_risk'],
                optimal_return=self.efficient_frontier_data['optimal_return'],
                portfolio_returns=self.portfolio_returns,
                etf_names=self.etf_names
            )
    
    def _save_results(self) -> None:
        """保存结果"""
        with Timer("结果保存"):
            # 准备保存的数据
            results = {
                'config': {
                    'etf_codes': self.config.etf_codes,
                    'start_date': self.config.start_date,
                    'end_date': self.config.end_date,
                    'risk_free_rate': self.config.risk_free_rate,
                    'trading_days': self.config.trading_days
                },
                'optimization_results': {
                    'optimal_weights': dict(zip(self.config.etf_codes, self.optimal_weights)),
                    'max_sharpe_ratio': self.max_sharpe_ratio,
                    'portfolio_return': self.annual_mean.values @ self.optimal_weights,
                    'portfolio_volatility': np.sqrt(self.optimal_weights.T @ self.cov_matrix.values @ self.optimal_weights)
                },
                'performance_metrics': self.metrics,
                'efficient_frontier': {
                    'risks': self.efficient_frontier_data['risks'],
                    'returns': self.efficient_frontier_data['returns']
                },
                'data_summary': {
                    'period_days': len(self.returns),
                    'etf_annual_returns': self.annual_mean.to_dict(),
                    'etf_volatilities': {etf: np.sqrt(self.cov_matrix.loc[etf, etf])
                                       for etf in self.annual_mean.index}
                },
                'correlation_analysis': self.correlation_analysis if self.correlation_analysis else {}
            }
  
            save_results(results, "optimization_results.json")

    def _generate_html_report(self) -> None:
        """生成HTML报告"""
        with Timer("HTML报告生成"):
            self.logger.info("📝 开始生成HTML分析报告...")

            try:
                # 准备报告数据
                config_data = {
                    'etf_codes': self.config.etf_codes,
                    'start_date': self.config.start_date,
                    'end_date': self.config.end_date,
                    'risk_free_rate': self.config.risk_free_rate,
                    'trading_days': self.config.trading_days
                }

                optimization_data = {
                    'optimal_weights': dict(zip(self.config.etf_codes, self.optimal_weights)),
                    'max_sharpe_ratio': self.max_sharpe_ratio,
                    'portfolio_return': self.annual_mean.values @ self.optimal_weights,
                    'portfolio_volatility': np.sqrt(self.optimal_weights.T @ self.cov_matrix.values @ self.optimal_weights),
                    'data_summary': {
                        'etf_annual_returns': self.annual_mean.to_dict(),
                        'etf_volatilities': {etf: np.sqrt(self.cov_matrix.loc[etf, etf])
                                           for etf in self.annual_mean.index}
                    }
                }

                # 生成增强HTML报告
                report_path = self.html_report_generator.generate_enhanced_html_report(
                    config=config_data,
                    optimization_results=optimization_data,
                    performance_metrics=self.metrics,
                    risk_report=getattr(self, 'risk_report', None),
                    investment_analysis=getattr(self, 'investment_analysis', None),
                    correlation_analysis=getattr(self, 'correlation_analysis', None),
                    etf_names=self.etf_names,
                    enhanced_signals=getattr(self, 'enhanced_signals', None),
                    enhanced_results=getattr(self, 'enhanced_optimization_results', None),
                    enhanced_charts=getattr(self, 'enhanced_charts', None)
                )

                self.logger.info(f"✅ HTML报告生成完成: {report_path}")

            except Exception as e:
                self.logger.error(f"❌ HTML报告生成失败: {e}")
                # 不抛出异常，继续执行其他步骤

    def _run_multi_objective_optimization(self) -> None:
        """运行多目标优化比较"""
        with Timer("多目标优化分析"):
            self.logger.info("🔄 开始多目标优化比较...")
            self.multi_objective_results = self.multi_objective_optimizer.compare_optimization_methods(
                self.annual_mean, self.cov_matrix, self.returns
            )

    def _analyze_risks(self) -> None:
        """进行高级风险分析"""
        with Timer("高级风险分析"):
            self.logger.info("🔒 开始高级风险分析...")
            self.risk_report = self.risk_manager.generate_risk_report(
                self.portfolio_returns, self.optimal_weights,
                self.config.etf_codes, self.returns
            )

    def _analyze_rebalancing(self) -> None:
        """分析再平衡策略"""
        with Timer("再平衡策略分析"):
            self.logger.info("⚖️ 开始再平衡策略分析...")
            # 模拟当前权重（假设有5%的偏离）
            current_weights = self.optimal_weights + np.random.normal(0, 0.02, len(self.optimal_weights))
            current_weights = np.maximum(current_weights, 0)
            current_weights = current_weights / np.sum(current_weights)

            self.rebalancing_report = self.rebalancing_engine.generate_rebalancing_report(
                current_weights, self.optimal_weights, 1000000,  # 假设100万组合
                self.portfolio_returns, self.config.etf_codes, self.returns
            )

    def _analyze_investment_tools(self) -> None:
        """分析投资实用工具"""
        with Timer("投资工具分析"):
            self.logger.info("💼 开始投资工具分析...")

            # 原始策略投资增长预测
            original_growth_projection = self.investment_calculator.project_portfolio_growth(
                self.metrics['annual_return'],
                self.metrics['annual_volatility'],
                years=5
            )

            # 计算增强策略的投资组合指标和增长预测
            enhanced_growth_projection = None
            if (self.enhanced_optimization_results and
                'enhanced_metrics' in self.enhanced_optimization_results):
                enhanced_metrics = self.enhanced_optimization_results['enhanced_metrics']

                # 使用增强策略的年化收益率和波动率进行增长预测
                enhanced_annual_return = enhanced_metrics.get('portfolio_return', self.metrics['annual_return'])
                enhanced_annual_volatility = enhanced_metrics.get('portfolio_volatility', self.metrics['annual_volatility'])

                try:
                    enhanced_growth_projection = self.investment_calculator.project_portfolio_growth(
                        enhanced_annual_return,
                        enhanced_annual_volatility,
                        years=5
                    )
                except Exception as e:
                    self.logger.error(f"增强策略增长预测计算失败: {e}")
                    enhanced_growth_projection = None

            # 行业敞口分析（基于原始策略）
            sector_analysis = self.portfolio_analyzer.analyze_sector_exposure(
                self.config.etf_codes, self.optimal_weights
            )

            # 投资建议
            recommendations = self.portfolio_analyzer.generate_investment_recommendations(
                self.risk_report, self.metrics
            )

            self.investment_analysis = {
                'growth_projection': original_growth_projection,
                'enhanced_growth_projection': enhanced_growth_projection,
                'sector_analysis': sector_analysis,
                'recommendations': recommendations
            }

    def _analyze_correlations(self) -> None:
        """进行相关性分析"""
        with Timer("相关性分析"):
            self.logger.info("🔗 开始相关性分析...")
            self.correlation_analysis = self.correlation_analyzer.generate_correlation_report(
                self.returns, self.optimal_weights, self.config.etf_codes
            )

    def _print_enhanced_final_report(self) -> None:
        """打印增强版最终报告"""
        print("\n" + "="*100)
        print("🎯 增强版ETF投资组合优化系统 - 综合分析报告")
        print("="*100)

        print(f"\n📅 分析期间: {self.config.start_date} 至 {self.config.end_date}")
        print(f"📊 分析标的: {', '.join(self.config.etf_codes)}")
        print(f"💰 无风险利率: {self.config.risk_free_rate:.2%}")

        # 基础优化结果
        print(f"\n🏆 最优组合基础表现:")
        print(f"  • 最大夏普比率: {self.max_sharpe_ratio:.4f}")
        print(f"  • 年化收益率: {self.metrics['annual_return']:.2%}")
        print(f"  • 年化波动率: {self.metrics['annual_volatility']:.2%}")
        print(f"  • 最大回撤: {self.metrics['max_drawdown']:.2%}")
        print(f"  • 夏普比率: {self.metrics['sharpe_ratio']:.4f}")

        # 多目标优化比较
        if self.multi_objective_results:
            print(f"\n🔄 多目标优化比较:")
            for method, result in self.multi_objective_results.items():
                metrics = result['metrics']
                print(f"  • {result['method']}: "
                      f"收益={metrics['portfolio_return']:.2%}, "
                      f"波动={metrics['portfolio_volatility']:.2%}, "
                      f"夏普={metrics['sharpe_ratio']:.4f}")

        # 风险分析结果
        if self.risk_report:
            risk_rating = self.risk_report.get('risk_rating', {}).get('overall_risk', '未知')
            var_95 = self.risk_report.get('var_cvar_analysis', {}).get(0.95, {}).get('var_historical', 0)
            concentration_hhi = self.risk_report.get('concentration_risk', {}).get('hhi', 0)

            print(f"\n🔒 高级风险分析:")
            print(f"  • 综合风险评级: {risk_rating}")
            print(f"  • 95% VaR (历史): {var_95:.2%}")
            print(f"  • 集中度指数 (HHI): {concentration_hhi:.0f}")

        # 再平衡建议
        if self.rebalancing_report:
            needs_rebalancing = self.rebalancing_report.get('weight_analysis', {}).get('needs_rebalancing', False)
            max_deviation = self.rebalancing_report.get('weight_analysis', {}).get('max_deviation', 0)

            print(f"\n⚖️ 再平衡分析:")
            print(f"  • 需要再平衡: {'是' if needs_rebalancing else '否'}")
            print(f"  • 最大权重偏离: {max_deviation:.2%}")

        # 相关性分析
        if self.correlation_analysis:
            risk_assessment = self.correlation_analysis.get('risk_analysis', {}).get('risk_assessment', {})
            summary = self.correlation_analysis.get('analysis_summary', {})

            print(f"\n🔗 相关性分析:")
            print(f"  • 相关性风险等级: {risk_assessment.get('risk_level', '未知')}")
            print(f"  • 分散化评分: {summary.get('diversification_score', 0):.1f}/100")
            print(f"  • 平均相关性: {summary.get('average_correlation', 0):.3f}")
            print(f"  • 高相关性ETF对: {summary.get('high_correlation_pairs', 0)}对")

        # 投资建议
        if self.investment_analysis:
            recommendations = self.investment_analysis.get('recommendations', [])
            growth_proj = self.investment_analysis.get('growth_projection', {})

            print(f"\n💡 投资建议:")
            for i, rec in enumerate(recommendations[:3], 1):  # 显示前3条建议
                print(f"  {i}. {rec}")

            print(f"\n📈 5年增长预测 (100万初始投资):")
            print(f"  📊 原始策略:")
            print(f"    • 平均预期价值: {growth_proj.get('final_value_statistics', {}).get('mean', 0):,.0f}元")
            print(f"    • 中位数价值: {growth_proj.get('final_value_statistics', {}).get('median', 0):,.0f}元")

            # 显示增强策略的增长预测
            enhanced_growth_proj = self.investment_analysis.get('enhanced_growth_projection')
            if enhanced_growth_proj:
                print(f"  🚀 量化增强策略:")
                print(f"    • 平均预期价值: {enhanced_growth_proj.get('final_value_statistics', {}).get('mean', 0):,.0f}元")
                print(f"    • 中位数价值: {enhanced_growth_proj.get('final_value_statistics', {}).get('median', 0):,.0f}元")

                # 计算改进情况
                original_mean = growth_proj.get('final_value_statistics', {}).get('mean', 0)
                enhanced_mean = enhanced_growth_proj.get('final_value_statistics', {}).get('mean', 0)
                if original_mean > 0:
                    improvement = ((enhanced_mean - original_mean) / original_mean) * 100
                    if improvement > 0:
                        print(f"    • 预期提升: +{improvement:.1f}%")
                    else:
                        print(f"    • 预期变化: {improvement:.1f}%")
            else:
                print(f"  🚀 量化增强策略: 暂无数据")

        # 权重分配
        print(f"\n⚖️ 最优权重分配:")
        for etf, weight in zip(self.config.etf_codes, self.optimal_weights):
            if weight > 0.001:
                print(f"  • {etf}: {weight:.2%}")

        # 文件输出
        print(f"\n📈 可视化图表:")
        print(f"  • 累计收益对比图: outputs/cumulative_returns.png")
        print(f"  • 有效前沿图: outputs/efficient_frontier.png")
        print(f"  • 权重饼图: outputs/portfolio_weights.png")
        print(f"  • 收益率分布图: outputs/returns_distribution.png")

        print(f"\n💾 数据文件:")
        print(f"  • 详细结果: outputs/optimization_results.json")
        print(f"  • 运行日志: etf_optimizer.log")

        print(f"\n📊 HTML报告:")
        print(f"  • 精美分析报告: outputs/etf_optimization_report.html")
        print(f"    (包含完整的分析结果、可视化图表和投资建议)")

        print("\n" + "="*100)
        print("✅ 增强分析完成！所有结果已保存到 outputs/ 目录")
        print("🎯 本报告提供了全面的投资决策支持，建议结合个人风险承受能力进行投资")
        print("="*100)

    def _analyze_enhanced_quant_signals(self) -> None:
        """分析高级量化指标"""
        with Timer("高级量化指标分析"):
            try:
                self.logger.info("🔬 开始高级量化指标分析...")

                # 生成增强信号
                # 从raw_data中提取价格数据，raw_data已经合并了所有ETF的价格
                price_columns = [col for col in self.raw_data.columns if col not in ['trade_date', 'ts_code']]
                prices = self.raw_data[['trade_date'] + price_columns].set_index('trade_date')

                # 直接使用简化量化指标版本
                self.enhanced_signals = self.simple_quant_signals.generate_signals(
                    self.returns, prices
                )
                if self.enhanced_signals:
                    print("\n" + "="*70)
                    print("🔬 量化指标分析完成")
                    print("="*70)

                    # 显示量化信号结果
                    if 'signal_analysis' in self.enhanced_signals:
                        analysis = self.enhanced_signals['signal_analysis']
                        print(f"\n📊 量化信号概况:")
                        print(f"  • 信号数量: {analysis['signal_count']}")
                        print(f"  • 最佳表现ETF: {list(analysis['top_performers'].keys())[:3]}")
                        print(f"  • 信号类型: {', '.join(analysis['signal_names'][:5])}...")

                        # 显示综合信号排名
                        if 'composite_signal' in self.enhanced_signals:
                            print(f"\n📈 综合信号排名 (前5名):")
                            composite = self.enhanced_signals['composite_signal'].sort_values(ascending=False)
                            for i, (etf, score) in enumerate(composite.head().items(), 1):
                                etf_name = self.etf_names.get(etf, etf) if self.etf_names else etf
                                print(f"  {i}. {etf_name} ({etf}): {score:.3f}")

                    # 生成信号建议
                    recommendations = self.simple_quant_signals.get_signal_recommendations(self.enhanced_signals)
                    if recommendations:
                        print(f"\n💡 量化信号建议:")
                        for rec in recommendations[:3]:
                            print(f"  • {rec}")
                    print("="*70)

                    # 显示主要信号
                    if 'composite_signal' in self.enhanced_signals:
                        print("\n📊 综合量化信号排名:")
                        composite_signal = self.enhanced_signals['composite_signal'].sort_values(ascending=False)
                        for etf, signal in composite_signal.items():
                            etf_name = self.etf_names.get(etf, etf) if self.etf_names else etf
                            print(f"  {etf_name} ({etf}): {signal:.3f}")

                    # 显示信号分析
                    if 'signal_normalized' in self.enhanced_signals:
                        print("\n📈 分项信号强度:")
                        signal_df = self.enhanced_signals['signal_normalized']
                        for signal_type in signal_df.columns:
                            print(f"\n  {signal_type}:")
                            for etf in signal_df.index:
                                signal_value = signal_df.loc[etf, signal_type]
                                etf_name = self.etf_names.get(etf, etf) if self.etf_names else etf
                                emoji = "📈" if signal_value > 0.5 else "📉" if signal_value < -0.5 else "➡️"
                                print(f"    {emoji} {etf_name}: {signal_value:.2f}")

                    # 计算信号表现
                    signal_performance = self.quant_signals._calculate_signal_performance(
                        self.enhanced_signals, self.returns
                    )

                    if signal_performance:
                        print("\n⚡ 信号历史表现:")
                        for metric, value in signal_performance.items():
                            print(f"  {metric}: {value:.4f}")

                    self.logger.info("✅ 高级量化指标分析完成")

            except Exception as e:
                self.logger.error(f"❌ 高级量化指标分析失败: {e}")
                self.enhanced_signals = {}

    def _run_enhanced_optimization(self) -> None:
        """运行增强投资组合优化"""
        with Timer("增强投资组合优化"):
            try:
                self.logger.info("🚀 开始增强投资组合优化...")

                if self.enhanced_signals:
                    # 准备价格数据
                    price_columns = [col for col in self.raw_data.columns if col not in ['trade_date', 'ts_code']]
                    prices = self.raw_data[['trade_date'] + price_columns].set_index('trade_date')

                    # 直接使用简化增强优化
                    enhanced_weights, enhanced_metrics = self.simple_enhanced_optimizer.optimize_with_signals(
                        self.returns, self.enhanced_signals
                    )
                    comparison = self.simple_enhanced_optimizer.compare_with_traditional(
                        self.returns, self.enhanced_signals
                    )

                    print("\n" + "="*70)
                    print("🚀 增强投资组合优化完成")
                    print("="*70)

                    # 显示增强优化结果
                    print(f"\n📊 增强优化指标:")
                    print(f"  • 夏普比率: {enhanced_metrics.get('sharpe_ratio', 0):.4f}")
                    print(f"  • 预期年化收益: {enhanced_metrics.get('portfolio_return', 0):.2%}")
                    print(f"  • 年化波动率: {enhanced_metrics.get('portfolio_volatility', 0):.2%}")
                    print(f"  • 集中度指数 (HHI): {enhanced_metrics.get('concentration_hhi', 0):.0f}")
                    print(f"  • 有效资产数量: {enhanced_metrics.get('effective_assets', 0):.1f}")
                    print(f"  • 分散化比率: {enhanced_metrics.get('diversification_ratio', 0):.3f}")

                    # 显示比较结果
                    if 'improvement' in comparison:
                        improvement = comparison['improvement']
                        print(f"\n📈 相比传统优化:")
                        print(f"  • 夏普比率提升: {improvement.get('sharpe_ratio_improvement', 0):+.4f}")
                        print(f"  • 夏普比率提升幅度: {improvement.get('sharpe_improvement_pct', 0):+.1f}%")
                        print(f"  • 收益变化: {improvement.get('return_change', 0):+.2%}")
                        print(f"  • 风险变化: {improvement.get('volatility_change', 0):+.2%}")

                    # 显示优化建议
                    recommendations = self.simple_enhanced_optimizer.get_optimization_recommendations(comparison)
                    if recommendations:
                        print(f"\n💡 优化建议:")
                        for rec in recommendations:
                            print(f"  {rec}")

                    print("="*70)

                    # 将权重数组转换为字典格式
                    enhanced_weights_dict = {}
                    for etf, weight in zip(self.config.etf_codes, enhanced_weights):
                        if weight > 0.001:  # 只保存有效权重
                            enhanced_weights_dict[etf] = float(weight)

                    self.enhanced_optimization_results = {
                        'enhanced_weights': enhanced_weights_dict,
                        'enhanced_metrics': enhanced_metrics,
                        'comparison': comparison,
                        'recommendations': self.enhanced_optimizer.get_optimization_recommendations(comparison)
                    }

                    # 显示增强优化结果
                    print("\n" + "="*70)
                    print("🚀 增强投资组合优化结果")
                    print("="*70)

                    print(f"\n📊 增强优化指标:")
                    print(f"  • 夏普比率: {enhanced_metrics.get('sharpe_ratio', 0):.4f}")
                    print(f"  • 预期年化收益: {enhanced_metrics.get('portfolio_return', 0):.2%}")
                    print(f"  • 年化波动率: {enhanced_metrics.get('portfolio_volatility', 0):.2%}")
                    print(f"  • 集中度指数 (HHI): {enhanced_metrics.get('concentration_hhi', 0):.0f}")
                    print(f"  • 有效资产数量: {enhanced_metrics.get('effective_assets', 0):.1f}")
                    print(f"  • 分散化比率: {enhanced_metrics.get('diversification_ratio', 0):.3f}")

                    print(f"\n⚖️ 增强优化权重分配:")
                    for etf, weight in zip(self.config.etf_codes, enhanced_weights):
                        if weight > 0.001:
                            etf_name = self.etf_names.get(etf, etf) if self.etf_names else etf
                            print(f"  • {etf_name} ({etf}): {weight:.2%}")

                    # 显示比较结果
                    if 'improvement' in comparison:
                        improvement = comparison['improvement']
                        print(f"\n📈 相比传统优化:")
                        print(f"  • 夏普比率提升: {improvement.get('sharpe_ratio_improvement', 0):+.4f}")
                        print(f"  • 夏普比率提升幅度: {improvement.get('sharpe_improvement_pct', 0):+.1f}%")
                        print(f"  • 收益变化: {improvement.get('return_change', 0):+.2%}")
                        print(f"  • 风险变化: {improvement.get('volatility_change', 0):+.2%}")

                    # 显示优化建议
                    if self.enhanced_optimization_results['recommendations']:
                        print(f"\n💡 优化建议:")
                        for rec in self.enhanced_optimization_results['recommendations']:
                            print(f"  {rec}")

                    self.logger.info("✅ 增强投资组合优化完成")

            except Exception as e:
                self.logger.error(f"❌ 增强投资组合优化失败: {e}")
                self.enhanced_optimization_results = {}

            # 生成增强可视化图表
            try:
                self.enhanced_charts = self.enhanced_visualizer.generate_all_enhanced_charts(
                    signals=self.enhanced_signals,
                    comparison=self.enhanced_optimization_results.get('comparison') if self.enhanced_optimization_results else None,
                    traditional_weights=self.optimal_weights,
                    enhanced_weights=self.enhanced_optimization_results.get('enhanced_weights') if self.enhanced_optimization_results else None,
                    etf_codes=self.config.etf_codes,
                    etf_names=self.etf_names
                )
                self.logger.info("✅ 增强可视化图表生成完成")
            except Exception as e:
                self.logger.error(f"❌ 增强可视化图表生成失败: {e}")
                self.enhanced_charts = []


def main():
    """主函数"""
    try:
        # 设置日志
        setup_logging("INFO")

        # 获取logger实例
        logger = logging.getLogger(__name__)

        # 创建并运行增强版分析器
        enhanced_optimizer = EnhancedETFSharpeOptimizer()
        enhanced_optimizer.run_analysis()

    except KeyboardInterrupt:
        logger.info("用户中断执行")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()