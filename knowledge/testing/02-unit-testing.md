---
id: testing/02-unit-testing
topic: testing
slug: unit-testing
title: "Unit Testing"
type: doc
order: 2
status: ready
tags: [testing, unit-testing]
related: [testing/01-testing-fundamentals, testing/03-integration-testing, testing/05-test-doubles, testing/09-assertions, testing/10-fixtures]
when_to_use: "Read before writing or reviewing a test for a single function, class, or module."
---
# Unit Testing

## Purpose

This document defines how to test a single unit — a function, class, or small module — in
isolation from the rest of the system. Unit tests are the base of the pyramid: the fastest,
most numerous, most deterministic tests you own. It is written so an agent can write unit
tests that pin down behavior without becoming brittle.

A "unit" is the smallest piece of code with meaningful behavior worth verifying on its own.
Isolation means the test exercises *that* logic, not the database, network, or clock.

## Why It Matters

Unit tests are where a bug is cheapest to find and fix — milliseconds after you wrote it,
with a stack trace pointing at the exact line. Push a check up to integration or E2E and
the same bug costs seconds to minutes to reproduce, and the failure points at a symptom,
not a cause. A strong unit layer is what lets the higher, slower layers stay small. But
unit tests are also the easiest to write badly: over-mock and they test the mocks; couple
to internals and they break on every refactor. The value is entirely in the discipline.

## Core Principles

- **One unit, one behavior per test.** Isolate the logic under test and assert a single
  observable outcome, so a failure names the exact broken behavior.
- **Prefer pure logic.** Code with no side effects is trivially testable — no setup, no
  doubles, no cleanup. Push I/O to the edges and keep the core pure.
- **Mock only what you must.** Replace a collaborator only when it is slow,
  non-deterministic, or has real side effects. Every double is a claim that can drift.
- **Test the contract, not the code path.** Assert what the caller relies on; do not
  assert *how* the unit computes it.
- **Cover the edges.** The interesting bugs live at boundaries: empty input, zero, one,
  many, null, max, and the error paths — not the happy path.

## Best Practices

- Keep unit tests **fast** (single-digit milliseconds) and **hermetic** — no filesystem,
  network, real clock, or shared database. If you need those, it is an integration test.
- Inject dependencies (clock, id generator, repository) so the test can supply
  deterministic doubles. Hard-coded `new Date()` or `Math.random()` inside the unit makes
  it untestable — see [test doubles](05-test-doubles.md).
- Use a table/parametrized test for many input→output cases instead of copy-pasting.
- Assert specific expected values, not just types or truthiness. See
  [assertions](09-assertions.md).
- Test error and boundary paths explicitly — the code that only runs when something goes
  wrong is exactly the code no one exercises by hand.
- Do not test third-party libraries or the language. Test *your* logic.

## Examples

**Good Example** — pure logic, injected clock, boundary covered

```ts
// The clock is a parameter, so the test is deterministic without mocking globals.
function isExpired(token: { expiresAt: number }, now: number): boolean {
  return token.expiresAt <= now;
}

test.each([
  [1000, 999, false], // not yet expired
  [1000, 1000, true],  // boundary: equal counts as expired
  [1000, 1001, true],  // expired
])("isExpired(exp=%i, now=%i) → %s", (expiresAt, now, expected) => {
  expect(isExpired({ expiresAt }, now)).toBe(expected);
});
```

**Bad Example** — hidden clock, over-mocked, asserts the mock

```ts
function isExpired(token: { expiresAt: number }): boolean {
  return token.expiresAt <= Date.now(); // untestable: real clock baked in
}

test("isExpired", () => {
  const spy = jest.spyOn(Date, "now").mockReturnValue(1000); // mocking a global
  isExpired({ expiresAt: 500 });
  expect(spy).toHaveBeenCalled(); // asserts the mock ran, not that the result is right
});
```

## Common Mistakes

- Baking `Date.now()`, `Math.random()`, or `fetch` into the unit, forcing global mocks
  and making the test fragile — inject them instead.
- Mocking everything until the test only verifies that the mocks were called, catching no
  real bug.
- Testing only the happy path and skipping the error and boundary cases where bugs hide.
- Asserting on private fields or call order, so a behavior-preserving refactor turns the
  suite red.
- Writing a "unit" test that hits a real database or network — that is an
  [integration test](03-integration-testing.md) wearing the wrong label.
- Chasing 100% line coverage with tests that assert nothing meaningful.

## Production Tips

- Run unit tests on every save locally and on every push in CI; they are cheap enough to
  gate every change.
- Keep the unit suite under a few seconds total by staying hermetic — slowness always
  traces back to hidden I/O.
- When a bug escapes to production, write the failing unit test first, then fix it. The
  test proves the fix and guards the regression.

## AI Review Checklist

- Is the unit tested in isolation, with no real I/O, network, or clock?
- Are dependencies injected so the test is deterministic without mocking globals?
- Does each test assert a specific observable outcome, not that a mock was called?
- Are boundary and error paths covered, not just the happy path?
- Would this test survive a refactor that preserves behavior?
- Is anything here actually an integration test mislabeled as a unit test?

## Related

- `knowledge/testing/01-testing-fundamentals.md`
- `knowledge/testing/03-integration-testing.md`
- `knowledge/testing/05-test-doubles.md`
- `knowledge/testing/09-assertions.md`
- `knowledge/testing/10-fixtures.md`
