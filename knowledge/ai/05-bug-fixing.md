---
id: ai/05-bug-fixing
topic: ai
slug: bug-fixing
title: "Bug Fixing"
type: doc
order: 5
status: ready
tags: [ai, bug-fixing]
related: [ai/01-context-gathering, engineering/03-debugging-methodology, workflows/02-fix-a-bug]
when_to_use: "Read before investigating and fixing a bug to find the root cause and avoid regressions."
---
# Bug Fixing

## Purpose

This document defines the standard process AI coding agents should follow when fixing software defects.

Bug fixing is an engineering investigation, not a code generation task.

The objective is to identify the root cause, implement the smallest safe fix, verify the solution, and avoid introducing regressions.

---

## Core Principle

Never fix a symptom.

Always identify and fix the underlying cause.

A bug that appears solved but whose root cause remains is likely to return.

---

## Bug Fix Workflow

Every bug investigation should follow the same sequence.

```
Receive Report
       ↓
Understand Expected Behavior
       ↓
Reproduce
       ↓
Gather Evidence
       ↓
Identify Root Cause
       ↓
Design Smallest Safe Fix
       ↓
Implement
       ↓
Verify
       ↓
Prevent Regression
```

Skipping investigation usually produces unstable fixes.

---

## Step 1 — Understand the Bug Report

Before reading code, determine:

- what the user expected;
- what actually happened;
- when the problem occurs;
- when it does not occur;
- whether the issue is reproducible.

Clarify ambiguous reports before continuing.

---

## Step 2 — Reproduce the Problem

Never implement a fix without reproducing the issue whenever possible.

The most reliable reproduction is an automated one. Before touching the source, encode the bug as a **failing test** that asserts the expected behavior. This test must be *red* for the current code and will become the regression guard in Step 9. Writing it first forces you to state the bug precisely and gives you an objective signal for "fixed" instead of a subjective click-through.

Bad — reproducing by hand and eyeballing the result:

```
"I ran the app, clicked Save, and the record didn't appear. Fixing now."
```

Good — a failing test that pins the exact input and expected output:

```ts
// discount.service.spec.ts — RED before the fix, GREEN after.
// Bug report: "$100 order with a 20% coupon still charges $100."
it('applies a percentage coupon to the order total', () => {
  const total = applyCoupon({ amountCents: 10_000, coupon: { type: 'percent', value: 20 } });
  expect(total).toBe(8_000); // fails today: returns 10_000
});
```

Run only this test in watch mode so the feedback loop is a few hundred milliseconds, not a full suite:

```bash
# Jest — run one file, one test name, watching for changes
npx jest discount.service.spec.ts -t 'applies a percentage coupon' --watch

# Vitest equivalent
npx vitest run discount.service.spec.ts -t 'applies a percentage coupon'
```

When the bug is environmental rather than logical, the reproduction must still be captured explicitly. Record the variables that flip the behavior — browser, OS, device, permissions, feature flags, user role, application state, input data — and narrow to the *smallest* set that still reproduces. A bug that only appears for `role: 'guest'` with `featureFlags.newCheckout = true` is a two-line reproduction, not "sometimes checkout breaks."

The shortest reliable reproduction is the best starting point.

---

## Step 3 — Gather Evidence

Collect evidence before changing code. Runtime evidence — logs, stack traces, network requests, API responses, database records, browser console, screenshots, recordings — explains *what* is happening. Version-control history explains *when it started* and *which change caused it*, which is often the fastest path to the root cause of a regression.

Two git techniques do most of the work.

**Search history for where the offending value or symbol lives.** `git log -S` (the "pickaxe") finds the commit where a string was added or removed — far more precise than reading `git blame` on the current line, because the current line may be innocent and the real change happened elsewhere:

```bash
# When did the string 'percent' enter the coupon code, and in what change?
git log -S 'percent' --oneline -- src/billing/discount.service.ts

# Show the full diff of the suspect commit
git show <commit> -- src/billing/discount.service.ts
```

**Bisect to the exact regression commit** when you know a version that worked. `git bisect` binary-searches history; scripting it with `git bisect run` makes it fully automated using the failing test from Step 2 as the oracle:

```bash
git bisect start
git bisect bad HEAD           # current commit is broken
git bisect good v2.3.0        # this release was fine
# The test exits non-zero on the buggy commit, zero on a good one.
git bisect run npx jest discount.service.spec.ts -t 'applies a percentage coupon'
git bisect reset              # always clean up when done
```

`git bisect run` prints the first bad commit and its author, message, and diff — usually the single most useful piece of evidence in a regression investigation.

Evidence should explain the observed behavior *and* localize it to a specific change before you edit anything.

---

## Step 4 — Inspect Existing Code

Read the complete implementation.

Review:

- related services;
- helper functions;
- validation;
- dependencies;
- surrounding modules;
- similar implementations.

Never assume the first suspicious line is the cause.

---

## Step 5 — Identify the Root Cause

Continue investigating until the underlying reason is known. Distinguish three levels and keep asking "why" until the answer is a specific line of code or data, not a restatement of the symptom:

| Level | Coupon example |
| --- | --- |
| Symptom | A $100 order with a 20% coupon still charges $100. |
| Cause | `applyCoupon` returns the original total unchanged. |
| Root cause | The percent branch divides by 100 using integer math, so `value / 100` is `0`, and `amount - 0` equals the original amount. |

The root cause is the line you can point at and the reason the test in Step 2 fails. Here it is a specific defect, not a vague "validation is wrong":

