---
id: rest-api/26-monitoring
topic: rest-api
slug: monitoring
title: "Monitoring"
type: doc
order: 26
status: ready
tags: [rest-api, monitoring]
related: [rest-api/09-error-handling, rest-api/07-status-codes, rest-api/28-production, rest-api/25-performance, rest-api/24-security]
when_to_use: "Read before shipping an API to production or when an incident can't be diagnosed because the signals aren't there."
---
# Monitoring

## Purpose

This document defines how to make a REST API observable: structured logs, metrics, traces,
health checks, and alerts. The goal is that when something breaks — a spike in errors, a
slow dependency, a bad deploy — you can see it, locate it, and correlate it across services
in minutes, not hours. Observability is not added after an incident; it is designed in so
the incident is diagnosable when it happens.

## Why It Matters

An API you cannot observe is an API you cannot operate. Without signals, the first report
of an outage comes from an angry user, the cause is a guess, and every deploy is a gamble.
The three pillars — logs (what happened), metrics (how much/how often), and traces (where
the time went) — turn "the site is slow" into "the `/checkout` endpoint's p99 tripled
after the 14:02 deploy because the payments call now times out." Monitoring is what makes
that sentence possible. It is also a security control: auth failures and rate-limit hits
are only useful if something is watching them.

## Core Principles

- **Log structured, not prose.** Emit JSON with consistent fields (timestamp, level,
  request id, route, status, latency), so logs are queryable, not just readable.
- **Correlate everything with a request id.** Generate or propagate a trace/correlation id
  per request and attach it to every log line and downstream call. Without it, distributed
  logs are noise.
- **Measure the four golden signals:** latency, traffic, errors, and saturation. They
  cover almost every failure mode of a request-serving system.
- **Alert on symptoms, not causes.** Page on user-visible SLO breaches (error rate,
  latency), not on every CPU blip. Noisy alerts get ignored, and ignored alerts miss outages.
- **Never log secrets.** Tokens, passwords, full request bodies, and PII must be redacted.
  A leaked credential in a log is a breach. See [security](24-security.md).
- **Health checks reflect real readiness.** `/health` must verify critical dependencies,
  not just return `200` from a process that cannot reach its database.

## Best Practices

- Emit one structured access log per request with method, route (templated, not the raw URL
  with ids), status, latency, request id, and user/tenant id where safe.
- Instrument RED metrics per endpoint: **R**ate, **E**rrors, **D**uration. Export them
  (Prometheus/OpenTelemetry) with route and status labels — but keep label cardinality
  bounded, so never label by raw user id or unbounded path.
- Use OpenTelemetry for distributed tracing across services and DB/HTTP calls, so you can
  see where a slow request spent its time.
- Expose `/health` (liveness: is the process up) and `/ready` (readiness: can it serve —
  DB, cache reachable). Load balancers use these to route and restart.
- Track latency as percentiles (p50/p95/p99), never as an average — averages hide the tail
  where real users suffer. See [performance](25-performance.md).
- Alert on error-rate and latency SLO breaches with sensible windows, and route pages to
  on-call; send low-severity signals to a dashboard, not a pager.
- Version and timestamp deploys in your telemetry so you can correlate regressions to
  releases.

## Examples

**Good Example** — structured log with correlation id and bounded labels

```ts
// Middleware: one structured access log per request, id propagated downstream.
app.use((req, res, next) => {
  const requestId = req.header("x-request-id") ?? crypto.randomUUID();
  req.requestId = requestId;
  const start = performance.now();

  res.on("finish", () => {
    logger.info({
      requestId,                     // correlate this line with traces and downstream logs
      method: req.method,
      route: req.route?.path ?? "unknown", // templated path, e.g. /users/:id — bounded cardinality
      status: res.statusCode,
      durationMs: Math.round(performance.now() - start),
      userId: req.user?.id,          // safe id, never the token or body
    });
    metrics.httpDuration.observe({ route: req.route?.path, status: res.statusCode }, ...);
  });
  next();
});
```

**Bad Example** — unstructured, unbounded, and leaking secrets

```ts
app.use((req, res, next) => {
  // Prose string: not queryable, no request id to correlate across services.
  // Raw URL as a metric/log key → unbounded cardinality (every id is a new series).
  // Logs the full body → dumps passwords and tokens into log storage (a breach).
  console.log(`Request to ${req.url} body=${JSON.stringify(req.body)}`);
  next();
});
```

## Common Mistakes

- Free-text `console.log` that cannot be filtered, aggregated, or alerted on.
- No correlation id, so a request's logs cannot be stitched across services.
- Labeling metrics by raw URL or user id, causing cardinality explosion that kills the
  metrics backend.
- Alerting on averages, which hide the p99 tail users actually experience.
- Health checks that return `200` without verifying the dependencies the API needs.
- Logging tokens, passwords, or full request/response bodies.
- Alert fatigue: paging on non-actionable causes until real alerts get muted.

## Production Tips

- Define SLOs (e.g. 99.9% of requests < 300 ms) and alert on error budget burn rate.
- Build dashboards per endpoint showing RED metrics side by side; annotate deploys on them.
- Retain logs long enough for incident forensics and compliance, but redact/expire PII.
- Test alerts by injecting failures in staging — an untested alert is not an alert.

## AI Review Checklist

- Are logs structured (JSON) with consistent, queryable fields?
- Does every request carry a correlation/trace id propagated to downstream calls?
- Are RED metrics exported per endpoint with bounded label cardinality?
- Is latency tracked as p95/p99 percentiles, not averages?
- Do `/health` and `/ready` actually verify critical dependencies?
- Do alerts fire on user-visible symptoms (SLO breaches), not noisy causes?
- Are secrets, tokens, and PII redacted from all logs?

## Related

- `knowledge/rest-api/09-error-handling.md`
- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/28-production.md`
- `knowledge/rest-api/25-performance.md`
- `knowledge/rest-api/24-security.md`
