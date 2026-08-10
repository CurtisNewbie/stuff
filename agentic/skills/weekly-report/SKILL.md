---
name: weekly-report
description: 帮助用户整理和撰写个人周报。将原始的工作笔记、任务列表或聊天记录转化为结构化的周报，每个事项使用 3W2H 框架展开说明，突出工作能力和关键成果，输出格式与团队飞书周报表格对齐（重点项目列 + 任务描述列）。当 workingdir 指向个人工作记录目录、需要按周追加本地工作记录时也使用。触发场景：用户提到"写周报"、"整理本周工作"、"帮我写周报"、"生成周报"、"整理周报"，或提供一堆工作记录需要整理成周报时使用。
---

# Weekly Report Skill

## 核心要求

本技能遵循 Leader 的周报规范：
- **每个需求/事项都附可点击的 PRD/需求链接**，链接必须放在任务描述段落中，不可只放项目列；但不只贴链接——展开工作内容，说清楚目标、进度和结果
- 输入没有链接时不编造，明确标注 **「PRD链接：未提供」**
- **区分链接用途**：PRD/需求链接与任务名称、任务描述、用户笔记等来源中的交付物、产出、参考文档链接分开处理；先提取所有来源中的 URL，去重并归属到对应事项，任务名称中的 URL 不能当作普通文本丢弃
- PRD/需求链接按现有规则放在 `PRD链接` 中；任务内的 wiki、docs、Apifox、看板、代码仓库等链接保留在对应 What/How 或「产出/参考链接」中，并说明用途
- 无法判断链接用途时不得静默删除，保留链接并询问用户或标注「用途待确认」；输出前核对每个事项的输入 URL，除非明确判定为无关并说明原因，否则必须在输出中出现
- 每个工作事项用 **3W2H** 框架展开（What/Why/When/How，How Much 内部参考不输出）
- 突出**做了什么能力/达到什么结果**，而不是复述需求标题
- **按项目分类**：相同项目的需求归为一组, 主动问用户是否已有大的项目类目，按用户提供为主

## 输出目标：团队飞书周报表格

用户只需填写表格中两列，skill 的输出应直接对应这两列：

| 列 | 内容 |
|----|------|
| **重点项目** | 项目名 + 项目级 context（本周整体进展、关键指标、风险/阻塞）|
| **任务描述** | `（进度%）` + PRD/需求链接 + 产出/参考链接（如有）+ 3W2H bullet points，每个需求一段 |

## 3W2H 框架

每个工作事项需包含：

| 维度 | 含义 | 关键问题 |
|------|------|---------|
| **What** | 问题/任务的本质 | 本质上做了什么能力？解决了什么问题？ |
| **Why** | 原因/背景 | 为什么要做这件事？背景是什么？ |
| **When** | 时间节点 | 关键节点/里程碑/完成时间是什么？ |
| **How** | 解决方案 | 采用什么方案/方法解决？ |

### 链接保留检查清单

- [ ] 已从需求标题/描述、任务名称/描述、用户笔记及其他输入来源提取 URL，并按事项去重归属
- [ ] 每个事项的 PRD/需求链接已保留；没有则标注 `PRD链接：未提供`
- [ ] 任务内 wiki/docs/Apifox/看板/代码仓库等链接已在 What/How 或「产出/参考链接」中保留并说明用途
- [ ] 输出 URL 与输入 URL 已逐项核对；用途不明的链接已保留并标注或询问

## 工作流

### Step 1：收集输入

**先判断当前 `workingdir` 是否为个人工作记录目录：**

- 如果 `workingdir` 是个人工作记录目录，必须先询问用户：

  > 「当前 workingdir 是个人工作记录目录，是否要把本周工作记录追加到本地？只有你明确确认后才会写入；拒绝或不确认则只输出周报。」

- 只有用户明确回复“确认”“是”等同意内容后，才允许在本次流程中写入本地文件；不得用历史同意、上下文或默认行为代替确认。
- `workingdir` 不是个人工作记录目录，或用户拒绝/未明确确认时，不读取或写入本地工作记录，只输出周报。

**如果用户没有提供任何内容，先询问：**

> 「需要帮你自动查询本周飞书项目中的需求并直接生成周报吗？如果有额外的笔记或资料，也可以一并提供。」

收集每个需求/事项时，必须同时确认对应的可点击 PRD/需求链接。用户提供事项但没有提供链接时，在本阶段询问：

> 「这个事项对应的 PRD/需求链接是什么？如果没有，请确认标注“PRD链接：未提供”。」

用户仍未提供链接时，不得猜测或编造，后续在该事项的任务描述段落中标注 **「PRD链接：未提供」**，普通任务同样适用。

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
输出 JSON，每条需求包含 `url`（输入的 story URL）、`title`、`description`、`description_links`（描述中的 URL）、`tasks`（名称/链接/估分/状态）、`total_points`。

