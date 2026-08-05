---
id: postgresql/03-data-types
topic: postgresql
slug: data-types
title: "PostgreSQL Data Types"
type: doc
order: 3
status: ready
tags: [postgresql, data-types]
related: [postgresql/04-indexes, postgresql/08-jsonb, postgresql/09-arrays, postgresql/22-migrations, postgresql/25-best-practices]
when_to_use: "Read before designing a table or choosing a column type in a migration."
---
# PostgreSQL Data Types

## Purpose

This document defines how to choose column types so that data is correct by
construction: temporal types, numeric precision, identifiers, text, enums, and the
semi-structured types. The type you pick is the schema's contract — it decides what
values are even representable, how they sort, how they index, and how much storage
and CPU each row costs. Choose the type that makes invalid data impossible.

## Why It Matters

The wrong type is a bug that hides until the data hits an edge. `timestamp` without
a time zone silently drops the offset, and a year later a daylight-saving boundary
shifts every reported time by an hour. `float` for money accumulates rounding error
that fails an audit. `text` for a status column lets a typo (`"acitve"`) slip past
every constraint. These are not performance issues — they are correctness issues
baked into the schema, and fixing a type on a large table means a rewrite migration
under load. The cheap moment to get it right is now.

## Core Principles

- **Store the domain, not a stringification of it.** A timestamp is `timestamptz`,
  money is `numeric`, a flag is `boolean` — not `text` you parse in the app.
- **Time is always zone-aware.** Use `timestamptz` and store UTC. `timestamp`
  (without zone) is almost always a bug.
- **Exact where exactness is required.** Use `numeric` for money and any value where
  rounding is unacceptable; `float`/`double` are for measurements, not currency.
- **Constrain the set of legal values.** Enums or `CHECK`/lookup tables prevent typos
  and document intent; `text` with no constraint accepts anything.
- **Right-size and let the database enforce it.** Prefer a narrow, checked type over
  a wide, permissive one; the database rejects bad rows the app forgot to validate.

## Best Practices

- Use `timestamptz` for all points in time; store and compute in UTC, format at the edge.
- Use `numeric(p, s)` for money and quantities requiring exact decimals; never `float`.
- Use `bigint` (or `int` only when a hard, small bound is certain) for counters and keys;
  `int` overflows at ~2.1 billion, and running out of key space is a painful migration.
- Prefer `uuid` (v7, time-ordered) or `bigint` identity for surrogate primary keys.
- Use native `enum` (or a FK to a lookup table) for small fixed value sets, not `text`.
- Use `text` freely for strings — `varchar(n)` gives no performance benefit; use a
  length only when the limit is a real business rule, enforced by `CHECK`.
- Reach for `jsonb` (see [jsonb](08-jsonb.md)) for genuinely dynamic data, not as an
  excuse to skip modeling known columns.
- Add `NOT NULL` wherever null is not a meaningful state; nulls silently break equality
  and aggregates.

## Examples

**Good Example** — precise types, constraints, zone-aware time

```sql
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'shipped', 'cancelled');

CREATE TABLE orders (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(), -- stable surrogate key
  customer_id  bigint NOT NULL REFERENCES customers(id),   -- won't overflow; enforced FK
  status       order_status NOT NULL DEFAULT 'pending',    -- typos are impossible
  total_cents  bigint NOT NULL CHECK (total_cents >= 0),   -- exact money as integer cents
  currency     char(3) NOT NULL CHECK (currency ~ '^[A-Z]{3}$'), -- ISO-4217, validated
  created_at   timestamptz NOT NULL DEFAULT now()          -- zone-aware, UTC
);
```

**Bad Example** — stringly-typed, imprecise, zone-naive

```sql
CREATE TABLE orders (
  id           serial PRIMARY KEY,          -- int serial overflows at ~2.1B rows
  customer_id  varchar(50),                 -- no FK, nullable: orphan/garbage rows
  status       varchar(20),                 -- "shpped" passes; no constrained set
  total        float,                       -- 0.1 + 0.2 != 0.3 → money drift, audit fail
  currency     text,                        -- "usd", "US$", "" all accepted
  created_at   timestamp DEFAULT now()      -- no zone: DST shifts break reporting
);
```

## Common Mistakes

- Using `timestamp` instead of `timestamptz`, losing the offset and breaking DST math.
- Storing money in `float`/`double`, accumulating rounding error.
- `varchar(n)` chosen for "performance" — it only adds a length check, no speedup.
- `serial`/`int` primary keys that overflow, forcing a disruptive `bigint` migration.
- Free-text status/type columns instead of enums or lookup FKs, allowing typos.
- Overusing `jsonb` for data that has a known, stable shape, losing constraints and indexes.
- Leaving columns nullable by default, so `NULL` silently corrupts joins and aggregates.

## Production Tips

- Adding a value to an `enum` is cheap (`ALTER TYPE ... ADD VALUE`) but cannot be
  removed or reordered easily — if the set churns, a lookup table is more flexible.
- Widening `int` to `bigint` on a large table rewrites every row and takes a long,
  lock-heavy migration; size keys as `bigint` from day one.
- Use `gen_random_uuid()` (built in via `pgcrypto`/core) rather than app-generated
  random keys so the default lives with the schema.

## AI Review Checklist

- Is every point in time a `timestamptz`, stored in UTC?
- Is money/exact-decimal stored as `numeric` or integer minor units, never `float`?
- Are primary keys `bigint` identity or `uuid`, not `serial`/`int`?
- Do fixed value sets use enums or lookup FKs instead of free `text`?
- Are `NOT NULL`, `CHECK`, `UNIQUE`, and foreign-key constraints present where they apply?
- Is `jsonb` reserved for genuinely dynamic data, with known fields modeled as columns?

## Related

- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/08-jsonb.md`
- `knowledge/postgresql/09-arrays.md`
- `knowledge/postgresql/22-migrations.md`
- `knowledge/postgresql/25-best-practices.md`
