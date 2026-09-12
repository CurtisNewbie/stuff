# OpenCode Configuration Repository Usage Guide

This document records the setup and usage knowledge for the opencode configuration repository.

**Repository Purpose**:
- Centralized management of opencode project configurations, commands, skills, and plugins
- Provides a versionable configuration management solution
- Supports synchronization to the global opencode environment (~/.opencode/ and ~/.config/opencode/)

**Main Components**:
- AGENTS.md - agent configuration and user requirements (use AGENTS_curr.md)
- commands/ - custom command definitions
- skills/ - custom agent skills
- opencode.jsonc - opencode core configuration
- sync.sh - synchronization script
- plugin/ - plugin-related configuration
- oh-my-opencode-slim.json - oh-my-opencode-slim configuration preset

**Theme Preference**:
- Preferred OpenCode theme: Everforest

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

## Matt Pocock 工程 Skills 包 (mattpocock/skills)

面向真实工程实践的 skill 合集（TDD、领域建模、代码审查、架构改善等），Stars 154k。

**安装前先询问用户是否需要**，该包有自己的初始化流程，属于有观点的工程框架，不适合所有项目。

```bash
npx skills@latest add mattpocock/skills
# 安装后在 agent 中运行：/setup-matt-pocock-skills

# 安装单个 skill（如 handoff 交接文档 skill）
npx skills add github.com/mattpocock/skills/tree/main/skills/productivity/handoff -g
```

**官方仓库**: https://github.com/mattpocock/skills

### 批量安装指定 Skills

`--skill` 支持空格分隔多个 skill 名，无需完整路径，CLI 会在整个仓库中匹配：

```bash
npx skills@latest add mattpocock/skills --skill codebase-design diagnosing-bugs domain-modeling grill-me grill-with-docs grilling handoff implement improve-codebase-architecture research setup-matt-pocock-skills tdd to-spec to-tickets triage wayfinder writing-for-agents -g -y
```

对应目录：
- `skills/engineering/`: codebase-design, diagnosing-bugs, domain-modeling, grill-with-docs, implement, improve-codebase-architecture, research, setup-matt-pocock-skills, tdd, to-spec, to-tickets, triage, wayfinder
- `skills/productivity/`: grill-me, grilling, handoff, writing-for-agents