用户也可以提供任意格式的补充内容，与脚本抓取结果合并处理：
- 零散的工作笔记或 bullet points
- 任务列表（含完成状态）
- 聊天记录片段
- 飞书项目需求链接（可自动提取任务详情）

整理时将 Git 提交和文件修改证据与用户笔记、飞书数据交叉核对。仅凭提交标题或文件 mtime 无法确认背景、目标、结果或 PRD 时，必须按 Step 2 的 SOP 补充检查，不能臆造成果或编造 PRD 链接；PRD 链接规则保持不变。

**如果信息仍不清晰，再询问：**
- 事项背景/原因不明时，询问 Why
- 时间节点不明时，询问完成时间或当前进展

### Step 2：收集 Git 工作证据

Git 工作证据作为 Step 1 的补充输入来源。若设置了 `$WORK_REPO_PATH`，先扫描 `$WORK_REPO_PATH/aaas` 下的直接子目录仓库，再扫描 `$WORK_REPO_PATH` 下其他直接子目录仓库；不递归扫描所有嵌套目录。调用：

```bash
python3 scripts/fetch_git_work.py
# 可选：python3 scripts/fetch_git_work.py --repo-root /path/to/work --week-start 2026-06-16 --max-files 200
```

脚本默认读取 `WORK_REPO_PATH`，输出 JSON，包含：

- `week`：周一至周五日期范围
- `repo_root`：实际扫描根目录
- `scan_order` / `scanned_repositories`：仓库扫描顺序
- `repositories[]`：有提交或文件修改证据的仓库；包括生效 Git `identity`、本人 `commits`、本周 `modified_files`
- `warnings`：缺失身份或单仓库扫描错误

Git 身份必须按每个仓库生效的 `git config user.name` / `user.email` 读取，并对 commit **author** 的 name/email 做大小写不敏感的精确匹配；明确按 author 匹配，不按 committer 匹配，不能把其他人的提交算入本人名下。文件 mtime 只作为工作线索，不等同于提交或成果。无 `WORK_REPO_PATH` 时提示用户设置环境变量或使用 `--repo-root`；不要把扫描结果直接写入个人工作记录。

**Git 证据核查 SOP：**

1. 整理 Git 历史时，先阅读本人 commit message，判断工作意图。
2. 如果 commit message 不清楚，或不足以说明 What/Why/How/结果，检查该 commit 的 `git show` / `git diff`；必要时阅读变更涉及的相关代码和配置，确认实际行为。
3. 未提交修改只有 mtime 线索时，同样检查 `git diff` 和变更涉及的相关代码；mtime 只能作为时间线索，不得当作成果。
4. 只有 commit message、diff、相关代码和配置仍无法确认背景、目标、结果或进度时，才询问用户。已有充分证据时不要重复检查。
5. 形成周报任务描述时保留每个事项的 PRD 链接；缺失时标注 `PRD链接：未提供`，不能从 Git 信息推测或编造链接。

### Step 3：收集项目级 Context

在整理每个项目分组前，**必须询问用户**：

> 「[项目名] 这个项目，本周有没有需要在周报里体现的整体进展、关键指标或风险？（例如：测试覆盖率变化、阻塞点、下周关键节点等）」

这部分内容会放在「重点项目」列的项目名下方，作为项目级总结。如用户说没有，则只填项目名。

### Step 4：整理与扩展

将每个工作事项按 3W2H 展开。参考 `references/template.md` 中的结构和示例。

每个需求/事项的任务描述段落中必须包含 `PRD链接：[可点击链接]`；没有链接时写 `PRD链接：未提供`，不可只在「重点项目」列放链接。

**质量要求：**
- What 必须描述**能力/成果**，不只是任务名称
- Why 要体现业务价值或技术背景
- How 要有具体的技术方案或操作路径，不能泛泛而谈
- 先汇总所有来源中的 URL，去重并归属到事项。PRD/需求链接单独放在 `PRD链接`；任务名称、任务描述、用户笔记中的链接作为任务内交付物/产出/参考链接，放入对应 What/How 或「产出/参考链接」并说明用途
- 任务名称中的 URL 必须保留。无法判断用途时保留并标注「用途待确认」或询问，不得静默删除
- 输出前逐项核对输入 URL；仅在明确判定为无关且写明原因时允许不重复该 URL
- 语言简洁专业，使用中文

### Step 5：生成输出

按项目分组输出，每个项目包含：
1. **【重点项目列】** 项目名 + 项目级 context（Step 3 收集）
2. **【任务描述列】** 每个需求单独一段：`（进度%）` + `PRD链接：[可点击链接]`（无链接时为 `PRD链接：未提供`）+ `产出/参考链接：[链接及用途]`（如有）+ What/Why/When/How；任务内 URL 必须归属到对应事项

