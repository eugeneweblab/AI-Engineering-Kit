---
id: mysql/24-json
topic: mysql
slug: json
title: "JSON"
type: doc
order: 24
status: ready
tags: [mysql, json]
related: [mysql/03-data-types, mysql/04-indexes, mysql/05-query-optimization, mysql/23-full-text-search]
when_to_use: "Read before storing, indexing, or querying JSON columns, or when tempted to model relational data as a JSON blob."
---
# JSON

## Purpose

This document defines how to use MySQL's native `JSON` type correctly: when a JSON
column is the right tool, how to query and index it, and where it silently costs you
performance or correctness. It targets MySQL 8.0+, where the binary `JSON` type,
functional indexes, and multi-valued indexes are available.

JSON is for *semi-structured, read-mostly* data whose shape varies per row. It is not a
substitute for normalized tables — see [data types](03-data-types.md). Reach for it when
a proper column would be wrong, not when modeling is inconvenient.

## Why It Matters

MySQL stores `JSON` in an optimized binary format, so reads do not re-parse text — but
every write rewrites the whole document, and a value buried in JSON cannot use an
ordinary B-tree index. Teams that dump business-critical fields (status, foreign keys,
prices) into a JSON blob discover too late that they cannot index, constrain, join, or
cheaply update them. The data looks flexible and works in development; at scale it forces
full-table scans and makes migrations nearly impossible. Choosing JSON is an
architectural decision, not a formatting one.

## Core Principles

- **Normalize first; JSON is the exception.** If a field is queried, filtered, joined,
  or constrained, it belongs in its own column. JSON is for attributes you store and
  return whole.
- **Use the `JSON` type, never `TEXT`.** `JSON` validates on insert, stores a parsed
  binary form, and enables the JSON functions. `TEXT` gives you none of that.
- **JSON columns cannot be indexed directly.** Index a *generated column* or a
  *multi-valued index* over an extracted path — nothing else is indexable.
- **Extraction is a scan by default.** `WHERE data->>'$.x' = ?` reads every row unless a
  matching functional/generated-column index exists.
- **Whole-document rewrites are the write cost.** Updating one key rewrites the entire
  value and its indexes; keep hot-updated fields out of large documents.

## Best Practices

- Use the `->>` operator (unquoting extract, shorthand for `JSON_UNQUOTE(JSON_EXTRACT())`)
  for scalar reads; use `->` only when you need the JSON-typed result.
- Index a queried path with a **generated column** (`STORED` or `VIRTUAL`) plus a normal
  index, or a **functional index** `((CAST(data->>'$.x' AS CHAR(32))))`. Always `CAST`
  to a bounded, deterministic type so the index is usable.
- For arrays you filter with `MEMBER OF` / `JSON_CONTAINS`, use a **multi-valued index**
  — the only index type that spans array elements.
- Validate structure with `JSON_SCHEMA_VALID()` in a `CHECK` constraint when the shape
  is meant to be stable. Loose JSON drifts silently.
- Modify in place with `JSON_SET`, `JSON_REPLACE`, `JSON_REMOVE`, `JSON_ARRAY_APPEND`
  rather than reading, mutating in the app, and writing the whole document back — it
  avoids a race and is often cheaper.
- Keep documents small (kilobytes, not megabytes). Large documents inflate every read
  and rewrite; move big payloads to object storage and keep a reference.

## Examples

**Good Example** — indexed generated column over a queried JSON path

```sql
CREATE TABLE orders (
  id       BIGINT PRIMARY KEY,
  -- Truly variable, read-whole attributes live in JSON:
  metadata JSON NOT NULL,
  -- The status is queried constantly, so it is promoted to an indexable column.
  -- STORED generated column is materialized once and indexed like any column.
  status   VARCHAR(20)
             AS (metadata->>'$.status') STORED,
  INDEX idx_status (status)
);

-- Uses idx_status, not a full scan, because status is a real indexed column:
SELECT id FROM orders WHERE status = 'shipped';

-- In-place update: rewrites only via the engine, no read-modify-write race:
UPDATE orders SET metadata = JSON_SET(metadata, '$.status', 'delivered') WHERE id = 42;
```

**Bad Example** — relational data hidden in JSON, unindexable filter

```sql
CREATE TABLE orders (
  id   BIGINT PRIMARY KEY,
  data JSON NOT NULL      -- customer_id, status, total all buried here
);

-- Full-table scan on every request: the extracted path has no index, and
-- MySQL must parse and extract '$.status' from every row before comparing.
SELECT id FROM orders WHERE data->>'$.status' = 'shipped';

-- Read-modify-write in the app: two concurrent updates lose one change.
-- (app SELECTs data, edits JSON in memory, writes it back)
```

## Common Mistakes

- Storing foreign keys, statuses, or money in JSON, then being unable to index, join, or
  add a `CHECK`/`FOREIGN KEY` constraint to them.
- Using `TEXT`/`VARCHAR` to hold JSON, losing validation and the binary storage benefit.
- Expecting `WHERE data->>'$.x' = ?` to use an index — it scans unless a generated or
  functional index exists for exactly that expression and type.
- Filtering array membership with `JSON_CONTAINS` but no multi-valued index, forcing a
  scan on every row.
- Read-modify-write of the whole document in application code, creating lost-update races
  instead of using `JSON_SET`.
- Growing documents without bound, so a single hot row rewrites megabytes per update.

## Production Tips

- Confirm index use with `EXPLAIN`: a JSON filter that shows `type: ALL` is scanning —
  add the generated column or functional index. See [query optimization](05-query-optimization.md).
- Prefer `VIRTUAL` generated columns when you only need the index (no extra storage);
  use `STORED` when the value is read far more than written.
- If you need full-text search inside JSON text, extract the field to a column and add a
  `FULLTEXT` index — see [full-text search](23-full-text-search.md); JSON has no
  full-text index of its own.

## AI Review Checklist

- Is any field that is filtered, joined, or constrained still trapped inside JSON instead
  of being a column?
- Is the column typed `JSON`, not `TEXT`/`VARCHAR`?
- Does every JSON path used in a `WHERE`/`ORDER BY` have a backing generated or functional
  index, with an explicit `CAST` to a bounded type?
- Are array-membership filters backed by a multi-valued index?
- Are updates done with `JSON_SET`/`JSON_REPLACE` rather than app-side read-modify-write?
- Is there a `JSON_SCHEMA_VALID` `CHECK` where the document shape is meant to be stable?

## Related

- `knowledge/mysql/03-data-types.md`
- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/23-full-text-search.md`
