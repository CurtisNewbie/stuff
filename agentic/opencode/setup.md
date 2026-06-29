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

---

## RTK - Token 优化工具 (rtk)

RTK (Rust Token Killer) 是一个高性能 CLI 代理工具，可将 LLM 的 token 消耗降低 60-90%。它通过过滤和压缩命令输出，在常见开发命令上实现显著的 token 节省。

### 安装步骤

**方法 1: 快速安装（推荐）**

```bash
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
```

**方法 2: 手动下载二进制文件**

```bash
# macOS ARM64 (Apple Silicon)
curl -L -o rtk.tar.gz https://github.com/rtk-ai/rtk/releases/latest/download/rtk-aarch64-apple-darwin.tar.gz
tar -xzf rtk.tar.gz
chmod +x rtk
sudo mv rtk /usr/local/bin/

# macOS Intel
curl -L -o rtk.tar.gz https://github.com/rtk-ai/rtk/releases/latest/download/rtk-x86_64-apple-darwin.tar.gz
tar -xzf rtk.tar.gz
chmod +x rtk
sudo mv rtk /usr/local/bin/

# Linux ARM64
curl -L -o rtk.tar.gz https://github.com/rtk-ai/rtk/releases/latest/download/rtk-aarch64-unknown-linux-gnu.tar.gz
tar -xzf rtk.tar.gz
chmod +x rtk
sudo mv rtk /usr/local/bin/

# Linux x86_64
curl -L -o rtk.tar.gz https://github.com/rtk-ai/rtk/releases/latest/download/rtk-x86_64-unknown-linux-musl.tar.gz
tar -xzf rtk.tar.gz
chmod +x rtk
sudo mv rtk /usr/local/bin/
```

**方法 3: 使用 Cargo**

```bash
cargo install --git https://github.com/rtk-ai/rtk
```

### 初始化 OpenCode 集成

```bash
# 为 OpenCode 安装 RTK hook
rtk init -g --opencode

# 重启 OpenCode
```

### 验证安装

```bash
rtk --version    # 检查版本
rtk gain         # 查看 token 节省统计
```

### 工作原理

RTK 通过 TypeScript 插件拦截 OpenCode 的 `tool.execute.before` 事件，自动将 shell 命令重写为 RTK 等价命令：

```
git status      → rtk git status
cargo test      → rtk cargo test
ls -la          → rtk ls -la
```

OpenCode 看不到重写过程，只是获得压缩后的输出，实现透明的 token 优化。

### 支持的命令类别

RTK 支持 100+ 常用开发命令，主要类别包括：

- **文件操作**: `ls`, `cat`, `find`, `grep` (-70-80% tokens)
- **Git 操作**: `git status`, `git log`, `git diff`, `git commit` (-70-90% tokens)
- **测试运行器**: `pytest`, `cargo test`, `go test`, `vitest` (-90% tokens)
- **构建工具**: `cargo build`, `npm`, `make` (-70-90% tokens)
- **语言服务器**: `tsc`, `mypy` (-80-83% tokens)
- **代码检查**: `eslint`, `ruff`, `golangci-lint`, `biome` (-80-85% tokens)
- **包管理器**: `pip`, `cargo install`, `pnpm list` (-75-80% tokens)
- **容器**: `docker ps`, `docker logs`, `kubectl pods` (-80% tokens)
- **AWS**: `aws sts`, `aws ec2`, `aws lambda` (结构化输出)

### 使用示例

```bash
# 查看节省统计
rtk gain                    # 摘要统计
rtk gain --graph            # ASCII 图表（最近 30 天）
rtk gain --history          # 最近命令历史
rtk gain --daily            # 按天分解

# 发现节省机会
rtk discover                # 查找错过的节省机会
rtk discover --all --since 7 # 所有项目，最近 7 天

# 直接使用 RTK 命令
rtk ls .                    # Token 优化的目录树
rtk read file.rs            # 智能文件读取
rtk grep "pattern" .        # 分组搜索结果
rtk git status              # 紧凑状态
rtk cargo test              # 紧凑测试输出
```

### 典型节省效果

在一个 30 分钟的会话中，RTK 可以实现：

| 操作类别 | 频率 | 标准 token | RTK token | 节省 |
|---------|------|-----------|----------|------|
| `ls` / `tree` | 10x | 2,000 | 400 | -80% |
| `cat` / `read` | 20x | 40,000 | 12,000 | -70% |
| `grep` / `rg` | 8x | 16,000 | 3,200 | -80% |
| `git status` | 10x | 3,000 | 600 | -80% |
| `git diff` | 5x | 10,000 | 2,500 | -75% |
| `git log` | 5x | 2,500 | 500 | -80% |
| `cargo test` / `npm test` | 5x | 25,000 | 2,500 | -90% |
| **总计** | | **~118,000** | **~23,900** | **-80%** |

### 配置文件

`~/.config/rtk/config.toml` (macOS: `~/Library/Application Support/rtk/config.toml`):

```toml
[hooks]
exclude_commands = ["curl", "playwright"]  # 跳过这些命令的重写

[tee]
enabled = true          # 失败时保存原始输出（默认：true）
mode = "failures"       # "failures", "always", 或 "never"
```

