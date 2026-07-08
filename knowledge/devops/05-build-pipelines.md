---
id: devops/05-build-pipelines
topic: devops
slug: build-pipelines
title: "Build Pipelines"
type: doc
order: 5
status: ready
tags: [devops, build-pipelines]
related: [devops/03-git-workflow, devops/04-branching-strategies, devops/23-quality-gates, devops/07-deployment-strategies, devops/17-secrets-management]
when_to_use: "Read before writing or reviewing CI/CD pipeline configuration that builds, tests, or ships code."
---
# Build Pipelines

## Purpose

This document defines how to build a Continuous Integration / Continuous Delivery (CI/CD)
pipeline: the automated sequence that turns a commit into a tested, versioned artifact
ready to deploy. It is the enforcement mechanism for the [development lifecycle](02-development-lifecycle.md)
and the [quality gates](23-quality-gates.md) — the pipeline is *how* those gates actually
stop bad changes. This doc covers building and validating the artifact; deploying it is
[07 Deployment Strategies](07-deployment-strategies.md).

## Why It Matters

The pipeline is the only path to production that is guaranteed to run every check, every
time, the same way. Humans skip steps under pressure; a pipeline does not. It is also the
fastest, cheapest place to catch defects — a failed test in CI costs a re-run, the same
defect in production costs an incident. A slow, flaky, or non-reproducible pipeline is
worse than none: it trains the team to ignore red builds and merge anyway, which quietly
disables every safety check the pipeline was supposed to provide.

## Core Principles

- **Fast feedback.** Order stages cheapest-and-most-likely-to-fail first: lint, then unit
  tests, then integration, then slow end-to-end. Fail fast so an engineer learns in minutes.
- **Reproducible and deterministic.** The same commit must produce the same result every
  run. Pin tool and dependency versions with lockfiles; a pipeline that depends on "latest"
  is a pipeline that breaks randomly.
- **Fail fast, fail loud.** Any failing gate stops the pipeline and blocks the merge/deploy.
  A red build must never be mergeable. Warnings that don't block get ignored.
- **Build once, promote the artifact.** Produce a single immutable, versioned artifact and
  promote *that* through environments. Never rebuild per stage.
- **Least privilege.** The pipeline holds powerful credentials. Scope them tightly, inject
  secrets at runtime from a manager, and never echo them into logs. See
  [17 Secrets Management](17-secrets-management.md).

## Best Practices

- Trigger CI on every push and pull request; make a green pipeline a required merge gate via
  branch protection.
- Cache dependencies and use layered/container builds to keep the pipeline fast — slow
  pipelines get bypassed. Target the whole run in single-digit minutes where feasible.
- Pin versions everywhere: base images by digest, dependencies by lockfile, actions/plugins
  by SHA. This is what makes builds reproducible and supply-chain-safe.
- Tag the artifact with the Git SHA (and semver on release) so any running instance is
  traceable to its exact source and pipeline run.
- Include security and quality gates in the pipeline: dependency/vulnerability scan, static
  analysis, and secret scanning — automated, not left to reviewer memory.
- Store least-privilege credentials in the CI provider's secret store or a vault; prefer
  short-lived OIDC tokens over long-lived static keys.

## Examples

**Good Example** — staged, pinned, fast-fail, build-once

```yaml
# GitHub Actions — cheap checks first, artifact built once and reused.
name: ci
on: [push, pull_request]
jobs:
  verify:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4          # pinned by major; prefer SHA in prod
      - uses: actions/setup-node@v4
        with: { node-version: "22", cache: "npm" }  # cache deps for speed
      - run: npm ci                        # install from lockfile → reproducible
      - run: npm run lint                  # seconds: fail fast on the cheapest check
      - run: npm test                      # unit tests before slower stages
      - run: npm audit --audit-level=high  # security gate blocks the build
  build:
    needs: [verify]                        # only build if all gates passed
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t registry/app:${{ github.sha }} .  # tagged by commit
      - run: docker push registry/app:${{ github.sha }}        # one artifact to promote
```

**Bad Example** — non-reproducible, slow-first, secret leak

```yaml
jobs:
  build:
    steps:
      - run: npm install                   # no lockfile ci → versions drift per run
      - run: npm run test:e2e              # slow 20-min suite runs BEFORE unit/lint
      - run: npm run lint                  # cheap check runs last — wastes 20 min to fail
      - run: echo "DEPLOY_KEY=$DEPLOY_KEY" # secret printed into build logs (leaked)
      - run: docker build -t app:latest .  # `latest` tag → untraceable, unpinnable
```

## Common Mistakes

- Non-reproducible builds using `npm install`/unpinned versions instead of `npm ci` and
  lockfiles, so builds fail or drift for reasons unrelated to the change.
- Running slow suites before fast ones, so engineers wait 20 minutes to learn a typo broke
  the lint.
- Making failures non-blocking ("continue-on-error"), which trains everyone to ignore red.
- Tagging artifacts `:latest` instead of by SHA, making a running instance impossible to
  trace back to its source.
- Printing secrets into logs, or storing long-lived cloud keys in the CI config.
- Rebuilding the artifact at each stage instead of promoting the one that was tested.

## Production Tips

- Fail the build on new critical/high vulnerabilities from the dependency scan; auto-open a
  PR to bump the offending package.
- Track pipeline duration and flakiness as first-class metrics — a flaky suite erodes trust
  until people merge past red.
- Prefer ephemeral, short-lived OIDC credentials from the cloud provider over static keys
  stored in CI, so a leaked token expires on its own.

## AI Review Checklist

- Are stages ordered fast-to-slow (lint → unit → integration → e2e) for quick feedback?
- Is the build reproducible — lockfile installs and pinned tool/image/action versions?
- Do failing gates actually block merge and deploy (nothing set to continue-on-error)?
- Is a single artifact built once and promoted, tagged by Git SHA (not `:latest`)?
- Do security gates (dependency scan, SAST, secret scan) run in the pipeline?
- Are secrets injected at runtime with least privilege and kept out of logs?

## Related

- `knowledge/devops/03-git-workflow.md`
- `knowledge/devops/04-branching-strategies.md`
- `knowledge/devops/23-quality-gates.md`
- `knowledge/devops/07-deployment-strategies.md`
- `knowledge/devops/17-secrets-management.md`
