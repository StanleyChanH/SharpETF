# 贡献指南

感谢您对SharpETF项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题
- 使用[GitHub Issues](https://github.com/StanleyChanH/SharpETF/issues)报告bug
- 提供详细的问题描述和复现步骤
- 包含相关的错误日志和截图

### 功能建议
- 在Issues中描述新功能的需求和用例
- 解释功能的业务价值和技术实现思路
- 提供相关的参考资料或示例

### 代码贡献

#### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/StanleyChanH/SharpETF.git
cd SharpETF

# 创建开发分支
git checkout -b feature/your-feature-name

# 设置环境
conda create -n sharpetf-dev python=3.9 -y
conda activate sharpetf-dev
pip install -r requirements.txt
```

#### 代码规范
- 遵循PEP 8 Python代码风格
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串
- 确保代码通过基本测试

#### 提交流程
1. Fork本项目到您的GitHub账户
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建Pull Request

## 📋 贡献类型

### 🐛 Bug修复
- 修复已知问题
- 改进错误处理
- 优化性能问题

### ✨ 新功能开发
- 新的量化指标
- 额外的优化策略
- 增强的可视化功能
- 新的数据源支持

### 📚 文档改进
- 更新README和文档
- 添加代码注释
- 改进使用指南
- 翻译文档

### 🧪 测试用例
- 单元测试
- 集成测试
- 性能测试
- 边界条件测试

### 🔧 性能优化
- 算法优化
- 内存使用优化
- 并行处理改进
- 缓存机制优化

## 📝 提交规范

### 提交信息格式
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### 类型说明
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例
```
feat(optimizer): 添加新的风险平价优化策略

- 实现基于风险贡献均等的权重分配算法
- 支持自定义风险约束条件
- 添加性能对比分析

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
```

## 🧪 测试要求

### 运行测试
```bash
# 基本功能测试
python main.py

# 检查代码质量
python -m py_compile src/*.py

# 检查导入
python -c "import main; print('导入成功')"
```

### 测试覆盖
- 确保新功能不会破坏现有功能
- 测试边界条件和异常情况
- 验证中文显示和字体配置
- 检查输出文件的完整性

## 📖 代码审查

### 审查要点
- [ ] 代码符合项目风格
- [ ] 功能实现正确
- [ ] 错误处理完善
- [ ] 文档更新完整
- [ ] 测试覆盖充分
- [ ] 性能影响可接受

### 审查流程
1. 自动化检查通过
2. 至少一个维护者审查
3. 解决所有审查意见
4. 合并到主分支

## 🏷️ 发布流程

### 版本管理
- 遵循[语义化版本](https://semver.org/)
- 主版本：不兼容的API变更
- 次版本：向后兼容的功能性新增
- 修订版本：向后兼容的问题修正

### 发布检查清单
- [ ] 所有测试通过
- [ ] 文档更新完整
- [ ] 版本号更新正确
- [ ] 变更日志更新
- [ ] 标签创建正确

## 🤝 社区准则

### 行为准则
- 尊重所有参与者
- 保持友好和专业的沟通
- 接受建设性的反馈
- 专注于对社区最有利的事情

### 沟通渠道
- GitHub Issues: 问题报告和功能请求
- Pull Request: 代码审查和讨论
- Discussions: 一般讨论和想法分享

## 📞 联系方式

- 项目维护者: [StanleyChanH](https://github.com/StanleyChanH)
- 问题反馈: [GitHub Issues](https://github.com/StanleyChanH/SharpETF/issues)
- 技术讨论: [GitHub Discussions](https://github.com/StanleyChanH/SharpETF/discussions)

---

感谢您的贡献！您的参与让这个项目变得更好。