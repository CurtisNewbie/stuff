# OpenCode Configuration Repository Usage Guide

This document records the setup and usage knowledge for the opencode configuration repository.

**Repository Purpose**:
- Centralized management of opencode project configurations, commands, skills, and plugins
- Provides a versionable configuration management solution
- Supports synchronization to the global opencode environment (~/.opencode/ and ~/.config/opencode/)

**Main Components**:
- AGENTS.md - agent configuration and user requirements
- commands/ - custom command definitions
- skills/ - custom agent skills
- opencode.jsonc - opencode core configuration
- sync.sh - synchronization script
- plugin/ - plugin-related configuration
- oh-my-opencode-slim.json - oh-my-opencode-slim configuration preset

---

## Oh My OpenCode Slim Installation

**Description**: oh-my-opencode-slim is a multi-agent programming system that provides specialized agent roles for OpenCode (orchestrator, oracle, librarian, explorer, designer, fixer), significantly improving programming efficiency.

### Installation Steps

1. **Run the installer** (recommended non-interactive mode):

```bash
bunx oh-my-opencode-slim@latest install --no-tui --tmux=no --skills=yes
```

**Option descriptions**:
- `--no-tui`: non-interactive mode
- `--tmux=no`: do not install tmux integration
- `--skills=yes`: install preset skills
- `--reset`: force override existing configuration (creates `.bak` backup)

2. **Authenticate with provider**:

```bash
opencode auth login
```

Select your provider and complete the OAuth flow.

3. **Verify installation**:

```bash
opencode
ping all agents
```

Confirm that all agents respond correctly.

### Configuration File Notes

- **Current preset**: `oh-my-opencode-slim.json` - configuration preset in this repository
- **Actual usage**: `~/.config/opencode/oh-my-opencode-slim.json` - global configuration after installation
- **Post-installation update**: by default, existing configuration files are not overwritten during installation; use `--reset` to force override (automatic backup)

**Note**: After installation, `~/.config/opencode/oh-my-opencode-slim.json` is updated based on system configuration and may differ from the preset file in the repository. When adjusting configuration, modify the global configuration file.

---

## Notification System (kdco/notify)

Push system notifications when AI tasks complete, encounter errors, or require permissions.

**Important**: This plugin should be installed globally, not locally for the project.

**Detailed documentation**: See [ocx-notify.md](./ocx-notify.md) for complete installation steps, configuration options, and usage instructions.

---

## Feishu/Lark Document Support (lark-cli)

If you need to read, write, or edit Feishu/Lark documents, messages, calendars, etc., you can configure the Feishu official CLI tool and skills.

### Installation Steps

```bash
# 1. Install CLI tool
npm install -g @larksuite/cli

# 2. Install CLI Skills (required)
npx skills add larksuite/cli -y -g

# 3. Configure app credentials (user completes in browser)
lark-cli config init --new

# 4. Login authentication (user completes in browser)
lark-cli auth login --recommend
```

### Main Skills

- `lark-doc` - create, read, update, search documents (Markdown-based)
- `lark-im` - send/reply messages, group chat management, message search, file upload/download
- `lark-calendar` - schedule viewing, event creation, meeting arrangement
- 17 other skills (sheets, base, tasks, mail, wiki, etc.)

**Official documentation**: https://github.com/larksuite/cli

**Note**: If you don't need to interact with Feishu/Lark, you can skip this configuration.

---

## 浏览器自动化 (agent-browser)

让 AI agent 可以操控浏览器，完成网页交互、表单填写、截图、数据抓取等任务。

### 安装步骤

```bash
# 安装 CLI
npm install -g agent-browser

# 下载 Chrome（首次使用）
agent-browser install

# 安装 Skill
npx skills add agent-browser -g -y
```

### 触发场景

- 打开网站、点击按钮、填写表单
- 截图、抓取页面数据
- 测试 Web 应用
- 自动化登录和会话管理

---

## PDF 处理 (pdf)

提供 PDF 文件的全套处理能力：提取文字/表格、创建新 PDF、合并/拆分文档、填写表单。

### 依赖安装

```bash
# Python 库
pip install pypdf pdfplumber reportlab

# 命令行工具（macOS）
brew install poppler qpdf

# OCR 支持（可选）
pip install pytesseract pdf2image
```

### 触发场景

- 提取 PDF 文字或表格内容
- 合并、拆分、旋转 PDF
- 创建新 PDF 文档
- 填写 PDF 表单

---

## Word 文档处理 (docx)

创建、编辑、分析 .docx 文件，支持追踪修改（Redlining）、批注、格式保留和文字提取。

### 依赖安装

```bash
# 文字提取
brew install pandoc

# 创建新文档
npm install -g docx

# PDF 转换和图片预览
brew install libreoffice poppler
```

### 触发场景

- 从 Markdown 创建 Word 文档
- 编辑现有文档（含追踪修改）
- 提取文档内容
- 法律/合同文档审阅（Redlining 工作流）

---

## 去 AI 味写作 (humanizer)

识别并消除文本中的 AI 写作特征，使内容更自然、更像人类写作。基于 Wikipedia「AI 写作特征」指南。

**无需安装**，直接触发 skill 即可使用。

### 触发场景

- 编辑或审阅文本，使其听起来更自然
- 去除 AI 常见词汇（pivotal、vibrant、delve 等）
- 消除过度使用的破折号、三段式结构、空洞结尾
- 为文章注入真实的个性和观点

---

## 提示词工程 (prompt-engineering-patterns)

掌握高级提示词技术，提升 LLM 在生产环境中的性能、可靠性和可控性。

**无需安装**，直接触发 skill 即可使用。

### 触发场景

- 设计复杂的生产级提示词
- 实现 Chain-of-Thought、Few-Shot 等推理模式
- 使用 Pydantic 强制结构化输出
- 优化提示词性能和一致性
- 调试输出不稳定的提示词

---

## 创建自定义 Skill (skill-creator)

将专业知识、工作流或工具集成封装为可复用的 Skill，扩展 AI agent 的能力。

**无需安装**，直接触发 skill 即可使用。

### 触发场景

- 创建新的 skill 包
- 更新或迭代现有 skill
- 将重复性工作流封装为可分发的 .skill 文件

### 快速开始

```bash
# 初始化新 skill
python ~/.agents/skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-dir>

# 打包发布
python ~/.agents/skills/skill-creator/scripts/package_skill.py <path/to/skill-folder>
```

---

## 发现更多 Skills (find-skills)

搜索和安装来自开放 agent skills 生态的 skill 包。

**无需安装**，直接触发 skill 即可使用。

### 触发场景

- 询问「有没有能做 X 的 skill？」
- 寻找特定领域的工具或工作流
- 扩展 agent 能力

### 手动搜索

```bash
# 搜索 skill
npx skills find <关键词>

# 安装 skill（全局）
npx skills add <owner/repo@skill> -g -y
```

**浏览所有 skills**：https://skills.sh/