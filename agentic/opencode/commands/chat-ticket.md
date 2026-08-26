---
name: chat-ticket
description: Log a task ticket from a conversation into progress_lark notes, optionally upload to Lark
---

Someone just gave the user a task verbally/in chat. Create a ticket entry so the user doesn't forget it and the task is trackable.

## Steps

1. **Read conventions first.** `cd ~/dev/notes/dev_design/progress_lark/` and read `AGENTS.md` there. Follow its conventions exactly (target file, entry format, date prefix style, upload process). Do not guess structure — AGENTS.md is authoritative.

2. **Parse the input.** User may give a raw paragraph, or structured fields (task name / description / Lark doc link). Extract:
   - Task name (short)
   - Task description (what needs doing, context from who/why if mentioned)
   - Any reference link (e.g. a Lark doc)

3. **Confirm the date prefix.** Default to today's date in the format AGENTS.md/existing entries use (e.g. `08/26`). Ask the user only if it's ambiguous whether this entry belongs to today or another date.

4. **Update the file.** Add the new entry to the correct HTML file per AGENTS.md's instructions, matching existing entry format/style exactly. Show the user the diff before finalizing.

5. **Ask before uploading.** After the local file is updated, ask the user: "Upload to Lark now?" Only run the upload step (per AGENTS.md, e.g. `upload_to_feishu.py`) if the user confirms. Never upload automatically.

## Constraints

- Do not invent a file format or entry structure not already established in AGENTS.md or existing entries — mirror what's there.
- Do not upload to Lark without explicit user confirmation.
- Do not over-explore the directory beyond AGENTS.md and the target file — this is the user's personal note system, keep it lightweight.
