---
id: cicd/98-production-checklist
topic: cicd
slug: production-checklist
title: "CI/CD Production Checklist"
type: doc
order: 98
status: ready
tags: [cicd, production-checklist]
related: [cicd/09-release-management, cicd/10-deployment, cicd/14-rollbacks, cicd/15-secrets, cicd/23-monitoring]
when_to_use: "Read before promoting a CI/CD pipeline or a release path to production."
---
# CI/CD Production Checklist

## Purpose

A verifiable, yes/no checklist to run before a CI/CD pipeline and its release path are
trusted with production traffic. Each item is concrete and checkable — if you cannot
answer "yes" with evidence, treat it as "no". Group by group, this is what separates a
pipeline that ships safely from one that ships and hopes.

## Why It Matters

Production is where an unpinned dependency, a leaked secret, or a missing rollback stops
being a review comment and becomes an incident. The checklist exists because these gaps
are invisible while everything works — they only surface under the exact conditions
(a bad deploy, a rollback, an audit) where you have no time to fix them.

## Build & Artifact

**Rules:** [Build Stage](03-build-stage.md) · [Artifacts](07-artifacts.md)

- [ ] The pipeline is defined in the repository and changes go through code review.
- [ ] Builds are deterministic: same commit produces the same artifact on any runner.
- [ ] Base images are pinned by digest and actions/plugins by SHA or exact version.
- [ ] Dependencies are installed from a committed lockfile, not resolved fresh.
- [ ] Each commit is built exactly once; the same artifact is promoted across environments.
- [ ] Artifacts are stored in a registry with an immutable, commit-derived tag.

## Test & Quality Gates

**Rules:** [Test Stage](04-test-stage.md) · [Quality Gates](05-quality-gates.md)

- [ ] CI runs on every push and pull request and blocks merge on failure.
- [ ] Unit, integration, and required end-to-end tests all run in the pipeline.
- [ ] Quality gates (coverage threshold, lint, type check) are enforced, not advisory.
- [ ] Flaky tests are quarantined and tracked, not silently retried away.
- [ ] The critical-path pipeline completes within the team's agreed time budget.

## Security

**Rules:** [Security Scanning](06-security-scanning.md) · [Secrets](15-secrets.md)

- [ ] Dependency and container image scanning runs and blocks on critical findings.
- [ ] Static analysis (SAST) and secret scanning run on every change.
- [ ] Secrets are injected at runtime from a secrets manager, never committed or baked in.
- [ ] CI logs are scrubbed of secrets; masked variables are verified as masked.
- [ ] Pipeline credentials use least privilege and short-lived / OIDC tokens where possible.
- [ ] Production deploy permissions are restricted to a protected branch/environment.

## Release & Deployment

**Rules:** [Deployment](10-deployment.md) · [Blue Green Deployment](11-blue-green-deployment.md)

- [ ] Production deploys require an explicit gate (manual approval or protected environment).
- [ ] The deployment strategy (blue-green, canary, rolling) is defined and automated.
- [ ] A one-step, tested rollback exists and has been exercised, not just documented.
- [ ] Database migrations are backward-compatible and decoupled from code deploys.
- [ ] Releases are versioned and each deploy records commit SHA, artifact digest, and actor.

## Observability & Recovery

**Rules:** [Monitoring](23-monitoring.md) · [Rollbacks](14-rollbacks.md)

- [ ] Deployments emit events/annotations visible on dashboards and in logs.
- [ ] Health checks and readiness probes gate traffic to a new version.
- [ ] Alerts fire on error-rate and latency regressions tied to a deploy.
- [ ] Post-deploy smoke tests run automatically against the live environment.
- [ ] Rollback and on-call runbooks are current and reachable during an incident.

## AI Review Checklist

- Does every unchecked box have an owner and a plan, or is the release blocked?
- Are "yes" answers backed by evidence in the pipeline config, not assumptions?
- Is the rollback path verified end-to-end, not merely described?
- Are secrets absent from both the repository and the build logs?

## Related

- `knowledge/cicd/09-release-management.md`
- `knowledge/cicd/10-deployment.md`
- `knowledge/cicd/14-rollbacks.md`
- `knowledge/cicd/15-secrets.md`
- `knowledge/cicd/23-monitoring.md`
