---
id: backend/22-observability
topic: backend
slug: observability
title: "Observability"
type: doc
order: 22
status: ready
tags: [backend, observability]
related: [backend/12-error-handling, backend/19-performance, backend/20-scalability, backend/27-production, backend/16-background-jobs]
when_to_use: "Read before adding logging, metrics, or tracing to a service, or when an incident could not be diagnosed from what the system emitted."
---
# Observability

## Purpose

This document defines how a backend service should expose what it is doing: structured
logs, metrics, distributed traces, and health checks. It is written so an agent instruments
code such that a future operator can answer "what happened and why?" from the telemetry
alone, without adding print statements after the fact.

Observability is the property that you can understand a system's internal state from its
outputs. Monitoring tells you *that* something is wrong (a dashboard, an alert);
observability lets you find out *why* (correlated logs, traces, and metrics). You need both.

## Why It Matters

Production fails in ways you did not anticipate, on inputs you never tested, at 3am. When
that happens, the only thing you have is what the service already emitted — you cannot go
back and add a log line to a request that already failed. A service that logs an opaque
"error occurred" turns a five-minute fix into an hour of guessing. Under load and across
many [instances](20-scalability.md), the request that failed is one of millions, so
telemetry must be structured and correlated or it is noise. Good observability is the
difference between diagnosing an incident and merely surviving it.

## Core Principles

- **Log structured events, not prose.** Emit JSON with typed fields (`user_id`,
  `order_id`, `duration_ms`), not interpolated sentences. Structured logs are queryable;
  string logs are grep-and-pray.
- **Correlate everything with a request/trace id.** Propagate one id through every log,
  service hop, and job so a single request can be reconstructed end to end.
- **Instrument the three signals deliberately.** Logs (discrete events), metrics
  (aggregatable numbers), and traces (causal timing) answer different questions; you need
  all three.
- **Measure the golden signals.** Latency, traffic, errors, and saturation tell you the
  health of any service. Track them per endpoint.
- **Never log secrets or PII.** Logs are widely readable and long-lived. A password or token
  in a log is a breach; redact at the logging boundary.

## Best Practices

- Emit logs as structured JSON at the right level: `error` for actionable failures, `warn`
  for degraded-but-handled, `info` for business events, `debug` for development only. Reserve
  `error` for things a human should act on, or alerts become noise.
- Attach a correlation id to every log line and propagate it via headers (`traceparent`)
  across service and queue boundaries.
- Include context on every error log: what operation, which entity id, and the cause — enough
  to reproduce without the original request.
- Expose metrics in a standard format (OpenTelemetry / Prometheus): request count, error
  count, latency histograms (p50/p95/p99), and resource saturation.
- Provide `liveness` (is the process up?) and `readiness` (can it serve traffic, including
  dependencies?) health endpoints so orchestrators route around unhealthy instances.
- Instrument distributed traces across service calls and database queries; a trace shows
  which hop consumed the latency.
- Redact or omit sensitive fields (passwords, tokens, full card numbers, PII) before logging;
  centralize this so no call site can leak.
- Make telemetry cheap enough to always be on: sample high-volume traces, but keep error
  traces and logs at 100%.

## Examples

**Good Example** — structured, correlated, safe

```ts
logger.info({
  event: "order.created",
  order_id: order.id,
  user_id: user.id,          // typed fields, queryable and filterable
  amount_cents: order.total,
  trace_id: ctx.traceId,     // ties this line to the whole request across services
  duration_ms: Date.now() - start,
}); // no email, no card number, no token — nothing sensitive
```

**Bad Example** — unstructured, uncorrelated, leaky

```ts
// A string blob: cannot filter by user, cannot join to a trace, cannot aggregate.
console.log("Order created for " + user.email + " card " + card.number); // logs PII + PAN
try {
  await charge(order);
} catch (e) {
  console.log("error");    // no id, no cause, no context — undiagnosable after the fact
}
```

## Common Mistakes

- Logging unstructured strings that cannot be queried, filtered, or aggregated.
- No correlation id, so a request cannot be traced across services or jobs.
- Logging secrets, tokens, or PII, turning the log store into a breach surface.
- Using `error` level for non-actionable noise, so real alerts get ignored.
- Catching an exception and logging only "error" with no context or cause.
- Health checks that return `200` without actually checking dependencies (false healthy).
- Measuring only averages; the p99 tail that hurts users is invisible.

## Production Tips

- Alert on symptoms users feel (error rate, p99 latency, saturation), not on causes (CPU),
  so you page for impact, not noise.
- Keep dashboards for the golden signals per endpoint and per dependency.
- Set log retention and sampling to control cost; keep 100% of errors, sample the rest.
- Test observability during game days: trigger a failure and confirm you can diagnose it
  from telemetry alone, without adding code.

## AI Review Checklist

- Are logs structured (JSON with typed fields), not interpolated strings?
- Does every request carry a correlation/trace id propagated across services and jobs?
- Do error logs include the operation, entity ids, and cause needed to diagnose?
- Are latency (p50/p95/p99), error, traffic, and saturation metrics exported?
- Do liveness and readiness endpoints actually check the process and its dependencies?
- Is all secret/PII redaction centralized so no log line can leak sensitive data?
- Is the `error` log level reserved for actionable failures, not routine noise?

## Related

- `knowledge/backend/12-error-handling.md`
- `knowledge/backend/19-performance.md`
- `knowledge/backend/20-scalability.md`
- `knowledge/backend/27-production.md`
- `knowledge/backend/16-background-jobs.md`
