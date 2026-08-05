---
id: devops/22-testing
topic: devops
slug: testing
title: "DevOps Testing"
type: doc
order: 22
status: ready
tags: [devops, testing]
related: [devops/23-quality-gates, devops/05-build-pipelines, devops/07-deployment-strategies, devops/21-performance, devops/16-security]
when_to_use: "Read before writing a test suite or CI test stage, or reviewing test coverage for a change."
---
# DevOps Testing

## Purpose

This document defines how to test software in a DevOps pipeline so that a green build
actually means "safe to deploy." It covers what to test at each level, how to keep tests
fast and reliable, and how to wire them into CI. It is written so an agent can build or
review a test suite that catches real regressions without becoming slow, flaky, or
theater.

Testing is the evidence layer of the pipeline. It feeds [quality gates](23-quality-gates.md)
(which decide pass/fail) and underpins safe [deployment strategies](07-deployment-strategies.md).
The goal is not coverage numbers; it is confidence that changes are correct.

## Why It Matters

Tests are the only thing that lets you ship fast without shipping bugs. A trustworthy
suite turns "hope it works" into a signal you can automate a deploy on. But the value is
entirely in the suite's *trust*: a flaky test that fails randomly gets ignored, and once
one red build is ignored, all of them are — the suite dies as a signal. Likewise tests
that assert nothing real (or only mocks) give false confidence, which is worse than no
tests because it hides risk behind a green check.

## Core Principles

- **Test behavior, not implementation.** Assert on observable outputs and side effects, so
  refactors that keep behavior don't break tests. Tests coupled to internals punish good
  refactoring and rot fast.
- **Shape the suite like a pyramid.** Many fast unit tests, fewer integration tests, a thin
  layer of end-to-end tests. Inverting it (mostly E2E) gives a slow, flaky suite.
- **Every test must be deterministic.** Same input, same result, every run. No real clocks,
  network, ordering, or shared state. Flaky tests destroy trust in the whole suite.
- **A test must be able to fail.** If it passes when the feature is broken, it tests
  nothing. Write the failing test first, or break the code to confirm it goes red.
- **Fast feedback beats exhaustive.** Unit tests in seconds, full CI in minutes. Slow suites
  get skipped, and skipped tests are no tests.

## Best Practices

- **Isolate unit tests** from I/O (DB, network, filesystem, clock). Inject dependencies so
  they run in-memory and in parallel. The cost is some test doubles — worth it for speed.
- **Use real dependencies in integration tests** via ephemeral containers (Testcontainers)
  rather than mocking the database. Mocked-DB tests pass while real SQL is wrong.
- **Keep E2E thin and targeted** at critical user journeys (login, checkout). They are slow
  and fragile; use them to cover integration seams, not business-logic permutations.
- **Make tests hermetic and parallel-safe**: each test creates and tears down its own data,
  assumes no order, and shares no mutable global state.
- **Assert on outcomes, and test the failure paths** (errors, timeouts, invalid input) —
  bugs live in the unhappy paths that happy-path tests never exercise.
- **Fix or delete flaky tests immediately.** Quarantine, root-cause, repair. A tolerated
  flake trains the team to ignore red.
- **Gate CI on the suite** and track coverage as a floor on critical modules, not a vanity
  target — 100% coverage of trivial getters proves nothing.
- **Control fixed inputs**: inject time, seed randomness, and freeze external responses so
  results are reproducible.

## Examples

**Good Example** — deterministic, behavior-focused, real dependency where it matters

```ts
// Time is injected → deterministic; asserts observable BEHAVIOR, not internals.
test("order older than 30 days is archivable", () => {
  const clock = () => new Date("2026-07-07T00:00:00Z"); // fixed clock, no real Date.now()
  const order = { createdAt: "2026-05-01T00:00:00Z" };
  expect(isArchivable(order, clock())).toBe(true);       // one clear outcome assertion
});

// Integration test runs against a REAL Postgres in an ephemeral container.
test("repository persists and reloads an order", async () => {
  const db = await startPostgresContainer();  // real SQL, real constraints, torn down after
  const repo = new OrderRepo(db);
  const saved = await repo.save({ total: 100 });
  expect(await repo.findById(saved.id)).toMatchObject({ total: 100 });
});
```

**Bad Example** — non-deterministic and asserting nothing real

```ts
test("archives old orders", async () => {
  const order = { createdAt: Date.now() - 40 * 864e5 }; // real clock → time-dependent
  await service.archive(order);
  expect(service.archive).toHaveBeenCalled();  // asserts the mock ran, not that it WORKED
                                               // passes even if archiving is completely broken
});
// Hits the live staging API over the network → flaky, order-dependent, slow.
```

## Common Mistakes

- Asserting on mocks/spies instead of real outcomes — green but meaningless.
- Time/network/ordering dependence causing intermittent, ignored failures.
- An inverted pyramid: mostly slow E2E tests, so CI is slow and flaky.
- Mocking the database, so tests pass while the actual SQL/migrations are wrong.
- Chasing a coverage percentage by testing trivial code, ignoring the risky paths.
- Testing only happy paths; the error and edge cases where bugs live go uncovered.
- Tolerating "known flaky" tests until the whole suite is treated as noise.

## Production Tips

- Track and publish **flake rate** and **suite duration**; both are reliability metrics that
  decay silently. Budget time to keep them healthy.
- Run the **fast subset on every push** and the full suite (incl. E2E) pre-merge, so
  developers get seconds-fast feedback without losing coverage at the gate.
- Add a **regression test with every bug fix** — reproduce the bug as a failing test first,
  then fix it, so it can never silently return.

## AI Review Checklist

- Do tests assert on observable behavior/outcomes, not on mocks or internals?
- Is every test deterministic (injected clock, seeded randomness, no shared state)?
- Does the suite follow the pyramid (many unit, fewer integration, thin E2E)?
- Do integration tests use real dependencies (ephemeral containers), not mocked DBs?
- Are failure paths and edge cases tested, not just the happy path?
- Are flaky tests fixed or quarantined rather than tolerated?
- Does each bug fix ship with a regression test that fails without the fix?

## Related

- `knowledge/devops/23-quality-gates.md`
- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/07-deployment-strategies.md`
- `knowledge/devops/21-performance.md`
- `knowledge/devops/16-security.md`
