# AI番茄写作助手

基于 MiniMax M2.5 的 AI 写作助手，支持自动写作、自动检查、记忆更新等功能，适用于番茄小说平台的长篇连载创作。

## 功能特性

### 🤖 AI 自动写作
- 基于 MiniMax M2.5 模型生成高质量章节
- 支持自定义本章目标、情绪基调、结尾钩子
- 可配置目标字数、对话比例、写作节奏
- 流式输出，边生成边显示

### 🔍 AI 自动检查
- **一致性检查**: 检测角色生死状态、境界、装备矛盾
- **违禁词检查**: 政治敏感、色情低俗、暴力血腥全覆盖
- **文风检查**: 句式重复度、AI机械感检测
- **质量检查**: 字数校验、标题生成、结尾钩子检测

### 🧠 记忆系统
- 5层上下文自动组装（设定+大纲+人物+事件+近期原文）
- 章节确认后自动生成100字摘要
- 自动提取人物状态变化
- 关键事件与伏笔追踪

### 📊 成本控制
- Token 消耗统计与可视化
- 每日调用上限设置
- 成本预警提醒

### 📤 导出功能
- 支持 TXT、HTML 格式导出
- 复制为番茄编辑器兼容格式
- 违禁词高亮显示

## 技术栈

- **语言**: Python 3.10+
- **AI模型**: MiniMax M2.5
- **界面**: PyQt6
- **数据库**: SQLite + SQLAlchemy

## 项目结构

```
ai_xiaosuo/
├── config.py          # 配置文件
├── main.py            # 应用入口
├── models/            # 数据库模型
│   ├── project.py    # 项目模型
│   ├── chapter.py    # 章节模型
│   ├── character.py  # 人物模型
│   ├── event.py      # 事件模型
│   ├── outline.py    # 大纲模型
│   └── foreshadowing.py # 伏笔模型
├── api/              # API 封装
│   ├── minimax_client.py  # MiniMax 客户端
│   └── prompts.py    # Prompt 模板
├── core/             # 核心业务
│   ├── context_assembler.py  # 上下文组装
│   ├── chapter_generator.py  # 章节生成
│   ├── memory_updater.py     # 记忆更新
│   └── cost_tracker.py       # 成本追踪
├── checkers/         # AI 检查模块
│   ├── consistency_checker.py # 一致性检查
│   ├── content_filter.py      # 违禁词过滤
│   ├── style_checker.py      # 文风检查
│   └── quality_checker.py     # 质量检查
├── ui/               # 界面组件
│   ├── main_window.py     # 主窗口
│   ├── writing_panel.py   # 写作面板
│   ├── check_panel.py     # 检查面板
│   └── project_panel.py   # 项目面板
└── export/           # 导出模块
    └── tomato_exporter.py # 番茄平台导出
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 API Key

设置环境变量：

```bash
export MINIMAX_API_KEY="your-api-key"
```

### 运行应用

```bash
python ai_xiaosuo/main.py
```

## 使用指南

### 1. 创建项目

1. 点击"新建项目"按钮
2. 填写项目名称、类型、目标平台
3. 设置世界观、主角设定、文风要求

### 2. 管理人物

1. 在项目面板点击"新建人物"
2. 填写人物名称、角色类型、境界等信息
3. 人物状态会在章节确认后自动更新

### 3. 生成章节

1. 选择目标章节序号
2. 填写本章写作目标
3. 设置情绪基调、结尾钩子
4. 点击"生成章节"
5. 生成完成后可编辑内容
6. 确认无误后点击"确认章节"

### 4. 内容检查

1. 切换到"AI检查"面板
2. 点击"开始检查"
3. 查看各项检查结果
4. 根据建议修改内容

### 5. 导出发布

1. 切换到"导出"功能
2. 选择导出格式（TXT/HTML/剪贴板）
3. 如有违禁词会有高亮提示
4. 复制到番茄小说编辑器发布

## 配置说明

在 `ai_xiaosuo/config.py` 中可调整以下配置：

```python
# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_MODEL = "abab6.5s-chat"  # 模型名称

# Token 限制
MAX_INPUT_TOKENS = 8000  # 最大输入 Token
TARGET_CHAPTER_LENGTH = 3000  # 目标章节字数
MIN_CHAPTER_LENGTH = 1800  # 最低章节字数

# 成本设置
TOKEN_COST_INPUT = 0.5   # 输入每百万 Token 成本($)
TOKEN_COST_OUTPUT = 1.0  # 输出每百万 Token 成本($)
DAILY_TOKEN_LIMIT = 5000000  # 每日 Token 限制
```

## 违禁词库

内置违禁词库覆盖以下类别：

- 政治敏感
- 色情低俗
- 暴力血腥
- 违规题材

可通过自定义词库扩展：

```python
from ai_xiaosuo.checkers import ContentFilter

filter = ContentFilter(custom_words_path="path/to/words.txt")
filter.add_custom_word("自定义词", "politics", "high")
```

## 注意事项

1. **API Key**: 使用前请确保已配置有效的 MiniMax API Key
2. **内容审核**: AI 生成内容仍需人工审核
3. **成本控制**: 建议设置每日预算避免超额使用
4. **数据备份**: 定期备份数据库文件 `ai_xiaosuo/data/ai_xiaosuo.db`

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
