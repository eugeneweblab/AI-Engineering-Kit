---
id: architecture/18-observability
topic: architecture
slug: observability
title: "Observability"
type: doc
order: 18
status: ready
tags: [architecture, observability]
related: [architecture/17-fault-tolerance, architecture/16-high-availability, architecture/09-microservices, architecture/21-distributed-systems, architecture/14-performance]
when_to_use: "Read before adding logging, metrics, or tracing to a service, or when a production incident is hard to diagnose."
---
# Observability

## Purpose

This document defines how to make a running system *explainable from the outside*:
logs, metrics, traces, and the conventions that tie them together. It is written so an
agent can instrument a service such that an operator can answer "what is broken and why?"
without attaching a debugger to production.

Observability is not monitoring. Monitoring watches for known failure modes you predicted
in advance. Observability lets you ask *new* questions about *unknown* failures after they
happen. A system is observable when its outputs — the three signals plus their correlation
IDs — are rich enough to explain any internal state you did not anticipate.

## Why It Matters

In a monolith you can read a stack trace. In a distributed system a single user action
crosses many services, queues, and databases, and no one process holds the whole story.
When latency spikes at 3 a.m., the only evidence is what you emitted *before* the incident.
Instrumentation is not something you can add retroactively to a request that already failed.
Under-instrument and you are blind; over-instrument and you drown in cost and noise, and the
one signal that mattered is buried. The goal is high-signal telemetry that pays for itself
the first time it shortens an outage.

## Core Principles

- **Emit the three signals, and correlate them.** Logs (discrete events), metrics
  (aggregatable numbers), and traces (causal request paths) answer different questions.
  A `trace_id` on every log and span is what turns three data sources into one story.
- **Instrument at the boundary.** Measure every inbound request, outbound call, and queue
  hop. Boundaries are where failures cross and where blame is assigned.
- **Structure everything.** Emit machine-parseable events (key/value or JSON), never
  free-form prose. You cannot aggregate or alert on a sentence.
- **Measure what users feel.** Alert on symptoms (latency, error rate, saturation) that map
  to user pain, not on causes (CPU, a restart) that may be harmless.
- **Adopt a standard, not a vendor.** Instrument with OpenTelemetry so telemetry is portable
  and you can change backends without re-touching every service.

## Best Practices

- Use structured logging with a fixed schema: `timestamp`, `level`, `service`, `trace_id`,
  `message`, plus typed fields. Log JSON in production so a collector can index it.
- Propagate context (W3C `traceparent`) across every network hop and async boundary, so a
  trace does not break at the first queue or thread pool.
- Track the four golden signals per service: latency, traffic, errors, saturation. For
  user-facing flows, define SLOs and alert on error budget burn, not raw thresholds.
- Prefer histograms over averages for latency. An average hides the p99 that is timing out;
  the tail is where users leave.
- Sample traces (head- or tail-based) to control cost, but keep 100% of errors. Cheap traces
  are worthless if they drop the failures.
- Give every metric bounded-cardinality labels. A label like `user_id` explodes into millions
  of time series and bankrupts the metrics backend.
- Redact secrets and PII at the logging layer, not by asking developers to remember. Tokens,
  passwords, and card numbers must never reach a log sink.

## Examples

**Good Example** — structured, correlated, bounded cardinality

```python
# One structured event per request, carrying the trace id that stitches
# this log to its distributed trace and to the request's metrics.
logger.info(
    "http_request",
    trace_id=ctx.trace_id,          # correlates log <-> trace <-> metric
    method=req.method,
    route=req.route,                # low-cardinality template, not the raw URL
    status=res.status,
    duration_ms=elapsed_ms,
)
# Latency as a histogram, labelled by route (bounded), not by user (unbounded).
request_latency.labels(route=req.route, status=res.status).observe(elapsed_ms)
```

**Bad Example** — unstructured, uncorrelated, cardinality bomb

```python
# Free-form string: cannot be filtered, aggregated, or joined to a trace.
logger.info(f"Request to {req.url} took {elapsed_ms}ms for user {user_id}")

# user_id as a label creates one time series per user -> the metrics store
# runs out of memory; there is no trace_id, so this number ties to nothing.
request_latency.labels(url=req.url, user=user_id).observe(elapsed_ms)
```

## Common Mistakes

- Logging free-form strings that no query can aggregate or alert on.
- No `trace_id`, so logs, metrics, and traces cannot be joined during an incident.
- High-cardinality labels (`user_id`, raw URL, request body) that blow up the metrics store.
- Alerting on causes (CPU 90%) instead of symptoms (checkout error rate), causing pager fatigue.
- Reporting average latency, hiding the p99 tail where the actual timeouts live.
- Sampling away errors along with successful traces, so failures leave no trace behind.
- Logging secrets or PII because redaction was left to developer discipline.

## Production Tips

- Set log **retention and volume budgets** deliberately; unbounded log ingestion is a
  top cloud cost surprise. Keep debug logs short-lived, keep audit logs long.
- Make dashboards answer "is it the user's problem or ours?" first, then drill into causes.
- Include a `trace_id` in error responses to users so support can jump straight to the trace.
- Run a periodic "can we debug this?" game day: pick a past incident and confirm the current
  telemetry would explain it.

## AI Review Checklist

- Does every log line carry `trace_id`, `service`, and `level` in a structured format?
- Is context propagated across every network and async boundary (W3C `traceparent`)?
- Are the four golden signals tracked, with alerts on symptoms and SLO burn, not raw causes?
- Is latency a histogram (p50/p95/p99), not an average?
- Are all metric labels bounded-cardinality — no `user_id`, no raw URLs?
- Are errors kept at 100% even when traces are sampled?
- Are secrets and PII redacted before reaching any log sink?

## Related

- `knowledge/architecture/17-fault-tolerance.md`
- `knowledge/architecture/16-high-availability.md`
- `knowledge/architecture/09-microservices.md`
- `knowledge/architecture/21-distributed-systems.md`
- `knowledge/architecture/14-performance.md`
