---
id: backend/18-database-design
topic: backend
slug: database-design
title: "Database Design"
type: doc
order: 18
status: ready
tags: [backend, database-design]
related: [backend/17-transactions, backend/13-caching, backend/09-validation, backend/19-performance, backend/08-domain-modeling]
when_to_use: "Read before creating a schema, adding a migration, choosing keys and indexes, or modeling a new persistent entity."
---
# Database Design

## Purpose

This document defines how to model persistent data: schema, keys, constraints,
indexes, normalization, and migrations. It is written so an agent can design a table
or change a schema without creating data-integrity bugs, silent corruption, or a
migration that locks production.

The schema is the one part of a system that outlives every rewrite. Application code
can be replaced in a weekend; a bad schema is dragged along for years because data has
already been written into its shape. Design it as if it is permanent, because it nearly
is.

## Why It Matters

The database is the single source of truth. When application logic is wrong, one
request fails; when the schema lets bad data in, every future read is poisoned and no
code change can fully undo it. Constraints you omit today become application bugs,
support tickets, and reconciliation scripts tomorrow. Meanwhile the schema dictates
which queries are fast and which are impossible, so early modeling choices quietly cap
[performance](19-performance.md) and [scalability](20-scalability.md) long before you
hit them.

## Core Principles

- **Make illegal states unrepresentable in the schema, not just in code.** A `NOT NULL`,
  `UNIQUE`, `CHECK`, or foreign key is enforced for every writer forever; an application
  check protects only the code path that remembered it.
- **Normalize until it hurts, denormalize until it works.** Start at third normal form so
  each fact lives in exactly one place. Denormalize only for a measured read problem, and
  own the resulting duplication deliberately.
- **Every table has a primary key.** No exceptions. A table without one has no stable
  identity for rows and breaks replication, updates, and deduplication.
- **The database owns data integrity; the application owns business rules.** Uniqueness,
  referential integrity, and non-null are the database's job. "A refund cannot exceed the
  order total" may be too dynamic for a `CHECK` and belongs in a transaction.
- **Migrations are forward-only and reviewed like production code.** You never edit a
  shipped migration; you add a new one. Each must be safe to run against live data.

## Best Practices

- Use a surrogate primary key (`bigint` identity or UUIDv7) for internal identity, and add
  a separate `UNIQUE` constraint for natural keys (email, SKU). Prefer UUIDv7 over UUIDv4
  when you need client-generated, sortable keys; random UUIDs fragment index locality.
- Declare foreign keys with explicit `ON DELETE` behavior (`RESTRICT`, `CASCADE`, or
  `SET NULL`). The default is silence; pick the one that matches the domain.
- Choose the tightest correct type: `timestamptz` (never naive `timestamp`) for time,
  `numeric` (never `float`) for money, native `enum` or a `CHECK` for closed sets.
- Index for the queries you actually run: columns in `WHERE`, `JOIN`, and `ORDER BY`.
  Add a composite index in the order columns are filtered. Every index speeds reads and
  slows writes, so justify each one.
- Store timestamps in UTC; convert at the presentation edge, never in storage.
- Run migrations in the expand/contract pattern for zero-downtime: add the new column
  nullable, backfill in batches, switch reads, then drop the old column in a later deploy.
- Add `created_at` / `updated_at` to every business table; you will always eventually need
  them for debugging and auditing.

## Examples

**Good Example** — constraints enforce integrity at the source

```sql
CREATE TABLE orders (
  id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id  bigint NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
  status       text   NOT NULL CHECK (status IN ('pending','paid','shipped','cancelled')),
  total_cents  bigint NOT NULL CHECK (total_cents >= 0), -- money as integer cents, never float
  created_at   timestamptz NOT NULL DEFAULT now()        -- tz-aware, defaulted in the DB
);
-- Index the foreign key we join and filter on; unindexed FKs cause slow deletes + scans.
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
```

**Bad Example** — the schema trusts the application to behave

```sql
CREATE TABLE orders (
  id          varchar,        -- no PK: rows have no stable identity; UUIDv4 in a string is worse
  customer_id varchar,        -- no FK: can reference a customer that never existed
  status      varchar,        -- free text: 'Shipped', 'shipped', 'shiped' all coexist
  total       float,          -- float money: 0.1 + 0.2 != 0.3, cents drift over time
  created_at  timestamp       -- naive: ambiguous across time zones and DST
);
-- No indexes: every lookup by customer is a full table scan.
```

## Common Mistakes

- Storing money in `float`/`double`, causing rounding drift that never reconciles.
- Tables with no primary key, or a "natural" primary key (email) that later needs to change.
- Missing foreign keys, so orphaned rows accumulate and referential integrity is a myth.
- Storing local time or naive timestamps instead of `timestamptz` in UTC.
- Indexing everything (write amplification) or nothing (sequential scans) instead of the
  actual query set.
- `SELECT`-friendly denormalization added before any measurement, then left unmaintained
  until the copies disagree.
- Editing an already-applied migration instead of adding a new one, so environments diverge.

## Production Tips

- Test every migration against a production-sized copy; an `ALTER TABLE` that rewrites the
  table can lock it for minutes. Prefer additive, non-blocking changes.
- Add indexes concurrently (`CREATE INDEX CONCURRENTLY` in Postgres) to avoid locking writes.
- Set explicit `NOT NULL` and defaults when adding columns; a nullable column backfilled
  later is a two-step migration, not one.
- Keep a slow-query log and review `EXPLAIN (ANALYZE)` for the top queries before shipping.

## AI Review Checklist

- Does every table have a primary key and appropriate `NOT NULL` / `CHECK` constraints?
- Are foreign keys declared with an explicit `ON DELETE` action, and are they indexed?
- Is money stored as integer minor units or `numeric`, never as `float`?
- Are timestamps `timestamptz` stored in UTC?
- Do indexes match the real `WHERE` / `JOIN` / `ORDER BY` columns, with no unused indexes?
- Is the migration additive and safe to run online, and is it a new file (not an edit)?
- Is denormalization justified by a measured read need, with the duplication owned?

## Related

- `knowledge/backend/17-transactions.md`
- `knowledge/backend/13-caching.md`
- `knowledge/backend/09-validation.md`
- `knowledge/backend/19-performance.md`
- `knowledge/backend/08-domain-modeling.md`
