---
id: postgresql/07-locking
topic: postgresql
slug: locking
title: "Locking"
type: doc
order: 7
status: ready
tags: [postgresql, locking]
related: [postgresql/06-transactions, postgresql/22-migrations, postgresql/05-query-planner, postgresql/17-monitoring]
when_to_use: "Read before writing SELECT ... FOR UPDATE, running a DDL migration on a live table, or diagnosing a deadlock or lock wait."
---
# Locking

## Purpose

This document defines how PostgreSQL locking works — row locks, table locks, advisory
locks — and how to acquire them without deadlocking or stalling production. It is written
so an agent can serialize concurrent writes correctly and run schema changes without
taking an outage.

Locking is the complement to [transactions](06-transactions.md): isolation levels decide
what a snapshot sees, locks decide who waits for whom. In PostgreSQL, ordinary reads never
take row locks (MVCC handles them), so nearly all lock contention comes from explicit
`FOR UPDATE`, from concurrent writes to the same row, or from DDL.

## Why It Matters

A lock held a moment too long turns a fast endpoint into a queue: every request waiting on
the same row serializes, latency spikes, and connections exhaust. Worse, a naive schema
migration takes an `ACCESS EXCLUSIVE` lock that blocks *all* reads and writes to the table
— a one-line `ALTER TABLE` can freeze an entire service for the duration of a table
rewrite. Deadlocks add a second failure mode: two transactions each hold what the other
needs, and PostgreSQL kills one after `deadlock_timeout`. These failures are load-dependent,
so they appear only in production, at peak, when they hurt most.

## Core Principles

- **Prefer atomic SQL over lock-then-modify.** `UPDATE ... SET n = n + 1` needs no explicit
  lock; the row lock is held only for the statement. Reach for `FOR UPDATE` only when the
  app must read a row, compute in application code, then write it back.
- **Acquire locks in a consistent global order.** Deadlocks require a cycle; a fixed order
  (e.g. always lock the lower account id first) makes a cycle impossible.
- **Hold locks for the shortest possible span.** Lock as late as you can, commit as soon as
  you can. A lock's cost is every transaction queued behind it.
- **Treat DDL as a locking problem.** Every `ALTER TABLE`/`CREATE INDEX` takes a lock; know
  which one and whether it rewrites the table before you run it on a live system.
- **Use `NOWAIT` or `lock_timeout` on contended locks** so a request fails fast instead of
  piling up behind a stuck holder.

## Best Practices

- For a work-queue, claim rows with `FOR UPDATE SKIP LOCKED` so workers grab different rows
  instead of all blocking on the first one.
- Serialize independent, non-row-backed critical sections with **advisory locks**
  (`pg_advisory_xact_lock(key)`) rather than inventing a lock table.
- Set `lock_timeout` (e.g. `SET lock_timeout = '3s'`) before risky statements so a blocked
  statement aborts instead of hanging a connection indefinitely.
- Create and drop indexes on live tables with `CREATE INDEX CONCURRENTLY` /
  `DROP INDEX CONCURRENTLY` — they take a weaker lock and do not block writes (but cannot run
  inside a transaction block).
- For `ALTER TABLE`, use forms that only need a metadata change: adding a nullable column or
  a column with a non-volatile default is instant on modern PostgreSQL; adding a `CHECK` or
  `NOT NULL` can be done in two steps (`NOT VALID` then `VALIDATE`) to avoid a long lock.
- Set `deadlock_timeout` appropriately (default 1s) and read the server log — PostgreSQL
  prints the exact queries and lock cycle when it breaks a deadlock.

## Examples

**Good Example** — skip-locked queue and ordered locking

```sql
-- Job queue: each worker locks a DIFFERENT available row instead of contending.
BEGIN;
SELECT id, payload FROM jobs
 WHERE status = 'pending'
 ORDER BY created_at
 FOR UPDATE SKIP LOCKED       -- do not wait on rows another worker already holds
 LIMIT 1;
-- process, then:
UPDATE jobs SET status = 'done' WHERE id = :id;
COMMIT;

-- Transfer: lock the two rows in a fixed id order so no pair can deadlock.
BEGIN;
SELECT * FROM accounts WHERE id IN (:a, :b)
 ORDER BY id FOR UPDATE;      -- consistent order = no lock cycle
UPDATE accounts SET balance = balance - 100 WHERE id = :from;
UPDATE accounts SET balance = balance + 100 WHERE id = :to;
COMMIT;
```

**Bad Example** — table-rewriting migration on a live table, unordered locks

```sql
-- Rewrites the whole table under ACCESS EXCLUSIVE: blocks ALL reads and writes
-- for as long as the rewrite takes. On a large table this is a production outage.
ALTER TABLE orders ADD COLUMN total numeric NOT NULL DEFAULT random();  -- volatile default -> full rewrite

-- Two sessions lock the same rows in opposite orders -> deadlock, one is killed.
-- session 1:  UPDATE accounts ... WHERE id = 1; then id = 2;
-- session 2:  UPDATE accounts ... WHERE id = 2; then id = 1;
```

## Common Mistakes

- Using `SELECT ... FOR UPDATE` and holding the lock across app-side I/O, serializing every request.
- Running `ALTER TABLE ADD COLUMN ... DEFAULT <volatile>` or type changes that rewrite the table
  during peak traffic instead of off-hours or in staged steps.
- `CREATE INDEX` without `CONCURRENTLY` on a busy table, blocking all writes until it finishes.
- Inconsistent lock ordering across code paths, producing intermittent deadlocks.
- No `lock_timeout`, so one stuck transaction backs up an unbounded queue of waiters.
- Reinventing distributed mutual exclusion with a lock row instead of an advisory lock.

## Production Tips

- Query `pg_locks` joined to `pg_stat_activity` to see who holds what and who waits; the
  `pg_blocking_pids()` function names the blocker directly.
- Wrap migrations with a low `lock_timeout` and retry, so a migration that cannot get its
  lock quickly aborts rather than blocking traffic behind it.
- Alert on `deadlock` log lines and on lock waits exceeding a threshold — both signal a
  design issue, not a transient blip. See [monitoring](17-monitoring.md).

## AI Review Checklist

- Are explicit row locks (`FOR UPDATE`) held only across SQL, never across app-side I/O?
- Do all code paths acquire multiple locks in a consistent, documented order?
- Does the job/queue code use `FOR UPDATE SKIP LOCKED` instead of serializing on one row?
- Do index changes on live tables use `CONCURRENTLY`?
- Is each `ALTER TABLE` checked for whether it rewrites the table or takes `ACCESS EXCLUSIVE`?
- Is `lock_timeout` set before contended statements and migrations?
- Are advisory locks used for critical sections instead of a hand-rolled lock table?

## Related

- `knowledge/postgresql/06-transactions.md`
- `knowledge/postgresql/22-migrations.md`
- `knowledge/postgresql/05-query-planner.md`
- `knowledge/postgresql/17-monitoring.md`
