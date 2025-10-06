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

    def _get_enhanced_css_styles(self) -> str:
        """获取增强CSS样式"""
        base_css = self._get_css_styles()

        enhanced_css = """
        <style>
            /* 增强量化信号样式 */
            .signals-ranking {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }

            .signal-item {
                display: flex;
                align-items: center;
                padding: 15px;
                border-radius: 10px;
                font-weight: 500;
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .signal-strong {
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
            }

            .signal-weak {
                background: linear-gradient(135deg, #f44336, #d32f2f);
                color: white;
            }

            .signal-neutral {
                background: linear-gradient(135deg, #FF9800, #F57C00);
                color: white;
            }

            .signal-emoji {
                font-size: 1.5em;
                margin-right: 10px;
            }

            .signal-etf {
                flex: 1;
                font-size: 0.9em;
            }

            .signal-value {
                font-size: 1.1em;
                font-weight: bold;
            }

            /* 增强优化结果样式 */
            .comparison-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }

            .comparison-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #3498db;
                transition: all 0.3s ease;
            }

            .comparison-value.positive {
                color: #28a745;
            }

            .comparison-value.negative {
                color: #dc3545;
            }

            /* 建议列表样式 */
            .recommendations-list {
                list-style: none;
                padding: 0;
            }

            .recommendations-list li {
                padding: 12px 15px;
                margin: 8px 0;
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                border-left: 4px solid #17a2b8;
                border-radius: 5px;
                position: relative;
                transition: all 0.3s ease;
            }

            .recommendations-list li::before {
                content: "💡";
                margin-right: 10px;
            }

            /* 方法论介绍样式 */
            .methodology-box {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
                border-left: 5px solid #3498db;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            }

            .methodology-content h4 {
                color: #2c3e50;
                margin: 25px 0 15px 0;
                font-size: 1.3em;
                border-bottom: 2px solid #3498db;
                padding-bottom: 8px;
            }

            .methodology-content p {
                margin-bottom: 15px;
                line-height: 1.7;
            }

            .methodology-content ul {
                margin-left: 20px;
                margin-bottom: 15px;
            }

            .methodology-content li {
                margin-bottom: 8px;
            }

            /* 信号维度卡片 */
            .signal-dimensions {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }

            .dimension-card {
                display: flex;
                align-items: flex-start;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }

            .dimension-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            }

            .dimension-icon {
                font-size: 2em;
                margin-right: 15px;
                margin-top: 5px;
            }

            .dimension-content h5 {
                color: #34495e;
                margin-bottom: 8px;
                font-size: 1.1em;
            }

            .dimension-content p {
                color: #7f8c8d;
                margin: 0;
                font-size: 0.95em;
            }

            /* 对比方法卡片 */
            .comparison-methodology {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin: 25px 0;
            }

            .method-card {
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }

            .method-card.traditional {
                background: linear-gradient(135deg, #e8f4f8, #d1e9f0);
                border-left: 4px solid #5dade2;
            }

            .method-card.enhanced {
                background: linear-gradient(135deg, #f4e8ff, #e8d5f0);
                border-left: 4px solid #af7ac5;
            }

            .method-card h5 {
                margin-bottom: 15px;
                font-size: 1.2em;
                color: #2c3e50;
            }

            .method-card ul {
                list-style: none;
                padding: 0;
            }

            .method-card li {
                padding: 8px 0;
                border-bottom: 1px solid rgba(0,0,0,0.1);
                position: relative;
                padding-left: 20px;
            }

            .method-card li:before {
                content: "•";
                position: absolute;
                left: 0;
                color: #3498db;
                font-weight: bold;
            }

            /* 处理流程步骤 */
            .signal-adjustment-process {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin: 30px 0;
                flex-wrap: wrap;
                gap: 15px;
            }

            .process-step {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                flex: 1;
                min-width: 200px;
                text-align: center;
            }

            .step-number {
                display: inline-block;
                width: 35px;
                height: 35px;
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white;
                border-radius: 50%;
                line-height: 35px;
                font-weight: bold;
                margin-bottom: 10px;
            }

            .step-content h5 {
                margin-bottom: 8px;
                color: #2c3e50;
            }

            .process-arrow {
                font-size: 1.5em;
                color: #3498db;
                font-weight: bold;
            }

            /* 数学公式样式 */
            .optimization-formula {
                background: white;
                padding: 25px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #e74c3c;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            }

            .formula {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 15px 0;
                font-family: 'Courier New', monospace;
            }

            .formula p {
                margin: 10px 0;
                font-size: 1.1em;
            }

            /* 风险约束样式 */
            .risk-constraints {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }

            .constraint-item {
                display: flex;
                align-items: center;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }

            .constraint-item:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 15px rgba(0,0,0,0.15);
            }

            .constraint-icon {
                font-size: 1.8em;
                margin-right: 15px;
            }

            .constraint-content h5 {
                margin-bottom: 5px;
                color: #2c3e50;
            }

            .constraint-content p {
                margin: 0;
                color: #7f8c8d;
                font-size: 0.95em;
            }

            /* 响应式设计 */
            @media (max-width: 768px) {
                .signal-dimensions {
                    grid-template-columns: 1fr;
                }

                .comparison-methodology {
                    grid-template-columns: 1fr;
                }

                .signal-adjustment-process {
                    flex-direction: column;
                }

                .process-arrow {
                    transform: rotate(90deg);
                }

                .risk-constraints {
                    grid-template-columns: 1fr;
                }

                .methodology-box {
                    padding: 20px;
                }
            }

            /* 投资方案对比样式 */
            .investment-comparison {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin: 30px 0;
            }

            .plan-card {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }

            .plan-card.traditional {
                border-color: #3498db;
            }

            .plan-card.enhanced {
                border-color: #e74c3c;
            }

            .plan-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            }

            .plan-card h4 {
                color: #2c3e50;
                margin-bottom: 15px;
                font-size: 1.3em;
                text-align: center;
            }

            .plan-description {
                text-align: center;
                margin-bottom: 20px;
                padding: 15px;
                background: rgba(255,255,255,0.7);
                border-radius: 8px;
            }

            .plan-features {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            .feature-item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 12px;
                background: rgba(255,255,255,0.5);
                border-radius: 6px;
                transition: all 0.2s ease;
            }

            .feature-item:hover {
                background: rgba(255,255,255,0.8);
                transform: translateX(5px);
            }

            .feature-icon {
                font-size: 1.2em;
                min-width: 25px;
                text-align: center;
            }

            .recommendation-box {
                background: linear-gradient(135deg, #2ecc71, #27ae60);
                color: white;
                padding: 25px;
                border-radius: 15px;
                margin-top: 30px;
                box-shadow: 0 5px 15px rgba(46, 204, 113, 0.3);
            }

            .recommendation-box h4 {
                color: white;
                margin-bottom: 15px;
                font-size: 1.4em;
                text-align: center;
            }

            .recommendation-content ul {
                list-style: none;
                padding: 0;
            }

            .recommendation-content li {
                padding: 8px 0;
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }

            .recommendation-content li:last-child {
                border-bottom: none;
            }

            .recommendation-content em {
                display: block;
                margin-top: 15px;
                padding: 12px;
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
                font-style: normal;
            }

            @media (max-width: 768px) {
                .investment-comparison {
                    grid-template-columns: 1fr;
                    gap: 20px;
                }

                .plan-card {
                    padding: 20px;
                }
            }
        </style>
        """

        return base_css + enhanced_css

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

    def _get_javascript_with_data(self, config: Dict[str, Any], optimization_results: Dict[str, Any],
                                 performance_metrics: Dict[str, Any], risk_report: Optional[Dict[str, Any]] = None,
                                 investment_analysis: Optional[Dict[str, Any]] = None, correlation_analysis: Optional[Dict[str, Any]] = None,
                                 etf_names: Optional[Dict[str, str]] = None, enhanced_signals: Optional[Dict[str, Any]] = None,
                                 enhanced_results: Optional[Dict[str, Any]] = None) -> str:
        """获取包含数据绑定的JavaScript代码"""

        # 将数据序列化为JSON字符串
        config_json = json.dumps(config, ensure_ascii=False, indent=2)
        optimization_json = json.dumps(optimization_results, ensure_ascii=False, indent=2)
        metrics_json = json.dumps(performance_metrics, ensure_ascii=False, indent=2)
        risk_json = json.dumps(risk_report or {}, ensure_ascii=False, indent=2)
        investment_json = json.dumps(investment_analysis or {}, ensure_ascii=False, indent=2)
        correlation_json = json.dumps(correlation_analysis or {}, ensure_ascii=False, indent=2)
        etf_names_json = json.dumps(etf_names or {}, ensure_ascii=False, indent=2)
        signals_json = json.dumps(enhanced_signals or {}, ensure_ascii=False, indent=2)
        enhanced_json = json.dumps(enhanced_results or {}, ensure_ascii=False, indent=2)

        data_script = f"""
        <script>
            // 嵌入的投资组合数据
            window.PORTFOLIO_DATA = {{
                config: {config_json},
                optimization_results: {optimization_json},
                performance_metrics: {metrics_json},
                risk_report: {risk_json},
                investment_analysis: {investment_json},
                correlation_analysis: {correlation_json},
                etf_names: {etf_names_json},
                enhanced_signals: {signals_json},
                enhanced_results: {enhanced_json}
            }};

            document.addEventListener('DOMContentLoaded', function() {{
                console.log('Portfolio data loaded:', window.PORTFOLIO_DATA);

                // 平滑滚动
                document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                    anchor.addEventListener('click', function (e) {{
                        e.preventDefault();
                        document.querySelector(this.getAttribute('href')).scrollIntoView({{
                            behavior: 'smooth'
                        }});
                    }});
                }});

                // 折叠面板功能
                document.querySelectorAll('.collapsible-header').forEach(header => {{
                    header.addEventListener('click', function() {{
                        const collapsible = this.parentElement;
                        collapsible.classList.toggle('active');
                    }});
                }});

                // 数字动画效果
                function animateValue(element, start, end, duration) {{
                    let startTimestamp = null;
                    const step = (timestamp) => {{
                        if (!startTimestamp) startTimestamp = timestamp;
                        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                        const value = Math.floor(progress * (end - start) + start);
                        element.textContent = value.toLocaleString();
                        if (progress < 1) {{
                            window.requestAnimationFrame(step);
                        }}
                    }};
                    window.requestAnimationFrame(step);
                }}

                // 生成打印友好版本
                document.getElementById('printBtn').addEventListener('click', function() {{
                    window.print();
                }});

                // 响应式图表容器
                function resizeCharts() {{
                    document.querySelectorAll('.chart-container img').forEach(img => {{
                        img.style.maxHeight = '600px';
                        img.style.objectFit = 'contain';
                    }});
                }}

                // 数据绑定功能
                function bindDataToElements() {{
                    const data = window.PORTFOLIO_DATA;

                    // 绑定绩效指标数据
                    if (data.performance_metrics) {{
                        const metrics = data.performance_metrics;
                        Object.keys(metrics).forEach(key => {{
                            const elements = document.querySelectorAll(`[data-metric="${{key}}"]`);
                            elements.forEach(element => {{
                                const value = metrics[key];
                                if (typeof value === 'number') {{
                                    if (key.includes('rate') || key.includes('ratio')) {{
                                        element.textContent = (value * 100).toFixed(2) + '%';
                                    }} else {{
                                        element.textContent = value.toFixed(2);
                                    }}
                                }} else {{
                                    element.textContent = value;
                                }}
                            }});
                        }});
                    }}

                    // 绑定投资组合权重数据
                    if (data.optimization_results && data.optimization_results.optimal_weights) {{
                        const weights = data.optimization_results.optimal_weights;
                        const etfNames = data.etf_names || {{}};

                        Object.keys(weights).forEach(etf_code => {{
                            const weight = weights[etf_code];
                            const etfName = etfNames[etf_code] || etf_code;
                            const displayName = `${{etfName}} (${{etf_code}})`;

                            // 查找对应的权重显示元素
                            const weightElements = document.querySelectorAll(`[data-etf="${{etf_code}}"]`);
                            weightElements.forEach(element => {{
                                element.textContent = (weight * 100).toFixed(2) + '%';
                            }});
                        }});
                    }}

                    // 绑定风险分析数据
                    if (data.risk_report) {{
                        const risk = data.risk_report;
                        Object.keys(risk).forEach(key => {{
                            const elements = document.querySelectorAll(`[data-risk="${{key}}"]`);
                            elements.forEach(element => {{
                                const value = risk[key];
                                if (typeof value === 'number') {{
                                    if (key.includes('ratio') || key.includes('rate')) {{
                                        element.textContent = (value * 100).toFixed(2) + '%';
                                    }} else {{
                                        element.textContent = value.toFixed(2);
                                    }}
                                }} else {{
                                    element.textContent = value;
                                }}
                            }});
                        }});
                    }}
                }}

                // 页面加载完成后绑定数据
                bindDataToElements();
                resizeCharts();
                window.addEventListener('resize', resizeCharts);
            }});
        </script>
        """
        return data_script

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
                <li><a href="#quant-signals">🔬 量化信号分析</a></li>
                <li><a href="#enhanced-optimization">🚀 增强优化结果</a></li>
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

    def _generate_quant_signals_section(self, enhanced_signals: Optional[Dict[str, Any]] = None) -> str:
        """生成量化信号分析部分"""

        # 量化信号分析方法介绍
        methodology_intro = """
        <div class="methodology-box">
            <h3>🔬 量化信号分析方法论</h3>
            <div class="methodology-content">
                <h4>📊 什么是量化信号？</h4>
                <p>量化信号是基于历史价格和交易数据计算出的数学指标，用于评估ETF的投资价值和未来表现潜力。系统通过多维度分析，从不同角度捕捉ETF的特征和趋势。</p>

                <h4>🎯 信号计算维度</h4>
                <div class="signal-dimensions">
                    <div class="dimension-card">
                        <span class="dimension-icon">📈</span>
                        <div class="dimension-content">
                            <h5>动量信号</h5>
                            <p>短期(20天)、中期(60天)、长期(120天)的价格动量，捕捉趋势强度</p>
                        </div>
                    </div>
                    <div class="dimension-card">
                        <span class="dimension-icon">📉</span>
                        <div class="dimension-content">
                            <h5>波动率信号</h5>
                            <p>历史波动率、下行波动率、波动率比率，评估风险特征</p>
                        </div>
                    </div>
                    <div class="dimension-card">
                        <span class="dimension-icon">🎢</span>
                        <div class="dimension-content">
                            <h5>趋势信号</h5>
                            <p>价格相对位置、移动平均信号、趋势强度，判断价格走向</p>
                        </div>
                    </div>
                    <div class="dimension-card">
                        <span class="dimension-icon">💎</span>
                        <div class="dimension-content">
                            <h5>质量信号</h5>
                            <p>收益稳定性、正收益比率、回撤控制，评估投资质量</p>
                        </div>
                    </div>
                </div>

                <h4>🔄 综合信号合成</h4>
                <p>系统将所有单一信号进行<strong>标准化处理</strong>，消除量纲影响，然后通过<strong>等权重平均</strong>的方式合成为综合信号。这种方法确保：</p>
                <ul>
                    <li>🎯 <strong>平衡性</strong>：各维度信号得到平等对待</li>
                    <li>📊 <strong>客观性</strong>：基于历史数据的数学计算</li>
                    <li>🔄 <strong>动态性</strong>：随市场变化及时更新</li>
                    <li>⚖️ <strong>稳定性</strong>：多维度分析避免单一指标偏差</li>
                </ul>
            </div>
        </div>
        """

        if not enhanced_signals:
            return f"""
            <div id="quant-signals" class="section">
                <h2>🔬 量化信号分析</h2>
                {methodology_intro}
                <div class="warning-box">
                    <p>当前运行中量化信号分析数据暂不可用。</p>
                </div>
            </div>
            """

        signals_html = f"""
        {methodology_intro}
        """

        # 显示综合信号排名
        if 'composite_signal' in enhanced_signals:
            signals_html += """
            <div class="metric-subsection">
                <h3>📊 综合量化信号排名</h3>
                <div class="signals-ranking">
            """

            composite_signal = enhanced_signals['composite_signal'].sort_values(ascending=False)
            for etf, signal in composite_signal.items():
                signal_class = "signal-strong" if signal > 0.5 else "signal-weak" if signal < -0.5 else "signal-neutral"
                signal_emoji = "📈" if signal > 0.5 else "📉" if signal < -0.5 else "➡️"

                signals_html += f"""
                <div class="signal-item {signal_class}">
                    <span class="signal-emoji">{signal_emoji}</span>
                    <span class="signal-etf">{etf}</span>
                    <span class="signal-value">{signal:.3f}</span>
                </div>
                """

            signals_html += "</div></div>"

        # 显示分项信号（可折叠，默认折叠）
        if 'signal_normalized' in enhanced_signals:
            signals_html += """
            <div class="metric-subsection">
                <div class="collapsible">
                    <div class="collapsible-header">
                        <h3>📈 分项信号强度分析</h3>
                        <span class="toggle-icon">▶</span>
                    </div>
                    <div class="collapsible-content">
                        <div class="signal-details">
            """

            signal_df = enhanced_signals['signal_normalized']
            for signal_type in signal_df.columns:
                signals_html += f"""
                <div class="signal-type-section">
                    <h4>{signal_type}</h4>
                    <div class="signal-type-grid">
                """

                for etf in signal_df.index:
                    signal_value = signal_df.loc[etf, signal_type]
                    signal_class = "signal-strong" if signal_value > 0.5 else "signal-weak" if signal_value < -0.5 else "signal-neutral"
                    signal_emoji = "📈" if signal_value > 0.5 else "📉" if signal_value < -0.5 else "➡️"

                    signals_html += f"""
                    <div class="mini-signal-item {signal_class}">
                        <span class="mini-signal-emoji">{signal_emoji}</span>
                        <span class="mini-signal-etf">{etf}</span>
                        <span class="mini-signal-value">{signal_value:.2f}</span>
                    </div>
                    """

                signals_html += "</div></div>"

            signals_html += "</div></div></div></div>"  # 关闭collapsible-content, collapsible, metric-subsection

        return f"""
        <div id="quant-signals" class="section">
            <h2>🔬 量化信号分析</h2>
            {signals_html}
        </div>
        """

    def _generate_enhanced_optimization_section(self, enhanced_results: Optional[Dict[str, Any]] = None,
                                               etf_names: Optional[Dict[str, str]] = None) -> str:
        """生成增强优化结果部分"""

        # 增强优化方法论介绍
        optimization_methodology = """
        <div class="methodology-box">
            <h3>🚀 增强优化方法论</h3>
            <div class="methodology-content">
                <h4>🎯 什么是增强优化？</h4>
                <p>增强优化是传统投资组合优化与量化信号分析的结合，通过将量化信号融入投资组合构建过程，实现更智能、更科学的大类资产配置。</p>

                <h4>⚖️ 传统优化 vs 增强优化</h4>
                <div class="comparison-methodology">
                    <div class="method-card traditional">
                        <h5>📊 传统优化</h5>
                        <ul>
                            <li>基于历史收益率计算预期收益</li>
                            <li>假设历史表现会延续到未来</li>
                            <li>仅考虑风险收益的数学关系</li>
                            <li>可能忽略市场结构变化</li>
                            <li>单一维度的优化目标</li>
                        </ul>
                    </div>
                    <div class="method-card enhanced">
                        <h5>🚀 增强优化</h5>
                        <ul>
                            <li>结合量化信号调整预期收益</li>
                            <li>多维度分析预测未来潜力</li>
                            <li>考虑趋势、质量、风险等因子</li>
                            <li>适应市场动态变化</li>
                            <li>综合多目标的优化策略</li>
                        </ul>
                    </div>
                </div>

                <h4>🔄 信号调整机制</h4>
                <div class="signal-adjustment-process">
                    <div class="process-step">
                        <span class="step-number">1</span>
                        <div class="step-content">
                            <h5>基础预期收益</h5>
                            <p>计算各ETF历史年化收益率作为基准</p>
                        </div>
                    </div>
                    <div class="process-arrow">→</div>
                    <div class="process-step">
                        <span class="step-number">2</span>
                        <div class="step-content">
                            <h5>信号强度调整</h5>
                            <p>根据量化信号强度对预期收益进行修正</p>
                        </div>
                    </div>
                    <div class="process-arrow">→</div>
                    <div class="process-step">
                        <span class="step-number">3</span>
                        <div class="step-content">
                            <h5>风险控制约束</h5>
                            <p>设置波动率、集中度等风险约束条件</p>
                        </div>
                    </div>
                    <div class="process-arrow">→</div>
                    <div class="process-step">
                        <span class="step-number">4</span>
                        <div class="step-content">
                            <h5>夏普比率最大化</h5>
                            <p>在约束条件下寻找最优权重配置</p>
                        </div>
                    </div>
                </div>

                <h4>📈 数学优化模型</h4>
                <div class="optimization-formula">
                    <h5>目标函数：最大化夏普比率</h5>
                    <div class="formula">
                        <p><strong>max</strong> SharpeRatio = (Rp - Rf) / σp</p>
                        <p>其中：</p>
                        <ul>
                            <li><strong>Rp</strong> = Σ(wi × Ri) - 投资组合预期收益</li>
                            <li><strong>Rf</strong> = 无风险利率 (2%)</li>
                            <li><strong>σp</strong> = √(W^T × Σ × W) - 投资组合波动率</li>
                            <li><strong>wi</strong> = 第i个ETF的权重</li>
                            <li><strong>Ri</strong> = 信号调整后的第i个ETF预期收益</li>
                        </ul>
                    </div>
                </div>

                <h4>⚠️ 风险控制约束</h4>
                <div class="risk-constraints">
                    <div class="constraint-item">
                        <span class="constraint-icon">🛡️</span>
                        <div class="constraint-content">
                            <h5>波动率约束</h5>
                            <p>投资组合年化波动率 ≤ 25%</p>
                        </div>
                    </div>
                    <div class="constraint-item">
                        <span class="constraint-icon">⚖️</span>
                        <div class="constraint-content">
                            <h5>集中度约束</h5>
                            <p>单个ETF权重 ≤ 50%</p>
                        </div>
                    </div>
                    <div class="constraint-item">
                        <span class="constraint-icon">🎯</span>
                        <div class="constraint-content">
                            <h5>权重总和约束</h5>
                            <p>所有ETF权重之和 = 100%</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

        if not enhanced_results:
            return f"""
            <div id="enhanced-optimization" class="section">
                <h2>🚀 增强优化结果</h2>
                {optimization_methodology}
                <div class="warning-box">
                    <p>当前运行中增强优化结果暂不可用。</p>
                </div>
            </div>
            """

        enhanced_metrics = enhanced_results.get('enhanced_metrics', {})
        comparison = enhanced_results.get('comparison', {})
        recommendations = enhanced_results.get('recommendations', [])

        # 增强优化权重分配（使用表格样式，匹配最优配置）
        enhanced_weights = enhanced_results.get('enhanced_weights', {})
        weights_html = ""
        if enhanced_weights:
            weights_html = """
            <div class="metric-subsection">
                <h3>⚖️ 增强优化权重分配</h3>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>ETF名称</th>
                                <th>权重</th>
                                <th>权重分布</th>
                            </tr>
                        </thead>
                        <tbody>
            """

            # 按权重排序
            sorted_weights = sorted(enhanced_weights.items(), key=lambda x: x[1], reverse=True)

            for etf_code, weight in sorted_weights:
                if weight > 0.001:  # 只显示权重大于0.1%的ETF
                    # 获取ETF中文名称
                    etf_name = etf_names.get(etf_code, etf_code) if etf_names else etf_code
                    weights_html += f"""
                    <tr>
                        <td>{etf_name}<br><small style="color: #666;">({etf_code})</small></td>
                        <td>{weight:.2%}</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {weight * 100}%"></div>
                            </div>
                        </td>
                    </tr>
                    """

            weights_html += """
                        </tbody>
                    </table>
                </div>
            </div>
            """

        # 增强优化指标
        metrics_html = f"""
        <div class="metric-subsection">
            <h3>📊 增强优化指标</h3>
            <div class="metrics-grid">
                <div class="metric-card positive">
                    <div class="metric-value">{enhanced_metrics.get('sharpe_ratio', 0):.4f}</div>
                    <div class="metric-label">夏普比率</div>
                </div>
                <div class="metric-card positive">
                    <div class="metric-value">{enhanced_metrics.get('portfolio_return', 0):.2%}</div>
                    <div class="metric-label">预期年化收益</div>
                </div>
                <div class="metric-card warning">
                    <div class="metric-value">{enhanced_metrics.get('portfolio_volatility', 0):.2%}</div>
                    <div class="metric-label">年化波动率</div>
                </div>
                <div class="metric-card info">
                    <div class="metric-value">{enhanced_metrics.get('concentration_hhi', 0):.0f}</div>
                    <div class="metric-label">集中度指数</div>
                </div>
                <div class="metric-card info">
                    <div class="metric-value">{enhanced_metrics.get('effective_assets', 0):.1f}</div>
                    <div class="metric-label">有效资产数量</div>
                </div>
                <div class="metric-card info">
                    <div class="metric-value">{enhanced_metrics.get('diversification_ratio', 0):.3f}</div>
                    <div class="metric-label">分散化比率</div>
                </div>
            </div>
        </div>
        """

        # 优化对比
        comparison_html = ""
        if 'improvement' in comparison:
            improvement = comparison['improvement']
            comparison_html = f"""
            <div class="metric-subsection">
                <h3>📈 相比传统优化改进</h3>
                <div class="comparison-grid">
                    <div class="comparison-item">
                        <span class="comparison-label">夏普比率提升:</span>
                        <span class="comparison-value positive">+{improvement.get('sharpe_ratio_improvement', 0):.4f}</span>
                    </div>
                    <div class="comparison-item">
                        <span class="comparison-label">夏普比率提升幅度:</span>
                        <span class="comparison-value positive">+{improvement.get('sharpe_improvement_pct', 0):.1f}%</span>
                    </div>
                    <div class="comparison-item">
                        <span class="comparison-label">收益率变化:</span>
                        <span class="comparison-value {'positive' if improvement.get('return_change', 0) > 0 else 'negative'}">
                            {improvement.get('return_change', 0):+.2%}
                        </span>
                    </div>
                    <div class="comparison-item">
                        <span class="comparison-label">风险变化:</span>
                        <span class="comparison-value {'negative' if improvement.get('volatility_change', 0) > 0 else 'positive'}">
                            {improvement.get('volatility_change', 0):+.2%}
                        </span>
                    </div>
                </div>
            </div>
            """

        # 优化建议和投资方案对比
        recommendations_html = ""
        if recommendations:
            recommendations_html = """
            <div class="metric-subsection">
                <h3>💡 优化建议</h3>
                <ul class="recommendations-list">
            """
            for rec in recommendations:
                recommendations_html += f"<li>{rec}</li>"
            recommendations_html += "</ul></div>"

        # 添加投资方案对比和推荐
        investment_comparison = f"""
        <div class="metric-subsection">
            <h3>📋 投资方案对比与推荐</h3>
            <div class="investment-comparison">
                <div class="plan-card traditional">
                    <h4>📊 传统优化方案</h4>
                    <div class="plan-description">
                        <p>基于历史数据的经典夏普比率最大化优化</p>
                    </div>
                    <div class="plan-features">
                        <div class="feature-item">
                            <span class="feature-icon">⚖️</span>
                            <span>权重分配相对保守</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">📈</span>
                            <span>侧重历史表现延续性</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">🛡️</span>
                            <span>风险控制较为严格</span>
                        </div>
                    </div>
                </div>

                <div class="plan-card enhanced">
                    <h4>🚀 增强优化方案</h4>
                    <div class="plan-description">
                        <p>结合量化信号的智能投资组合配置</p>
                    </div>
                    <div class="plan-features">
                        <div class="feature-item">
                            <span class="feature-icon">🔬</span>
                            <span>融入多维度量化信号</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">📊</span>
                            <span>动态调整预期收益</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">🎯</span>
                            <span>适应市场变化趋势</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="recommendation-box">
                <h4>🎯 投资建议</h4>
                <div class="recommendation-content">
                    <p><strong>推荐采用增强优化方案</strong>，原因如下：</p>
                    <ul>
                        <li>📈 <strong>收益潜力更高</strong>：结合量化信号识别高潜力标的</li>
                        <li>🔬 <strong>分析更全面</strong>：多维度评估避免单一数据源偏差</li>
                        <li>📊 <strong>适应性更强</strong>：能够响应市场结构和趋势变化</li>
                        <li>⚖️ <strong>风险可控</strong>：在量化信号基础上进行风险约束</li>
                    </ul>
                    <p><em>注：增强优化方案引入了新能源ETF(516160.SH)，该标的在量化信号分析中表现优异，建议重点关注。</em></p>
                </div>
            </div>
        </div>
        """

        return f"""
        <div id="enhanced-optimization" class="section">
            <h2>🚀 增强优化结果</h2>
            {weights_html}
            {metrics_html}
            {comparison_html}
            {recommendations_html}
            {investment_comparison}
        </div>
        """

    def _generate_enhanced_charts_section(self, correlation_analysis: Optional[Dict[str, Any]] = None,
                                         enhanced_charts: Optional[List[str]] = None) -> str:
        """生成增强可视化图表部分"""
        # 基础图表
        charts = [
            ("cumulative_returns.png", "累计收益对比图"),
            ("efficient_frontier.png", "有效前沿图"),
            ("portfolio_weights.png", "投资组合权重分布"),
            ("returns_distribution.png", "收益率分布图")
        ]

        # 如果有相关性分析，添加相关性热力图
        if correlation_analysis and correlation_analysis.get('heatmap_path'):
            charts.append(("correlation_heatmap.png", "ETF相关性热力图"))

        # 添加增强图表
        if enhanced_charts:
            enhanced_chart_titles = {
                'quant_signals_heatmap.png': '量化信号热力图',
                'signal_importance_chart.png': '信号重要性分析',
                'signal_correlation_chart.png': '信号相关性分析',
                'optimization_comparison_chart.png': '优化结果对比',
                'portfolio_composition_chart.png': '投资组合构成对比'
            }

            for chart_file in enhanced_charts:
                if chart_file in enhanced_chart_titles:
                    charts.append((chart_file, enhanced_chart_titles[chart_file]))

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
        enhanced_growth_proj = investment_analysis.get('enhanced_growth_projection') if investment_analysis else None

        # 计算预期变化
        improvement_html = ""
        if enhanced_growth_proj and growth_proj:
            original_mean = growth_proj.get("final_value_statistics", {}).get("mean", 0)
            enhanced_mean = enhanced_growth_proj.get("final_value_statistics", {}).get("mean", 0)
            if original_mean > 0:
                improvement = ((enhanced_mean - original_mean) / original_mean) * 100
                color = "green" if improvement > 0 else "red"
                improvement_html = f'<tr><td><strong style="color: {color};">预期变化</strong></td><td style="color: {color};">{improvement:+.1f}%</td></tr>'

        # 构建增强策略HTML
        enhanced_strategy_html = ""
        if enhanced_growth_proj:
            enhanced_strategy_html = f'''
                        <div class="strategy-card enhanced">
                            <h4>🚀 量化增强策略预测（{enhanced_growth_proj.get("years", 5)}年）</h4>
                            <table>
                                <tr><td><strong>平均预期价值</strong></td><td>{enhanced_growth_proj.get("final_value_statistics", {}).get("mean", 0):,.0f}元</td></tr>
                                <tr><td><strong>中位数价值</strong></td><td>{enhanced_growth_proj.get("final_value_statistics", {}).get("median", 0):,.0f}元</td></tr>
                                <tr><td><strong>标准差</strong></td><td>{enhanced_growth_proj.get("final_value_statistics", {}).get("std", 0):,.0f}元</td></tr>
                                <tr><td><strong>翻倍成功率</strong></td><td>{enhanced_growth_proj.get("success_probability", 0):.1%}</td></tr>
                                {improvement_html}
                            </table>
                        </div>'''
        else:
            enhanced_strategy_html = '<h4 style="color: #e74c3c;">🚀 量化增强策略预测</h4><p>增强策略增长预测数据暂不可用</p>'

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
                    <span>📈 增长预测对比</span>
                    <span>▼</span>
                </div>
                <div class="collapsible-content">
                    <!-- 策略对比 -->
                    <div class="strategy-comparison">
                        <div class="strategy-card original">
                            <h4>📊 原始策略预测（{growth_proj.get("years", 5)}年）</h4>
                            <table>
                                <tr><td><strong>平均预期价值</strong></td><td>{growth_proj.get("final_value_statistics", {}).get("mean", 0):,.0f}元</td></tr>
                                <tr><td><strong>中位数价值</strong></td><td>{growth_proj.get("final_value_statistics", {}).get("median", 0):,.0f}元</td></tr>
                                <tr><td><strong>标准差</strong></td><td>{growth_proj.get("final_value_statistics", {}).get("std", 0):,.0f}元</td></tr>
                                <tr><td><strong>翻倍成功率</strong></td><td>{growth_proj.get("success_probability", 0):.1%}</td></tr>
                            </table>
                        </div>

                        {enhanced_strategy_html}
                    </div>

                    <style>
                    .strategy-comparison {{
                        display: grid;
                        grid-template-columns: {f'1fr 1fr' if enhanced_growth_proj else '1fr'};
                        gap: 20px;
                        margin: 20px 0;
                    }}

                    .strategy-card {{
                        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                        border-radius: 12px;
                        padding: 20px;
                        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                    }}

                    .strategy-card.original {{
                        border-left: 4px solid #3498db;
                    }}

                    .strategy-card.enhanced {{
                        border-left: 4px solid #e74c3c;
                    }}

                    .strategy-card h4 {{
                        margin: 0 0 15px 0;
                        color: #2c3e50;
                        font-size: 16px;
                    }}

                    .strategy-card table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}

                    .strategy-card td {{
                        padding: 8px;
                        border-bottom: 1px solid #eee;
                    }}

                    .strategy-card td:first-child {{
                        font-weight: bold;
                        color: #555;
                    }}
                    </style>

                    <!-- 概率分布对比 -->
                    <h4>📊 概率分布对比</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <th style="border: 1px solid #ddd; padding: 8px; background: #f5f5f5;">分位数</th>
                            <th style="border: 1px solid #ddd; padding: 8px; background: #f5f5f5;">原始策略</th>
                            {f'<th style="border: 1px solid #ddd; padding: 8px; background: #f5f5f5;">量化增强策略</th>' if enhanced_growth_proj else ''}
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 8px;"><strong>10%分位数（最差10%）</strong></td>
                            <td style="border: 1px solid #ddd; padding: 8px;">{growth_proj.get("final_value_percentiles", {}).get(1, 0):,.0f}元</td>
                            {f'<td style="border: 1px solid #ddd; padding: 8px;">{enhanced_growth_proj.get("final_value_percentiles", {}).get(1, 0):,.0f}元</td>' if enhanced_growth_proj else ''}
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 8px;"><strong>25%分位数</strong></td>
                            <td style="border: 1px solid #ddd; padding: 8px;">{growth_proj.get("final_value_percentiles", {}).get(25, 0):,.0f}元</td>
                            {f'<td style="border: 1px solid #ddd; padding: 8px;">{enhanced_growth_proj.get("final_value_percentiles", {}).get(25, 0):,.0f}元</td>' if enhanced_growth_proj else ''}
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 8px;"><strong>75%分位数</strong></td>
                            <td style="border: 1px solid #ddd; padding: 8px;">{growth_proj.get("final_value_percentiles", {}).get(75, 0):,.0f}元</td>
                            {f'<td style="border: 1px solid #ddd; padding: 8px;">{enhanced_growth_proj.get("final_value_percentiles", {}).get(75, 0):,.0f}元</td>' if enhanced_growth_proj else ''}
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 8px;"><strong>90%分位数（最优10%）</strong></td>
                            <td style="border: 1px solid #ddd; padding: 8px;">{growth_proj.get("final_value_percentiles", {}).get(90, 0):,.0f}元</td>
                            {f'<td style="border: 1px solid #ddd; padding: 8px;">{enhanced_growth_proj.get("final_value_percentiles", {}).get(90, 0):,.0f}元</td>' if enhanced_growth_proj else ''}
                        </tr>
                    </table>

                    <!-- 多目标成功率 -->
                    <h4>🎖️ 多目标成功率</h4>
                    <table>
                        <tr><td><strong>盈利25%</strong></td><td>{growth_proj.get("success_analysis", {}).get("target_multipliers", {}).get("1.25x", 0):.1%}</td></tr>
                        <tr><td><strong>盈利50%</strong></td><td>{growth_proj.get("success_analysis", {}).get("target_multipliers", {}).get("1.5x", 0):.1%}</td></tr>
                        <tr><td><strong>翻倍（100%）</strong></td><td>{growth_proj.get("success_analysis", {}).get("target_multipliers", {}).get("2.0x", 0):.1%}</td></tr>
                        <tr><td><strong>翻三倍（200%）</strong></td><td>{growth_proj.get("success_analysis", {}).get("target_multipliers", {}).get("3.0x", 0):.1%}</td></tr>
                        <tr><td><strong>翻五倍（400%）</strong></td><td>{growth_proj.get("success_analysis", {}).get("target_multipliers", {}).get("5.0x", 0):.1%}</td></tr>
                    </table>

                    <!-- 风险指标 -->
                    {self._generate_risk_metrics_section(growth_proj) if growth_proj.get("risk_metrics") else ''}

                    <!-- 情景分析 -->
                    {self._generate_scenario_section(growth_proj) if growth_proj.get("scenario_analysis") else ''}

                    <!-- 多年度分析 -->
                    {self._generate_multi_year_section(growth_proj) if growth_proj.get("multi_year_analysis") else ''}

                    <!-- 模拟参数 -->
                    <p style="margin-top: 15px; font-size: 0.9em; color: #666;">
                        <strong>模拟参数：</strong>基于{growth_proj.get("simulations", 0):,}次蒙特卡洛模拟，考虑均值回归和波动率聚集效应
                    </p>
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

    def _serialize_data(self, data: Any) -> Any:
        """
        递归序列化数据，确保所有pandas对象转换为基本类型

        Args:
            data: 需要序列化的数据

        Returns:
            序列化后的数据
        """
        import pandas as pd
        import numpy as np

        if isinstance(data, pd.Series):
            return data.to_dict()
        elif isinstance(data, pd.DataFrame):
            return data.to_dict()
        elif isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, dict):
            return {key: self._serialize_data(value) for key, value in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self._serialize_data(item) for item in data]
        elif isinstance(data, (np.integer, np.floating)):
            return float(data)
        elif isinstance(data, (int, float, str, bool)) or data is None:
            return data
        else:
            # 对于其他类型，尝试转换为字符串
            return str(data)

    def generate_enhanced_html_report(self,
                                     config: Dict[str, Any],
                                     optimization_results: Dict[str, Any],
                                     performance_metrics: Dict[str, Any],
                                     risk_report: Optional[Dict[str, Any]] = None,
                                     investment_analysis: Optional[Dict[str, Any]] = None,
                                     correlation_analysis: Optional[Dict[str, Any]] = None,
                                     etf_names: Optional[Dict[str, str]] = None,
                                     enhanced_signals: Optional[Dict[str, Any]] = None,
                                     enhanced_results: Optional[Dict[str, Any]] = None,
                                     enhanced_charts: Optional[List[str]] = None) -> str:
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
            enhanced_signals: 增强量化信号（可选）
            enhanced_results: 增强优化结果（可选）
            enhanced_charts: 增强图表列表（可选）

        Returns:
            生成的HTML文件路径
        """
        logger.info("📝 开始生成增强HTML分析报告...")

        try:
            # 为HTML生成保留原始数据（可能包含pandas对象）
            original_enhanced_signals = enhanced_signals

            # 序列化数据用于JavaScript嵌入
            serialized_config = self._serialize_data(config)
            serialized_optimization_results = self._serialize_data(optimization_results)
            serialized_performance_metrics = self._serialize_data(performance_metrics)
            serialized_risk_report = self._serialize_data(risk_report or {})
            serialized_investment_analysis = self._serialize_data(investment_analysis or {})
            serialized_correlation_analysis = self._serialize_data(correlation_analysis or {})
            serialized_etf_names = self._serialize_data(etf_names or {})
            serialized_enhanced_signals = self._serialize_data(enhanced_signals or {})
            serialized_enhanced_results = self._serialize_data(enhanced_results or {})
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
                {self._get_enhanced_css_styles()}
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
                        {self._generate_quant_signals_section(original_enhanced_signals)}
                        {self._generate_enhanced_optimization_section(enhanced_results, etf_names)}
                        {self._generate_correlation_section(correlation_analysis, etf_names)}
                        {self._generate_risk_section(risk_report)}
                        {self._generate_enhanced_charts_section(correlation_analysis, enhanced_charts)}
                        {self._generate_recommendations_section(investment_analysis)}
                    </div>
                    {self._generate_footer()}
                </div>
                {self._get_javascript_with_data(serialized_config, serialized_optimization_results, serialized_performance_metrics,
                                               serialized_risk_report, serialized_investment_analysis, serialized_correlation_analysis,
                                               serialized_etf_names, serialized_enhanced_signals, serialized_enhanced_results)}
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

    def _generate_risk_metrics_section(self, growth_proj: Dict[str, Any]) -> str:
        """生成风险指标部分"""
        risk_metrics = growth_proj.get("risk_metrics", {})
        tail_risk = growth_proj.get("distribution_analysis", {}).get("tail_risk", {})

        return f"""
        <h4>⚠️ 风险指标</h4>
        <table>
            <tr><td><strong>最大回撤（平均）</strong></td><td>{risk_metrics.get("max_drawdown_analysis", {}).get("mean", 0):.1%}</td></tr>
            <tr><td><strong>最大回撤（5%最差）</strong></td><td>{risk_metrics.get("max_drawdown_analysis", {}).get("worst_5_percent", 0):.1%}</td></tr>
            <tr><td><strong>夏普比率（平均）</strong></td><td>{risk_metrics.get("sharpe_ratio_distribution", {}).get("mean", 0):.2f}</td></tr>
            <tr><td><strong>VaR 95%（风险价值）</strong></td><td>{tail_risk.get("var_95", 0):,.0f}元</td></tr>
            <tr><td><strong>CVaR 95%（条件风险价值）</strong></td><td>{tail_risk.get("cvar_95", 0):,.0f}元</td></tr>
        </table>
        """

    def _generate_scenario_section(self, growth_proj: Dict[str, Any]) -> str:
        """生成情景分析部分"""
        scenarios = growth_proj.get("scenario_analysis", {})

        return f"""
        <h4>🎭 情景分析</h4>
        <table>
            <tr><td><strong>牛市情景（收益+50%）</strong></td><td>{scenarios.get("bull_market", {}).get("success_probability", 0):.1%}</td></tr>
            <tr><td><strong>熊市情景（收益-50%）</strong></td><td>{scenarios.get("bear_market", {}).get("success_probability", 0):.1%}</td></tr>
            <tr><td><strong>高波动情景（波动+100%）</strong></td><td>{scenarios.get("high_volatility", {}).get("success_probability", 0):.1%}</td></tr>
            <tr><td><strong>低波动情景（波动-50%）</strong></td><td>{scenarios.get("low_volatility", {}).get("success_probability", 0):.1%}</td></tr>
        </table>
        """

    def _generate_multi_year_section(self, growth_proj: Dict[str, Any]) -> str:
        """生成分年度分析部分"""
        multi_year = growth_proj.get("multi_year_analysis", {})

        return f"""
        <h4>📅 分年度表现</h4>
        <table>
            <tr><td><strong>第1年平均价值</strong></td><td>{multi_year.get("year_1", {}).get("mean", 0):,.0f}元</td></tr>
            <tr><td><strong>第2年平均价值</strong></td><td>{multi_year.get("year_2", {}).get("mean", 0):,.0f}元</td></tr>
            <tr><td><strong>第3年平均价值</strong></td><td>{multi_year.get("year_3", {}).get("mean", 0):,.0f}元</td></tr>
            <tr><td><strong>第1年正收益概率</strong></td><td>{multi_year.get("year_1", {}).get("positive_return_prob", 0):.1%}</td></tr>
            <tr><td><strong>第1年翻倍概率</strong></td><td>{multi_year.get("year_1", {}).get("doubling_prob", 0):.1%}</td></tr>
        </table>
        """


def get_html_report_generator(output_dir: str = "outputs") -> HTMLReportGenerator:
    """获取HTML报告生成器实例"""
    return HTMLReportGenerator(output_dir)