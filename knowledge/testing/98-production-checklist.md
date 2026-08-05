---
id: testing/98-production-checklist
topic: testing
slug: production-checklist
title: "Testing Production Checklist"
type: checklist
order: 98
status: ready
tags: [testing, production-checklist]
related: [testing/21-cicd, testing/22-flaky-tests, testing/19-test-coverage, testing/27-quality-gates, testing/25-production-testing]
when_to_use: "Read before merging to a release branch or promoting a build to production."
---
# Testing Production Checklist

## Purpose

This is the gate a test suite must pass before its code ships. Each item is a verifiable
yes/no an agent or reviewer can check against the repository and the CI pipeline. If an
item cannot be answered "yes," the suite is not production-ready — fix it or record an
explicit, time-boxed exception. This complements the [quality gates](27-quality-gates.md)
that enforce these checks automatically.

## Why It Matters

Tests that never run in CI, run non-deterministically, or pass without asserting anything
give false confidence — the most expensive kind, because teams act on it. A production
release rides on the suite being honest: green must mean "safe to ship." This checklist
turns that requirement into concrete, auditable items so nothing load-bearing is assumed.

## Suite Correctness

**Rules:** [Assertions](09-assertions.md) · [Best Practices](24-best-practices.md)

- [ ] Every test asserts observable behavior, not internal state or call counts.
- [ ] Each test can fail: you can name the production change that turns it red.
- [ ] No test is skipped or disabled without a linked ticket and an owner.
- [ ] There are no `sleep`/fixed-delay hacks; waits are condition-based with timeouts.
- [ ] Tests do not depend on execution order and pass when run in isolation and in parallel.

## Determinism and Isolation

**Rules:** [Flaky Tests](22-flaky-tests.md) · [Test Data](07-test-data.md)

- [ ] No test reads the real wall clock, network, filesystem, or random source without
      control (injected clock, seeded RNG, stubbed transport).
- [ ] Each test creates and tears down its own data; no shared mutable global state.
- [ ] The suite passes on a clean machine with no pre-seeded local state.
- [ ] The known flake rate is at or near zero; any flaky test is quarantined with a fix ticket.

## Coverage and Levels

**Rules:** [Test Coverage](19-test-coverage.md) · [Strategy](28-testing-strategy.md)

- [ ] Critical paths (auth, payments, data writes) have integration or E2E coverage, not
      just unit tests. See [testing strategy](28-testing-strategy.md).
- [ ] The [test pyramid](01-testing-fundamentals.md) holds: many fast unit tests, fewer
      integration, fewest E2E — not the inverse.
- [ ] Negative and error paths are tested, not only the happy path.
- [ ] Coverage is measured and meets the agreed threshold, and the threshold is not gamed
      by assertion-free tests. See [test coverage](19-test-coverage.md).

## CI/CD Integration

**Rules:** [CI/CD](21-cicd.md) · [Quality Gates](27-quality-gates.md)

- [ ] The full suite runs on every pull request and blocks merge on failure.
- [ ] A red build cannot be merged; the gate is enforced, not advisory.
- [ ] Test run time is tracked and the inner-loop (unit) suite stays fast enough to run locally.
- [ ] CI runs against the same runtime versions and config as production, not just the dev machine.
- [ ] Flaky-test retries, if any, are logged and surfaced — never silently swallowed. See
      [CI/CD](21-cicd.md).

## Data and Environment

**Rules:** [Test Data](07-test-data.md) · [Fixtures](10-fixtures.md)

- [ ] Test data uses factories/builders, not brittle shared fixtures copied across tests.
- [ ] No test uses real production data, real credentials, or real third-party accounts.
- [ ] External services are faked, stubbed, or run as ephemeral containers — never called live.
- [ ] Secrets used in tests come from the CI secret store, not committed to the repo.

## Production-Time Testing

**Rules:** [Production Testing](25-production-testing.md) · [Observability](26-observability.md)

- [ ] Smoke tests run against the deployed build before it takes traffic. See
      [production testing](25-production-testing.md).
- [ ] Health checks and key user journeys are monitored post-deploy, with alerting.
- [ ] A rollback path is verified, so a failed smoke test can revert automatically.
- [ ] Synthetic monitoring covers the critical paths continuously, not just at deploy time.

## AI Review Checklist

- Does CI block merge on any test failure, and is that enforced by the platform?
- Is the suite deterministic and free of order dependence, verified by a parallel run?
- Do critical paths have coverage at the right level, including error paths?
- Are external dependencies faked or containerized rather than called live?
- Do smoke tests and monitoring guard the build after it deploys?

## Related

- `knowledge/testing/21-cicd.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/19-test-coverage.md`
- `knowledge/testing/27-quality-gates.md`
- `knowledge/testing/25-production-testing.md`
