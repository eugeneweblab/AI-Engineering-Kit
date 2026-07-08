---
id: devops/13-observability
topic: devops
slug: observability
title: "Observability"
type: doc
order: 13
status: ready
tags: [devops, observability]
related: [devops/12-monitoring, devops/14-logging, devops/15-alerting, devops/25-incident-management, devops/27-sre-principles]
when_to_use: "Read before instrumenting a service with traces, spans, or context propagation, or when debugging why a distributed request is slow or failing."
---
# Observability

## Purpose

This document defines how to build a system you can *ask new questions of* after it is
already running — one where you can explain a novel failure from its telemetry without
shipping new code. It covers the three signals (metrics, logs, traces), context
propagation, and OpenTelemetry, so an agent can instrument a service that stays
debuggable as it grows into a distributed system.

Observability is the superset of [monitoring](12-monitoring.md). Monitoring answers
predefined questions ("is latency over budget?"); observability lets you answer the
questions you did not think to ask ("*why* is latency over budget for Android users in
one region on the checkout path?"). You need both.

## Why It Matters

In a monolith, a stack trace tells you where a request broke. In a distributed system a
single user action fans out across a dozen services, and no one node holds the whole
story. Without correlated telemetry, debugging degrades into guessing and grep across
machines while the incident runs. The property that saves you is **correlation**: being
able to follow one request end to end and pivot from a metric spike to the exact traces
and logs behind it. That property must be *designed in* — you cannot bolt it on during
an outage. The cost of getting it wrong is measured in mean-time-to-resolution on your
worst day.

## Core Principles

- **Three signals, one identity.** Metrics tell you *that* something is wrong, traces
  tell you *where*, logs tell you *why*. They are only useful together — wire them with
  a shared **trace ID** so you can pivot between them in one click.
- **Propagate context across every hop.** A trace that stops at a service boundary is
  useless. The trace/span ID must ride along on every outbound call (HTTP header, queue
  message, RPC metadata) or the request appears to vanish.
- **Instrument with an open standard.** Use **OpenTelemetry** (the 2026 default) so
  instrumentation is vendor-neutral and you can switch backends without re-instrumenting.
- **High cardinality is a feature here, not a bug.** Unlike metrics, traces and
  structured events *should* carry user id, request id, and version — that is what lets
  you isolate the one broken cohort.
- **Sample deliberately.** You cannot store every trace at scale. Decide sampling as
  policy (keep all errors and slow requests; sample the rest) rather than dropping data
  blindly.

## Best Practices

- Adopt **OpenTelemetry SDKs + OTLP** export. Emit to a collector, not directly to a
  vendor, so pipeline changes never touch application code.
- Ensure the **trace ID appears in every log line** (see [logging](14-logging.md)). This
  single field is what turns three separate tools into one investigation.
- Create a span at every **service boundary and every I/O call** (DB, cache, HTTP,
  queue). Name spans by operation (`db.query users`), not by dynamic value.
- Record **span attributes** for the dimensions you will want to filter on later:
  `user.id`, `http.route`, `service.version`, `db.system`. Follow OTel semantic
  conventions so backends understand them.
- Use **tail-based sampling** at the collector: decide whether to keep a trace *after*
  seeing the whole thing, so you always retain errors and slow outliers.
- Set **span status to error** and record the exception on failure, so a broken trace is
  visibly broken, not just a gap.
- Propagate the **W3C `traceparent`** header — the interoperable standard — across all
  hops, including into async work and background jobs.

## Examples

**Good Example** — one span per boundary, context propagated, error recorded (OTel/Go)

```go
func (s *Service) GetOrder(ctx context.Context, id string) (*Order, error) {
    // Child span inherits trace ID from ctx and is linked to the caller automatically.
    ctx, span := tracer.Start(ctx, "GetOrder")
    defer span.End()
    span.SetAttributes(attribute.String("order.id", id)) // high cardinality is OK in traces

    // Passing ctx propagates the trace across the DB call, so the query is a child span,
    // not an orphan. The `traceparent` header would do the same across an HTTP hop.
    order, err := s.db.QueryOrder(ctx, id)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, "db query failed") // trace is now visibly broken
        return nil, err
    }
    return order, nil
}
```

**Bad Example** — context dropped, so the trace breaks at the boundary

```go
func (s *Service) GetOrder(ctx context.Context, id string) (*Order, error) {
    ctx, span := tracer.Start(ctx, "GetOrder")
    defer span.End()

    // Anti-pattern: context.Background() severs the trace. The DB call starts a NEW
    // root trace with no link back, so in the UI the request appears to end here and
    // the slow query is invisible when you follow the original trace.
    order, err := s.db.QueryOrder(context.Background(), id)
    if err != nil {
        return nil, err // error never recorded on the span -> trace looks successful
    }
    return order, nil
}
```

## Common Mistakes

- Breaking trace propagation by starting a fresh context (`context.Background()`,
  a new HTTP client without the header) across a boundary.
- Treating logs, metrics, and traces as three unrelated systems with no shared trace ID,
  so correlation is manual and slow.
- Head-based sampling that drops the exact error traces you need to debug.
- Naming spans by dynamic value (`GET /users/42`), exploding the operation list.
- Rolling your own tracing format instead of OpenTelemetry, locking yourself to one
  backend.
- Not recording errors on spans, so failed requests look successful in the trace view.

## Production Tips

- Run an **OpenTelemetry Collector** as the single egress point; it handles batching,
  sampling, and re-routing without redeploying services.
- Link metrics to traces with **exemplars** so a latency spike on a dashboard jumps
  directly to a representative slow trace.
- Budget cost early: tail sampling plus retention tiers keep a high-traffic service's
  trace bill sane without losing the traces that matter.

## AI Review Checklist

- Is the service instrumented with OpenTelemetry (not a bespoke tracing format)?
- Does trace context propagate across every hop, including async and queue work?
- Is the trace ID present on every log line for cross-signal correlation?
- Is there a span at each service boundary and I/O call, named by operation not value?
- Are errors recorded on spans and span status set to error on failure?
- Is sampling tail-based so errors and slow requests are always retained?

## Related

- `knowledge/devops/12-monitoring.md`
- `knowledge/devops/14-logging.md`
- `knowledge/devops/15-alerting.md`
- `knowledge/devops/25-incident-management.md`
- `knowledge/devops/27-sre-principles.md`
