---
id: sql/16-query-planning
topic: sql
slug: query-planning
title: "Query Planning"
type: doc
order: 16
status: ready
tags: [sql, query-planning]
related: [sql/17-query-optimization, sql/15-indexes, sql/23-performance, sql/05-joins, sql/100-common-antipatterns]
when_to_use: "Read before diagnosing a slow query, or whenever you need to interpret an EXPLAIN plan."
---
# Query Planning

## Purpose

This document defines how to read what the database actually does with a query: how to
run `EXPLAIN`/`EXPLAIN ANALYZE`, interpret the plan, and identify the operation that is
costing the time. It is written so an agent diagnoses a slow query from evidence rather
than guessing.

SQL is declarative: you state *what* you want, and the planner (optimizer) decides *how*
to get it — which indexes to use, which join algorithm, in what order. Performance work
is almost never about rewriting the SQL by feel; it is about reading the plan the planner
chose and understanding why.

## Why It Matters

The same query can run a thousand times faster or slower depending on the plan, and the
plan changes with data volume and statistics. A query that used an index seek at ten
thousand rows can flip to a sequential scan at ten million, or vice versa, when the
planner's row estimates drift. Without reading the plan, every optimization is a guess,
and guesses often make things worse. `EXPLAIN` turns performance from folklore into
measurement.

## Core Principles

- **Measure the plan before changing anything.** `EXPLAIN (ANALYZE, BUFFERS)` shows the
  real plan, real row counts, and real time. Optimize what it reveals, not what you assume.
- **The gap between estimated and actual rows is the first clue.** A large mismatch means
  the planner has stale or missing statistics and is choosing a bad plan on bad numbers.
- **Sequential scan is not automatically bad.** For a small table or a query touching most
  rows, a full scan is the *correct* choice; an index seek would be slower.
- **Join order and join algorithm dominate cost.** Nested loop, hash join, and merge join
  each win in different regimes; the wrong one on a big join is the usual culprit.
- **Read the plan bottom-up, inner-to-outer.** Time and rows flow from the leaf nodes up;
  find the deepest node where actual rows or time explodes.

## Best Practices

- Use `EXPLAIN ANALYZE` (which executes the query) for real timings; plain `EXPLAIN` only
  shows estimates. Never run `ANALYZE` form on a destructive statement outside a rollback.
- Include `BUFFERS` to see whether the work is I/O-bound (blocks read from disk) or served
  from cache — it changes what "slow" means.
- Compare `rows` (estimate) to `actual rows`; when they diverge by an order of magnitude,
  run `ANALYZE <table>` to refresh statistics before touching the query.
- Look for the expensive operators: sequential scan on a large table, a nested loop over
  many outer rows, an external (on-disk) sort or hash, and rows filtered late.
- Check "Rows Removed by Filter" — a large value means the index (or predicate) let too
  many rows through and they were discarded after fetching. That is wasted I/O.
- Keep statistics fresh: ensure autovacuum/auto-analyze is running; increase the
  statistics target on skewed columns the planner keeps misestimating.
- Reproduce plans on production-like data; a plan from a tiny dev table is meaningless.

## Examples

**Good Example** — reading the plan and acting on the evidence

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE customer_id = 42 AND status = 'paid';

-- Index Scan using idx_orders_customer_status on orders
--   (cost=0.43..8.45 rows=1 width=64)
--   (actual time=0.02..0.03 rows=1 loops=1)
--   Buffers: shared hit=4
-- Estimate (rows=1) matches actual (rows=1): stats are healthy, index is used,
-- work is served from cache (shared hit). Nothing to fix — this is a good plan.
```

**Bad Example** — a plan being ignored

```sql
-- Slapping DISTINCT and reordering columns "to make it faster" without EXPLAIN:
SELECT DISTINCT * FROM orders WHERE customer_id = 42;
-- Seq Scan on orders (rows=10 est) ... (actual rows=2000000)
-- Estimate is off by 200,000x → stale statistics. The real fix is ANALYZE orders
-- and an index on customer_id, not DISTINCT (which only adds a costly sort/hash).
```

## Common Mistakes

- Optimizing by rewriting SQL without ever running `EXPLAIN` first.
- Reading estimates from plain `EXPLAIN` and believing they are real timings.
- Treating every sequential scan as a bug and forcing an index that is actually slower.
- Ignoring a huge estimate-vs-actual gap, the clearest sign of stale statistics.
- Testing plans on a tiny dataset, where the planner's choices do not reflect production.
- Overlooking "Rows Removed by Filter" and the join algorithm, the two usual hotspots.
- Using planner hints/`SET enable_seqscan=off` as a permanent fix instead of fixing stats
  or indexes.

## Production Tips

- Enable `auto_explain` (or slow-query logging with plans) so the plan of a slow
  production query is captured when it happens, not reconstructed later.
- Log and review the slowest queries by total time (`pg_stat_statements`); the worst
  offender is usually a frequent mid-cost query, not the single slowest run.
- After a large data load or bulk delete, run `ANALYZE` explicitly so the next queries
  plan against accurate statistics instead of pre-load estimates.

## AI Review Checklist

- Was `EXPLAIN (ANALYZE, BUFFERS)` run before proposing a performance change?
- Do estimated and actual row counts roughly agree (statistics are fresh)?
- Is the chosen scan and join algorithm appropriate for the data size?
- Is there a large "Rows Removed by Filter" indicating a missing or weak index?
- Is the diagnosis based on production-like data, not a toy table?
- Is the fix a stats/index/schema change rather than a brittle planner hint?
- Was `ANALYZE` run after any bulk data change that preceded the query?

## Related

- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/15-indexes.md`
- `knowledge/sql/23-performance.md`
- `knowledge/sql/05-joins.md`
- `knowledge/sql/100-common-antipatterns.md`
