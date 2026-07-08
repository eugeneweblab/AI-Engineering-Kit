---
id: devops/21-performance
topic: devops
slug: performance
title: "Performance"
type: doc
order: 21
status: ready
tags: [devops, performance]
related: [devops/20-scalability, devops/12-monitoring, devops/13-observability, devops/05-build-pipelines]
when_to_use: "Read before optimizing latency/throughput, setting SLOs, or diagnosing a slow service."
---
# Performance

## Purpose

This document defines how to make a system fast and keep it fast: how to measure latency
and throughput, where to optimize, and how to avoid the two classic failure modes —
guessing instead of profiling, and optimizing the wrong thing. It is written so an agent
can improve performance with evidence, not intuition.

Performance answers "how fast is a single unit of work, and how much can we do per second?".
It is distinct from [scalability](20-scalability.md) (handling more load by adding
resources): a system can be slow yet scalable, or fast yet unable to scale. Measure and
fix them separately.

## Why It Matters

Performance is a feature users feel on every interaction, and small regressions compound
into churn, cost, and incidents. But most performance work is wasted because it targets
code that was never the bottleneck — Amdahl's law caps the payoff of optimizing anything
that is not on the critical path. Worse, teams optimize against **averages**, which hide
the slow tail; the p99 request is the one that times out, retries, and cascades. Real
performance work is disciplined: measure, find the dominant cost, fix it, measure again.

## Core Principles

- **Measure before optimizing.** Profile the real workload to find where time actually
  goes. Intuition about hotspots is usually wrong; the cost is the hours you waste on the
  wrong function.
- **Optimize the critical path only.** Speeding up code that is not the bottleneck yields
  nothing. Fix the dominant term first, then re-measure — the bottleneck moves.
- **Track percentiles, not averages.** p50/p95/p99 tell the real story; a good average can
  hide a terrible tail. Set SLOs on p95/p99.
- **Latency and throughput are a trade-off.** Batching raises throughput but adds latency;
  parallelism cuts latency but adds contention. Optimize for the one that matters to users.
- **The fastest work is work you do not do.** Caching, avoiding N+1 queries, and removing
  needless round-trips beat micro-optimizing the work itself.

## Best Practices

- **Profile with real data and realistic concurrency.** Flame graphs and DB query plans
  reveal the true cost; a benchmark on empty tables lies. `EXPLAIN ANALYZE` your hot queries.
- **Kill N+1 queries** — the single most common backend performance bug. Batch, join, or
  eager-load. One query for N rows, not N+1 queries.
- **Cache the expensive and stable**, with explicit TTLs and invalidation. Cache close to
  the consumer (in-process → Redis → CDN). The cost is staleness — bound it deliberately.
- **Index for your access patterns** and verify the planner uses the index; add covering
  indexes for hot read paths. An unused index only slows writes.
- **Set timeouts and budgets** per request (a latency budget split across dependencies) so
  one slow call cannot blow the whole SLO.
- **Do slow/optional work asynchronously** off the request path (emails, thumbnails,
  analytics). Return fast; process later.
- **Guard performance in CI** with a benchmark or load-test gate on critical endpoints so
  regressions are caught before release, not by users.
- **Continuously profile in production** (sampling profilers, distributed traces) — lab
  numbers rarely match production data shapes and cache states.

## Examples

**Good Example** — one batched query, measured, with a latency budget

```ts
// One query for N users instead of N+1. Verified with EXPLAIN ANALYZE on prod-shaped data.
const users = await db.query(
  "SELECT * FROM users WHERE org_id = ANY($1)", [orgIds]
); // O(1) round-trips regardless of N → the dominant cost is removed

// Bound the call so a slow dependency cannot blow the request's latency budget.
const profile = await fetchProfile(id, { timeout: 200 }); // 200ms of a 500ms p95 budget
```

```bash
# Prove the fix on the critical path before and after, at realistic concurrency.
autocannon -c 50 -d 30 https://api.local/orders   # compare p95/p99, not just avg
```

**Bad Example** — N+1, unmeasured, optimized in the wrong place

```ts
const orders = await db.query("SELECT * FROM orders WHERE user_id = $1", [id]);
for (const o of orders) {
  // One query PER order: N+1. For 200 orders that is 201 round-trips.
  o.items = await db.query("SELECT * FROM items WHERE order_id = $1", [o.id]);
}

// Meanwhile someone hand-optimizes this string concat "for speed" — it is 0.1% of the time.
const label = names.reduce((a, b) => a + "," + b, ""); // wrong target; measure first
// No timeout anywhere; one slow item query makes the whole endpoint hang.
```

## Common Mistakes

- Optimizing without profiling, then "fixing" code that was never the bottleneck.
- Reporting averages, hiding the p99 tail that actually causes timeouts.
- N+1 queries — the default performance bug of ORM-heavy code.
- Caching without invalidation or TTL, trading a speed bug for a correctness bug.
- Benchmarking on empty/tiny datasets that do not exercise the real query plan.
- No per-request timeout/budget, so one slow dependency blows the whole SLO.
- Micro-optimizing CPU while the real cost is I/O, locks, or network round-trips.

## Production Tips

- Attach **distributed tracing** so you can see where a slow request spends its time across
  services instead of guessing.
- Alert on **p95/p99 SLO burn**, and keep a small set of **performance-critical endpoints**
  under a CI benchmark gate.
- Re-profile after every major data-growth milestone; performance that held at 1M rows can
  collapse at 100M when an index stops fitting in memory.

## AI Review Checklist

- Was the bottleneck identified by profiling real, prod-shaped data before optimizing?
- Are SLOs and reports based on p95/p99, not averages?
- Are N+1 query patterns eliminated on hot paths, verified with the query plan?
- Do caches have explicit TTL and invalidation, and is staleness bounded?
- Does every request carry a latency budget with per-dependency timeouts?
- Is slow/optional work moved off the request path?
- Is there a CI performance gate on critical endpoints to catch regressions?

## Related

- `knowledge/devops/20-scalability.md`
- `knowledge/devops/12-monitoring.md`
- `knowledge/devops/13-observability.md`
- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/22-testing.md`
