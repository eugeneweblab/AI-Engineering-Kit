---
id: testing/25-production-testing
topic: testing
slug: production-testing
title: "Production Testing"
type: doc
order: 25
status: ready
tags: [testing, production-testing]
related: [testing/26-observability, testing/21-cicd, testing/16-load-testing, testing/04-e2e-testing, testing/27-quality-gates]
when_to_use: "Read before validating behavior against the live system: canaries, synthetic checks, feature-flag rollouts, or chaos."
---
# Production Testing

## Purpose

This document covers testing that runs *against or in* the live production system:
synthetic monitors, canary and progressive rollouts, feature-flag gating, shadow
traffic, and controlled fault injection. It complements the pre-merge suite — it does not
replace it. Ship only code that already passed [CI](21-cicd.md); production testing
catches what a staging environment structurally cannot.

The goal is not to test *instead of* before release, but to close the gap between "passes
in CI" and "behaves correctly under real traffic, real data, and real dependencies."

## Why It Matters

Staging lies. It has clean data, no legacy edge cases, a fraction of the traffic, and
mocked third parties. Whole classes of defects — data-shape surprises, latency under
concurrency, a dependency that degrades at scale, a config that differs by environment —
only appear in production. Testing in production, done safely, turns those surprises into
detected, bounded, reversible events instead of outages. Done unsafely, it *is* the
outage. The discipline is entirely about limiting blast radius.

## Core Principles

- **Blast radius first.** Never expose a change to 100% of users at once. Ring it:
  internal, then canary, then progressive percentages, with an automated halt.
- **Every production test must be reversible.** A feature flag you can flip and a rollout
  you can roll back are prerequisites, not nice-to-haves.
- **Guard real users' data.** Synthetic tests must not create, mutate, or bill real
  customer records; use dedicated test tenants and clearly marked synthetic accounts.
- **Automate the abort.** A canary is only safe if error-rate and latency thresholds
  trigger an automatic rollback without a human in the loop.
- **Observe, don't assume.** Production testing is only meaningful if you can *see* the
  result — it depends entirely on [observability](26-observability.md).

## Best Practices

- Run **synthetic monitors**: scripted critical-path journeys (login, checkout) executed
  every few minutes from outside, alerting when they fail or slow down.
- Roll out behind **feature flags** so deploy and release are decoupled. Enable for
  internal users, then a canary cohort, then ramp, watching SLOs at each step.
- Use **canary deployments**: route a small traffic slice to the new version, compare its
  error rate and latency to the baseline, and auto-promote or auto-rollback.
- **Shadow (mirror) traffic** to a new implementation without returning its response, to
  validate behavior and load without user-visible risk. Never let shadow writes hit real
  state.
- Practice **controlled chaos** (kill an instance, inject latency) in business hours with
  an owner watching, to verify [fault tolerance](../architecture/17-fault-tolerance.md)
  assumptions before an incident forces the test.
- Define **rollback criteria as code**: explicit thresholds (e.g. error rate > 1%, p99 >
  budget) that abort the rollout automatically.
- Tag all synthetic requests (header, user-agent, or account) so they are excluded from
  business metrics and billing.

## Examples

**Good Example** — canary with an automated, threshold-based abort

```yaml
# Progressive rollout: each step must clear the SLO gate before advancing.
canary:
  steps: [5, 25, 50, 100]        # percent of traffic, ramped
  interval: 10m
  analysis:
    metrics:
      - name: error-rate
        threshold: 1%             # abort if the canary exceeds baseline+1%
      - name: p99-latency-ms
        threshold: 400
    onFailure: rollback           # automatic, no human required
```

**Bad Example** — irreversible, all-at-once, unobservable

```yaml
deploy:
  strategy: all-at-once           # 100% of users hit the new code instantly
  migration: drop-and-recreate    # destroys the rollback path
  monitoring: none                # no signal, so failures are invisible
  # A bad build now means a full outage with no way back and no alert.
```

## Common Mistakes

- Treating "it deployed" as "it works" — no synthetic check confirms the path still runs.
- Rolling out to everyone at once because a flag felt like overhead.
- Synthetic tests that create real orders or charge real cards.
- Manual rollback only: by the time a human reacts, the incident is minutes deep.
- Shadowing traffic but letting the shadow path perform real writes or send real emails.
- Running chaos experiments with no owner watching and no defined stop condition.
- No feature flag, so a bad release requires a full redeploy to undo.

## Production Tips

- Keep an explicit, tested rollback runbook; rehearse it, don't discover it mid-incident.
- Expire feature flags — a flag left on forever becomes untested dead branching. Track
  and remove stale flags.
- Correlate synthetic-check failures with recent deploys and flag changes to localize
  cause fast (see [observability](26-observability.md)).

## AI Review Checklist

- Is the change gated behind a feature flag or canary, not shipped to 100% at once?
- Are rollback criteria defined as automated thresholds, not a manual judgment call?
- Do synthetic tests avoid mutating or billing real customer data?
- Is there a synthetic monitor covering the critical path this change touches?
- Can the change be fully reverted (flag off or rollback) without a data migration?
- Does shadow traffic, if used, avoid all real side effects (writes, emails, charges)?
- Are chaos experiments scoped, owned, and bounded by a stop condition?

## Related

- `knowledge/testing/26-observability.md`
- `knowledge/testing/21-cicd.md`
- `knowledge/testing/16-load-testing.md`
- `knowledge/testing/04-e2e-testing.md`
- `knowledge/testing/27-quality-gates.md`
