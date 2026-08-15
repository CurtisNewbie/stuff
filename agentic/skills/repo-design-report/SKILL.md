---
name: repo-design-report
description: Produce a design research report of a source code repository (whole repo or a domain subset). The report shows (1) the core entities and their relationships — what they are, what they represent, and the design intent behind them, giving a sense of what the software's authors were thinking; (2) the persistent data structures — tables, fields, and what each field means; (3) the core workflows — how data flows as a workflow progresses, with concrete worked examples, detailed enough that a developer could reimplement the design from the report. Use when the user asks to "analyze this repo's design", "write a source code research report", "research/analyze the design of this project's source code", "how is X designed in this codebase", "understand the design of this system before rebuilding it", or when a developer needs to learn a codebase's design to rebuild, extend, or evaluate it.
---

# repo-design-report

Guide the agent to analyze a source code repo (whole or part) and write a readable design research report. Quality bar: a domain deep-dive report on Frappe/HRMS/ERPNext expense reimbursement — entity map with one-line purposes, ASCII entity-relationship diagram, per-table field breakdowns with plain-language meanings, state machines, a worked numeric workflow example with journal entries, design insights, and stub sections for future deep-dives. If the user provides their own reference report, match or beat that one instead.

## Principles (non-negotiable)

- **Plain language, reader first.** Straight-forward terms; if a concept is hard, give a concrete example. Understanding is the goal, not exhaustive coverage. Do not overcomplicate.
- **No unexplained acronyms.** Every acronym is expanded at first use as "full name (acronym)" — e.g. 物料申请（MR, Material Request）、采购订单（PO, Purchase Order）— before any bare use. Domain jargon the code uses (MR, PO, GL) is the worst offender; never assume the reader knows it. After expansion, reusing the acronym is fine.
- **Cold-reader principle.** The target reader is a developer who has never touched this codebase and may not know the domain — the report must be self-contained and understandable in one cold pass. Test every section against: "can someone who cannot open the code follow this?" If a term, identifier, or mechanic needs code knowledge to follow, gloss it, explain it, or cut it. The ultimate test: a cold reader could reimplement the design from the report alone.
- **No fabrication.** Every entity, field, and workflow claim must be verified against the code. Anything not confirmed from source is marked `⚠️ UNVERIFIED` — never invented.
- **Logic-first narrative; citations are evidence, not content.** Workflow steps are described as design logic — what happens, when, why, in what order, in business terms. Function names are how you verified the logic during research, not what the reader needs: verification is a research-process gate, not report content. Produce an evidence appendix (trigger point → function mapping, labeled "验证依据 / evidence — 不必读") only when the user explicitly asks for auditability; otherwise omit it. Per entity: cite the schema definition file path. No line numbers (they rot). The reading path is not a code walkthrough: no function internals, SQL constructs (subqueries, exists), iteration/dimension mechanics, or file-scoped implementation detail in prose — say what happens and why in business terms; a sentence that needs code knowledge to parse goes to the appendix or gets rewritten.
- **Coverage boundary stated.** The report explicitly says what was and wasn't covered.
- **Language.** Match the language of the user's request (Chinese request → Chinese report, English request → English report). The skill instructions themselves are always English; only the produced report follows the request language.

## Inputs

