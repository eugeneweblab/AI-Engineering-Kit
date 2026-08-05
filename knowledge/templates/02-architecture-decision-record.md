---
id: templates/02-architecture-decision-record
topic: templates
slug: architecture-decision-record
title: "Architecture Decision Record Template"
type: doc
order: 2
status: ready
tags: [templates, architecture-decision-record, "@dev", "@maria", DECIMAL, Accepted, JavaScript]
related: [templates/01-pull-request, architecture/26-architecture-decision-records, architecture/25-documentation, engineering/01-decision-framework, templates/03-incident-report]
when_to_use: "Copy when recording a decision that is expensive to reverse or will be questioned later."
---
# Architecture Decision Record Template

## Purpose

An ADR records *why* a decision was made, while the reasoning is still available. Six months
later the code shows what was chosen; only the ADR shows what else was considered and what
constraints applied at the time.

Store them as numbered files under `docs/adr/`, committed with the change they describe.

---

## When to Write One

Write an ADR when at least one is true:

- Reversing the decision would take more than a few days.
- A reasonable engineer would ask "why not X instead?"
- The choice constrains future work (a framework, a data model, a protocol).
- The decision was contested, and the resolution should outlive the discussion.

Do **not** write one for choices the code already explains, or for decisions that are cheap
to revisit — an ADR per library upgrade devalues the ones that matter.

---

## The Template

```markdown
# ADR-0007: Use server-side rendering for the product catalog

- **Status:** Accepted
- **Date:** 2026-07-14
- **Deciders:** @maria, @dev
- **Supersedes:** —
- **Superseded by:** —

## Context

What is true right now that forces a decision. Constraints, requirements, and the pressure
that makes this worth deciding deliberately. Written so someone unfamiliar with the
discussion can follow it.

## Decision

What we are doing, stated in one or two sentences, in the active voice.

## Alternatives considered

### <Alternative A>
Why it was plausible, and the specific reason it was not chosen.

### <Alternative B>
Same.

## Consequences

**Accepted costs** — what becomes harder, slower, or more expensive.

**Benefits** — what this buys, tied to the context above.

**Revisit if** — the condition under which this decision should be reopened.
```

---

## Status Values

| Status | Meaning |
|---|---|
| `Proposed` | Under discussion; not yet acted on |
| `Accepted` | Decided and being implemented |
| `Superseded by ADR-NNNN` | A later decision replaced it |
| `Deprecated` | No longer applies, with nothing replacing it |

**Never edit an accepted ADR's decision.** Write a new one that supersedes it and link both
ways. The record is a history, not a current-state document — rewriting it destroys exactly
what makes it useful.

---

## A Filled Example

```markdown
# ADR-0007: Store money as integer cents

- **Status:** Accepted
- **Date:** 2026-03-02
- **Deciders:** @dev, @finance-lead

## Context

Order totals were stored as `DECIMAL(10,2)` in Postgres and read into JavaScript numbers.
Two support tickets in January traced to a one-cent discrepancy between the invoice and the
charged amount, introduced by floating-point rounding in the discount calculation.

We support four currencies today, including JPY, which has no minor unit.

## Decision

Store all monetary values as integers in the currency's smallest unit, alongside an
explicit currency code. Formatting happens at the presentation boundary only.

## Alternatives considered

### Keep DECIMAL and use a decimal library in the application
Correct, and would have solved the rounding. Rejected because the boundary is easy to
violate — any code path that reads the value as a plain number reintroduces the bug, and
nothing enforces the library's use.

### Store as DECIMAL and round at every calculation
Rejected: it makes correctness a discipline rather than a property. The January defect was
exactly this pattern, applied inconsistently.

## Consequences

**Accepted costs**
- A migration over `orders`, `refunds`, and `invoice_lines`, with a backfill.
- Zero-decimal currencies need a per-currency exponent; a naive `/100` is wrong for JPY.
- Every read site needs updating; a plain integer reads as a plausible amount, so a missed
  site shows 100x the price rather than failing loudly.

**Benefits**
- Rounding errors become structurally impossible rather than avoided by care.
- Matches how Stripe represents amounts, removing a conversion at the boundary.

**Revisit if** we adopt a currency with more than two minor-unit digits, or move billing
entirely to a third party that owns the arithmetic.
```

---

## Common Mistakes

- **Writing the ADR after the fact, from the code.** The alternatives are already forgotten;
  that section becomes fiction.
- **Recording only the decision.** Without context and alternatives, it is a comment, not a
  record.
- **Editing history** instead of superseding it.
- **An ADR per commit**, which buries the handful that matter.
- **No "revisit if"**, leaving no signal for when the decision has expired.

---

## Examples

**Good Example** — the alternatives and the cost are recorded, not just the choice

```markdown
# ADR-014: Use Postgres row-level security for tenant isolation

**Status** Accepted — 2026-08-04
**Deciders** Platform team
**Supersedes** ADR-009 (application-level tenant filtering)

## Context
Three incidents in six months were cross-tenant data leaks caused by a query
that forgot `WHERE tenant_id = ?`. Application-level filtering puts the
invariant in every query, where it is one omission away from failing.

## Decision
Enforce tenant isolation with Postgres row-level security. The application sets
`SET LOCAL app.tenant_id` at the start of each transaction; policies do the rest.

## Consequences
Positive — a forgotten filter now returns zero rows instead of another tenant's.
Negative — every connection must run in a transaction; connection pooling needs
`pgbouncer` in transaction mode. Migrations must set the tenant explicitly.
Cost — roughly two weeks to migrate 40 tables, plus a load test.

## Alternatives considered
- **Schema per tenant** — strongest isolation, but 4,000 schemas breaks
  migrations and connection reuse at our tenant count.
- **Keep application-level filtering, add a lint rule** — cheap, but the rule
  cannot see dynamic query builders, which is where two of the three leaks were.
```

**Bad Example** — a decision with no reasoning to review later

```markdown
# ADR-014: Use RLS

**Status** Accepted

## Decision
We will use row-level security.

## Consequences
Better security.
```

In a year, nobody can tell whether schema-per-tenant was rejected for a good reason or never
considered — so the argument is had again from scratch, with less information.

---

## Related

- `knowledge/templates/01-pull-request.md`
- `knowledge/architecture/26-architecture-decision-records.md`
- `knowledge/architecture/25-documentation.md`
- `knowledge/engineering/01-decision-framework.md`
- `knowledge/templates/03-incident-report.md`
