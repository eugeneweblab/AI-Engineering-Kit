---
id: engineering/01-decision-framework
topic: engineering
slug: decision-framework
title: "Engineering Decision Framework"
type: doc
order: 1
status: ready
tags: [engineering, decision-framework, findMany, formatCurrency, applyDiscount, apply, DiscountStrategy]
related: [engineering/00-engineering-principles, architecture/26-architecture-decision-records, templates/02-architecture-decision-record]
when_to_use: "Read before writing or modifying code to work through engineering decisions systematically."
---
# Engineering Decision Framework

## Purpose

This document defines a universal decision-making process for engineers and AI coding agents.

Before writing, modifying, or reviewing code, every engineering task should follow the same sequence of decisions.

The framework is intentionally technology-independent and can be applied to any programming language, framework, or codebase.

---

## Step 1 — Understand the Request

Do not start implementing immediately.

Identify:

- the requested outcome;
- the actual problem;
- the expected behavior;
- the scope of the change;
- any explicit constraints.

If the request is ambiguous, resolve the ambiguity before implementation. One wrong assumption here wastes every hour spent downstream.

**Bad Example**

> Ticket: "The export button is broken. Fix it."
>
> The engineer opens the export handler, sees a `null` reference, wraps it in a `try/catch`, and closes the ticket. The button still produces an empty file, because the real request was "the CSV export is missing the new `tax` column."

**Good Example**

> Ticket: "The export button is broken. Fix it."
>
> Before touching code, the engineer asks:
> - What did you click, and what happened?
> - What did you expect instead?
> - Which export (CSV, PDF)? Which screen?
>
> Answer: "The CSV downloads, but the `tax` column is empty since last week's release."
>
> Now the scope is a data-mapping bug in one export path, not a null-guard in the click handler.

The cost of asking is minutes. The cost of guessing is a fix that ships, passes review, and does not solve the problem.

---

## Step 2 — Understand the Existing System

Never assume the current implementation is incorrect.

Inspect:

- project architecture;
- existing patterns;
- related components;
- similar implementations;
- documentation;
- configuration;
- tests.

The goal is to understand why the current solution exists before replacing it.

---

## Step 3 — Define the Real Problem

Many requests describe symptoms instead of root causes.

Examples:

**Request**

> Make this API faster.

Possible root causes:

- unnecessary database queries;
- inefficient caching;
- network latency;
- oversized payloads;
- client-side rendering issues.

Never optimize before identifying the actual bottleneck. Measure first, then change the thing the measurement points at.

**Bad Example — optimize on a guess**

The request is "make the orders page faster." The engineer assumes the database is slow and adds a cache layer:

```ts
// Guessed fix: cache the whole response, no measurement taken.
const cache = new Map<number, Order[]>();

async function getOrders(customerId: number): Promise<Order[]> {
  if (cache.has(customerId)) return cache.get(customerId)!;
  const orders = await loadOrders(customerId);
  cache.set(customerId, orders); // never invalidated → stale data bugs later
  return orders;
}
```

The page is still slow, and now there is a cache with no invalidation path.

**Good Example — measure, then fix the real bottleneck**

Profiling the query first reveals an N+1 pattern: one query for orders, then one more per order for its items.

```ts
// Bad: 1 + N queries. This is what the profiler flagged.
const orders = await db.order.findMany({ where: { customerId } });
for (const order of orders) {
  order.items = await db.item.findMany({ where: { orderId: order.id } });
}
```

```ts
// Good: one query. Load related rows in a single round trip.
const orders = await db.order.findMany({
  where: { customerId },
  include: { items: true },
});
```

The fix targets the measured cause (round-trip count), needs no cache, and introduces no staleness.

---

## Step 4 — Evaluate Existing Solutions

Before introducing new code, determine whether the project already contains an appropriate solution.

Search for:

- reusable components;
- shared utilities;
- helper functions;
- existing services;
- design patterns;
- abstractions.

Reuse should always be considered before creating something new. A second implementation of the same logic is a second place bugs can hide and a second place behavior can drift.

**Bad Example — reimplement what already exists**

```ts
// The project already exports formatCurrency() from utils/currency.ts,
// but a component defines its own formatter with subtly different rules.
function formatPrice(value: number): string {
  return "$" + value.toFixed(2); // wrong for EUR, no locale, no rounding rules
}
```

Now two functions format money differently, and a locale change must be made in two places.

**Good Example — reuse the shared utility**

```ts
import { formatCurrency } from "@/utils/currency";

const label = formatCurrency(value, "USD"); // one source of truth
```

Reuse is not always correct. Reuse only when the existing code matches the new need; forcing an ill-fitting abstraction is worse than a second small function. State the trade-off: if the shared utility would need a new flag or branch for every caller, a purpose-built function is the simpler choice.

---

## Step 5 — Evaluate Impact

Every change has consequences.

Consider:

- affected modules;
- public APIs;
- backward compatibility;
- performance;
- accessibility;
- security;
- testing;
- documentation.

