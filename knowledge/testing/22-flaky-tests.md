---
id: testing/22-flaky-tests
topic: testing
slug: flaky-tests
title: "Flaky Tests"
type: doc
order: 22
status: ready
tags: [testing, flaky-tests]
related: [testing/21-cicd, testing/23-debugging-tests, testing/04-e2e-testing, testing/20-test-maintenance, testing/06-mocking]
when_to_use: "Read before writing async or E2E tests, or when a test passes and fails on the same code."
---
# Flaky Tests

## Purpose

This document defines what makes a test flaky, how to eliminate the root causes,
and how to contain flakiness so it never erodes trust in the suite. A flaky test
is one that passes and fails on the *same* code without any change — the single
most corrosive failure mode a test suite can have. It is written so an agent can
write deterministic tests and diagnose non-determinism when it appears.

The goal is a suite where a red result is always a real regression. Flakiness
attacks that guarantee directly: it teaches the team that failures are noise.

## Why It Matters

One flaky test that fails 5% of the time will fail on roughly one in four
ten-test PRs. Developers learn to hit "re-run," and once re-running is normal, the
suite has stopped being a gate — a genuine regression now hides among the noise
and gets re-run into green like everything else. Flakiness does not just waste CI
minutes; it destroys the *trust* that gives tests their value. A suite the team
does not trust is a suite the team ignores. This is why flaky tests are treated as
build-breaking defects, not minor annoyances.

## Core Principles

- **Flakiness is a defect, not bad luck.** Every intermittent failure has a
  deterministic cause: timing, ordering, shared state, or an external dependency.
  "It's just flaky" is an unfinished diagnosis.
- **Never sleep; wait for a condition.** Fixed `sleep(500)` is the number-one
  cause of flakiness — too short and it fails under load, too long and it wastes
  time. Poll or await the actual state you need.
- **Tests must be order-independent and isolated.** Any test that depends on
  another test running first, or on leftover state, will fail when the runner
  parallelizes or reorders. Each test sets up and tears down its own world.
- **Retries hide, they do not fix.** Auto-retrying a flaky test converts a visible
  problem into an invisible one. Use retries only as temporary quarantine with a
  tracking ticket, never as the cure.
- **Control every non-deterministic input.** Time, randomness, network, and
  concurrency must be pinned or stubbed. Real clocks and real networks are flaky
  by nature.

## Best Practices

- Replace `sleep` with explicit waits on the observable condition (`waitFor`,
  `expect(locator).toBeVisible()`, polling assertions with a timeout). Assert the
  end state, not a duration.
- Freeze time (`vi.useFakeTimers`, `jest.useFakeTimers`, or a clock port) and
  seed randomness so date- and random-dependent tests are reproducible.
- Isolate state: fresh database transaction/schema per test (roll back after),
  unique fixture ids, and no reliance on execution order.
- Stub external services with a mock server or contract stub; never hit a live
  third-party API in a functional test — it is the classic source of "fails at 2am."
- Run the suite in **random order** and in **parallel** in CI to surface hidden
  ordering and shared-state coupling early.
- When a test flakes, reproduce it deterministically first (loop it 100×, disable
  isolation, run under load) — then fix the root cause, do not just add a wait.
- Quarantine a genuinely flaky test out of the required lane immediately, with an
  auto-filed ticket, so it stops blocking merges while it is being fixed.

## Examples

**Good Example** — waits on the condition, controls time, self-contained

```tsx
test("shows the order confirmation after submit", async () => {
  vi.useFakeTimers();                 // deterministic time — no wall-clock races
  const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
  render(<Checkout order={anOrder()} />);

  await user.click(screen.getByRole("button", { name: /place order/i }));

  // Waits for the actual end state with a bounded timeout — passes under any load,
  // never sooner or later than the real condition allows.
  expect(await screen.findByRole("status", { name: /confirmed/i })).toBeVisible();
});
```

**Bad Example** — sleeps, real clock, depends on prior test's state

```ts
let cart; // shared across tests → order-dependent and parallel-hostile

test("adds an item", async () => {
  cart = await addItem(realApi, "sku-1"); // real network call — flaky by nature
});

test("checks out", async () => {
  await checkout(cart);                    // fails if "adds an item" didn't run first
  await new Promise(r => setTimeout(r, 500)); // arbitrary sleep: too short under load
  expect(document.querySelector(".confirmed")).toBeTruthy(); // races the render
});
```

## Common Mistakes

- Using `sleep`/`setTimeout` to "wait for" async work instead of awaiting the
  actual condition.
- Sharing mutable state (module variables, a seeded row, a logged-in session)
  between tests, creating order dependence.
- Depending on real time or `Math.random` without freezing/seeding them.
- Calling live external services, whose latency and downtime leak into the suite.
- Adding an auto-retry and closing the ticket — the flake is now hidden, not fixed.
- Running tests only in a fixed order locally, so parallel CI surfaces failures the
  author never saw.

## Production Tips

- Track a per-test flake rate (failures on unchanged code) and alert when a test
  crosses a threshold — data beats anecdote for prioritizing fixes.
- Keep a quarantine lane that runs flaky tests non-blocking, and enforce that
  every quarantined test has an owner and an expiry; quarantine is a hospital, not
  a graveyard.
- Reproduce intermittent failures by running the single test in a tight loop and
  under artificial CPU load — most timing flakes appear only when the machine is busy.

## AI Review Checklist

- Does the test wait on an observable condition instead of a fixed `sleep`?
- Are time and randomness frozen/seeded so runs are reproducible?
- Is each test fully isolated — its own state, no reliance on execution order?
- Are external services stubbed rather than called live?
- Is the suite run in random order and in parallel to catch ordering coupling?
- Are flaky tests quarantined with a tracking ticket rather than auto-retried into
  green?

## Related

- `knowledge/testing/21-cicd.md`
- `knowledge/testing/23-debugging-tests.md`
- `knowledge/testing/04-e2e-testing.md`
- `knowledge/testing/20-test-maintenance.md`
- `knowledge/testing/06-mocking.md`
