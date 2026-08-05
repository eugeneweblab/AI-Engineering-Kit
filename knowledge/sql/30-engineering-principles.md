---
id: sql/30-engineering-principles
topic: sql
slug: engineering-principles
title: "SQL Engineering Principles"
type: doc
order: 30
status: ready
tags: [sql, engineering-principles, VARCHAR, TIMESTAMPTZ, EXPLAIN, CHECK, customers, SUPERUSER]
related: [sql/14-transactions, sql/15-indexes, sql/17-query-optimization, sql/22-security, sql/26-best-practices]
when_to_use: "Read before designing a schema, writing non-trivial queries, or reviewing SQL that will run against production data."
---
# SQL Engineering Principles

## Purpose

This document defines the durable engineering principles that govern all SQL work:
how to model data, write queries, and change schemas so the result is correct,
performant, and safe to run against production. It is the lens through which every
other doc in this topic should be read. When a specific guide and a general principle
appear to conflict, the principle wins unless the guide gives a concrete reason.

SQL is declarative: you describe the result you want, and the engine decides how to
produce it. That gap between intent and execution is where most defects live. These
principles exist to keep intent, execution, and data integrity aligned.

## Why It Matters

A single bad query or migration touches every row it can reach, not one request. An
unbounded `UPDATE`, a missing index on a hot join, or a nullable column that should
have been `NOT NULL` degrades or corrupts data at scale and often silently. Unlike
application bugs, data bugs persist after the code is fixed — you must repair the rows
too. Because the blast radius is the whole dataset and the failure is frequently
invisible until a report is wrong, SQL is held to a higher bar than ordinary code.

## Core Principles

- **The database owns integrity, not the application.** Encode invariants as
  constraints (`NOT NULL`, `UNIQUE`, `CHECK`, `FOREIGN KEY`). Application checks race
  under concurrency; a constraint is enforced atomically for every writer.
- **Make the schema express the domain.** Correct types, keys, and constraints are
  documentation the engine enforces. A `TIMESTAMPTZ` column, not `VARCHAR`, for a time.
- **Every query has a plan — know it before production.** `EXPLAIN` is not optional for
  any query on a large table. Guessing at performance is how full-table scans reach prod.
- **Set-based, not row-by-row.** Express work as one statement over a set. Looping in
  application code to issue N queries (the N+1 pattern) is orders of magnitude slower.
- **Transactions are the unit of correctness.** Group writes that must succeed or fail
  together into one transaction. Choose an isolation level deliberately, not by default.
- **Migrations are code and must be reversible and online.** A schema change is a
  deploy: version it, review it, test the rollback, and avoid locking hot tables.
- **Least privilege for every connection.** The app's runtime role should not own the
  schema or hold `SUPERUSER`. Read replicas get read-only roles.

## Best Practices

- Declare columns `NOT NULL` unless absence is a real, distinct state; `NULL` breaks
  equality, aggregates, and `IN` in ways that surprise. Give sensible `DEFAULT`s.
- Add a `FOREIGN KEY` for every real relationship, and index the referencing column —
  the constraint alone does not create an index, so joins and cascades scan without one.
- Filter and aggregate in SQL, close to the data; return only the rows and columns you
  need. Shipping raw rows to the app to filter there wastes I/O, memory, and network.
- Always constrain writes: an `UPDATE`/`DELETE` without a `WHERE` (or with a wrong one)
  rewrites the table. Test the `WHERE` with a `SELECT` first.
- Parameterize every value. Never build SQL by string concatenation — it is the direct
  cause of injection (see [security](22-security.md)).
- Keep transactions short. Long-running transactions hold locks and bloat MVCC versions,
  starving other writers.
- Version schema with migration tooling; never hand-edit production schema.

## Examples

**Good Example** — the schema enforces the invariant; the write is set-based and bounded

```sql
-- The DB guarantees no order can reference a missing customer and no negative total,
-- regardless of what any application code does.
CREATE TABLE orders (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id BIGINT      NOT NULL REFERENCES customers(id),
  total_cents INTEGER     NOT NULL CHECK (total_cents >= 0),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON orders (customer_id); -- FK is not auto-indexed; joins need this

-- One set-based statement, explicitly bounded, instead of a per-row loop.
UPDATE orders SET status = 'shipped'
WHERE id = ANY($1) AND status = 'paid';
```

**Bad Example** — integrity pushed to the app, unbounded write, row-by-row loop

```sql
-- No FK, no CHECK: any customer_id and any total, valid or not, is accepted.
CREATE TABLE orders (
  id          INT,
  customer_id INT,
  total_cents INT,           -- can go negative; no constraint catches it
  created_at  VARCHAR(32)    -- a timestamp stored as text: unsortable, unvalidated
);

-- Missing WHERE: this rewrites EVERY row in the table.
UPDATE orders SET status = 'shipped';
-- ...and the app "fixes" it by looping one UPDATE per id (N round trips).
```

## Common Mistakes

- Enforcing uniqueness or foreign keys in application code instead of with constraints,
  then losing the race under concurrent writers.
- Storing dates, money, or enums as `VARCHAR`, defeating validation, sorting, and math.
- Running `UPDATE`/`DELETE` in production without first checking the `WHERE` via `SELECT`.
- Never running `EXPLAIN`, so a query that works on 1k rows melts on 10M.
- N+1 query loops from an ORM: one query per row instead of one join.
- Wrapping unrelated work in one long transaction, holding locks far longer than needed.
- Running the app as a schema-owning or superuser role.

## Production Tips

- Set `statement_timeout` and `lock_timeout` on the application role so a runaway query
  cannot pin the database indefinitely.
- Track the slow-query log and `pg_stat_statements` (or the engine equivalent); optimize
  by measured cost, not intuition.
- Take a backup and confirm restore *before* any destructive migration.

## AI Review Checklist

- Are domain invariants enforced by constraints, not just application code?
- Do all columns use precise types (`TIMESTAMPTZ`, `NUMERIC`, enums) rather than `VARCHAR`?
- Is every foreign key indexed on the referencing side?
- Does every `UPDATE`/`DELETE` have a verified, bounded `WHERE` clause?
- Are values parameterized rather than concatenated into the SQL string?
- Has the query been checked with `EXPLAIN` against realistic data volume?
- Is the migration reversible and non-locking on hot tables?

## Related

- `knowledge/sql/14-transactions.md`
- `knowledge/sql/15-indexes.md`
- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/22-security.md`
- `knowledge/sql/26-best-practices.md`
