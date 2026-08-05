---
id: devops/12-monitoring
topic: devops
slug: monitoring
title: "DevOps Monitoring"
type: doc
order: 12
status: ready
tags: [devops, monitoring, labels, REQUEST_DURATION, threshold, call_next, "@app"]
related: [devops/13-observability, devops/15-alerting, devops/14-logging, devops/27-sre-principles, devops/25-incident-management]
when_to_use: "Read before adding metrics, dashboards, or health checks to a service, or reviewing a service's readiness for production."
---
# DevOps Monitoring

## Purpose

This document defines how to measure whether a running system is healthy: what to
measure, how to expose it, and how to turn raw numbers into a signal a human or alert
can act on. It is written so an agent can instrument a service correctly the first time,
without drowning operators in noise or missing the failures that matter.

Monitoring answers a *known* question — "is this metric inside its expected range?".
It is the narrow, curated view. When you need to ask questions you did not anticipate,
that is [observability](13-observability.md). Monitoring feeds
[alerting](15-alerting.md); do not conflate the three.

## Why It Matters

You cannot operate what you cannot see. Without monitoring, the first report of an
outage comes from a customer, and the mean time to detection is measured in the length
of your worst day. Good monitoring turns a silent, spreading failure into an early,
bounded one. But monitoring has a cost that scales badly: every metric is data to store,
a dashboard to maintain, and a potential false alarm. Over-monitoring buries the one
signal that matters under a thousand that do not, and operators learn to ignore all of
them. The goal is not maximum coverage — it is the *smallest* set of signals that
reliably reflect user-facing health.

## Core Principles

- **Monitor symptoms users feel, not just causes.** A high CPU number is a cause; a
  slow checkout is a symptom. Alert on symptoms; use causes for diagnosis. The cost of
  cause-only monitoring is you page on things that never hurt anyone.
- **Prefer the four golden signals** — latency, traffic, errors, saturation — as the
  backbone of every service. They generalize across almost any request-driven system.
- **Measure at percentiles, not averages.** An average latency of 200 ms hides a p99 of
  9 s that is timing out one user in a hundred. Averages lie about tail behavior.
- **Instrument once, at the boundary.** Emit metrics where requests enter and leave the
  service, so coverage is uniform and does not depend on each code path remembering to
  report.
- **Every metric must have an owner and a purpose.** If no one can say what decision a
  metric drives, delete it. Unused metrics are pure cost.

## Best Practices

- Track the **RED** metrics for every request-serving component — **R**ate, **E**rrors,
  **D**uration — and the **USE** metrics for every resource — **U**tilization,
  **S**aturation, **E**rrors. Together they cover requests and the resources behind them.
- Use a pull-based, dimensional metrics system (Prometheus / OpenMetrics is the 2026
  default) and expose a `/metrics` endpoint. Labels let you slice by route, status, and
  version without a new metric per combination.
- Keep **label cardinality bounded**. Never put user IDs, request IDs, emails, or raw
  URLs in labels — each unique value is a new time series and will exhaust memory. Use
  the route *template* (`/users/:id`), not the concrete path.
- Expose **liveness** and **readiness** probes separately. Liveness = "restart me if
  this fails"; readiness = "stop sending traffic until this passes". Conflating them
  causes restart loops or blackholed requests.
- Record request duration as a **histogram**, not a gauge, so percentiles can be
  computed server-side across instances.
- Set explicit **SLOs** (e.g. 99.9% of requests < 300 ms over 30 days) and monitor the
  error budget. The SLO, not a gut feeling, decides when a metric is "bad".
- Monitor the **monitoring**: alert if a target stops reporting (`up == 0`). A silent
  exporter looks identical to a healthy system.

## Examples

**Good Example** — bounded-cardinality histogram at the boundary (Prometheus client)

```python
from prometheus_client import Histogram

# One histogram, sliced by low-cardinality labels; route is a TEMPLATE, not the raw path.
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    labelnames=["method", "route", "status"],   # bounded set of values
    buckets=(0.01, 0.05, 0.1, 0.3, 1, 3, 10),   # tuned to the SLO threshold (0.3s)
)

@app.middleware("http")
async def measure(request, call_next):
    with REQUEST_DURATION.labels(request.method, request.scope["route"], "pending").time():
        response = await call_next(request)
    # Percentiles are derived from buckets across ALL instances at query time.
    return response
```

**Bad Example** — unbounded cardinality and an average that hides the tail

```python
from prometheus_client import Gauge

# Anti-pattern: the concrete URL and user id are labels -> a new time series per user,
# per path. This grows without limit and eventually OOMs the metrics store.
LATENCY = Gauge("request_latency_ms", "latency", ["full_url", "user_id"])

def handle(request, user):
    start = now()
    process(request)
    # A gauge overwrites; you can only ever read the LAST value, and averaging these
    # loses p99 entirely. The one slow user in a hundred is invisible.
    LATENCY.labels(request.url, user.id).set((now() - start) * 1000)
```

## Common Mistakes

- Putting high-cardinality values (user id, request id, raw URL) in metric labels,
  eventually OOMing the metrics backend.
- Alerting on causes (CPU, memory) instead of user-facing symptoms, producing pages
  for conditions no user ever noticed.
- Reporting averages instead of percentiles, hiding tail latency.
- Using the same probe for liveness and readiness, causing restart storms under load.
- Collecting hundreds of metrics no dashboard or alert ever reads.
- No alert when a target stops scraping, so a dead exporter reads as "all green".

## Production Tips

- Right-size retention: keep high-resolution data for days, downsampled data for
  months. Full-resolution long-term storage is expensive and rarely queried.
- Version dashboards and alert rules as code (e.g. in Git next to the service) so they
  review and roll back like any other change.
- Attach an exemplar trace ID to latency histograms so a spike links straight to a slow
  [trace](13-observability.md).

## AI Review Checklist

- Does the service expose the four golden signals (or RED/USE) for its main paths?
- Are all metric labels bounded in cardinality — no user IDs, request IDs, or raw URLs?
- Is latency a histogram measured at percentiles, not an average or gauge?
- Are liveness and readiness probes distinct and correct?
- Is there an explicit SLO that defines what "unhealthy" means?
- Is there an alert for a target that stops reporting (`up == 0`)?
- Does every metric map to a dashboard or alert that drives a decision?

## Related

- `knowledge/devops/13-observability.md`
- `knowledge/devops/15-alerting.md`
- `knowledge/devops/14-logging.md`
- `knowledge/devops/27-sre-principles.md`
- `knowledge/devops/25-incident-management.md`
