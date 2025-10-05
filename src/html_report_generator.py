"""
HTML报告生成模块
创建精美的专业HTML分析报告
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import base64
from pathlib import Path

logger = logging.getLogger(__name__)


class HTMLReportGenerator:
    """HTML报告生成器"""

    def __init__(self, output_dir: str = "outputs"):
        """
        初始化HTML报告生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """确保输出目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)

    def _encode_image_base64(self, image_path: str) -> Optional[str]:
        """
        将图片编码为base64字符串

        Args:
            image_path: 图片路径

        Returns:
            base64编码的图片字符串
        """
        try:
            full_path = os.path.join(self.output_dir, image_path)
            if os.path.exists(full_path):
                with open(full_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            return None
        except Exception as e:
            logger.warning(f"图片编码失败 {image_path}: {e}")
            return None

    def _get_css_styles(self) -> str:
        """获取CSS样式"""
        return """
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }

            .header {
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 40px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }

            .header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
                opacity: 0.3;
            }

            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 700;
                position: relative;
                z-index: 1;
            }

            .header p {
                font-size: 1.2em;
                opacity: 0.9;
                position: relative;
                z-index: 1;
            }

            .nav {
                background: #f8f9fa;
                padding: 20px 40px;
                border-bottom: 1px solid #e9ecef;
            }

            .nav ul {
                list-style: none;
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
            }

            .nav a {
                color: #495057;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 8px;
                transition: all 0.3s ease;
                font-weight: 500;
            }

            .nav a:hover {
                background: #007bff;
                color: white;
                transform: translateY(-2px);
            }

            .content {
                padding: 40px;
            }

            .section {
                margin-bottom: 60px;
                opacity: 0;
                animation: fadeInUp 0.8s ease forwards;
            }

            .section:nth-child(1) { animation-delay: 0.2s; }
            .section:nth-child(2) { animation-delay: 0.4s; }
            .section:nth-child(3) { animation-delay: 0.6s; }
            .section:nth-child(4) { animation-delay: 0.8s; }
            .section:nth-child(5) { animation-delay: 1.0s; }

            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .section h2 {
                font-size: 2em;
                margin-bottom: 20px;
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .section h3 {
                font-size: 1.5em;
                margin: 30px 0 15px 0;
                color: #34495e;
            }

            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }

            .metric-card {
                background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                transform: translateY(0);
                transition: all 0.3s ease;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }

            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 30px rgba(0,0,0,0.2);
            }

            .metric-card.positive {
                background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
            }

            .metric-card.negative {
                background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
            }

            .metric-card.warning {
                background: linear-gradient(135deg, #fdcb6e 0%, #f39c12 100%);
            }

            .metric-value {
                font-size: 2.5em;
                font-weight: 700;
                margin-bottom: 5px;
            }

            .metric-label {
                font-size: 1em;
                opacity: 0.9;
            }

            .chart-container {
                background: white;
                border-radius: 15px;
                padding: 30px;
                margin: 20px 0;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                border: 1px solid #e9ecef;
            }

            .chart-container img {
                width: 100%;
                height: auto;
                border-radius: 10px;
            }

            .chart-title {
                font-size: 1.3em;
                font-weight: 600;
                margin-bottom: 20px;
                color: #2c3e50;
                text-align: center;
            }

            .table-responsive {
                overflow-x: auto;
                margin: 20px 0;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }

            table {
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 10px;
                overflow: hidden;
            }

            th, td {
                padding: 15px;
                text-align: left;
                border-bottom: 1px solid #e9ecef;
            }

            th {
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                font-weight: 600;
                font-size: 0.95em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            tr:hover {
                background: #f8f9fa;
            }

            tr:last-child td {
                border-bottom: none;
            }

            .highlight-box {
                background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%);
                border-left: 5px solid #27ae60;
                padding: 20px;
                margin: 20px 0;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }

            .warning-box {
                background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
                border-left: 5px solid #f39c12;
                padding: 20px;
                margin: 20px 0;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }

            .risk-indicator {
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .risk-low {
                background: #d4edda;
                color: #155724;
            }

            .risk-medium {
                background: #fff3cd;
                color: #856404;
            }

            .risk-high {
                background: #f8d7da;
                color: #721c24;
            }

            .progress-bar {
                width: 100%;
                height: 20px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
                margin: 10px 0;
            }

            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #3498db 0%, #2ecc71 100%);
                transition: width 1s ease;
                border-radius: 10px;
            }

            .footer {
                background: #2c3e50;
                color: white;
                padding: 30px;
                text-align: center;
            }

            .footer p {
                margin: 5px 0;
                opacity: 0.8;
            }

            .collapsible {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 10px;
                margin: 10px 0;
                overflow: hidden;
            }

            .collapsible-header {
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                padding: 15px 20px;
                cursor: pointer;
                font-weight: 600;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .collapsible-content {
                padding: 20px;
                display: none;
            }

            .collapsible.active .collapsible-content {
                display: block;
            }

            @media (max-width: 768px) {
                .container {
                    margin: 10px;
                    border-radius: 15px;
                }

                .header {
                    padding: 30px 20px;
                }

                .header h1 {
                    font-size: 2em;
                }

                .content {
                    padding: 20px;
                }

                .metrics-grid {
                    grid-template-columns: 1fr;
                }

                .nav ul {
                    flex-direction: column;
                    gap: 10px;
                }

                table {
                    font-size: 0.9em;
                }

                th, td {
                    padding: 10px;
                }
            }

            .print-only {
                display: none;
            }

            @media print {
                .print-only {
                    display: block;
                }

                .nav {
                    display: none;
                }

                .container {
                    box-shadow: none;
                    border: 1px solid #ddd;
                }
            }
        </style>
        """

    def _get_javascript(self) -> str:
        """获取JavaScript代码"""
        return """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // 平滑滚动
                document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                    anchor.addEventListener('click', function (e) {
                        e.preventDefault();
                        document.querySelector(this.getAttribute('href')).scrollIntoView({
                            behavior: 'smooth'
                        });
                    });
                });

                // 折叠面板功能
                document.querySelectorAll('.collapsible-header').forEach(header => {
                    header.addEventListener('click', function() {
                        const collapsible = this.parentElement;
                        collapsible.classList.toggle('active');
                    });
                });

                // 数字动画效果
                function animateValue(element, start, end, duration) {
                    let startTimestamp = null;
                    const step = (timestamp) => {
                        if (!startTimestamp) startTimestamp = timestamp;
                        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                        const value = Math.floor(progress * (end - start) + start);
                        element.textContent = value.toLocaleString();
                        if (progress < 1) {
                            window.requestAnimationFrame(step);
                        }
                    };
                    window.requestAnimationFrame(step);
                }

                // 生成打印友好版本
                document.getElementById('printBtn').addEventListener('click', function() {
                    window.print();
                });

                // 响应式图表容器
                function resizeCharts() {
                    document.querySelectorAll('.chart-container img').forEach(img => {
                        img.style.maxHeight = '600px';
                        img.style.objectFit = 'contain';
                    });
                }

                resizeCharts();
                window.addEventListener('resize', resizeCharts);
            });
        </script>
        """

    def _generate_header(self, config: Dict[str, Any]) -> str:
        """生成报告头部"""
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

        return f"""
        <div class="header">
            <h1>📊 ETF投资组合优化分析报告</h1>
            <p>基于夏普比率最大化策略的专业投资分析</p>
            <p>分析时间: {current_time}</p>
        </div>
        """

    def _generate_navigation(self) -> str:
        """生成导航菜单"""
        return """
        <div class="nav">
            <ul>
                <li><a href="#overview">📋 投资概览</a></li>
                <li><a href="#performance">📈 绩效指标</a></li>
                <li><a href="#portfolio">⚖️ 组合配置</a></li>
                <li><a href="#correlation">🔗 相关性分析</a></li>
                <li><a href="#risk">🔒 风险分析</a></li>
                <li><a href="#charts">📊 可视化分析</a></li>
                <li><a href="#recommendations">💡 投资建议</a></li>
            </ul>
        </div>
        """

    def _generate_overview_section(self, config: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """生成概览部分"""
        return f"""
        <div id="overview" class="section">
            <h2>📋 投资概览</h2>

            <div class="metrics-grid">
                <div class="metric-card positive">
                    <div class="metric-value">{metrics.get('annual_return', 0):.2%}</div>
                    <div class="metric-label">预期年化收益率</div>
                </div>

                <div class="metric-card warning">
                    <div class="metric-value">{metrics.get('annual_volatility', 0):.2%}</div>
                    <div class="metric-label">年化波动率</div>
                </div>

                <div class="metric-card positive">
                    <div class="metric-value">{metrics.get('sharpe_ratio', 0):.4f}</div>
                    <div class="metric-label">夏普比率</div>
                </div>

                <div class="metric-card negative">
                    <div class="metric-value">{metrics.get('max_drawdown', 0):.2%}</div>
                    <div class="metric-label">最大回撤</div>
                </div>
            </div>

            <div class="highlight-box">
                <h3>📊 分析基本信息</h3>
                <table>
                    <tr><td><strong>分析期间</strong></td><td>{config.get('start_date', '')} 至 {config.get('end_date', '')}</td></tr>
                    <tr><td><strong>投资标的</strong></td><td>{', '.join(config.get('etf_codes', []))}</td></tr>
                    <tr><td><strong>无风险利率</strong></td><td>{config.get('risk_free_rate', 0):.2%}</td></tr>
                    <tr><td><strong>年交易天数</strong></td><td>{config.get('trading_days', 252)}天</td></tr>
                </table>
            </div>
        </div>
        """

    def _generate_performance_section(self, metrics: Dict[str, Any]) -> str:
        """生成绩效指标部分"""
        def _get_metric_card(value: float, label: str, threshold_good: float = None, threshold_bad: float = None) -> str:
            if threshold_good is not None and threshold_bad is not None:
                if value >= threshold_good:
                    card_class = "positive"
                elif value <= threshold_bad:
                    card_class = "negative"
                else:
                    card_class = "warning"
            else:
                card_class = "positive"

            return f"""
            <div class="metric-card {card_class}">
                <div class="metric-value">{value:.4f}</div>
                <div class="metric-label">{label}</div>
            </div>
            """

        return f"""
        <div id="performance" class="section">
            <h2>📈 绩效指标详情</h2>

            <div class="metrics-grid">
                {_get_metric_card(metrics.get('sharpe_ratio', 0), "夏普比率", 1.0, 0.5)}
                {_get_metric_card(metrics.get('calmar_ratio', 0), "Calmar比率", 1.0, 0.5)}
                {_get_metric_card(metrics.get('sortino_ratio', 0), "索提诺比率", 1.0, 0.5)}
                {_get_metric_card(metrics.get('skewness', 0), "偏度", 0, -0.5)}
            </div>

            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>指标</th>
                            <th>数值</th>
                            <th>说明</th>
                            <th>评价</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>年化收益率</td>
                            <td>{metrics.get('annual_return', 0):.2%}</td>
                            <td>投资组合的预期年化收益</td>
                            <td>{'优秀' if metrics.get('annual_return', 0) > 0.1 else '良好' if metrics.get('annual_return', 0) > 0.05 else '一般'}</td>
                        </tr>
                        <tr>
                            <td>年化波动率</td>
                            <td>{metrics.get('annual_volatility', 0):.2%}</td>
                            <td>收益率的标准差，衡量风险</td>
                            <td>{'较低' if metrics.get('annual_volatility', 0) < 0.15 else '适中' if metrics.get('annual_volatility', 0) < 0.25 else '较高'}</td>
                        </tr>
                        <tr>
                            <td>夏普比率</td>
                            <td>{metrics.get('sharpe_ratio', 0):.4f}</td>
                            <td>单位超额收益的性价比</td>
                            <td>{'优秀' if metrics.get('sharpe_ratio', 0) > 1.5 else '良好' if metrics.get('sharpe_ratio', 0) > 1.0 else '一般'}</td>
                        </tr>
                        <tr>
                            <td>最大回撤</td>
                            <td>{metrics.get('max_drawdown', 0):.2%}</td>
                            <td>历史上最大亏损幅度</td>
                            <td>{'较小' if abs(metrics.get('max_drawdown', 0)) < 0.1 else '适中' if abs(metrics.get('max_drawdown', 0)) < 0.2 else '较大'}</td>
                        </tr>
                        <tr>
                            <td>Calmar比率</td>
                            <td>{metrics.get('calmar_ratio', 0):.4f}</td>
                            <td>年化收益与最大回撤的比值</td>
                            <td>{'优秀' if metrics.get('calmar_ratio', 0) > 1.0 else '良好' if metrics.get('calmar_ratio', 0) > 0.5 else '一般'}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        """

    def _generate_portfolio_section(self, optimal_weights: List[float], etf_codes: List[str],
                                  annual_mean: Dict[str, float], etf_names: Dict[str, str]) -> str:
        """生成投资组合配置部分"""

        weights_table = ""
        for etf, weight in zip(etf_codes, optimal_weights):
            if weight > 0.001:
                expected_return = annual_mean.get(etf, 0)
                # 获取ETF中文名称，如果没有则使用代码
                display_name = etf_names.get(etf, etf) if etf_names else etf
                weights_table += f"""
                <tr>
                    <td>{display_name}<br><small style="color: #666;">({etf})</small></td>
                    <td>{weight:.2%}</td>
                    <td>{expected_return:.2%}</td>
                    <td>-</td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {weight * 100}%"></div>
                        </div>
                    </td>
                </tr>
                """

        return f"""
        <div id="portfolio" class="section">
            <h2>⚖️ 最优投资组合配置</h2>

            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>ETF名称</th>
                            <th>权重</th>
                            <th>预期年化收益</th>
                            <th>年化波动率</th>
                            <th>权重分布</th>
                        </tr>
                    </thead>
                    <tbody>
                        {weights_table}
                    </tbody>
                </table>
            </div>

            <div class="collapsible active">
                <div class="collapsible-header">
                    <span>📊 配置详情</span>
                    <span>▼</span>
                </div>
                <div class="collapsible-content">
                    <div class="highlight-box">
                        <h4>组合特点</h4>
                        <ul>
                            <li><strong>分散化程度：</strong>{len([w for w in optimal_weights if w > 0.001])}个ETF标的</li>
                            <li><strong>最大权重：</strong>{max(optimal_weights):.2%}</li>
                            <li><strong>最小权重：</strong>{min([w for w in optimal_weights if w > 0.001] or [0]):.2%}</li>
                            <li><strong>集中度(HHI)：</strong>{sum([w**2 for w in optimal_weights]):.4f}</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        """

    def _generate_correlation_section(self, correlation_analysis: Optional[Dict[str, Any]] = None,
                                  etf_names: Optional[Dict[str, str]] = None) -> str:
        """生成相关性分析部分"""
        if not correlation_analysis:
            return """
            <div id="correlation" class="section">
                <h2>🔗 相关性分析</h2>
                <div class="warning-box">
                    <p>相关性分析数据暂不可用，建议在进行实际投资前进行详细的相关性评估。</p>
                </div>
            </div>
            """

        risk_analysis = correlation_analysis.get('risk_analysis', {})
        summary = correlation_analysis.get('analysis_summary', {})
        optimization_suggestions = correlation_analysis.get('optimization_suggestions', [])

        risk_assessment = risk_analysis.get('risk_assessment', {})
        risk_level = risk_assessment.get('risk_level', '未知')
        diversification_score = summary.get('diversification_score', 0)
        avg_correlation = summary.get('average_correlation', 0)
        high_corr_pairs = summary.get('high_correlation_pairs', 0)
        moderate_corr_pairs = summary.get('moderate_correlation_pairs', 0)

        # 确定风险等级样式
        risk_class = "risk-low" if risk_level in ["低风险"] else "risk-medium" if risk_level in ["中等风险"] else "risk-high"

        # 生成高相关性ETF对表格
        high_corr_table = ""
        if risk_analysis.get('high_correlation_pairs'):
            high_corr_table = """
            <h4>⚠️ 高相关性ETF对</h4>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>ETF名称1</th>
                            <th>ETF名称2</th>
                            <th>相关系数</th>
                            <th>风险等级</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for pair in risk_analysis.get('high_correlation_pairs', []):
                etf1 = pair.get('etf1', '')
                etf2 = pair.get('etf2', '')
                # 获取ETF中文名称
                etf1_name = etf_names.get(etf1, etf1) if etf_names else etf1
                etf2_name = etf_names.get(etf2, etf2) if etf_names else etf2

                high_corr_table += f"""
                        <tr>
                            <td>{etf1_name}<br><small style="color: #666;">({etf1})</small></td>
                            <td>{etf2_name}<br><small style="color: #666;">({etf2})</small></td>
                            <td>{pair.get('correlation', 0):.3f}</td>
                            <td><span class="risk-indicator {risk_class}">{pair.get('risk_level', '')}</span></td>
                        </tr>
                """
            high_corr_table += """
                    </tbody>
                </table>
            </div>
            """

        # 生成优化建议列表
        suggestions_html = ""
        for i, suggestion in enumerate(optimization_suggestions[:5], 1):
            suggestions_html += f"<li>{suggestion}</li>"

  
        return f"""
        <div id="correlation" class="section">
            <h2>🔗 相关性分析</h2>

            <div class="metrics-grid">
                <div class="metric-card {risk_class.replace('risk-', '')}">
                    <div class="metric-value">{risk_level}</div>
                    <div class="metric-label">相关性风险等级</div>
                </div>

                <div class="metric-card positive">
                    <div class="metric-value">{diversification_score:.1f}</div>
                    <div class="metric-label">分散化评分</div>
                </div>

                <div class="metric-card warning">
                    <div class="metric-value">{avg_correlation:.3f}</div>
                    <div class="metric-label">平均相关性</div>
                </div>

                <div class="metric-card negative">
                    <div class="metric-value">{high_corr_pairs}</div>
                    <div class="metric-label">高相关性ETF对</div>
                </div>
            </div>

            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>指标</th>
                            <th>数值</th>
                            <th>说明</th>
                            <th>评价</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>平均相关性</td>
                            <td>{avg_correlation:.3f}</td>
                            <td>所有ETF对的相关系数平均值</td>
                            <td>{'较低' if avg_correlation < 0.3 else '适中' if avg_correlation < 0.5 else '较高'}</td>
                        </tr>
                        <tr>
                            <td>高相关性ETF对</td>
                            <td>{high_corr_pairs}对</td>
                            <td>相关系数≥0.7的ETF对数</td>
                            <td>{'较少' if high_corr_pairs == 0 else '一般' if high_corr_pairs <= 2 else '较多'}</td>
                        </tr>
                        <tr>
                            <td>中等相关性ETF对</td>
                            <td>{moderate_corr_pairs}对</td>
                            <td>相关系数在0.5-0.7之间的ETF对数</td>
                            <td>{'较少' if moderate_corr_pairs <= 2 else '一般' if moderate_corr_pairs <= 5 else '较多'}</td>
                        </tr>
                        <tr>
                            <td>分散化评分</td>
                            <td>{diversification_score:.1f}/100</td>
                            <td>基于相关性的分散化程度评分</td>
                            <td>{'优秀' if diversification_score >= 70 else '良好' if diversification_score >= 50 else '一般'}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            {high_corr_table}

            <div class="collapsible">
                <div class="collapsible-header">
                    <span>🎯 相关性风险说明</span>
                    <span>▼</span>
                </div>
                <div class="collapsible-content">
                    <div class="warning-box">
                        <h4>⚠️ 相关性风险要点</h4>
                        <ul>
                            <li><strong>高相关性风险：</strong>相关性过高会降低分散化效果，增加系统性风险</li>
                            <li><strong>市场冲击：</strong>在市场剧烈波动时，相关性会上升，分散化效果减弱</li>
                            <li><strong>集中风险：</strong>高相关性的ETF可能属于同一行业或主题，面临共同风险</li>
                            <li><strong>波动放大：</strong>相关性高的组合可能表现出更大的波动性</li>
                        </ul>
                    </div>

                    <div class="highlight-box">
                        <h4>💡 优化建议</h4>
                        <ol>
                            {suggestions_html}
                        </ol>
                    </div>
                </div>
            </div>
        </div>
        """

    def _generate_risk_section(self, risk_report: Optional[Dict[str, Any]] = None) -> str:
        """生成风险分析部分"""
        if not risk_report:
            return """
            <div id="risk" class="section">
                <h2>🔒 风险分析</h2>
                <div class="warning-box">
                    <p>风险分析数据暂不可用，建议在进行实际投资前进行更详细的风险评估。</p>
                </div>
            </div>
            """

        risk_rating = risk_report.get('risk_rating', {}).get('overall_risk', '未知')
        var_95 = risk_report.get('var_cvar_analysis', {}).get(0.95, {}).get('var_historical', 0)

        risk_class = "risk-low" if risk_rating in ["低", "较低"] else "risk-medium" if risk_rating in ["中等", "中"] else "risk-high"

        return f"""
        <div id="risk" class="section">
            <h2>🔒 风险分析</h2>

            <div class="metrics-grid">
                <div class="metric-card {risk_class.replace('risk-', '')}">
                    <div class="metric-value">{risk_rating}</div>
                    <div class="metric-label">综合风险评级</div>
                </div>

                <div class="metric-card warning">
                    <div class="metric-value">{var_95:.2%}</div>
                    <div class="metric-label">95% VaR</div>
                </div>
            </div>

            <div class="warning-box">
                <h3>⚠️ 风险提示</h3>
                <ul>
                    <li>历史业绩不代表未来表现，投资有风险，决策需谨慎</li>
                    <li>建议根据个人风险承受能力调整投资配置</li>
                    <li>定期关注市场变化，适时调整投资策略</li>
                    <li>分散投资有助于降低非系统性风险</li>
                </ul>
            </div>
        </div>
        """

    def _generate_charts_section(self, correlation_analysis: Optional[Dict[str, Any]] = None) -> str:
        """生成可视化图表部分"""
        charts = [
            ("cumulative_returns.png", "累计收益对比图"),
            ("efficient_frontier.png", "有效前沿图"),
            ("portfolio_weights.png", "投资组合权重分布"),
            ("returns_distribution.png", "收益率分布图")
        ]

        # 如果有相关性分析，添加相关性热力图
        if correlation_analysis and correlation_analysis.get('heatmap_path'):
            charts.append(("correlation_heatmap.png", "ETF相关性热力图"))

        charts_html = ""
        for chart_file, chart_title in charts:
            encoded_image = self._encode_image_base64(chart_file)
            if encoded_image:
                charts_html += f"""
                <div class="chart-container">
                    <div class="chart-title">{chart_title}</div>
                    <img src="data:image/png;base64,{encoded_image}" alt="{chart_title}">
                </div>
                """
            else:
                charts_html += f"""
                <div class="chart-container">
                    <div class="chart-title">{chart_title}</div>
                    <p style="text-align: center; color: #666; padding: 40px;">
                        图表生成失败或文件不存在
                    </p>
                </div>
                """

        return f"""
        <div id="charts" class="section">
            <h2>📊 可视化分析</h2>
            {charts_html}
        </div>
        """

    def _generate_recommendations_section(self, investment_analysis: Optional[Dict[str, Any]] = None) -> str:
        """生成投资建议部分"""
        recommendations = [
            "建议定期（如每季度）评估投资组合表现，根据市场变化调整配置",
            "关注宏观经济环境变化，特别是利率政策对ETF价格的影响",
            "在市场剧烈波动时保持冷静，避免情绪化决策",
            "考虑分批建仓或定投策略，降低择时风险",
            "设置合理的止损和止盈点，控制风险锁定收益"
        ]

        if investment_analysis and investment_analysis.get('recommendations'):
            recommendations = investment_analysis['recommendations'][:5]

        rec_html = ""
        for i, rec in enumerate(recommendations, 1):
            rec_html += f"<li>{rec}</li>"

        growth_proj = investment_analysis.get('growth_projection', {}) if investment_analysis else {}

        return f"""
        <div id="recommendations" class="section">
            <h2>💡 投资建议</h2>

            <div class="highlight-box">
                <h3>🎯 核心建议</h3>
                <ol>
                    {rec_html}
                </ol>
            </div>

            {f'''
            <div class="collapsible">
                <div class="collapsible-header">
                    <span>📈 增长预测</span>
                    <span>▼</span>
                </div>
                <div class="collapsible-content">
                    <table>
                        <tr><td><strong>5年预期价值（100万初始）</strong></td><td>{growth_proj.get("final_value_statistics", {}).get("mean", 0):,.0f}元</td></tr>
                        <tr><td><strong>中位数价值</strong></td><td>{growth_proj.get("final_value_statistics", {}).get("median", 0):,.0f}元</td></tr>
                        <tr><td><strong>成功率（>100万）</strong></td><td>{growth_proj.get("success_probability", 0):.1%}</td></tr>
                    </table>
                </div>
            </div>
            ''' if growth_proj else ''}

            <div class="warning-box">
                <h3>⚠️ 重要声明</h3>
                <p>本报告基于历史数据分析生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。在进行实际投资前，请咨询专业的投资顾问，根据个人情况制定投资策略。</p>
            </div>
        </div>
        """

    def _generate_footer(self) -> str:
        """生成页脚"""
        current_time = datetime.now().strftime("%Y年%m月%d日")
        return f"""
        <div class="footer">
            <p><strong>ETF夏普比率最优组合研究系统</strong></p>
            <p>专业量化投资分析工具 | 基于现代投资组合理论</p>
            <p>报告生成时间: {current_time}</p>
            <p style="margin-top: 20px;">
                <button id="printBtn" style="background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                    🖨️ 打印报告
                </button>
            </p>
        </div>
        """

    def generate_html_report(self,
                           config: Dict[str, Any],
                           optimization_results: Dict[str, Any],
                           performance_metrics: Dict[str, Any],
                           risk_report: Optional[Dict[str, Any]] = None,
                           investment_analysis: Optional[Dict[str, Any]] = None,
                           correlation_analysis: Optional[Dict[str, Any]] = None,
                           etf_names: Optional[Dict[str, str]] = None) -> str:
        """
        生成完整的HTML报告

        Args:
            config: 配置信息
            optimization_results: 优化结果
            performance_metrics: 绩效指标
            risk_report: 风险分析报告（可选）
            investment_analysis: 投资分析（可选）
            correlation_analysis: 相关性分析（可选）
            etf_names: ETF代码到中文名称的映射字典（可选）

        Returns:
            生成的HTML文件路径
        """
        logger.info("📝 开始生成HTML分析报告...")

        try:
            # 提取数据
            optimal_weights = list(optimization_results.get('optimal_weights', {}).values())
            etf_codes = list(optimization_results.get('optimal_weights', {}).keys())

            # 构建HTML内容
            html_content = f"""
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ETF投资组合优化分析报告</title>
                {self._get_css_styles()}
            </head>
            <body>
                <div class="container">
                    {self._generate_header(config)}
                    {self._generate_navigation()}
                    <div class="content">
                        {self._generate_overview_section(config, performance_metrics)}
                        {self._generate_performance_section(performance_metrics)}
                        {self._generate_portfolio_section(optimal_weights, etf_codes,
                                                        optimization_results.get('data_summary', {}).get('etf_annual_returns', {}),
                                                        etf_names or {})}
                        {self._generate_correlation_section(correlation_analysis, etf_names)}
                        {self._generate_risk_section(risk_report)}
                        {self._generate_charts_section(correlation_analysis)}
                        {self._generate_recommendations_section(investment_analysis)}
                    </div>
                    {self._generate_footer()}
                </div>
                {self._get_javascript()}
            </body>
            </html>
            """

            # 保存HTML文件
            report_path = os.path.join(self.output_dir, "etf_optimization_report.html")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"✅ HTML报告已生成: {report_path}")
            return report_path

        except Exception as e:
            logger.error(f"❌ HTML报告生成失败: {e}")
            raise


def get_html_report_generator(output_dir: str = "outputs") -> HTMLReportGenerator:
    """获取HTML报告生成器实例"""
    return HTMLReportGenerator(output_dir)