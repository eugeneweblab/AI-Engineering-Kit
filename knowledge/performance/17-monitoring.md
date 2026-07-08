---
id: performance/17-monitoring
topic: performance
slug: monitoring
title: "Monitoring"
type: doc
order: 17
status: ready
tags: [performance, monitoring]
related: [performance/02-metrics, performance/16-profiling, performance/25-production-monitoring, performance/14-api-performance, performance/26-debugging]
when_to_use: "Read before adding metrics, dashboards, or alerts, or when a production slowdown has no visibility."
---
# Monitoring

## Purpose

This document defines how to observe a running system's performance: which signals to
emit, how to instrument them, and how to alert so a regression is caught before users
report it. It is written so an agent can add monitoring that answers "is it slow, for
whom, and where?" without drowning the team in noise.

Monitoring is the production counterpart to [profiling](16-profiling.md): profiling
finds bottlenecks in code you can run, monitoring finds them in a live system you
cannot pause. It builds on the [metrics](02-metrics.md) doc, which defines *what*
percentiles and rates mean; this doc covers how to *collect, dashboard, and alert* on
them.

## Why It Matters

A system you cannot see is a system you cannot keep fast. Performance regressions are
usually gradual and load-dependent — a query that slows as data grows, a p99 that
creeps up after a deploy — and without monitoring the first signal is an angry user or
a lost sale. Monitoring turns invisible degradation into a graph and a page. It also
scopes incidents: good instrumentation tells you *which endpoint*, *which dependency*,
and *which percentile* regressed, turning an hours-long hunt into minutes. The cost of
getting this wrong is not just downtime; it is optimizing blind because you never had
the data to know what was slow.

## Core Principles

- **Measure the user's experience, not the server's mood.** Percentile latency and
  error rate at the request boundary are what users feel; CPU graphs alone are not.
- **Alert on symptoms, monitor causes.** Page on high-level SLO breaches (latency,
  errors); keep resource dashboards for diagnosis. Paging on causes creates noise.
- **The tail is the signal.** Track **p95/p99**, never averages — an average hides the
  slow requests that are the actual problem.
- **Every alert must be actionable.** An alert nobody acts on trains everyone to
  ignore all alerts. If there is no response, it is a dashboard, not an alert.
- **Instrument once, at the boundaries.** Standardize on RED (Rate, Errors, Duration)
  for services and USE (Utilization, Saturation, Errors) for resources.

## Best Practices

- Emit **RED metrics per endpoint** — request rate, error rate, and duration
  histograms — and **USE metrics per resource** (CPU, memory, connection pool, queue).
- Record latency as a **histogram**, not a gauge or average, so p95/p99 are computed
  correctly across instances. Averaging pre-averaged latencies is meaningless.
- Set alert thresholds against an **SLO** (e.g. "p99 < 300ms over 5 min") and alert on
  **error budget burn rate**, not single spikes, to cut false pages.
- Attach **trace/correlation IDs** so a slow request in a metric can be followed across
  services; distributed tracing turns "the API is slow" into "call C waited on D."
- Monitor **saturation signals that fail silently**: connection-pool usage, queue
  depth, replication lag, GC pause time — each precedes an outage.
- Keep **cardinality bounded**: never put user IDs, request IDs, or unbounded values in
  metric labels — it explodes storage and cost. Use logs/traces for high-cardinality.
- Version dashboards and alerts **as code** next to the service, so monitoring evolves
  with the system instead of rotting.

## Examples

**Good Example** — histogram, bounded labels, symptom alert

```python
from prometheus_client import Histogram

# Duration as a histogram → p95/p99 are computable. Labels are bounded (route, method,
# status class) — never the raw path or a user id, which would explode cardinality.
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds", "Request duration",
    ["route", "method", "status_class"],
)

@app.middleware("http")
async def measure(request, call_next):
    with REQUEST_DURATION.labels(request.scope["route"], request.method, "pending").time():
        return await call_next(request)
```
```yaml
# Alert on the user-facing symptom (SLO breach), not on a raw CPU number.
- alert: HighApiLatency
  expr: histogram_quantile(0.99, http_request_duration_seconds) > 0.3
  for: 5m          # sustained, not a single spike → actionable, low-noise
```

**Bad Example** — average gauge, unbounded labels, noisy alert

```python
from prometheus_client import Gauge

# A gauge of average latency: p99 is unrecoverable, and the raw URL as a label
# creates a new time series per unique path → cardinality explosion, huge cost.
AVG_LATENCY = Gauge("avg_latency", "Average latency", ["full_url", "user_id"])
AVG_LATENCY.labels(request.url, request.user_id).set(elapsed)  # unbounded labels
```
```yaml
# Pages on a transient CPU spike no human will act on → alert fatigue,
# and the real latency regression goes unnoticed under the noise.
- alert: CpuSpike
  expr: cpu_usage > 0.8      # no "for" duration, no SLO, not user-facing
```

## Common Mistakes

- Monitoring averages instead of p95/p99, hiding the slow tail that matters.
- Storing latency as a gauge, making cross-instance percentiles impossible.
- High-cardinality labels (user IDs, raw URLs) that blow up metric storage and cost.
- Alerting on causes (CPU, memory) instead of user-facing symptoms, creating noise.
- Alerts with no runbook or owner, training the team to ignore every page.
- No tracing/correlation IDs, so a slow metric cannot be tied to a request or service.
- Ignoring silent saturation signals (pool, queue, replication lag) until they fail.

## Production Tips

- Define SLOs and alert on **error-budget burn rate** (multi-window) so brief blips do
  not page but sustained degradation does.
- Keep a dashboard that overlays deploys on latency/error graphs; most regressions are
  a deploy, and the overlay names the cause instantly.
- Route high-cardinality detail to **logs and traces**, and reserve **metrics** for
  bounded aggregates — the three form a layered path from "something is slow" to "this
  line is slow" (see [debugging](26-debugging.md)).

## AI Review Checklist

- Are per-endpoint RED metrics (rate, errors, duration) emitted as histograms?
- Are p95/p99 tracked and alerted on, rather than averages?
- Are metric labels bounded — no user IDs, request IDs, or raw URLs?
- Do alerts fire on user-facing symptoms/SLO breaches with a `for` duration, not raw
  causes?
- Does every alert have an owner and an actionable runbook?
- Are correlation/trace IDs present so a slow metric can be followed across services?
- Are silent saturation signals (pool, queue depth, replication lag) monitored?

## Related

- `knowledge/performance/02-metrics.md`
- `knowledge/performance/16-profiling.md`
- `knowledge/performance/25-production-monitoring.md`
- `knowledge/performance/14-api-performance.md`
- `knowledge/performance/26-debugging.md`
