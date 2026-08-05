---
id: databases/20-performance
topic: databases
slug: performance
title: "Database Performance"
type: doc
order: 20
status: ready
tags: [databases, performance]
related: [databases/07-indexing, databases/08-query-optimization, databases/21-monitoring, databases/16-partitioning, databases/14-replication]
when_to_use: "Read before diagnosing a slow query, sizing a connection pool, or reviewing a data-access path for latency or scale."
---
# Database Performance

## Purpose

This document defines how to make a database fast and keep it fast: reading query plans,
using indexes, controlling the number of round trips, pooling connections, and knowing
when to cache. It is written so an agent can find and fix the real bottleneck instead of
guessing, and can review data-access code for the patterns that quietly destroy latency.

Performance work is measurement, not intuition. The rule is: measure, find the dominant
cost, fix that, measure again. Everything else in this document serves that loop.

## Why It Matters

The database is the most common bottleneck in a system and the hardest to scale away. A
single missing index turns a 2 ms query into a 2 s full scan; an N+1 loop turns one page
load into a thousand round trips. These costs are invisible on a laptop with 100 rows and
catastrophic in production with 100 million — the code "works" in review and falls over
under real load. Because the database is shared, one slow query does not just hurt its own
request; it holds connections, locks, and buffer cache, degrading every other user at
once. Getting this right is the difference between a system that scales and one that
topples on launch day.

## Core Principles

- **Measure before optimizing.** Read the actual query plan (`EXPLAIN ANALYZE`) and the
  real metrics. Never optimize a query you have not profiled — you will fix the wrong thing.
- **Index the columns you filter, join, and sort on.** An index turns an O(n) scan into an
  O(log n) lookup. The cost is slower writes and storage, so index deliberately, not
  everywhere. See [indexing](07-indexing.md).
- **Minimize round trips.** Latency is dominated by the number of queries, not their size.
  One query returning 1,000 rows beats 1,000 queries returning one row each.
- **Fetch only what you need.** Avoid `SELECT *`; select named columns and paginate large
  result sets. Over-fetching wastes I/O, memory, and network on every call.
- **Pool connections.** Opening a connection is expensive and the server has a hard limit.
  A pool reuses connections and caps concurrency; unbounded connections crash the engine.

## Best Practices

- Use `EXPLAIN (ANALYZE, BUFFERS)` to see the plan the optimizer *actually* chose, not the
  one you assumed. Look for sequential scans on large tables and mis-estimated row counts.
- Add **composite indexes in the right column order** (equality columns first, then range/
  sort). A `(tenant_id, created_at)` index serves `WHERE tenant_id = ? ORDER BY created_at`.
- Kill **N+1 queries**: load related rows in one query with a join or an `IN (...)` batch,
  or an ORM eager-load. This is the single most common performance defect.
- Paginate with **keyset (seek) pagination** for deep pages; `OFFSET 100000` still scans
  and discards 100,000 rows every time.
- Keep transactions **short**; long-running transactions hold locks and bloat MVCC, hurting
  everyone. See [query-optimization](08-query-optimization.md).
- Keep table and index statistics fresh (autovacuum/`ANALYZE`) so the planner estimates
  correctly; stale stats produce bad plans.
- Cache **read-heavy, slow-changing** data (with explicit invalidation) — but only after
  the query itself is as fast as it reasonably can be. A cache is not a fix for a bad query.
- Scale reads with **replicas** before sharding; scale writes with [partitioning](16-partitioning.md)
  or [sharding](15-sharding.md) only when a single node is genuinely the limit.

## Examples

**Good Example** — one indexed, batched, paginated query

```sql
-- Composite index matches the filter + sort exactly, so the planner does an index scan.
CREATE INDEX idx_orders_customer_created ON orders (customer_id, created_at DESC);
```

```ts
// Load orders for many customers in ONE round trip (no N+1), select only needed columns,
// and use keyset pagination so page depth does not increase cost.
const orders = await db.query(
  `SELECT id, customer_id, total, created_at
     FROM orders
    WHERE customer_id = ANY($1)
      AND created_at < $2          -- seek cursor, not OFFSET
    ORDER BY created_at DESC
    LIMIT 50`,
  [customerIds, cursor],
);
```

**Bad Example** — N+1 loop, full-row fetch, offset paging

```ts
const customers = await db.query("SELECT * FROM customers");   // over-fetch every column
for (const c of customers) {
  // One query PER customer: 1 + N round trips. 10k customers = 10k queries.
  c.orders = await db.query(
    `SELECT * FROM orders WHERE customer_id = ${c.id}          -- also unindexed + injectable
       ORDER BY created_at DESC OFFSET ${page * 50} LIMIT 50`, // OFFSET rescans every page
  );
}
```

## Common Mistakes

- Optimizing without reading the query plan, then "fixing" a query that was never the cost.
- Missing indexes on `WHERE`/`JOIN`/`ORDER BY` columns, causing full table scans at scale.
- N+1 query loops hidden behind an ORM's lazy loading.
- `SELECT *` and unpaginated result sets that balloon with data growth.
- `OFFSET`-based pagination on deep pages, which rescans and discards all skipped rows.
- No connection pool, or a pool sized larger than the server's connection limit.
- Over-indexing — every extra index slows writes and consumes cache and disk.
- Treating a cache as a substitute for a correct index or query.

## Production Tips

- Enable the **slow query log** (`log_min_duration_statement`, `pg_stat_statements`) and
  review the top queries by total time weekly — the worst offender is rarely the one you'd
  guess. See [monitoring](21-monitoring.md).
- Load-test with **production-scale data volumes**; a plan that index-scans at 1k rows can
  flip to a seq scan at 10M as the optimizer's estimates change.
- Watch cache hit ratio, lock waits, and connection saturation — these predict a cliff
  before latency does.

## AI Review Checklist

- Was the query plan (`EXPLAIN ANALYZE`) read before any optimization was made?
- Do all `WHERE`, `JOIN`, and `ORDER BY` columns have supporting indexes in the right order?
- Are there N+1 loops that should be a single join or batched `IN`/`ANY` query?
- Does the code select named columns and paginate (keyset, not deep `OFFSET`)?
- Are connections pooled, with the pool size within the server's connection limit?
- Are transactions short, and are table statistics kept fresh for the planner?
- Is caching applied only to already-optimized, read-heavy data with real invalidation?

## Related

- `knowledge/databases/07-indexing.md`
- `knowledge/databases/08-query-optimization.md`
- `knowledge/databases/21-monitoring.md`
- `knowledge/databases/16-partitioning.md`
- `knowledge/databases/14-replication.md`
