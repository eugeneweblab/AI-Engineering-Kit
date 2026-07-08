---
id: databases/28-best-practices
topic: databases
slug: best-practices
title: "Best Practices"
type: doc
order: 28
status: ready
tags: [databases, best-practices]
related: [databases/00-overview, databases/23-data-integrity, databases/17-migrations, databases/09-transactions, databases/07-indexing]
when_to_use: "Read before designing, changing, or reviewing any database schema, query, or access path."
---
# Best Practices

## Purpose

This document distills the highest-leverage rules for working with databases into one place: the
practices that prevent data loss, corruption, downtime, and slow queries. It is a synthesis, not a
deep dive — each rule links to the topic that develops it. Use it as a pre-flight checklist when
you touch a schema, write a query, or run a migration.

The single most important idea: the database is the last line of defense for your data. Application
code is rewritten constantly; the data outlives it. So correctness and integrity belong *in* the
database, where they hold regardless of which service, script, or admin wrote the row.

## Why It Matters

Most database mistakes are cheap to prevent and expensive to fix. A missing constraint lets bad
data in for months before anyone notices; a missing index turns a fast page into a timeout under
load; an unsafe migration locks a table and takes production down at deploy time; an unbounded
`DELETE` corrupts data in one keystroke. None of these are exotic — they are the same handful of
errors, repeated. Codifying the defenses as habits is what separates a database that stays correct
and fast for years from one that slowly rots. The reasoning matters as much as the rule: an agent
that knows *why* a constraint exists won't drop it to make a test pass.

## Core Principles

- **Put integrity in the schema, not just the app.** Constraints (`NOT NULL`, `UNIQUE`, foreign
  keys, `CHECK`) are enforced for every writer, forever. App checks are enforced only by the code
  path that remembered them. See [data integrity](23-data-integrity.md).
- **Wrap multi-statement changes in transactions.** All-or-nothing is the default expectation of
  correct data. A partial change is a corrupt change. See [transactions](09-transactions.md).
- **Model for the queries you run.** Normalize by default for write correctness; denormalize
  deliberately, with a reason, for a proven read hotspot. See [data modeling](03-data-modeling.md).
- **Every query has a plan; know it for hot paths.** Index what you filter, join, and sort on;
  read the EXPLAIN. An unindexed scan is fine until the table grows. See [indexing](07-indexing.md).
- **Migrations are production changes.** They must be reversible, run without long locks, and be
  tested against realistic volume. See [migrations](17-migrations.md).

## Best Practices

- Declare constraints at the schema level: `NOT NULL` on required columns, `UNIQUE` on natural
  keys, foreign keys on every relationship, `CHECK` for invariants. Let the database reject bad data.
- Use explicit, typed columns — the narrowest correct type (`TIMESTAMPTZ` not `TEXT` for time,
  `NUMERIC` not `FLOAT` for money). Wrong types are silent corruption.
- Never run an unscoped `UPDATE`/`DELETE`. Require a `WHERE`, and preview the row count in a
  transaction before commit. See [testing](27-testing.md) for how to guard this in CI.
- Index selectively: cover the columns you filter and join on, prefer composite indexes ordered by
  selectivity, and remove unused indexes — every index taxes writes. See [indexing](07-indexing.md).
- Parameterize every query. String-concatenated SQL is an injection hole *and* defeats plan caching.
  See [security](19-security.md).
- Keep transactions short and consistent in lock order to avoid deadlocks; pick the isolation level
  deliberately. See [concurrency](10-concurrency.md).
- Make migrations additive and reversible: add columns/tables first, backfill in batches, switch
  reads, drop old objects last. Avoid table-rewriting `ALTER`s under load.
- Back up on a schedule and *test restores*. An untested backup is a hope, not a recovery plan.
  See [backup and recovery](18-backup-and-recovery.md).
- Monitor slow queries, connection saturation, replication lag, and error rates from day one.
  See [monitoring](21-monitoring.md).

## Examples

**Good Example** — integrity in the schema, safe scoped change in a transaction

```sql
CREATE TABLE orders (
  id          BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  customer_id BIGINT      NOT NULL REFERENCES customers(id),  -- relationship enforced by the DB
  status      TEXT        NOT NULL CHECK (status IN ('pending','paid','shipped')),
  total_cents BIGINT      NOT NULL CHECK (total_cents >= 0),  -- money as integer cents, never FLOAT
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX orders_customer_created ON orders (customer_id, created_at);  -- matches the hot query

BEGIN;
UPDATE orders SET status = 'shipped' WHERE id = :id AND status = 'paid';  -- scoped + guarded
-- verify exactly one row changed before COMMIT; otherwise ROLLBACK
COMMIT;
```

**Bad Example** — integrity in the app, unsafe query, wrong types

```sql
CREATE TABLE orders (
  id          TEXT,          -- no primary key, no identity
  customer_id TEXT,          -- no foreign key: orphan orders are allowed
  status      TEXT,          -- no CHECK: 'shpiped' typo persists forever
  total       FLOAT,         -- floating money: 0.1 + 0.2 rounding corrupts totals
  created_at  TEXT           -- time as text: unsortable, timezone-ambiguous
);
```
```ts
// String-built SQL: injection risk, and an unscoped update on a bug in `filter`.
await db.query(`UPDATE orders SET status='shipped' WHERE ${filter}`);
```

## Common Mistakes

- Enforcing rules only in application code, so any other writer bypasses them.
- Storing money as `FLOAT` or timestamps as `TEXT`, corrupting data silently.
- Running `UPDATE`/`DELETE` without a `WHERE`, or outside a transaction for multi-step changes.
- Adding indexes reactively without checking EXPLAIN, or never removing dead ones.
- Concatenating user input into SQL instead of parameterizing.
- Shipping a migration that rewrites or exclusively locks a large table at peak.
- Taking backups but never testing a restore, discovering the gap during an outage.

## AI Review Checklist

- Are integrity rules (`NOT NULL`, `UNIQUE`, foreign keys, `CHECK`) declared in the schema?
- Are types the narrowest correct choice, with money as integers and time as `TIMESTAMPTZ`?
- Are all multi-statement changes transactional, and are `UPDATE`/`DELETE` always scoped?
- Are hot-path queries indexed to match, and are unused indexes removed?
- Is every query parameterized rather than string-built?
- Is the migration additive, reversible, and free of long locks on large tables?
- Are backups scheduled and restores tested, with monitoring on slow queries and lag?

## Related

- `knowledge/databases/00-overview.md`
- `knowledge/databases/23-data-integrity.md`
- `knowledge/databases/17-migrations.md`
- `knowledge/databases/09-transactions.md`
- `knowledge/databases/07-indexing.md`
