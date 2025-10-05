# 🚀 增强版ETF投资组合优化系统

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tushare](https://img.shields.io/badge/data-Tushare-orange.svg)](https://tushare.pro)

> 专业级ETF投资组合优化工具，提供全方位的量化投资决策支持

基于Tushare API的智能投资组合优化系统，通过先进的量化算法帮助投资者构建最优ETF投资组合，实现风险调整收益最大化。

## ✨ 核心特色

### 🎯 专业量化分析
- **多目标优化** - 夏普比率、风险平价、稳定性优化、分层风险平价
- **高级风险管理** - VaR/CVaR计算、压力测试、集中度分析
- **动态再平衡** - 智能再平衡策略和交易成本优化
- **实用投资工具** - 增长预测、定投计算、业绩归因分析

### 📊 全方位评估体系
- **基础指标** - 年化收益率、波动率、夏普比率、最大回撤
- **高级指标** - Calmar比率、索提诺比率、偏度、峰度
- **风险指标** - VaR(95%/99%)、CVaR、HHI集中度指数
- **实用指标** - 再平衡建议、投资增长预测

### 🎨 专业可视化
- 累计收益对比图
- 有效前沿图
- 投资组合权重饼图
- 收益率分布直方图

#### 📊 可视化图表展示

**1. 累计收益对比图**
![累计收益对比图](assets/images/cumulative_returns.png)
展示各ETF与最优组合的累计收益表现，直观对比不同策略的投资效果。

**2. 有效前沿图**
![有效前沿图](assets/images/efficient_frontier.png)
经典马科维茨有效前沿，显示风险-收益的最优边界，红点标记最优组合位置。

**3. 投资组合权重饼图**
![投资组合权重饼图](assets/images/portfolio_weights.png)
清晰展示最优组合中各ETF的权重分配，帮助投资者理解资产配置结构。

**4. 收益率分布直方图**
![收益率分布直方图](assets/images/returns_distribution.png)
分析投资组合收益率的分布特征，包含正态分布拟合和统计指标。

## ⚠️ 重要提示

**需要Tushare Pro账号和2000+积分**才能使用`fund_daily`接口！

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/your-username/SharpETF.git
cd SharpETF

# 创建conda环境（推荐）
conda create -n sharpetf python=3.9 -y
conda activate sharpetf

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置Tushare Token

**方法1：修改配置文件**
```bash
cp config.json.example config.json
```

编辑 `config.json` 文件：
```json
{
    "tushare_token": "您的Tushare Token",
    "etf_codes": ["159632.SZ", "159670.SZ", "159770.SZ", "159995.SZ", "159871.SZ", "510210.SH"],
    "start_date": "20240101",
    "end_date": "20241201",
    "risk_free_rate": 0.02,
    "trading_days": 252,
    "output_dir": "outputs"
}
```

**方法2：设置环境变量**
```bash
# Linux/Mac
export TUSHARE_TOKEN=您的Tushare Token

# Windows
set TUSHARE_TOKEN=您的Tushare Token
```

### 3. 运行分析

```bash
python main.py
```

## 📁 项目架构

```
SharpETF/
├── src/                                    # 源代码目录
│   ├── config.py                           # 配置管理
│   ├── data_fetcher.py                     # 数据获取模块
│   ├── data_processor.py                   # 数据处理模块
│   ├── portfolio_optimizer.py              # 基础优化模块
│   ├── portfolio_optimizer_scipy.py        # SciPy优化引擎
│   ├── evaluator.py                        # 评估指标模块
│   ├── visualizer.py                       # 可视化模块
│   ├── utils.py                            # 工具函数模块
│   ├── risk_manager.py                     # 🆕 高级风险管理
│   ├── rebalancing_engine.py               # 🆕 动态再平衡引擎
│   ├── multi_objective_optimizer.py        # 🆕 多目标优化器
│   └── investment_tools.py                 # 🆕 实用投资工具
├── main.py                                 # 主执行脚本
├── config.json.example                     # 配置文件模板
├── requirements.txt                        # 依赖库列表
├── README.md                               # 项目文档
├── ENHANCED_USAGE_GUIDE.md                 # 🆕 详细使用指南
├── CLAUDE.md                               # 项目架构说明
└── outputs/                                # 输出目录（自动创建）
    ├── cumulative_returns.png
    ├── efficient_frontier.png
    ├── portfolio_weights.png
    ├── returns_distribution.png
    └── optimization_results.json
```

## 🎯 系统功能详解

### 1. 多目标优化引擎

| 优化策略 | 目标 | 适用场景 | 特点 |
|----------|------|----------|------|
| **最大夏普比率** | 风险调整收益最大化 | 追求高收益 | 经典Markowitz优化 |
| **风险平价** | 等风险贡献 | 稳健投资 | 分散化风险 |
| **稳定性优化** | 收益稳定性 | 保守投资 | 降低波动性 |
| **分层风险平价** | 相关性聚类 | 复杂组合 | 智能分层 |

### 2. 高级风险管理

#### VaR/CVaR分析
```python
# 95% VaR (历史法): -2.34%
# 99% VaR (参数法): -3.12%
# 95% CVaR: -4.56%
```

#### 压力测试情景
- 📉 市场崩盘 (-30%)
- 📊 温和下跌 (-15%)
- ⚡ 闪电崩盘 (-10%)
- 🐻 熊市情景 (-40%)

#### 集中度风险
- **HHI指数**: 集中度测量
- **有效持仓**: 真实分散度
- **最大单一权重**: 风险集中度

### 3. 动态再平衡策略

#### 触发条件
- ⏰ **时间触发**: 月度/季度定期
- 📏 **阈值触发**: 权重偏离>5%
- 📊 **波动率触发**: 偏离目标20%

#### 交易成本优化
- 💰 最小交易金额限制
- 📊 净收益评估
- 🎯 智能交易时机

### 4. 实用投资工具

#### 投资增长预测
```python
# 5年期预测 (100万初始投资)
• 平均预期价值: 1,950万元
• 中位数价值: 1,900万元
• 成功概率 (翻倍): 85%
```

#### 定投计算器
```python
# 月定投5000元，10年期
• 总投入: 60万元
• 预期价值: 120万元
• 年化收益: 8.5%
```

## 📊 输出示例

### 综合分析报告
```
====================================================================================================
🎯 增强版ETF投资组合优化系统 - 综合分析报告
====================================================================================================

🏆 最优组合基础表现:
  • 最大夏普比率: 6.3520
  • 年化收益率: 105.43%
  • 年化波动率: 11.13%
  • 最大回撤: -3.26%

🔄 多目标优化比较:
  • Maximum Sharpe Ratio: 收益=72.71%, 波动=11.13%, 夏普=6.3520
  • Risk Parity: 收益=115.46%, 波动=22.85%, 夏普=4.9657
  • Hierarchical Risk Parity: 收益=78.31%, 波动=12.88%, 夏普=5.9234

🔒 高级风险分析:
  • 综合风险评级: 中风险
  • 95% VaR (历史): -0.76%
  • 集中度指数 (HHI): 3733

💡 投资建议:
  1. 持仓集中度过高，建议分散化投资
  2. 当前风险水平适中，适合积极型投资者
  3. 建议每季度进行一次再平衡

📈 5年增长预测 (100万初始投资):
  • 平均预期价值: 19,462万元
  • 中位数价值: 19,010万元
```

### 📊 实际输出图表展示

以下是系统运行生成的实际可视化图表：

![累计收益对比图](assets/images/cumulative_returns.png)
![有效前沿图](assets/images/efficient_frontier.png)
![投资组合权重饼图](assets/images/portfolio_weights.png)
![收益率分布直方图](assets/images/returns_distribution.png)

## 🔧 高级配置

### 风险参数调整
```python
# 自定义风险模型
risk_manager = get_advanced_risk_manager(
    confidence_levels=[0.90, 0.95, 0.99]  # 自定义置信度
)

# 再平衡参数
rebalancing_engine = get_rebalancing_engine(
    transaction_cost=0.002,    # 0.2%交易成本
    min_trade_amount=5000      # 最小交易5000元
)
```

### 多目标优化配置
```python
# 风险约束优化
weights, metrics = optimizer.maximize_sharpe_with_risk_constraint(
    max_volatility=0.12,     # 最大波动率12%
    max_drawdown=0.15        # 最大回撤15%
)

# 稳定性优化
weights, metrics = optimizer.optimize_for_stable_returns(
    stability_weight=0.3     # 30%稳定性权重
)
```

## 📈 投资策略建议

### 保守型投资者
- 选择风险平价或分层风险平价策略
- 关注VaR和最大回撤指标
- 定期进行再平衡

### 平衡型投资者
- 选择最大夏普比率策略
- 关注风险调整收益
- 适度分散投资

### 积极型投资者
- 关注收益最大化
- 可以承受较高波动
- 动态调整权重

## ❓ 常见问题

### Q: 出现"积分不足"错误怎么办？
A: 需要购买Tushare Pro账号的积分，2000积分起购。访问 [Tushare官网](https://tushare.pro) 购买。

### Q: 如何选择适合的优化策略？
A:
- **保守型**: 选择风险平价
- **平衡型**: 选择最大夏普比率
- **积极型**: 选择稳定性优化

### Q: 系统支持哪些ETF？
A: 支持所有在Tushare中有数据的ETF，包括但不限于：
- `159632.SZ` - 新能源ETF
- `159670.SZ` - 半导体ETF
- `159995.SZ` - 芯片ETF
- `159871.SZ` - 新能源车ETF
- `510210.SH` - 国债ETF

### Q: 如何解读风险评级？
A:
- **低风险**: 适合保守投资者，预期收益稳定
- **中风险**: 适合平衡投资者，风险收益平衡
- **高风险**: 适合积极投资者，追求高收益

### Q: 投资建议的可靠性如何？
A: 系统基于历史数据和量化模型生成建议，仅供参考。投资决策应结合个人风险承受能力和市场情况。

## 🔍 技术亮点

### 核心算法
- **SciPy优化引擎**: 高效的数值优化
- **Monte Carlo模拟**: 投资增长预测
- **风险管理模型**: VaR/CVaR计算
- **相关性分析**: 分层聚类算法

### 性能优化
- **并行数据获取**: 提高数据获取效率
- **智能缓存机制**: 减少重复计算
- **内存优化**: 支持大规模数据处理
- **错误处理**: 完善的异常处理机制

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 如何贡献
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 贡献方向
- 🐛 Bug修复
- ✨ 新功能开发
- 📚 文档改进
- 🧪 测试用例
- 🔧 性能优化

## 📊 更新日志

### v2.0.0 (2024-12-01) - 重大更新
- ✨ 新增多目标优化引擎
- ✨ 增加高级风险管理模块
- ✨ 实现动态再平衡策略
- ✨ 添加实用投资工具
- 🎨 全新UI界面设计
- 📊 增强可视化图表
- 🐛 修复已知问题
- ⚡ 性能大幅提升

### v1.0.0 (2024-06-01)
- 🎉 初始版本发布
- 📊 基础夏普比率优化
- 📈 有效前沿计算
- 🎨 可视化图表生成

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Tushare](https://tushare.pro) - 提供高质量的金融数据服务
- [SciPy](https://scipy.org) - 优秀的科学计算库
- [Pandas](https://pandas.pydata.org) - 强大的数据分析工具
- [Matplotlib](https://matplotlib.org) - 专业的可视化库
- [NumPy](https://numpy.org) - 高性能数值计算库

## 📞 联系我们

- 🐛 Issues: [GitHub Issues](https://github.com/StanleyChanH/SharpETF/issues)
- 📖 文档: [使用指南](ENHANCED_USAGE_GUIDE.md)

---

<div align="center">

**免责声明**: 本系统仅供研究和学习使用，不构成投资建议。投资有风险，决策需谨慎。

Made with ❤️ by [StanleyChanH]

</div>