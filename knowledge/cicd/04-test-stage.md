---
id: cicd/04-test-stage
topic: cicd
slug: test-stage
title: "Test Stage"
type: doc
order: 4
status: ready
tags: [cicd, test-stage, isValid, toBe, setTimeout, useRealTimers, useFakeTimers, afterEach, ordering, automated, tests]
related: [cicd/02-pipeline-design, cicd/03-build-stage, cicd/05-quality-gates, cicd/06-security-scanning, cicd/26-performance]
when_to_use: "Read before adding, ordering, or debugging automated tests that run in a pipeline."
---
# Test Stage

## Purpose

This document defines how automated tests should run inside a pipeline: how to structure
them by cost, how to keep them isolated and deterministic, and how to handle flakiness so
the suite stays trustworthy. Thresholds and blocking rules that turn test results into a
merge gate live in [Quality Gates](05-quality-gates.md); this doc is about running the
tests correctly in the first place.

The test stage exists to produce one honest bit of information: is this artifact safe to
promote? Anything that makes that bit unreliable — flaky tests, shared state, tests that
depend on the network — defeats the purpose.

## Why It Matters

A test suite is only as valuable as it is trusted. The moment a suite goes red for reasons
unrelated to the change — a flaky timing test, a shared database another job mutated, an
external API that blipped — developers learn to re-run until green. Once "just retry it"
becomes reflex, the suite stops catching real regressions, because a real failure looks
exactly like the noise everyone ignores. A fast, isolated, deterministic suite is a safety
net; a slow, flaky one is a tax that everyone routes around. The test stage must be
engineered for reliability, not just coverage.

## Core Principles

- **Follow the test pyramid.** Many fast unit tests, fewer integration tests, very few
  slow end-to-end tests. Cost and flakiness rise as you go up; keep the base wide.
- **Isolation is mandatory.** Each test controls its own state and shares nothing mutable
  with another. Tests must pass in any order and in parallel.
- **Determinism over realism.** A test that depends on wall-clock time, random seeds, or a
  live third-party service will eventually flake. Freeze time, seed randomness, and stub
  external dependencies.
- **Flaky is failing.** A test that passes only sometimes carries no signal. Quarantine or
  fix it — never paper over it with blanket auto-retries.
- **Test the built artifact, not a fresh build.** Run tests against the exact artifact the
  build stage produced, so you test what you ship. See [Build Stage](03-build-stage.md).

## Best Practices

- Run unit tests first and fastest; gate slower integration/e2e suites behind them so a
  broken unit test does not cost the full suite duration.
- Give each test its own fixtures — a fresh transaction, a unique temp dir, an isolated
  container — and tear them down. Never share a mutable database across parallel jobs.
- Stub the network: no test should call a real third-party API. Use recorded fixtures or a
  local test double so results do not depend on someone else's uptime.
- Control nondeterminism explicitly: inject a fixed clock, seed every RNG, and sort
  collections before asserting on order.
- Shard slow suites across parallel runners to keep wall-clock time down rather than
  accepting a 30-minute run. See [Performance](26-performance.md).
- Track flaky tests as first-class bugs; quarantine them out of the gate and fix them,
  don't hide them behind `retry: 3`.

## Examples

**Good Example** — isolated state, frozen time, stubbed network, deterministic

```ts
import { test, expect, vi, beforeEach, afterEach } from "vitest";

let db: TestDb;
beforeEach(async () => { db = await TestDb.freshSchema(); }); // isolated per test
afterEach(async () => { await db.drop(); });

test("expires a token after its TTL", async () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-01-01T00:00:00Z"));     // deterministic clock

  const token = await db.issueToken({ ttlSeconds: 60 });
  vi.advanceTimersByTime(61_000);                          // no real waiting, no flake

  expect(await db.isValid(token)).toBe(false);
  vi.useRealTimers();
});
```

**Bad Example** — shared state, real sleep, live network, order-dependent

```ts
import { test, expect } from "vitest";

test("expires a token after its TTL", async () => {
  const token = await sharedDb.issueToken({ ttlSeconds: 1 }); // global db, mutated by others
  await new Promise((r) => setTimeout(r, 1100));              // real sleep → slow + flaky
  const rate = await fetch("https://api.example.com/rate");  // live 3rd-party call in a test
  expect(await sharedDb.isValid(token)).toBe(false);         // passes only if run in order
});
```

## Common Mistakes

- Blanket `retries` on the whole suite to mask flakiness, destroying the signal.
- Tests that share a mutable database or global singleton, so they fail when parallelized.
- Real `sleep`/`setTimeout` and live network calls, making tests slow and nondeterministic.
- Running the biggest end-to-end suite first, so a trivial regression costs the full run.
- Rebuilding the app for tests instead of testing the artifact that will ship.
- Asserting on unordered collections without sorting, causing intermittent failures.

## Production Tips

- Report per-test timing and flake rate; a test that flakes >1% of runs should be
  quarantined automatically and ticketed.
- Publish test results (JUnit XML) as a pipeline artifact so failures are diagnosable
  without re-running locally.
- Keep integration tests hermetic with ephemeral containers (test databases, queues) spun
  up in the job, not a shared long-lived staging instance.

## AI Review Checklist

- Do tests run in the pyramid order (unit → integration → e2e), fastest first?
- Is each test isolated — own fixtures, no shared mutable state, order-independent?
- Are clocks frozen, RNGs seeded, and external services stubbed rather than called live?
- Is flakiness treated as a failure (quarantine + fix), not hidden by auto-retries?
- Do tests run against the built artifact rather than a separate fresh build?

## Related

- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/03-build-stage.md`
- `knowledge/cicd/05-quality-gates.md`
- `knowledge/cicd/06-security-scanning.md`
- `knowledge/cicd/26-performance.md`
