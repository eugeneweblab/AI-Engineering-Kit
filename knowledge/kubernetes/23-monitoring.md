---
id: kubernetes/23-monitoring
topic: kubernetes
slug: monitoring
title: "Kubernetes Monitoring"
type: doc
order: 23
status: ready
tags: [kubernetes, monitoring]
related: [kubernetes/21-observability, kubernetes/20-autoscaling, kubernetes/19-resource-management, kubernetes/26-production]
when_to_use: "Read before defining alerts, dashboards, or SLOs for a cluster or workload, or when alerts are noisy, missing, or not actionable."
---
# Kubernetes Monitoring

## Purpose

This document defines how to turn raw telemetry into operational awareness: SLOs,
alerting rules, dashboards, and health checks that tell an operator when something is
wrong and whether users are affected. It is written so an agent can define alerts that
fire on real problems and stay quiet otherwise.

Monitoring consumes what [observability](21-observability.md) emits. It also closes the
loop with [autoscaling](20-autoscaling.md) (the same metrics drive scaling) and
[resource management](19-resource-management.md) (saturation alerts catch bad sizing).

## Why It Matters

An alert that fires on everything trains operators to ignore it; an alert that never
fires lets outages run unnoticed. Both failures cost incidents. In a cluster, health is
also multi-layered — a node can be down while pods reschedule fine, or every pod can be
Ready while users get errors. Monitoring must alert on *user-visible symptoms*, not
internal causes, or you page humans for problems Kubernetes already self-healed. Good
monitoring is the difference between "we knew at the first failed request" and "a
customer told us."

## Core Principles

- **Alert on symptoms, not causes.** Page on "error rate is high" or "latency SLO is
  burning," not "CPU is 80%." Kubernetes self-heals most causes; symptoms mean users hurt.
- **Every page must be actionable.** If there is nothing a human should do right now,
  it is a dashboard signal, not an alert. Non-actionable pages cause fatigue.
- **Define SLOs, then alert on the error budget.** A latency/availability SLO with
  burn-rate alerting fires proportionally to how fast you are failing, cutting noise.
- **Use RED for services, USE for resources.** Rate/Errors/Duration per service;
  Utilization/Saturation/Errors per node and pool. Together they cover most questions.
- **Monitor the platform and the workload.** Watch control-plane, node, and pod health
  *and* application SLOs; a green cluster can still serve errors.

## Best Practices

- Standardize on Prometheus + Alertmanager (or a compatible managed backend);
  scrape `kube-state-metrics`, node-exporter, and the control plane.
- Write multi-window, multi-burn-rate SLO alerts (fast burn pages, slow burn tickets) so
  a small chronic error does not page at 3am but a fast outage does.
- Alert on `CrashLoopBackOff`, pods stuck non-`Ready`, `OOMKilled` restarts, Pending
  pods, and PVC saturation — these are early, specific signals.
- Route pages by severity: `critical` pages a human, `warning` opens a ticket, `info`
  only shows on dashboards.
- Include a runbook link and enough context (namespace, service, dashboard) in every
  alert so the on-call can act without hunting.
- Monitor the monitoring: alert if Prometheus stops scraping a target ("dead man's
  switch"), or you will trust silence that means blindness.
- Set dashboard panels on the golden signals so triage starts from user impact.

## Examples

**Good Example** — a symptom-based, burn-rate SLO alert

```yaml
# Fires when the 99% availability SLO's error budget burns fast (14.4x)
# over both a 5m and 1h window — a real, fast outage, not a blip.
groups:
  - name: slo
    rules:
      - alert: OrdersErrorBudgetFastBurn
        expr: |
          (
            sum(rate(http_requests_total{job="orders",code=~"5.."}[5m]))
            / sum(rate(http_requests_total{job="orders"}[5m]))
          ) > (14.4 * 0.01)
          and
          (
            sum(rate(http_requests_total{job="orders",code=~"5.."}[1h]))
            / sum(rate(http_requests_total{job="orders"}[1h]))
          ) > (14.4 * 0.01)
        for: 2m
        labels: { severity: critical }
        annotations:
          summary: "Orders burning error budget fast"
          runbook: "https://runbooks.example.com/orders-5xx"
```

**Bad Example** — cause-based, non-actionable, noisy

```yaml
groups:
  - name: noise
    rules:
      - alert: HighCPU
        expr: rate(container_cpu_usage_seconds_total{pod=~"orders.*"}[1m]) > 0.8
        # Pages on a CAUSE the HPA already handles by scaling out.
        # No 'for:' → fires on a single scrape spike.
        # No severity, no runbook → on-call cannot act and learns to mute it.
        labels: {}
        annotations: { summary: "CPU high" }
```

## Common Mistakes

- Alerting on resource causes (CPU, memory) that autoscaling already resolves.
- No `for:` duration, so transient spikes page instantly.
- Alerts with no runbook, owner, or context, forcing the on-call to reverse-engineer them.
- Paging on `warning`-level or informational signals, causing alert fatigue.
- No SLO/error-budget framing, so every deviation looks equally urgent.
- Monitoring only the app or only the cluster, missing the other layer.
- No dead-man's-switch, so a broken scrape pipeline looks like "all healthy."

## Production Tips

- Review alert firing history monthly; delete or tune any alert that pages without action.
- Test alerts by injecting failure (chaos/load tests) and confirming they fire and route.
- Keep dashboards and alerts as code (version-controlled) so changes are reviewed like
  any other production change.

## AI Review Checklist

- Do alerts page on user-visible symptoms, not self-healing causes?
- Is every `critical` alert actionable and linked to a runbook?
- Are SLOs defined with multi-window burn-rate alerting?
- Are pod-health signals (CrashLoopBackOff, OOMKilled, Pending, non-Ready) alerted?
- Do alerts have a `for:` duration to avoid firing on single spikes?
- Is severity-based routing in place (critical → page, warning → ticket)?
- Is there a dead-man's-switch verifying the monitoring pipeline itself is alive?

## Related

- `knowledge/kubernetes/21-observability.md`
- `knowledge/kubernetes/20-autoscaling.md`
- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/26-production.md`
