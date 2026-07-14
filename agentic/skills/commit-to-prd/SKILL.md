---
name: commit-to-prd
description: Generate a PRD-style title and description (in Chinese) from git commits or code changes. Use when the user asks to "write a PRD", "generate a feature description", "write a requirement doc", "帮我写需求描述", "生成需求标题和描述", or "帮我写这个 commit 的需求" — or after completing a feature and wanting to document it formally.
---

# commit-to-prd

Generate a structured PRD title and description from git commits or code changes.

## Input

Accept any of:
- A commit hash or range (`git log`, `git show`)
- A branch diff
- A paste of changes or feature summary already in context

If no input is given, run `git log --oneline -10` to show recent commits and ask the user which to document.

## Workflow

1. **Gather changes** — read commits via `git log -p`, `git show <hash>`, or `git diff <base>..<head>`. Read enough to understand what changed and why.
2. **Analyze** — identify: what the feature does, what problem it solves, how it solves it, and the value it delivers. Focus on **functional behavior and user-facing impact**, not code mechanics.
3. **Generate** — produce a title, a 需求目标（量化指标）(one sentence, ≤50 字), and a description following the format in `references/format.md`.
4. **Humanize** — load and apply the `humanizer` skill to the generated title, 需求目标, and description. Remove AI writing patterns (inflated language, rule of three, em dash overuse, vague attributions, promotional tone, etc.) and make the text sound natural.
5. **Output** — print the result directly in the chat (no file unless asked).

## Language

Default to **Chinese**. Switch to English only if the user explicitly asks.

## Format

See `references/format.md` for the exact structure, field guidance, and a complete example.
