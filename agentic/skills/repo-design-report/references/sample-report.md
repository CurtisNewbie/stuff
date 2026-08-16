# 借款与报销 设计研究报告（样张）

> 本文件是数据模型优先风格的完整样张，领域是合成的（员工借款 + 报销，5 张表），只演示风格与质量标准。真实报告中的 schema 路径、证据点等要素以实际项目为准。

## 1. 核心实体与用途总表

| 表 | 用途 |
|---|---|
| employee 员工 | 员工主数据，借款和报销的主体 |
| advance 借款单 | 员工向公司借的一笔钱，含已核销金额 |
| expense_claim 报销单 | 一次报销请求，含审批状态 |
| expense_item 报销明细 | 报销单的行：哪类费用、申请多少、核定多少 |
| advance_settlement 核销记录 | 桥表：一次"用报销冲销借款"就是一行 |

## 2. 核心概念

- **一个业务对象一张表**：借款单、报销单、明细、核销记录各是一张物理表，一份数据一行。明细是子表，行靠 parent 挂在报销单下面；加字段就是加列。
- **状态分两层**：生命周期状态（草稿/已提交/已取消，系统预置、含义固定）和业务状态（审批走到哪一步、借款核销了多少）。本系统没有审批工作流，"已提交/已审批/已付款"就是业务字段，代码自己维护。
- **余额不存，现算**：借款单只存"借了多少"和"已核销"，剩余未核销永远是算出来的（见 §6 设计洞察）。

## 3. 实体关系

```
employee ──< advance ──┐
                       └──< advance_settlement >── expense_claim ──< expense_item
```

- employee 1:N advance：一个员工有多张借款单。
- expense_claim 1:N expense_item：父表删，明细跟着删。
- advance N:M expense_claim，经核销记录桥接，按 (advance_id, claim_id) 关联：借款可被多张报销单分次冲销，一张报销单也可冲销多笔借款。
- advance.claimed_amount 不手填，系统在每次核销时累加写入，约束条件等于核销记录按 advance_id 求和（见 §5 步骤 4）。

## 4. 表字段详解

概念总结：借款单和报销单是两个独立单据，中间靠核销记录连接；已核销金额由系统累加写入，剩余未核销永远现算。

### employee 员工

借款和报销都要落到具体的人身上，这张表就是那个"人"。

| 字段 | 含义 |
|---|---|
| id | 员工编号 |
| name | 姓名 |
| dept_id | 部门编号 |

### advance 借款单

员工向公司借钱，得有一张单子记着借给谁、借多少，以及这笔钱后来被核销了多少。

| 字段 | 含义 |
|---|---|
| id | 借款单号 |
| employee_id | 借给谁（关联 employee） |
| amount | 借款金额，人工填 |
| claimed_amount | 已核销金额，系统写回：每次核销时累加，等于核销记录按 advance_id 求和 |
| status | 状态：草稿 / 已借款 / 已结清（派生：claimed_amount = amount 时自动结清） |

### expense_claim 报销单

一次报销就是一张单：谁报销、总额多少、走到哪一步了。

| 字段 | 含义 |
|---|---|
| id | 报销单号 |
| employee_id | 谁报销（关联 employee） |
| total_amount | 总额，系统写回 = 明细行核定金额之和 |
| status | 状态：草稿 / 已提交 / 已审批 / 已付款 |

### expense_item 报销明细

一张报销单可以贴很多票，每张票一行：哪类费用、申请多少。砍价就发生在这一层。

| 字段 | 含义 |
|---|---|
| claim_id | 属于哪张报销单（关联 expense_claim） |
| expense_type | 费用类型（差旅、餐饮、办公...） |
| amount | 申请金额，人工填 |
| sanctioned_amount | 核定金额，审批人可调低（"砍价"），默认等于申请金额 |
| pay_from_advance | 是否用借款支付，人工勾选；决定核销步骤处理哪些行 |

### advance_settlement 核销记录

借款要被多张报销单分次冲销，每次冲销记一行，否则"还欠多少、抵了多少"就说不清。

| 字段 | 含义 |
|---|---|
| id | 记录号 |
| advance_id | 冲销哪笔借款（关联 advance） |
| claim_id | 来自哪张报销单（关联 expense_claim） |
| amount | 本次冲销金额，系统写回 = 对应明细行的核定金额 |

Schema: sample/advance_settlement.json（样张为合成领域，仅演示引用格式）

## 5. 核心工作流

流程总览：借款 → 报销 → 审批（可砍价）→ 核销 → 付款。

1. **借款**
   业务：员工申请借款，公司放款。
   表操作：写 advance（金额、状态）→ 状态 草稿→已借款。
2. **报销**
   业务：员工贴票填明细，每行是"哪类费用、申请多少"，可勾选"用借款付"。
   表操作：写 expense_claim + expense_item 行 → 读明细行求和 → 写回 claim.total_amount。
3. **审批（可砍价）**
   业务：审批人逐行看明细，可把核定金额改小，总额跟着变。
   表操作：逐行读 expense_item → 写 item.sanctioned_amount → 重算写回 claim.total_amount → 状态 已提交→已审批；驳回则回草稿。
4. **核销**
   业务：付款前，把勾了"用借款付"的明细行冲销对应借款。
   表操作：对每行借款类明细，写 advance_settlement（advance_id, claim_id, 金额=核定金额）→ 写回 advance.claimed_amount += 行金额。
5. **付款**
   业务：公司支付应付金额（总额 − 已核销）。
   表操作：读 claim.total_amount、核销记录求和 → 写 claim.status = 已付款。

状态机：

```
expense_claim.status:  草稿 --提交--> 已提交 --审批--> 已审批 --付款--> 已付款
                                    \--驳回--> 草稿
advance.status:        草稿 --放款--> 已借款 --(claimed_amount = amount)--> 已结清
```

关键公式：

- claim.total_amount = Σ expense_item.sanctioned_amount
- advance.claimed_amount = Σ advance_settlement.amount（按 advance_id）
- 应付金额 = claim.total_amount − Σ advance_settlement.amount（按 claim_id）

直观理解：借款单上没人填"还剩多少没核销"。已核销是核销记录一行行加出来的，剩余 = 借了多少 − 已核销，全是现算，不会出现"账实不符"。

**完整示例（数字已用脚本验证）**

员工 A 借了 800 元，出差回来报销：

```
明细：机票 1000（申请）、酒店 500（申请），机票勾选"用借款付"
审批：机票 1000、酒店 400（砍 100）→ total_amount = 1000 + 400 = 1400
核销：机票行冲销借款 → 核销记录写一行 800 → advance.claimed_amount = 800，剩余 0
应付 = 1400 − 800 = 600 → 付款 600 → 报销单状态 = 已付款
```

（本领域不涉及会计；若涉及，此处给出借/贷分录，并检查借方合计 = 贷方合计）

## 6. 设计洞察

- **借款与报销不直接挂钩，中间隔一张桥表。** 借款可以分多次被不同报销单冲销，每次冲销都是一行历史记录，谁在什么时候抵了哪笔，可审计。
- **剩余余额不存储，永远现算。** 借款单存 amount 和 claimed_amount（核销时累加写回），不存"剩余未核销"，报表时用 amount − claimed_amount 现算。存余额的表迟早对不上账，算出来的余额不会。
- **金额在明细不在主表。** 砍价发生在行级别，主表总额只是明细的和。审批粒度细，总额永远对得上。
