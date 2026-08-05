---
id: javascript/24-testing
topic: javascript
slug: testing
title: "JavaScript Testing"
type: doc
order: 24
status: ready
tags: [javascript, testing, fetchUser, spyOn, beforeEach, NotFoundError, restoreAllMocks, boundary]
related: [javascript/14-error-handling, javascript/08-asynchronous-javascript, javascript/23-clean-code, javascript/28-best-practices, javascript/29-tooling]
when_to_use: "Read before writing, reviewing, or restructuring any JavaScript test suite."
---
# JavaScript Testing

## Purpose

This document defines how to test JavaScript code so tests catch real defects,
stay fast, and do not rot. It covers what to test, how to structure a test, how to
handle asynchronous code and time, and where the boundaries between unit,
integration, and end-to-end tests belong. It is written so an agent can write or
review a test suite without producing brittle, false-confidence tests.

A passing suite is not the goal. A suite that *fails when the code is wrong and only
then* is the goal. Everything below serves that.

## Why It Matters

Tests are the executable specification of a system. When they are good, they let you
refactor fearlessly and catch regressions before users do. When they are bad — coupled
to implementation details, flaky, or asserting nothing meaningful — they cost more than
they save: engineers stop trusting red, disable "annoying" tests, and ship the bug the
suite was supposed to catch. A test you cannot trust is worse than no test, because it
manufactures false confidence.

## Core Principles

- **Test behavior, not implementation.** Assert on observable outputs and side effects,
  not on private methods or internal call counts. Internals change; behavior is the
  contract. The cost of over-coupling is a suite that breaks on every refactor.
- **One reason to fail per test.** Each test names one behavior. When it goes red, the
  name should tell you what broke without reading the body.
- **Deterministic or delete it.** A test that passes and fails on the same code is
  noise. Control time, randomness, network, and ordering — never depend on them.
- **Arrange–Act–Assert.** Set up state, perform one action, assert the result. Keep the
  three phases visually distinct.
- **Fast feedback dominates.** Prefer many fast unit tests, fewer integration tests,
  and a thin layer of end-to-end tests (the testing pyramid). Slow suites get skipped.

## Best Practices

- Use a modern runner — **Vitest** or **Jest** for units, **Playwright** for E2E. Node's
  built-in `node:test` is fine for zero-dependency libraries.
- Name tests as behavior: `it("returns 401 when the token is expired")`, not
  `it("test token")`.
- Assert on real values. `expect(result).toEqual({ id: 1 })` beats `expect(result).toBeTruthy()`,
  which passes for almost anything.
- Mock only what you own and what crosses a real boundary (network, clock, filesystem).
  Over-mocking tests the mocks, not the code.
- Use fake timers (`vi.useFakeTimers()`) for `setTimeout`/`setInterval`/`Date` instead
  of real waits. Real waits are slow and flaky.
- `await` every async assertion and reject-path. Un-awaited promises pass silently even
  when the assertion fails.
- Keep tests isolated: reset mocks and shared state between tests (`beforeEach`). Never
  let test order matter.
- Cover the unhappy paths — errors, empty inputs, boundaries — not just the golden path.

## Examples

**Good Example** — behavior-focused, deterministic, awaits rejection

```js
import { describe, it, expect, vi, beforeEach } from "vitest";
import { fetchUser } from "./user.js";

describe("fetchUser", () => {
  beforeEach(() => vi.restoreAllMocks()); // isolate: no state leaks between tests

  it("throws NotFoundError when the API returns 404", async () => {
    // Mock the boundary (network), not fetchUser's internals.
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(null, { status: 404 })
    );

    // Assert on observable behavior: the rejection. `await expect` is required —
    // without it the assertion resolves after the test ends and never fails.
    await expect(fetchUser("42")).rejects.toThrow("NotFoundError");
  });
});
```

**Bad Example** — couples to internals, un-awaited, asserts nothing

```js
it("works", () => {
  const spy = vi.spyOn(user, "_parseResponse"); // tests a private method — breaks on refactor
  fetchUser("42");                               // not awaited: rejection is swallowed
  expect(spy).toHaveBeenCalled();                // asserts a call happened, not a result
  expect(fetchUser("42")).toBeTruthy();          // a pending Promise is always truthy → always passes
});
```

## Common Mistakes

- Not awaiting async assertions, so failures pass silently.
- Asserting `toBeTruthy()`/`toBeDefined()` where the real value should be checked.
- Mocking the unit under test's own internals, coupling the test to implementation.
- Real `setTimeout` or network calls, making the suite slow and flaky.
- Shared mutable state across tests, so order determines pass/fail.
- Chasing 100% coverage with tests that execute lines but assert nothing meaningful.
- Snapshot tests over large objects that everyone blindly re-approves on failure.

## Production Tips

- Run tests in CI on every push; fail the build on any red. Track flaky tests and quarantine
  them explicitly rather than retrying blindly.
- Measure coverage as a signal, not a target — 80% with strong assertions beats 100% of
  hollow tests. Gate on *uncovered critical paths*, not a global percentage.
- Seed randomness and pin the timezone (`TZ=UTC`) in CI so results are reproducible.

## AI Review Checklist

- Does each test assert on observable behavior, not private methods or call counts?
- Is every async path `await`ed, including rejection assertions?
- Are timers, dates, and randomness controlled rather than real?
- Is shared state reset between tests so order does not matter?
- Do tests cover error and boundary cases, not only the happy path?
- Does each failing test name tell you what broke without reading the body?
- Are mocks limited to real boundaries (network, clock, filesystem)?

## Related

- `knowledge/javascript/14-error-handling.md`
- `knowledge/javascript/08-asynchronous-javascript.md`
- `knowledge/javascript/23-clean-code.md`
- `knowledge/javascript/28-best-practices.md`
- `knowledge/javascript/29-tooling.md`
