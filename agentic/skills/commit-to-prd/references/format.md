# PRD Title & Description Format

## Title

One line. Pattern: `{系统/模块}，{动作} {功能名称}`

- 简洁，15字以内
- 动词优先：增加、支持、优化、重构、修复
- 带上所属系统或模块让读者快速定位

Examples:
- `AgentLoop 框架，增加 OutputCheck 输出校验回调功能`
- `AgentLoop 框架，增加 ToolCall Offloading 功能`
- `用户服务，优化 Token 刷新机制`

---

## Description

Four paragraphs in order. Each paragraph is 2–4 sentences.

### 1. 背景与目标
What is this system/module, and what is the goal of this change? Give enough context for a non-technical reader to understand the setting.

### 2. 问题
What specific pain point or gap does this address? Be concrete — describe what breaks, fails, or is missing without this feature.

### 3. 解决方案
How does the change solve the problem? Describe the mechanism, key design decisions, and notable behaviors. Technical detail is welcome here.

### 4. 价值
What is the outcome for users, developers, or the system? Frame in terms of reliability, efficiency, flexibility, or quality improvements.

---

## Example (complete)

**Title**
```
AgentLoop 框架，增加 OutputCheck 输出校验回调功能
```

**Description**
```
此需求为 Agent 输出质量控制功能。Agent 在完成任务后，其最终输出（纯文本回复，非工具调用）有时不符合调用方预期的格式、质量或安全要求，例如输出结构不满足 JSON 规范、缺少必要的 XML 标签包裹、包含敏感内容等，此前只能在结果返回后由业务层被动处理，无法让 Agent 自我修正。

此功能在 AgentConfig 中新增 OutputCheck OutputCheckFunc 回调字段，在 Agent 每次产生纯文本最终回复后、进入 final_output 节点前触发校验。OutputCheckFunc 签名为 func(ctx, agentCtx, attempt, output) (hint string, ok bool, err error)，三种返回语义清晰分离：ok=true 输出通过，ok=false 将 hint 插回对话让 Agent 重新生成，err!=nil 立即中止并上抛错误。框架同时追踪当前执行内校验的调用次数（attempt，从 1 开始），支持调用方针对不同轮次实现差异化策略。

内置实现 FinalResponseTagOutputCheck(maxAttempts int) 解决 Agent 有时使用错误标签（如 <final_answer>、<answer>）包裹输出的问题，检测 <final_response> 标签是否存在，缺失时生成结构化纠错提示引导 Agent 使用正确格式重写。

此功能将输出格式保障内嵌于 Agent 执行循环，支持格式校验、质量审核、安全检测等多种场景，减少业务层对 Agent 输出的后处理逻辑，提升 Agent 输出的可靠性与一致性。
```

---

## Tips

- **Avoid implementation jargon in 背景/价值** — keep those paragraphs readable by a PM or tech lead unfamiliar with the codebase.
- **解决方案：公开接口可以提及，内部实现不要出现** — 可以出现的：配置字段名、公开 API 名称、用户可感知的行为和开关。不应出现的：内部变量名、内部函数名、数据结构类型名、框架内部调用链。

  ❌ 过于代码化：`traceAcc 的 snapshot() 在错误检查之前调用，确保即使图执行中止也能返回已收集的追踪记录，错误路径同时由返回零值 TaskOutput{} 改为返回携带部分数据的 result。`

  ✅ 描述功能行为：`框架在任务执行中途出错时仍会保留已采集的追踪记录，随错误结果一并返回，确保调用方不丢失部分执行数据。`

- **One feature per PRD** — if commits span multiple unrelated changes, split into separate PRDs or ask the user which to focus on.
- **Don't pad** — if a paragraph has nothing meaningful to say, merge it with an adjacent one rather than writing filler.
