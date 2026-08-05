---
id: testing/21-cicd
topic: testing
slug: cicd
title: "CI/CD"
type: doc
order: 21
status: ready
tags: [testing, cicd, runs-on, upload, failure, GitHub]
related: [testing/22-flaky-tests, testing/27-quality-gates, testing/19-test-coverage, testing/28-testing-strategy, testing/25-production-testing]
when_to_use: "Read before wiring a test suite into a CI pipeline or configuring merge gates for a repository."
---
# CI/CD

## Purpose

This document defines how to run tests inside a continuous integration and
delivery pipeline so that the pipeline is a **trustworthy gate**: green means
safe to merge and deploy, red means something is genuinely broken. It is written
so an agent can configure test stages, gates, and feedback that catch regressions
early without becoming slow or noisy.

CI/CD is where testing pays off. A test that is not run automatically on every
change is a test that will silently rot. The pipeline turns your suite from
documentation into an enforced contract.

## Why It Matters

The value of a test suite is proportional to how consistently and quickly it runs.
Run manually, tests are skipped under deadline pressure exactly when they matter
most. In CI they run on every push, on the same clean environment, for every
contributor. But a pipeline is only as trusted as its reliability: a suite that is
slow or intermittently red trains the team to ignore it, `--no-verify` past it, or
merge on red. A fast, deterministic pipeline is the difference between a safety net
and a formality. Getting this right protects every downstream deploy.

## Core Principles

- **Fast feedback first.** Order stages cheapest-to-slowest: lint and type-check,
  then unit, then integration, then E2E. Fail fast so a syntax error does not
  wait ten minutes behind a browser suite.
- **Deterministic and isolated.** Every run starts from a clean, pinned
  environment with fixed dependency versions and seeded data. Non-determinism in
  CI is a bug, not a quirk — [flaky tests](22-flaky-tests.md) must be quarantined,
  not retried into green.
- **Green must mean green.** Never allow "known failing" tests to stay red or be
  auto-retried until they pass. A required check that is allowed to fail is not a
  gate.
- **The pipeline is the source of truth.** Merge protection requires the checks to
  pass; local runs are a convenience, not the contract.
- **Tests run against production-like artifacts.** Build once, test the built
  artifact, deploy the same artifact. Testing one build and shipping another
  invalidates the whole pipeline.

## Best Practices

- Pin dependencies (lockfiles) and cache them by lockfile hash so runs are
  reproducible and fast; invalidate the cache only when the lock changes.
- Parallelize and **shard** slow suites across runners, and run only tests
  affected by the diff on PRs where the tooling supports it — reserve the full
  suite for the merge queue or main.
- Make required status checks **branch-protection gates**: coverage regression,
  lint, type-check, and the test suites must pass before merge.
- Upload artifacts on failure — screenshots, videos, traces, logs, and coverage —
  so a red build is debuggable without re-running locally.
- Run E2E against an ephemeral, seeded environment spun up per pipeline, torn down
  after, so tests never share mutable state across runs.
- Set a hard timeout per job and per test so a hung test fails loudly instead of
  burning the runner budget.
- Keep secrets in the CI secret store, injected as env vars — never in the repo or
  test fixtures.

## Examples

**Good Example** — staged, cached, fail-fast, artifacts on failure

```yaml
# GitHub Actions: cheap checks gate the expensive ones; failures upload evidence.
jobs:
  static:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm } # cache keyed on package-lock.json
      - run: npm ci
      - run: npm run lint && npm run typecheck   # fastest signals first

  test:
    needs: static                                # don't burn runners if static fails
    runs-on: ubuntu-latest
    strategy:
      matrix: { shard: [1, 2, 3, 4] }            # shard the suite for speed
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm test -- --shard=${{ matrix.shard }}/4 --coverage
      - uses: actions/upload-artifact@v4
        if: failure()                            # traces/coverage available on red
        with:
          name: test-output-${{ matrix.shard }}
          path: |
            coverage
            test-results
```

**Bad Example** — retries hide flakiness; failures are undiagnosable

```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: npm install            # no lockfile install → non-reproducible versions
    - run: npm test || npm test || npm test  # brute-force retry masks real flakiness
    # No caching (slow), no sharding (slow), no artifact upload (undebuggable),
    # and the retry means "green" no longer means the suite is actually passing.
```

## Common Mistakes

- Auto-retrying the whole suite until it passes, converting flaky failures into
  false green and hiding real regressions.
- Running the slowest suite first, so trivial errors take the full pipeline time
  to surface.
- Using `npm install` / unpinned versions, making CI non-reproducible ("works on
  my machine, fails in CI").
- No artifact upload on failure, forcing developers to reproduce locally to see
  what broke.
- Marking checks "optional" or allowing merge on red, so the gate is decorative.
- Sharing a long-lived test database across pipeline runs, causing order-dependent
  cross-run failures.

## Production Tips

- Track pipeline duration and flaky-failure rate as first-class metrics; a
  creeping p95 runtime silently erodes the whole team's velocity.
- Use a **merge queue** so PRs are tested against the exact post-merge state,
  eliminating "green PR, broken main" from parallel merges.
- Quarantine a newly flaky test into a non-blocking lane with an auto-filed
  ticket rather than retrying it in the required lane — keep the gate honest.

## AI Review Checklist

- Are stages ordered fast-to-slow (lint/type → unit → integration → E2E) with
  fail-fast between them?
- Are dependencies pinned via lockfile and cached by lockfile hash?
- Are required test/coverage/lint checks enforced by branch protection before
  merge?
- Are failure artifacts (traces, screenshots, logs, coverage) uploaded on red?
- Is the suite free of blanket retries that would mask flakiness?
- Do E2E tests run against an ephemeral, seeded environment rather than shared
  mutable state?

## Related

- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/27-quality-gates.md`
- `knowledge/testing/19-test-coverage.md`
- `knowledge/testing/28-testing-strategy.md`
- `knowledge/testing/25-production-testing.md`