The best implementation is not always the smallest one.

Backward compatibility is the impact most often missed. Changing the shape of a public response breaks every existing consumer at once.

**Bad Example — rename a public field in place**

```ts
// A shipped API returned { userName }. Renaming it breaks every client
// that reads response.userName until they all deploy a matching change.
return { name: user.name };
```

**Good Example — add the new field, deprecate the old one**

```ts
return {
  name: user.name,
  // Deprecated: retained for existing clients. Remove in v3.0 (tracked: JIRA-1421).
  userName: user.name,
};
```

Both callers keep working, the migration has an owner and a removal date, and the change ships without a coordinated flag day.

---

## Step 6 — Choose the Simplest Correct Solution

Prefer solutions that are:

- understandable;
- maintainable;
- testable;
- consistent with the existing architecture.

Avoid introducing unnecessary abstractions.

Avoid solving future problems that do not yet exist.

**Bad Example — abstraction for a single caller**

```ts
// There is exactly one discount rule and one place that uses it.
// A factory + strategy interface adds three files and indirection for no payoff.
interface DiscountStrategy {
  apply(total: number): number;
}

class DiscountStrategyFactory {
  static create(): DiscountStrategy {
    return { apply: (total) => total * 0.9 };
  }
}

const total = DiscountStrategyFactory.create().apply(price);
```

**Good Example — a plain function until a second case exists**

```ts
function applyDiscount(total: number): number {
  return total * 0.9;
}

const total = applyDiscount(price);
```

Introduce the strategy pattern when a second, genuinely different discount rule arrives — not before. The trade-off is real: premature abstraction costs reading time on every future change and hides the one behavior that actually runs.

---

## Step 7 — Verify Before Completing

Before considering the task complete, verify:

- requirements are satisfied;
- existing behavior remains unchanged where expected;
- no unrelated code was modified;
- naming remains consistent;
- documentation remains accurate;
- tests still pass.

Implementation is not complete until verification is complete.

---

## Decision Checklist

Before writing code:

- Do I understand the problem?
- Do I understand the existing implementation?
- Am I solving the root cause?
- Can existing code be reused?
- Is this solution consistent with the project?
- Have I considered side effects?
- Is there a simpler solution?

If any answer is **No**, continue investigating before implementing.

---

## Decision Tree

```
Receive request
        │
        ▼
Understand the problem
        │
        ▼
Inspect existing implementation
        │
        ▼
Identify root cause
        │
        ▼
Search for reusable solution
        │
        ▼
Choose the simplest correct implementation
        │
        ▼
Evaluate impact
        │
        ▼
Implement
        │
        ▼
Verify
        │
        ▼
Complete
```

---

## Worked Example — Applying the Framework End to End

**Request:** "Users are getting logged out randomly. Stop it."

**Step 1 — Understand the request.** Ask for specifics. Answer: sessions drop after roughly 15 minutes of activity, only on the mobile web app, and only since the last release.

**Step 2 — Understand the existing system.** Sessions are JWT-based. The token has a 15-minute expiry and there is a refresh endpoint. The mobile web build was changed last release.

**Step 3 — Define the real problem.** The symptom is "random logout." The evidence points at token refresh, not authentication. Reproduce it: watch the network tab, confirm the refresh call is never sent on mobile.

**Bad diagnosis:** "Sessions are too short — raise the token expiry to 24 hours."

**Good diagnosis:** "The silent-refresh timer was removed on mobile in the last release, so the token expires and is never renewed."

Raising the expiry would hide the bug for most users while weakening security for everyone — a symptom fix.

**Step 4 — Evaluate existing solutions.** The desktop build already has a working refresh scheduler. Reuse it rather than writing a new one.

**Step 5 — Evaluate impact.** The fix touches only the mobile bootstrap. No API change, no token-lifetime change, so no security or backward-compatibility impact.

**Step 6 — Choose the simplest correct solution.** Restore the scheduled refresh before expiry:

```ts
// Refresh the token one minute before it expires, matching desktop behavior.
const REFRESH_MARGIN_MS = 60_000;

function scheduleTokenRefresh(expiresAt: number): () => void {
  const delay = Math.max(0, expiresAt - Date.now() - REFRESH_MARGIN_MS);
  const timer = setTimeout(refreshToken, delay);
  return () => clearTimeout(timer); // cleanup on logout/unmount
}
```

No new abstraction, no widened token lifetime — the smallest change that fixes the measured cause.

**Step 7 — Verify.** Confirm the refresh call fires before expiry on mobile, the session survives past 15 minutes, desktop is unchanged, and add a test asserting `scheduleTokenRefresh` arms the timer. Done.

---

## Summary

Good engineering decisions are rarely the result of writing code quickly.

They are the result of understanding the problem deeply, respecting the existing system, and making deliberate, verifiable changes.

## Related

- `knowledge/engineering/00-engineering-principles.md`
- `knowledge/architecture/26-architecture-decision-records.md`
- `knowledge/templates/02-architecture-decision-record.md`
