---
id: testing/24-best-practices
topic: testing
slug: best-practices
title: "Testing Best Practices"
type: doc
order: 24
status: ready
tags: [testing, best-practices, toBeTruthy, Date, toBe, not.toThrow, toBeDefined, console.log, fast, keep, suite]
related: [testing/01-testing-fundamentals, testing/09-assertions, testing/08-test-organization, testing/22-flaky-tests, testing/29-test-review]
when_to_use: "Read before writing or reviewing any test, to keep the suite fast, clear, and trustworthy."
---
# Testing Best Practices

## Purpose

This document collects the cross-cutting habits that separate a test suite people trust
from one they learn to ignore. It is not about a specific test type — see
[testing fundamentals](01-testing-fundamentals.md) and [testing strategy](28-testing-strategy.md)
for that — but about *how* to write any test so it earns its keep.

A good test proves one behavior, fails for exactly one reason, and reads like a
specification. Everything here serves those three properties.

## Why It Matters

Tests are code that guards code, so their defects are doubly expensive: a wrong test
either blocks correct changes (false positive) or waves through broken ones (false
negative). Both erode trust, and a suite nobody trusts gets skipped, which is worse than
having no suite at all — it costs CI minutes and gives false confidence. The practices
below exist to keep every failure *actionable*: when the suite goes red, an engineer
should know within seconds what broke and why.

## Core Principles

- **Test behavior, not implementation.** Assert on observable outputs and effects, not
  private methods or call counts. Tests coupled to internals break on every refactor and
  teach the team to distrust red.
- **One reason to fail per test.** A test with five unrelated assertions tells you
  something is wrong but not what. Split by behavior so a failure names its own cause.
- **Deterministic or nothing.** A test that passes 99% of the time is a lie 1% of the
  time. No real clocks, real randomness, real network, or shared mutable state.
- **Arrange–Act–Assert, visibly.** Structure every test in three beats so a reader sees
  setup, the action under test, and the expectation without decoding it.
- **The test is documentation.** Its name and body should let a newcomer learn the
  intended behavior without reading the implementation.

## Best Practices

- Name tests as `does X when Y` sentences (`rejects transfer when balance is insufficient`),
  not `test1` or `testTransfer`. The name is the first thing shown on failure.
- Keep one logical assertion per test. Multiple physical `expect`s are fine when they
  describe one behavior (an object's fields); unrelated checks belong in separate tests.
- Build inputs with named factories/builders, not sprawling literals, so each test shows
  only the fields that matter to it (see [test data](07-test-data.md)).
- Assert on specific values, not just "truthy" or "not null" — `expect(total).toBe(42)`
  catches bugs that `expect(total).toBeDefined()` sleeps through (see [assertions](09-assertions.md)).
- Inject time, randomness, and IDs so they can be frozen. Never `sleep()` to wait; poll a
  condition or advance a fake timer (see [flaky tests](22-flaky-tests.md)).
- Keep tests independent: each must pass alone and in any order. No test may depend on
  state left by another.
- Fail fast on the assertion that matters. Put the behavior check first, not buried after
  ten lines of incidental setup.
- Delete or rewrite tests that no longer describe desired behavior. A stale test is debt,
  not coverage.

## Examples

**Good Example** — one behavior, deterministic inputs, specific assertion

```ts
// Time and id are injected, so the result is exact and repeatable.
test("marks invoice overdue when due date has passed", () => {
  const invoice = makeInvoice({ dueDate: "2026-01-01", paidAt: null });
  const now = new Date("2026-02-01"); // frozen clock, no real time

  const status = invoiceStatus(invoice, now);

  expect(status).toBe("overdue"); // specific value, not toBeTruthy()
});
```

**Bad Example** — tests internals, non-deterministic, vague

```ts
test("invoice", () => {
  const invoice = makeInvoice({ dueDate: "2026-01-01", paidAt: null });

  invoiceStatus(invoice, new Date());          // real clock → flaky near boundaries
  expect(invoice._recomputeCount).toBe(1);     // asserts a private counter, not behavior
  expect(invoiceStatus(invoice)).toBeTruthy(); // "overdue", "paid" both pass — proves nothing
});
```

## Common Mistakes

- Asserting on mock call counts or private fields instead of the observable result.
- One giant test that exercises a whole workflow, so any break reports the same red.
- Sharing a mutable fixture across tests, creating order-dependent pass/fail.
- `sleep(500)` to wait for async work — slow and flaky; poll or use fake timers.
- Vague assertions (`toBeTruthy`, `not.toThrow`) that pass on wrong values.
- Copy-pasting a test and forgetting to change the assertion, so it re-tests case one.
- Leaving `console.log`, `.only`, or skipped tests in the committed suite.

## Production Tips

- Track suite runtime as a first-class metric; a slow suite gets skipped locally. Budget
  unit tests in milliseconds, integration in seconds.
- Quarantine, don't ignore, a newly flaky test: move it to a tracked non-blocking lane
  and fix it within a sprint (see [flaky tests](22-flaky-tests.md)).
- Run the suite in randomized order in CI to surface hidden inter-test coupling early.

## AI Review Checklist

- Does each test assert observable behavior rather than implementation details?
- Does the test name state the behavior and condition (`does X when Y`)?
- Are the assertions specific values, not `toBeTruthy`/`toBeDefined`?
- Is the test deterministic — clock, randomness, IDs, and I/O all controlled?
- Can the test pass in isolation and in random order, with no shared state?
- Does a failure point to exactly one cause, or are unrelated checks bundled?
- Are there leftover `.only`, skips, or debug logs?

## Related

- `knowledge/testing/01-testing-fundamentals.md`
- `knowledge/testing/09-assertions.md`
- `knowledge/testing/08-test-organization.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/29-test-review.md`
