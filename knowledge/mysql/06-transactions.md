---
id: mysql/06-transactions
topic: mysql
slug: transactions
title: "MySQL Transactions"
type: doc
order: 6
status: ready
tags: [mysql, transactions]
related: [mysql/07-locking, mysql/08-storage-engines, mysql/09-replication, mysql/05-query-optimization]
when_to_use: "Read before writing any code that modifies more than one row or table and must be all-or-nothing."
---
# MySQL Transactions

## Purpose

This document defines how to group MySQL statements into an atomic unit of work that
either fully commits or fully rolls back, and how to pick the isolation level that
matches your correctness needs. It is written so an agent can wrap a multi-statement
operation in a transaction without introducing lost updates, phantom reads, or
half-applied writes.

Transactions are a property of the **InnoDB** storage engine. `MyISAM` and `MEMORY`
tables silently ignore `BEGIN`/`COMMIT` — see [storage engines](08-storage-engines.md).
If your table is not InnoDB, none of this applies and your "transaction" is a no-op.

## Why It Matters

A transaction is the contract that keeps data consistent when an operation touches
multiple rows. Without it, a crash, error, or concurrent writer between two statements
leaves the database in a state that no valid business rule allows: money debited but
never credited, an order with no line items, a counter double-incremented. These bugs
are intermittent and load-dependent — they pass every test and surface only in
production under concurrency, where they are hardest to reproduce and most expensive to
unwind. Correct transaction boundaries are cheaper than reconciliation scripts.

## Core Principles

- **Wrap every multi-statement invariant in one transaction.** If two writes must both
  succeed or both fail, they belong in the same transaction — no exceptions.
- **Commit or roll back on every path.** An open transaction holds locks and pins the
  undo log. Leaking one starves other writers and bloats the tablespace.
- **Keep transactions short.** A transaction is a lock-holding window. Do no network
  calls, no user prompts, no slow computation while one is open.
- **Pick the weakest isolation level that is still correct.** Stronger isolation costs
  concurrency and increases deadlock risk. Do not raise it "to be safe."
- **Read errors are not commits.** A statement failing inside a transaction does not
  auto-roll-back the transaction (unless it is a deadlock/lock-timeout); you must decide.

## Best Practices

- Set `autocommit` awareness explicitly. By default `autocommit=1`, so a bare statement
  is its own transaction. Use an explicit `START TRANSACTION` when you need more than one.
- Understand the four isolation levels. InnoDB defaults to **REPEATABLE READ**; MySQL's
  own replication-safe default. Use **READ COMMITTED** for high-concurrency OLTP where you
  want fewer gap locks and each statement to see the latest committed data.
- Never use **READ UNCOMMITTED** (dirty reads) or **SERIALIZABLE** (converts plain SELECTs
  to locking reads) unless you can state exactly why.
- Prevent lost updates with `SELECT ... FOR UPDATE` (pessimistic) or an optimistic
  `WHERE version = ?` guard plus a retry — never read-modify-write without one.
- Handle deadlocks by **retrying** the whole transaction. InnoDB error 1213 is expected
  under concurrency, not a bug; wrap the transaction in a bounded retry loop.
- Roll back in the error path of the calling code, and let connection-pool teardown roll
  back anything still open. Never leave commit/rollback to chance.
- Do DDL (`ALTER`, `CREATE`, `DROP`) outside transactions — in MySQL it causes an
  **implicit commit**, silently ending any transaction you thought was open.

## Examples

**Good Example** — atomic transfer, correct isolation, deadlock retry

```sql
-- Both rows move together or not at all. FOR UPDATE locks the two accounts
-- so a concurrent transfer cannot read a stale balance (prevents lost update).
START TRANSACTION;

SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;  -- lock source row
SELECT balance FROM accounts WHERE id = 2 FOR UPDATE;  -- lock destination row

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT;  -- releases both locks; on error the caller issues ROLLBACK and retries
```

**Bad Example** — no transaction, read-modify-write race

```sql
-- Two concurrent debits both read 500, both write 400: one debit is lost.
SELECT balance FROM accounts WHERE id = 1;   -- app reads 500
-- ... application subtracts 100 in code ...
UPDATE accounts SET balance = 400 WHERE id = 1;  -- clobbers the other writer

-- The credit is a separate statement with no shared boundary: a crash here
-- leaves money debited and never credited.
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
```

## Common Mistakes

- Assuming a table is transactional when it is `MyISAM` — the `BEGIN`/`COMMIT` do nothing.
- Read-modify-write in application code without `FOR UPDATE` or a version guard, causing
  lost updates under concurrency.
- Leaving a transaction open across an external HTTP call or user think-time, holding
  locks for seconds and blocking other writers.
- Not retrying on deadlock (error 1213) or lock wait timeout (error 1205), surfacing a
  routine concurrency event as a user-facing 500.
- Running an `ALTER TABLE` mid-transaction and being surprised the prior writes committed
  (implicit commit).
- Raising isolation to SERIALIZABLE to "fix" a race, then blaming MySQL for the deadlocks
  and throughput collapse that follow.

## Production Tips

- Set a sane `innodb_lock_wait_timeout` (default 50s is often too long for web requests;
  5–10s fails fast and lets the request retry).
- Monitor `SHOW ENGINE INNODB STATUS` and `information_schema.INNODB_TRX` for long-running
  or stuck transactions; alert on transactions open longer than a few seconds.
- Keep the number of statements — and rows locked — per transaction small; large
  transactions bloat the undo log and stall purge.

## AI Review Checklist

- Is every multi-row / multi-table invariant wrapped in a single transaction?
- Are the affected tables InnoDB (so the transaction actually has effect)?
- Is there a `ROLLBACK` on every error path, and is nothing left open on early return?
- Is read-modify-write protected by `FOR UPDATE` or an optimistic version check?
- Are deadlocks and lock-wait timeouts retried rather than propagated as fatal errors?
- Is the isolation level the weakest one that is still correct, and is any raise justified?
- Are DDL statements kept out of open transactions to avoid surprise implicit commits?

## Related

- `knowledge/mysql/07-locking.md`
- `knowledge/mysql/08-storage-engines.md`
- `knowledge/mysql/09-replication.md`
- `knowledge/mysql/05-query-optimization.md`
