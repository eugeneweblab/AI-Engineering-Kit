---
id: cicd/11-blue-green-deployment
topic: cicd
slug: blue-green-deployment
title: "Blue Green Deployment"
type: doc
order: 11
status: ready
tags: [cicd, blue-green-deployment]
related: [cicd/10-deployment, cicd/12-canary-deployment, cicd/14-rollbacks, cicd/16-environments]
when_to_use: "Read before implementing blue-green deploys or choosing a zero-downtime strategy with instant rollback."
---
# Blue Green Deployment

## Purpose

This document defines **blue-green deployment**: running two identical production
environments — *blue* (current) and *green* (next) — and cutting all traffic from one to
the other in a single switch. It is a specific [deployment](10-deployment.md) strategy
chosen when you need **instant, atomic rollback** and a full validation window before
exposing users.

The defining property: release becomes a traffic switch, and rollback is switching back.
No re-deploy, no rebuild, no gradual drain — just flip the router.

## Why It Matters

The riskiest moment in a deploy is the cutover, and the riskiest failure is one you cannot
undo quickly. Blue-green collapses both risks: the new version is fully deployed and
smoke-tested on the green environment *before* it receives any user traffic, and if
anything goes wrong after the switch, you revert by pointing the router back at blue — a
sub-second operation, with the old version still warm and running. Compared to a rolling
deploy, you trade higher cost (two full environments running at once) for the strongest
possible rollback guarantee and a clean pre-flight test surface. That trade is worth it for
high-stakes services where a bad deploy is very expensive and mid-rollout states are hard
to reason about.

## Core Principles

- **Two complete environments, one live.** Blue and green are identical in capacity and
  config; only the router decides which serves users. The cost is ~2x infra during the
  window; the payoff is atomic cutover and rollback.
- **Validate green before the switch.** Run smoke tests and health checks against green
  while it takes zero user traffic. The switch happens only after green is proven.
- **The switch is atomic.** Traffic moves all at once via one router change (load balancer
  target, DNS weight, service selector), so there is no mixed-version window at the edge.
- **Rollback is the reverse switch.** Keep blue running and untouched until green is
  confirmed healthy in production, so reverting is instant and needs no rebuild.
- **State must survive the switch.** The database and other shared state are common to both
  environments, so schema changes must be backward-compatible with both versions.

## Best Practices

- Keep blue fully running for a defined soak period after cutover before decommissioning
  it; that window is your free, instant rollback.
- Point health checks and a real smoke-test suite at green's internal endpoint before
  switching; never switch on "it deployed" alone.
- Make the switch a single declarative change (e.g. flip a Kubernetes Service `selector`,
  update an ALB target group) so it is atomic and auditable.
- Use **expand/contract** migrations so the shared database is compatible with *both* blue
  and green simultaneously — otherwise rollback corrupts or breaks on the schema.
- Drain long-lived connections (WebSockets, streams) gracefully on the old environment
  after the switch, since existing sessions may still be pinned to blue.
- Automate the whole sequence — provision green, deploy, test, switch, soak, retire blue —
  and automate the revert path too.
- Consider cost controls: scale green up just before deploy and blue down after the soak,
  rather than paying for two full stacks continuously.

## Examples

**Good Example** — deploy to green, verify, atomic switch, blue kept for rollback

```yaml
# Kubernetes: one Service selects the live color; deployments are blue and green
# 1. Green is already deployed with the new image, receiving NO user traffic.
# 2. Verify green in isolation before touching the router:
- run: |
    kubectl rollout status deploy/api-green
    ./smoke-test https://green.internal.acme   # must pass before we switch

# 3. Atomic switch: repoint the Service selector from blue to green in one change
- run: kubectl patch service api -p '{"spec":{"selector":{"color":"green"}}}'
    # All new traffic now hits green instantly. Blue is still running, untouched.

# 4. Rollback (if needed) is the reverse patch — sub-second, no rebuild:
#    kubectl patch service api -p '{"spec":{"selector":{"color":"blue"}}}'
# 5. Only after a healthy soak: scale blue down.
```

**Bad Example** — "blue-green" that cannot actually roll back

```bash
# Deploy new version to green
deploy green v2
# Immediately tear down blue to save money — before validating green in prod
destroy blue                          # rollback target is now gone
switch-traffic green                  # switched with NO smoke test against green first
# Shipped a DESTRUCTIVE migration (dropped a column) that v1 needs:
psql -c "ALTER TABLE users DROP COLUMN legacy_flag;"
# Now even if blue still existed, it would crash on the missing column.
# This is a big-bang deploy wearing a blue-green costume: no test gate, no rollback.
```

## Common Mistakes

- Tearing down or reusing blue before green is confirmed healthy, destroying the rollback
  target.
- Switching traffic without smoke-testing green first — you find the bug with real users.
- Shipping a destructive/backward-incompatible migration, so blue can no longer serve and
  rollback is impossible.
- Environments that are not truly identical (different config, capacity, or data), so green
  passes tests but fails under real load.
- Ignoring long-lived connections pinned to blue, dropping active sessions at cutover.
- Using blue-green when a [canary](12-canary-deployment.md) is a better fit — blue-green
  exposes 100% of traffic at once, with no progressive validation on real users.

## Production Tips

- Emit a deploy marker at the switch so alerts correlate to the exact cutover; watch error
  rate and latency for the full soak window before retiring blue.
- Automate an error-rate-triggered auto-revert during the soak, so a bad switch flips back
  without a human in the loop.
- For databases, keep the expand and contract steps in *separate* releases spanning at
  least one full blue-green cycle, so no single deploy can break both colors.
- If two full environments are too costly, prefer canary or rolling; blue-green earns its
  cost only when instant, atomic rollback is a hard requirement.

## AI Review Checklist

- Are blue and green truly identical in image, config, and capacity?
- Is green validated with health checks and smoke tests *before* the traffic switch?
- Is the cutover a single atomic router change, not a gradual per-instance swap?
- Is blue kept running and untouched through a defined soak window for instant rollback?
- Are database migrations backward-compatible with both colors (expand/contract, split
  across releases)?
- Are long-lived connections drained gracefully after the switch?
- Is the revert path automated (ideally auto-triggered on health regression)?

## Related

- `knowledge/cicd/10-deployment.md`
- `knowledge/cicd/12-canary-deployment.md`
- `knowledge/cicd/14-rollbacks.md`
- `knowledge/cicd/16-environments.md`
