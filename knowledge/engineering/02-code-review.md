---
id: engineering/02-code-review
topic: engineering
slug: code-review
title: "Engineering Code Review"
type: doc
order: 2
status: ready
tags: [engineering, code-review, apply, DiscountStrategy, toUpperCase, findMany, findById, findOne]
related: [engineering/00-engineering-principles, workflows/05-review-pull-request, checklists/02-pull-request-author]
when_to_use: "Read before reviewing a pull request or self-reviewing changes for correctness and consistency."
---
# Engineering Code Review

## Purpose

This document defines how software engineers and AI coding agents should review code before considering a task complete.

Code review is not the final step of development.

It is an essential part of engineering that ensures code is correct, maintainable, understandable, and consistent with the project.

This document should be used both for reviewing pull requests and for performing self-review before submitting changes.

---

## Review Mindset

The purpose of a review is to improve the software—not to criticize the author.

A good review focuses on:

- correctness;
- maintainability;
- consistency;
- readability;
- long-term engineering quality.

Every review should assume good intentions.

---

## Review Order

Always review code in the following order.

Do not start by reviewing formatting or naming.

## 1. Requirements

Verify that the implementation satisfies the original requirements.

Ask:

- Does it solve the requested problem?
- Does it solve the correct problem?
- Is any requirement missing?
- Was unnecessary functionality introduced?

---

## 2. Scope

Verify that only the required parts of the project were modified.

Look for:

- unrelated refactoring;
- formatting-only changes;
- accidental file modifications;
- unnecessary dependency updates.

Small pull requests are easier to understand and safer to deploy.

---

## 3. Architecture

Check whether the implementation follows the existing architecture.

Questions:

- Does this fit the project?
- Is a new pattern being introduced?
- Is there an existing solution that should have been reused?
- Does this increase architectural complexity?

Architecture should evolve intentionally.

---

## 4. Simplicity

Prefer the simplest solution that fully satisfies the requirements.

Review for:

- unnecessary abstractions;
- deeply nested logic;
- duplicated responsibilities;
- premature optimization;
- over-engineering.

Simple code is easier to maintain.

**Bad Example** — a strategy registry built for a requirement that has two fixed values.

```ts
interface DiscountStrategy {
  apply(total: number): number;
}

class NoDiscount implements DiscountStrategy {
  apply(total: number) {
    return total;
  }
}

class PercentageDiscount implements DiscountStrategy {
  constructor(private percent: number) {}
  apply(total: number) {
    return total - total * (this.percent / 100);
  }
}

const registry = new Map<string, DiscountStrategy>([
  ["none", new NoDiscount()],
  ["ten", new PercentageDiscount(10)],
]);

function priceFor(code: string, total: number): number {
  return (registry.get(code) ?? new NoDiscount()).apply(total);
}
```

Why it fails: only two codes exist and neither is configurable. Three types and a
registry hide a one-line calculation, and every future reader must trace the
indirection to confirm what the code does.

**Good Example** — direct code that matches the actual requirement.

```ts
const DISCOUNT_PERCENT: Record<string, number> = { none: 0, ten: 10 };

function priceFor(code: string, total: number): number {
  const percent = DISCOUNT_PERCENT[code] ?? 0;
  return total - total * (percent / 100);
}
```

Introduce the strategy pattern when discount rules become dynamic or diverge in
behavior—not before. The trade-off is real: the simple version must be refactored
if requirements grow, but paying that cost later is cheaper than maintaining
unused abstraction now.

---

## 5. Readability

Code should explain itself.

Review:

- names;
- function size;
- class responsibilities;
- file organization;
- logical flow.

Future maintainers should understand the implementation without additional explanation.

---

## 6. Reusability

Determine whether existing code could have been reused.

Look for:

- duplicated utilities;
- duplicated components;
- repeated business logic;
- similar API implementations.

Avoid introducing duplicate solutions.

---

## 7. Error Handling

Verify that failures are handled intentionally.

Check:

- invalid input;
- API failures;
- database failures;
- empty states;
- timeout handling;
- fallback behavior.

Happy-path code is not sufficient.

**Bad Example** — the function assumes every step succeeds.

```ts
async function getUserName(id: string): Promise<string> {
  const res = await fetch(`/api/users/${id}`);
  const user = await res.json();
  return user.name.toUpperCase();
}
```

Failure modes hidden here: a non-2xx response still parses, so a 404 or 500 flows
through as if it were data; a body without `name` throws `Cannot read properties
of undefined` inside `toUpperCase()`, far from the real cause. The reader cannot
tell which failures were considered.

**Good Example** — each failure is handled where it happens and produces a clear signal.

```ts
async function getUserName(id: string): Promise<string> {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) {
    throw new Error(`User ${id} lookup failed with status ${res.status}`);
  }
  const user = (await res.json()) as { name?: string };
  if (!user.name) {
    throw new Error(`User ${id} response is missing a name`);
  }
  return user.name.toUpperCase();
}
```

In review, ask which of these guards is missing rather than whether the happy path
works. The happy path almost always works; the value of the review is the paths
the author did not run.

---

## 8. Security

Every review should include a basic security assessment.

Verify:

- input validation;
- output escaping;
- authentication;
- authorization;
- secrets handling;
- dependency usage.

Security is a requirement, not an enhancement.

The most common defect that passes review is authentication without
authorization: the code confirms *who* the caller is but not whether they may
touch *this* record.

**Bad Example** — any authenticated user can read any invoice by guessing an ID.

