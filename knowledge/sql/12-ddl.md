---
id: sql/12-ddl
topic: sql
slug: ddl
title: "DDL"
type: doc
order: 12
status: ready
tags: [sql, ddl, CHECK, timestamptz, numeric, float, varchar, UNIQUE]
related: [sql/11-data-types, sql/13-dml, sql/15-indexes, sql/14-transactions, sql/100-common-antipatterns]
when_to_use: "Read before writing any CREATE, ALTER, or DROP that changes a schema, or any migration."
---
# DDL

## Purpose

This document defines how to shape schema with Data Definition Language: `CREATE`,
`ALTER`, and `DROP` on tables, columns, constraints, and types. It is written so an
agent can design or migrate a schema without silently corrupting data, dropping a
column that still has readers, or taking a lock that stalls production.

DDL declares the *rules the data must obey*. Get the constraints right here and the
database enforces correctness for you; get them wrong and every downstream query
inherits ambiguity that application code can never fully repair.

## Why It Matters

Schema is the most expensive thing to change after launch. A missing `NOT NULL` or
`FOREIGN KEY` lets bad rows accumulate for months before anyone notices, and by then
you cannot add the constraint without a cleanup project. Worse, DDL is not free at
runtime: an unguarded `ALTER TABLE` can take an `ACCESS EXCLUSIVE` lock and block
every read and write on a hot table until it completes. The blast radius of a bad
migration is the whole application, not one request.

## Core Principles

- **Constraints are correctness, not decoration.** Encode every invariant you can
  (`NOT NULL`, `UNIQUE`, `CHECK`, `FOREIGN KEY`) so the database rejects bad data.
  Application-only validation always leaks.
- **Every table has an explicit primary key.** No key means no stable row identity,
  no safe replication, and duplicate rows you cannot dedupe.
- **DDL is versioned, forward-only migrations — never hand-edited.** Each change is a
  reviewed, ordered file that runs identically in every environment.
- **Migrations must be safe to run against live traffic.** Assume the old and new
  application versions run simultaneously during a deploy.
- **Choose the narrowest correct type.** The type is a constraint too (see
  [data types](11-data-types.md)); `text` where you meant `timestamptz` invites bad data.

## Best Practices

- Add `NOT NULL` and a sensible default to every column that should always have a
  value. Nullable-by-default columns push three-valued logic into every query.
- Name constraints explicitly (`CONSTRAINT orders_total_positive CHECK (...)`) so
  errors are readable and migrations can drop them by name.
- Add new columns as nullable or with a constant default, then backfill, then add
  `NOT NULL` in a later step — a single `NOT NULL DEFAULT` on a huge table can rewrite it.
- Create indexes concurrently (`CREATE INDEX CONCURRENTLY` in PostgreSQL) so index
  builds do not lock writes; the cost is that it cannot run inside a transaction.
- Expand-then-contract for renames: add the new column, dual-write, migrate readers,
  drop the old column in a separate release. Never rename a column in one shot.
- Use `timestamptz` (not `timestamp`) for all points in time, and store UTC.
- Set `ON DELETE` behavior explicitly on every foreign key (`RESTRICT`, `CASCADE`, or
  `SET NULL`) so referential cleanup is a decision, not an accident.

## Examples

**Good Example** — explicit keys, constraints, and safe types

```sql
CREATE TABLE orders (
  id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- stable identity
  customer_id  bigint NOT NULL REFERENCES customers (id)
                 ON DELETE RESTRICT,                             -- referential rule is explicit
  status       text NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending','paid','shipped')), -- invalid states impossible
  total_cents  integer NOT NULL CHECK (total_cents >= 0),        -- money as integer, never float
  created_at   timestamptz NOT NULL DEFAULT now()                -- UTC instant, not naive timestamp
);
```

**Bad Example** — no key, no constraints, lossy types

```sql
CREATE TABLE orders (
  customer_id  int,            -- nullable FK-in-name-only: nothing enforces it
  status       varchar(255),   -- any string allowed; typos become silent data corruption
  total        float,          -- floating point money rounds and drifts
  created_at   timestamp       -- no zone: ambiguous instant across regions
);
-- No primary key: duplicate rows are now possible and undedupable.
```

## Common Mistakes

- Tables with no primary key, so rows have no identity and replication breaks.
- `ALTER TABLE ... ADD COLUMN ... NOT NULL DEFAULT <expr>` on a large table, forcing a
  full rewrite under an exclusive lock.
- Renaming or dropping a column in the same release that still has live readers.
- Storing money as `float`/`double` instead of `integer` cents or `numeric`.
- Foreign keys with no explicit `ON DELETE`, leaving orphan rows or surprise cascades.
- Using `varchar(n)` as validation; it caps length but permits any garbage under it.
- Editing schema directly in production instead of through a reviewed migration.

## Production Tips

- Set a short `lock_timeout` (and `statement_timeout`) before DDL so a migration that
  cannot get its lock fails fast instead of queueing behind it and blocking all traffic.
- Split every migration into "expand" (add, backfill) and "contract" (drop) phases
  deployed separately, so a rollback never strands the running app.
- Test migrations against a production-sized copy; lock and rewrite behavior is
  invisible at ten rows and catastrophic at ten million.

## AI Review Checklist

- Does every table have an explicit primary key?
- Are invariants encoded as `NOT NULL`, `CHECK`, `UNIQUE`, and `FOREIGN KEY`?
- Does every foreign key set `ON DELETE` behavior explicitly?
- Will this `ALTER` avoid a full table rewrite or a long exclusive lock on a hot table?
- Are new columns added nullable/defaulted first, then backfilled, then constrained?
- Are indexes built concurrently on live tables?
- Are timestamps `timestamptz` in UTC and money an integer/`numeric`, not `float`?

## Related

- `knowledge/sql/11-data-types.md`
- `knowledge/sql/13-dml.md`
- `knowledge/sql/15-indexes.md`
- `knowledge/sql/14-transactions.md`
- `knowledge/sql/100-common-antipatterns.md`
