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

from src.config import get_config
from src.data_fetcher import get_data_fetcher
from src.data_processor import get_data_processor
from src.evaluator import get_portfolio_evaluator
from src.visualizer import get_visualizer
from src.utils import (
    setup_logging, save_results, print_welcome_banner,
    print_summary_table, Timer
)

# 尝试导入优化器，优先使用scipy版本
try:
    from src.portfolio_optimizer_scipy import get_portfolio_optimizer_scipy as get_portfolio_optimizer
    OPTIMIZER_TYPE = "scipy"
except ImportError:
    try:
        from src.portfolio_optimizer import get_portfolio_optimizer
        OPTIMIZER_TYPE = "cvxpy"
    except ImportError:
        raise ImportError("没有可用的优化器，请安装scipy或cvxpy")


class ETFSharpeOptimizer:
    """ETF夏普比率最优组合研究主类"""
    
    def __init__(self):
        """初始化主类"""
        self.config = get_config()
        self.data_fetcher = get_data_fetcher()
        self.data_processor = get_data_processor(self.config.trading_days)
        self.portfolio_optimizer = get_portfolio_optimizer(self.config.risk_free_rate)
        self.evaluator = get_portfolio_evaluator(self.config.trading_days, self.config.risk_free_rate)
        self.visualizer = get_visualizer(self.config.output_dir)
        
        # 存储中间结果
        self.raw_data = None
        self.returns = None
        self.annual_mean = None
        self.cov_matrix = None
        self.optimal_weights = None
        self.max_sharpe_ratio = None
        self.portfolio_returns = None
        self.metrics = None
        
        # 记录使用的优化器类型
        logging.info(f"使用优化器: {OPTIMIZER_TYPE}")
    
    def run_analysis(self) -> None:
        """运行完整的分析流程"""
        print_welcome_banner()
        
        try:
            with Timer("完整分析流程"):
                # 1. 数据获取
                self._fetch_data()
                
                # 2. 数据处理
                self._process_data()
                
                # 3. 组合优化
                self._optimize_portfolio()
                
                # 4. 计算评估指标
                self._evaluate_portfolio()
                
                # 5. 生成可视化
                self._generate_visualizations()
                
                # 6. 保存结果
                self._save_results()
                
                # 7. 打印报告
                self._print_final_report()
            
            logging.info("分析完成！")
            
        except Exception as e:
            logging.error(f"分析失败: {e}")
            sys.exit(1)
    
    def _fetch_data(self) -> None:
        """获取数据"""
        with Timer("数据获取"):
            self.raw_data = self.data_fetcher.fetch_etf_data()
            logging.info(f"获取到 {len(self.raw_data)} 个交易日数据")
    
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
                self.metrics, self.optimal_weights, self.config.etf_codes
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
                portfolio_returns=self.portfolio_returns
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
                }
            }
            
            save_results(results, "optimization_results.json")
    
    def _print_final_report(self) -> None:
        """打印最终报告"""
        print("\n" + "="*80)
        print("🎯 ETF夏普比率最优组合研究 - 最终报告")
        print("="*80)
        
        print(f"\n📅 分析期间: {self.config.start_date} 至 {self.config.end_date}")
        print(f"📊 分析标的: {', '.join(self.config.etf_codes)}")
        print(f"💰 无风险利率: {self.config.risk_free_rate:.2%}")
        
        print(f"\n🏆 最优组合表现:")
        print(f"  • 最大夏普比率: {self.max_sharpe_ratio:.4f}")
        print(f"  • 年化收益率: {self.metrics['annual_return']:.2%}")
        print(f"  • 年化波动率: {self.metrics['annual_volatility']:.2%}")
        print(f"  • 最大回撤: {self.metrics['max_drawdown']:.2%}")
        
        print(f"\n⚖️ 最优权重分配:")
        for etf, weight in zip(self.config.etf_codes, self.optimal_weights):
            if weight > 0.001:  # 只显示权重大于0.1%的ETF
                print(f"  • {etf}: {weight:.2%}")
        
        print(f"\n📈 可视化图表:")
        print(f"  • 累计收益对比图: outputs/cumulative_returns.png")
        print(f"  • 有效前沿图: outputs/efficient_frontier.png")
        print(f"  • 权重饼图: outputs/portfolio_weights.png")
        print(f"  • 收益率分布图: outputs/returns_distribution.png")
        
        print(f"\n💾 数据文件:")
        print(f"  • 详细结果: outputs/optimization_results.json")
        print(f"  • 运行日志: etf_optimizer.log")
        
        print("\n" + "="*80)
        print("✅ 分析完成！所有结果已保存到 outputs/ 目录")
        print("="*80)


def main():
    """主函数"""
    try:
        # 设置日志
        setup_logging("INFO")
        
        # 创建并运行分析器
        optimizer = ETFSharpeOptimizer()
        optimizer.run_analysis()
        
    except KeyboardInterrupt:
        logging.info("用户中断执行")
        sys.exit(0)
    except Exception as e:
        logging.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()