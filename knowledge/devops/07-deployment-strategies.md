---
id: devops/07-deployment-strategies
topic: devops
slug: deployment-strategies
title: "Deployment Strategies"
type: doc
order: 7
status: ready
tags: [devops, deployment-strategies, preStop, maxUnavailable, maxSurge, SIGTERM]
related: [devops/06-release-management, devops/11-orchestration, devops/12-monitoring, devops/19-high-availability, devops/25-incident-management]
when_to_use: "Read before choosing how a new version replaces the running one, or reviewing a rollout that risks downtime."
---
# Deployment Strategies

## Purpose

This document defines how a released version replaces the running one with controlled
risk: rolling, blue-green, canary, and the health checks and rollback that make any of
them safe. It is written so an agent can pick and implement a rollout that does not drop
traffic and can be reversed fast.

Deployment is the **mechanism** half of shipping; [release management](06-release-management.md)
is the **decision** half. This doc assumes you already have an identified, approved
artifact and asks only: how do we swap it in without hurting users?

## Why It Matters

The moment of swapping versions is when most user-visible outages happen — connections
drop, a bad build reaches 100% of traffic at once, or a schema and code go out of sync.
A deployment strategy exists to shrink the *blast radius* and *time-to-recover* of a bad
release. The difference between "we deployed a bug to 1% and rolled back in 90 seconds"
and "every user hit the bug for 20 minutes" is entirely the strategy you chose before
anything went wrong.

## Core Principles

- **No hard cutover with in-flight requests.** New and old versions must coexist briefly;
  drain connections instead of killing them.
- **Every rollout is guarded by health checks.** A deploy that cannot tell healthy from
  unhealthy cannot be automated and cannot auto-rollback.
- **Expose change to a small blast radius first.** Canary a fraction of traffic, watch
  real metrics, then widen. Confidence should be earned from production, not staging alone.
- **Rollback must be at least as fast as roll-forward.** If undoing is slower than doing,
  you will ride out incidents you should have aborted.
- **Decouple database migrations from code swaps.** Schema changes must be
  backward-compatible so old and new code run against the same database simultaneously.

## Best Practices

- **Rolling update** (default for stateless services): replace instances in batches with
  a health gate between batches. Set `maxUnavailable` low to preserve capacity and a
  bounded `maxSurge`. Simple and resource-cheap; the trade-off is a mixed-version window.
- **Blue-green**: run the new version (green) fully alongside old (blue), switch the
  router, keep blue warm for instant rollback. Fast, clean rollback; the cost is double
  the infrastructure during the switch.
- **Canary**: route a small percentage to the new version, compare error rate/latency
  against the baseline, promote automatically only if metrics hold. Best risk control;
  the cost is the automation and metrics plumbing to judge the canary.
- Use **expand/contract (parallel change)** for schema: add the new column/table
  (expand), deploy code that writes both and reads new, backfill, then drop the old
  (contract) in a *later* release. Never ship a migration that the currently-running
  code cannot tolerate.
- Make health checks meaningful: **readiness** gates traffic (don't route until
  dependencies are up), **liveness** restarts a wedged process. A readiness probe that
  only returns 200 statically proves nothing.
- Always drain: on shutdown, stop accepting new requests, finish in-flight ones, then
  exit. Wire this to the orchestrator's `preStop` / `SIGTERM` grace period.

## Examples

**Good Example** — canary with an automated metric gate and abort

```yaml
# Argo Rollouts: shift traffic in steps and roll back automatically on bad metrics.
strategy:
  canary:
    steps:
      - setWeight: 5           # expose only 5% of traffic first — small blast radius
      - pause: { duration: 5m }
      - analysis:              # compare canary vs. baseline on REAL production metrics
          templates: [{ templateName: error-rate }]
          # If error rate exceeds threshold, the rollout aborts and reverts automatically.
      - setWeight: 50
      - pause: { duration: 5m }
      - setWeight: 100         # full promotion only after the canary earned it
```

**Bad Example** — recreate strategy: kill everything, then start new

```yaml
# Kubernetes: "Recreate" terminates ALL old pods before ANY new pod is ready.
spec:
  strategy:
    type: Recreate            # guaranteed downtime window between old and new
  template:
    spec:
      containers:
        - name: api
          image: api:2.4.0
          # No readiness probe: traffic is sent the instant the container starts,
          # before the app can serve — users hit connection errors during startup.
```

## Common Mistakes

- Using `Recreate`/hard cutover for a service that must stay available.
- No readiness probe, so traffic hits instances before they can serve.
- Shipping a destructive migration (drop/rename column) in the same release as the code
  that depends on it — old pods crash during the rollout window.
- Canarying by percentage but never actually comparing metrics, so the canary is theater.
- No connection draining, so every deploy resets in-flight requests.
- A rollback path that requires a rebuild, making it slower than the forward deploy.

## Production Tips

- Automate abort: wire canary analysis to your real SLO metrics (error rate, p99
  latency) so a bad release rolls itself back without a human in the loop.
- Keep the previous version deployable for the whole incident window, not just minutes.
- Test the drain path under load; graceful shutdown that works when idle often fails
  under real connection volume.
- For stateful systems, prefer blue-green with a tested data cutover over in-place
  rolling updates.

## AI Review Checklist

- Does the strategy avoid a full-downtime cutover for an availability-sensitive service?
- Is there a readiness probe gating traffic and a liveness probe for stuck processes?
- Are database migrations backward-compatible (expand/contract), not destructive-in-place?
- Is traffic exposed incrementally (canary/rolling) with a defined promotion criterion?
- Can the deployment roll back at least as fast as it rolled forward?
- Is graceful connection draining wired to shutdown (SIGTERM/preStop)?

## Related

- `knowledge/devops/06-release-management.md`
- `knowledge/devops/11-orchestration.md`
- `knowledge/devops/12-monitoring.md`
- `knowledge/devops/19-high-availability.md`
- `knowledge/devops/25-incident-management.md`
