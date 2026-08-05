---
id: performance/02-metrics
topic: performance
slug: metrics
title: "Metrics"
type: doc
order: 2
status: ready
tags: [performance, metrics, handle, histogram_quantile, Histogram, labels, time]
related: [performance/01-performance-fundamentals, performance/17-monitoring, performance/25-production-monitoring, performance/18-web-vitals, performance/22-load-testing]
when_to_use: "Read before instrumenting a service or interpreting a latency number, so you measure the right thing the right way."
---
# Metrics

## Purpose

This document defines *what* to measure and *how to read* it: latency percentiles, the
difference between averages and tails, and the standard signal sets (RED for
request-driven services, USE for resources). It exists so an agent instruments a system
in a way that reveals real user experience instead of hiding it behind a comforting mean.

A metric you cannot act on is noise. This doc is about choosing metrics that name the
problem.

## Why It Matters

The average latency is the most misleading number in performance. A service with a 50ms
average can be timing out for 5% of users, and the average will never show it. Teams ship
dashboards full of means, declare the system healthy, and get paged anyway — because users
live in the tail. Choosing percentiles and saturation signals over averages is the
difference between a dashboard that predicts incidents and one that only explains them
afterward.

## Core Principles

- **Percentiles, not averages.** Report p50, p95, p99. The average blends fast and slow
  requests into a number no user actually experiences.
- **The tail defines the experience.** A page that makes 10 backend calls is as slow as
  its slowest call; p99 of one dependency becomes typical page latency.
- **Latency, traffic, errors, saturation.** For any service, track all four (this is the
  core of both RED and the "four golden signals"). One in isolation misleads.
- **Measure at the edge and at the source.** Client-side (real user) numbers include
  network and render; server-side numbers isolate backend cost. You need both.
- **Percentiles do not average.** You cannot average p99 across shards or time buckets;
  aggregate from histograms, not from pre-computed percentiles.
- **Every metric needs a threshold.** A number with no target is not actionable — decide
  what "too slow" is before an incident forces you to.

## Standard Signal Sets

- **RED** (request-driven services): **R**ate (requests/sec), **E**rrors (failed/sec),
  **D**uration (latency distribution). Use for APIs and endpoints.
- **USE** (resources: CPU, memory, disk, network): **U**tilization, **S**aturation
  (queue depth / wait), **E**rrors. Use to find *which* resource is the bottleneck.
- **Web Vitals** (frontend): LCP, INP, CLS — see [web-vitals](18-web-vitals.md).

## Best Practices

- Emit latency as a **histogram**, not a gauge or an average, so percentiles are computed
  correctly at query time.
- Label metrics by endpoint, status, and region — but keep cardinality bounded; never
  label by user id or raw URL.
- Set **SLOs** on the tail (e.g. "p99 < 300ms over 30 days") and alert on the error
  budget burn, not on single spikes.
- Correlate saturation with latency: rising p99 with rising queue depth points at a
  saturated resource, not slow code.
- Capture **both** RUM (real user monitoring) and synthetic/server metrics; disagreement
  between them localizes the problem to the network or client.
- Keep a **baseline**: record normal p50/p95/p99 so a regression is visible.

## Examples

**Good Example** — histogram, percentiles, actionable threshold

```python
from prometheus_client import Histogram

# Buckets chosen around the SLO so p95/p99 land on real boundaries.
LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    labelnames=["route", "status"],
    buckets=(0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 5),
)

def handle(req):
    with LATENCY.labels(route=req.route, status="200").time():
        return process(req)
# Alert rule: histogram_quantile(0.99, ...) > 0.3 for 5m  → tail SLO breach
```

**Bad Example** — average gauge that hides the tail

```python
total_ms = 0
count = 0

def handle(req):
    global total_ms, count
    start = now()
    resp = process(req)
    total_ms += now() - start
    count += 1
    # Dashboards show total_ms / count. A 50ms mean can hide 5% of requests at 3s;
    # you cannot recover p99 from a running average. High-cardinality-free but useless.
    return resp
```

## Common Mistakes

- Reporting or alerting on the **mean** latency, which hides the tail users feel.
- Averaging pre-computed percentiles across instances or time (mathematically invalid).
- Tracking latency but not errors and saturation, so you cannot tell *why* it is slow.
- Unbounded label cardinality (user id, full URL), which melts the metrics backend.
- No baseline, so a 2x regression looks like a normal number.
- Measuring only server-side and blaming the backend for what is actually network/render.

## Production Tips

- Put p50/p95/p99 latency, error rate, and saturation on one dashboard per service so
  an on-call engineer reads the whole picture at a glance.
- Alert on **SLO burn rate**, not raw thresholds, to cut false pages from brief spikes.
- Keep histogram buckets tuned to your SLO; default buckets often miss the region you
  care about.

## AI Review Checklist

- Are latencies reported as percentiles (p50/p95/p99), never as an average?
- Is latency emitted as a histogram so percentiles aggregate correctly?
- Are rate, errors, and saturation tracked alongside latency (RED/USE covered)?
- Is metric label cardinality bounded (no user id / raw URL labels)?
- Does each key metric have a threshold or SLO defined?
- Is there both a client-side and a server-side view where it matters?

## Related

- `knowledge/performance/01-performance-fundamentals.md`
- `knowledge/performance/17-monitoring.md`
- `knowledge/performance/25-production-monitoring.md`
- `knowledge/performance/18-web-vitals.md`
- `knowledge/performance/22-load-testing.md`
