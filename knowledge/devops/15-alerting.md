---
id: devops/15-alerting
topic: devops
slug: alerting
title: "Alerting"
type: doc
order: 15
status: ready
tags: [devops, alerting]
related: [devops/12-monitoring, devops/13-observability, devops/25-incident-management, devops/26-postmortems, devops/27-sre-principles]
when_to_use: "Read before writing or reviewing an alert rule, on-call routing, or escalation policy."
---
# Alerting

## Purpose

This document defines how to turn a monitoring signal into a page that a human should
act on — and, just as important, how to *not* page for everything else. It covers what
deserves to wake someone up, how to write a rule that fires precisely, and how to keep
on-call sustainable. It is written so an agent creates alerts that catch real incidents
without training the team to ignore them.

Alerting sits on top of [monitoring](12-monitoring.md) and feeds
[incident management](25-incident-management.md). An alert is a promise: "this needs a
human, now." Every alert that breaks that promise erodes trust in all of them.

## Why It Matters

The failure mode of alerting is not too few alerts — it is too many. **Alert fatigue**
is the single most common cause of missed incidents: when a pager fires ten times a
night for things that self-resolve, responders mute it, and the eleventh alert — the
real outage — is ignored. Every noisy alert has a cost paid in the responder's trust and
sleep. A good alerting system is ruthlessly small: it pages only on user-facing harm
that a human can fix right now, and routes everything else to a ticket or a dashboard.
The metric that matters is not coverage; it is the ratio of actionable to total pages.

## Core Principles

- **Page on symptoms, ticket on causes.** A page must mean a user is being hurt (or
  imminently will be). Alert on the SLO burn — "checkout error rate above budget" — not
  on "CPU at 80%". CPU is a dashboard concern until it breaks a symptom.
- **Every page must be actionable.** If the responder's only move is to acknowledge and
  wait, it should not have paged. Ask of each alert: "what will a human *do* at 3 a.m.?"
  If there is no answer, downgrade it.
- **Alert on SLO burn rate, not raw thresholds.** Burn-rate alerts fire faster for
  severe problems and slower for minor ones, matching urgency to impact. A fixed
  threshold either pages constantly or misses slow burns.
- **Severity maps to response, not to feeling.** Page = act now. Ticket = act this week.
  FYI = no notification. Miscategorizing is how fatigue starts.
- **An alert without a runbook is half-built.** The page must link to what to check and
  what to do first.

## Best Practices

- Base critical alerts on **multi-window, multi-burn-rate** SLO rules: a fast window
  (e.g. 1h) catches acute outages, a slow window (e.g. 6h) catches gradual erosion.
  This is the SRE-standard way to page precisely.
- **Require a "for" duration** so a single scrape blip does not page. Alert only when the
  condition holds for a sustained window (e.g. `for: 5m`).
- **Route by severity and ownership.** Pages go to the owning team's on-call; warnings go
  to a queue. Never send everything to one firehose channel.
- Include in every alert: **what broke, how bad, since when, and a runbook link**. A page
  that just says "HighErrorRate" wastes the responder's first five minutes.
- **Set escalation**: if the primary does not ack within N minutes, escalate to
  secondary, then to the incident channel. Silence is not acknowledgment.
- **Deduplicate and group** related alerts into one incident so a downstream failure
  does not send fifty pages for one root cause.
- **Delete alerts that never fire or always get ignored.** Review pager volume regularly
  and prune; an alert no one acts on is negative value.

## Examples

**Good Example** — SLO burn-rate page with duration and runbook (Prometheus rule)

```yaml
# Pages only when error budget burns fast enough to matter, sustained for 5m.
# Two windows: fast burn (acute outage) and confirmation window (not a blip).
- alert: CheckoutErrorBudgetBurn
  expr: |
    (
      sum(rate(http_requests_total{route="/checkout",status=~"5.."}[5m]))
      / sum(rate(http_requests_total{route="/checkout"}[5m]))
    ) > (14.4 * 0.001)                       # 14.4x burn of a 99.9% SLO
    and
    (
      sum(rate(http_requests_total{route="/checkout",status=~"5.."}[1h]))
      / sum(rate(http_requests_total{route="/checkout"}[1h]))
    ) > (14.4 * 0.001)                       # second window confirms it is real
  for: 5m                                     # ignore single-scrape spikes
  labels: { severity: page, team: checkout }  # routed to the owning on-call
  annotations:
    summary: "Checkout burning error budget 14.4x (p=high)"
    runbook: "https://runbooks/checkout-5xx"  # responder knows what to do
```

**Bad Example** — noisy cause-based threshold that pages for nothing actionable

```yaml
# Anti-pattern: pages on a raw resource metric with no duration and no runbook.
- alert: HighCPU
  expr: node_cpu_usage > 0.8   # CPU at 80% is normal under load; no user is harmed
  # No `for:` -> fires on every transient spike. Severity/routing missing -> lands in a
  # firehose channel. No runbook -> responder acks and shrugs. Result: everyone mutes it,
  # and the real outage alert gets muted with it.
  labels: { severity: page }
```

## Common Mistakes

- Paging on causes (CPU, memory, disk) instead of user-facing symptoms.
- Fixed-threshold alerts with no `for:` duration, firing on transient blips.
- No runbook link, so every page starts from zero.
- One firehose channel with no severity routing or ownership.
- No escalation, so an unacknowledged page silently goes unhandled.
- Fifty pages for one root cause because alerts are not grouped/deduplicated.
- Keeping alerts that never fire or are always ignored, feeding fatigue.

## Production Tips

- Track **alert volume and actionability** as a metric. If the actionable ratio drops,
  fix the alerts before adding more.
- Every incident [postmortem](26-postmortems.md) should ask: did an alert fire, too late,
  too early, or not at all? Tune rules from real incidents.
- Test alert *routing* periodically (a synthetic page) so you discover a broken pager
  before a real outage does.

## AI Review Checklist

- Does every page correspond to user-facing harm a human can act on right now?
- Are critical alerts based on SLO burn rate, not raw resource thresholds?
- Does each alert have a `for:` duration to suppress transient blips?
- Is there a runbook link and clear "what broke / how bad / since when" in the alert?
- Is routing by severity and ownership, with escalation on no-ack?
- Are related alerts grouped so one root cause does not page many times?
- Have alerts that never fire or are always ignored been pruned?

## Related

- `knowledge/devops/12-monitoring.md`
- `knowledge/devops/13-observability.md`
- `knowledge/devops/25-incident-management.md`
- `knowledge/devops/26-postmortems.md`
- `knowledge/devops/27-sre-principles.md`
