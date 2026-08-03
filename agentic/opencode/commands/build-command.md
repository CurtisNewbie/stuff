---
name: build-command
description: Guide the creation of a new custom command
---

Help the user create a new custom command file for OpenCode.

## Command File Structure

Commands are markdown files in `commands/` with YAML frontmatter.

**Required format:**

```markdown
---
name: <command-name>
description: <short description shown in command list>
---

<Instructions that guide the agent when this command is invoked.>
```

**Example** — `commands/commit.md`:

```markdown
---
name: commit
description: Generate commit message
---

Generate git commit message for the commited changes in git (including the staging area).

A good commit message may consist of a title and description, most commits should only have a title.
A good commit title should be short and informative, it may start with a verb, describing what was done and changed.
Commit message should start with uppercase.

You shall not create the git commit yourself, just output the commit message, let the user decides.
```

## Creation Process

### Step 1: Clarify Requirements

Before writing anything, gather from the user:

1. **Name** — what to call the command (lowercase, hyphen-separated)
2. **Purpose** — what task does this command automate or guide?
3. **Trigger context** — when should the user invoke it? What state should the workspace be in?
4. **Input** — does it need arguments, or does it read from current context (git state, open files, etc.)?
5. **Output** — what should the agent produce? (text, file, code, action)
6. **Constraints** — what should the agent NOT do?

If the user's request is vague, ask targeted questions. Do not guess at critical details.

### Step 2: Draft the Command

**Load the prompt-engineering-patterns skill first.** Apply its patterns when writing the command prompt:

- Structured outputs (define expected format explicitly)
- Chain-of-thought (break complex tasks into steps)
- Few-shot examples (show concrete input/output when helpful)
- Role-based instructions (define agent expertise if relevant)
- Validation and verification (include self-check steps)

Write the command file following these principles:

- **Be specific**: vague instructions produce inconsistent agent behavior
- **Define boundaries**: state what the agent should and should not do
- **Set output format**: if the output has structure, describe it explicitly
- **Keep it concise**: minimum instructions that fully define the task. No speculative features
- **Use examples**: when output format matters, show a concrete example

### Step 3: Validate

Before presenting to the user, verify:

- [ ] Frontmatter has correct `name` and `description`
- [ ] `name` matches the filename (without `.md`)
- [ ] Instructions are unambiguous — another agent reading this would produce consistent results
- [ ] Constraints are explicit (what NOT to do)
- [ ] No unnecessary verbosity

### Step 4: Present and Confirm

Show the user the complete command file content. Ask if adjustments are needed before writing.

### Step 5: Save to Repository

After the user confirms the command, ask if they want to save it to the shared commands repository at `$STUFF/agentic/opencode/commands/`. If yes, write the file there.