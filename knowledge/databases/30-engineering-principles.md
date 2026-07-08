---
id: databases/30-engineering-principles
topic: databases
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [databases, engineering-principles]
related: [databases/09-transactions, databases/23-data-integrity, databases/17-migrations, databases/07-indexing, databases/28-best-practices]
when_to_use: "Read before designing a schema, writing data-access code, or reviewing any change that touches the database."
---
# Engineering Principles

## Purpose

This document defines the durable engineering principles for working with databases:
how to treat the schema, transactions, integrity, and access patterns so that data
stays correct as the system grows. It is the reasoning layer beneath the specific
technique docs — [indexing](07-indexing.md), [query optimization](08-query-optimization.md),
[migrations](17-migrations.md), and the rest. Read it so that every schema and query you
write starts from the same defensible baseline.

## Why It Matters

Application code is disposable — you can redeploy it in minutes. Data is not. A dropped
column, a lost transaction, or a bad migration is often unrecoverable, and the damage is
silent: the app keeps serving while the numbers quietly go wrong. The database is also the
one component every request funnels through, so its correctness and its performance ceiling
bound the whole system. Because the blast radius is total and mistakes are hard to reverse,
data-access code is held to a higher bar than ordinary application code.

## Core Principles

- **The database is the source of truth, not the application.** Enforce invariants where
  the data lives — constraints, foreign keys, `NOT NULL`, `CHECK`, `UNIQUE`. Application
  checks are a convenience layer that races and gets bypassed; the database is the only
  guard that always runs.
- **Make illegal states unrepresentable.** Model the schema so bad data cannot be written
  in the first place. A constraint that rejects the write beats a nightly job that finds
  the corruption.
- **A transaction is a unit of correctness, not a performance knob.** Wrap every set of
  writes that must succeed or fail together in one transaction. Never leave related writes
  un-atomic to "save a round trip."
- **Design for the read and write patterns you actually have.** Model and index for the
  queries the application runs, not for abstract purity. An unindexed hot query is a
  latent outage.
- **Every schema change is a migration, forward and backward.** Schema evolves under live
  traffic. Treat each change as a reversible, deploy-safe step, never a manual edit.
- **Assume concurrency.** Two requests will touch the same row at the same time. Reason
  about isolation and locking explicitly; do not assume your write is alone.

## Best Practices

- Declare constraints in the schema: foreign keys, `NOT NULL`, `UNIQUE`, `CHECK`, and
  sensible defaults. Push validation down to the closest layer to the data.
- Use the narrowest correct column types (`bigint` vs `int`, `timestamptz` vs `timestamp`,
  `numeric` for money — never `float`). The type is the first line of integrity.
- Keep transactions short and touch rows in a consistent order to avoid deadlocks; do no
  network or user I/O while holding a transaction open.
- Choose isolation deliberately. Know your engine's default (often `READ COMMITTED`) and
  raise to `REPEATABLE READ`/`SERIALIZABLE` for read-modify-write logic that must not race.
- Always parameterize queries. String-built SQL is both a correctness and a
  [security](19-security.md) failure.
- Paginate with keyset (seek) pagination on large tables; `OFFSET` scans and discards rows
  and degrades linearly.
- Index the columns that filter, join, and sort real queries — and drop indexes nothing
  uses, because each one taxes every write.
- Make writes idempotent where retries are possible (unique keys, upserts). Networks retry;
  design so a duplicate delivery cannot double-charge or double-insert.

## Examples

**Good Example** — atomic transfer with the invariant enforced in the database

```sql
-- Balance can never go negative: enforced by the schema, not by hope.
ALTER TABLE accounts ADD CONSTRAINT balance_non_negative CHECK (balance >= 0);

BEGIN;
  -- Both updates commit together or not at all. A crash between them rolls back.
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- CHECK rejects overdraft
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

**Bad Example** — check in the app, writes outside a transaction

```python
# Two requests read the same balance before either writes: both pass the check,
# both debit, and the account goes negative. The check raced; nothing enforced it.
row = db.execute("SELECT balance FROM accounts WHERE id = 1").fetchone()
if row.balance >= 100:                       # app-level guard, not atomic
    db.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    db.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
    # No BEGIN/COMMIT: a failure after the debit loses the money permanently.
```

## Common Mistakes

- Enforcing invariants only in application code, so concurrent requests corrupt data.
- Storing money in `float`, or timestamps without a time zone, then chasing rounding and
  off-by-an-hour bugs forever.
- Leaving a transaction open across a slow call (HTTP, email), holding locks and starving
  other writers.
- Building SQL by string concatenation, opening injection and breaking on odd input.
- Adding indexes speculatively and never measuring, so writes slow down for no read gain.
- Editing production schema by hand instead of through a reviewed, reversible migration.

## Production Tips

- Enforce every new invariant with a migration that first backfills, then adds the
  constraint `NOT VALID`, then validates — so the change is online and reversible.
- Keep a slow-query log and alert on plan regressions; a query that was fast at 10k rows
  can table-scan at 10M.
- Load-test with production-scale data volumes, not a seed of 100 rows — most database
  bugs only appear at size.

## AI Review Checklist

- Are the data invariants enforced by database constraints, not only in application code?
- Is every group of related writes wrapped in a single transaction?
- Are column types correct and precise (`numeric` for money, `timestamptz` for time)?
- Is the isolation level appropriate for any read-modify-write logic?
- Are all queries parameterized rather than string-built?
- Do the indexes match the actual filter/join/sort columns of real queries?
- Is every schema change expressed as a reversible, deploy-safe migration?

## Related

- `knowledge/databases/09-transactions.md`
- `knowledge/databases/23-data-integrity.md`
- `knowledge/databases/17-migrations.md`
- `knowledge/databases/07-indexing.md`
- `knowledge/databases/28-best-practices.md`
