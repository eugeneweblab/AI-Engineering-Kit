---
id: sql/13-dml
topic: sql
slug: dml
title: "DML"
type: doc
order: 13
status: ready
tags: [sql, dml, deleted_at, RETURNING, updated_at, ROLLBACK, COMMIT, LIMIT]
related: [sql/12-ddl, sql/14-transactions, sql/05-joins, sql/06-subqueries, sql/100-common-antipatterns]
when_to_use: "Read before writing any INSERT, UPDATE, DELETE, MERGE, or bulk data change."
---
# DML

## Purpose

This document defines how to change data safely with Data Manipulation Language:
`INSERT`, `UPDATE`, `DELETE`, and `MERGE`/upsert. It is written so an agent can modify
rows without deleting the wrong ones, losing a concurrent writer's update, or locking a
table for the duration of a full-table rewrite.

DML is where data is created and destroyed. Unlike a bad `SELECT`, a bad `UPDATE` or
`DELETE` leaves no evidence and no undo once the transaction commits. The discipline
here is: scope precisely, run inside a transaction, and prove the row count before you
trust it.

## Why It Matters

The single most common production data-loss incident is a `DELETE` or `UPDATE` whose
`WHERE` clause was wrong or absent — every row in the table changed in one statement.
Concurrency makes it subtler: two requests read a value, both compute a new one, and
the second overwrites the first (a lost update). And bulk writes that ignore batching
can hold locks long enough to stall the application. These failures are silent and
permanent, so DML earns the same rigor as auth code.

## Core Principles

- **Every `UPDATE` and `DELETE` has a `WHERE` that selects known rows.** A missing or
  over-broad predicate is the default failure mode; guard against it deliberately.
- **Mutations run in transactions.** Group related writes so they commit or roll back
  as a unit; a half-applied change is corruption (see [transactions](14-transactions.md)).
- **Never trust "it probably matched the right rows."** Check the affected row count and
  fail loudly when it is not what you expected.
- **Concurrent writers need optimistic or explicit locking.** Read-modify-write without
  a version check or `FOR UPDATE` silently loses updates.
- **Upsert with the database's atomic construct**, not read-then-insert; the gap between
  the two is a race that produces duplicates or unique-violation errors.

## Best Practices

- Write the `WHERE` clause first and verify it with a `SELECT` before turning it into a
  `DELETE`/`UPDATE`. The predicate is the safety mechanism.
- Use `RETURNING` (PostgreSQL) to get the affected rows back in one round trip instead of
  a second query, and to confirm what actually changed.
- For read-modify-write, guard with an optimistic version/`updated_at` check in the
  `WHERE`; if zero rows matched, someone else won — retry, do not overwrite.
- Use `INSERT ... ON CONFLICT` (PostgreSQL) or `MERGE` (standard) for upserts so the
  check-and-insert is atomic under concurrency.
- Batch large deletes/updates into bounded chunks (e.g. by id range or `LIMIT`) so each
  transaction is short and locks are released promptly.
- Prefer set-based statements over row-by-row loops; one `UPDATE ... FROM` beats a
  thousand round trips and is atomic.
- Always use parameterized statements. String-concatenated values are SQL injection.

## Examples

**Good Example** — scoped, transactional, lost-update-safe

```sql
BEGIN;
-- Optimistic lock: only update if the row is still the version we read.
UPDATE accounts
   SET balance = balance - 100,
       version = version + 1
 WHERE id = 42
   AND version = 7            -- concurrent writer bumped version → 0 rows → we abort/retry
RETURNING id, balance;        -- confirm exactly one row changed
COMMIT;
```

**Bad Example** — unscoped and race-prone

```sql
-- Application read balance=500 earlier, now writes back a computed value.
UPDATE accounts SET balance = 400;  -- NO WHERE: every account is now 400
-- Even with WHERE id = 42, blindly writing the computed value overwrites
-- any concurrent deposit made since the read (lost update).
DELETE FROM accounts;               -- one keystroke from an empty table
```

## Common Mistakes

- Running `UPDATE`/`DELETE` with no `WHERE`, or a `WHERE` that is broader than intended.
- Read-modify-write with no version check, silently discarding a concurrent update.
- Emulating upsert with `SELECT` then `INSERT`, racing another writer into a duplicate.
- Deleting millions of rows in one statement, holding locks and bloating the WAL/undo log.
- Ignoring the affected row count, so "updated 0 rows" passes as success.
- Building statements by string concatenation, opening SQL injection.
- Assuming `UPDATE ... FROM`/`MERGE` join conditions are unique — a fan-out join updates
  a row multiple times unpredictably.

## Production Tips

- Wrap destructive one-off scripts in a transaction and inspect the row count *before*
  `COMMIT`; keep `ROLLBACK` one keystroke away.
- Soft-delete (a `deleted_at` column) where audit or recovery matters, and filter it in
  reads; hard `DELETE` only when retention policy requires it.
- For big backfills, batch by primary-key range, sleep briefly between batches, and log
  progress so the job is resumable and does not saturate I/O.

## AI Review Checklist

- Does every `UPDATE`/`DELETE` have a `WHERE` that selects exactly the intended rows?
- Are related mutations wrapped in a transaction that commits or rolls back atomically?
- Is read-modify-write protected by a version check, `FOR UPDATE`, or a set-based update?
- Are upserts done with `ON CONFLICT`/`MERGE` rather than check-then-insert?
- Are large mutations batched to keep transactions and locks short?
- Is the affected row count checked instead of assumed?
- Are all values passed as parameters, never string-concatenated?

## Related

- `knowledge/sql/12-ddl.md`
- `knowledge/sql/14-transactions.md`
- `knowledge/sql/05-joins.md`
- `knowledge/sql/06-subqueries.md`
- `knowledge/sql/100-common-antipatterns.md`