参考 `references/template.md` 中的示例格式。

### Step 6：按确认更新本地工作记录

仅当 Step 1 已确认 `workingdir` 是个人工作记录目录且用户明确同意时执行；否则跳过，不写入本地文件。

1. 以当前 `workingdir` 为记录目录，不使用示例路径替换实际路径。读取该目录的 `AGENTS.md` 和目标年份文件（例如 `2026.md`），先遵循 `AGENTS.md`，再参考年份文件现有 Markdown 分类、缩进、链接格式。
2. 用本周周一至周五的日期范围作为二级标题，并按目标年份文件现有日期格式和连接符书写。仅按日期范围识别周标题，不要把项目标题或其他内容用的二级标题当作周标题。检查该日期范围对应的周标题是否已存在：
   - 已有本周标题：在该标题之后、下一个日期范围周标题之前（若无则到文件末尾）定位本周分组末尾，追加本次工作内容；不得覆盖、删除或重写已有内容。
   - 没有本周标题：在年份文件末尾新增本周分组，再追加本次工作内容。
3. 只追加本次生成的工作内容，保持目标文件已有分类、缩进和 Markdown 链接格式；每个需求/事项的任务描述段落保留 PRD 链接，没有链接时写 `PRD链接：未提供`。

**安全约束：**

- 写入前必须已获得本次明确确认；确认范围仅限本次更新。
- 只允许写入当前个人工作记录目录中的目标年份文件，不修改其他本地文件。
- `AGENTS.md` 或目标年份文件无法读取、路径不明确、日期标题格式无法判断时，停止本地写入并询问用户，不自行创建、覆盖或猜测格式。

### Step 7：更新重点事项跟踪表

对于 **重点事项跟踪表**，每周需同步更新「关键进展（截止MMDD）」列。

**先读取跟踪表内容（如设置了 `FEISHU_TRACKER_WIKI_URL` 环境变量）：**

```bash
lark-cli docs +fetch --doc "$FEISHU_TRACKER_WIKI_URL" --format pretty
```

读取后，筛选 **AI 分类**下属于当前用户的行，为每一行生成本周关键进展更新。若用户未提供跟踪表 URL 且环境变量未设置，跳过此步或询问用户。

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

基于 Step 1、Step 2 收集的内容和 Step 3 的项目级 context，为每个有进展的行生成关键进展更新。

## 参考资料

- 报告模板和示例：见 `references/template.md`
- How Much 自动提取脚本：见 `scripts/fetch_feishu_tasks.py`
- Git 工作证据脚本：见 `scripts/fetch_git_work.py`

## 脚本说明

### fetch_git_work.py

从 `$WORK_REPO_PATH`（或 `--repo-root`）按固定顺序扫描 Git 仓库，提取本周周一至周五的本人 author 提交和 tracked/untracked non-ignored 文件 mtime。脚本仅读取仓库信息，不执行 fetch/pull/checkout，不修改仓库或用户工作记录。

**用法：**

```bash
python3 scripts/fetch_git_work.py
python3 scripts/fetch_git_work.py --repo-root <repo_root> [--week-start YYYY-MM-DD] [--max-files N]
```

**输出字段：**

- `week`：扫描周一至周五范围
- `repo_root`：扫描根目录
- `scan_order` / `scanned_repositories`：固定扫描顺序
- `repositories[].identity`：该仓库生效的 `user.name` / `user.email`
- `repositories[].commits[]`：按 author 精确匹配的提交（hash / author / date / subject / files）
- `repositories[].modified_files[]`：本周文件相对路径和修改时间
- `warnings`：身份缺失或单仓库错误；单仓库失败不阻断其他仓库

不按 committer 过滤；无证据的仓库可不出现在 `repositories` 中。

### fetch_feishu_tasks.py

从飞书项目自动发现或手动指定需求，提取后端开发任务数据（标题、描述、子任务、工时）。

**前置条件：** `chromedb` 已在 PATH + Chrome 已登录飞书项目

`chromedb` 是 Go 编译的 CLI 工具，通常已安装在 `~/go/bin/chromedb`，无需额外安装。

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
- `url`：输入的 story URL
- `description`：需求描述（用于理解 What/Why）
- `tasks[]`：后端开发子任务（name / links / status / points / start / end）；`links` 为任务名称中的去重 URL
- `description_links`：需求描述中的去重 URL
- `total_points`：本周子任务人天合计

**已知限制：**
- 仅支持 macOS（依赖 Keychain 解密）
- Chrome 需保持登录状态（cookies 未过期）
