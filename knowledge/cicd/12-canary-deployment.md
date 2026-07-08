---
id: cicd/12-canary-deployment
topic: cicd
slug: canary-deployment
title: "Canary Deployment"
type: doc
order: 12
status: ready
tags: [cicd, canary-deployment]
related: [cicd/11-blue-green-deployment, cicd/13-feature-flags, cicd/14-rollbacks, cicd/23-monitoring, cicd/10-deployment]
when_to_use: "Read before rolling out a release to a subset of production traffic and deciding whether to promote it."
---
# Canary Deployment

## Purpose

This document defines how to release a new version to a small slice of real production
traffic, measure it against the current version, and then either promote it to 100% or
abort. It is written so an agent can design or review a canary rollout that catches
regressions with minimal blast radius.

A canary differs from [blue-green](11-blue-green-deployment.md): blue-green flips *all*
traffic at once between two full environments, while a canary shifts traffic
*gradually* (1% → 10% → 50% → 100%) and gates each step on live metrics. Use a canary
when you want to observe real behavior before full commitment.

## Why It Matters

Staging never fully reproduces production: real traffic mix, data volume, cache state,
and third-party latency only exist in prod. A canary is the cheapest way to test the
one environment that matters without betting every user on it. If the new version has a
memory leak, a slow query, or a broken code path on real data, a canary exposes it while
only 1% of users are affected — and an automated gate rolls it back before a human even
notices. The alternative, a full rollout, turns a subtle regression into a total outage.

## Core Principles

- **Shift traffic in small, reversible steps.** Each increment must be undoable in
  seconds by routing traffic back to the stable version. Never jump straight to a large
  percentage.
- **Gate promotion on metrics, not on time.** "It's been 10 minutes, promote" is not a
  gate. Compare error rate, latency, and saturation of the canary against the baseline.
- **Compare canary to baseline, not to history.** Both versions must serve traffic
  simultaneously so you compare under identical conditions. Yesterday's numbers are not
  a valid control.
- **Automate the abort.** A rollback that depends on a human watching a dashboard at 3am
  will fail. The pipeline must halt and revert on threshold breach.
- **Keep versions compatible.** During a canary, old and new run at once against the
  same database. Schema and API changes must be backward compatible (expand/contract).

## Best Practices

- Start at 1–5% of traffic, hold long enough to gather statistically meaningful signal,
  then step up (5% → 25% → 50% → 100%). Match hold time to your traffic volume.
- Define explicit SLO-based gates *before* rollout: e.g. canary p99 latency ≤ 110% of
  baseline, error rate ≤ baseline + 0.1%. Encode them, don't eyeball them.
- Route by weight at the load balancer, service mesh (Istio, Linkerd), or ingress —
  keep routing config in version control, not a manual console click.
- Ensure sticky sessions or idempotency so a user bounced between versions mid-flow does
  not corrupt state.
- Emit a version label on every metric and log line so canary and baseline are
  separable in your observability stack.
- Automatically roll back on gate breach and page on-call; never auto-promote a canary
  that only "looks fine."
- Bake (hold at partial traffic) long enough to catch slow leaks — memory, connection
  pools, disk — not just immediate 500s.

## Examples

**Good Example** — progressive rollout gated on live analysis (Argo Rollouts)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: checkout
spec:
  strategy:
    canary:
      steps:
        - setWeight: 5           # start tiny: only 5% of users at risk
        - pause: { duration: 5m } # bake to catch latency/error regressions
        - analysis:              # automated gate compares canary vs baseline
            templates: [{ templateName: success-rate }]
        - setWeight: 25
        - pause: { duration: 5m }
        - setWeight: 50
        - pause: { duration: 5m }
        # reaching here promotes to 100%; any failed analysis auto-aborts + rolls back
```

**Bad Example** — time-based promotion with no comparison

```bash
# Anti-pattern: shift all traffic, sleep, assume success
kubectl set image deploy/checkout app=checkout:v2   # 100% at once — no canary at all
sleep 600                                            # a timer is not a health signal
echo "Deployed v2"                                   # no metrics compared, no rollback path
# A regression now affects every user, and nothing reverts it automatically.
```

## Common Mistakes

- Promoting on elapsed time instead of on a metric comparison against the baseline.
- Sending too little traffic to the canary to reach statistical significance, so a real
  regression hides in the noise.
- Comparing canary metrics to yesterday's numbers instead of the concurrently running
  stable version.
- Shipping a non-backward-compatible schema change, so old and new versions cannot
  safely share the database during the rollout.
- No automated rollback, so a bad canary sits degrading users until a human intervenes.
- Ignoring slow-burn failures (memory, file descriptors) by baking for seconds, not
  long enough to reveal them.

## Production Tips

- Weight canary analysis by traffic that actually exercises the change; a canary that
  only sees health-check pings proves nothing.
- Combine canaries with [feature flags](13-feature-flags.md): deploy dark, then use the
  flag to control exposure independent of the traffic weight.
- Record every canary decision (metrics, verdict, who/what promoted) for post-incident
  review.

## AI Review Checklist

- Does the rollout shift traffic in small, reversible increments rather than all at once?
- Is promotion gated on canary-vs-baseline metrics (error rate, latency, saturation)?
- Is rollback automated on gate breach, not dependent on a human watching?
- Are canary and baseline running concurrently and comparably (same conditions)?
- Are schema and API changes backward compatible for the mixed-version window?
- Is every metric/log labeled with version so the two can be compared?
- Is the bake time long enough to surface slow-burn regressions, not just immediate errors?

## Related

- `knowledge/cicd/11-blue-green-deployment.md`
- `knowledge/cicd/13-feature-flags.md`
- `knowledge/cicd/14-rollbacks.md`
- `knowledge/cicd/23-monitoring.md`
- `knowledge/cicd/10-deployment.md`
