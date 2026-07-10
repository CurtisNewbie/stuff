---
name: 360-rating
description: Assist with Feishu/Lark 360 performance reviews for a candidate. Uses agent-browser to navigate the perf review page, read the candidate's half-year report, extract all rating metrics and scoring standards (0–5 scale), then propose scores and justifications for each rating section. Confirms full comprehension before rating by summarizing candidate outcomes, metrics, and sections. Use when asked to "do a 360 review", "help rate a candidate", "fill in perf review", "360评分", or when given a Feishu perf review URL (*.feishu.cn/perf/review/...).
---

Use agent-browser (Default profile) to complete a Feishu/Lark 360 performance review for a candidate.

## Workflow

### Step 1: Get the review page URL
Ask the user for the 360 rating page URL. Format: `https://{company}.feishu.cn/perf/review/{id}/.../members`
If they don't know where to find it, guide them to navigate there in Feishu.

### Step 2: Read the full page
Navigate to the URL. Scroll down completely to read all content:
- Candidate's half-year self-report
- All rating sections and their descriptions
- Scoring standards and metrics (0–5 scale)

### Step 3: Confirm comprehension
Before rating, show the user a summary to confirm full understanding:
1. **Candidate outcomes** — major results/achievements from the report
2. **Rating metrics** — all scoring standards and what each level means
3. **Rating sections** — all sections that need to be scored

Wait for user confirmation before proceeding.

### Step 4: Rate each section
For each section, propose:
- A score (0–5)
- A written justification grounded in the candidate's report

### Step 5: Iterate
After presenting all scores, ask the user if they want to adjust any score or reasoning. Revise and re-present until the user is satisfied.

