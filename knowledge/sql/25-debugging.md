---
id: sql/25-debugging
topic: sql
slug: debugging
title: "SQL Debugging"
type: doc
order: 25
status: ready
tags: [sql, debugging]
related: [sql/16-query-planning, sql/17-query-optimization, sql/23-performance, sql/14-transactions, sql/24-testing]
when_to_use: "Read when a query returns wrong rows, runs slowly, deadlocks, or a migration fails."
---
# SQL Debugging

## Purpose

This document defines how to diagnose SQL problems: wrong results, slow queries,
locking and deadlocks, and failed migrations. It is written so an agent finds the
actual cause instead of guessing and adding indexes at random.

SQL debugging is different from application debugging. There is no breakpoint and no
stack trace — the database is a black box that took a declarative query and chose an
execution strategy. The whole job is making that strategy and the data visible.

## Why It Matters

The two failure modes look nothing alike but are debugged the same way. A *wrong
result* is a logic bug — usually a `JOIN` type, a `NULL`, or a `GROUP BY` that is not
what you meant. A *slow query* is a planner problem — usually a missing index, stale
statistics, or a non-sargable predicate. Both are solved by reproducing on real data
and reading the plan, not by staring at the SQL text and reasoning about what it
"should" do.

Guessing is worse than useless here. Adding an index to fix a slow query that is
actually slow because of stale statistics leaves you with a slow query *and* a
write-amplifying index. Measure first.

## Core Principles

- **Reproduce on realistic data first.** A bug that only appears at 10M rows will not
  reproduce at 10. Restore a production-shaped dataset (anonymized) before debugging
  anything performance- or plan-related.
- **Read the plan, don't guess it.** `EXPLAIN` shows the intended plan; `EXPLAIN
  ANALYZE` runs it and shows actual rows and time. The gap between estimated and
  actual rows is the single most useful debugging signal — a large gap means stale or
  missing statistics. See [query-planning](16-query-planning.md).
- **Isolate wrong-result bugs by shrinking the query.** Strip clauses until the bug
  disappears; the last clause you removed is the cause. Check `JOIN` type, `WHERE`,
  and `GROUP BY` in that order.
- **Suspect `NULL` in every wrong-result bug.** `NULL = NULL` is unknown, `NOT IN
  (… NULL …)` returns nothing, and `NULL` silently drops from aggregates and `INNER
  JOIN`s. This is the most common SQL logic bug.
- **Change one thing, then re-measure.** Never add an index, rewrite a predicate, and
  bump `work_mem` in one shot — you will not know which one mattered.

## Best Practices

- Run `EXPLAIN (ANALYZE, BUFFERS)` (Postgres) or `EXPLAIN ANALYZE` (MySQL 8+) and read
  from the **most-indented node outward** — that is where execution starts and where
  the time usually is.
- When estimated rows differ from actual rows by an order of magnitude, run `ANALYZE`
  (update statistics) before touching indexes; stale stats mislead the planner.
- For **slow writes or hangs**, query the lock views (`pg_locks` +
  `pg_stat_activity`, or `SHOW ENGINE INNODB STATUS`) to find the blocking session
  rather than assuming the query itself is slow.
- Reproduce **deadlocks** by reading the deadlock log — it names both transactions and
  the lock order. The fix is almost always making all transactions acquire locks in a
  consistent order. See [transactions](14-transactions.md).
- Debug **wrong results with a known-answer subset**: run the query against a handful
  of rows whose correct output you computed by hand.
- Log the **exact parameterized query with its bound values** in the application; a
  bug often lives in the parameters, not the SQL.

## Examples

**Good Example** — measure, read the plan, fix the real cause

```sql
-- 1. Reproduce and MEASURE with actual vs estimated rows.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE customer_id = 42 AND status = 'open';
-- Plan shows: Seq Scan, estimated rows=1, actual rows=50000.
-- The 1-vs-50000 gap => statistics are stale OR no usable index.

-- 2. Refresh statistics first (cheap, non-destructive) and re-check.
ANALYZE orders;

-- 3. Still a Seq Scan? THEN add the index the predicate needs, and re-measure.
CREATE INDEX CONCURRENTLY idx_orders_customer_status
  ON orders (customer_id, status);   -- CONCURRENTLY: no long write lock in prod
```

**Bad Example** — guessing without measuring

```sql
-- Query is "slow", so add an index on a hunch. No EXPLAIN, no ANALYZE.
CREATE INDEX idx1 ON orders (created_at);   -- unrelated to the actual predicate
CREATE INDEX idx2 ON orders (total);        -- also unrelated

-- The real cause was stale statistics; the query is still slow, and now every
-- INSERT/UPDATE maintains two useless indexes. The bug is hidden, not fixed.
SELECT * FROM orders WHERE customer_id = 42 AND status = 'open';
```

## Common Mistakes

- Adding indexes to "fix slow" without running `EXPLAIN ANALYZE` — treating a symptom
  and often creating write overhead for no gain.
- Debugging on an empty or tiny dataset, so the plan never matches production.
- Ignoring the estimated-vs-actual row gap, the clearest signal of stale statistics.
- Forgetting `NULL` in wrong-result bugs (`NOT IN`, `<>`, aggregate drops).
- Blaming a slow `SELECT` when the real problem is a lock held by another transaction.
- Changing several variables at once, so no conclusion can be drawn.

## Production Tips

- Enable **slow-query logging** (`log_min_duration_statement` in Postgres, the slow
  query log in MySQL) so problem queries surface before users report them.
- Use `pg_stat_statements` (or the MySQL performance schema) to rank queries by total
  time — the worst query is often frequent-and-medium, not the one obviously slow one.
- Keep `auto_explain` (Postgres) available to capture plans of slow production queries
  you cannot reproduce locally.
- Set a **statement timeout** so a runaway debugging query cannot hold locks and stall
  the system.

## AI Review Checklist

- Was the problem reproduced on realistic, production-shaped data?
- Was `EXPLAIN ANALYZE` used to read the actual plan before any change?
- Was the estimated-vs-actual row gap checked, and `ANALYZE` run for stale stats?
- For wrong results, was `JOIN` type, `WHERE`, `GROUP BY`, and `NULL` handling checked?
- For locking issues, was the actual blocking session identified from lock views?
- Was exactly one change made and re-measured, rather than several at once?

## Related

- `knowledge/sql/16-query-planning.md`
- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/23-performance.md`
- `knowledge/sql/14-transactions.md`
- `knowledge/sql/24-testing.md`
