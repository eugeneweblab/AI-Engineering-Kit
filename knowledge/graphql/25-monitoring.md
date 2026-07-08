---
id: graphql/25-monitoring
topic: graphql
slug: monitoring
title: "Monitoring"
type: doc
order: 25
status: ready
tags: [graphql, monitoring]
related: [graphql/20-error-handling, graphql/22-performance, graphql/15-n1-problem, graphql/27-production, graphql/24-testing]
when_to_use: "Read before adding metrics, tracing, or logging to a GraphQL server, or when debugging why a query is slow in production."
---
# Monitoring

## Purpose

This document defines how to observe a GraphQL API in production: what to measure, how to
attribute latency and errors to individual fields and operations, and how to log without
leaking data. It is written so an agent can instrument a server that stays debuggable at
scale instead of one that reports a single meaningless "average latency."

GraphQL breaks the assumptions of REST monitoring. One URL serves every operation, and one
request runs many resolvers, so per-route dashboards tell you nothing. You must monitor at
the granularity of *operation* and *field*, not *endpoint*.

## Why It Matters

Because every operation POSTs to a single `/graphql` path, HTTP-level metrics collapse a
fast health check and a catastrophic nested query into the same bucket. Errors are worse:
resolvers fail inside a `200` response, so your HTTP error rate reads `0%` while clients see
broken fields. Without per-field tracing, "the API is slow" is unactionable — the slowness
is one N+1 resolver among fifty. Good instrumentation turns these invisible failures into
named operations, named fields, and named error codes you can alert on.

## Core Principles

- **Name and attribute every operation.** Require a unique operation name and key all
  metrics by it. Anonymous operations are un-monitorable.
- **Errors live in the payload, not the status code.** Track the `errors` array and the
  `extensions.code`, not the HTTP status. HTTP `200` is not "success."
- **Trace at the field level.** Emit spans per resolver so you can see which field, in which
  operation, spent the time. Aggregate request latency hides the culprit.
- **Log the operation, never the data.** Log operation name, variables shape, error code,
  and timing — never variable *values*, results, tokens, or PII.
- **Measure what users experience.** Alert on p95/p99 per operation and on error *rate* per
  operation, not on server-wide averages that mask tail latency.

## Best Practices

- Emit these metrics keyed by operation name: request count, error count, resolved-field
  count, and duration histograms (p50/p95/p99). Averages hide the tail; use histograms.
- Capture per-resolver spans with OpenTelemetry so a slow field shows up as a slow span
  inside the operation's trace. This is how you find N+1 (see [the N+1 problem](15-n1-problem.md)).
- Classify errors by `extensions.code` (e.g. `FORBIDDEN`, `BAD_USER_INPUT`, `INTERNAL`).
  Alert only on server-fault codes; client-input errors are expected and should not page.
- Track query complexity/depth per operation and alert when it spikes — a sudden jump often
  means an abusive or accidentally expensive client. See [performance](22-performance.md).
- Persist a rolling registry of operations you actually receive; use it to prioritize what
  to optimize and to build post-deploy smoke tests. See [testing](24-testing.md).
- Redact variables at the logging boundary with an allowlist, so a new sensitive argument
  is redacted by default rather than logged by accident.

## Examples

**Good Example** — per-field span, per-operation metric, redacted log

```ts
// Envelop/Apollo plugin: one span per resolver, one metric per operation.
const monitoringPlugin = {
  onExecute({ args }) {
    const op = args.operationName ?? "anonymous";
    const start = performance.now();
    return {
      onResolverCalled({ info }) {
        const span = tracer.startSpan(`${info.parentType.name}.${info.fieldName}`);
        return () => span.end(); // field-level timing → find the slow resolver
      },
      onExecuteDone({ result }) {
        const code = firstErrorCode(result); // read errors[], not HTTP status
        metrics.observe("gql_op_ms", performance.now() - start, { op, code });
        logger.info("graphql", { op, code, ms: performance.now() - start });
        // Note: no variable values, no result data — only names, codes, timing.
      },
    };
  },
};
```

**Bad Example** — HTTP-level metrics, logs the payload

```ts
app.post("/graphql", (req, res, next) => {
  const start = Date.now();
  res.on("finish", () => {
    // Every operation lands on the same route → one useless latency number.
    metrics.observe("http_ms", Date.now() - start, { route: "/graphql" });
    // status is 200 even when resolvers threw → error rate always reads 0%.
    metrics.increment("http_status", { status: res.statusCode });
    logger.info("req", { body: req.body }); // logs variables → leaks tokens/PII
  });
  next();
});
```

## Common Mistakes

- Monitoring the `/graphql` route as one endpoint, so all operations blur together.
- Using HTTP status for error rate, which stays `0%` while resolvers fail inside `200`.
- Reporting average latency instead of p95/p99, hiding the tail that users feel.
- Logging full request bodies or results, leaking tokens, PII, and secrets.
- Allowing anonymous operations, which cannot be attributed or alerted on.
- Paging on client-input errors (`BAD_USER_INPUT`), training the team to ignore alerts.
- No field-level tracing, so "it's slow" never narrows to a specific resolver.

## Production Tips

- Sample traces (e.g. 100% of errors, 5% of successes) to control cost while keeping every
  failure fully traced.
- Feed the operation registry from real traffic into your CI smoke tests and complexity
  budgets so monitoring and testing share one source of truth.
- Correlate a `traceId` into `errors[].extensions` (safe, non-sensitive) so a client bug
  report maps directly to a server trace. See [error handling](20-error-handling.md).

## AI Review Checklist

- Are metrics keyed by operation name rather than by the shared `/graphql` route?
- Is the error rate derived from the `errors` array and `extensions.code`, not HTTP status?
- Are there per-resolver spans so a slow field is attributable?
- Do latency alerts use p95/p99 per operation instead of a global average?
- Are logs free of variable values, result data, tokens, and PII?
- Are anonymous operations rejected or flagged so everything is attributable?
- Do client-input error codes stay out of paging alerts?

## Related

- `knowledge/graphql/20-error-handling.md`
- `knowledge/graphql/22-performance.md`
- `knowledge/graphql/15-n1-problem.md`
- `knowledge/graphql/27-production.md`
- `knowledge/graphql/24-testing.md`
