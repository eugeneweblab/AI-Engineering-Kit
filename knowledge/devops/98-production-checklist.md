---
id: devops/98-production-checklist
topic: devops
slug: production-checklist
title: "DevOps Production Checklist"
type: doc
order: 98
status: ready
tags: [devops, production-checklist]
related: [devops/07-deployment-strategies, devops/17-secrets-management, devops/18-disaster-recovery, devops/25-incident-management, devops/99-ai-review-checklist]
when_to_use: "Read before promoting any service, pipeline, or infrastructure change to production."
---
# DevOps Production Checklist

## Purpose

This is the go/no-go checklist for putting a change into production through your delivery
pipeline. Every item is a verifiable yes/no an agent or reviewer can confirm against the
pipeline, the infrastructure config, or the running system — not advice, but a gate. If an
item is "no", the honest answer is either fix it or consciously accept the risk in writing.
Use it alongside the [AI review checklist](99-ai-review-checklist.md), which reviews the
delivery design; this one reviews operational readiness.

## Why It Matters

Deployments fail for boringly repetitive reasons: no rollback, a secret baked into an
image, an unrun migration, a health check that lies, no alert on the thing that broke. Each
is trivially preventable and each has taken down real systems. A checklist turns "we
probably handled that" into "we verified that", and moves the cost of finding a gap from an
outage to a five-minute review.

## Build & Artifact

- [ ] A single **immutable artifact** is built once in CI and promoted unchanged across
  environments — not rebuilt per environment (see [build pipelines](05-build-pipelines.md)).
- [ ] The artifact is **versioned and pinned** by digest/tag; the exact commit it was built
  from is traceable.
- [ ] The build is **reproducible**: dependencies are locked, and the pipeline runs from a
  clean checkout, not a developer's machine.
- [ ] Container images run as a **non-root** user and are scanned for known vulnerabilities.

## Configuration & Secrets

- [ ] Configuration is **externalized per environment**; the same artifact reads different
  injected config (see [configuration management](09-configuration-management.md)).
- [ ] No secrets in code, images, or committed config; all secrets come from a **secrets
  manager** and are rotatable (see [secrets management](17-secrets-management.md)).
- [ ] Secret and config changes are versioned and applied by the pipeline, not hand-edited
  on live hosts.

## Deployment & Rollback

- [ ] The deploy is **automated and repeatable** and supports a tested **rollback**
  (blue/green, canary, or versioned revert — see [deployment strategies](07-deployment-strategies.md)).
- [ ] A **health/readiness** check gates the deploy and distinguishes "alive" from "ready to
  serve traffic"; a failing check blocks or auto-reverts.
- [ ] **Graceful shutdown** drains in-flight requests before the old version exits.
- [ ] Database **migrations are backward-compatible** and safe to run while the previous
  version is still live (expand/contract, decoupled from the deploy).
- [ ] The change can be rolled back **independently**, without a coordinated multi-service
  deploy.

## Observability & Alerting

- [ ] Structured **logs** with correlation/trace IDs, **metrics**, and **traces** are
  emitted for the request path (see [observability](13-observability.md)).
- [ ] **Alerts** exist on the SLOs and on saturation (error rate, latency, resource use),
  and every alert is actionable with a runbook (see [alerting](15-alerting.md)).
- [ ] A dashboard lets on-call answer "did this deploy make things worse?" in under a
  minute.
- [ ] Deploy events are recorded so a regression can be correlated to the change that caused
  it.

## Reliability & Recovery

- [ ] Resource **limits and requests** (CPU, memory) are set; nothing relies on unbounded
  resources.
- [ ] There is a tested **backup and restore** — an untested backup is not a backup (see
  [disaster recovery](18-disaster-recovery.md)).
- [ ] The service degrades gracefully when a non-critical dependency is down, rather than
  failing every request.
- [ ] Failure and load behavior have been tested before this reaches production.

## Ownership & Process

- [ ] The change passed all **quality gates** (tests, lint, security scan) and none were
  skipped or marked flaky-ignore (see [quality gates](23-quality-gates.md)).
- [ ] A **runbook** documents how to deploy, roll back, and respond to the top failure
  modes (see [incident management](25-incident-management.md)).
- [ ] **Ownership and on-call** are assigned; there is a named owner for this service.

## AI Review Checklist

- Is one immutable artifact built once and promoted, with config injected per environment?
- Are all secrets sourced from a manager and absent from the repo and image?
- Is the deploy automated with a tested, independent rollback and a real health check?
- Is the migration backward-compatible and decoupled from the deploy?
- Are logs, metrics, traces, and actionable alerts present and wired before release?
- Is there a runbook, a tested restore, and a named owner before this ships?

## Related

- `knowledge/devops/07-deployment-strategies.md`
- `knowledge/devops/17-secrets-management.md`
- `knowledge/devops/18-disaster-recovery.md`
- `knowledge/devops/25-incident-management.md`
- `knowledge/devops/99-ai-review-checklist.md`
