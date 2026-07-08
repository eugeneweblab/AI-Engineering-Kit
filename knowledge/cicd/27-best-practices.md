---
id: cicd/27-best-practices
topic: cicd
slug: best-practices
title: "Best Practices"
type: doc
order: 27
status: ready
tags: [cicd, best-practices]
related: [cicd/02-pipeline-design, cicd/05-quality-gates, cicd/15-secrets, cicd/26-performance, cicd/100-common-antipatterns]
when_to_use: "Read before designing a new pipeline or reviewing an existing one for structural soundness."
---
# Best Practices

## Purpose

This document collects the cross-cutting practices that make a CI/CD pipeline
trustworthy: reproducible, fast, secure, and readable. It is the synthesis of the
topic — where [pipeline design](02-pipeline-design.md), [quality gates](05-quality-gates.md),
[secrets](15-secrets.md), and [performance](26-performance.md) meet. Use it as the
checklist against which any pipeline is judged.

A good pipeline is boring: it does the same thing every time, tells you clearly
when something is wrong, and gets out of the way when everything is right. This
document is about achieving that boring reliability on purpose.

## Why It Matters

The pipeline is the single gate every change passes through before it reaches
users. Its quality is a force multiplier — a well-built one catches regressions,
enforces standards, and ships confidently dozens of times a day. A poorly built
one becomes the bottleneck everyone routes around, and the moment people route
around it, the safety it was supposed to provide is gone.

Because every engineer touches the pipeline daily, its flaws compound: a flaky
step, a non-reproducible build, or a confusing failure message taxes the whole
team on every run. Investment in pipeline quality pays back faster than almost any
other engineering investment because of that multiplier.

## Core Principles

- **Reproducibility over convenience.** The same commit must produce the same
  result on any runner, any day. Pin versions, pin base images, use lockfiles.
  Non-determinism is the root of most CI pain.
- **Fail fast, fail loud, fail specific.** Cheap checks first; the first failure
  stops the run; the message names exactly what broke and where.
- **Everything as code, reviewed like code.** Pipeline definitions live in the
  repo, are version-controlled, and go through pull request review — not clicked
  into a UI.
- **Least privilege everywhere.** Jobs get only the secrets and permissions they
  need, scoped and short-lived. Default-deny, grant narrowly.
- **The pipeline is a product with users.** Its users are developers under
  deadline pressure. Optimize for their feedback speed and their ability to
  self-diagnose a failure.

## Best Practices

- Keep pipeline config in the repository next to the code it builds, so a change
  and its pipeline change ship and review together.
- Pin action/image/tool versions to a specific version or digest, not `latest` or
  a floating tag, so builds don't change under you.
- Enforce [quality gates](05-quality-gates.md) — tests, coverage threshold, lint,
  security scan — as required checks that block merge, not advisory warnings.
- Make stages idempotent and independent where possible; a re-run must be safe and
  produce the same result.
- Store all credentials as [secrets](15-secrets.md) with least privilege; never
  echo them, and prefer short-lived OIDC tokens over long-lived static keys.
- Keep total feedback time short (see [performance](26-performance.md)); target
  under ~10 minutes for the pre-merge path.
- Build an artifact once and promote the *same* artifact through environments —
  never rebuild per environment, which risks shipping something you didn't test.
- Notify actionably on failure of protected branches (see
  [notifications](24-notifications.md)) and keep success quiet.

## Examples

**Good Example** — pinned, gated, least-privilege, build-once

```yaml
permissions:
  contents: read              # least privilege: read-only by default
jobs:
  ci:
    runs-on: ubuntu-latest
    timeout-minutes: 15       # bounded runtime
    steps:
      - uses: actions/checkout@v4        # pinned major version
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci                       # reproducible install from lockfile
      - run: npm run lint                 # cheap check first (fail fast)
      - run: npm test -- --coverage       # gate: coverage enforced in config
      - run: npm run build                # build the artifact ONCE
      - uses: actions/upload-artifact@v4  # promote this exact artifact downstream
        with: { name: dist, path: dist/ }
```

**Bad Example** — floating tags, no gates, broad permissions, rebuilds

```yaml
permissions: write-all        # every job can write everything -> huge blast radius
jobs:
  ci:
    runs-on: ubuntu-latest    # no timeout -> hangs cost money
    steps:
      - uses: actions/checkout@latest     # floating tag: build changes under you
      - run: npm install                  # non-deterministic resolution
      - run: npm test || true             # "gate" that never blocks anything
      # build happens again separately in the deploy job -> ships untested output
```

## Common Mistakes

- Configuring pipelines by clicking in a UI, so the config is unversioned and
  unreviewable.
- Using `latest` / floating tags for actions and base images, making builds
  irreproducible.
- Treating tests, coverage, or scans as advisory instead of merge-blocking gates.
- Rebuilding the artifact for each environment instead of promoting one built-once
  artifact.
- Granting broad permissions or long-lived static credentials to every job.
- Long pipelines (>15–20 min) that push developers to bypass CI.
- Copy-pasting the same steps across jobs instead of extracting reusable
  workflows/templates.

## Production Tips

- Extract shared logic into reusable workflows/templates so a fix propagates
  everywhere instead of drifting across copies.
- Adopt trunk-based development with short-lived branches so the pipeline
  integrates small changes continuously rather than giant risky merges.
- Periodically audit the pipeline for the [common antipatterns](100-common-antipatterns.md)
  and against the [production checklist](98-production-checklist.md).

## AI Review Checklist

- Is the pipeline config version-controlled in the repo and reviewed via PR?
- Are all actions, images, and tools pinned to fixed versions or digests?
- Are tests, coverage, lint, and security scans enforced as blocking gates?
- Is the artifact built once and promoted, rather than rebuilt per environment?
- Do jobs run with least-privilege permissions and short-lived credentials?
- Is pre-merge feedback time kept short enough that people don't bypass it?

## Related

- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/05-quality-gates.md`
- `knowledge/cicd/15-secrets.md`
- `knowledge/cicd/26-performance.md`
- `knowledge/cicd/100-common-antipatterns.md`
