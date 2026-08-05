---
id: linux/16-monitoring
topic: linux
slug: monitoring
title: "Linux Monitoring"
type: doc
order: 16
status: ready
tags: [linux, monitoring, rate, symptom, DB_HOST]
related: [linux/15-logging, linux/18-performance, linux/06-processes, linux/25-production]
when_to_use: "Read before adding health checks, metrics, or alerts to a Linux service or host."
---
# Linux Monitoring

## Purpose

This document defines how to observe the health of a Linux host and its services —
metrics, health checks, resource signals, and alerting. It covers what to measure, the
tools to read it (`top`, `ps`, `ss`, `df`, node/exporter metrics), and how to turn
signals into actionable alerts. It is written so an agent can make a system observable
and alert on the right things, not on noise.

## Why It Matters

You cannot operate what you cannot see. Without monitoring, the first sign of trouble is a
user complaint, and the mean time to detection is however long it takes someone to
notice. But monitoring done wrong is worse than none: alerts that fire on every blip get
muted, and the one real alert is muted with them. The goal is a small set of signals that
reliably mean "a human should act", tied to symptoms users feel — not a wall of graphs
nobody reads.

## Core Principles

- **Alert on symptoms, not causes.** Page on "requests are failing" or "latency is high",
  which users feel; treat CPU/memory as diagnostic context, not primary alerts.
- **Every alert must be actionable.** If there is no response to an alert, it should be a
  dashboard or a ticket, not a page. Non-actionable pages train people to ignore pages.
- **Measure the four golden signals.** Latency, traffic, errors, and saturation cover most
  service health with a handful of metrics.
- **Health checks must test the real dependency path.** A liveness check that returns 200
  while the database is down is a lie that hides outages.
- **Baselines and rates beat thresholds.** "Error rate above 1% for 5 minutes" is more
  robust than "more than 100 errors", which scales with traffic.

## Best Practices

- Expose an application health endpoint that checks critical dependencies (DB, cache,
  queue) and returns non-200 when they are unhealthy; wire it to the orchestrator's
  readiness probe.
- Export metrics in a standard format (Prometheus/OpenMetrics via `node_exporter` and an
  app client) rather than parsing `top` output in scripts.
- Watch disk (`df`, inodes), memory pressure, load average vs core count, open file
  descriptors, and connection counts (`ss -s`) — these cause slow, silent degradation.
- Alert on rates and durations, with hysteresis (`for: 5m`) to avoid flapping.
- Set alert severities: page for user-facing outages, ticket/warn for capacity trends
  (disk 80% full and rising) so you fix them before they page.
- Monitor the monitor: alert if a target stops reporting (`up == 0`) — silence often
  means the exporter or host died, the most important failure to catch.
- Keep dashboards purposeful: one overview per service (the golden signals), drill-downs
  on demand.

## Examples

**Good Example** — a health check that tests the real dependency path

```bash
#!/usr/bin/env bash
# Readiness probe: only "ready" if the DB the app depends on is reachable.
set -euo pipefail

# Exit non-zero if the dependency is down, so the orchestrator stops routing traffic.
if pg_isready -h "$DB_HOST" -t 3 >/dev/null; then
  echo "ok"; exit 0
else
  echo "db unreachable"; exit 1   # honest failure → node pulled from rotation
fi
```

```yaml
# Prometheus rule: page on a symptom (error rate), with hysteresis to avoid flapping.
- alert: HighErrorRate
  expr: sum(rate(http_requests_total{code=~"5.."}[5m]))
      / sum(rate(http_requests_total[5m])) > 0.01
  for: 5m                 # must persist 5 min → no paging on a single blip
  labels: { severity: page }
```

**Bad Example** — a health check that hides outages, an alert that will be muted

```bash
# "Liveness" that always returns ok — reports healthy while the DB is down.
echo "ok"; exit 0        # tells the orchestrator everything is fine when it is not
```

```yaml
# Fires on a single spike with no duration and a traffic-dependent threshold.
- alert: TooManyErrors
  expr: http_5xx_total > 100   # 100 errors is nothing at 1M rps, an outage at 10 rps
  # no `for:` → flaps on every transient blip → gets muted → real alert missed
```

## Common Mistakes

- Paging on CPU or memory directly instead of on the user-visible symptom they might
  cause; most high-CPU moments are harmless.
- Health checks that do not touch real dependencies, so they stay green during an outage.
- Absolute-count thresholds that break when traffic changes.
- No alert for "target down / no data", so a crashed exporter looks like a healthy
  system.
- Alert fatigue from noisy, non-actionable alerts, which desensitizes responders.
- Ignoring slow-burn signals (disk filling, FD leak) until they become a hard outage.

## Production Tips

- Define SLOs and alert on error budget burn rate; it ties paging directly to user pain
  and cuts noise.
- Include runbook links in alert annotations so the responder knows the first step.
- Track saturation early: alert on disk at 80% with time-to-full projection, not at 99%.
- Load-test to learn each signal's normal range before setting thresholds; guessed
  thresholds are the main source of both misses and false pages.

## AI Review Checklist

- Do alerts fire on user-visible symptoms (latency/errors/availability), with resource
  metrics as context?
- Is every paging alert actionable, with a runbook?
- Do health/readiness checks exercise real dependencies and fail honestly?
- Are alerts based on rates/durations with hysteresis, not raw counts?
- Is there an alert for "no data / target down"?
- Are capacity trends (disk, FDs, memory) watched before they become outages?
- Are the four golden signals covered for each service?

## Related

- `knowledge/linux/15-logging.md`
- `knowledge/linux/18-performance.md`
- `knowledge/linux/06-processes.md`
- `knowledge/linux/25-production.md`
