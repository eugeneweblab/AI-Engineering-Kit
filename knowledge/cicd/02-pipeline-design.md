---
id: cicd/02-pipeline-design
topic: cicd
slug: pipeline-design
title: "Pipeline Design"
type: doc
order: 2
status: ready
tags: [cicd, pipeline-design]
related: [cicd/01-ci-cd-fundamentals, cicd/03-build-stage, cicd/04-test-stage, cicd/05-quality-gates, cicd/26-performance]
when_to_use: "Read before creating or restructuring a pipeline's stages, ordering, or parallelism."
---
# Pipeline Design

## Purpose

This document defines how to structure a pipeline: what the stages are, how to order them,
where to parallelize, and how to keep the whole run fast and deterministic. It is about the
*shape* of the pipeline, not the contents of any one stage — those are covered in
[Build](03-build-stage.md), [Test](04-test-stage.md), and [Quality Gates](05-quality-gates.md).

A well-designed pipeline gives developers the fastest possible honest answer to "is my
change safe?" — and fails on the first problem instead of hiding it behind a slow build.

## Why It Matters

Pipeline shape decides how fast the team learns it broke something. A serial, mis-ordered
pipeline that runs an expensive integration suite before a lint check wastes 15 minutes to
tell you a semicolon is missing. Developers respond to slow feedback by batching changes,
which makes each failure bigger and harder to diagnose — the opposite of what CI is for.
Shape also decides determinism: a pipeline with hidden state, shared mutable caches, or
unpinned tools produces flaky results that erode trust. Design the pipeline for speed and
reproducibility, or it will be routed around.

## Core Principles

- **Fail fast: cheapest and flakiest checks first.** Order stages so the check most
  likely to fail, and cheapest to run, runs first — lint and type before unit tests
  before integration before end-to-end. Feedback should arrive in seconds when possible.
- **Parallelize independent work; serialize only real dependencies.** Lint, unit tests,
  and type checks share no state — run them concurrently. Deploy genuinely depends on
  build, so it waits.
- **Build once, reuse the artifact.** The build stage produces an artifact that later
  stages consume. Never rebuild in the test or deploy stage.
- **Determinism over convenience.** Pin tool and runtime versions, install from
  lockfiles, and isolate from the network so a rerun on the same commit is identical.
- **Cache inputs, never outputs you must verify.** Cache dependencies and compiler
  layers keyed by lockfile hash; never cache test results you are supposed to re-prove.

## Best Practices

- Keep total wall-clock time under ~10 minutes; split or parallelize stages that exceed it.
- Key caches by a content hash of the lockfile (e.g. `hashFiles('**/package-lock.json')`),
  not by branch name, so a stale cache can never mask a dependency change.
- Make every job idempotent and retriable — no reliance on state left by a prior run.
- Use a matrix to fan out across versions/platforms instead of copy-pasting jobs.
- Set explicit timeouts on every job so a hung step fails instead of blocking the queue.
- Pin action/image versions to a tag or SHA; `@latest` makes builds non-reproducible.

## Examples

**Good Example** — fail-fast ordering, parallel checks, cached deps, build reused

```yaml
jobs:
  # Fast, independent checks run in parallel and gate the expensive stages.
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }   # cache keyed by lockfile
      - run: npm ci
      - run: npm run lint && npm run typecheck

  test:
    runs-on: ubuntu-latest
    steps: [ /* unit tests, run concurrently with lint */ ]

  build:
    needs: [lint, test]            # expensive build only after cheap checks pass
    runs-on: ubuntu-latest
    steps:
      - run: npm ci && npm run build
      - uses: actions/upload-artifact@v4
        with: { name: dist, path: dist/ }            # publish once, reuse downstream
```

**Bad Example** — serial, mis-ordered, rebuilds, unpinned

```yaml
jobs:
  everything:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@latest   # unpinned → non-reproducible
      - run: npm install                # no lockfile install
      - run: npm run build              # build BEFORE lint: slow feedback on typos
      - run: npm run e2e                # slowest suite first, blocks everything
      - run: npm run lint               # the cheap check that should have run first
      - run: npm run build              # rebuilds again for deploy — wasteful, drift risk
```

## Common Mistakes

- Running end-to-end or integration suites before lint/type/unit, so trivial errors cost
  the full pipeline duration.
- One giant serial job instead of parallel independent jobs, doubling wall-clock time.
- Caching keyed by branch, so a dependency change silently uses a stale cache.
- Rebuilding the artifact in later stages, allowing what you test to differ from what you ship.
- Unpinned actions/images (`@latest`, `:latest`) that make reruns non-deterministic.
- No per-job timeout, so a hung step blocks the runner queue indefinitely.

## Production Tips

- Track pipeline duration and failure rate over time; a slowly climbing p95 is a leading
  indicator that developers are about to stop trusting CI.
- Split slow suites with test sharding across parallel runners rather than accepting a
  30-minute serial run. See [Performance](26-performance.md).
- Use `concurrency` groups to cancel superseded runs on the same branch and save minutes.

## AI Review Checklist

- Are cheap, flaky-prone checks (lint, type, unit) ordered before expensive ones?
- Do independent jobs run in parallel, with `needs` only on real dependencies?
- Is the artifact built once and passed downstream, never rebuilt?
- Are caches keyed by lockfile hash, and tool/action versions pinned (no `@latest`)?
- Does every job have an explicit timeout, and is total run time roughly under 10 minutes?

## Related

- `knowledge/cicd/01-ci-cd-fundamentals.md`
- `knowledge/cicd/03-build-stage.md`
- `knowledge/cicd/04-test-stage.md`
- `knowledge/cicd/05-quality-gates.md`
- `knowledge/cicd/26-performance.md`
