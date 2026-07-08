---
id: nodejs/27-monitoring
topic: nodejs
slug: monitoring
title: "Monitoring"
type: doc
order: 27
status: ready
tags: [nodejs, monitoring]
related: [nodejs/16-error-handling, nodejs/17-logging, nodejs/19-performance, nodejs/20-memory-management, nodejs/26-deployment]
when_to_use: "Read before adding metrics, tracing, or health checks — or when a production issue is invisible in your telemetry."
---
# Monitoring

## Purpose

This document defines how to make a running Node.js service observable: metrics, traces,
health checks, and alerting. It is written so an agent can instrument a service well
enough that an incident can be detected, located, and explained from telemetry alone —
without adding a `console.log` and redeploying.

Monitoring is the third pillar alongside [logging](17-logging.md) (what happened) and
[error handling](16-error-handling.md) (how failures are caught). Its job is to answer,
in production, *is the system healthy, and if not, where and why?*

## Why It Matters

Node.js hides its most dangerous failures. A blocked event loop, a slow memory leak, a
pool exhaustion — none throw an error; the process keeps answering the health check while
latency climbs and users time out. Without metrics you learn about the outage from
customers, and without traces you cannot tell which of a dozen services caused it. The
cost of poor observability is not just downtime; it is *mean time to resolution* — the
hours spent guessing. Instrumentation is what turns "the site is slow" into "the payment
service's DB pool is saturated."

## Core Principles

- **Instrument the golden signals.** Latency, traffic, errors, and saturation cover most
  incidents. Start there before adding vanity metrics.
- **Watch Node-specific health.** Event-loop delay, heap usage, GC pauses, and active
  handles reveal problems that HTTP metrics miss entirely.
- **Trace across boundaries.** Propagate a trace id (W3C Trace Context) through every hop
  so a request can be reconstructed across services and async jobs.
- **Alert on symptoms, not causes.** Page on user-facing SLO breaches (error rate,
  latency) — not on CPU being high, which is often normal and noisy.
- **Use structured, low-cardinality telemetry.** Metrics with unbounded label values
  (user id, request id) explode storage and cost; keep those in logs/traces.

## Best Practices

- Emit metrics in a standard format — **OpenTelemetry** (vendor-neutral) or a Prometheus
  `/metrics` endpoint via `prom-client` — not a bespoke format that locks you in.
- Track event-loop lag explicitly (`perf_hooks.monitorEventLoopDelay`); rising lag is the
  single best early warning of a blocked or overloaded process.
- Export RED metrics per route: Rate, Errors, Duration (as a histogram, so you get p95/p99,
  not just an average that hides tail latency).
- Give `/health` (liveness: is the process alive?) and `/ready` (readiness: can it serve,
  including dependency checks?) distinct meanings, matching [deployment](26-deployment.md).
- Correlate logs, metrics, and traces with a shared trace id so one click moves between them.
- Set alerts against an SLO with a burn-rate policy; a single spike should not page, a
  sustained breach should.
- Auto-instrument HTTP, DB, and outbound clients with OpenTelemetry rather than
  hand-wrapping every call.
- Never put secrets, tokens, or PII in metric labels, span attributes, or trace names.

## Examples

**Good Example** — event-loop and RED metrics, standard endpoint

```ts
import client from "prom-client";
import { monitorEventLoopDelay } from "node:perf_hooks";

client.collectDefaultMetrics(); // heap, GC, handles — the Node internals that HTTP metrics miss

const h = monitorEventLoopDelay({ resolution: 20 });
h.enable();
new client.Gauge({
  name: "event_loop_delay_p99_ms",
  help: "99th percentile event loop delay",
  collect() { this.set(h.percentile(99) / 1e6); }, // rising p99 = process is overloaded
});

// Duration as a histogram → real p95/p99, with bounded labels (route, not raw URL).
const httpDur = new client.Histogram({
  name: "http_request_duration_seconds",
  help: "request duration",
  labelNames: ["method", "route", "status"], // low cardinality: template path, never the id
  buckets: [0.05, 0.1, 0.3, 1, 3],
});

app.get("/metrics", async (_req, res) => {
  res.set("Content-Type", client.register.contentType);
  res.end(await client.register.metrics());
});
```

**Bad Example** — averages, unbounded labels, cause-based alert

```ts
let total = 0, count = 0;
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => {
    total += Date.now() - start; count++;
    // Average hides the slow tail: p99 can be 5s while the mean stays 80ms.
    metrics.gauge("avg_latency", total / count,
      { url: req.url, userId: req.user?.id }); // per-URL + per-user labels → cardinality explosion
  });
  next();
});
// Pages the on-call at 3am for high CPU during a normal batch job — cause, not symptom.
alertWhen("cpu > 80%");
```

## Common Mistakes

- Reporting average latency instead of a histogram, so tail latency (the user's actual
  experience) is invisible.
- High-cardinality labels (user id, request id, raw URL) that blow up metric storage/cost.
- No event-loop or heap metrics, missing the blocked-loop and memory-leak failure modes.
- Alerting on causes (CPU, memory) instead of user-facing symptoms, producing alert fatigue.
- Liveness and readiness collapsed into one endpoint, so a warming instance gets killed
  or a broken one keeps taking traffic.
- No trace-id propagation, making multi-service incidents unreconstructable.
- Logging PII/secrets into spans or metric labels.

## Production Tips

- Add synthetic checks (an external prober hitting a real endpoint) so you detect total
  outages even when the process cannot report on itself.
- Keep dashboards next to runbooks: each alert should link to the query and the fix steps,
  so responders act instead of investigate from scratch.
- Sample high-volume traces (head or tail sampling) to control cost while keeping the slow
  and errored requests that matter.
- Track [memory](20-memory-management.md) trend over days; leaks reveal themselves as a
  sawtooth that never returns to baseline after GC.

## AI Review Checklist

- Are the golden signals (latency, traffic, errors, saturation) all instrumented?
- Is latency a histogram (p95/p99), not an average?
- Are Node internals — event-loop delay, heap, GC — exported?
- Are metric labels low-cardinality, with no user/request ids or PII?
- Are traces propagated across services and async jobs via a shared trace id?
- Do alerts fire on SLO/symptom breaches with a burn-rate policy, not raw resource use?
- Are liveness and readiness distinct and wired to the orchestrator?

## Related

- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/17-logging.md`
- `knowledge/nodejs/19-performance.md`
- `knowledge/nodejs/20-memory-management.md`
- `knowledge/nodejs/26-deployment.md`
