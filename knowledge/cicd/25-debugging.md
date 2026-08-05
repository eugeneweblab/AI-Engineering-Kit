---
id: cicd/25-debugging
topic: cicd
slug: debugging
title: "CI/CD Debugging"
type: doc
order: 25
status: ready
tags: [cicd, debugging]
related: [cicd/04-test-stage, cicd/26-performance, cicd/24-notifications, cicd/03-build-stage, cicd/21-docker-integration]
when_to_use: "Read before diagnosing a failing, flaky, or 'works on my machine' pipeline run."
---
# CI/CD Debugging

## Purpose

This document defines how to diagnose a CI/CD pipeline that is broken, flaky, or
behaves differently from a local machine. It covers reproducing failures,
reading logs, isolating the failing step, handling non-determinism, and doing all
of this without turning debugging into a 50-commit "add echo, push, wait"
spiral.

Pipeline debugging is distinct from application debugging: the environment is
ephemeral, remote, and often can't be attached to with a debugger. The core skill
is making the invisible visible — surfacing the state of an environment you
cannot log into.

## Why It Matters

A red pipeline blocks every merge behind it, so a single flaky test or a slow-to-
diagnose failure taxes the whole team, not one engineer. When people can't trust
the pipeline, they start bypassing it — merging on red, disabling checks,
retrying until green — which defeats the entire purpose of CI/CD.

The naive debugging loop (edit YAML, push, wait five minutes for the runner,
read logs, repeat) is brutally slow because the feedback cycle is minutes, not
seconds. Most wasted CI time comes not from the pipeline but from *debugging* the
pipeline this way. Structured diagnosis — reproduce locally, read what you already
have, change one variable at a time — is the difference between minutes and a
day.

## Core Principles

- **Reproduce before you change.** Run the failing step in the same container
  locally (`act`, `docker run` with the CI image) before pushing a "fix." Blind
  push-and-pray wastes runner minutes and hides the real cause.
- **The logs already hold the answer — read them first.** Failures near the top of
  a stack are usually symptoms; scroll to the *first* error, not the last.
- **Change one variable at a time.** Environment, dependency versions, cache
  state, and concurrency are all suspects. Alter one and observe; changing several
  at once tells you nothing.
- **Flaky is a bug, not bad luck.** A test that fails 1 in 20 runs is a real
  defect (shared state, timing, ordering). Quarantine it, do not retry-until-green
  in a way that masks it forever.
- **Difference between local and CI is always the environment.** Versions, env
  vars, file ordering, timezone, or missing services — enumerate what CI has that
  you don't, and vice versa.

## Best Practices

- Pin and print the toolchain versions (`node --version`, `python --version`) at
  the start of a run so "works locally" gaps are visible in the log.
- Reproduce with the exact CI image: `docker run --rm -it <ci-image> bash`, then
  run the failing command by hand. This collapses the feedback loop from minutes
  to seconds.
- Enable step debug logging when stuck (GitHub Actions: set secret
  `ACTIONS_STEP_DEBUG=true`; GitLab: `CI_DEBUG_TRACE=true`) — then turn it off; it
  can leak values into logs.
- Upload logs, screenshots, and reports as [artifacts](07-artifacts.md) on
  failure so you can inspect them after the ephemeral runner is gone.
- For flaky tests: reproduce with a fixed seed and repeated runs
  (`--repeat`/`--count`), fix root cause (isolation, ordering, timing), and only
  quarantine as a temporary, tracked measure.
- Use an interactive debug session (`tmate`, GitLab interactive web terminal) as a
  last resort to inspect a live runner — never leave it enabled on shared
  pipelines.
- Add `--no-cache` / clear the cache when a build passes clean but fails
  incrementally; stale [cache](26-performance.md) is a top cause of phantom
  failures.

## Examples

**Good Example** — reproduce locally, one variable, real diagnosis

```bash
# 1. Reproduce in the exact CI environment, not "on my Mac".
docker run --rm -it node:22-bookworm bash
#    Inside the container, mirror the failing step:
npm ci                       # same clean install CI uses (not `npm install`)
npm test -- --runInBand      # disable parallelism to test the "flaky" hypothesis

# 2. If it now passes, the variable is concurrency -> shared state between tests.
#    Fix the isolation; do NOT just add a retry.
```

**Bad Example** — push-and-pray, multiple variables, masks the bug

```yaml
# Each "fix" is a blind commit; the loop takes minutes and proves nothing.
test:
  script:
    - npm install            # changed install AND
    - export TZ=UTC          # changed timezone AND
    - npm test || npm test   # retried until green -> flaky bug now permanent + hidden
  retry: 2                   # masks non-determinism instead of fixing it
```

## Common Mistakes

- Debugging by pushing commits and waiting for the runner instead of reproducing
  locally in the CI image.
- Reading the last error in the log instead of scrolling to the first one.
- Changing several things in one commit, so a pass/fail tells you nothing about
  cause.
- "Fixing" flaky tests with automatic retries, converting an intermittent failure
  into a permanent hidden bug.
- Losing diagnostic output because logs/reports weren't uploaded as artifacts
  before the runner was destroyed.
- Leaving step-debug or an interactive `tmate` session enabled, leaking secrets or
  hanging shared pipelines.
- Ignoring stale cache as a cause when a clean build passes but an incremental one
  fails.

## Production Tips

- Track flaky tests in a dashboard with fail-rate over time; a rising rate is a
  reliability regression, treat it like an incident.
- Keep a "reproduce locally" one-liner in the README so anyone can run the exact
  CI step without reverse-engineering the YAML.
- Capture `env`, versions, and `git rev-parse HEAD` in a "diagnostics" step that
  always runs, so every failed log is self-describing.

## AI Review Checklist

- Can the failing step be reproduced locally in the CI image, and is that
  documented?
- Does the fix change exactly one variable, with the reasoning stated?
- Are flaky tests fixed at the root (isolation/ordering/timing) rather than hidden
  behind retries?
- Are logs, reports, and screenshots uploaded as artifacts on failure?
- Is step-debug / interactive-terminal access disabled by default and free of
  secret leakage?
- Is stale cache ruled out when incremental builds fail but clean builds pass?

## Related

- `knowledge/cicd/04-test-stage.md`
- `knowledge/cicd/26-performance.md`
- `knowledge/cicd/24-notifications.md`
- `knowledge/cicd/03-build-stage.md`
- `knowledge/cicd/21-docker-integration.md`
