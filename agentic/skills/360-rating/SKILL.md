---
name: 360-rating
description: Assist with Feishu/Lark 360 performance reviews for a candidate. Uses agent-browser to navigate the perf review page, read the candidate's half-year report, extract all rating metrics and scoring standards (0–5 scale), then propose scores and justifications for each rating section. Confirms full comprehension before rating by summarizing candidate outcomes, metrics, and sections. Use when asked to "do a 360 review", "help rate a candidate", "fill in perf review", "360评分", or when given a Feishu perf review URL (*.feishu.cn/perf/review/...).
---

Use agent-browser (Default profile, headed mode) to complete a Feishu/Lark 360 performance review for a candidate. Respond and write all justifications in 中文. Pass all written justifications through the humanizer skill before presenting to the user.

## Prerequisites

Before starting, verify both required skills/tools are available:

- **agent-browser** — check with `agent-browser --version`. If missing: `npx skills add https://github.com/vercel-labs/agent-browser --skill agent-browser`
- **humanizer** — check if the skill is listed in available skills. If missing: `npx skills add https://github.com/blader/humanizer --skill humanizer`

If either is unavailable, stop and prompt the user to install before proceeding.

## Workflow

### Step 1: Get the review page URL
Ask the user for the 360 rating page URL. This page shows the candidate's report — the content the rater will evaluate.
Format: `https://{company}.feishu.cn/perf/review/{id}/.../members`
If they don't know where to find it, guide them to navigate there in Feishu.

### Step 2: Read the full page
Navigate to the URL. Scroll down completely to read all content. Use `read` to extract text — do not take screenshots.
- Candidate's half-year self-report
- All rating sections and their descriptions
- Scoring standards and metrics (0–5 scale)

### Step 3: Confirm comprehension
Before rating, show the user a summary to confirm full understanding:
1. **Candidate outcomes** — major results/achievements from the report
2. **Rating metrics** — all scoring standards and what each level means
3. **Rating sections** — all sections that need to be scored

Wait for user confirmation before proceeding.

### Step 4: Gather rater's perspective
Read [`references/rating-distribution.md`](references/rating-distribution.md) for the company's forced distribution rules before asking.

Ask the user for their input as the rater:
- **Target grade** — which grade are they aiming for this candidate? (S / A+ / A / B+ / B / B-/ C). Show the distribution table so they can make an informed choice.
- **Overall impression** — how do they feel about this person across the rating sections?
- **Highlights** — what standout strengths or achievements should be reflected in the ratings?
- **Leader's sentiment** — what does the candidate's direct leader think of them? (positive, neutral, critical, or specific concerns)

Use these inputs to calibrate ratings:
- Use the target grade's score range as the anchor — the weighted average of all section scores must land within that range.
- Surface the highlights in justifications.
- Ensure the overall tone reflects the rater's impression.
- If the leader holds a negative or critical view, avoid scores that would clearly contradict that — a significantly higher rating than the leader's sentiment would create inconsistency in the review system.
- Remind the rater if their target grade is in a scarce quota (S, A+, A) so they go in with realistic expectations.

### Step 5: Rate each section
For each section, propose:
- A score (0–5)
- A written justification grounded in both the candidate's report and the rater's perspective

### Step 6: Iterate
After presenting all scores, ask the user if they want to adjust any score or reasoning. Revise and re-present until the user is satisfied.

