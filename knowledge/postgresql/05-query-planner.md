---
id: postgresql/05-query-planner
topic: postgresql
slug: query-planner
title: "Query Planner"
type: doc
order: 5
status: ready
tags: [postgresql, query-planner, ANALYZE, EXPLAIN, BUFFERS, pg_stat_statements, auto_explain]
related: [postgresql/04-indexes, postgresql/21-analyze, postgresql/16-performance, postgresql/24-debugging, postgresql/27-tuning]
when_to_use: "Read before diagnosing a slow query or interpreting an EXPLAIN plan."
---
# Query Planner

## Purpose

This document defines how to read and influence PostgreSQL's cost-based query
planner so you can diagnose slow queries from evidence, not guesswork. It covers
`EXPLAIN` vs `EXPLAIN ANALYZE`, how to read a plan, why the planner picks the scans
and joins it does, the role of statistics, and the small number of levers that
legitimately change its decisions. The planner is the bridge between the SQL you
write and the work the database does — understanding it is how you make queries fast.

## Why It Matters

The same query can run in a millisecond or a minute depending on the plan the
optimizer chooses, and it chooses based on statistics that can be stale, missing, or
misleading. When a query is slow, the instinct is to add an index or rewrite the SQL
blindly — but without reading the plan you are guessing, and you will often "fix" the
wrong thing while the real cause (a bad estimate, a missing `ANALYZE`, a
non-sargable predicate) persists. `EXPLAIN (ANALYZE, BUFFERS)` turns a performance
mystery into a readable trace. Learning to read it is the highest-return skill in
database performance work.

## Core Principles

- **The plan is the source of truth.** Use `EXPLAIN (ANALYZE, BUFFERS)` to see what
  the database actually did, then act on that — never on a hunch about what is slow.
- **The planner is cost-based and stats-driven.** It estimates row counts from
  statistics (kept fresh by `ANALYZE`) and picks the cheapest estimated plan. Bad
  stats produce bad plans.
- **A sequential scan is not always wrong.** For a small table or a low-selectivity
  filter, a seq scan beats an index scan. The planner knows this; trust the costs.
- **Estimate vs actual is the key signal.** A large gap between estimated and actual
  rows in `EXPLAIN ANALYZE` points straight at the stats or predicate problem.
- **Write sargable predicates.** Keep the indexed column bare on one side of the
  operator; wrapping it in a function or cast defeats the index.

## Best Practices

- Diagnose with `EXPLAIN (ANALYZE, BUFFERS)` on a representative dataset; plain
  `EXPLAIN` shows estimates only, `ANALYZE` runs the query and shows reality.
- Read the plan **inside-out and bottom-up**: the deepest node runs first; costs and
  row counts accumulate upward. Find the node where actual time or rows explodes.
- Compare **estimated rows vs actual rows** at each node; a 100x mismatch means stale
  statistics — run `ANALYZE` (see [analyze](21-analyze.md)) and re-check.
- For correlated columns whose combination the planner misjudges, create **extended
  statistics** (`CREATE STATISTICS`).
- Look at `BUFFERS`: high `read` (vs `hit`) means the data was not cached; high shared
  reads on a supposedly indexed query hint at a missing or unused index.
- Keep predicates sargable — index `lower(email)` and query `lower(email)`, don't
  wrap the column at query time.
- Reach for planner GUCs (`enable_seqscan = off`, `join_collapse_limit`) only to
  *diagnose* — as a permanent fix they mask the real cause. Prefer fixing stats or indexes.

## Examples

**Good Example** — measure, read the mismatch, fix the cause

```sql
-- Diagnose with real execution data, not estimates.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE customer_id = 42 AND status = 'paid';

-- Plan shows: Seq Scan, estimated rows=1  actual rows=50000  → stats are stale.
-- The 50,000x gap, not the seq scan itself, is the problem. Fix the stats first:
ANALYZE orders;
-- Re-run EXPLAIN ANALYZE: now the planner estimates correctly and chooses an
-- Index Scan on idx_orders_customer_status. The query drops from 900ms to 3ms.
```

**Bad Example** — guessing, and a non-sargable predicate

```sql
-- No EXPLAIN: forcing the planner's hand to "make it use the index".
SET enable_seqscan = off;   -- global sledgehammer; hides the real cause everywhere

-- Non-sargable: the cast wraps the indexed column, so idx on created_at is unusable.
SELECT * FROM orders
WHERE created_at::date = '2026-07-01';   -- seq scan regardless of the index

-- Correct, sargable form (range on the bare column) uses the index:
-- WHERE created_at >= '2026-07-01' AND created_at < '2026-07-02';
```

## Common Mistakes

- Changing indexes or SQL without ever running `EXPLAIN ANALYZE` first.
- Reading only estimated costs (plain `EXPLAIN`) and missing the estimate-vs-actual gap.
- Assuming a sequential scan is always the bug; on small or low-selectivity data it is optimal.
- Non-sargable predicates (`col::date =`, `lower(col)` without an expression index,
  leading-wildcard `LIKE '%x'`) that silently disable indexes.
- Leaving statistics stale after a bulk load, so the planner estimates wildly wrong.
- Permanently setting `enable_seqscan = off` or other GUCs instead of fixing stats/indexes.
- Ignoring `BUFFERS`, so you cannot tell a cold-cache read from a genuinely bad plan.

## Production Tips

- Enable `pg_stat_statements` to find the queries that consume the most total time,
  then `EXPLAIN` the worst offenders — optimize by aggregate cost, not by anecdote.
- Use `auto_explain` (with a `log_min_duration`) to capture plans of slow queries as
  they happen in production, including the parameters that triggered them.
- Watch autovacuum/autoanalyze: they keep stats fresh automatically, but a table with
  a sudden bulk change may need a manual `ANALYZE` before its stats catch up.

## AI Review Checklist

- Is the slow-query diagnosis backed by `EXPLAIN (ANALYZE, BUFFERS)` output?
- Was estimated-vs-actual row count checked, and stale stats ruled out with `ANALYZE`?
- Are all predicates sargable (no function/cast wrapping the indexed column)?
- Is a sequential scan genuinely the problem, or is it optimal for this data size?
- Were planner GUCs used only for diagnosis, not shipped as a permanent workaround?
- Are the highest-total-cost queries (`pg_stat_statements`) the ones being optimized?

## Related

- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/21-analyze.md`
- `knowledge/postgresql/16-performance.md`
- `knowledge/postgresql/24-debugging.md`
- `knowledge/postgresql/27-tuning.md`
