---
id: cicd/26-performance
topic: cicd
slug: performance
title: "CI/CD Performance"
type: doc
order: 26
status: ready
tags: [cicd, performance, poetry.lock, go.sum, install, node_modules]
related: [cicd/03-build-stage, cicd/04-test-stage, cicd/02-pipeline-design, cicd/21-docker-integration, cicd/07-artifacts]
when_to_use: "Read before optimizing a slow pipeline or when CI feedback time is hurting developer throughput."
---
# CI/CD Performance

## Purpose

This document defines how to make a CI/CD pipeline fast without making it
unreliable. It covers caching, parallelization, dependency management, image size,
test splitting, and the trade-offs each one carries. The target is short feedback:
a developer should learn whether a change is safe in minutes, not tens of minutes.

Speed is a correctness concern in disguise. A pipeline slow enough that people
batch changes, skip checks, or context-switch away is a pipeline whose value is
being eroded. This document is about buying speed *without* buying flakiness.

## Why It Matters

CI runtime multiplies across the team every single day. A pipeline that takes 20
minutes instead of 5 costs 15 minutes per push, dozens of times a day — and worse,
it breaks the developer's flow. Once feedback crosses roughly ten minutes, people
stop waiting for it: they switch tasks, merge speculatively, and lose the tight
loop that makes CI useful.

Slow pipelines also cost money directly — runner minutes are billed — and cost
reliability indirectly, because the usual "fixes" (aggressive caching, high
parallelism, retries) introduce non-determinism if done carelessly. The skill is
optimizing the biggest bottleneck first, measuring the result, and never trading
correctness for speed.

## Core Principles

- **Measure before optimizing.** Read the per-step timings and attack the single
  largest cost first. Optimizing a 10-second step while a 6-minute one sits
  untouched is wasted effort.
- **Cache what is expensive and deterministic; key it exactly.** Dependency
  installs and build outputs are ideal to cache — but the cache key must include a
  hash of the lockfile so a dependency change invalidates it. A stale cache is a
  correctness bug.
- **Parallelize independent work; respect real dependencies.** Lint, unit tests,
  and type-checks can run at once. Don't fake parallelism across steps that share
  state or ordering.
- **Do the cheapest, most-likely-to-fail work first.** Lint and fast unit tests
  before slow integration/e2e, so common failures return in seconds and don't burn
  a full run.
- **Smaller inputs, faster everything.** Shallow clones, slim base images, and
  scoped test selection cut time at every stage. Pull less, build less, run less.

## Best Practices

- Cache package manager directories keyed on the lockfile hash
  (`hashFiles('**/package-lock.json')`, `poetry.lock`, `go.sum`). Never key a
  cache on branch name alone — it will serve stale or cross-contaminated content.
- Use `npm ci` / `pip install --require-hashes` / equivalent for clean,
  reproducible installs; they are faster and deterministic versus `install`.
- Split slow test suites across parallel shards (matrix / `parallel` keyword) and
  balance shards by timing, not by file count.
- Use multi-stage Docker builds and layer ordering so dependency layers cache and
  only changed source invalidates; see [Docker integration](21-docker-integration.md).
- Shallow-clone (`fetch-depth: 1`) unless full history is required (e.g. for
  changelog or blame), cutting checkout time on large repos.
- Fail fast: order stages cheap-to-expensive and stop the pipeline on the first
  gate failure rather than running everything and reporting at the end.
- Set sensible timeouts on every job so a hung step fails in minutes instead of
  holding a runner (and its cost) for an hour.

## Examples

**Good Example** — lockfile-keyed cache, clean install, parallel shards

```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]        # split slow suite into balanced parallel shards
steps:
  - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
    with: { fetch-depth: 1 }   # shallow clone: no full history needed for tests
  - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4.4.0
    with:
      node-version: '22'
      cache: 'npm'             # cache key derived from package-lock.json hash
  - run: npm ci                # deterministic, faster than `npm install`
  - run: npm test -- --shard=${{ matrix.shard }}/4
```

**Bad Example** — cache keyed on branch, serial, no timeout

```yaml
steps:
  - uses: actions/checkout@v4  # full history clone by default -> slow on big repos
  - uses: actions/cache@v4
    with:
      path: node_modules
      key: cache-${{ github.ref }}   # keyed on branch -> stale + cross-branch bleed
  - run: npm install           # non-deterministic; may resolve new versions
  - run: npm run test:all      # one serial run of everything, no shards, no timeout
```

## Common Mistakes

- Optimizing a minor step while the actual bottleneck (often e2e tests or image
  build) goes untouched — because timings were never measured.
- Keying the cache on branch or a static string, so it serves stale artifacts and
  produces flaky, hard-to-explain failures.
- Caching `node_modules` directly instead of the package manager cache, breaking
  when the platform or lockfile changes.
- Cranking up parallelism across steps that share state, causing intermittent
  race-condition failures.
- Running expensive integration/e2e tests before cheap lint/unit checks, so a
  trivial failure costs a full pipeline.
- No per-job timeouts, letting a hung step consume runner minutes indefinitely.

## Production Tips

- Track pipeline duration (p50/p95) over time as a first-class metric; a rising
  p95 is a regression to investigate, not accept.
- Use path/change filters so unaffected pipelines (e.g. docs-only changes) skip
  heavy build and test stages entirely.
- Warm caches on the default branch nightly so feature branches start from a
  populated cache instead of a cold one.

## AI Review Checklist

- Were step timings measured, and does the optimization target the actual
  bottleneck?
- Is every cache keyed on a content hash (lockfile) that invalidates on change?
- Are independent checks parallelized while genuinely dependent steps stay
  ordered?
- Do cheap, high-signal checks (lint, unit) run before slow ones (integration,
  e2e)?
- Are clones shallow and base images slim where full history/size isn't needed?
- Does every job have a timeout to bound cost and catch hangs?

## Related

- `knowledge/cicd/03-build-stage.md`
- `knowledge/cicd/04-test-stage.md`
- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/21-docker-integration.md`
- `knowledge/cicd/07-artifacts.md`
