---
id: kubernetes/21-observability
topic: kubernetes
slug: observability
title: "Kubernetes Observability"
type: doc
order: 21
status: ready
tags: [kubernetes, observability]
related: [kubernetes/23-monitoring, kubernetes/24-debugging, kubernetes/04-pods, kubernetes/26-production]
when_to_use: "Read before instrumenting a workload with logs, metrics, or traces, or when an incident cannot be diagnosed from the data the cluster emits."
---
# Kubernetes Observability

## Purpose

This document defines how to make a Kubernetes workload legible from the outside through
the three signals of observability: **logs** (what happened), **metrics** (how much/how
often), and **traces** (where time went across services). It is written so an agent can
instrument an app such that an operator can answer novel questions during an incident.

Observability is the input; [monitoring](23-monitoring.md) — dashboards, alerts, SLOs —
is what you build on top of it. Emit the right signals here or monitoring has nothing to
work with.

## Why It Matters

In a cluster, pods are ephemeral: they are rescheduled, scaled to zero, and replaced by
new IPs constantly. You cannot SSH into "the server" to look around. The only durable
record of what a workload did is the telemetry it emitted while alive. If a container
logs to a file inside itself or exposes no metrics, that information dies with the pod.
Observability is not a nice-to-have add-on; it is the sole diagnostic surface for a
system whose components are designed to disappear.

## Core Principles

- **Emit to stdout/stderr, not to files.** The container runtime captures stdout;
  a cluster log agent (Fluent Bit, Vector) ships it off-node. A logfile inside the
  container is lost on restart and invisible to the platform.
- **Structure your logs.** Emit JSON with stable keys, not free-text. Structured logs
  are queryable; prose is not.
- **Correlate the three signals.** Put a `trace_id` in logs and expose it in traces so an
  operator can pivot from a slow request to its logs to its metrics.
- **Instrument the golden signals.** Latency, traffic, errors, and saturation answer
  most "is it healthy?" questions. Expose them per service.
- **Standardize on OpenTelemetry.** Use OTel SDKs and the OTel Collector so
  instrumentation is vendor-neutral and you can swap backends without recoding.

## Best Practices

- Log JSON to stdout with `level`, `timestamp`, `message`, `trace_id`, and request
  context; never log secrets, tokens, or full request bodies.
- Expose Prometheus metrics on a dedicated `/metrics` port and annotate the pod (or use a
  `ServiceMonitor`) so they are scraped automatically.
- Use histogram metrics (not just counters/gauges) for latency so you can compute p95/p99
  percentiles, which averages hide.
- Propagate W3C `traceparent` headers across service calls so traces are not broken at
  every hop; auto-instrument with the OTel Collector where possible.
- Add liveness, readiness, and startup probes — their transitions are first-class
  diagnostic events, and readiness gates traffic.
- Set log levels via config/env, not code, so you can raise verbosity during an incident
  without a redeploy.
- Include Kubernetes metadata (namespace, pod, node, deployment) in every signal via the
  Downward API or the collector, so you can slice by workload.

## Examples

**Good Example** — structured stdout logging with correlation

```go
// Structured JSON to stdout: the platform log agent ships it off-node,
// and every line carries the trace_id so logs join to traces.
logger.Info("order placed",
    "trace_id", span.SpanContext().TraceID().String(),
    "order_id", order.ID,
    "amount_cents", order.AmountCents,
    // note: no PAN, no auth token, no full request body
)
```

```yaml
# Pod exposes metrics; a ServiceMonitor (Prometheus Operator) scrapes them.
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata: { name: orders }
spec:
  selector: { matchLabels: { app: orders } }
  endpoints:
    - port: metrics        # a named container port serving /metrics
      interval: 30s
```

**Bad Example** — file logging, no structure, no correlation

```go
// Writes to a file INSIDE the container: lost on pod restart, invisible
// to the cluster's log pipeline, and unqueryable free text.
f, _ := os.OpenFile("/var/log/app.log", os.O_APPEND|os.O_WRONLY, 0644)
fmt.Fprintf(f, "order %d placed for user %s, card %s\n",
    order.ID, user.Email, order.CardNumber) // logs PII + PAN, no trace_id
```

## Common Mistakes

- Logging to a file inside the container instead of stdout/stderr.
- Free-text logs that cannot be filtered or aggregated.
- No `trace_id`, so logs, metrics, and traces cannot be correlated.
- Only exposing averages, hiding the p99 latency where users actually hurt.
- Logging secrets, tokens, or PII into a pipeline that fans out everywhere.
- Broken trace propagation because `traceparent` headers are dropped between services.
- Missing readiness probes, so traffic hits pods that are not ready and you cannot see it.

## Production Tips

- Keep application logs at `info` in production and expose a runtime knob to bump to
  `debug` during incidents without redeploying.
- Sample high-volume traces (e.g. tail-based) so cost stays bounded while errors are
  always captured.
- Retain enough log/metric history to cover your longest diagnosis window, then expire —
  storage is not free.

## AI Review Checklist

- Does the app log structured JSON to stdout/stderr (not to a file)?
- Do logs carry a `trace_id` and Kubernetes metadata for correlation?
- Are Prometheus metrics exposed and discoverable (annotation or ServiceMonitor)?
- Are latency histograms present so p95/p99 can be computed?
- Is trace context (`traceparent`) propagated across every service hop?
- Are secrets, tokens, and PII kept out of all telemetry?
- Are liveness, readiness, and startup probes defined?

## Related

- `knowledge/kubernetes/23-monitoring.md`
- `knowledge/kubernetes/24-debugging.md`
- `knowledge/kubernetes/04-pods.md`
- `knowledge/kubernetes/26-production.md`
