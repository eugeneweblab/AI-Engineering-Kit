---
id: postgresql/06-transactions
topic: postgresql
slug: transactions
title: "PostgreSQL Transactions"
type: doc
order: 6
status: ready
tags: [postgresql, transactions, SERIALIZABLE, execute, VACUUM, idle_in_transaction_session_timeout, fetchone, lines]
related: [postgresql/07-locking, postgresql/05-query-planner, postgresql/04-indexes, postgresql/20-vacuum]
when_to_use: "Read before writing any multi-statement write, choosing an isolation level, or handling a serialization/deadlock error."
---
# PostgreSQL Transactions

## Purpose

This document defines how to group PostgreSQL statements into atomic units of work,
which isolation level to pick, and how to handle the errors that isolation produces.
It is written so an agent can implement a correct transaction boundary and retry loop
without silently corrupting data under concurrency.

A transaction answers "did all of this happen, or none of it?". PostgreSQL uses MVCC
(multiversion concurrency control): readers never block writers and writers never block
readers, so most correctness bugs come from choosing the wrong isolation level rather
than from locking. See [locking](07-locking.md) for the cases where writers do block.

## Why It Matters

Concurrency bugs are the hardest class of defect to reproduce and the easiest to ship:
the code passes every single-user test and fails only when two requests interleave in
production. A lost update — two sessions read a balance, both add to it, one overwrites
the other — leaves no error in the log, just wrong data. Because PostgreSQL defaults to
`READ COMMITTED`, which does *not* prevent lost updates across separate statements, the
default is safe for simple writes and dangerous for read-modify-write logic. Getting the
boundary and isolation level right is the difference between a database that enforces
invariants and one that merely stores whatever the last writer left.

## Core Principles

- **Keep transactions short.** A transaction holds a snapshot and locks for its entire
  life. Long transactions block `VACUUM` from reclaiming dead tuples (bloat) and hold row
  locks that stall other writers. Never do network I/O or wait for user input inside one.
- **Pick isolation by the invariant you must protect, not by habit.** `READ COMMITTED`
  (default) prevents dirty reads only. `REPEATABLE READ` gives a stable snapshot and
  blocks lost updates on the same rows. `SERIALIZABLE` guarantees the result equals *some*
  serial order — the only level that is safe for arbitrary read-modify-write logic.
- **Assume `SERIALIZABLE` and `REPEATABLE READ` transactions can fail and retry them.**
  They raise `40001` (serialization_failure) when a conflict is detected. A retry loop is
  not optional; it is part of using these levels.
- **One logical operation, one transaction.** Do not split a bank transfer across two
  transactions "to be faster" — a crash between them leaves the invariant broken.
- **Never swallow a rollback.** If any statement fails, the whole transaction is aborted
  and every subsequent statement errors until you `ROLLBACK`. Detect and surface it.

## Best Practices

- Set the isolation level as the first statement: `BEGIN ISOLATION LEVEL REPEATABLE READ;`
  or via the driver, so it is explicit and reviewable.
- For read-modify-write, either use `SERIALIZABLE`/`REPEATABLE READ` with a retry loop, or
  do the update atomically in SQL (`UPDATE ... SET balance = balance - 100`) so no gap exists.
- Wrap `40001` and `40P01` (deadlock) in a bounded retry with exponential backoff and jitter,
  capped at 3–5 attempts. Retrying is correct only if the whole transaction re-runs.
- Use `SAVEPOINT` for sub-operations you want to recover from without aborting the outer
  transaction — but keep them rare; they add overhead and complexity.
- Set `idle_in_transaction_session_timeout` (e.g. 30s) so a leaked open transaction cannot
  pin the database's oldest snapshot forever.
- Match application-level retries to idempotency: a retried transaction must produce the
  same result, not double-charge.

## Examples

**Good Example** — atomic update, explicit isolation, retry on conflict

```sql
-- Read-modify-write done atomically: the subtraction happens inside the UPDATE,
-- so no two sessions can read the same balance and both overwrite it.
BEGIN;
UPDATE accounts SET balance = balance - 100
 WHERE id = 42 AND balance >= 100;   -- guard prevents overdraft in one statement
-- Check row count in the app; 0 rows means insufficient funds -> ROLLBACK.
UPDATE accounts SET balance = balance + 100 WHERE id = 99;
COMMIT;
```

```python
# Serializable read-modify-write MUST be wrapped in a retry loop.
for attempt in range(5):
    try:
        with conn.transaction(isolation_level="SERIALIZABLE"):
            total = conn.execute("SELECT sum(amount) FROM lines WHERE order_id=%s", [oid]).fetchone()[0]
            conn.execute("INSERT INTO lines (order_id, amount) VALUES (%s, %s)", [oid, total * 0.1])
        break
    except SerializationFailure:      # 40001 -- expected under contention, retry whole txn
        sleep(random.uniform(0, 0.1 * 2 ** attempt))
```

**Bad Example** — read-modify-write across statements at READ COMMITTED

```sql
BEGIN;  -- default READ COMMITTED
SELECT balance FROM accounts WHERE id = 42;   -- app reads 500
-- ... app computes 500 - 100 = 400 ...
UPDATE accounts SET balance = 400 WHERE id = 42;  -- clobbers a concurrent update: LOST UPDATE
COMMIT;
-- Two sessions both read 500, both write 400. One withdrawal silently vanishes.
```

## Common Mistakes

- Read-modify-write at `READ COMMITTED` without a lock or atomic expression → lost updates.
- Using `SERIALIZABLE`/`REPEATABLE READ` but not retrying `40001`, so requests fail randomly.
- Holding a transaction open across an HTTP call, message publish, or `sleep` → bloat and lock waits.
- Catching an error mid-transaction and continuing to issue statements, all of which error
  with "current transaction is aborted".
- Splitting one invariant across multiple transactions, leaving a window where it is violated.
- Assuming a single `UPDATE` needs a transaction wrapper — a lone statement is already atomic.

## Production Tips

- Monitor `pg_stat_activity` for `state = 'idle in transaction'` with a long `xact_start`;
  these are the transactions that cause bloat and lock storms.
- Alert on rising `40001`/`40P01` rates — they indicate contention that may need a design
  change (shorter transactions, better lock ordering, or queue-based serialization).
- Track the oldest running `xact_start` against `VACUUM` progress; the oldest transaction
  sets the horizon for tuple cleanup. See [vacuum](20-vacuum.md).

## AI Review Checklist

- Is every read-modify-write either atomic in SQL or run at `REPEATABLE READ`/`SERIALIZABLE`?
- Is there a bounded retry loop with backoff around `40001` and `40P01`?
- Are transactions free of network I/O, user waits, and other blocking calls?
- Is the isolation level set explicitly rather than relying on the default?
- Does the code detect a rollback and stop issuing statements after a failure?
- Is `idle_in_transaction_session_timeout` configured to cap leaked transactions?
- Is each retried transaction idempotent so a retry cannot double-apply an effect?

## Related

- `knowledge/postgresql/07-locking.md`
- `knowledge/postgresql/05-query-planner.md`
- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/20-vacuum.md`
