---
id: testing/01-testing-fundamentals
topic: testing
slug: testing-fundamentals
title: "Testing Fundamentals"
type: doc
order: 1
status: ready
tags: [testing, testing-fundamentals, spyOn, toBeDefined, toHaveBeenCalled, toBe, place, whether, test]
related: [testing/00-overview, testing/02-unit-testing, testing/03-integration-testing, testing/09-assertions, testing/28-testing-strategy]
when_to_use: "Read before deciding what kind of test to write or reviewing whether a test earns its place."
---
# Testing Fundamentals

## Purpose

This document defines the mental model every other testing doc builds on: what a test is
for, how to structure one, which level to write it at, and how to tell a good test from a
harmful one. It is written so an agent can decide *whether* and *how* to test a change
before writing a single assertion.

A test is an executable claim about behavior. It has one job: to fail loudly when that
behavior breaks, and to stay silent otherwise. Everything below serves that job.

## Why It Matters

Most of a test suite's cost is paid *after* it is written — every run in CI, every false
alarm, every rewrite when the code changes. A suite that is fast, focused, and honest
lets a team change code fearlessly. A suite that is slow, coupled to internals, or flaky
does the opposite: it trains people to ignore failures, and a red build that everyone
ignores protects nothing. Getting the fundamentals right is what makes the difference
between tests that pay compound interest and tests that are technical debt.

## Core Principles

- **Test observable behavior, not implementation.** Assert on what a caller can see —
  return values, state changes, emitted events. A test that reaches into private state
  breaks on refactors that changed nothing a user cares about.
- **Follow the pyramid.** Many fast unit tests, fewer integration tests, very few E2E
  tests. Push each check to the lowest level that can catch the bug, because cost and
  flakiness rise sharply as you climb.
- **One reason to fail per test.** When a test fails you should know *what* broke without
  debugging. A test asserting five unrelated things hides which one regressed.
- **Deterministic or delete it.** A test that passes and fails on the same input teaches
  the team to ignore red. Non-determinism is a defect in the test.
- **The test must be able to fail.** If you cannot describe an implementation bug that
  would make it red, it asserts nothing.

## Best Practices

- Structure every test as **Arrange-Act-Assert**: set up state, perform the one
  action under test, assert the outcome. Keep the "Act" to a single call so the cause of
  a failure is unambiguous.
- Name tests for behavior, not method names: `rejects transfer when balance is
  insufficient`, not `test transfer 2`. The name is the spec.
- Make each test independent — no shared mutable state, no ordering dependency. Tests
  must pass when run alone, in parallel, and in random order.
- Prefer real objects over doubles until a dependency is slow, non-deterministic, or has
  side effects you cannot afford. Every double is a claim that may drift from reality.
- Assert on specific values, not just "no error." `expect(total).toBe(42)` catches bugs
  that `expect(fn).not.toThrow()` misses. See [assertions](09-assertions.md).
- Write the test you would trust to gate a deploy. If you would not, it is not done.

## Examples

**Good Example** — behavior-focused, one reason to fail, deterministic

```ts
// Tests the observable outcome (returned total), not how it is computed.
test("applies a 10% discount to orders over $100", () => {
  // Arrange: fixed inputs, no clock or network → deterministic.
  const order = { subtotal: 200, code: "SAVE10" };

  // Act: exactly one call under test.
  const total = priceOrder(order);

  // Assert: a specific expected value, so a wrong calc is caught.
  expect(total).toBe(180);
});
```

**Bad Example** — couples to internals, cannot meaningfully fail

```ts
test("priceOrder works", () => {
  const order = { subtotal: 200, code: "SAVE10" };
  const spy = jest.spyOn(order, "toString"); // asserting on an internal detail

  priceOrder(order);

  expect(spy).toHaveBeenCalled(); // passes even if the total is completely wrong
  expect(priceOrder).toBeDefined(); // asserts nothing about behavior
});
```

## Common Mistakes

- Asserting that a private method or dependency *was called* instead of that the result
  is correct — the test then breaks on refactors and misses real bugs.
- Writing E2E tests for logic a unit test could cover, making the suite slow and flaky.
- Sharing mutable state between tests, so they pass together but fail in isolation.
- Depending on `Date.now()`, random values, or network without control, producing
  intermittent failures.
- Tests with no failing path — `expect(true).toBe(true)`, or asserting a mock you set up.
- Naming tests after methods, so a failure name tells you nothing about what broke.

## Production Tips

- Run the suite in CI on every push; a test that does not gate merges rots.
- Randomize test order in CI to surface hidden inter-test dependencies early.
- Track suite runtime as a first-class metric — a slow suite gets skipped, and a skipped
  suite protects nothing.

## AI Review Checklist

- Does each test assert observable behavior, not implementation details?
- Is the test at the lowest level (unit > integration > E2E) that can catch the bug?
- Does each test have exactly one clear reason to fail?
- Is the test deterministic — free of real time, randomness, order, and network?
- Can you name a code bug that would make this test red? If not, it asserts nothing.
- Does the test name describe the behavior being verified?

## Related

- `knowledge/testing/00-overview.md`
- `knowledge/testing/02-unit-testing.md`
- `knowledge/testing/03-integration-testing.md`
- `knowledge/testing/09-assertions.md`
- `knowledge/testing/28-testing-strategy.md`
