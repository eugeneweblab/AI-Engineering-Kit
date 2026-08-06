---
id: postgresql/25-best-practices
topic: postgresql
slug: best-practices
title: "PostgreSQL Best Practices"
type: doc
order: 25
status: ready
tags: [postgresql, best-practices, invoice, numeric, timestamp, timestamptz, float, CHECK]
related: [postgresql/04-indexes, postgresql/06-transactions, postgresql/22-migrations, postgresql/16-performance, postgresql/100-common-antipatterns]
when_to_use: "Read before designing a schema, writing queries, or reviewing any PostgreSQL data-access code."
---
# PostgreSQL Best Practices

## Purpose

This document collects the default decisions that make PostgreSQL code correct, fast,
and safe to change: schema design, key choice, query shape, transaction scope, and
migration hygiene. It is the baseline an agent should follow unless a specific document
or measured requirement says otherwise.

These are defaults with reasons, not laws. Each rule states the trade-off so an agent can
tell when the rule applies and when a measured exception overrides it.

## Why It Matters

A database schema outlives the application that created it. Bad early choices — a
`float` for money, a natural key that later changes, an unbounded `text` column indexed
in full — become expensive to reverse once terabytes and dozens of services depend on
them. Getting the defaults right costs nothing up front and saves a migration under load
later. Postgres is also strict and honest: it will enforce exactly the constraints you
declare and no more, so correctness is a design choice you make deliberately.

## Core Principles

- **Model constraints in the database.** `NOT NULL`, `FOREIGN KEY`, `UNIQUE`, and `CHECK`
  are enforced regardless of which service writes. Application-only validation is
  eventually bypassed.
- **Pick types that match meaning.** The right type rejects impossible data for free:
  `timestamptz` for time, `numeric` for money, `uuid` for opaque ids, `jsonb` for
  documents.
- **Keep transactions short and single-purpose.** A transaction holds locks and an old
  snapshot for its entire life; long ones cause bloat and contention.
- **Let the query planner work; give it statistics, not hints.** Postgres has no query
  hints by design — the fix for a bad plan is better indexes and fresh `ANALYZE`.
- **Every migration must be reversible and online.** Schema changes run against live
  traffic; a lock or a rewrite that blocks writes is an outage.

## Best Practices

- Use `timestamptz`, never `timestamp`, for any point in time. `timestamp` silently
  drops the zone and produces wrong comparisons across DST and regions.
- Use `numeric` for money and any exact decimal. `float`/`double` cannot represent `0.10`
  and will lose cents.
- Prefer identity columns (`GENERATED ALWAYS AS IDENTITY`) or `uuid` over legacy `serial`.
  `serial` has surprising ownership and permission edge cases.
- Add `NOT NULL` and a sensible default to every column that logically requires a value;
  nullable columns force three-valued logic on every query that touches them.
- Always name and index foreign keys. Postgres does **not** auto-index the referencing
  column, so `ON DELETE`/joins do sequential scans without it.
- Select explicit columns, never `SELECT *`, in application code. `*` breaks when the
  schema changes and pulls wide/`TOAST` columns you did not need.
- Use parameterized queries exclusively. String-built SQL is an injection hole and defeats
  plan caching.
- Batch bulk writes with `COPY` or multi-row `INSERT`; row-by-row inserts pay per-round-trip
  and per-transaction overhead.
- Wrap multi-statement changes in an explicit transaction so partial failure rolls back
  cleanly.

## Examples

**Good Example** — types match meaning, constraints in the DB, FK indexed

```sql
CREATE TABLE invoice (
  id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id uuid        NOT NULL REFERENCES customer(id),
  amount      numeric(12,2) NOT NULL CHECK (amount >= 0), -- exact money, no negatives
  currency    char(3)     NOT NULL,
  status      text        NOT NULL DEFAULT 'pending',
  created_at  timestamptz NOT NULL DEFAULT now()          -- zone-aware, correct across DST
);

-- Postgres does not auto-index FKs; joins and cascades scan without this.
CREATE INDEX invoice_customer_id_idx ON invoice (customer_id);

-- Parameterized, explicit columns, short transaction.
-- $1 is bound by the driver — no injection, plan is reusable.
SELECT id, amount, status FROM invoice WHERE customer_id = $1 AND status = 'pending';
```

**Bad Example** — wrong types, no constraints, unindexed FK, injectable

```sql
CREATE TABLE invoice (
  id          serial PRIMARY KEY,       -- legacy; identity columns are preferred
  customer_id int,                      -- nullable FK-by-convention, not enforced
  amount      float,                    -- 19.99 cannot be stored exactly -> lost cents
  created_at  timestamp                 -- no zone -> wrong across regions/DST
);
-- no FK, no index on customer_id -> every join is a sequential scan

```

The query is then built by string concatenation — SQL injection, and no plan caching:

```ts
db.query("SELECT * FROM invoice WHERE customer_id = " + userInput);
```

## Common Mistakes

- Storing money in `float`/`double` and discovering rounding drift in reports.
- Using `timestamp` instead of `timestamptz`, then fighting timezone bugs forever.
- Declaring a foreign key but forgetting the index on the referencing column.
- `SELECT *` in application code, which breaks silently when a column is added or removed.
- Leaving columns nullable "just in case," forcing `IS NULL`/`COALESCE` everywhere.
- Long-running transactions (e.g. an open transaction across an HTTP call) that block
  vacuum and hold locks.

## Production Tips

- Enforce a review rule that every new foreign key ships with its index in the same
  migration.
- Add `CHECK` constraints for domain invariants (`amount >= 0`, valid status values) so
  bad data cannot enter from any client, including ad-hoc SQL.
- Set a conservative `statement_timeout` and `idle_in_transaction_session_timeout` so a
  stuck client cannot hold locks indefinitely.

## AI Review Checklist

- Is money `numeric` and time `timestamptz` (never `float`/`timestamp`)?
- Does every foreign key have both the constraint and an index on the referencing column?
- Are `NOT NULL`, `UNIQUE`, and `CHECK` used to enforce invariants in the database?
- Are queries parameterized and selecting explicit columns rather than `*`?
- Are transactions short, single-purpose, and free of external calls while open?
- Is the migration online (no long lock or table rewrite) and reversible?

## Related

- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/06-transactions.md`
- `knowledge/postgresql/22-migrations.md`
- `knowledge/postgresql/16-performance.md`
- `knowledge/postgresql/100-common-antipatterns.md`
