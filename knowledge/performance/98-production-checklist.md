---
id: performance/98-production-checklist
topic: performance
slug: production-checklist
title: "Performance Production Checklist"
type: doc
order: 98
status: ready
tags: [performance, production-checklist]
related: [performance/25-production-monitoring, performance/17-monitoring, performance/22-load-testing, performance/20-capacity-planning, performance/99-ai-review-checklist]
when_to_use: "Read before promoting any performance-sensitive service or change to production."
---
# Performance Production Checklist

## Purpose

This is the go/no-go checklist for putting a performance-sensitive system into production.
Every item is a verifiable yes/no an agent or reviewer can confirm against the running
system, its dashboards, or its config — not advice, but a gate. If an item is "no", the
honest answer is to fix it or consciously accept the risk in writing. Use it alongside the
[AI review checklist](99-ai-review-checklist.md), which reviews the change; this one reviews
operational readiness under load.

## Why It Matters

Systems fall over in production for boringly repetitive reasons: no timeout so one slow
dependency stalls every thread, an N+1 query that is invisible at 10 rows and fatal at
10,000, an unbounded cache that OOMs the box, no dashboard so nobody sees latency climb
until users complain. Each is trivially preventable and each has taken down real systems. A
checklist turns "we probably handled that" into "we verified that", and moves the cost of
finding a gap from a 3 a.m. incident to five minutes during review.

## Targets & Budget

**Rules:** [Budget](23-performance-budget.md) · [Metrics](02-metrics.md)

- [ ] A **performance budget** exists with explicit latency (p95/p99) and throughput targets
  per critical path (see [performance budget](23-performance-budget.md)).
- [ ] The change was measured against the budget, and the after-numbers are recorded.
- [ ] Targets are set on **percentiles**, not averages, and match real user-facing paths.

## Load & Capacity

**Rules:** [Load Testing](22-load-testing.md) · [Capacity Planning](20-capacity-planning.md)

- [ ] The system was **load-tested** at expected peak plus headroom, and met its targets
  under that load (see [load testing](22-load-testing.md)).
- [ ] **Capacity** is sized from measured per-request cost, with a known scaling limit and
  headroom for spikes (see [capacity planning](20-capacity-planning.md)).
- [ ] The service **scales horizontally** (stateless, or state externalized) so more traffic
  can be met by adding instances, not just bigger boxes.
- [ ] Behavior under overload is defined: **shed load / back-pressure / rate-limit** rather
  than accept work it cannot finish and degrade for everyone.

## Data & Queries

**Rules:** [Query Optimization](15-query-optimization.md) · [— Database Access](13-database-performance.md)

- [ ] Every query on the hot path is **indexed** for its access pattern; `EXPLAIN` shows no
  full scans on large tables (see [query optimization](15-query-optimization.md)).
- [ ] No **N+1 query** patterns on request paths; related data is batched or joined.
- [ ] List and search endpoints are **paginated or bounded**; no query can return unbounded
  rows.
- [ ] Connection **pools** are sized and bounded; the app cannot exhaust the database's
  connection limit (see [database performance](13-database-performance.md)).

## Caching & Memory

**Rules:** [Caching](08-caching.md) · [Memory](04-memory.md)

- [ ] Every cache has a defined **invalidation strategy or TTL**; nothing is cached forever
  by accident (see [caching](08-caching.md)).
- [ ] Caches and buffers are **bounded** (max size / eviction), so they cannot grow until the
  process is killed.
- [ ] Cache **stampede** protection exists on expensive keys (single-flight, jittered TTL).
- [ ] There are no known **memory leaks**; memory is stable under a soak test (see
  [memory](04-memory.md)).

## Resilience Under Latency

**Rules:** [API Performance](14-api-performance.md) · [Scalability](21-scalability.md)

- [ ] Every outbound network call has a **timeout** so one slow dependency cannot stall the
  caller indefinitely.
- [ ] Slow or failing dependencies are isolated (timeout, circuit breaker, fallback) so they
  degrade one feature, not the whole request.
- [ ] Expensive or long work is **async / offloaded** from the request path where it does not
  need to be synchronous.

## Assets & Delivery (web)

**Rules:** [Images](11-images.md) · [Code Splitting](10-code-splitting.md)

- [ ] Static assets are **compressed** (gzip/brotli), **cache-headed**, and served from a
  CDN where applicable.
- [ ] Images are sized and modern-format; fonts are subset and `font-display` is set (see
  [images](11-images.md), [fonts](12-fonts.md)).
- [ ] Client bundles are **code-split** and non-critical work is deferred; Core Web Vitals
  meet target (see [web vitals](18-web-vitals.md)).

## Observability

**Rules:** [Production Monitoring](25-production-monitoring.md) · [Monitoring](17-monitoring.md)

- [ ] Latency (with percentiles), throughput, error rate, and saturation are **emitted as
  metrics** and visible on a dashboard (see [monitoring](17-monitoring.md)).
- [ ] **Alerts** fire on budget breaches (p95 over target, error rate, saturation) before
  users are widely affected.
- [ ] Traces or timing spans exist for slow paths so a regression can be **localized**
  without redeploying (see [production monitoring](25-production-monitoring.md)).
- [ ] A **regression benchmark** guards hot paths in CI, so a silent slowdown fails the build.

## AI Review Checklist

- Does the change have a recorded before/after measurement against a stated budget?
- Was it load-tested at peak, and does it scale horizontally with defined overload behavior?
- Are hot-path queries indexed, paginated, and free of N+1s, with bounded connection pools?
- Does every cache have invalidation/TTL and a size bound, and is memory stable under soak?
- Does every outbound call have a timeout and isolation from slow dependencies?
- Are latency percentiles, error rate, and saturation on a dashboard with alerts wired?

## Related

- `knowledge/performance/25-production-monitoring.md`
- `knowledge/performance/17-monitoring.md`
- `knowledge/performance/22-load-testing.md`
- `knowledge/performance/20-capacity-planning.md`
- `knowledge/performance/99-ai-review-checklist.md`
