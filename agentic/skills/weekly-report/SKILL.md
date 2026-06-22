---
name: weekly-report
description: 帮助用户整理和撰写个人周报。将原始的工作笔记、任务列表或聊天记录转化为结构化的周报，每个事项使用 3W2H 框架展开说明，突出工作能力和关键成果，输出格式与团队飞书周报表格对齐（重点项目列 + 任务描述列）。触发场景：用户提到"写周报"、"整理本周工作"、"帮我写周报"、"生成周报"、"整理周报"，或提供一堆工作记录需要整理成周报时使用。
---

# Weekly Report Skill

## 核心要求

本技能遵循 Leader 的周报规范：
- **附需求链接**，但不只贴链接——展开工作内容，说清楚目标、进度和结果
- 每个工作事项用 **3W2H** 框架展开（What/Why/When/How，How Much 内部参考不输出）
- 突出**做了什么能力/达到什么结果**，而不是复述需求标题
- **按项目分类**：相同项目的需求归为一组, 主动问用户是否已有大的项目类目，按用户提供为主

## 输出目标：团队飞书周报表格

用户只需填写表格中两列，skill 的输出应直接对应这两列：

| 列 | 内容 |
|----|------|
| **重点项目** | 项目名 + 项目级 context（本周整体进展、关键指标、风险/阻塞）|
| **任务描述** | `（进度%）` + 3W2H bullet points，每个需求一段 |

## 3W2H 框架

每个工作事项需包含：

| 维度 | 含义 | 关键问题 |
|------|------|---------|
| **What** | 问题/任务的本质 | 本质上做了什么能力？解决了什么问题？ |
| **Why** | 原因/背景 | 为什么要做这件事？背景是什么？ |
| **When** | 时间节点 | 关键节点/里程碑/完成时间是什么？ |
| **How** | 解决方案 | 采用什么方案/方法解决？ |

## 工作流

### Step 1：收集输入

**如果用户没有提供任何内容或链接，先询问：**

> 「需要帮你自动查询本周飞书项目中的需求并直接生成周报吗？如果有额外的笔记或资料，也可以一并提供。」

用户确认后，直接运行脚本（会自动读取 `FEISHU_GANTT_URL` 环境变量）：

```bash
python3 scripts/fetch_feishu_tasks.py
```

**如果用户提供了飞书项目需求链接，用脚本提取：**

```bash
python3 scripts/fetch_feishu_tasks.py \
  "https://project.feishu.cn/xxx/story/detail/XXXX" \
  "https://project.feishu.cn/xxx/story/detail/YYYY"
```

**如果用户提供了甘特图视图链接：**

```bash
python3 scripts/fetch_feishu_tasks.py --gantt "https://project.feishu.cn/xxx/userGantt/VIEW_ID"
# 指定周：--week 2026-06-16
```

脚本通过 `chromedb` 从 Chrome Default profile 读取 cookies，无需额外认证。
输出 JSON，每条需求包含 `title`、`description`、`tasks`（名称/估分/状态）、`total_points`。

用户也可以提供任意格式的补充内容，与脚本抓取结果合并处理：
- 零散的工作笔记或 bullet points
- 任务列表（含完成状态）
- 聊天记录片段
- 飞书项目需求链接（可自动提取任务详情）

**如果信息仍不清晰，再询问：**
- 事项背景/原因不明时，询问 Why
- 时间节点不明时，询问完成时间或当前进展

### Step 2：收集项目级 Context

在整理每个项目分组前，**必须询问用户**：

> 「[项目名] 这个项目，本周有没有需要在周报里体现的整体进展、关键指标或风险？（例如：测试覆盖率变化、阻塞点、下周关键节点等）」

这部分内容会放在「重点项目」列的项目名下方，作为项目级总结。如用户说没有，则只填项目名。

### Step 3：整理与扩展

将每个工作事项按 3W2H 展开。参考 `references/template.md` 中的结构和示例。

**质量要求：**
- What 必须描述**能力/成果**，不只是任务名称
- Why 要体现业务价值或技术背景
- How 要有具体的技术方案或操作路径，不能泛泛而谈
- 语言简洁专业，使用中文

### Step 4：生成输出

按项目分组输出，每个项目包含：
1. **【重点项目列】** 项目名 + 项目级 context（Step 2 收集）
2. **【任务描述列】** 每个需求单独一段：`（进度%）` + What/Why/When/How

参考 `references/template.md` 中的示例格式。

### Step 5：生成重点项目进展更新

对于 **重点事项** 跟踪表，每周需同步更新「关键进展（截止MMDD）」列。

**格式：**
```
MM/DD 进度：
- [关键结果/当前状态]
- [当前阻塞（如有）]
- [接下来]
```

**要求：**
- 比 3W2H 更简洁，不需要 Why/How
- 聚焦：**做了什么、现状如何、下一步是什么**
- 有量化数据的必须带上（如测试集覆盖率从 X% 上升至 Y%）

基于 Step 1 收集的内容和 Step 2 的项目级 context，为每个有进展的行生成关键进展更新。

## 参考资料

- 报告模板和示例：见 `references/template.md`
- How Much 自动提取脚本：见 `scripts/fetch_feishu_tasks.py`

## 脚本说明

### fetch_feishu_tasks.py

从飞书项目自动发现或手动指定需求，提取后端开发任务数据（标题、描述、子任务、工时）。

**前置条件：** `chromedb` 已安装并在 PATH + Chrome 已登录飞书项目

**用法：**

```bash
# 无参数：自动读取 FEISHU_GANTT_URL 环境变量，发现本周需求（推荐）
python3 scripts/fetch_feishu_tasks.py

# 甘特图视图自动发现（等同于设置环境变量）
python3 scripts/fetch_feishu_tasks.py --gantt <gantt_url>
python3 scripts/fetch_feishu_tasks.py --gantt <gantt_url> --week 2026-06-16

# 手动指定需求 URL
python3 scripts/fetch_feishu_tasks.py <story_url> [story_url ...]
```

**工作原理：** 通过 `chromedb` 读取 Chrome Default profile 的加密 cookies（配合 macOS Keychain 自动解密），直接调用飞书项目 API，无需打开浏览器。

**输出字段：**
- `title`：需求标题
- `description`：需求描述（用于理解 What/Why）
- `tasks[]`：后端开发子任务（name / status / points / start / end）
- `total_points`：本周子任务人天合计

**已知限制：**
- 仅支持 macOS（依赖 Keychain 解密）
- Chrome 需保持登录状态（cookies 未过期）
