---
id: sql/23-performance
topic: sql
slug: performance
title: "SQL Performance"
type: doc
order: 23
status: ready
tags: [sql, performance, lower, OFFSET, LIKE, EXISTS, email, ANALYZE]
related: [sql/15-indexes, sql/16-query-planning, sql/17-query-optimization, sql/19-materialized-views, sql/100-common-antipatterns]
when_to_use: "Read before optimizing a slow query, sizing a query for scale, or reviewing SQL that will run against large or growing tables."
---
# SQL Performance

## Purpose

This document defines how to reason about SQL performance: what actually makes
queries slow, how to measure before changing anything, and which levers matter
most. It is written so an agent optimizes based on evidence — the query plan and
real numbers — rather than folklore.

Performance work in SQL is the discipline of doing less work per query: touching
fewer rows, using an index instead of a scan, and letting the engine do set-based
work instead of round-trips. It is closely tied to [indexes](15-indexes.md),
[query planning](16-query-planning.md), and [query optimization](17-query-optimization.md).

## Why It Matters

Database time dominates most application latency, and SQL performance degrades
non-linearly: a query that is fine on 10,000 rows can be unusable on 10 million.
The failure mode is insidious because it passes every test on a small dev
database, then falls over in production once data accumulates. Worse, one slow
query holding locks or saturating I/O can degrade the entire system, not just its
own request. Getting SQL performance right is often the single highest-leverage
thing you can do for an application's responsiveness.

## Core Principles

- **Measure before optimizing.** Read the actual plan (`EXPLAIN ANALYZE`) and find
  where time and rows go. Guessing wastes effort and often makes things slower.
- **The biggest win is an index that turns a scan into a seek.** Most slow OLTP
  queries are missing an index on a filter or join column. See
  [indexes](15-indexes.md).
- **Do work in sets, not row-by-row.** N+1 query patterns and per-row loops turn
  one fast query into thousands of slow ones. Fetch and mutate in batches.
- **Return only what you need.** `SELECT *` over wide tables, unbounded result
  sets, and unfiltered scans move data nobody uses. Project columns; paginate.
- **Beware how performance scales, not just current speed.** Judge a query by its
  plan's complexity against production-sized data, not its wall time on a laptop.

## Best Practices

- Add indexes on columns used in `WHERE`, `JOIN`, and `ORDER BY`; use composite
  indexes ordered to match your predicates, and covering indexes to serve a query
  from the index alone. Every index costs write speed and storage — index for real
  query patterns, not speculatively.
- Kill N+1 patterns: replace a loop of per-row queries with one set-based `JOIN`
  or `IN`/`ANY` batch. This is usually the largest real-world speedup.
- Keep predicates sargable: avoid wrapping the indexed column in a function
  (`WHERE lower(email) = ...` defeats an index on `email`; index the expression or
  store normalized). Compare against constants/parameters the index can use.
- Paginate large result sets; prefer keyset (seek) pagination over large `OFFSET`,
  which forces the engine to scan and discard the skipped rows.
- Prefer `EXISTS` over `IN (subquery)` for semi-joins on large sets, and `JOIN`
  over correlated subqueries the planner cannot flatten.
- Cache expensive, tolerant-of-staleness aggregations in a
  [materialized view](19-materialized-views.md) rather than recomputing per request.
- Keep transactions short; long-running transactions hold locks and bloat, slowing
  every other writer. See [transactions](14-transactions.md).

## Examples

**Good Example** — one set-based query with a supporting index

```sql
-- Index the join/filter columns so this is an index seek, not a full scan.
CREATE INDEX idx_orders_customer_created ON orders (customer_id, created_at);

-- Fetch all orders for a page of customers in ONE round-trip, projecting
-- only needed columns. Scales because the index answers the predicate directly.
SELECT o.id, o.customer_id, o.total_cents, o.created_at
FROM orders o
WHERE o.customer_id = ANY($1)      -- batch of ids, not one query per customer
  AND o.created_at >= $2
ORDER BY o.created_at DESC
LIMIT 50;
```

**Bad Example** — N+1 loop, non-sargable filter, unbounded projection

```sql
-- Called once PER customer in an application loop: N+1 round-trips.
-- SELECT * drags every column over the wire; lower() defeats any index on email;
-- no LIMIT means an unbounded result set as the table grows.
SELECT *
FROM orders
WHERE lower(customer_email) = lower($1);   -- function on column -> full scan
```

## Common Mistakes

- Optimizing without reading the query plan, so effort lands on the wrong bottleneck.
- Missing an index on a filter/join column, forcing full table scans.
- N+1 query patterns from per-row loops instead of one set-based query.
- Non-sargable predicates (function on the indexed column, leading `%` in `LIKE`)
  that silently prevent index use.
- `SELECT *` and unbounded results that move and buffer data nobody needs.
- Large `OFFSET` pagination that scans and throws away skipped rows.
- Testing performance only on a tiny dev dataset, missing the non-linear cliff.
- Over-indexing: adding indexes for queries that do not exist, taxing every write.

## Production Tips

- Turn on slow-query logging and review the top offenders regularly; optimize by
  measured impact, not intuition.
- Keep table statistics current (`ANALYZE`) so the planner makes good choices; a
  bad plan is often a stale-statistics problem, not a query problem.
- Load-test against production-scale data volumes before shipping a new query path.
- Watch for lock contention and connection-pool exhaustion — often the real cause
  of "the database is slow" is one long transaction, not query cost.

## AI Review Checklist

- Was the actual query plan (`EXPLAIN ANALYZE`) consulted before optimizing?
- Are `WHERE`/`JOIN`/`ORDER BY` columns backed by appropriate indexes?
- Are there N+1 patterns that should be one set-based query?
- Are predicates sargable (no function-wrapped indexed columns, no leading `%`)?
- Does the query project only needed columns and bound its result set?
- Is pagination keyset-based rather than large `OFFSET`?
- Was performance judged against production-scale data, not a tiny dev set?

## Related

- `knowledge/sql/15-indexes.md`
- `knowledge/sql/16-query-planning.md`
- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/19-materialized-views.md`
- `knowledge/sql/100-common-antipatterns.md`
