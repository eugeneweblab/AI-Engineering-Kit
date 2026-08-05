---
id: github/09-workflows
topic: github
slug: workflows
title: "Workflows"
type: doc
order: 9
status: ready
tags: [github, workflows, timeout-minutes, cancel-in-progress, paths, continue-on-error, concurrency, runs-on]
related: [github/08-actions, github/06-pull-requests, github/11-releases, github/17-branch-protection, github/26-automation]
when_to_use: "Read before writing or changing a GitHub Actions workflow file under .github/workflows."
---
# Workflows

## Purpose

This document defines how to structure a **GitHub Actions workflow** — the YAML file under
`.github/workflows/` that describes triggers, jobs, and their dependencies. It covers when
a workflow runs, how jobs relate, and how to keep runs fast, deterministic, and safe. The
security of the individual steps you call is covered in [actions](08-actions.md); this doc
is about the workflow's shape and behavior.

A workflow is executable policy: it decides what "green" means for your repository. Get it
wrong and CI either blocks nothing or blocks everything.

## Why It Matters

Workflows are what branch protection enforces, what gates merges, and what ships releases.
A workflow that triggers on the wrong event runs at the wrong time; one with no
concurrency control burns runner minutes and lets stale runs override fresh ones; one
that is flaky trains the team to click "re-run" until it passes, defeating the check
entirely. And because workflows run with repository tokens on every push, a mis-scoped
trigger is also a security exposure. The workflow's correctness is the CI's correctness.

## Core Principles

- **Trigger on exactly the right events.** `push` to protected branches, `pull_request`
  for validation. Do not run the full pipeline on every event "just in case" — it wastes
  minutes and dilutes signal.
- **Make runs deterministic.** Pin runner versions, pin action SHAs, and lock dependency
  versions so a green run today is a green run tomorrow. Flakiness is a bug, not weather.
- **Fail fast and fail loud.** Cheap checks (lint, type) before expensive ones (e2e).
  Never `continue-on-error` a check that is supposed to gate merges.
- **One concurrency group per ref.** Cancel superseded in-progress runs so only the latest
  commit's result matters and minutes are not wasted on dead runs.
- **Least privilege at the top.** Declare `permissions:` at the workflow level as
  read-only and elevate per job — the default token is too powerful.

## Best Practices

- Scope PR workflows with `paths:` / `branches:` filters so a docs-only change does not run
  the full test matrix.
- Add a `concurrency:` block keyed on the ref with `cancel-in-progress: true` for PR
  validation, so pushing a fix cancels the prior run.
- Set `timeout-minutes` on every job to cap hung runs; the default is 6 hours of wasted
  minutes.
- Cache dependencies (`actions/cache` or `setup-*` built-in cache) keyed on the lockfile
  hash to cut install time without risking stale caches.
- Use a **matrix** to test across versions/OSes in parallel instead of serial jobs.
- Extract shared logic into **reusable workflows** (`workflow_call`) or composite actions
  so the same pipeline is defined once, not copy-pasted per repo.
- Name jobs stably and mark the ones that must pass as **required checks** in branch
  protection — the workflow only gates merges if the check is required.

## Examples

**Good Example** — scoped triggers, concurrency, least privilege, fail-fast order

```yaml
name: CI
on:
  pull_request:
    paths: ["src/**", "package.json", "package-lock.json"]  # skip docs-only PRs

permissions:
  contents: read                       # least privilege for the whole workflow

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true             # a new push cancels the stale run

jobs:
  test:
    runs-on: ubuntu-24.04              # pinned runner → reproducible
    timeout-minutes: 15                # cap hung jobs
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: actions/setup-node@39370e3970a6d050c480ffad4ff0ed4d3fdee5af # v4.1.0
        with: { node-version: "22", cache: "npm" }   # cache keyed on lockfile
      - run: npm ci
      - run: npm run lint              # cheap checks first...
      - run: npm run typecheck
      - run: npm test                  # ...expensive last, so failures surface fast
```

**Bad Example** — over-broad trigger, no concurrency, non-gating checks

```yaml
name: CI
on: push                              # every branch + tag runs the full pipeline

jobs:
  test:
    runs-on: ubuntu-latest            # non-reproducible; no timeout → can hang 6h
    steps:
      - uses: actions/checkout@v4      # mutable tag
      - run: npm install               # unpinned deps, no cache
      - run: npm test || true          # swallows failures → check is always "green"
```

## Common Mistakes

- Triggering on `push` for everything, so tags and every branch run the full matrix.
- No `concurrency` block, so obsolete runs finish and can report over the latest commit.
- `continue-on-error: true` or `|| true` on a gating step, making red look green.
- No `timeout-minutes`, letting a hung job consume the full 6-hour ceiling.
- Duplicating the same pipeline across ten repos instead of a reusable workflow.
- Naming a check inconsistently so branch protection cannot pin it as required.
- Running expensive e2e before cheap lint, so trivial failures take 20 minutes to show.

## Production Tips

- Store shared pipelines in a central repo and call them with `uses: org/repo/.github/
  workflows/ci.yml@<sha>` so every project inherits fixes at once.
- Use environment protection rules (required reviewers, wait timers) on deploy jobs so a
  workflow cannot push to production unattended.
- Watch runner-minute spend; `paths` filters and concurrency cancellation are the two
  biggest levers on cost.
- Treat a flaky workflow as a P2 bug: quarantine the flaky test, do not add blanket
  retries that hide real failures.

## AI Review Checklist

- Do triggers and `paths`/`branches` filters run the workflow only when needed?
- Is there a `concurrency` group with `cancel-in-progress` for PR validation?
- Are `permissions` least-privilege at the workflow level?
- Does every job set `timeout-minutes` and use a pinned runner image?
- Are gating steps free of `continue-on-error`/`|| true` that mask failures?
- Are cheap checks ordered before expensive ones for fast feedback?
- Are required-for-merge jobs named stably and marked required in branch protection?

## Related

- `knowledge/github/08-actions.md`
- `knowledge/github/06-pull-requests.md`
- `knowledge/github/11-releases.md`
- `knowledge/github/17-branch-protection.md`
- `knowledge/github/26-automation.md`
