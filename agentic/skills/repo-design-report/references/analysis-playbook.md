# Analysis Playbook — repo-design-report

Framework-agnostic heuristics for digging through an unfamiliar codebase: finding schema definitions, mapping domains, tracing workflows, and building verified worked examples. Read this during discovery and deep-dive; do not attempt to enumerate every file — target the spine.

## Table of Contents

1. [Framework orientation: where schemas live](#1-framework-orientation-where-schemas-live)
2. [Entity discovery](#2-entity-discovery)
3. [Entry points and domain map](#3-entry-points-and-domain-map)
4. [Spine workflow identification](#4-spine-workflow-identification)
5. [Tracing techniques](#5-tracing-techniques)
6. [Worked example construction](#6-worked-example-construction)
7. [Anti-patterns](#7-anti-patterns)

## 1. Framework orientation: where schemas live

First 15 minutes of any repo: identify the stack and where table definitions live. Schema sources are the **authoritative** place for fields — always prefer them over usage sites.

| Stack | Where table/schema definitions live |
|---|---|
| Django | `*/models.py`, migrations `*/migrations/*.py` |
| Rails | `db/schema.rb`, `db/migrate/*.rb` |
| Java Spring | `@Entity` classes, `resources/db/migration/*` (Flyway/Liquibase) |
| Go | `*_model.go` / GORM structs with `gorm:"column:..."` tags, migration files |
| TypeScript | `prisma/schema.prisma`, TypeORM `@Entity()` decorators, Drizzle schema files |
| Python (SQLAlchemy) | `models/*.py`, `__tablename__` |
| Frappe (Python) | `*/doctype/<name>/<name>.json` (fields), `<name>.py` (business logic) |
| Unknown | grep for `CREATE TABLE`, `@Entity`, `__tablename__`, `schema.rb`, `migrations/` dirs |

Detection shortcuts: read README + `package.json`/`pyproject.toml`/`go.mod`/`pom.xml`, then confirm with one grep for table-definition patterns.

## 2. Entity discovery

- Find the schema source (per framework table above) and enumerate entities.
- Name-based inventory: group files by domain prefix (e.g. `expense_claim`, `expense_claim_type`, `expense_claim_advance`, `employee_advance` are clearly one family).
- One-line purpose per entity: derive from (a) the schema file's own description field if present, (b) the file name, (c) one glance at its key fields, (d) its usage in the workflow. Do not read every entity fully at this stage.
- **Flag deprecated/dead structures during inventory.** Names hint at it (`legacy_`, `deprecated`, old-version prefixes), migration/upgrade patches confirm it. Verify by grepping who references the entity or code path:
  - Only migration patches / upgrade scripts / back-compat shims reference it, no live runtime path → **dead**. Omit from the report **entirely**: no purpose-table row, no field-table row, no coverage-boundary mention. Only exception: one sentence of old-vs-new contrast inside a design insight when it explains why the *current* structure is shaped this way — never a description of the old structure itself.
  - Still on a live runtime path (old controller executed unconditionally, back-compat branch that actually runs, dual-controller transitions) → **legacy but live**, not deprecated. Keep it only when it changes what the reader would reimplement (e.g. the double-validation side effect); one paragraph max, no field tables.
- Note **framework-injected system columns** once (e.g. Frappe's `parent/parenttype/parentfield/idx`; Rails timestamps) and then ignore them in field tables.
- Note **dynamic fields** (e.g. ERPNext Accounting Dimension injects fields at runtime). Document the mechanism, don't enumerate the injected fields.

## 3. Entry points and domain map

- Entry points: web routes/controllers, API endpoints, CLI commands, scheduled jobs, message consumers, README feature lists, `docs/`.
- Group entry points into candidate domains by path prefix / module / naming (e.g. `/api/expense/*`, `payroll/`, `hr/`).
- The domain map = list of candidate domains with their entry points and rough size (file counts). This is the shortlist shown to the user in domain mode.
- Recommendation heuristic for "most central domain" when unsure: the domain whose entities are referenced by the most other domains (follow reference fields), or the one with the richest lifecycle.

## 4. Spine workflow identification

For the chosen domain, find its main document/entity's lifecycle:

1. Find the status/state field(s) on the main entity (e.g. `docstatus`, `status`, `approval_status`). Grep its assignments.
2. Follow each state transition to its handler (submit/approve/pay/cancel functions).
3. Trace what each handler writes: validations, field updates, subtable changes, other entities (write-backs), side-effect records.
4. The spine = the end-to-end lifecycle chain (e.g. expense: Draft → submit → approval → advance offset → payment → posting). Entities touched = core set.

## 5. Tracing techniques

- **Who writes a field**: grep the field name across the codebase; separate human input (schema `read_only: false`, form scripts, `set_value` from UI) from system write-back (computed in validation/submit hooks, ledger summaries).
- **Formulas**: for aggregate fields (`total_*`, `grand_total`, `tax_amount`...), find the compute function (often named `set_*_amounts`, `calculate_*`) and copy the exact formula from code, then express it in plain terms.
- **State machines**: grep for the status field's possible values and where each is assigned; look for derivation functions (a `get_status()` that combines `docstatus` + payment history is a derived state — describe it as such).
- **Functions are breadcrumbs, not content.** Use function names to trace and verify logic, but the report narrates design logic in business terms. Collect the trigger-point → function mapping during research to verify claims; keep names out of the narrative. An evidence appendix appears only when the user asks for auditability. Same for mechanics: SQL constructs, iteration structure, dimension handling, function internals — trace with them, narrate in business terms, park the detail in the appendix only if one is being produced.
- **Write-back flows**: when entity A's submit handler updates entity B, that's a write-back (e.g. expense claim submit → `employee_advance.claimed_amount += allocated`). These are the report's data-flow facts — collect them explicitly.
- **Ledger/advisory tables**: some tables are event ledgers, not accounting (e.g. the advance-payment ledger records Submit/Adjustment events and is the source for all write-back amounts). Identify which tables are read-only sources of truth for others.
- **Tests as ground truth**: the repo's tests encode expected behavior (amounts, state transitions, error cases). Read the domain's test files for confirmation — they are faster and more reliable than tracing UI.
- **Don't over-verify**: once a formula/flow is confirmed from code + tests, move on. Only genuinely unverifiable items get `⚠️ UNVERIFIED`.

## 6. Worked example construction

Purpose: show the reader exactly how the system behaves on a realistic case, so they could reimplement the design.

1. Pick a scenario covering the normal path **plus one interesting branch** (a cut-down approval, multi-currency, partial allocation, cancellation).
2. Walk the scenario step-by-step through the spine workflow. At each step: inputs → computed values → row writes (which table/fields) → state change.
3. If the domain involves double-entry (accounting), show the journal entries: debit/credit lines with accounts and amounts, and the invariant check (sum of debits = sum of credits).
4. **Verify every number with a script** (python one-liner is fine). Never hand-calculate — arithmetic errors destroy report credibility.
5. Keep the example short enough to read in one minute; put detail in tables/code blocks, not prose.

## 7. Anti-patterns

- **Don't trust comments/README over code.** Docs lie; the schema and handlers don't.
- **Don't infer a field's meaning from one usage.** Check the schema definition + at least two usages.
- **Don't document framework machinery as domain design.** System columns and framework plumbing get one sentence each, then disappear.
- **Don't enumerate.** If there are 30 similar entities, document the pattern once and list the rest in a table row.
- **Don't read linearly.** Grep, jump, follow references. Reading files in order wastes context on noise.
- **Don't dump identifiers.** The report is design, not a code map. Function names stay out of the narrative (an evidence appendix exists only when the user asks for it); the narrative stays logic-first.
- **Don't guess at design intent.** Insights must be grounded in what the code does; a claim like "X is essentially Y" needs at least two pieces of supporting evidence.
