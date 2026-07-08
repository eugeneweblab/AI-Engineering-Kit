---
id: mysql/07-locking
topic: mysql
slug: locking
title: "Locking"
type: doc
order: 7
status: ready
tags: [mysql, locking]
related: [mysql/06-transactions, mysql/08-storage-engines, mysql/04-indexes, mysql/14-performance]
when_to_use: "Read before writing concurrent writes, diagnosing deadlocks, or adding SELECT ... FOR UPDATE."
---
# Locking

## Purpose

This document defines how InnoDB locking works and how to write concurrent code that is
correct and does not deadlock or stall. It covers row locks, gap locks, next-key locks,
intention locks, and the interaction between locking and indexing. It is written so an
agent can reason about *which rows a statement locks* before shipping it.

Locking is inseparable from [transactions](06-transactions.md): locks are acquired inside
a transaction and released at `COMMIT`/`ROLLBACK`. This doc assumes InnoDB; `MyISAM` uses
coarse table-level locks and is unsuitable for concurrent writes (see
[storage engines](08-storage-engines.md)).

## Why It Matters

Locking is the mechanism that makes concurrent transactions safe — but it is also the
mechanism that makes them slow or wedged. Get it wrong and you get deadlocks (queries
abort), lock-wait timeouts (queries hang then fail), or lock escalation that serializes
your whole workload behind one hot row. The failure mode is load-dependent: fine in a
test with one client, catastrophic under production concurrency. Worse, the *rows a
statement locks depend on the indexes it uses* — so a missing index quietly turns a
narrow row lock into a range that blocks unrelated writers.

## Core Principles

- **Locks follow the index, not the table.** InnoDB locks index records it scans. Without
  a usable index, a locking read scans and locks far more rows than it returns.
- **Reads are non-locking by default.** Plain `SELECT` uses MVCC and takes no locks. You
  opt into locking with `FOR UPDATE` (exclusive) or `FOR SHARE` (shared).
- **Gap locks prevent phantoms under REPEATABLE READ.** They lock the *space between*
  index records, so they can block inserts into ranges you never explicitly touched.
- **Deadlocks are normal; design to retry.** Two transactions that lock the same rows in
  opposite order will deadlock. InnoDB detects it and rolls one back — you retry.
- **Lock ordering prevents deadlocks.** If every transaction acquires locks in the same
  order (e.g., ascending primary key), cyclic waits cannot form.

## Best Practices

- Ensure every locking query (`FOR UPDATE`, `UPDATE`, `DELETE`) hits an index on the
  `WHERE` column. Verify with `EXPLAIN`; a full scan locks every row it examines.
- Acquire multiple row locks in a **deterministic order** (e.g., always by ascending id)
  across all code paths, so concurrent transactions cannot form a cycle.
- Use **READ COMMITTED** to shrink locking footprint when gap locks cause contention: it
  disables most gap locks and releases non-matching row locks sooner.
- Reach for `FOR UPDATE` only when you will write the row you read. For read-mostly
  optimistic patterns, use a `version` column and re-check on update instead.
- Keep the locked window minimal: `SELECT ... FOR UPDATE` immediately before the
  `UPDATE`, then `COMMIT`. Do not hold locks across application logic or I/O.
- Catch deadlock (1213) and lock-wait timeout (1205) and **retry the whole transaction**
  with a small bounded backoff. Never retry just the failed statement.
- Prefer `INSERT ... ON DUPLICATE KEY UPDATE` or `INSERT ... ON CONFLICT`-style upserts
  over select-then-insert, which races and can deadlock on the gap.

## Examples

**Good Example** — indexed lookup, consistent lock order

```sql
-- id is the primary key, so each FOR UPDATE locks exactly one index record.
-- Always locking the lower id first gives every transaction the same order,
-- so two concurrent transfers cannot deadlock on each other.
START TRANSACTION;
SELECT * FROM accounts WHERE id = LEAST(1, 2) FOR UPDATE;  -- locks id=1 first
SELECT * FROM accounts WHERE id = GREATEST(1, 2) FOR UPDATE; -- then id=2
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

**Bad Example** — unindexed locking read escalates to a range lock

```sql
-- No index on email: this FOR UPDATE scans the whole table and takes
-- next-key locks on every row it examines, blocking unrelated inserts and
-- updates until COMMIT — a table-wide lock in all but name.
START TRANSACTION;
SELECT * FROM accounts WHERE email = 'a@b.com' FOR UPDATE;
UPDATE accounts SET status = 'active' WHERE email = 'a@b.com';
COMMIT;
```

## Common Mistakes

- Running a `FOR UPDATE`/`UPDATE`/`DELETE` on a non-indexed column, locking far more rows
  than intended and serializing the workload.
- Acquiring locks in different orders across code paths, guaranteeing eventual deadlocks.
- Treating deadlock errors as fatal instead of retrying the transaction.
- Being surprised that an `INSERT` blocks under REPEATABLE READ — a gap lock from another
  transaction's ranged `SELECT ... FOR UPDATE` is holding the gap.
- Using `LOCK TABLES` in application code; it is a blunt instrument that defeats InnoDB's
  row-level concurrency.
- Holding locks across a slow external call, converting a millisecond lock into seconds of
  contention.

## Production Tips

- Inspect live contention with `SELECT * FROM performance_schema.data_lock_waits` and
  `information_schema.INNODB_TRX`; the blocking/blocked pairs point straight at the culprit.
- `SHOW ENGINE INNODB STATUS` prints the most recent deadlock, including both transactions'
  SQL and the locks held — read it before guessing.
- Track the `Innodb_row_lock_time` and deadlock counters; a rising trend means growing
  contention before users notice.

## AI Review Checklist

- Does every locking statement (`FOR UPDATE`, `UPDATE`, `DELETE`) use an index on its
  `WHERE` column, confirmed with `EXPLAIN`?
- Are multiple locks always acquired in the same deterministic order across all paths?
- Are deadlocks (1213) and lock-wait timeouts (1205) caught and the transaction retried?
- Is the locked window as short as possible, with no I/O or app logic inside it?
- Is `FOR UPDATE` used only when the row will actually be written?
- Is the isolation level (REPEATABLE READ vs READ COMMITTED) chosen with gap-lock impact
  in mind?

## Related

- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/08-storage-engines.md`
- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/14-performance.md`
