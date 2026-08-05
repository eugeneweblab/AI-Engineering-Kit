---
id: sql/11-data-types
topic: sql
slug: data-types
title: "SQL Data Types"
type: doc
order: 11
status: ready
tags: [sql, data-types]
related: [sql/12-ddl, sql/10-functions, sql/09-aggregate-functions, sql/15-indexes, sql/27-portability]
when_to_use: "Read before choosing a column type in a CREATE TABLE, or when money, dates, JSON, or text encoding are involved."
---
# SQL Data Types

## Purpose

This document defines how to choose column data types — numeric, exact-decimal, string,
temporal, boolean, UUID, JSON, and array/enum types — in a schema. Type choice is made
once in [DDL](12-ddl.md) and is expensive to change later, so it is one of the
highest-leverage decisions in a database.

The right type enforces correctness (a `DATE` cannot hold "banana"), saves storage and
memory, keeps indexes small and fast, and prevents whole classes of bugs — floating-point
money, timezone drift, truncated text — before they can occur.

## Why It Matters

The wrong type is a bug that lives in the schema and infects every query forever.
`FLOAT` for money guarantees rounding errors that fail an accountant's reconciliation.
`TIMESTAMP` without a timezone loses information the moment two regions write to it.
`VARCHAR(255)` "just in case" is arbitrary and permits invalid data. Because changing a
column type on a large, live table often means a full rewrite and lock, these mistakes are
costly to reverse — the cheapest place to be correct is at `CREATE TABLE`.

## Core Principles

- **Money is `NUMERIC`/`DECIMAL`, never `FLOAT`/`REAL`.** Binary floating point cannot
  represent 0.10 exactly; sums drift. Use `NUMERIC(p, s)` for exact decimal arithmetic.
- **Timestamps are `TIMESTAMPTZ` (store UTC).** A bare `TIMESTAMP` has no timezone and is
  ambiguous across regions and DST. Store instants in UTC; convert on display.
- **Pick the narrowest type that fits the domain.** `INT` vs `BIGINT`, `SMALLINT` for small
  enumerations — narrower columns mean smaller rows, smaller indexes, more cache hits.
- **Constrain length only for a real business rule, not a guess.** In PostgreSQL, `TEXT`
  and `VARCHAR(n)` have identical performance; use `TEXT` unless a limit is meaningful.
- **Use the type that carries semantics.** `BOOLEAN` not `INT(0/1)`, `UUID` not `CHAR(36)`,
  `ENUM`/lookup table not free-text status — the type enforces the invariant for you.

## Best Practices

- Use `NUMERIC(19, 4)` (or your currency's scale) for monetary amounts; keep the scale
  consistent across the schema so joins and sums do not silently re-round.
- Default new surrogate keys to `BIGINT` identity or `UUID`; a busy table outgrows `INT`
  (~2.1B) and migrating a key type mid-life is painful.
- Choose `UUID` (native type, 16 bytes) over storing UUIDs as `CHAR(36)` text — half the
  size and faster comparisons/indexes.
- Store enumerations as a small `ENUM` or a foreign-keyed lookup table, not free text, so
  invalid states are unrepresentable.
- Prefer `JSONB` over `JSON` (PostgreSQL) when you will query into the document — `JSONB`
  is indexable (GIN); reserve `JSON` for opaque blobs you only read whole.
- Set `NOT NULL` and a sensible `DEFAULT` at column definition time; a nullable column is a
  promise to handle `NULL` in every query.
- Fix text encoding to `UTF-8` and be explicit about collation for sort/compare rules.

## Examples

**Good Example** — exact money, UTC timestamp, semantic types, right widths

```sql
CREATE TABLE invoices (
    id           BIGINT      GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- room to grow
    customer_id  UUID        NOT NULL,                                 -- native, 16 bytes
    amount       NUMERIC(19,4) NOT NULL,          -- exact decimal money, no float drift
    currency     CHAR(3)     NOT NULL,            -- fixed-width ISO 4217 code
    status       invoice_status NOT NULL DEFAULT 'open', -- ENUM: invalid states impossible
    metadata     JSONB,                            -- queryable, GIN-indexable
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()      -- UTC instant, timezone-aware
);
```

**Bad Example** — float money, naive timestamp, stringly-typed everything

```sql
CREATE TABLE invoices (
    id          INT,                 -- overflows at ~2.1B rows; also nullable, no PK
    customer_id CHAR(36),            -- UUID as text: double the bytes, slower index
    amount      FLOAT,               -- money in binary float → guaranteed rounding errors
    status      VARCHAR(255),        -- free text: 'open', 'Open', 'opne' all allowed
    metadata    TEXT,                -- JSON as text: cannot index or query into it
    created_at  TIMESTAMP            -- no timezone → ambiguous across regions and DST
);
```

## Common Mistakes

- `FLOAT`/`REAL`/`DOUBLE` for money, producing rounding errors that fail reconciliation.
- `TIMESTAMP` instead of `TIMESTAMPTZ`, losing timezone and breaking at DST boundaries.
- `INT` primary keys on tables that will exceed ~2.1 billion rows.
- Storing UUIDs, JSON, or booleans as generic `TEXT`/`VARCHAR`, losing validation and
  indexability.
- Arbitrary `VARCHAR(255)` limits that reflect no real rule and truncate valid data.
- Nullable columns where the value is always required, forcing `NULL` checks everywhere.
- Mismatched numeric scales across joined columns, causing implicit re-rounding.

## Production Tips

- Changing a column type on a large table can rewrite and lock it; plan such migrations
  with a backfill + swap strategy, not an in-place `ALTER` on a hot table.
- Match join-key types exactly (both `BIGINT`, both `UUID`) — a type mismatch forces an
  implicit cast that can disable index use.
- Prefer native `UUID`/`INET`/`JSONB` types over emulating them in text; the engine
  optimizes and validates them for you.

## AI Review Checklist

- Is every monetary column `NUMERIC`/`DECIMAL` with a consistent scale, never a float?
- Are timestamps `TIMESTAMPTZ` storing UTC, not naive `TIMESTAMP`?
- Are surrogate keys `BIGINT` or `UUID` with headroom, and do join keys match types exactly?
- Are UUID, boolean, JSON, and enum values stored as their native/semantic types?
- Are length limits justified by a real rule, and are `NOT NULL`/`DEFAULT` set where apt?
- Is queryable JSON stored as `JSONB` (indexable) rather than `TEXT`?

## Related

- `knowledge/sql/12-ddl.md`
- `knowledge/sql/10-functions.md`
- `knowledge/sql/09-aggregate-functions.md`
- `knowledge/sql/15-indexes.md`
- `knowledge/sql/27-portability.md`
