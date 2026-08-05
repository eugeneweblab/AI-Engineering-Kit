---
id: engineering/05-context-first-development
topic: engineering
slug: context-first-development
title: "Context-First Development"
type: doc
order: 5
status: ready
tags: [engineering, context-first-development]
related: [engineering/04-task-execution, ai/01-context-gathering, engineering/00-engineering-principles]
when_to_use: "Read before modifying an unfamiliar codebase to gather context before making changes."
---
# Context-First Development

## Purpose

This document defines one of the most important engineering principles in AI-assisted software development:

> Every implementation should begin with understanding the surrounding context before modifying code.

The quality of engineering decisions depends directly on the quality of the available context.

Adding more code without understanding the existing system usually increases technical debt.

### Good Example

A ticket says "add a discount field to the checkout total." Before writing code, the engineer searches the repository and finds an existing `calculateOrderTotal` service that already handles tax and shipping. The discount is added inside that service, so every caller stays consistent.

```ts
// Existing service found by searching for "OrderTotal" before writing anything.
export function calculateOrderTotal(order: Order): Money {
  const subtotal = sumLineItems(order.items);
  const discount = applyDiscounts(subtotal, order.coupons); // reused existing helper
  const taxed = applyTax(subtotal.minus(discount), order.taxRegion);
  return taxed.plus(order.shippingCost);
}
```

### Bad Example

The same ticket is implemented by subtracting a discount in the React component that renders the total. Tax and shipping still calculate from the pre-discount subtotal, and the mobile app (a second caller of the API) never gets the discount at all.

```ts
// Discount bolted onto the view. The server-side total is now wrong,
// and only this one screen shows the discounted price.
const displayTotal = order.total - order.couponAmount;
```

The failure is not a syntax error. It is a missing-context error: the engineer never checked *where* the total is authoritative before changing it.

---

## Core Principle

Context always comes before implementation.

Never begin writing code simply because a file has been identified.

Instead, understand:

- why the file exists;
- how it interacts with the rest of the system;
- what assumptions it makes;
- which architectural decisions it follows.

Implementation without context produces inconsistent software.

---

## What Is Context?

Context is every piece of information that influences an engineering decision.

Examples include:

- project architecture;
- business requirements;
- existing design patterns;
- coding conventions;
- folder structure;
- naming conventions;
- dependencies;
- APIs;
- database schema;
- user experience;
- accessibility requirements;
- security requirements;
- performance requirements.

Context extends beyond the current file.

---

## Levels of Context

Engineering decisions should be made using multiple levels of context.

## Level 1 — Business Context

Understand:

- What problem is being solved?
- Who benefits from this change?
- What is the expected outcome?
- What are the business constraints?

Without business context it is impossible to determine whether a solution is actually correct.

---

## Level 2 — Project Context

Understand the project itself.

Review:

- architecture;
- technology stack;
- coding standards;
- project structure;
- existing conventions.

Every project has its own engineering language.

Learn it before contributing.

---

## Level 3 — Module Context

Inspect the module that will be modified.

Questions:

- What is its responsibility?
- Which modules depend on it?
- Which modules does it depend on?
- Does it expose public APIs?

Understanding module boundaries prevents accidental regressions.

---

## Level 4 — File Context

Read the entire file before modifying it.

Determine:

- overall responsibility;
- public interface;
- internal structure;
- existing comments;
- TODO items;
- technical debt.

Never modify code after reading only a few lines.

---

## Level 5 — Local Context

Only after understanding the larger system should individual functions be modified.

Understand:

- inputs;
- outputs;
- side effects;
- assumptions;
- error handling.

Local optimizations should never violate higher-level architecture.

---

## Context Investigation Checklist

Before writing code, inspect:

- similar implementations;
- existing utilities;
- related components;
- project configuration;
- documentation;
- tests;
- previous implementations.

Engineering is often about discovering existing solutions rather than creating new ones.

### Worked Example

Task: "Add rate limiting to the public API." Investigation happens before any code is written.

```bash
# 1. Is rate limiting already implemented somewhere?
grep -ri "rate.limit\|throttle\|too.many.requests\|429" src/

# 2. What middleware pattern does the project already use?
ls src/middleware/ && grep -rl "export function.*Middleware" src/

# 3. Is there a shared store (Redis/cache) the limiter should use?
grep -ri "redis\|createClient\|cache" src/config/

# 4. Are limits already defined in config rather than hard-coded?
grep -ri "RATE_LIMIT\|MAX_REQUESTS" .env.example src/config/
```

If step 1 finds an existing throttle guard, the task becomes "apply the existing guard to these new routes," not "build a rate limiter." The investigation changed the size of the task and prevented a duplicate implementation. That is the entire point of context-first work.

---

## Context Before Creation

Before creating a new...

## Component

Search for:

- similar UI;
- shared layouts;
- reusable patterns.

---

## Utility

Search for:

- helper functions;
- existing abstractions;
- framework capabilities.

