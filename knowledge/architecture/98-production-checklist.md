---
id: architecture/98-production-checklist
topic: architecture
slug: production-checklist
title: "Architecture Production Checklist"
type: doc
order: 98
status: ready
tags: [architecture, production-checklist]
related: [architecture/16-high-availability, architecture/17-fault-tolerance, architecture/18-observability, architecture/24-deployment, architecture/99-ai-review-checklist]
when_to_use: "Read before promoting any service or significant change to production."
---
# Architecture Production Checklist

## Purpose

This is the go/no-go checklist for putting an architecture into production. Every item is
a verifiable yes/no an agent or reviewer can confirm against the running system or its
config — not advice, but a gate. If an item is "no", the honest answer is either fix it or
consciously accept the risk in writing. Use it alongside the
[AI review checklist](99-ai-review-checklist.md), which reviews the design; this one
reviews operational readiness.

## Why It Matters

Systems fail in production for boringly repetitive reasons: no timeout, no health check, a
secret in a config file, an unrun migration, no way to roll back. Each is trivially
preventable and each has taken down real systems. A checklist turns "we probably handled
that" into "we verified that", and moves the cost of finding a gap from 3 a.m. during an
outage to five minutes during review.

## Reliability & Fault Tolerance

- [ ] Every outbound network call has a **timeout** and a bounded **retry** with backoff
  and jitter (see [fault tolerance](17-fault-tolerance.md)).
- [ ] Retries are only applied to **idempotent** operations, or protected by an
  idempotency key, so a retry cannot double-charge or double-write.
- [ ] A **circuit breaker** or equivalent protects calls to any dependency that can fail.
- [ ] The service degrades gracefully when a non-critical dependency is down (fallback,
  cached data, or feature disable) rather than failing the whole request.
- [ ] There is **no single point of failure** in the critical path, or the SPOF is
  documented and accepted (see [high availability](16-high-availability.md)).
- [ ] Load and failure modes have been tested (load test, dependency-kill / chaos test).

## Scalability & Performance

- [ ] The service is **stateless**, or its state is externalized, so it can scale
  horizontally (see [scalability](13-scalability.md)).
- [ ] Resource **limits and requests** (CPU, memory) are set; the service does not rely on
  unbounded resources.
- [ ] Connection pools, thread pools, and queues have **explicit bounds**.
- [ ] Expensive or hot read paths have a defined [caching strategy](19-caching-strategies.md)
  with explicit TTL and invalidation.
- [ ] Latency and throughput targets (SLOs) are defined and measured against real traffic.

## Data & State

- [ ] Schema migrations are **backward-compatible** and safe to run while the old version
  is still live (expand/contract, no destructive change coupled to deploy).
- [ ] There is a tested **backup** and a tested **restore** procedure — an untested backup
  is not a backup.
- [ ] Data retention, deletion, and PII handling meet the applicable
  [security](15-security.md) and compliance requirements.
- [ ] Transactions and consistency boundaries are explicit; no cross-service write assumes
  distributed ACID it does not have.

## Observability

- [ ] Structured **logs** (with correlation/trace IDs), **metrics**, and **traces** are
  emitted for every request path (see [observability](18-observability.md)).
- [ ] A **health/readiness** endpoint distinguishes "alive" from "ready to serve traffic".
- [ ] **Alerts** exist on the SLOs and on saturation (error rate, latency, resource use),
  and every alert is actionable — no alert without a runbook.
- [ ] Dashboards let an on-call engineer answer "is it healthy?" in under a minute.

## Security

- [ ] No secrets in code, images, or committed config; all secrets come from a **secrets
  manager** and are rotatable.
- [ ] All traffic is encrypted in transit (TLS) and sensitive data encrypted at rest.
- [ ] Every endpoint enforces authentication and authorization; nothing is public by
  accident.
- [ ] Dependencies are scanned for known vulnerabilities and the image runs as a
  non-root user.

## Deployment & Operations

- [ ] Deploys are automated, repeatable, and support a **rollback** (blue/green, canary,
  or versioned rollback — see [deployment](24-deployment.md)).
- [ ] Configuration is externalized per environment; the same artifact is promoted across
  environments, not rebuilt.
- [ ] Graceful shutdown drains in-flight requests before the process exits.
- [ ] A **runbook** documents how to deploy, roll back, and respond to the top failure
  modes.
- [ ] Ownership and on-call are assigned; there is a named owner for this service.

## AI Review Checklist

- Does every external call in the diff have a timeout, bounded retry, and idempotency
  where needed?
- Is the service horizontally scalable (stateless or externalized state)?
- Are logs, metrics, traces, and a readiness probe present and wired to alerts?
- Are all secrets sourced from a manager and absent from the repo and image?
- Is the migration backward-compatible and the deploy rollback-capable?
- Is there a runbook and a named owner before this ships?

## Related

- `knowledge/architecture/16-high-availability.md`
- `knowledge/architecture/17-fault-tolerance.md`
- `knowledge/architecture/18-observability.md`
- `knowledge/architecture/24-deployment.md`
- `knowledge/architecture/99-ai-review-checklist.md`
