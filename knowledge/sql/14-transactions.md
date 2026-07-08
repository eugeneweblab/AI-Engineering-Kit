---
id: sql/14-transactions
topic: sql
slug: transactions
title: "Transactions"
type: doc
order: 14
status: ready
tags: [sql, transactions]
related: [sql/13-dml, sql/15-indexes, sql/12-ddl, sql/23-performance, sql/100-common-antipatterns]
when_to_use: "Read before writing multi-statement writes, choosing an isolation level, or debugging deadlocks and lost updates."
---
# Transactions

## Purpose

This document defines how to group work into atomic, isolated units with `BEGIN`,
`COMMIT`, and `ROLLBACK`, and how to choose an isolation level. It is written so an agent
can make concurrent writes correct without inviting deadlocks, lost updates, or a
transaction held open across a network call.

A transaction is a promise: either all of its changes happen, or none do, and concurrent
transactions see a consistent view. The hard part is not `BEGIN`/`COMMIT` — it is knowing
which anomalies your isolation level still permits and defending against them.

## Why It Matters

Concurrency bugs are the worst kind: they pass every test, work in staging, and corrupt
data only under production load, non-deterministically. The default isolation level in
most databases is `READ COMMITTED`, which still allows lost updates and non-repeatable
reads — so "I used a transaction" does not mean "it is correct." Meanwhile a transaction
left open (especially across an HTTP or RPC call) holds locks and pins old row versions,
stalling other writers and bloating storage. Correctness and availability both live here.

## Core Principles

- **A transaction is atomic and all-or-nothing.** Partial application is corruption; on
  any error, roll back the whole unit.
- **Isolation level is a correctness decision, not a default.** Know what anomalies your
  level allows and either raise the level or guard against them.
- **Keep transactions short and CPU-local.** Never hold a transaction open across a
  network call, user think-time, or a queue read. Locks are held until `COMMIT`.
- **Acquire locks in a consistent order.** Deadlocks come from two transactions taking
  the same locks in opposite orders; a fixed order prevents the cycle.
- **Deadlocks and serialization failures are normal — retry them.** The database will
  abort one transaction; the caller must catch and re-run the whole unit.

## Best Practices

- Pick the isolation level per operation: `READ COMMITTED` for ordinary work,
  `REPEATABLE READ`/`SERIALIZABLE` for read-modify-write on invariants (balances, stock).
- For lost-update protection under `READ COMMITTED`, use `SELECT ... FOR UPDATE` to lock
  the row, or an optimistic `version`/`updated_at` check in the `WHERE`.
- Under `SERIALIZABLE`, wrap the transaction in a retry loop; serialization failures
  (SQLSTATE `40001`) are expected, not exceptional.
- Set `idle_in_transaction_session_timeout` so a forgotten open transaction cannot pin
  locks and old row versions indefinitely.
- Do all external I/O (calling an API, sending email) *outside* the transaction, before
  or after — never between `BEGIN` and `COMMIT`.
- Keep DDL out of long transactions; schema changes take strong locks (see [DDL](12-ddl.md)).
- Use savepoints for partial rollback within a large transaction only when genuinely
  needed; they add lock-tracking overhead.

## Examples

**Good Example** — locked row, short scope, retryable

```sql
BEGIN ISOLATION LEVEL READ COMMITTED;

-- Take a row lock so no concurrent transaction can modify this balance until we commit.
SELECT balance FROM accounts WHERE id = 42 FOR UPDATE;

UPDATE accounts SET balance = balance - 100 WHERE id = 42 AND balance >= 100;
-- 0 rows means insufficient funds → application rolls back and reports it.

COMMIT;  -- lock released immediately; no external calls happened inside the transaction
```

**Bad Example** — read-then-write race, long-held locks

```sql
BEGIN;
SELECT balance FROM accounts WHERE id = 42;   -- reads 500, no lock taken
-- ... application calls a payment API here, holding the transaction open ...
UPDATE accounts SET balance = 400 WHERE id = 42;  -- overwrites any concurrent change (lost update)
COMMIT;  -- locks + external latency held the transaction open for seconds
```

## Common Mistakes

- Assuming the default `READ COMMITTED` prevents lost updates — it does not.
- Read-modify-write with no `FOR UPDATE` and no version check.
- Holding a transaction open across a network/API call, blocking other writers.
- No retry loop around `SERIALIZABLE`/deadlock aborts, so transient failures surface as
  user-facing errors.
- Inconsistent lock ordering across code paths, producing deadlocks under load.
- Doing external side effects (email, webhook) inside the transaction, so a rollback
  leaves the side effect done but the data reverted.
- Forgetting to `ROLLBACK` on the error path, leaking an open transaction.

## Production Tips

- Monitor for long-running and idle-in-transaction sessions; alert before they cause
  lock pileups or vacuum/undo bloat.
- Log deadlock events with the involved statements; a recurring deadlock almost always
  reveals an inconsistent lock-ordering bug to fix, not just retry.
- Make retryable transactions idempotent (or key them) so a retry after a partial
  network failure does not double-apply the effect.

## AI Review Checklist

- Is the isolation level chosen deliberately for the invariant being protected?
- Is read-modify-write guarded with `FOR UPDATE` or an optimistic version check?
- Are `SERIALIZABLE` and deadlock aborts caught and retried?
- Is the transaction free of network/API calls between `BEGIN` and `COMMIT`?
- Are locks acquired in a consistent order across code paths?
- Are external side effects moved outside the transaction boundary?
- Is there an `idle_in_transaction` timeout and a `ROLLBACK` on every error path?

## Related

- `knowledge/sql/13-dml.md`
- `knowledge/sql/15-indexes.md`
- `knowledge/sql/12-ddl.md`
- `knowledge/sql/23-performance.md`
- `knowledge/sql/100-common-antipatterns.md`
