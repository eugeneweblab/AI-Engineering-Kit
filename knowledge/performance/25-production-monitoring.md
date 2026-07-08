---
id: performance/25-production-monitoring
topic: performance
slug: production-monitoring
title: "Production Monitoring"
type: doc
order: 25
status: ready
tags: [performance, production-monitoring]
related: [performance/17-monitoring, performance/02-metrics, performance/18-web-vitals, performance/26-debugging, performance/23-performance-budget]
when_to_use: "Read before shipping a service to production or when adding observability to catch performance regressions in the wild."
---
# Production Monitoring

## Purpose

This document defines how to observe performance in production: which signals to collect,
how to summarize them honestly, and how to alert on real user pain instead of noise. It is
written so an agent can instrument a service such that a slowdown is detected, located, and
explained — before customers report it.

Production is the only environment where the real workload, data, and concurrency exist.
Monitoring is how you keep that environment in view continuously, not just when something
breaks.

## Why It Matters

Performance regressions in production are invisible without instrumentation: the app
returns correct results, just slower, and averages hide the pain. A p50 of 80 ms can sit
next to a p99 of 6 seconds — and it is the p99 users remember and abandon carts over.
Without production signals you learn about slowdowns from angry users, hours late, with no
data to explain them. Good monitoring turns "the site feels slow" into "checkout p99
crossed budget at 14:03 when the cache hit rate dropped," which is actionable.

## Core Principles

- **Measure percentiles, never averages.** Report p50/p95/p99. A mean is dominated by the
  fast majority and conceals the tail where users actually suffer.
- **Instrument the four golden signals.** Latency, traffic, errors, and saturation
  together describe a service's health; watch all four.
- **Alert on symptoms, not causes.** Page on user-visible SLO breaches (latency, error
  rate), not on internal metrics like CPU that may be fine or benign at 90%.
- **Trace end to end.** A slow request is a sum of spans; distributed tracing shows which
  hop owns the time. Aggregates alone cannot locate a bottleneck.
- **Attribute cost with high-cardinality context.** Tag by route, tenant, and version so
  you can answer "who and where," not just "how much."

## Best Practices

- Track **latency as a distribution** (histogram), and record it as close to the user as
  possible — real user monitoring, not just server-side. See [web vitals](18-web-vitals.md).
- Define **SLOs and error budgets** and alert when the burn rate threatens them, using
  multi-window burn-rate rules to avoid both flapping and slow detection.
- Correlate signals: latency, throughput, saturation (queue depth, connection pool, CPU),
  and error rate on one dashboard so a spike has context.
- Emit **structured logs and traces with a shared request/trace ID** so a log line, its
  trace, and its metrics line up.
- Keep cardinality under control: tag with bounded dimensions (route, region, version),
  never unbounded ones (user ID, raw URL with IDs) that explode metric storage and cost.
- Retain enough history to compare **week over week**; a regression is often only visible
  against last week's baseline, not the last hour.
- Make dashboards answer a question. A wall of graphs nobody reads is not monitoring.

## Examples

**Good Example** — histogram, labeled by route, percentile-ready

```python
from prometheus_client import Histogram

# Buckets chosen around the SLO (200 ms) so p95/p99 are computed accurately.
REQUEST_LATENCY = Histogram(
    "http_request_seconds",
    "Request latency",
    ["route", "method"],                       # bounded, high-value labels
    buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 5),
)

def handle(request):
    with REQUEST_LATENCY.labels(request.route, request.method).time():
        return process(request)
    # A histogram lets the backend compute p95/p99 per route.
    # Alerts fire on the tail, and the label tells you which route to look at.
```

**Bad Example** — average of a scalar, unbounded label, blind spot

```python
total_ms = 0
count = 0

def handle(request):
    global total_ms, count
    start = time.time()
    result = process(request)
    total_ms += (time.time() - start) * 1000
    count += 1
    log.info(f"avg={total_ms / count}", url=request.full_url)  # per-request URL = cardinality bomb
    return result
    # Only a running average exists: the p99 tail is invisible, so the
    # slow requests that lose customers never show up on any graph.
```

## Common Mistakes

- Reporting averages, which mask the tail latency users actually feel.
- Alerting on CPU/memory (causes) instead of latency and error SLOs (symptoms) — pages
  that are either noise or fire after users already hurt.
- No distributed tracing, so a slow request cannot be attributed to a service.
- High-cardinality labels (user ID, raw path) that blow up metric storage and cost.
- Server-only timing that ignores client render and network — the user's real latency.
- Dashboards without a baseline, so "is this normal?" is unanswerable.
- Sampling traces so aggressively that the slow outliers are the ones dropped.

## Production Tips

- Use exemplar-linked histograms so a latency bucket links straight to a trace of a slow
  request in that bucket.
- Alert on multi-window burn rate (e.g. fast 5m + slow 1h) to catch both sudden and
  gradual SLO erosion without flapping.
- Keep a "golden signals" dashboard per service and review it after every deploy; pair it
  with [debugging](26-debugging.md) runbooks.

## AI Review Checklist

- Is latency recorded as a histogram and reported as p50/p95/p99, not a mean?
- Are all four golden signals (latency, traffic, errors, saturation) covered?
- Do alerts fire on user-visible SLO breaches rather than raw resource metrics?
- Is there end-to-end tracing with a shared trace ID across services?
- Are metric labels bounded (no user IDs or raw URLs)?
- Is client-side (real user) latency captured, not just server time?
- Can a dashboard compare current values against a prior-week baseline?

## Related

- `knowledge/performance/17-monitoring.md`
- `knowledge/performance/02-metrics.md`
- `knowledge/performance/18-web-vitals.md`
- `knowledge/performance/26-debugging.md`
- `knowledge/performance/23-performance-budget.md`
