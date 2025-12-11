# 书籍内容核查工具

这是一个用于检查书籍内容准确性的Python工具，特别针对物理学和数学内容设计，能够检查公式、定理、概念表述等是否符合学术标准。

## 功能特点

- 🔍 **自动内容检查**: 检查物理概念、数学公式、定理表述的准确性
- 🧮 **公式验证**: 自动提取并验证LaTeX数学公式
- 📚 **学术标准**: 确保内容符合物理学学术规范
- 📝 **详细报告**: 生成完整的问题报告和修正建议
- 🔄 **批量处理**: 支持同时检查多个文件

## 安装依赖

```bash
# 选择一个（或两个）模型库安装
pip install anthropic  # 使用Claude模型
pip install openai     # 使用GPT模型

# 可选: 安装多模型支持
pip install anthropic openai
```

## 使用方法

### 1. 设置API密钥

#### 方式一：使用配置向导（推荐）
```bash
# 运行交互式配置工具
python3 setup_api_key.py

# 或快速配置
python3 quick_setup.py
```

#### 方式二：手动设置环境变量
```bash
# 使用Claude模型 (推荐)
export ANTHROPIC_API_KEY="你的密钥"

# 或使用GPT模型
export OPENAI_API_KEY="你的密钥"
```

### 2. 一键运行检查

最简单的方式是使用一键检查脚本：

```bash
python run_checker.py
```

### 3. 高级使用

使用 `content_checker.py` 进行更详细的配置：

```bash
# 使用特定模型
python content_checker.py --model anthropic

# 指定文件夹
python content_checker.py --original-folder MyOriginal --examined-folder MyChecked

# 使用自定义API密钥
python content_checker.py --api-key "你的密钥"
```

## 文件结构

```
.
├── Originial/           # 原始书籍文件
│   ├── Chapter5_1_Section.md
│   └── ...
├── Examinied/          # 检查结果输出文件夹
│   ├── Chapter5_1_Section_checked.md
│   └── ...
├── content_checker.py  # 主检查程序
├── run_checker.py      # 一键运行脚本
├── config.json         # 配置文件
└── README_checker.md   # 本说明文档
```

## 检查内容

工具会检查以下方面：

1. **物理概念准确性**
   - 统计物理基本概念
   - 伊辛模型的物理意义
   - 相变理论

2. **数学公式验证**
   - LaTeX公式语法
   - 数学推导正确性
   - 物理量单位

3. **定理和命题**
   - 表述准确性
   - 适用条件
   - 证明流程

4. **历史事实**
   - 物理学家名字
   - 发现年份
   - 重要贡献

5. **专业术语**
   - 使用规范性
   - 一致性
   - 定义准确性

## 检查报告格式

每个文件的检查报告包含：
- 原文件名和检查日期
- 总体评价
- 发现的问题（分类列出）
- 修正建议
- 修改后的完整版本

## 注意事项

1. **API配额**: 大模型API调用有配额限制，避免批量处理过大的文件
2. **处理时间**: 每个文件可能需要几分钟时间，请耐心等待
3. **知识截止**: 大模型有知识截止时间，对于最新的研究进展可能不了解
4. **人工确认**: 机器检查结果需要人工最终确认，特别是关键公式和定理

## 故障排除

## API密钥获取指南

### Anthropic (Claude) - 推荐
1. 访问 https://console.anthropic.com/
2. 注册/登录账号
3. 进入API密钥管理页面
4. 点击创建新密钥
5. 复制密钥并开始使用

### OpenAI (GPT)
1. 访问 https://platform.openai.com/api-keys
2. 登录OpenAI账号
3. 点击 "Create new secret key"
4. 复制密钥（注意：只能查看一次）

### API调用失败
```
错误: API调用失败: ...
```
- 检查API密钥是否正确设置
- 确认网络连接正常
- 等待几分钟后重试（可能API限速）

### 文件读取失败
```
错误: 文件读取失败: ...
```
- 确认文件编码为UTF-8
- 检查文件权限
- 确认文件没有损坏

### 检查结果不准确
- 可以多次运行检查取多数结果
- 对于争议性内容，建议查阅原始文献
- 重要内容建议咨询相关领域专家

## 联系与支持

如有问题，请通过以下方式获取支持：
- 检查GitHub Issues
- 查看API提供商的文档
- 确保所有依赖已正确安装

---

**注意**: 本工具旨在辅助内容检查，不能替代专业的学术审查。对于关键内容，仍建议咨询相关领域的专业人士。