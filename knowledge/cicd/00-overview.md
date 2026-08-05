---
id: cicd/00-overview
topic: cicd
slug: overview
title: "CI/CD Overview"
type: doc
order: 0
status: ready
tags: [cicd, overview]
related: [cicd/01-ci-cd-fundamentals, cicd/02-pipeline-design, cicd/05-quality-gates, cicd/10-deployment, cicd/100-common-antipatterns]
when_to_use: "Read first when setting up, reviewing, or reasoning about any CI/CD pipeline in this repo."
---
# CI/CD Overview

## Purpose

This topic teaches an agent how to build and reason about **CI/CD** — the automated
path that turns a commit into a verified, deployable, and deployed artifact. It covers
the pipeline as a whole (fundamentals, design), each stage (build, test, quality gates,
security, artifacts), and the delivery side (versioning, releases, deployment strategies,
rollbacks). Read this page to orient yourself, then jump to the specific doc you need.

CI (Continuous Integration) is about *proving a change is safe* — every commit is built
and tested automatically. CD (Continuous Delivery/Deployment) is about *shipping that
proven change* — packaging it and rolling it out with minimal human intervention. A
correct pipeline does both, in that order, and never lets an unproven change reach users.

## Why It Matters

The pipeline is the single gate every line of code passes through before it reaches
production. If the gate is weak — flaky tests, skipped scans, manual steps that get
forgotten — bad code ships and the whole team's velocity depends on luck. If the gate is
slow, developers batch changes and stop trusting it. A pipeline is infrastructure: it
must be as correct, deterministic, and reviewable as the application it ships. An agent
editing pipeline config is editing production safety, not a convenience script.

## How These Docs Fit Together

- **Foundations** — start here to understand the model.
  - [CI/CD Fundamentals](01-ci-cd-fundamentals.md): what CI vs CD mean, trigger model, trunk-based flow.
  - [Pipeline Design](02-pipeline-design.md): stages, ordering, parallelism, fail-fast, caching.
- **The verification stages** — what runs on every commit.
  - [Build Stage](03-build-stage.md): deterministic, reproducible builds.
  - [Test Stage](04-test-stage.md): the test pyramid in CI, isolation, flakiness.
  - [Quality Gates](05-quality-gates.md): coverage, lint, type, and gate thresholds that block merge.
  - [Security Scanning](06-security-scanning.md): SAST, dependency, secret, and image scans.
- **The delivery stages** — turning a green build into a running release.
  - [Artifacts](07-artifacts.md) and [Versioning](08-versioning.md): build once, version immutably.
  - [Release Management](09-release-management.md) and [Deployment](10-deployment.md).
  - [Blue-Green](11-blue-green-deployment.md), [Canary](12-canary-deployment.md),
    [Feature Flags](13-feature-flags.md), [Rollbacks](14-rollbacks.md).
- **Cross-cutting concerns** — [Secrets](15-secrets.md), [Environments](16-environments.md),
  and platform guides ([GitHub Actions](17-github-actions.md), [GitLab CI](18-gitlab-ci.md)).
- **Reference** — [Best Practices](27-best-practices.md),
  [Production Checklist](98-production-checklist.md),
  [AI Review Checklist](99-ai-review-checklist.md),
  [Common Anti-Patterns](100-common-antipatterns.md).

## Core Principles

- **Build once, promote the same artifact.** Never rebuild per environment; a rebuilt
  binary is a different binary. Build in CI, then promote the identical artifact through
  staging to production.
- **Every merge is gated by an automated proof.** No green pipeline, no merge. The gate
  is the same for everyone, including hotfixes.
- **Fail fast and loud.** Order stages cheapest-and-most-likely-to-fail first so feedback
  arrives in seconds, not after a 20-minute build.
- **Pipelines are code, reviewed like code.** Config lives in the repo, is version
  controlled, and goes through pull request review.
- **Deterministic in, deterministic out.** Pin versions, isolate from the network, and
  make a rerun on the same commit produce the same result.

## Best Practices

- Keep the whole CI run under ~10 minutes; longer feedback loops train developers to
  context-switch and stop trusting the pipeline.
- Run the pipeline on pull requests *and* on the protected branch after merge — PR
  results can be stale relative to the merge target.
- Store pipeline definitions in the repo (`.github/workflows`, `.gitlab-ci.yml`) so
  changes are diffable and revertible.
- Make jobs idempotent and independent so they can be retried and parallelized safely.
- Surface results where developers work — required status checks on the PR, not a
  dashboard nobody opens.

## Common Mistakes

- Treating CI/CD as ops-only config that skips code review.
- Rebuilding artifacts for each environment, so "tested in staging" no longer guarantees
  the production binary.
- Letting flaky tests be retried until green, which trains everyone to ignore failures.
- Long, serial pipelines that make developers batch large risky changes.
- Manual deploy steps that live only in someone's head or a wiki.

## AI Review Checklist

- Is the pipeline definition version-controlled and reviewed like application code?
- Is the artifact built once and promoted, rather than rebuilt per environment?
- Does a red pipeline actually block merge and deploy (required checks, not advisory)?
- Are stages ordered fail-fast, with cheap checks before expensive ones?
- Is the full feedback loop fast enough (~10 min) that developers trust it?

## Related

- `knowledge/cicd/01-ci-cd-fundamentals.md`
- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/05-quality-gates.md`
- `knowledge/cicd/10-deployment.md`
- `knowledge/cicd/100-common-antipatterns.md`
