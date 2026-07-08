---
id: nodejs/21-testing
topic: nodejs
slug: testing
title: "Testing"
type: doc
order: 21
status: ready
tags: [nodejs, testing]
related: [nodejs/16-error-handling, nodejs/22-debugging, nodejs/28-best-practices, nodejs/29-tooling, nodejs/15-configuration]
when_to_use: "Read before writing or reviewing tests for a Node.js codebase, or when choosing a test strategy."
---
# Testing

## Purpose

This document defines how to test Node.js code so the suite actually protects
against regressions instead of merely existing. It covers the built-in
`node:test` runner, what to test at each level (unit, integration, end-to-end),
how to handle async and time, and how to isolate the code under test from the
network, clock, and filesystem without over-mocking it into meaninglessness.

## Why It Matters

Tests are the executable contract that lets an agent change code safely. A suite
that is flaky, slow, or coupled to implementation details is worse than none: it
either blocks every PR with false failures or gives false confidence while missing
real bugs. In Node specifically, async control flow and shared module state make it
easy to write tests that pass by accident — an unawaited promise whose assertion
never runs looks green. The value of a test is entirely in whether it fails when the
behavior breaks.

## Core Principles

- **Test behavior, not implementation.** Assert on observable outputs and effects, not
  internal calls. Tests coupled to internals break on every refactor and protect nothing.
- **Isolate the unit from the world.** Stub the network, clock, and randomness so a
  test is deterministic and fast. Non-determinism is the root of flakiness.
- **Prefer the smallest test that gives confidence.** Unit tests for logic, a few
  integration tests for wiring, minimal E2E for critical paths. Invert the pyramid at your peril.
- **Every async path must be awaited and asserted.** An assertion behind an unawaited
  promise is dead code that always passes. Return or await every promise in a test.
- **A test must be able to fail.** If you cannot describe the change that turns it red,
  it is documentation, not a test.

## Best Practices

- Use the built-in `node:test` runner with `node --test` — no dependency, native
  coverage (`--experimental-test-coverage`), watch mode, and TAP output. Reach for
  Vitest/Jest only when you need their specific ecosystem features.
- Control time with fake timers (`node:test` `t.mock.timers` or `@sinonjs/fake-timers`)
  instead of real `setTimeout`. Real sleeps make suites slow and flaky.
- Inject dependencies (clients, clocks, config) as parameters so tests can substitute
  fakes. Hard-coded `import` of a live client is untestable without global mocking.
- Test error and edge paths explicitly: rejected promises, invalid input, timeouts,
  empty results. Bugs live at the boundaries, not the happy path.
- Keep each test independent — no shared mutable state, no ordering dependency. Reset
  state in `beforeEach`. Order-dependent tests fail mysteriously in parallel.
- Assert on rejected promises with `assert.rejects`, not a `try/catch` that silently
  passes when no error is thrown.
- Run tests in CI on every PR and gate merge on them; track coverage as a signal, not a target.

## Examples

**Good Example** — deterministic, async-aware, injected dependency

```js
import { test, mock } from "node:test";
import assert from "node:assert/strict";
import { chargeCard } from "./billing.js";

test("retries once then throws on repeated gateway failure", async () => {
  // inject a fake gateway: no network, fully deterministic
  const gateway = { charge: mock.fn(async () => { throw new Error("503"); }) };

  // assert on the rejection explicitly — the await guarantees it actually ran
  await assert.rejects(() => chargeCard(gateway, { amount: 100 }), /503/);
  assert.equal(gateway.charge.mock.callCount(), 2); // retried exactly once
});
```

**Bad Example** — hits the network, unawaited assertion, no failure mode

```js
import { test } from "node:test";
import { chargeCard } from "./billing.js";

test("charges a card", () => {
  // real network call: slow, flaky, non-deterministic, may charge real money
  chargeCard(liveStripe, { amount: 100 }).then((r) => {
    assert.ok(r.ok); // not awaited/returned → if it rejects, the test still passes
  });
});
```

## Common Mistakes

- Forgetting to `await`/`return` a promise, so the assertion never runs and the test always passes.
- Mocking so much that the test only verifies the mocks, not real behavior.
- Real network, clock, or filesystem access, producing slow and flaky suites.
- Asserting on internal method calls, so every refactor breaks green tests.
- Shared mutable state between tests, causing order-dependent failures under parallelism.
- Testing only the happy path; leaving error handling and edge cases unverified.
- Chasing a coverage percentage with assertion-free tests that execute lines but check nothing.

## Production Tips

- Split fast unit tests (run on every save/PR) from slow integration/E2E (run pre-merge)
  so feedback stays quick. Tag with `--test-name-pattern` or separate directories.
- Use test containers (`testcontainers`) for integration against real Postgres/Redis
  rather than mocks, so wiring bugs surface before production.
- Quarantine and fix flaky tests immediately; a tolerated flake trains the team to ignore red.
- Seed randomness and freeze time in CI so failures are reproducible from the logs.

## AI Review Checklist

- Is every async operation in a test awaited or returned so its assertions run?
- Are network, clock, and randomness stubbed so the test is deterministic?
- Does each test assert observable behavior, not internal implementation calls?
- Are error, timeout, and edge-case paths tested, not just the happy path?
- Are tests independent of order and shared mutable state?
- Can you name the code change each test would catch (i.e. can it fail)?
- Is the suite wired into CI as a merge gate?

## Related

- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/22-debugging.md`
- `knowledge/nodejs/28-best-practices.md`
- `knowledge/nodejs/29-tooling.md`
- `knowledge/nodejs/15-configuration.md`
