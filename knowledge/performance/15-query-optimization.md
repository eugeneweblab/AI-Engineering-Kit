---
id: performance/15-query-optimization
topic: performance
slug: query-optimization
title: "Query Optimization"
type: doc
order: 15
status: ready
tags: [performance, query-optimization]
related: [performance/13-database-performance, performance/16-profiling, performance/14-api-performance, performance/08-caching, performance/02-metrics]
when_to_use: "Read before writing a complex SQL query, adding an index, or diagnosing one specific slow statement."
---
# Query Optimization

## Purpose

This document defines how to make a single database query fast: how to read a query
plan, when an index helps, why a query scans instead of seeks, and which query shapes
defeat the optimizer. It is written so an agent can take one slow statement and make
it fast, guided by evidence from the planner rather than guesswork.

This is the *statement-level* companion to [database performance](13-database-performance.md),
which covers the system-level concerns (pooling, transactions, schema). Start here
when you have one query to fix; start there when the whole data layer is slow.

## Why It Matters

A query optimizer chooses a plan based on indexes and statistics, and small changes to
the query text flip it between a millisecond index seek and a multi-second full scan.
The difference is invisible in the SQL — both queries return the right answer — so the
only way to know which you wrote is to read the plan. Because query cost scales with
data size, a plan that scans works perfectly in development and falls over in
production. Learning to read `EXPLAIN ANALYZE` is the highest-leverage skill in backend
performance: it turns "the app is slow" into "this exact node scanned 2M rows."

## Core Principles

- **Read the plan, do not guess.** `EXPLAIN ANALYZE` shows what the database actually
  did — scans, seeks, join methods, and where the time and rows went. Optimize the
  most expensive node, not the query you *think* is slow.
- **Seek, do not scan.** A `Seq Scan` (or full table scan) on a large table filtered
  by a selective predicate means a missing or unusable index. That is the fix.
- **Keep predicates sargable.** Wrapping an indexed column in a function or applying
  it to the leading edge of an expression disables the index. Transform the constant
  side instead of the column side.
- **Selectivity drives everything.** An index only helps when the predicate eliminates
  most rows. Indexing a low-cardinality column (a boolean) rarely helps.
- **Estimated vs actual rows reveal stale stats.** A large gap means the planner is
  working from bad statistics and choosing a bad plan; refresh them.

## Best Practices

- Run `EXPLAIN (ANALYZE, BUFFERS)` on the real data shape and look for `Seq Scan` on
  big tables, large **estimated-vs-actual row** gaps, and expensive sort/hash nodes.
- Add a **composite index** matching the query's equality columns first, then one
  range or sort column — the planner uses a left-to-right prefix of the index.
- Use a **covering index** (include the selected columns) so the query is answered
  from the index alone (`Index Only Scan`), skipping the table fetch.
- Keep predicates **sargable**: write `created_at >= $1 AND created_at < $2` instead of
  `DATE(created_at) = $1`; write `col = $1` instead of `col + 0 = $1`.
- Replace correlated subqueries and `SELECT DISTINCT`-to-dedupe with explicit `JOIN` /
  `GROUP BY` when the plan shows repeated per-row execution.
- Keep table **statistics fresh** (`ANALYZE`) after bulk loads so the planner estimates
  correctly; autovacuum settings matter for write-heavy tables.
- For deep pagination use **keyset/seek** (`WHERE id < $last ORDER BY id LIMIT n`)
  instead of `OFFSET`, which the planner must still walk past.

## Examples

**Good Example** — sargable predicate, composite index, verified plan

```sql
-- Index chosen to match the query: equality column first, range/sort column last.
CREATE INDEX idx_orders_user_created ON orders (user_id, created_at DESC);

EXPLAIN ANALYZE
SELECT id, total
FROM orders
WHERE user_id = $1               -- equality on leading index column
  AND created_at >= $2           -- sargable range: index can seek the boundary
ORDER BY created_at DESC
LIMIT 20;
-- Plan: Index Scan using idx_orders_user_created → seeks, reads ~20 rows, no sort.
```

**Bad Example** — non-sargable predicate defeats the index

```sql
EXPLAIN ANALYZE
SELECT * FROM orders                        -- SELECT * prevents an index-only scan
WHERE DATE(created_at) = $1                 -- function on the column disables the index
  AND user_id::text = $2;                   -- cast on the column also disables it
ORDER BY created_at DESC
OFFSET 100000 LIMIT 20;                      -- OFFSET walks 100k rows before returning
-- Plan: Seq Scan on orders (2M rows) + Sort → seconds, and slower as data grows.
```

## Common Mistakes

- Adding indexes by guessing instead of reading `EXPLAIN ANALYZE` first.
- Wrapping an indexed column in a function or cast, silently disabling the index.
- A composite index whose column order does not match the query's predicates.
- Indexing a low-selectivity column where a scan is actually cheaper.
- Ignoring a large estimated-vs-actual row gap caused by stale statistics.
- `OFFSET` pagination that the planner must walk through row by row.
- Over-indexing: every index slows writes and consumes memory; add only what plans need.

## Production Tips

- Capture plans from production data volumes, not a small dev database — a `Seq Scan`
  can be the *right* plan on 1,000 rows and catastrophic on 10M.
- Enable the slow-query log and the database's statement-statistics view
  (`pg_stat_statements` or equivalent) to find the queries worth optimizing at all.
- Re-check the plan after data grows; a query that seeks today can flip to a scan as
  cardinality and statistics change.

## AI Review Checklist

- Was the plan inspected with `EXPLAIN ANALYZE` before changing indexes or SQL?
- Are all predicates sargable (no functions/casts on indexed columns)?
- Does the composite index column order match the query's equality-then-range shape?
- Is `SELECT *` avoided so a covering/index-only scan is possible?
- Is deep pagination done with keyset seeks rather than large `OFFSET`s?
- Are table statistics fresh, and is the estimated-vs-actual row count close?

## Related

- `knowledge/performance/13-database-performance.md`
- `knowledge/performance/16-profiling.md`
- `knowledge/performance/14-api-performance.md`
- `knowledge/performance/08-caching.md`
- `knowledge/performance/02-metrics.md`
