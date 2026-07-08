---
id: prisma/26-observability
topic: prisma
slug: observability
title: "Observability"
type: doc
order: 26
status: ready
tags: [prisma, observability]
related: [prisma/15-performance, prisma/20-debugging, prisma/25-production, prisma/18-error-handling, prisma/13-middleware]
when_to_use: "Read before instrumenting a Prisma app with logging, metrics, or tracing, or when diagnosing slow or failing queries in production."
---
# Observability

## Purpose

This document defines how to make Prisma's behavior visible: query logging, metrics
(pool saturation, query counts, durations), and distributed tracing. The goal is that
when the database is the bottleneck, you can prove it and locate the exact query — from
telemetry, not from guesswork.

## Why It Matters

Prisma hides SQL, which is a feature until something is slow. Without instrumentation the
only signal is "the endpoint is slow," and the query builder gives you no way to see the
N+1 loop, the missing index, or the pool that is 100% checked out. Observability turns an
opaque ORM into a diagnosable one: a trace shows the query inside the request span, a
metric shows the pool draining before requests hang, and structured logs show the exact
statement — without ever leaking the parameter values, which are user data.

## Core Principles

- **Emit events, not `console.log`.** Configure the client's `log` as event emitters and
  route them into your structured logger with correlation IDs.
- **Trace queries inside request spans.** Use OpenTelemetry so each query is a child span
  of the HTTP request; that is what reveals N+1 and slow statements in context.
- **Watch the pool, not just the queries.** Connection-pool saturation is the metric that
  predicts outages; individual query time does not.
- **Never log parameters with PII.** Query text is safe to log; bound values are user
  data. Log the statement, redact the params.
- **Measure in the database's terms.** Correlate Prisma timings with the DB's own slow
  query log and index stats; the ORM view alone is incomplete.

## Best Practices

- Set `log: [{ level: "query", emit: "event" }, "warn", "error"]` and subscribe with
  `prisma.$on("query", …)` to capture duration and target per query.
- Enable the `tracing` (OpenTelemetry) integration via `@prisma/instrumentation` and
  register it with your OTel SDK so spans nest under incoming requests.
- Enable metrics (`previewFeatures = ["metrics"]` where required) and export
  `prisma.$metrics.json()` — pool busy/idle counts, query totals, histograms — to your
  metrics backend on a scrape or interval.
- Add a slow-query threshold in the query listener: log at `warn` when
  `event.duration > N ms`, so noisy fast queries do not drown the signal.
- Propagate a request/trace ID into logs so a slow query can be tied back to the user
  request and the full trace.
- Alert on pool saturation (`prisma_pool_connections_busy` near the limit) and on
  `P2024` pool-timeout errors — both mean requests are about to queue.
- Keep log verbosity env-driven; `query`-level logging is high volume and belongs behind
  a flag, not on by default in production.

## Examples

**Good Example** — event logging with slow-query flag and redacted params

```ts
import { PrismaClient } from "@prisma/client";
import { logger } from "./logger";

const prisma = new PrismaClient({
  log: [{ level: "query", emit: "event" }, "warn", "error"],
});

prisma.$on("query", (e) => {
  // Log the statement and timing; NEVER e.params — those are user values.
  const level = e.duration > 200 ? "warn" : "debug";
  logger[level]({ msg: "prisma_query", query: e.query, ms: e.duration });
});

// Export pool + query metrics to the monitoring backend on a schedule.
setInterval(async () => {
  logger.info({ msg: "prisma_metrics", metrics: await prisma.$metrics.json() });
}, 15_000);
```

**Bad Example** — console logging that leaks data and hides the pool

```ts
const prisma = new PrismaClient({ log: ["query"] }); // prints to stdout, unstructured

prisma.$on("query" as any, (e: any) => {
  console.log(e.query, e.params); // params contain emails, tokens → PII in logs
});
// No metrics, no tracing: when the pool saturates, requests just hang with no signal.
```

## Common Mistakes

- Leaving `log: ["query"]` on stdout in production — unstructured, uncorrelated, noisy.
- Logging `e.params`, spilling user data and secrets into the log store.
- Instrumenting query durations but never the connection pool, so saturation is invisible.
- No trace context, so a slow query cannot be tied to the request that caused it.
- Treating every query log equally instead of flagging slow ones against a threshold.
- Turning on verbose logging globally and drowning real signals (and paying the cost).

## Production Tips

- Build a dashboard from `$metrics`: pool busy vs. limit, query rate, p95/p99 duration.
  The pool panel is your early-warning system.
- Sample query tracing under high load rather than tracing 100%; keep the errors and slow
  spans, drop the rest.
- Cross-reference Prisma slow-query logs with `pg_stat_statements` to find the missing
  index. See [performance](15-performance.md) and [indexes](16-indexes.md).

## AI Review Checklist

- Is the client's `log` configured as events routed to a structured logger, not stdout?
- Are query parameters excluded from logs (statement text only)?
- Is OpenTelemetry tracing enabled so queries nest under request spans?
- Are `$metrics` exported, including pool busy/idle counts?
- Is there a slow-query threshold that raises the log level?
- Is there an alert on pool saturation and `P2024` timeouts?
- Is query-level logging behind an env flag rather than always on?

## Related

- `knowledge/prisma/15-performance.md`
- `knowledge/prisma/20-debugging.md`
- `knowledge/prisma/25-production.md`
- `knowledge/prisma/18-error-handling.md`
- `knowledge/prisma/13-middleware.md`
