# Report Template — repo-design-report

Canonical skeleton for the final report. Default structure; deviate only with explicit justification. **Write the report in the language of the user's request** — the skeleton below is shown in English; when the report language is Chinese, translate headings and content accordingly (see the heading translation table in §2).

## Table of Contents

1. [Skeleton](#skeleton)
2. [Section-by-section guidance](#section-by-section-guidance)
3. [Style rules](#style-rules)
4. [Mini examples](#mini-examples)

## Skeleton

```
# <Domain/Repo> Design Research Report    (title in report language)

## 1. Intro                                  scope statement
## 2. Core Entities & Purposes               entity map
## 3. Entity Relationships                   relationships + design intent
## 4. Core Design Ideas                      what the authors were thinking
## 5. Core Entities in Detail                persistent data structures (one section per entity)
## 6. Core Workflows                         workflows + data flow + worked example
## 7. State Machine Summary                  (only when several exist)
```

**Heading translation for Chinese reports** (when the user requests Chinese):

| English | 中文 |
|---|---|
| 1. Intro | 1. 范围说明 |
| 2. Core Entities & Purposes | 2. 核心实体与用途总表 |
| 3. Entity Relationships | 3. 实体关系 |
| 4. Core Design Ideas | 4. 核心设计思想 |
| 5. Core Entities in Detail | 5. 核心实体详解 |
| 6. Core Workflows | 6. 核心工作流 |
| 7. State Machine Summary | 7. 状态机汇总 |

**Whole-repo mode**: repeat §5 and §6 once per deep-dived domain (each under a domain index in §2); non-deep-dived domains get one-liners in §2.

## Section-by-section guidance

### 1. Intro — scope statement

- Repos analyzed (name + link), tech stack (one line, e.g. "Python Flask + Vue/Vite, built on the Frappe framework").
- **Coverage boundary**: what this report covers, what it does not (e.g. "Covers: expense claims, employee advances, advance offsetting, posting. Not covered: budget allocation, approval-flow configuration, AI receipt recognition"). Mandatory.
- **Schema primer (one short paragraph)**: where table definitions live in this stack and how to read them, so the reader can navigate the cited files themselves (e.g. "表结构在 `../doctype/` 里, 字段定义在 `expense_claim_type.json`"). One paragraph, no more.

### 2. Core Entities & Purposes

Table of all entities in scope: `Entity | Purpose`, one plain-language line each (from entity inventory). Example:

| Entity | Purpose |
|---|---|
| expense_claim + expense_claim_detail | Expense claim header / line items |
| employee_advance | Employee loan/advance, incl. sanctioned amount |
| expense_claim_advance | Expense-to-advance offsetting (writing off loans against claims) |

Optionally add a "design takeaways" quote-box, 1-3 lines, when it genuinely helps the reader (e.g. "借鉴方向: 报销字段建模、借款→冲销生命周期、费用类型体系"). Never author-facing advice ("worth copying") — the report explains the system, it doesn't coach the author. **Consistency rule** (if the quote-box is present): every claim in it must hold against the detail sections — if one entity is an exception (e.g. one of four gates is a real approval flow while the others are submit-time checks), state the exception; no overgeneralization.

### 3. Entity Relationships

Real relationship semantics, grouped by type — not a code/trigger map:

1. **Structure (composition)** — parent-child links with cardinality and what the child represents (e.g. Budget 1:N Budget Distribution: each row is one time-slice, rows sum to the yearly total, child dies with parent).
2. **References** — every reference link annotated with what it means (e.g. Budget.account → Account: which expense category this budget constrains; a budget on a tree-group expands to all descendants = shared quota). A bare `A.b → C` mapping with no meaning annotation is not done. Include dynamically injected references.
3. **Matching relationships (read-only)** — the links that matter at validation/report time: which entities are compared on what key, all read-only (e.g. GL Entry matched to Budget on the (dimension, account) key = "already spent"; prefix-sum of distribution rows = "how much should be spent by now").

Keep trigger points and query flows OUT of this section — they belong to §6 workflows. Then 1-3 plain paragraphs on what the relationships imply (e.g. "budget and consumption have no balance table — spending is never written back to the budget").

### 4. Core Design Ideas (the "what were they thinking" section)

2-5 short paragraphs capturing the system's core ideas. Derive from what is surprising, repeated, or carefully designed. If the code contradicts a naive expectation, that contrast is usually the insight.

Good examples (from the Frappe expense report):
- "An expense claim is essentially a business document plus an accounting voucher; submitting the claim is the posting act itself" (voucher layer vs ledger layer: every document eventually writes into the one general-ledger table).
- "The advance request has no exchange-rate field. The rate exists only on the payment entry: the rate becomes a fact at the moment of payment" (information flow: advance request → payment entry (rate born here) → claim offset rows → submit writes back).
- "Accounts are not hand-entered; the system derives them from a (expense type, company) mapping table, to prevent misclassified postings".

If you can't find deep insights, state the design's basic structure plainly — do not inflate.

If the domain has a clear conceptual layering, show it as a small diagram — it is often the single most clarifying picture (e.g. voucher layer vs one general-ledger table: "报销单 / 付款单 / JE 全部写进唯一一张 GL Entry 表"; or an event ledger that is the source of truth for write-backs). Each insight paragraph must carry ≥2 code-grounded evidence points.

### 5. Core Entities in Detail (persistent data structures)

One subsection per core entity (spine-path entities only; peripheral entities get one-liners in section 2). Each subsection:

- **Domain model in one line** at the top of the section, before the per-entity subsections: the whole thing in one plain sentence, e.g. "Budget = company × cost object × account × time window → one total; Budget Distribution = time slices of that total, summing to it". Reader gets the mental model first, detail after. If this one-liner is hard to write, the report isn't ready yet.
- **One sentence**: what it is, what it represents, and **why it exists** (what problem it solves). Must be understandable to a reader who has never seen this domain — if an everyday analogy helps, use it (e.g. "an annual salary budget is 12 monthly slices — you manage month by month, not by year-to-date"). If "why it exists" needs more than one sentence, expand it — this is where the report earns its keep.
- **Field table**: `Field | Meaning`, grouped by logic when many fields (basics / approval / currency / amounts / payment / attribution / FX / other...). Every field has a plain-language meaning. Mark read-only/system-written fields (read-only, system write-back). Include formulas in the meaning (e.g. `grand_total = sanctioned total + tax − advance offset`).
- **Child tables** documented under their parent (e.g. the Expense Claim's three child tables: expenses/taxes/advances, each with its own field table).
- **Who writes it**: note which fields humans fill vs which the system writes back (e.g. "only the request fields are human-filled; after payment all amounts are system write-backs").
- **Schema path citation** at the end of each entity section: `Schema: frappe__hrms/hrms/hr/doctype/expense_claim/expense_claim.json`.

Skip framework boilerplate columns once they're explained (e.g. Frappe's `parent/parenttype/parentfield/idx` — mention in one sentence, then never repeat). Deprecated/dead entities (migration-only references) never appear anywhere in the report — not here, not in the coverage boundary. Legacy-but-live structures get one short paragraph only if they affect behavior the reader must know (e.g. an old validator that still runs); no field tables for them.

### 6. Core Workflows (workflows + data flow + worked example)

The spine workflow, as a step-by-step walkthrough with:

- **One-line closed-loop summary at the top** — the reader gets the whole flow before the detail (e.g. "标准的「申请 → 审批(可砍价) → 核销借款 → 支付 → 入账」闭环").
- Each step described in **business terms**: what happens, when, why, in what order, what it reads/writes — no function names in the narrative. Trigger points are stated in plain language (e.g. "the check runs when a purchase request is submitted, when a submitted PO's lines change, and as a backstop when GL entries are posted — all read-only, never writing the budget").
- **Evidence appendix (optional)**: only when the user asks for auditability — at the end of the workflow section, one compact table mapping each trigger point to its function(s) (file + name), labeled "验证依据 / evidence — 不必读". Default: omit; verification happens during research, not in the report. Function names stay out of the narrative — except when the name itself is the fact (e.g. "the legacy validator runs unconditionally" — keep the fact, name optional).
- **State machines**: submit states, approval states, derived states with their derivation rules. A compact diagram works:
  ```
  docstatus:  Draft(0) --submit--> Submitted(1) --cancel--> Cancelled(2)
  approval_status:  Draft --> Approved / Rejected
  status (read-only derived):  Submitted+Approved+fully paid --> Paid ...
  ```
- **Key formulas** with exact computations and the computing function.
- **One-line intuition after hard rules**: after each key formula or subtle rule, add a plain-language 直观理解 line (e.g. "you either hold the qualification of the highest hit threshold, or any higher-threshold rule's qualification — higher-threshold rules apply to you too, so senior approvers can submit any amount"). If the rule needs the intuition to be understood, the intuition is not optional.
- **Data flow**: which entity writes back to which (e.g. submitting a claim writes GL entries, updates the advance's claimed_amount, records offsets in the advance-payment ledger; cashier payment sets is_paid → status Paid).
- **Worked example (mandatory)**: one realistic scenario with concrete numbers through every step. Structure:

  ```
  Employee A, Singapore company, claims travel expenses:
    Line items: flight 1000 SGD (claimed), hotel 500 SGD (claimed)
    Approver sanctions: flight 1000, hotel 400 (cut 100) → total_claimed=1500, sanctioned=1400
    Tax row GST 9% → tax=126, grand_total = 1400+126−800 (offset) = 726
    Submit → GL: debit travel account 1526 / credit advance 800 / credit payable 726 ...
    Cashier pays 726 → is_paid → status Paid
  ```

  Cover the normal path **plus one interesting branch** (cut-down approval / multi-currency / partial offset / cancellation). If the domain has journal entries, show them (debit/credit per line). Verify all arithmetic with a script. Presentation: the header states at most "数字已用脚本验证 / numbers script-verified" — no script paths, no run commands, no work/ references in the report; formulas appear as plain math (120,000 ÷ 12 = 10,000), not code syntax (flt(...)).

### 7. State Machine Summary

Only if several state machines exist and weren't fully covered in §6. Otherwise skip.

## Style rules

- **Plain language, concrete rules.** Short sentences, one idea per sentence. Everyday words over fancy ones whenever they mean the same thing. A sentence that needs a dictionary is a rewrite.
- **Explain every domain term once, at first use, in the simplest way** (e.g. "核销 = 用报销冲抵借款", "offsetting = writing off an advance against a claim"). After that, reuse the term — no re-explaining, no quoting it.
- **Code identifiers in the reading path get glossed or removed.** If a field name / API term must appear (e.g. `base_grand_total`, `Dynamic Link`, `per_billed`), give its plain meaning inline at first use; if it adds nothing, drop it. Unglossed identifiers in the narrative are not done — identifiers are welcome only in the evidence appendix. Same for implementation mechanics: function internals, SQL constructs (subqueries/exists), iteration and dimension handling, file-scoped detail — narrate the business behavior or move it to an evidence appendix, when one exists. A sentence that reads like a code walkthrough is a rewrite.
- **No buzzwords or filler.** Banned in reports: leverage, robust, seamless, streamline, empower, comprehensive, cutting-edge, granular, "it is important to note", "in order to", 赋能, 抓手, 闭环 (unless it is the actual domain term), 打通, 体系化. If a word adds nothing, cut it.
- **The worked example is the explanation.** When a concept is hard to describe in words, show it in the example instead of adding more adjectives.
- **Tables** for fields, **ASCII diagrams** for relationships, **code blocks** for formulas/state machines/workflow steps.
- Every entity section cites its schema file path; every workflow step was verified against a real function during research.
- Worked example numbers must be internally consistent (script-checked).
- No marketing/AI-flavored prose. Straight-forward terms.
- **Humanize prose (mandatory):** after drafting, run the humanizer skill on prose paragraphs only (never tables/code/numbers) — works for both Chinese and English reports. Then review each of its changes: keep edits that cut fluff, revert any that weaken technical precision or change a domain term's meaning.
- Deviations from this template must be stated explicitly at the top of the report.

## Mini examples

### A. Field table (style reference)

| Field | Meaning |
|---|---|
| expense_type | Expense type, required, points to Expense Claim Type |
| amount / sanctioned_amount | Claimed amount / sanctioned amount. Sanctioned defaults to claimed; approver may lower it (the "cut") |
| base_amount / base_sanctioned_amount | Base-currency copies (multi-currency: every amount field has a base_* counterpart) |
| default_account | Account. Derived by the system from the (type, company) mapping, not hand-entered, to prevent misclassified postings |

### B. Annotated relationship diagram (style reference)

```
Expense Claim Type ----┐
  └-- Expense Claim Account (company→account mapping) --> Account (chart of accounts)

Expense Claim (claim doc)              Employee Advance (loan doc)
  |-- Expense Claim Detail (line items)        └-- paid/claimed/returned/pending amounts
  |-- Expense Claim Advance (offset bridge) ----┘
  |-- Expense Taxes and Charges (tax rows)
  └- is_paid --> Payment Entry (claim payment)
```

### C. Design insight (style reference)

> An expense claim is essentially a business document plus an accounting voucher; submitting the claim is the posting act itself.

> The advance request has no exchange-rate field. The rate exists only on the payment entry: the rate becomes a fact at the moment of payment.