Run a search across the codebase before writing a helper. Use the concept, not the exact name you have in mind, because the existing helper is often named differently.

### Bad Example

Needing to show prices, the engineer writes a fresh formatter that hard-codes the currency and rounding.

```ts
// Reinvented, locale-unaware, and wrong for currencies with no decimals (JPY).
function formatPrice(amount: number): string {
  return "$" + amount.toFixed(2);
}
```

### Good Example

A quick search (`grep -ri "NumberFormat\|formatMoney\|formatCurrency" src/`) shows the platform already offers this, and the team wraps it in one shared helper. Reuse it instead of adding a competing version.

```ts
// One shared helper, driven by the standard Intl API. Correct across locales.
export function formatCurrency(amount: number, currency: string, locale = "en-US"): string {
  return new Intl.NumberFormat(locale, { style: "currency", currency }).format(amount);
}
```

Trade-off: reusing a shared helper couples your feature to its interface, so a breaking change there affects you too. That coupling is almost always cheaper than maintaining a second formatter that silently drifts out of sync.

---

## API Endpoint

Search for:

- existing endpoints;
- reusable services;
- shared validation;
- authentication logic.

---

## Database Model

Review:

- existing relationships;
- naming conventions;
- migration strategy.

---

## Service

Determine whether the responsibility already exists elsewhere.

Prefer extending an existing service over introducing competing abstractions.

---

## Warning Signs

The following often indicate insufficient context.

Examples:

- duplicate components;
- duplicate utilities;
- inconsistent naming;
- multiple architectural patterns;
- unnecessary abstractions;
- excessive refactoring;
- repeated business logic.

Most of these problems originate from implementing before investigating.

---

## AI Guidance

Before generating code, AI coding agents should explicitly determine:

- the architectural pattern being used;
- the conventions followed by the project;
- existing reusable implementations;
- expected coding style;
- likely integration points.

If important context is missing, AI should explain what information is required instead of making assumptions.

### Bad Example

> The user asked for a `sendEmail` function, so here is one using `nodemailer` with an SMTP config.

This ignores whether the project already sends email, which provider it uses, and where credentials live. It is a plausible answer to the wrong question.

### Good Example

> Before adding email sending, I searched the repo and found `src/services/notification.ts`, which already sends transactional email through the existing provider client. I will add your new message type there and reuse the configured client rather than introducing a second email dependency. If you instead want a different provider, tell me and I will adjust.

The second response states what context was gathered, what it implies, and where the change belongs. It also surfaces the one open question instead of guessing.

---

## Self Review

Before implementation ask:

- Do I understand the business problem?
- Do I understand the architecture?
- Have I inspected similar code?
- Have I searched for reusable solutions?
- Do I understand why the current implementation exists?
- Am I modifying the correct location?
- Have I considered downstream effects?

If any answer is **No**, continue investigating.

---

## Anti-patterns

Avoid:

Reading only the current function.

Making assumptions based on filenames.

Creating new abstractions without searching the repository.

Copying code from unrelated projects.

Ignoring project conventions.

Treating every task as an isolated problem.

---

## Examples

**Good Example** — the shape of the change is decided by what already exists

```text
Request: "add CSV export to the orders page"

Context gathered first
  - src/lib/export/ already exists: `toCsv(rows, columns)` used by the invoices page.
  - Exports are streamed via a Route Handler, not generated in the browser
    (src/app/api/invoices/export/route.ts is the pattern).
  - The orders query is already paginated; there is a `findAllForUser` on the
    repository that the invoices export uses in the same way.
  - CONTRIBUTING.md: "no new dependencies without an ADR".

Plan that follows from it
  1. src/app/api/orders/export/route.ts — mirrors the invoices route exactly.
  2. Reuse `toCsv`; add the orders column map next to the invoices one.
  3. No new dependency, no new pattern, no client-side generation.

Estimated diff: ~40 lines, all of it in the shape a reviewer already knows.
```

**Bad Example** — the shape of the change is decided by the first idea

```tsx
// Written without looking: a new dependency, a second CSV implementation, and
// generation in the browser — where the page only has the current page of rows,
// so the export silently contains 20 of 4,000 orders.
import { unparse } from 'papaparse';          // new dependency, no ADR

export function ExportButton({ orders }: { orders: Order[] }) {
  const download = () => {
    const csv = unparse(orders.map((o) => ({ id: o.id, total: o.totalCents / 100 })));
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    window.open(url);
  };

  return <button onClick={download}>Export CSV</button>;
}
```

The code works in the demo, where there are twelve orders. The defect — an export that is
quietly incomplete — is the kind that is trusted for months before anyone notices.

---

## Summary

Strong engineers spend significant time building context before writing code.

The larger the system becomes, the more valuable context becomes.

Understanding the system first consistently produces simpler, safer, and more maintainable solutions than implementation driven by assumptions.

## Related

- `knowledge/engineering/04-task-execution.md`
- `knowledge/ai/01-context-gathering.md`
- `knowledge/engineering/00-engineering-principles.md`
