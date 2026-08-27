---
name: chat-ticket
description: Log a task ticket from a conversation into progress_lark notes, optionally upload to Lark
---

This command tracks tasks in progress_lark notes. The user's input may ask to log a new task, or to update/close/change an existing one. Recognize which before acting.

## Step 0: Recognize intent

Classify the input into one of:

- **`new_ticket`** — describes a new task to log. Signals: "someone asked me to...", "need to do X", "add a ticket for...", no reference to an existing entry.
  e.g. "PM just asked me to fix the login redirect bug" → `new_ticket`
- **`update_status`** — marks an existing ticket done/in-progress/blocked. Signals: "mark X as done", "finished the Y ticket", "X is blocked on...".
  e.g. "the redirect bug fix is done" → `update_status`
- **`update_content`** — edits an existing entry's description/link/date without a full new task. Signals: "update the Y ticket with...", "add this link to the X entry", "correct the date on...".
  e.g. "add the design doc link to the redirect bug ticket" → `update_content`
- **`unclear`** — doesn't fit cleanly, or could match an existing entry ambiguously (e.g. multiple similar entries, or no entry text to match against).

If `unclear`, ask the user to clarify (which entry, and what change) before doing anything else. Do not guess and silently pick an intent.

State the recognized intent briefly before proceeding (e.g. "Recognized as: update_status").

## Steps

1. **Read conventions first.** `cd ~/dev/notes/dev_design/progress_lark/` and read `AGENTS.md` there. Follow its conventions exactly (target file, entry format, date prefix style, upload process). Do not guess structure — AGENTS.md is authoritative.

2. **Branch on intent:**

   **If `new_ticket`:**
   - Parse the input. User may give a raw paragraph, or structured fields (task name / description / Lark doc link). Extract: task name (short), task description (what needs doing, context from who/why if mentioned), any reference link.
   - Confirm the date prefix. Default to today's date in the format AGENTS.md/existing entries use (e.g. `08/26`). Ask the user only if it's ambiguous whether this entry belongs to today or another date.
   - Add the new entry to the correct HTML file per AGENTS.md's instructions, matching existing entry format/style exactly.

   **If `update_status` or `update_content`:**
   - Locate the existing entry by searching the target file for matching task name/keywords. If multiple entries plausibly match, list them and ask the user which one.
   - If no match found, tell the user and ask whether to create a new entry instead — don't invent a match.
   - Apply the change in place (status marker, description, link, etc.) matching the existing entry's format/style exactly.

3. **Show the diff.** Before finalizing, show the user the exact before/after diff of the file change, regardless of intent.

4. **Ask before uploading.** After the local file is updated, ask the user: "Upload to Lark now?" Only run the upload step (per AGENTS.md, e.g. `upload_to_feishu.py`) if the user confirms. Never upload automatically.

## Constraints

- Do not invent a file format or entry structure not already established in AGENTS.md or existing entries — mirror what's there.
- Do not upload to Lark without explicit user confirmation.
- Do not over-explore the directory beyond AGENTS.md and the target file — this is the user's personal note system, keep it lightweight.
- Do not silently guess intent or target entry when ambiguous — ask.
