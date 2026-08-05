---
id: engineering/03-debugging-methodology
topic: engineering
slug: debugging-methodology
title: "Debugging Methodology"
type: doc
order: 3
status: ready
tags: [engineering, debugging-methodology]
related: [engineering/04-task-execution, workflows/02-fix-a-bug, workflows/06-investigate-production-bug]
when_to_use: "Read before debugging a defect to investigate the root cause systematically."
---
# Debugging Methodology

## Purpose

This document defines a structured approach to debugging software systems.

Debugging is an investigation process, not a guessing process.

The goal is to identify and eliminate the root cause of a problem with the smallest possible change while preserving existing behavior.

This methodology applies to all technologies, programming languages, and AI coding agents.

---

## Core Principle

Never fix a bug you do not understand.

Every bug has a cause.

Until that cause is identified, every code change is a hypothesis.

---

## The Debugging Process

Always follow the same sequence.

```
Observe
    ↓
Reproduce
    ↓
Define Expected Behavior
    ↓
Isolate the Problem
    ↓
Collect Evidence
    ↓
Identify the Root Cause
    ↓
Design the Fix
    ↓
Verify the Fix
    ↓
Prevent Regression
```

Never skip steps.

---

## Step 1 — Observe

Understand what actually happened.

Collect evidence before writing code.

Examples:

- error messages;
- stack traces;
- logs;
- screenshots;
- recordings;
- browser console output;
- network requests;
- API responses.

Facts are more valuable than assumptions.

---

## Step 2 — Reproduce

A bug that cannot be reproduced cannot be reliably fixed.

Determine:

- exact steps;
- environment;
- browser;
- operating system;
- device;
- user permissions;
- application state;
- feature flags.

Document the shortest possible reproduction.

---

## Step 3 — Define Expected Behavior

Before fixing the issue, define what should happen.

Questions:

- What is the correct behavior?
- Where is it documented?
- Does another feature behave correctly?
- Is the current behavior actually incorrect?

Do not assume the report is accurate.

---

## Step 4 — Isolate the Problem

Reduce the problem to the smallest possible scope.

Identify:

- affected component;
- affected service;
- affected API;
- affected database query;
- affected configuration;
- affected dependency.

The smaller the investigation area, the faster the solution.

---

## Step 5 — Collect Evidence

Avoid changing code during investigation.

Instead:

- inspect variables;
- inspect network traffic;
- inspect logs;
- inspect database records;
- inspect request payloads;
- inspect configuration.

Evidence should explain the behavior.

Observe without changing behavior. Temporary logging that you remove afterward is evidence collection. Editing business logic mid-investigation is not—it hides the original bug behind a second change and makes root cause verification impossible.

### Good Example

```js
// Observe the actual values without altering control flow.
console.debug('checkout.user', { userId: user?.id, cartId: cart.id });
```

### Bad Example

```js
// A "fix" added during investigation. Now the guest branch masks
// the real defect: you can no longer tell why user was missing.
if (!user) {
  user = await createGuestUser();
}
```

---

## Step 6 — Identify the Root Cause

Ask repeatedly:

Why did this happen?

Continue until the underlying cause becomes clear. Each answer should be an observed fact, not a guess.

### Bad Example — a symptom described as a cause

"The button doesn't work." This is the report, not a diagnosis. It names no component, no line, and no verifiable fact. Any fix based on it is a guess.

### Good Example — a chain of observed facts

Keep asking "why" until the answer is a specific, verifiable statement:

1. The button does nothing when clicked.
2. Why? The click handler never runs (no log line fires).
3. Why? The button is never rendered—its container returns `null`.
4. Why? The container renders only when `isReady === true`.
5. Why? `isReady` is derived from `data?.status`, and the API now returns `state` instead of `status`, so `isReady` is always `false`.

Root cause: a renamed API field. Fix the field mapping—not the button.

Fix the root cause, not the symptom.

---

## Step 7 — Design the Fix

Before modifying code, determine:

- smallest safe change;
- affected modules;
- possible regressions;
- existing patterns to follow;
- existing utilities to reuse.

Avoid rewriting working code.

---

## Step 8 — Verify the Fix

Confirm that:

- the bug no longer exists;
- no new issues were introduced;
- related functionality still works;
- edge cases behave correctly.

Verification is mandatory.

---

## Step 9 — Prevent Regression

Whenever practical:

- add a test;
- improve validation;
- improve logging;
- improve documentation;
- simplify the implementation.

A good fix reduces the chance of the same issue returning.

---

## Debugging Rules

Always:

- understand before changing;
- reproduce before fixing;
- isolate before modifying;
- verify before closing.

Never:

- guess;
- rewrite unrelated code;
- ignore warnings;
- suppress errors without understanding them.

---

## Debugging Checklist

## Investigation

- Can the issue be reproduced?
- Is the expected behavior known?
- Has the affected area been isolated?
- Was sufficient evidence collected?

---

## Solution

- Was the root cause identified?
- Is the solution minimal?
- Does it follow existing architecture?
- Were existing utilities reused?

---

## Verification

- Is the original issue fixed?
- Were edge cases tested?
- Was regression risk evaluated?
- Were tests updated if needed?

