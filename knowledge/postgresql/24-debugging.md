---
id: postgresql/24-debugging
topic: postgresql
slug: debugging
title: "Debugging"
type: doc
order: 24
status: ready
tags: [postgresql, debugging]
related: [postgresql/05-query-planner, postgresql/17-monitoring, postgresql/07-locking, postgresql/16-performance, postgresql/20-vacuum]
when_to_use: "Read before diagnosing a slow query, a lock stall, a connection storm, or any unexpected PostgreSQL behavior in a running system."
---
# Debugging

## Purpose

This document defines how to diagnose PostgreSQL problems from evidence rather than
guesswork: slow queries, lock waits, connection exhaustion, bloat, and wrong results.
It is written so an agent can find the actual cause and confirm the fix, instead of
changing settings at random and hoping.

Debugging Postgres is mostly *reading the right catalog view or plan*, not editing code.
The database exposes almost everything about its own state — the skill is knowing which
view answers which question.

## Why It Matters

A production database is a shared, stateful, single point of failure. A guess that
"fixes" a symptom often moves the problem elsewhere: adding an index to speed one query
slows every write; killing a blocked backend can abort a transaction mid-way. Because
the blast radius spans every client at once, diagnosis must be grounded in what the
server reports right now, and every change must be verified against the same evidence
that revealed the problem.

## Core Principles

- **Reproduce, then measure.** Capture the exact query, parameters, and timing before
  changing anything. You cannot confirm a fix you never quantified.
- **Ask the catalog, not your memory.** `pg_stat_activity`, `pg_locks`,
  `pg_stat_statements`, and `EXPLAIN (ANALYZE, BUFFERS)` are the ground truth. Opinions
  about "what should be fast" are not evidence.
- **Distinguish planning from execution.** A bad plan, a bad statistic, and a bad schema
  are three different bugs with three different fixes.
- **Change one variable at a time.** Batch changes make it impossible to know which one
  helped or hurt.
- **Prefer read-only inspection first.** Look before you touch. Most Postgres debugging
  needs no write and no restart.

## Best Practices

- Always debug slow queries with `EXPLAIN (ANALYZE, BUFFERS)`, not plain `EXPLAIN`.
  `BUFFERS` shows real I/O; `ANALYZE` shows real row counts versus the planner's estimate.
- Compare **estimated vs actual rows** in the plan. A large gap means stale statistics —
  run `ANALYZE` on the table before touching indexes.
- Enable `pg_stat_statements` and sort by `total_exec_time` to find the queries that
  actually cost the most, which are rarely the ones that "feel" slow.
- Use `log_min_duration_statement` (e.g. `500ms`) to capture slow statements in the log
  with their parameters, instead of trying to reproduce them by hand.
- For a stall, query `pg_stat_activity` filtered by `wait_event_type` and join `pg_locks`
  to find the blocking PID before you consider `pg_terminate_backend`.
- Reproduce plan problems safely by wrapping the query in `BEGIN; ... ROLLBACK;` so
  `EXPLAIN ANALYZE` on `UPDATE`/`DELETE` does not mutate data.
- Set `\timing on` in `psql` and run a query several times — the first run pays cache
  and planning costs that mislead you about steady-state performance.

## Examples

**Good Example** — find the real blocker from live server state

```sql
-- Who is waiting, and on which PID are they blocked? Read-only, no side effects.
SELECT pid,
       wait_event_type,
       wait_event,
       pg_blocking_pids(pid) AS blocked_by, -- the exact backend(s) holding the lock
       left(query, 80)       AS query
FROM   pg_stat_activity
WHERE  state <> 'idle'
ORDER  BY blocked_by DESC NULLS LAST;

-- Diagnose the plan with real numbers, inside a transaction so nothing is written.
BEGIN;
EXPLAIN (ANALYZE, BUFFERS)          -- ANALYZE = actual rows/time; BUFFERS = real I/O
  UPDATE orders SET status = 'shipped' WHERE id = 42;
ROLLBACK;                            -- discard the test mutation
```

**Bad Example** — guessing, mutating, and measuring nothing

```sql
-- No parameters, no BUFFERS, no ANALYZE: shows estimates only, hides I/O and the
-- estimate-vs-actual gap that reveals stale stats.
EXPLAIN SELECT * FROM orders WHERE status = 'shipped';

-- "It felt slow, so add an index." No evidence it helps; slows every write to orders.
CREATE INDEX ON orders (status);

-- A backend is blocked, so kill it blindly without finding what it was blocked ON —
-- aborts a live transaction and the real blocker keeps holding the lock.
SELECT pg_terminate_backend(12345);
```

## Common Mistakes

- Running plain `EXPLAIN` and trusting estimated rows as if they were measured.
- Ignoring the estimated-vs-actual row gap, then blaming the index instead of statistics.
- Debugging on the primary when a read replica or a restored snapshot would isolate the
  problem without risk.
- Terminating a blocked backend instead of the backend that is *holding* the lock.
- Tuning `work_mem` or `shared_buffers` before confirming the query is even the bottleneck.
- Testing a query once and reporting the cold-cache time as its true cost.

## Production Tips

- Keep `pg_stat_statements` loaded in `shared_preload_libraries` in every environment so
  the data exists before you need it — you cannot analyze a spike after it ends.
- Log `log_lock_waits = on` and `deadlock_timeout` so lock contention leaves a trail.
- Snapshot `pg_stat_activity` and `pg_locks` into a table during an incident; live views
  change the instant the problem clears.
- Reset `pg_stat_statements` after a deploy to attribute regressions to the new release.

## AI Review Checklist

- Was the slow query measured with `EXPLAIN (ANALYZE, BUFFERS)`, not guessed?
- Was estimated-vs-actual row count checked before adding or changing an index?
- Was `ANALYZE` run to rule out stale statistics before schema changes?
- For a stall, was the *blocking* PID identified via `pg_blocking_pids` before any kill?
- Were test mutations wrapped in a transaction and rolled back?
- Is the fix verified against the same metric that exposed the problem?

## Related

- `knowledge/postgresql/05-query-planner.md`
- `knowledge/postgresql/17-monitoring.md`
- `knowledge/postgresql/07-locking.md`
- `knowledge/postgresql/16-performance.md`
- `knowledge/postgresql/20-vacuum.md`
