---
id: mysql/18-debugging
topic: mysql
slug: debugging
title: "MySQL Debugging"
type: doc
order: 18
status: ready
tags: [mysql, debugging]
related: [mysql/05-query-optimization, mysql/07-locking, mysql/15-monitoring, mysql/14-performance, mysql/06-transactions]
when_to_use: "Read before diagnosing a slow query, a deadlock, a lock wait timeout, or unexpected query results in MySQL."
---
# MySQL Debugging

## Purpose

This document defines how to find *why* MySQL is behaving wrong: a query that is slow,
a statement that returns the wrong rows, a deadlock, a lock wait timeout, or a connection
that hangs. It teaches the tools that turn "the database is slow" into a specific,
reproducible cause you can fix.

Debugging here means observation, not guessing. Every claim about MySQL behavior must be
backed by output from `EXPLAIN`, the slow log, `performance_schema`, or
`SHOW ENGINE INNODB STATUS` — never by intuition about what the optimizer "probably" does.

## Why It Matters

Database bugs hide behind healthy-looking application code. The query runs, returns rows,
and passes tests — then falls over at production scale because it does a full table scan
of 40 million rows, or serializes every write behind one hot lock. The symptom (a timeout,
a 500) appears far from the cause (a missing index, a wide transaction). Without the right
diagnostic tools you change random things and hope; with them you read the exact plan the
optimizer chose and the exact lock a transaction is blocked on.

## Core Principles

- **Reproduce before you fix.** Capture the exact statement, parameters, and dataset size.
  A query that is fast on 1,000 rows and fatal on 10 million is a different bug.
- **Read the plan, not the query.** `EXPLAIN` shows what MySQL will actually do; the SQL
  only shows what you asked. When they disagree, the plan is the truth.
- **Measure, then change one thing.** Add an index, re-run `EXPLAIN ANALYZE`, compare.
  Changing several things at once tells you nothing about which one worked.
- **Distinguish slow from blocked.** A slow query burns CPU or I/O; a blocked query waits
  on a lock held by someone else. They look identical to the user and need opposite fixes.
- **Prefer built-in instrumentation over guesswork.** `performance_schema` and the slow
  log record what happened; they do not lie or forget.

## Best Practices

- Use `EXPLAIN ANALYZE` (MySQL 8.0+) to get *actual* row counts and timing per plan node,
  not just the optimizer's estimates. Large gaps between estimated and actual rows point at
  stale statistics — run `ANALYZE TABLE`.
- Enable the slow query log with `long_query_time` set low (e.g. `0.5`) and
  `log_queries_not_using_indexes = ON` in staging; aggregate it with `pt-query-digest`.
- For deadlocks, read `SHOW ENGINE INNODB STATUS` — the `LATEST DETECTED DEADLOCK` section
  names both transactions, their SQL, and the locks each held and wanted.
- For lock waits, query `performance_schema.data_lock_waits` joined to `data_locks` to see
  exactly which session blocks which, and on which index.
- Set `innodb_lock_wait_timeout` and `max_execution_time` so a stuck query fails fast and
  loudly instead of hanging the connection pool.
- When results are wrong, suspect implicit type coercion, `NULL` semantics, or a `JOIN`
  that silently multiplied rows before an aggregate — not the engine.

## Examples

**Good Example** — measure the real plan, then confirm the fix

```sql
-- Reproduce with actual timings and row counts, not estimates.
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped';
-- Output shows: table scan, actual rows=8.2M, actual time=4200ms.
-- The optimizer had no usable index, so it read the whole table.

CREATE INDEX idx_orders_customer_status ON orders (customer_id, status);

EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped';
-- Re-run confirms: index range scan, actual rows=113, actual time=1.4ms.
-- The change is verified by measurement, not assumed.
```

**Bad Example** — guessing, and hiding the real failure

```sql
-- "It's slow, probably needs an index somewhere." Adds an index on a hunch,
-- never checks the plan, and the query still scans because the column is
-- wrapped in a function the index cannot be used for:
SELECT * FROM orders WHERE DATE(created_at) = '2026-07-07';
-- DATE(created_at) forces a full scan: the index on created_at cannot be used
-- because the column is not compared directly. Correct form is a range:
--   WHERE created_at >= '2026-07-07' AND created_at < '2026-07-08'
-- Without EXPLAIN, this bug is invisible until production load exposes it.
```

## Common Mistakes

- Trusting `EXPLAIN` estimates as truth; they are cost guesses. Use `EXPLAIN ANALYZE` for
  reality, and `ANALYZE TABLE` when estimates are far off actuals.
- Wrapping an indexed column in a function (`DATE()`, `LOWER()`, `CAST()`) or leading it
  with `%` in `LIKE`, which disables the index.
- Confusing a deadlock (auto-rolled-back, retryable) with a lock wait timeout (one waiter
  gave up) and applying the wrong fix.
- Debugging on a tiny dev dataset where every plan looks fine, then shipping to production
  scale where the plan flips to a scan.
- Reading only the query and ignoring the transaction around it — a lock held across a slow
  application call blocks everyone else.

## Production Tips

- Keep the slow query log on in production with a conservative `long_query_time`, and ship
  it to a digest tool so regressions surface as trend changes, not incidents.
- Capture `SHOW ENGINE INNODB STATUS` and `performance_schema` snapshots automatically when
  lock waits or deadlocks spike — the state is gone once the transaction ends.
- Add the SQL statement digest (from `performance_schema.events_statements_summary_by_digest`)
  to dashboards so you can rank queries by total time, not just single-run latency.

## AI Review Checklist

- Was the slow or wrong query reproduced with realistic data volume before any fix?
- Does the diagnosis cite `EXPLAIN ANALYZE`, the slow log, or `performance_schema` output?
- Is a slow query distinguished from a blocked one, with the matching remedy?
- For deadlocks, was `SHOW ENGINE INNODB STATUS` consulted for the actual lock cycle?
- Are indexed columns compared directly, not wrapped in functions or leading wildcards?
- Was the fix confirmed by re-running the plan, not assumed to work?

## Related

- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/07-locking.md`
- `knowledge/mysql/15-monitoring.md`
- `knowledge/mysql/14-performance.md`
- `knowledge/mysql/06-transactions.md`