### 卸载

```bash
rtk init -g --uninstall     # 移除 hook、RTK.md、settings.json 条目
cargo uninstall rtk          # 移除二进制文件（如果通过 cargo 安装）
sudo rm /usr/local/bin/rtk   # 手动移除二进制文件（如果手动安装）
```

**官方文档**: https://github.com/rtk-ai/rtk
**用户指南**: https://www.rtk-ai.app/guide

---

## Excalidraw 图表生成 (excalidraw-diagram-generator)

从自然语言描述生成 Excalidraw 格式图表，输出可直接在 Excalidraw 中打开的 `.excalidraw` JSON 文件。

### 安装步骤

```bash
npx skills add https://github.com/github/awesome-copilot --skill excalidraw-diagram-generator -g -y
```

**无需额外依赖**，直接触发 skill 即可使用。

### 支持的图表类型

- **流程图 (Flowchart)**: 顺序流程、工作流、决策树
- **关系图 (Relationship)**: 实体关系、系统组件、依赖关系
- **思维导图 (Mind Map)**: 概念层级、头脑风暴、主题组织
- **架构图 (Architecture)**: 系统设计、模块交互、数据流
- **数据流图 (DFD)**: 数据流可视化、数据转换过程
- **泳道图 (Swimlane)**: 跨职能工作流、基于角色的流程
- **类图 (Class Diagram)**: 面向对象设计、类结构与关系
- **时序图 (Sequence Diagram)**: 交互时序、消息传递
- **ER 图 (ER Diagram)**: 数据库实体关系

### 触发场景

- 「创建一个展示...的图表」
- 「画一个...的流程图」
- 「可视化...的架构」
- 「生成...的思维导图」
- 「用 Excalidraw 画出...」

---

## LLM Wiki 知识库 (karpathy-llm-wiki)

将文档、网页、论文等原始资料编译为结构化 wiki 知识页面，支持带引用的知识查询。与 RAG 的区别：在 ingest 阶段就合成知识，形成可复利的 markdown 页面，而非每次查询时检索原始片段。

### 安装步骤

```bash
npx add-skill Astro-Han/karpathy-llm-wiki
```

### 工作原理

```
your-project/
├── raw/        ← 不可变的原始资料
└── wiki/
    ├── topic/  ← LLM 维护的知识页面
    ├── index.md
    └── log.md  ← 追加式操作日志
```

三个核心操作：

| 操作 | 说明 |
|---|---|
| **Ingest** | 拉取原始资料到 `raw/`，编译/更新 `wiki/` 知识页面 |
| **Query** | 搜索 wiki，返回带引用的答案 |
| **Lint** | 检查索引完整性、断链、过期交叉引用，自动修复 |

### 触发场景

- 构建个人/团队知识库（网页、论文、PDF、笔记）
- 需要基于自己合成知识库的带引用回答
- 构建有界、可维护的知识库（替代 RAG）

**源码**：https://github.com/Astro-Han/karpathy-llm-wiki

---

## 消息延迟队列 (open-queue)

OpenCode 插件，在模型运行中途将后续消息放入队列，等模型完成后按序发送，避免打断当前执行上下文。

### 安装步骤

```bash
bun x @0xsero/open-queue
# 或
npx @0xsero/open-queue
```

自动写入 `opencode.json` 并注册 `/queue` 命令。

### 使用方式

```
/queue hold       # 开启队列模式
/queue immediate  # 恢复正常模式（冲刷队列）
/queue status     # 查看当前模式
```

也可通过环境变量默认开启：

```bash
OPENCODE_MESSAGE_QUEUE_MODE=hold opencode
```

### 触发场景

- 模型执行长任务时，想追加补充说明而不打断它
- 发现遗漏信息，希望等当前任务完成后再处理

**注意**：hold 模式下消息在 UI 中会短暂显示为已发送后重发，属于视觉问题，模型只收到一次。

**源码**：https://github.com/0xSero/open-queue

---

## 代码知识图谱 (codegraph)

为 agent 提供预索引的代码知识图谱，减少 grep/read 工具调用，降低 token 消耗。

**效果**：平均节省 ~35% 费用，减少 ~71% 工具调用，100% 本地运行。

### 安装步骤

```bash
# 安装并配置（自动检测 opencode）
npx @colbymchenry/codegraph install --target=opencode --yes

# 重启 opencode

# 在每个项目目录下初始化索引
cd your-project
codegraph init -i
```

### 工作原理

在项目根目录存在 `.codegraph/` 时，agent 可使用以下 MCP 工具：

| 工具 | 用途 |
|---|---|
| `codegraph_context` | 映射功能/区域，一次调用替代多次 grep |
| `codegraph_search` | 按名称快速查找符号 |
| `codegraph_trace` | 跨文件追踪调用路径 |
| `codegraph_explore` | 一次调用查看多个相关符号源码 |
| `codegraph_callers` / `codegraph_callees` | 逐跳遍历调用图 |
| `codegraph_impact` | 编辑前查看影响范围 |
| `codegraph_node` | 获取单个符号的源码/签名 |

索引通过文件监听自动同步，无需手动运行 `codegraph sync`。

**官方文档**: https://github.com/colbymchenry/codegraph