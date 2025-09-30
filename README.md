# ETF夏普比率最优组合研究系统

基于Tushare API的量化投资组合优化工具，通过最大化夏普比率来寻找最优ETF投资组合。

## 🎯 项目特色

- **严格遵循Tushare规范**：使用`fund_daily`接口，仅获取必要字段
- **专业量化分析**：夏普比率最大化、有效前沿计算
- **完整评估体系**：8项核心金融指标评估
- **精美可视化**：4种专业图表展示
- **模块化设计**：易于扩展和维护

## ⚠️ 重要提示

**需要Tushare Pro账号和2000+积分**才能使用`fund_daily`接口！

## 📋 系统功能

### 核心功能
- ✅ 多ETF数据获取（fund_daily接口）
- ✅ 收益率计算和数据处理
- ✅ 夏普比率最大化优化
- ✅ 有效前沿计算
- ✅ 投资组合绩效评估
- ✅ 专业可视化图表生成

### 评估指标
- 年化收益率
- 年化波动率
- 夏普比率
- 最大回撤
- Calmar比率
- 索提诺比率
- 偏度
- 峰度

### 可视化图表
- 累计收益对比图
- 有效前沿图
- 权重饼图
- 收益率分布图

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd etf_sharpe_optimizer

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置Tushare Token

**方法1：修改配置文件**
编辑 `config.json` 文件：
```json
{
    "tushare_token": "您的Tushare Token",
    "etf_codes": ["510050.SH", "510300.SH", "510500.SH"],
    "start_date": "20200101",
    "end_date": "20231231",
    "risk_free_rate": 0.02,
    "trading_days": 252,
    "fields": "trade_date,close",
    "output_dir": "outputs"
}
```

**方法2：设置环境变量**
```bash
# Windows
set TUSHARE_TOKEN=您的Tushare Token

# Linux/Mac
export TUSHARE_TOKEN=您的Tushare Token
```

### 3. 运行分析

```bash
python main.py
```

## 📁 项目结构

```
etf_sharpe_optimizer/
├── src/                          # 源代码目录
│   ├── __init__.py              # 包初始化
│   ├── config.py                # 配置管理
│   ├── data_fetcher.py          # 数据获取模块
│   ├── data_processor.py        # 数据处理模块
│   ├── portfolio_optimizer.py   # 组合优化模块
│   ├── evaluator.py             # 评估指标模块
│   ├── visualizer.py            # 可视化模块
│   └── utils.py                 # 工具函数模块
├── main.py                      # 主执行脚本
├── config.json                  # 配置文件
├── requirements.txt             # 依赖库列表
├── README.md                    # 项目文档
└── outputs/                     # 输出目录（自动创建）
    ├── cumulative_returns.png
    ├── efficient_frontier.png
    ├── portfolio_weights.png
    ├── returns_distribution.png
    └── optimization_results.json
```

## 🔧 配置说明

### ETF代码配置
支持标准的ETF代码格式：
- `510050.SH` - 上证50ETF
- `510300.SH` - 沪深300ETF  
- `510500.SH` - 中证500ETF
- `159915.SZ` - 创业板ETF

### 时间范围配置
- 格式：`YYYYMMDD`
- 示例：`20200101` - `20231231`

### 参数说明
- `risk_free_rate`: 无风险利率（默认2%）
- `trading_days`: 年交易天数（默认252）
- `fields`: 数据字段（默认仅获取交易日和收盘价）

## 📊 输出结果

### 控制台输出
```
📊 投资组合评估报告
==================================================
🎯 绩效指标:
指标                值                 说明
--------------------------------------------------
年化收益率          12.34%             越高越好
年化波动率          15.67%             越低越好
夏普比率            0.65               越高越好
最大回撤            -18.23%            越小越好
Calmar比率          0.68               越高越好
索提诺比率          0.72               越高越好

📈 分布特征:
偏度                -0.12              >0右偏, <0左偏
峰度                3.45               >3尖峰, <3低峰

⚖️ 最优权重分配:
  510050.SH: 45.23%
  510300.SH: 32.67%
  510500.SH: 22.10%
```

### 文件输出
- `outputs/optimization_results.json` - 详细分析结果
- `outputs/cumulative_returns.png` - 累计收益对比图
- `outputs/efficient_frontier.png` - 有效前沿图
- `outputs/portfolio_weights.png` - 权重饼图
- `outputs/returns_distribution.png` - 收益率分布图
- `etf_optimizer.log` - 运行日志

## 🔍 核心算法

### 夏普比率最大化
```python
# 目标函数
sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_vol

# 约束条件
sum(weights) = 1
weights >= 0  # long-only约束
```

### 有效前沿计算
通过遍历目标收益率，计算最小风险组合来构建有效前沿曲线。

## 🛠️ 自定义配置

### 添加更多ETF
在 `config.json` 中修改 `etf_codes`：
```json
{
    "etf_codes": ["510050.SH", "510300.SH", "510500.SH", "159915.SZ", "510880.SH"]
}
```

### 调整分析期间
```json
{
    "start_date": "20190101",
    "end_date": "20241231"
}
```

### 修改无风险利率
```json
{
    "risk_free_rate": 0.025  # 2.5%
}
```

## ❓ 常见问题

### Q: 出现"积分不足"错误怎么办？
A: 需要购买Tushare Pro账号的积分，2000积分起购。访问 [Tushare官网](https://tushare.pro) 购买。

### Q: 如何获取Tushare Token？
A: 注册Tushare Pro账号后，在个人中心获取Token。

### Q: 支持哪些ETF代码？
A: 支持所有在Tushare中有数据的ETF，格式为`代码.交易所`（如`510050.SH`）。

### Q: 如何添加新的评估指标？
A: 在 `src/evaluator.py` 的 `PortfolioEvaluator` 类中添加新的计算方法。

### Q: 数据获取失败怎么办？
A: 检查网络连接、Token有效性、积分余额，以及ETF代码和时间范围的正确性。

## 📈 示例分析

### 典型输出结果
```
🎯 最优组合表现:
• 最大夏普比率: 0.6523
• 年化收益率: 12.34%
• 年化波动率: 15.67%
• 最大回撤: -18.23%

⚖️ 最优权重分配:
• 510050.SH: 45.23%
• 510300.SH: 32.67%
• 510500.SH: 22.10%
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License

## 🙏 致谢

- [Tushare](https://tushare.pro) - 提供高质量的金融数据
- [CVXPY](https://www.cvxpy.org) - 优秀的凸优化库
- [Matplotlib](https://matplotlib.org) - 强大的可视化库

---

**注意**: 本工具仅供研究和学习使用，不构成投资建议。投资有风险，入市需谨慎。