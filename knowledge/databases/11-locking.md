---
id: databases/11-locking
topic: databases
slug: locking
title: "Database Locking"
type: doc
order: 11
status: ready
tags: [databases, locking]
related: [databases/10-concurrency, databases/09-transactions, databases/12-acid, databases/07-indexing, databases/17-migrations]
when_to_use: "Read before using explicit row locks, diagnosing a deadlock, or running DDL on a live table."
---
# Database Locking

## Purpose

This document defines how database locks work and how to use them safely: row vs
table locks, shared vs exclusive modes, `SELECT ... FOR UPDATE`, deadlocks, and the
locks that DDL takes. It is written so an agent can lock exactly what it needs, for as
short as possible, without wedging the database or deadlocking under load.

Locking is the enforcement mechanism behind [concurrency](10-concurrency.md) and
[transactions](09-transactions.md). Even code that never writes an explicit lock is
subject to the locks the engine takes automatically.

## Why It Matters

Locks are how the database serializes conflicting access to the same data. Used well,
a row lock lets you safely do read-modify-write on a hot row. Used badly, locks are
the most common cause of production stalls: one long transaction holding a lock blocks
every writer behind it, requests pile up, connection pools exhaust, and the whole
service appears down while the database itself is idle, just waiting.

Deadlocks add a second failure mode. When two transactions grab the same locks in
opposite order, neither can proceed and the engine kills one. This is invisible in
testing and appears only under concurrent load, so lock discipline has to be designed
in, not debugged in.

## Core Principles

- **Lock the narrowest scope for the shortest time.** Prefer a single-row lock over a
  range, a range over a table. Acquire late, release at commit — keep the transaction
  tight.
- **Acquire locks in a consistent order everywhere.** Deadlocks come from inconsistent
  ordering. If all code locks parent-before-child, id-ascending, they can't deadlock
  on each other.
- **Shared (read) locks coexist; exclusive (write) locks don't.** An exclusive lock
  blocks all other access to that row. Take the weakest mode that is correct.
- **Locks are held until the transaction ends.** There is no early release. A lock's
  cost is the whole remaining transaction duration — so keep it short.
- **DDL takes heavy locks.** `ALTER TABLE` can take an `ACCESS EXCLUSIVE` lock that
  blocks reads and writes; naive migrations cause outages. See
  [migrations](17-migrations.md).

## Best Practices

- Use `SELECT ... FOR UPDATE` to lock the exact rows you will modify, then update them,
  then commit — the standard safe read-modify-write.
- Add `FOR UPDATE SKIP LOCKED` for queue/worker patterns so each worker grabs a
  different unlocked row instead of all contending for the head of the queue.
- Set a `lock_timeout` so a blocked statement fails fast rather than waiting
  indefinitely and holding its own locks while it waits.
- Lock rows in a deterministic order (e.g. `ORDER BY id`) when locking several, so
  concurrent transactions can't deadlock by locking the same set in different orders.
- For low-contention updates, prefer optimistic concurrency (a `version` guard) over
  locking — no lock is held, no one is blocked; see [concurrency](10-concurrency.md).
- Run schema changes with lock-aware techniques: `CREATE INDEX CONCURRENTLY`, add
  `NOT NULL` via `NOT VALID` then `VALIDATE`, and set a short `lock_timeout` with retry
  so DDL doesn't queue behind (or block) traffic.
- Never hold a lock across a network call, user think-time, or a slow loop.

## Examples

**Good Example** — lock the row, ordered, timed, released at commit

```sql
BEGIN;
SET LOCAL lock_timeout = '3s';          -- fail fast instead of blocking forever

-- Lock exactly the row we will change; concurrent transfers wait only on this row.
SELECT balance FROM accounts
WHERE id = 42
FOR UPDATE;                             -- exclusive row lock, held until COMMIT

UPDATE accounts SET balance = balance - 100 WHERE id = 42;
COMMIT;                                 -- lock released here, promptly
```

**Bad Example** — inconsistent lock order, slow work under lock

```sql
-- Transaction A                         -- Transaction B (runs concurrently)
BEGIN;                                   BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;   SELECT * FROM accounts WHERE id = 2 FOR UPDATE;
-- ... calls an external fraud API here (slow) ...  -- ... also calls a slow service ...
SELECT * FROM accounts WHERE id = 2 FOR UPDATE;   SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- A waits for B's lock on 2; B waits for A's lock on 1  -> DEADLOCK; the engine kills one.
-- Even without deadlock, the slow API call holds row locks the whole time.
```

## Common Mistakes

- Locking rows in different orders across code paths, guaranteeing eventual deadlock.
- Holding locks across external calls, user interaction, or long computations.
- Locking more than needed — a table lock or wide range where one row would do.
- No `lock_timeout`, so a blocked query waits forever and cascades into a pileup.
- Running `ALTER TABLE` on a large live table without a lock strategy, blocking all
  traffic during the rewrite.
- Using pessimistic `FOR UPDATE` on low-contention rows where optimistic concurrency
  would block no one.
- Ignoring engine deadlock errors instead of catching and retrying the transaction.

## Production Tips

- Monitor lock waits and blocking chains (`pg_locks`, `pg_stat_activity`,
  `sys.dm_tran_locks`) and alert on long blockers.
- Log and count deadlocks; a rising rate points to a lock-ordering bug on a hot path.
- For online DDL, prefer tooling that does it lock-safely (e.g. `pg_repack`,
  `gh-ost`) on large tables; see [migrations](17-migrations.md).

## AI Review Checklist

- Is the lock scope the narrowest that is correct (row over range over table)?
- Are multiple locks always acquired in a consistent, deterministic order?
- Is a `lock_timeout` set so blocked statements fail fast?
- Is any lock held across a network call, user wait, or slow loop?
- Is `SELECT ... FOR UPDATE` used for read-modify-write, or optimistic concurrency for
  low contention?
- Do queue consumers use `SKIP LOCKED` instead of contending on the same rows?
- Do schema changes use a lock-safe strategy on large live tables?

## Related

- `knowledge/databases/10-concurrency.md`
- `knowledge/databases/09-transactions.md`
- `knowledge/databases/12-acid.md`
- `knowledge/databases/07-indexing.md`
- `knowledge/databases/17-migrations.md`
