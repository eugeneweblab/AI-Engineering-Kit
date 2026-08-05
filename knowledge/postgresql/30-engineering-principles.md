---
id: postgresql/30-engineering-principles
topic: postgresql
slug: engineering-principles
title: "PostgreSQL Engineering Principles"
type: doc
order: 30
status: ready
tags: [postgresql, engineering-principles]
related: [postgresql/06-transactions, postgresql/04-indexes, postgresql/22-migrations, postgresql/05-query-planner, postgresql/25-best-practices]
when_to_use: "Read before designing a schema, writing migrations, or making any decision that affects how the database enforces correctness."
---
# PostgreSQL Engineering Principles

## Purpose

This document defines the durable engineering principles for building on PostgreSQL:
how to let the database do the work it is best at, and how to keep data correct under
concurrency and change. It is the lens through which the topic's other docs — schema,
[transactions](06-transactions.md), [indexes](04-indexes.md),
[migrations](22-migrations.md) — should be read.

These are not tuning tips. They are the invariants that keep a system correct as it
scales, and they are cheap to honor early and expensive to retrofit later.

## Why It Matters

The database is the one component you cannot easily replace and the one place where
correctness is permanent. A lost update in application code is one bad request; a
missing constraint in the schema is corruption that accumulates silently for months
until a report shows numbers that cannot be reconciled. PostgreSQL gives you strong
tools — ACID transactions, foreign keys, check constraints, MVCC — but only if you
push correctness *into* the database instead of hoping every code path remembers to
enforce it. Every rule that lives in the schema is enforced for all writers, forever,
including the ones you have not written yet.

## Core Principles

- **The database is the source of truth, not a dumb store.** Enforce invariants with
  constraints (`NOT NULL`, `CHECK`, `UNIQUE`, `FOREIGN KEY`), not application code.
  App-level checks race under concurrency; a constraint cannot be bypassed.
- **Model for correctness first, performance second.** Get the types and constraints
  right, then add indexes where the [query planner](05-query-planner.md) proves you
  need them. Never denormalize before you have measured the cost.
- **Every write is a transaction; make its boundary deliberate.** Group operations that
  must succeed or fail together, and keep transactions short. Long transactions hold
  locks and block [vacuum](20-vacuum.md).
- **Assume concurrency.** Two sessions run your code at once. Read-modify-write without
  a lock or a proper isolation level is a lost update waiting to happen.
- **Migrations are code and run against live data.** They must be reversible in intent,
  non-blocking, and safe to deploy before the code that depends on them.
- **Prefer the strictest type that fits.** `timestamptz` not `timestamp`, `numeric` for
  money not `float`, a real `enum`/lookup table not free-text. The type is a constraint.

## Best Practices

- Use `timestamptz` for every point in time; store UTC and convert at the edges. Naive
  `timestamp` silently drops the offset and produces wrong intervals across DST.
- Use `numeric` for money and any exact decimal; `float`/`double` cannot represent
  `0.10` and will lose cents. Reserve floats for genuinely approximate quantities.
- Give every table a primary key. Prefer `bigint GENERATED ALWAYS AS IDENTITY` or a
  UUID; avoid `serial` (its sequence-ownership quirks bite on restore).
- Add foreign keys with an explicit `ON DELETE` action. An unindexed FK column makes
  deletes on the parent slow — index the referencing column.
- Make writes idempotent where possible: `INSERT ... ON CONFLICT DO NOTHING/UPDATE`
  and natural unique keys turn retries into no-ops instead of duplicates.
- Choose an isolation level deliberately. `READ COMMITTED` (the default) does not
  prevent lost updates across statements; use `SELECT ... FOR UPDATE` or
  `SERIALIZABLE` for read-modify-write. See [transactions](06-transactions.md).
- Let the planner work: keep columns "sargable" (no functions wrapping an indexed
  column in a `WHERE`), and `ANALYZE` after bulk loads so statistics are fresh.
- Version every schema change as a forward migration in source control. The database's
  current shape must be reproducible from an empty database.

## Examples

**Good Example** — the invariant lives in the schema and the update is atomic

```sql
-- Constraints make bad states unrepresentable for every writer.
CREATE TABLE account (
  id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  owner_id   bigint NOT NULL REFERENCES app_user(id),
  balance    numeric(14,2) NOT NULL DEFAULT 0
             CHECK (balance >= 0),                 -- overdraft is impossible, not "unlikely"
  updated_at timestamptz NOT NULL DEFAULT now()    -- tz-aware, UTC
);

-- Single atomic statement: no read-modify-write gap for a concurrent session to slip into.
UPDATE account
   SET balance = balance - 100.00, updated_at = now()
 WHERE id = 42 AND balance >= 100.00;              -- row-level lock held for the statement
```

**Bad Example** — invariants in app code, lost update under concurrency

```sql
-- App reads, decides in memory, then writes back. Two sessions both read 100,
-- both pass the check, both write 0 — one withdrawal vanishes. No CHECK, so the
-- balance can also go negative and nothing in the DB objects.
SELECT balance FROM account WHERE id = 42;         -- app sees 100
-- ...application checks `balance >= 100` here (races)...
UPDATE account SET balance = 0 WHERE id = 42;      -- clobbers the other write
```

## Common Mistakes

- Enforcing uniqueness or non-null "in the service layer" instead of with constraints,
  so a second instance or a manual `INSERT` corrupts the table.
- Using `timestamp` (no tz) or `float` for money — both lose information silently.
- Read-modify-write under `READ COMMITTED` with no `FOR UPDATE`, causing lost updates.
- Wrapping migrations in one giant transaction that takes an `ACCESS EXCLUSIVE` lock and
  stalls the whole table on deploy.
- Adding indexes speculatively instead of from `EXPLAIN` evidence, paying write cost for
  reads that never happen.
- Storing enums as free-text `varchar`, so typos become permanent distinct values.

## Production Tips

- Set `lock_timeout` and `statement_timeout` for migration sessions so a blocked DDL
  fails fast instead of freezing traffic behind it.
- Turn on `log_min_duration_statement` to surface slow queries before users report them.
- Keep autovacuum aggressive on high-churn tables; a bloated table is a correctness-
  adjacent problem (dead tuples, transaction-ID wraparound risk).

## AI Review Checklist

- Is every invariant enforced by a constraint, not just by application code?
- Are time columns `timestamptz` and money columns `numeric`, never `float`?
- Does every table have a primary key, and every foreign key an indexed column?
- Is each read-modify-write protected by `FOR UPDATE` or a serializable transaction?
- Are transactions scoped to the smallest unit of atomic work and kept short?
- Is every schema change a version-controlled, non-blocking forward migration?
- Do new indexes trace back to `EXPLAIN` evidence, not guesswork?

## Related

- `knowledge/postgresql/06-transactions.md`
- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/22-migrations.md`
- `knowledge/postgresql/05-query-planner.md`
- `knowledge/postgresql/25-best-practices.md`
