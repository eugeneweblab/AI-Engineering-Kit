---
id: backend/23-testing
topic: backend
slug: testing
title: "Backend Testing"
type: doc
order: 23
status: ready
tags: [backend, testing, placeOrder, toBe, toBeGreaterThan, toHaveBeenCalled, level, suite, test]
related: [backend/07-business-logic, backend/12-error-handling, backend/17-transactions, backend/09-validation, backend/21-security]
when_to_use: "Read before writing tests for backend code, reviewing a test suite, or deciding what to test at which level."
---
# Backend Testing

## Purpose

This document defines how to test backend code so the suite actually protects against
regressions: what to test at which level, how to make tests deterministic, and what makes a
test worth keeping. It is written so an agent writes tests that catch real bugs and give a
green build genuine meaning, rather than tests that merely pass.

A test suite is an executable specification of intended behavior and a safety net for
change. Its value is not coverage percentage; it is the confidence that a passing build is
actually shippable. A suite that is slow, flaky, or asserts the wrong things erodes that
confidence until the team ignores it.

## Why It Matters

Backend code encodes the rules that move money, grant access, and mutate the source of
truth — exactly the code where a silent regression is most expensive and least visible. The
suite is what lets you change that code without fear; without it, every refactor is a gamble
and velocity collapses under the weight of manual verification. But tests are code too: a
flaky or tautological test is worse than none, because it trains the team to distrust red
and merge through it. The goal is a fast, deterministic suite that fails only for real bugs.

## Core Principles

- **Test behavior, not implementation.** Assert on observable outputs and effects, so a
  refactor that preserves behavior keeps the tests green. Tests coupled to internal calls
  break on every change and protect nothing.
- **Follow the test pyramid.** Many fast unit tests over pure logic, fewer integration tests
  over real collaborators (database, HTTP), very few end-to-end tests. Inverting it yields a
  slow, brittle suite.
- **Determinism is non-negotiable.** A test must pass or fail the same way every run. Control
  time, randomness, and ordering; a flaky test is a broken test.
- **Test the edges and the failures.** Empty, boundary, duplicate, concurrent, and error
  inputs are where bugs live. The happy path rarely breaks in production.
- **Each test states one behavior and is independent.** Given clear inputs, assert one
  outcome; no shared mutable state or ordering between tests.

## Best Practices

- Unit-test pure business logic and validation with no I/O; these are fast and can exhaustively
  cover branches and edge cases. Push logic out of I/O layers so it is unit-testable.
- Integration-test against a real database (a container or throwaway schema), not a mock. Mocks
  of your own database hide the bugs — wrong SQL, constraint violations — that matter most.
- Reserve end-to-end tests for a few critical user journeys; they are slow and flaky, so keep
  them scarce and high-value.
- Make each test set up its own data and clean up (transaction rollback or truncate) so tests
  are isolated and can run in parallel and any order.
- Inject clock and randomness so time- and random-dependent code is deterministic under test.
- Assert on the failure paths: rejected input, thrown errors, denied authorization, rolled-back
  transactions — the behavior your production incidents actually exercise.
- Only mock at true external boundaries (third-party APIs, email/SMS providers), and assert on
  the resulting behavior, not that a mock was called a certain way.
- Name tests by the behavior they pin (`rejects_order_when_stock_insufficient`) so a failure
  names the broken rule.

## Examples

**Good Example** — behavioral, edge case, deterministic

```ts
it("rejects an order when stock is insufficient", async () => {
  await seed({ sku: "A1", quantity: 1 });        // explicit, self-contained setup

  const result = await placeOrder({ sku: "A1", amount: 5 });

  // Assert the observable outcome, not which internal methods ran.
  expect(result.status).toBe("rejected");
  expect(await stockOf("A1")).toBe(1);            // side effect verified: stock unchanged
});
```

**Bad Example** — tests implementation, non-deterministic, no assertion of effect

```ts
it("places an order", async () => {
  const repo = { save: jest.fn() };               // mocks the DB: never runs real SQL
  await placeOrder({ sku: "A1", amount: 5 }, repo);

  expect(repo.save).toHaveBeenCalled();           // asserts a call, not a result — passes even if wrong
  expect(Date.now()).toBeGreaterThan(0);          // tautology; and time is uncontrolled elsewhere
});
```

## Common Mistakes

- Asserting that internal methods were called instead of asserting on the resulting behavior.
- Mocking your own database, so wrong queries and constraint violations pass the suite.
- Flaky tests from real time, randomness, network, or inter-test ordering — then retried until green.
- Only testing the happy path; empty, boundary, and error inputs go uncovered.
- Chasing a coverage number with tests that execute lines but assert nothing meaningful.
- Shared mutable fixtures that make tests pass or fail depending on run order.
- A slow suite nobody runs locally, so it stops gating anything.

## Production Tips

- Run the full suite in CI on every push and block merges on red; a suite that does not gate
  merges provides no protection.
- Add a regression test that reproduces each production bug before fixing it, so it can never
  return silently.
- Track and fix flaky tests immediately; quarantining and ignoring them normalizes a red build.
- Keep the unit suite fast (seconds) so developers run it constantly; put slow tests behind a
  separate CI stage.

## AI Review Checklist

- Do tests assert on observable behavior and effects, not on internal call sequences?
- Does the suite follow the pyramid: many unit, fewer integration, minimal e2e?
- Do integration tests hit a real database rather than a mock of it?
- Are time, randomness, and ordering controlled so tests are deterministic?
- Are edge cases and failure paths (errors, rejections, rollbacks) tested, not just the happy path?
- Is each test independent, with its own setup/teardown and no shared mutable state?
- Does every fixed production bug have a regression test locking it down?

## Related

- `knowledge/backend/07-business-logic.md`
- `knowledge/backend/12-error-handling.md`
- `knowledge/backend/17-transactions.md`
- `knowledge/backend/09-validation.md`
- `knowledge/backend/21-security.md`
