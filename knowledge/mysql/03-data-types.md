---
id: mysql/03-data-types
topic: mysql
slug: data-types
title: "MySQL Data Types"
type: doc
order: 3
status: ready
tags: [mysql, data-types]
related: [mysql/04-indexes, mysql/00-overview, mysql/24-json, mysql/16-migrations, mysql/05-query-optimization]
when_to_use: "Read before designing a table schema or choosing a column type."
---
# MySQL Data Types

## Purpose

This document defines how to pick MySQL column types: which type fits which kind of value,
and why the choice matters beyond "it stores the data". The narrowest correct type is a
correctness and performance decision, not a cosmetic one.

## Why It Matters

Column types are the schema's type system — they decide what values are even representable,
and MySQL's strict mode will reject the rest. They also drive size: every index on a column
carries that column's width, so an oversized type multiplies through the buffer pool and
inflates memory and disk for the life of the table. Worst of all, some choices are actively
wrong for the data: `FLOAT` for money produces rounding errors, and 3-byte `utf8` silently
drops emoji. These mistakes are cheap to avoid at `CREATE TABLE` time and expensive to fix
once billions of rows exist.

## Core Principles

- **Pick the narrowest type that holds every valid value.** Narrower columns pack more rows per
  page, so more of the working set fits in the buffer pool. The cost of "just use BIGINT
  everywhere" is wasted memory on every read.
- **Never store money or exact decimals in `FLOAT`/`DOUBLE`.** Binary floating point cannot
  represent 0.10 exactly; sums drift. Use `DECIMAL` or integer minor units (cents).
- **Use the type that matches the value's meaning.** Dates in `DATETIME`/`DATE`, not strings;
  booleans in `TINYINT(1)`/`BOOL`; enumerations in `ENUM` or a lookup table — so the database
  can validate, compare, and index them.
- **`utf8mb4` is the only correct UTF-8.** MySQL's `utf8` is a 3-byte legacy alias that cannot
  store 4-byte characters. Always use `utf8mb4`.

## Best Practices

- Integers: use `UNSIGNED` for values that are never negative (IDs, counts) to double the
  positive range. Size to the domain: `TINYINT`, `INT`, or `BIGINT` for surrogate keys.
- Strings: use `VARCHAR(n)` with a realistic `n`, not `VARCHAR(255)` by reflex. Use `CHAR(n)`
  only for genuinely fixed-width values (country codes, hashes). Use `TEXT` for large blobs of
  prose, knowing it is stored off-page and can't be fully indexed.
- Money: `DECIMAL(13,2)` or an integer count of the minor unit (`total_cents INT UNSIGNED`).
- Time: `DATETIME` for wall-clock timestamps you control; `TIMESTAMP` when you want automatic
  UTC conversion, but note its 2038 range limit. Store UTC and convert in the application.
- Enumerations: `ENUM('a','b','c')` for a small, stable set — it validates and stores compactly.
  For a set that grows or needs metadata, use a lookup table with a foreign key instead.
- Booleans: `BOOL` (an alias for `TINYINT(1)`), constrained to 0/1.
- JSON: use the native `JSON` type for genuinely schemaless data; do not use it to avoid
  modeling structured, queried fields. See [json](24-json.md).
- Always declare `NOT NULL` unless the column has a real "unknown" state; `NULL` complicates
  comparisons, indexes, and aggregates.

## Examples

**Good Example** — types match meaning and range

```sql
CREATE TABLE payments (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,   -- surrogate key, never negative
  user_id      BIGINT UNSIGNED NOT NULL,
  amount_cents INT UNSIGNED    NOT NULL,   -- money as integer minor units: exact
  currency     CHAR(3)         NOT NULL,   -- fixed-width ISO 4217 code
  method       ENUM('card','bank','wallet') NOT NULL,     -- validated, compact
  note         VARCHAR(280)    NULL,       -- realistic length, nullable "unknown"
  paid_at      DATETIME        NOT NULL,   -- real timestamp, comparable and indexable
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Bad Example** — wrong and oversized types

```sql
CREATE TABLE payments (
  id       VARCHAR(255),        -- key as string: bloats every index, slow joins
  user_id  INT,                 -- signed, and too narrow for a large user table
  amount   FLOAT,               -- money in binary float: sums drift by cents
  currency VARCHAR(255),        -- 3 chars in a 255-wide column, any string "valid"
  method   VARCHAR(50),         -- typos like 'crad' pass silently; no validation
  paid_at  VARCHAR(30)          -- date as text: can't range-query or index by time
) CHARSET=utf8;                  -- 3-byte utf8: drops emoji in notes
```

## Common Mistakes

- Storing money in `FLOAT`/`DOUBLE`, accumulating rounding errors on totals.
- Reflexively using `VARCHAR(255)` for every string, inflating index and temp-table size.
- Storing dates or numbers as strings, which defeats range queries, sorting, and indexing.
- Using `utf8` instead of `utf8mb4`, silently truncating 4-byte characters.
- Making surrogate keys `VARCHAR`/`UUID-as-string`, bloating the clustered index and every FK.
- Overusing `NULL`, complicating `WHERE`, `UNIQUE`, and aggregate behavior.
- Using signed integers for IDs and counts, halving the usable range for no reason.

## Production Tips

- Changing a column type on a large table rewrites it and can lock or take hours; get the type
  right at creation. When you must change it, use an online-DDL tool. See [migrations](16-migrations.md).
- Prefer `BIGINT UNSIGNED AUTO_INCREMENT` surrogate keys for high-write tables; if you need
  UUIDs, store them as `BINARY(16)`, not `CHAR(36)`, to keep the index compact.

## AI Review Checklist

- Is money stored as `DECIMAL` or integer minor units, never `FLOAT`/`DOUBLE`?
- Are dates, times, and numbers stored in their native types, not `VARCHAR`?
- Is every text column `utf8mb4`, and is `VARCHAR(n)` sized to a realistic length?
- Are IDs and counts `UNSIGNED` and sized to their domain?
- Are surrogate keys integers (or `BINARY(16)` UUIDs), not `CHAR(36)` strings?
- Is `NOT NULL` the default, with `NULL` reserved for a real "unknown" state?
- Are small stable value sets `ENUM` or a lookup table, not free-text `VARCHAR`?

## Related

- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/00-overview.md`
- `knowledge/mysql/24-json.md`
- `knowledge/mysql/16-migrations.md`
- `knowledge/mysql/05-query-optimization.md`