---

## Common Anti-patterns

## Guess-Driven Development

Changing random code until something appears to work.

---

## Symptom Fixing

Masking the visible issue while leaving the underlying cause unchanged.

The bug returns the moment the input changes, and the masking code becomes a permanent source of confusion for the next reader.

### Bad Example

```js
// The total renders as a concatenated string like "09.9912.00".
// This clamps the display but the total is still wrong.
const displayTotal = Number.isNaN(Number(total)) ? '0.00' : total;
```

### Good Example

```js
// Fix where the wrong type enters the system: coerce once, at the boundary.
function normalizeItems(apiItems) {
  return apiItems.map((item) => ({ ...item, price: Number(item.price) }));
}
```

---

## Rewrite Instead of Investigate

Replacing large parts of the implementation without understanding the defect.

---

## Multiple Changes at Once

Making several unrelated modifications during debugging.

This makes root cause verification difficult.

---

## Ignoring Existing Patterns

Implementing a completely new solution instead of following existing architecture.

---

## AI Guidance

When debugging, AI coding agents should:

1. Gather evidence before proposing fixes.
2. Inspect existing implementations.
3. Explain the suspected root cause.
4. Clearly distinguish facts from assumptions.
5. Propose the smallest safe change.
6. Explain possible side effects.
7. Suggest verification steps after implementation.

AI should never present hypotheses as facts.

---

## Worked Example

This example applies every step to one concrete defect.

**Report:** "The cart total is wrong."

### Step 1–3 — Observe, Reproduce, Define Expected

- Observe: the total renders as `09.9912.00` instead of `21.99`.
- Reproduce: happens on every cart with two or more items. The shortest reproduction is a cart with two items.
- Expected: the total is the numeric sum of item prices.

### Step 4–5 — Isolate and Collect Evidence

Isolate to the summing function. Add one temporary log to inspect the values without changing behavior:

```js
function calculateTotal(items) {
  console.debug('calculateTotal.items', items);
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

The log shows `price` arrives as a string: `[{ price: "9.99" }, { price: "12.00" }]`.

### Step 6 — Identify the Root Cause

With string operands, `sum + item.price` concatenates instead of adding: `0 + "9.99"` yields `"09.99"`. The prices are strings because the API response is used without type coercion. That is the root cause—not the display.

### Step 7 — Design the Fix

The smallest safe change is to coerce prices to numbers once, at the boundary where the API data enters the system. Leave `calculateTotal` untouched so it keeps a single responsibility.

### Bad Example — patch the symptom at the render site

```js
// Hides the bug for two-item carts, breaks differently for three items,
// and leaves every other consumer of the data still broken.
const displayTotal = String(total).replace(/^0/, '');
```

### Good Example — fix the type at the boundary

```js
function normalizeItems(apiItems) {
  return apiItems.map((item) => ({ ...item, price: Number(item.price) }));
}

function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

### Step 8–9 — Verify and Prevent Regression

Verify the total is now `21.99`, and lock the behavior in with a test that fails against the old code:

```js
test('calculateTotal sums numeric prices', () => {
  const items = normalizeItems([{ price: '9.99' }, { price: '12.00' }]);
  expect(calculateTotal(items)).toBeCloseTo(21.99);
});
```

Remove the temporary `console.debug` line before finishing.

---

## Examples

**Good Example** — narrow the search space with evidence at each step

```text
Symptom     Checkout returns 500 for ~2% of users since 14:10 today.

1. Bound it
   Logs: all failures carry `plan: "legacy"`. 98% of traffic is `plan: "standard"`.
   → not load, not infrastructure; it is data-dependent.

2. Bisect the change
   git log --oneline --since="12:00" → 3 deploys. The 14:05 one touched pricing.
   git bisect between 12:00 and 14:10 using a request replay → lands on 8f2c1a9.

3. Read the diff, not the whole file
   8f2c1a9 changed `plan.discountPercent` from optional to required.
   Legacy plans have it as null in the database.

4. Confirm before fixing
   Reproduced locally by seeding one legacy plan: same stack trace, same 500.
```

```diff
-const discount = plan.discountPercent;
+// Legacy plans predate the field; treat a missing value as no discount.
+const discount = plan.discountPercent ?? 0;
```

Every step removed possibilities. The fix was written once, after the cause was known.

**Bad Example** — change things until the symptom disappears

```text
14:20  Restarted the service. Still failing.
14:35  Rolled back the cache config "just in case". No change.
14:50  Added a try/catch around the pricing call, returning a default price.
       Errors stopped appearing in the log.
15:00  Marked resolved.
```

The 500s stopped; the wrong prices did not. Legacy customers are now charged the default
price silently, the cause is still unknown, and the try/catch removed the only signal that
would have led to it.

---

## Summary

Effective debugging is a disciplined engineering process.

The fastest fix is rarely the best fix.

Understanding the problem thoroughly almost always leads to a simpler, safer, and more maintainable solution.

## Related

- `knowledge/engineering/04-task-execution.md`
- `knowledge/workflows/02-fix-a-bug.md`
- `knowledge/workflows/06-investigate-production-bug.md`
