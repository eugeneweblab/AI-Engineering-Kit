---
id: databases/06-schema-design
topic: databases
slug: schema-design
title: "Schema Design"
type: doc
order: 6
status: ready
tags: [databases, schema-design, VARCHAR, CHECK, TIMESTAMPTZ, DOUBLE, BIGINT]
related: [databases/04-normalization, databases/05-denormalization, databases/23-data-integrity, databases/07-indexing, databases/17-migrations]
when_to_use: "Read before creating a new table, adding a column, or reviewing a migration that changes structure."
---
# Schema Design

## Purpose

This document defines how to turn a data model into concrete, physical table
definitions: column types, keys, constraints, nullability, and defaults. It is
written so an agent can author a schema — or review a migration — that stays
correct as data grows and requirements change.

Schema design sits between abstract [data modeling](03-data-modeling.md) and
physical concerns like [indexing](07-indexing.md). The model decides *what*
entities exist; the schema decides *how* the database enforces their rules.

## Why It Matters

The schema is the last line of defense for data correctness. Application code has
bugs, ships in many versions, and connects from many services — but every write
passes through the same table definition. A constraint declared in the schema
holds for all of them, forever, including the ad-hoc `UPDATE` someone runs at 2am.
A rule left to the application is a rule that will eventually be violated.

Schema mistakes are also the most expensive to fix. Changing a column type or
adding a `NOT NULL` on a billion-row table means a migration, a backfill, and
often downtime. Getting the shape right before data accumulates costs minutes;
fixing it after costs a planned outage.

## Core Principles

- **Push invariants into the schema.** If a value must be unique, non-null,
  positive, or reference another row, declare that with a constraint. The database
  enforces it under all concurrency; application checks race and drift.
- **Every table has a primary key.** No exceptions. A table without one has no
  stable row identity, breaks replication tooling, and cannot be safely updated.
- **Choose the narrowest correct type.** Type is documentation the engine enforces.
  A date is not a string; money is not a float; an enum is not free text.
- **Model nullability deliberately.** `NULL` means "unknown/absent" and has
  three-valued logic that surprises everyone. Make a column `NOT NULL` with a
  default unless absence is a real, distinct state.
- **Design for change.** Additive changes (new nullable column, new table) are
  cheap and online; destructive changes (drop, retype, add `NOT NULL`) are not.

## Best Practices

- Use a surrogate primary key (`BIGINT` identity or UUIDv7) for internal identity,
  and add a separate `UNIQUE` constraint on any natural key. This keeps foreign
  keys stable when business identifiers change.
- Prefer `BIGINT` over `INT` for keys on any table that could exceed ~2 billion
  rows over its lifetime — retyping a live PK is a major operation.
- Store money as `NUMERIC(precision, scale)`, never `FLOAT`/`DOUBLE`. Binary
  floating point cannot represent `0.10` exactly and silently loses cents.
- Store timestamps as `TIMESTAMPTZ` (UTC), not `TIMESTAMP` or local time. Convert
  to the user's zone at the edge, never in storage.
- Add `FOREIGN KEY` constraints with an explicit `ON DELETE` action. Orphaned rows
  are a class of bug the database can prevent for free.
- Use `CHECK` constraints for domain rules (`price >= 0`, `status IN (...)`) and a
  database `ENUM` or lookup table for closed value sets.
- Give every table `created_at` and `updated_at` (`TIMESTAMPTZ NOT NULL DEFAULT now()`).
  You will need them, and backfilling them later is guesswork.
- Name things consistently: `snake_case`, singular or plural but not both, foreign
  keys as `<referenced_table>_id`. Consistency lets tooling and humans predict names.

## Examples

**Good Example** — types enforce meaning, constraints enforce rules

```sql
CREATE TABLE orders (
  id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- stable surrogate key
  public_id    UUID        NOT NULL DEFAULT gen_random_uuid(),   -- exposed to clients
  customer_id  BIGINT      NOT NULL REFERENCES customers(id)     -- FK prevents orphans
                            ON DELETE RESTRICT,
  status       TEXT        NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending','paid','shipped','cancelled')),
  total_cents  BIGINT      NOT NULL CHECK (total_cents >= 0),    -- integer cents, never float
  currency     CHAR(3)     NOT NULL,                             -- ISO 4217, fixed width
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (public_id)                                             -- natural key kept separate from PK
);
```

**Bad Example** — the schema enforces almost nothing

```sql
CREATE TABLE orders (
  id          INT,                 -- no PK: no row identity; INT will overflow
  customer    VARCHAR(255),        -- FK relationship exists only in the app's head
  status      VARCHAR(255),        -- any string is "valid"; typos become data
  total       FLOAT,               -- money in binary float: rounding errors accrue
  currency    VARCHAR(255),        -- unbounded width for a 3-char code
  created_at  VARCHAR(255)         -- a timestamp stored as text: unsortable, unvalidated
);
```

## Common Mistakes

- No primary key, or a mutable natural key as the primary key.
- `VARCHAR(255)` as a default for everything, encoding no real constraint.
- Money in `FLOAT`/`DOUBLE`; timestamps in local time or as strings.
- Missing `FOREIGN KEY` constraints, leaving referential integrity to the app.
- Nullable columns everywhere because it was easier than choosing a default.
- Storing status/type as free text instead of a `CHECK` list or lookup table.
- Overloading one column with a delimited blob (CSV in a string) instead of rows.

## Production Tips

- Every structural change ships as a reviewed [migration](17-migrations.md), never a
  manual `ALTER` in production. The schema history is the source of truth.
- Adding `NOT NULL` to a populated column is two steps: add the constraint as
  `NOT VALID`, backfill, then `VALIDATE` — avoids a full-table lock.
- Set an explicit default before adding `NOT NULL` so in-flight writes don't fail.

## AI Review Checklist

- Does every table have a primary key, and is it a stable (non-mutable) value?
- Is money stored as integer cents or `NUMERIC`, never a float?
- Are timestamps `TIMESTAMPTZ` in UTC, not strings or local time?
- Does every reference have a `FOREIGN KEY` with an explicit `ON DELETE` action?
- Are closed value sets enforced by `CHECK`/enum/lookup, not free text?
- Is each column's nullability deliberate, with defaults where absence is not meaningful?
- Is the change additive/online, or does it need a phased [migration](17-migrations.md)?

## Related

- `knowledge/databases/04-normalization.md`
- `knowledge/databases/05-denormalization.md`
- `knowledge/databases/23-data-integrity.md`
- `knowledge/databases/07-indexing.md`
- `knowledge/databases/17-migrations.md`