Bad — the buggy code. Integer division truncates `20 / 100` to `0`:

```ts
function applyCoupon({ amountCents, coupon }: { amountCents: number; coupon: Coupon }): number {
  if (coupon.type === 'percent') {
    // value/100 is 0.2 in float, but the surrounding logic below
    // truncates: (value / 100 | 0) === 0, so nothing is discounted.
    const rate = coupon.value / 100 | 0;
    return amountCents - amountCents * rate;
  }
  return amountCents - coupon.value;
}
```

The `| 0` bitwise operation was added in an unrelated "round the rate" change (found via `git log -S` in Step 3). It is the true root cause; the missing discount is only the symptom.

Only the root cause should be fixed. A tempting symptom fix — special-casing 20% or clamping the output — would leave every other percentage broken.

---

## Step 6 — Design the Fix

Before editing code determine:

- the smallest required change;
- affected files;
- possible side effects;
- reusable utilities;
- verification strategy.

Prefer extending existing logic over replacing it.

---

## Step 7 — Implement Carefully

The fix should be the minimum diff that eliminates the root cause found in Step 5 — no rename, no restructure, no drive-by cleanup. For the coupon bug the correct change is a single line: remove the truncating `| 0` and compute the discount in integer cents so money stays exact.

Good — the smallest change that makes the Step 2 test go green:

```ts
function applyCoupon({ amountCents, coupon }: { amountCents: number; coupon: Coupon }): number {
  if (coupon.type === 'percent') {
    // Keep arithmetic in integer cents: multiply first, divide last.
    return amountCents - Math.round((amountCents * coupon.value) / 100);
  }
  return amountCents - coupon.value;
}
```

The diff touches one branch of one function. It preserves the signature, the naming, and the fixed-amount branch. Re-run the watched test from Step 2 — it now passes — and run the file's full suite to confirm no sibling case regressed.

During implementation:

- preserve architecture;
- preserve naming;
- preserve existing behavior;
- modify only required files;
- avoid unrelated refactoring.

Every changed line should have a clear reason.

---

## Step 8 — Verify the Fix

Confirm:

- the original bug no longer exists;
- existing functionality still works;
- edge cases behave correctly;
- related features remain unaffected.

Never assume a successful compilation means the bug is fixed.

---

## Step 9 — Prevent Regression

The failing test written in Step 2 is now the primary regression guard — keep it. Strengthen it so it locks in the *class* of defect, not just the one reported value. The original bug was truncation, so add the boundary cases that truncation and rounding get wrong:

```ts
describe('applyCoupon percent branch (regression: integer truncation)', () => {
  it.each([
    [10_000, 20, 8_000],  // the reported case
    [10_000, 100, 0],     // full discount must not underflow
    [999, 33, 669],       // 999 - round(329.67) = 999 - 330
    [10_000, 0, 10_000],  // zero coupon is a no-op
  ])('amount %i cents at %i%% -> %i', (amount, value, expected) => {
    expect(applyCoupon({ amountCents: amount, coupon: { type: 'percent', value } })).toBe(expected);
  });
});
```

Name the test after the defect so the next engineer sees *why* it exists, and reference the issue in the commit body. Beyond the test, prevent recurrence at the source: if the root cause was a category error (money handled in floats, unvalidated input, a missing null guard), fix the category — improve validation, tighten a type, or add a lint rule — so the same mistake cannot re-enter silently.

A good bug fix reduces the probability of the same defect returning.

---

## AI Execution Checklist

## Investigation

☐ Understand the bug report.

☐ Reproduce the issue.

☐ Collect evidence.

☐ Read all related code.

☐ Search for similar implementations.

☐ Identify the root cause.

---

## Implementation

☐ Modify the smallest possible area.

☐ Reuse existing utilities.

☐ Preserve architecture.

☐ Avoid unrelated refactoring.

☐ Keep public behavior unchanged unless required.

---

## Verification

☐ Reproduce the original scenario.

☐ Verify related scenarios.

☐ Review side effects.

☐ Remove debug code.

☐ Verify tests.

☐ Update documentation if required.

---

## Risk Assessment

Before implementing, estimate the impact.

Low Risk

- UI text
- Styling
- Documentation

Medium Risk

- Validation
- Component logic
- API behavior

High Risk

- Authentication
- Authorization
- Database schema
- Payments
- Shared infrastructure
- Public APIs

Higher-risk fixes require additional verification.

---

## Common Anti-patterns

Avoid:

Fixing symptoms instead of causes.

Making multiple unrelated changes.

Guessing instead of investigating.

Suppressing errors.

Replacing large implementations unnecessarily.

Deleting code without understanding why it exists.

Declaring the issue fixed without verification.

---

## AI Responsibilities

When proposing a bug fix, AI should explain:

- the observed behavior;
- the expected behavior;
- the suspected root cause;
- supporting evidence;
- why the proposed solution is appropriate;
- possible risks;
- how the fix should be verified.

Engineering decisions should always be transparent.

---

## Definition of Success

A bug fix is successful when:

- the root cause has been eliminated;
- the smallest reasonable change was made;
- existing functionality remains intact;
- regression risk is minimized;
- the implementation follows project conventions;
- verification confirms the issue is resolved.

---

## Summary

Professional bug fixing is a structured investigation process.

The quality of a bug fix is determined not by how quickly code was changed, but by how confidently the underlying problem was understood and resolved.

## Related

- `knowledge/ai/01-context-gathering.md`
- `knowledge/engineering/03-debugging-methodology.md`
- `knowledge/workflows/02-fix-a-bug.md`
