---
id: graphql/98-production-checklist
topic: graphql
slug: production-checklist
title: "GraphQL Production Checklist"
type: doc
order: 98
status: ready
tags: [graphql, production-checklist]
related: [graphql/17-security, graphql/22-performance, graphql/25-monitoring, graphql/27-production, graphql/29-schema-evolution]
when_to_use: "Read before shipping a GraphQL API to production or promoting it to a new environment."
---
# GraphQL Production Checklist

## Purpose

A verifiable, grouped checklist to run before a GraphQL API serves real traffic. Every
item is a yes/no an engineer or agent can confirm by reading code or config. If an item
is unchecked, the service is not production-ready. Do not treat this as aspirational —
each unchecked box is a known incident waiting to happen.

## Why It Matters

GraphQL moves query composition to the client, which means the failure modes only appear
under real, adversarial, or high-volume traffic — a query no one wrote in staging can
fan out into a database meltdown. This list front-loads those failures into a checklist
so they are caught before launch, not during an outage.

## Schema and Contract

- [ ] The production schema is published to a registry and diffed against the last
      shipped version in CI (breaking changes fail the build).
- [ ] All removed or renamed fields went through `@deprecated` first and show zero usage
      in telemetry.
- [ ] Non-null output fields are only ones the server can always resolve; downstream-
      dependent fields are nullable.
- [ ] Introspection is disabled in production (or gated to authenticated internal tools).

## Query Cost and Safety

- [ ] Maximum query **depth** is enforced and rejects overly nested queries.
- [ ] Query **complexity/cost** limits are enforced before execution.
- [ ] A per-operation **timeout** is set and cancels in-flight resolver work.
- [ ] All list fields are **paginated connections** with an enforced max page size.
- [ ] **Batched/aliased query** abuse is bounded (limit on operations and aliases).
- [ ] Persisted queries or an operation allowlist is in place for untrusted clients.

## Performance

- [ ] **DataLoader** (or equivalent per-request batching) covers every entity fetched in
      a list context; no N+1 remains under load test.
- [ ] Resolver-level and downstream **caching** is configured with sane TTLs and keys.
- [ ] The service has been **load-tested** with the deepest/most expensive allowed query.
- [ ] Slow-query and slow-resolver thresholds are defined and alert.

## Security

- [ ] Authentication is verified in **context**, once per request, not per resolver ad hoc.
- [ ] Authorization is enforced at the **field/type** level, not only at the entry query.
- [ ] Error responses are **sanitized** — no stack traces, SQL, or internal paths leak
      to clients in production.
- [ ] CSRF/CORS is configured; mutations require the correct content-type and origin.
- [ ] Rate limiting is applied per client/identity on the GraphQL endpoint.
- [ ] Input types have length/range/format validation before hitting business logic.

## Errors and Observability

- [ ] Expected failures are modeled as **result unions/data**; only faults become GraphQL
      errors.
- [ ] Errors carry stable, documented **error codes** in `extensions`.
- [ ] Per-field **tracing** (resolver timing) is exported to APM.
- [ ] Structured logs include operation name, viewer id, and cost — never raw variables
      containing secrets.
- [ ] Dashboards and alerts exist for error rate, p95 latency, and rejected-by-cost count.

## Operations

- [ ] Health and readiness endpoints exist and reflect downstream dependency health.
- [ ] Graceful shutdown drains in-flight operations before exit.
- [ ] Subscriptions (if used) have connection limits, auth on connect, and backpressure.
- [ ] Rollback plan exists; schema changes are backward-compatible for in-flight clients.

## AI Review Checklist

- Are depth, complexity, and timeout limits all present and enforced pre-execution?
- Is every list a bounded connection and every entity fetch batched?
- Is authorization enforced at field level and are errors sanitized?
- Are breaking schema changes blocked in CI against the published schema?
- Do dashboards and alerts cover latency, error rate, and cost rejections?

## Related

- `knowledge/graphql/17-security.md`
- `knowledge/graphql/22-performance.md`
- `knowledge/graphql/25-monitoring.md`
- `knowledge/graphql/27-production.md`
- `knowledge/graphql/29-schema-evolution.md`
