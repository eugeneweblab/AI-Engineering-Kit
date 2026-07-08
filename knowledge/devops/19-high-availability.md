---
id: devops/19-high-availability
topic: devops
slug: high-availability
title: "High Availability"
type: doc
order: 19
status: ready
tags: [devops, high-availability]
related: [devops/18-disaster-recovery, devops/20-scalability, devops/11-orchestration, devops/07-deployment-strategies]
when_to_use: "Read before designing redundancy, health checks, failover, or SLA targets for a production service."
---
# High Availability

## Purpose

This document defines how to keep a service serving requests through the failures that
happen constantly in real systems: a crashed process, a dead node, a slow dependency, a
lost availability zone. It is written so an agent can design or review an architecture
that degrades gracefully instead of collapsing at the first fault.

High availability (HA) answers "how do we stay up when a *part* of the system fails?".
It is distinct from [disaster recovery](18-disaster-recovery.md), which recovers *after*
a catastrophe, and from [scalability](20-scalability.md), which handles load. HA is about
tolerating faults with no or minimal downtime.

## Why It Matters

Every component you depend on will fail — the only variables are when and how often. At
scale, "rare" hardware failures happen daily. A system with a single instance of anything
inherits that thing's full failure rate as downtime. HA is not gold-plating; it is the
baseline that turns a routine node death from an outage into a non-event. Availability
also compounds: chaining ten 99.9% dependencies in series yields ~99% — the math punishes
hidden single points of failure hard.

## Core Principles

- **Eliminate single points of failure (SPOF).** Every tier — app, database, cache, load
  balancer, DNS — needs redundancy. One instance of anything is a scheduled outage.
- **Redundancy only helps if failover is automatic and tested.** A standby nobody has
  failed over to is a SPOF with extra cost. Prove failover works before you rely on it.
- **Health checks must reflect real readiness.** A process that is up but cannot reach its
  database is not healthy. Route traffic only to instances that can actually serve.
- **Design for graceful degradation.** When a non-critical dependency fails, shed that
  feature and keep the core path alive rather than failing the whole request.
- **Availability is a budget, not a wish.** Pick an SLO, compute the allowed downtime, and
  spend the resulting error budget deliberately (see [SRE principles](27-sre-principles.md)).

## Best Practices

- Run **N+1 (or more) redundancy** across **multiple availability zones**. A single-AZ
  deployment fails entirely when that AZ does. The cost is cross-AZ traffic and data sync.
- Put stateless services behind a **load balancer with health-check-based routing**, and
  keep them stateless so any instance can serve any request.
- For databases, use **replication with automatic failover** (e.g. Patroni, managed
  multi-AZ RDS). Verify the promotion path and the application's reconnect behavior.
- Separate **liveness** (is the process alive?) from **readiness** (can it serve now?).
  Failing readiness drains traffic without killing the pod; failing liveness restarts it.
- Add **timeouts, retries with backoff+jitter, and circuit breakers** on every network
  call. A dependency that hangs must not hang your whole thread pool.
- Use **bulkheads / connection-pool limits** so one slow dependency cannot exhaust
  resources shared by healthy paths.
- Deploy with **rolling or blue-green** strategies and **PodDisruptionBudgets** so
  maintenance never drops below the minimum healthy replica count.
- **Test failure**: run game days / chaos experiments (kill a node, block an AZ) to prove
  the system behaves as designed under fault.

## Examples

**Good Example** — real readiness check plus bounded, resilient dependency call

```yaml
# Kubernetes: liveness restarts a hung process; readiness drains a pod that
# temporarily cannot serve (e.g. lost DB) WITHOUT killing it.
livenessProbe:
  httpGet: { path: /healthz, port: 8080 }   # process is alive
  periodSeconds: 10
readinessProbe:
  httpGet: { path: /readyz, port: 8080 }     # deps reachable → safe to route traffic
  periodSeconds: 5
```

```ts
// Every network call is bounded and fails fast; a slow dependency cannot pile up.
const res = await circuitBreaker.run(() =>
  fetch(url, { signal: AbortSignal.timeout(2000) }) // hard timeout, no unbounded hang
);
// Non-critical feature degrades instead of failing the whole request.
const recs = await getRecommendations().catch(() => []); // empty list, page still loads
```

**Bad Example** — SPOF plus a health check that lies

```ts
// Single instance, single AZ: this node's failure IS the outage.
app.get("/healthz", (_req, res) => res.send("ok")); // always "ok" even if DB is down
                                                     // → LB keeps routing to a broken pod

async function getUser(id: string) {
  return db.query("SELECT * FROM users WHERE id = $1", [id]); // no timeout:
}                                                             // a hung DB hangs every request
```

## Common Mistakes

- A "healthy" check that returns 200 without verifying downstream dependencies.
- Redundancy on paper but failover never tested — it fails the first time it's needed.
- Deploying replicas in a single availability zone, so an AZ loss is a full outage.
- No timeouts on network calls, letting one slow dependency exhaust all threads.
- Retrying without backoff+jitter, turning a blip into a self-inflicted retry storm.
- Sticky in-memory session state, so losing one node logs out a slice of users.
- Treating the load balancer, DNS, or message broker as if it cannot itself fail.

## Production Tips

- Measure availability from the **user's perspective** (successful requests / total), not
  from whether processes are running. Users experience errors, not uptime.
- Alert on **error budget burn rate**, not raw error count, so paging tracks SLO risk.
- Keep a **minimum viable degraded mode** documented: which features you shed, in what
  order, to protect the core path under partial failure.

## AI Review Checklist

- Is every tier (app, DB, cache, LB, DNS) redundant across at least two AZs?
- Has automatic failover been tested, not just configured?
- Do readiness checks verify real dependencies, and are liveness/readiness separated?
- Does every network call have a timeout, backoff+jitter retry, and a circuit breaker?
- Are services stateless (or state externalized) so any instance can serve any request?
- Is there a defined SLO with an error budget and burn-rate alerting?
- Does the system degrade gracefully when a non-critical dependency fails?

## Related

- `knowledge/devops/18-disaster-recovery.md`
- `knowledge/devops/20-scalability.md`
- `knowledge/devops/11-orchestration.md`
- `knowledge/devops/07-deployment-strategies.md`
- `knowledge/devops/27-sre-principles.md`