- **Repo path** — local directory, or a clone URL (clone to a temp dir first).
- **Optional: domain/focus hint** — e.g. "expense reimbursement", "billing", "auth", "the payment flow".
- **Optional: output dir** — default: `<repo>-design-report/` next to the repo (ask only if ambiguous).
- **Optional: reference report** — path or URL to a sample design report the output should match or beat (e.g. the user's own research report on a similar system). If none is given, the quality bar described in the Overview applies.

## Modes

- **Domain deep-dive (default)** — analyze one domain to full depth, like the Frappe expense-claim reference report.
- **Whole-repo survey** — map all major domains first, then deep-dive one domain and summarize the rest, or deep-dive several (ask the user which). Multi-domain assembly: each deep-dived domain gets its own detail + workflow sections under a domain index in §2; non-deep-dived domains get one-liners in §2 and stub entries in §9.

If the user's intent is not obvious, ask which mode.

## Workflow

### 1. Scope

1. Determine mode (ask if unclear; whole-repo is only worth it for small/medium repos).
2. **Domain mode, no focus given:** discover candidate domains from code entry points (routes/controllers/service modules/README/module dirs — see analysis-playbook.md §3), present a shortlist with a recommendation, and ask the user to pick (or approve the recommendation). Do not start a deep-dive before the domain is chosen.
3. **Whole-repo mode:** same discovery, show the domain map, ask which domains to deep-dive.

### 2. Setup

Create the output dir `<out>/` for the final report. Optional `<out>/work/` for draft artifacts — use it only when a long session risks context loss or the user asks for intermediate records; do not persist drafts for their own sake.

### 3. Discovery (optional drafts → `work/`)

1. **Framework orientation** — tech stack, and where schema definitions live (analysis-playbook.md §1).
2. **Domain map** — candidate domains with entry points (optionally save to work/domain-map.md).
3. **Entity inventory** — every entity/table in scope, one-line purpose each (optionally save to work/entities.md). This becomes the purpose overview table in the report.
4. **Spine workflow** — the domain's main business flow traced end-to-end (e.g. expense: request → approval (approver may cut amounts) → advance offset → payment → posting). Entities the spine touches = core entities. Everything else is peripheral.

### 4. Deep-dive per core entity

1. Pull the **full schema definition from source** (never from usage alone).
2. Extract fields + meanings: name, type, required/read-only, what it means, **who writes it** (human / system write-back), formula if any.
3. Note relationships: reference fields, parent-child subtables, mapping tables.
4. Note **design intent**: why this entity exists, what it represents, what it implies about the system's design (e.g. "the advance request has no exchange-rate field — the rate exists only on the payment entry, because the rate becomes a fact at the moment of payment").
5. Optionally save as a field-table draft (work/entity-<name>.md) when persistence helps.

Peripheral entities: one-line purpose only — no field tables (core-path rule). Deprecated/dead entities (only migration/back-compat references, no live path): omit entirely — never mention them anywhere, not even in the coverage boundary (only exception: one sentence of old-vs-new contrast in a design insight that explains the current structure's shape). Legacy-but-live code paths: one paragraph max, only when they change what the reader would reimplement (see analysis-playbook.md §2).

### 5. Workflow tracing

For the spine workflow, trace step by step: trigger → function(s) → validations → data writes (which table, which fields) → state transitions → side effects (optionally save to work/workflow-<domain>.md). Extract:

- **State machines** — submit states, approval states, derived display states, with transition rules (e.g. `docstatus: Draft(0) → Submitted(1) → Cancelled(2)`).
- **Formulas** — exact computations from code (totals, tax, exchange gain/loss), with the function that computes them.
- **Write-back flows** — which entity writes which fields on other entities when (e.g. expense claim submit → employee_advance.claimed_amount += allocated).
- **Worked example (mandatory)** — a realistic scenario run through the whole workflow with concrete numbers at every step: inputs → computed values → resulting row writes → journal entries if the domain is accounting. Verify the arithmetic with a script (e.g. python) — never hand-calculate. Presentation: the header says at most "数字已用脚本验证" — never cite the script's path or run command, never reference work/ files; formulas in the example are plain math (120,000 ÷ 12 = 10,000), not code syntax (flt(...)).

### 6. Assemble the final report

Follow `references/report-template.md` (canonical skeleton). Deviate from the template only with explicit justification. The three mandatory sections from the principles are: entities + relationships + design intent, persistent data structures, and core workflows with examples.

If a reference report was provided (user-supplied or the built-in example): before assembling, diff the planned outline against the reference section-by-section — anything the reference covers that the report doesn't must either be covered or explicitly justified as dropped.

### 7. Verify (gate — do not output before passing)

- Every field in the report exists in the cited schema file (re-read and spot-check).
- Every workflow step was verified against a real function during research (spot-check existence in source).
- Formulas re-derived from code, arithmetic script-checked.
- Unverified items carry `⚠️ UNVERIFIED`.
- Coverage boundary present.
- The worked example is present, and its arithmetic was verified by running a script (python or equivalent) — no script run, no example, not done.
- Every entity in scope has either a field table or an explicit peripheral one-liner — no orphans.
- Mandatory sections (entity map, entity detail, workflows, coverage boundary) all present — no silent deviations.
- Every design-insight paragraph cites its supporting evidence (≥2 code-grounded points).
- Prose is plain language: short sentences, no buzzwords or filler, every domain term explained once at first use; every acronym expanded as "full name (acronym)" at first use — no bare acronym in the reading path before its expansion.
- Every summary/quote-box claim is consistent with the detail sections — exceptions stated, no overgeneralization.
- No code walkthrough in the reading path: unglossed identifiers, function names with file references, SQL constructs, and iteration/mechanics detail appear only in the evidence appendix — prose that needs code knowledge to parse is a rewrite.
- Cold-reader pass done: the final draft was read top-to-bottom as a reader who cannot open the code; anything requiring code knowledge to follow was glossed, explained, or removed.

### 8. Output

- Final report: `<out>/<domain>-design-report.md` (or `<repo>-design-report.md` for whole-repo). The final report is the single consolidated, self-contained deliverable.
- If created, drafts stay in `<out>/work/` — work products, not deliverables; don't polish them.
- Publish to Feishu only if the user explicitly asks (e.g. via lark-cli).

## References

- `references/report-template.md` — canonical report skeleton, section guidance, and style rules with mini examples. **Read before assembling the final report.**
- `references/analysis-playbook.md` — framework-agnostic discovery: finding schema definitions, entities, entry points, and tracing workflows; worked-example construction; anti-patterns. **Read during discovery and deep-dive.**
