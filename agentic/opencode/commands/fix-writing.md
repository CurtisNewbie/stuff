---
name: fix-writing
description: Apply humanizer skill plus additional style rules to written text
---

Use this command whenever you produce prose for the user (docs, messages, reports) or when the user asks you to fix/improve existing writing.

## Step 1: Load general advice

Load the `humanizer` skill and apply its checks first (AI-sounding vocabulary, filler phrases, promotional tone, em dashes, overused bold, rule-of-three, etc.).

Humanizer's signposting/filler list is English-focused (e.g. "let's dive in"). For Chinese text, also catch the equivalent openers: 核心来说、简单来说、说白了、一句话说 / 一句话总结 / 一句话带过 等. These add no information, drop them and start with the actual content.

## Step 2: Apply these additional hard rules

These are not covered, or not fully covered, by the humanizer skill. Treat them as hard constraints on top of it.

1. **No `--`, `->`, or arrow characters (`→`, `⇒`, etc.).** Do not use double hyphens or arrows, ASCII or Unicode, as connectors or substitutes for words like "to", "leads to", "then". Rewrite with a real word or split into two sentences.
2. **Readability over vocabulary.** Explain concepts in plain words. Don't stack multiple technical terms together to describe one idea, unpack it instead. If a concept matters, give a concrete, simple example rather than a denser explanation.
   - **Avoid unnecessary jargon.** When describing a process or logic, question whether a professional/technical term actually adds precision or just restates something already said in plain words. If it's redundant, cut it instead of translating it.
     > Bad: 按文档原样提取每人的字段，不做归一化，提取后...
     > Good: 按文档原样提取每人的字段，提取后...
   - **Avoid compressed/abbreviated phrasing that forces the reader to guess.** A short noun phrase can save words but leave the action or form unclear. Expand it so the action and the form are both explicit.
     > Bad: 提取表先给用户确认
     > Good: 提取后以表格形式先给用户确认
   - **Keep terminology consistent.** If a concept has both an English term and a Chinese translation (or two Chinese phrasings), pick one and use it throughout. Switching back and forth makes the reader stop and check whether it's the same thing.
     > Bad: ...序列化进一个 hidden JSON 字段...（later）...加一个隐藏的状态字段列
     > Good: 两处都用"隐藏的"，全文统一
3. **Don't overuse `**bold**` or `` `code` `` formatting inside paragraphs.** Even though these render, piling them into running text makes it look cluttered and hard to read. Use them sparingly, only for genuine emphasis or actual code/file/command references, not as a highlighting habit.
4. **Symbol connectors must join symmetrical items.** Don't use `+`, `/`, or similar symbols to glue together two phrases of different grammatical shape (a noun plus a full clause, for example). If both sides are truly parallel nouns, a symbol connector is fine; otherwise spell it out with words or list the items separately.
   > Bad: 判断流程跑到哪了，全靠"状态字段值 + 有没有 Open 待办"这两个值推断。
   > Good: 判断流程跑到哪了，全靠两个信号：状态字段的值，以及有没有 Open 待办。

## Step 3: Self-check before returning

Before delivering the final text, scan it for:
- `--`, `->`, arrow characters (→, ⇒), em dashes, en dashes
- `+`/`/` connecting two grammatically mismatched phrases
- The same concept referred to with different terms (English vs Chinese, or two Chinese phrasings) across the text
- Paragraphs with more than one or two bold/code spans
- Any sentence that could be said in plainer words

Fix any hits, then return the final text.

## Output

- If the user gave you existing text to fix: return only the corrected text (plus a short list of what changed, if useful).
- If you are about to write new text: apply these rules while drafting, don't write first and fix after.

Do not invent facts, change meaning, or restructure content beyond what's needed to satisfy these rules.
</content>
</invoke>
