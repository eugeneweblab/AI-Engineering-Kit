---
id: devops/27-sre-principles
topic: devops
slug: sre-principles
title: "SRE Principles"
type: doc
order: 27
status: ready
tags: [devops, sre-principles]
related: [devops/25-incident-management, devops/12-monitoring, devops/13-observability, devops/24-change-management, devops/19-high-availability]
when_to_use: "Read before defining SLOs, error budgets, on-call policy, or deciding how much reliability work a service needs."
---
# SRE Principles

## Purpose

This document defines the core practices of Site Reliability Engineering: how to make
reliability a measured, budgeted engineering concern rather than a vague aspiration. It
is written so an agent can set service objectives, reason about error budgets, and
balance feature velocity against stability using data instead of opinion.

SRE treats operations as a software problem. Its central move is to define reliability
as a *number* users care about (an SLO), measure it, and spend the gap between that
number and 100% as a budget for taking risks. This turns "should we ship?" from an
argument into arithmetic.

## Why It Matters

Two failure modes destroy teams. One is chasing 100% uptime: it is impossible, and each
extra "nine" costs exponentially more while users cannot even perceive the difference.
The other is shipping recklessly until reliability collapses and trust with it. SRE
resolves the tension: it sets an explicit reliability target that is *good enough for
users*, and lets the team spend everything below that target on moving fast. Without an
agreed number, reliability decisions are made by whoever argues loudest in the moment —
usually after an outage, in the wrong direction.

## Core Principles

- **100% is the wrong target.** Pick a reliability level users actually need. The gap
  from 100% is the **error budget** — the amount of unreliability you are permitted to
  spend. See [high availability](19-high-availability.md) for the cost of each nine.
- **SLI → SLO → error budget.** An SLI is a measured indicator (e.g. fraction of
  requests served under 300ms). An SLO is the target for that SLI (e.g. 99.9% over 28
  days). The error budget is `1 − SLO`. Measure the SLI from the user's perspective.
- **Error budgets govern velocity.** Budget remaining → ship features. Budget exhausted
  → the team's priority automatically shifts to reliability until it recovers. This is a
  policy agreed in advance, not a fight during an outage.
- **Toil is a bug.** Manual, repetitive operational work that scales with traffic should
  be automated away. Cap the fraction of time spent on toil (commonly ~50%) so
  engineering keeps happening.
- **Blameless learning.** Reliability improves by fixing systems, not people — see
  [postmortems](26-postmortems.md).

## Best Practices

- Base SLOs on symptoms users experience (latency, error rate, availability of a
  critical journey), not on internal metrics like CPU. A healthy CPU during a checkout
  outage is worthless.
- Set the SLO *just* high enough to keep users happy and no higher. An over-tight SLO
  burns engineering on gains no user notices and leaves no budget to move.
- Alert on **error-budget burn rate**, not on raw thresholds: page fast when the budget
  is being consumed quickly, ticket slowly when it drains gradually. This cuts noise and
  catches real degradation early. See [alerting](15-alerting.md).
- Write an explicit error-budget policy: what happens (feature freeze, reliability
  sprint) when the budget is spent, and who decides.
- Measure and review toil each cycle; convert the most expensive toil into automation.
- Keep on-call sustainable: humane rotation, sane paging volume, and every page should be
  actionable.

## Examples

**Good Example** — user-centric SLO with burn-rate alerting

```yaml
slo:
  service: checkout
  sli: proportion of requests completing < 300ms with 2xx/3xx
  objective: 99.9%           # over rolling 28 days
  # error budget = 0.1% ≈ 40 min/28d. Spend it on shipping; defend it when low.
alerting:
  # WHY burn rate: page only when the budget is draining fast enough to matter.
  - name: fast-burn
    condition: budget_burn_rate_1h > 14   # would exhaust 28d budget in ~2h
    action: page
  - name: slow-burn
    condition: budget_burn_rate_6h > 1
    action: ticket
```

**Bad Example** — vanity target, cause-based noisy alerts

```yaml
slo:
  objective: 100%            # impossible; guarantees permanent "SLO breach"
alerting:
  - condition: cpu > 80%     # a cause, not a symptom — fires when users are fine,
    action: page             # silent when users hurt but CPU is low
  # WHY WRONG: no error budget means no data-driven ship/no-ship decision.
  # 100% target means the team is always "in violation" and stops trusting it.
  # CPU paging trains responders to ignore the pager.
```

## Common Mistakes

- Targeting 100% (or an unjustified number of nines) instead of what users need.
- Defining SLIs on internal causes (CPU, memory) rather than user-facing symptoms.
- Having SLOs but no error-budget *policy*, so nothing changes when the budget is spent.
- Threshold alerts instead of burn-rate alerts, producing noise or blind spots.
- Accepting unbounded toil instead of treating repetitive ops work as a bug to automate.
- Copying Google's exact numbers instead of choosing targets for your own users.

## Production Tips

- Start with one SLO on your most important user journey; expand once it drives behavior.
- Review SLO attainment and budget burn in a regular reliability review, alongside the
  feature roadmap, so the trade-off is explicit.
- Instrument SLIs at the edge closest to the user (load balancer, client) so the number
  reflects real experience, not just backend health.

## AI Review Checklist

- Is each SLO defined on a user-facing symptom, measured from the user's perspective?
- Is the reliability target justified by user need, not set to 100% or an arbitrary nine?
- Is there an error budget and a written policy for what happens when it is exhausted?
- Do alerts fire on budget burn rate rather than raw cause-based thresholds?
- Is toil measured and capped, with the worst offenders being automated?
- Is on-call load sustainable and every page actionable?

## Related

- `knowledge/devops/25-incident-management.md`
- `knowledge/devops/12-monitoring.md`
- `knowledge/devops/13-observability.md`
- `knowledge/devops/24-change-management.md`
- `knowledge/devops/19-high-availability.md`