```ts
app.get("/invoices/:id", requireAuth, async (req, res) => {
  const invoice = await db.invoice.findById(req.params.id);
  res.json(invoice);
});
```

`requireAuth` proves the user is logged in. It does not prove the invoice belongs
to them. This is an insecure direct object reference (IDOR).

**Good Example** — the query is scoped to the caller, so ownership is enforced by construction.

```ts
app.get("/invoices/:id", requireAuth, async (req, res) => {
  const invoice = await db.invoice.findOne({
    id: req.params.id,
    ownerId: req.user.id,
  });
  if (!invoice) {
    return res.status(404).json({ error: "Not found" });
  }
  res.json(invoice);
});
```

Return `404` rather than `403` for records the caller may not access, so the
endpoint does not leak which IDs exist. Enforcing ownership in the query itself is
safer than a separate `if (invoice.ownerId !== req.user.id)` check, which is easy
to forget on the next endpoint.

---

## 9. Performance

Performance should be reviewed using evidence.

Look for:

- unnecessary rendering;
- duplicate requests;
- repeated calculations;
- excessive database queries;
- unnecessary allocations.

Do not optimize hypothetical bottlenecks.

The highest-value performance finding in review is usually the N+1 query: one
query to load a list, then one more query per item.

**Bad Example** — 100 orders produce 101 database round trips.

```ts
const orders = await db.order.findMany({ where: { status: "open" } });
for (const order of orders) {
  order.customer = await db.customer.findById(order.customerId);
}
```

**Good Example** — two queries regardless of how many orders load.

```ts
const orders = await db.order.findMany({ where: { status: "open" } });
const customerIds = [...new Set(orders.map((o) => o.customerId))];
const customers = await db.customer.findMany({
  where: { id: { in: customerIds } },
});
const byId = new Map(customers.map((c) => [c.id, c]));
for (const order of orders) {
  order.customer = byId.get(order.customerId);
}
```

Review with evidence, not intuition. The N+1 fix only matters when the collection
can grow; for a list that is always three items, the loop is fine and the batched
version is needless complexity. Confirm the pattern in query logs before asking for
a rewrite.

---

## 10. Accessibility

For user interfaces verify:

- keyboard navigation;
- semantic HTML;
- focus management;
- labels;
- color contrast;
- screen reader support.

Accessibility is part of product quality.

---

## 11. Testing

Review whether the implementation is sufficiently verified.

Questions:

- Are existing tests still valid?
- Should new tests exist?
- Are edge cases covered?
- Is manual verification documented when automated testing is unavailable?

---

## 12. Documentation

Determine whether documentation needs updating.

Examples:

- README
- API documentation
- Architecture documentation
- Configuration
- Environment variables
- Migration instructions

Code and documentation should evolve together.

---

## Self Review

Before submitting changes, every engineer should perform a complete self-review.

Self-review should answer the following questions.

## Understanding

- Did I fully understand the problem?
- Did I verify my assumptions?
- Did I inspect similar implementations?

---

## Correctness

- Does the implementation satisfy every requirement?
- Did I verify edge cases?
- Could this introduce regressions?

---

## Consistency

- Does the implementation match project conventions?
- Did I introduce a competing pattern?
- Are naming conventions consistent?

---

## Maintainability

- Can another engineer understand this quickly?
- Can this implementation be extended safely?
- Did I remove unnecessary complexity?

---

## Safety

- Did I accidentally modify unrelated files?
- Did I leave debugging code?
- Did I remove temporary workarounds?
- Did I remove commented-out code?

---

## Final Checklist

Before considering the task complete, verify:

- Requirements are fully satisfied.
- No unrelated code was modified.
- Existing architecture was respected.
- Code is readable.
- Code is maintainable.
- Existing solutions were reused whenever possible.
- Error handling is appropriate.
- Security considerations were reviewed.
- Performance implications were evaluated.
- Accessibility was considered where applicable.
- Tests were updated or verified.
- Documentation remains accurate.

---

## Review Anti-patterns

Avoid reviews that focus primarily on:

- formatting preferences;
- personal coding style;
- unnecessary micro-optimizations;
- subjective opinions without engineering justification.

Every review comment should answer at least one of the following questions:

- Does this improve correctness?
- Does this improve maintainability?
- Does this reduce risk?
- Does this improve consistency?
- Does this improve developer understanding?

If the answer is **no**, the comment may not be valuable.

A useful comment names the observation, the consequence, and the suggested change.
A vague comment forces the author to guess what you meant and why.

**Bad Comment**

> This is wrong. Please fix.

It states no observation, no consequence, and no direction. The author cannot act
on it without a follow-up conversation.

**Good Comment**

> `res.json()` runs before `res.ok` is checked, so a 500 response is parsed as valid
> data and later fails as a `TypeError` in the caller. Guard with
> `if (!res.ok) throw ...` so the error points at the HTTP status instead of an
> unrelated property access.

For anything non-blocking, mark it as such (for example, prefix with `nit:`) so the
author can tell a required change from a preference. This keeps the review honest
about what actually blocks the merge.

---

## Summary

Excellent engineering reviews improve software quality, reduce long-term maintenance costs, and encourage consistent decision-making.

The goal of a review is not to find fault.

The goal is to leave the codebase in a better state than before.

## Related

- `knowledge/engineering/00-engineering-principles.md`
- `knowledge/workflows/05-review-pull-request.md`
- `knowledge/checklists/02-pull-request-author.md`
