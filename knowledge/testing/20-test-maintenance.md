---
id: testing/20-test-maintenance
topic: testing
slug: test-maintenance
title: "Test Maintenance"
type: doc
order: 20
status: ready
tags: [testing, test-maintenance]
related: [testing/08-test-organization, testing/06-mocking, testing/22-flaky-tests, testing/24-best-practices, testing/29-test-review]
when_to_use: "Read before refactoring a test suite, deleting a test, or when tests break on every unrelated change."
---
# Test Maintenance

## Purpose

This document defines how to keep a test suite valuable over years: tests that
fail only for real regressions, are cheap to update when requirements change, and
never rot into a suite everyone ignores. It is written so an agent can refactor,
prune, and structure tests to minimize long-term maintenance cost.

A test suite is code with a support cost. The goal is a **high signal-to-noise
ratio**: every failure means something is broken, and legitimate refactors do not
cascade into hundreds of unrelated red tests.

## Why It Matters

Tests are written once and maintained forever. A suite that breaks on every
internal refactor teaches the team a fatal lesson: failures are noise. Once that
happens, red builds get rubber-stamped, `.skip` proliferates, and the safety net
quietly disappears while the numbers still look healthy. The cost of a brittle
test is not the one time you write it — it is every future change that must
detour to fix tests that were coupled to implementation, not behavior. Maintainable
tests are what keep a codebase changeable a year from now.

## Core Principles

- **Test behavior, not implementation.** Assert on observable outputs and public
  contracts. A test coupled to private methods, internal call order, or DOM
  structure breaks on refactors that changed nothing a user can see.
- **DRY the setup, DAMP the assertions.** Factor repeated arrangement into
  builders and fixtures, but keep each test's intent readable in-line. A test you
  cannot understand without chasing five helpers is unmaintainable.
- **A test that never fails is dead weight; a test that fails randomly is worse.**
  Prune tests that assert nothing meaningful, and fix or delete
  [flaky ones](22-flaky-tests.md) immediately — they poison trust in the whole suite.
- **Delete fearlessly when behavior is gone.** When a feature is removed, its
  tests go with it. Keeping "just in case" tests around obsolete code is debt.
- **Minimize mocking of internal code.** Every mock is a copy of an assumption
  that silently drifts from reality. Prefer real collaborators; mock only slow or
  external boundaries.

## Best Practices

- Extract test data into **builders/factories** with sensible defaults so a
  requirement change updates one factory, not fifty tests.
- Query the UI by role, label, or text — never by CSS class or deep selectors —
  so restyling does not break tests. Mirror the [accessibility](18-accessibility-testing.md) contract.
- Keep one logical assertion per test and a descriptive name that states the
  behavior; when it fails, the name alone should explain what broke.
- When a refactor breaks many tests at once, treat it as a signal: the tests were
  coupled to structure. Fix the coupling, do not just re-record snapshots.
- Review and prune **snapshot tests** regularly; a giant auto-updated snapshot
  asserts everything and therefore nothing. Snapshot small, intentional output.
- Co-locate tests with the code they cover and name them consistently so the
  suite is navigable and dead tests are easy to spot.
- Run the suite fast (parallelize, shard) so maintenance stays cheap — a slow
  suite is one people avoid running, which lets rot accumulate.

## Examples

**Good Example** — behavior-focused, builder-backed, refactor-resilient

```ts
// One shared builder; each test overrides only what it cares about.
const anOrder = (overrides = {}) => ({ items: [item()], coupon: null, ...overrides });

test("free shipping applies over the threshold", () => {
  const order = anOrder({ items: [item({ price: 60 }), item({ price: 60 })] });

  // Asserts the *outcome* (shipping cost), not which internal function computed it.
  expect(checkout(order).shipping).toBe(0);
});

test("standard shipping applies under the threshold", () => {
  const order = anOrder({ items: [item({ price: 10 })] });
  expect(checkout(order).shipping).toBe(5); // survives any internal refactor
});
```

**Bad Example** — coupled to internals; every refactor breaks it

```ts
test("checkout", () => {
  const svc = new CheckoutService();
  const spy = jest.spyOn(svc as any, "_calcShipping"); // asserts a private method exists
  svc.process({ items: [{ price: 60 }, { price: 60 }] });

  // Breaks if the private method is renamed, inlined, or called a different number
  // of times — none of which changes behavior. This is maintenance debt by design.
  expect(spy).toHaveBeenCalledTimes(1);
  expect((svc as any)._state).toEqual({ shipping: 0 }); // reaching into internals
});
```

## Common Mistakes

- Asserting on private methods, call counts, or internal state, so refactors that
  preserve behavior turn the suite red.
- Selecting DOM by CSS class or nth-child, coupling tests to styling.
- Over-mocking internal collaborators until tests verify the mocks, not the code.
- Giant snapshot tests that get blindly `--updated` on every failure, asserting
  nothing.
- Keeping skipped or always-passing tests around instead of deleting them,
  hiding coverage gaps behind green.
- Duplicating setup across dozens of tests so a single requirement change forces
  a sweeping, error-prone edit.

## Production Tips

- Track and burn down `.skip`/`.only`/`xit` in CI — fail the build on a stray
  `.only`, and require a linked ticket for every skipped test.
- When deleting a feature, delete its tests in the same PR; leaving them causes
  confusing failures against code that no longer exists.
- Periodically audit the slowest and most-frequently-edited test files — they are
  the maintenance hotspots and usually reveal a coupling or fixture problem.

## AI Review Checklist

- Do the tests assert observable behavior rather than private methods, call
  order, or internal state?
- Is repeated setup factored into builders/fixtures while assertions stay readable
  in-line?
- Are UI elements queried by role/label/text instead of CSS class?
- Are snapshots small and intentional, not blanket auto-updated blobs?
- Are skipped, `.only`, and always-passing tests removed or ticketed?
- When a feature is deleted, are its tests deleted in the same change?

## Related

- `knowledge/testing/08-test-organization.md`
- `knowledge/testing/06-mocking.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/24-best-practices.md`
- `knowledge/testing/29-test-review.md`
