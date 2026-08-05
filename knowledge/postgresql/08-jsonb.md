---
id: postgresql/08-jsonb
topic: postgresql
slug: jsonb
title: "JSONB"
type: doc
order: 8
status: ready
tags: [postgresql, jsonb, CHECK, GIN, EXPLAIN]
related: [postgresql/03-data-types, postgresql/04-indexes, postgresql/09-arrays, postgresql/05-query-planner]
when_to_use: "Read before adding a JSONB column, querying inside JSON, or deciding whether data belongs in JSONB or in real columns."
---
# JSONB

## Purpose

This document defines when to use PostgreSQL's `jsonb` type, how to query and index it,
and where JSONB is the wrong tool. It is written so an agent can model semi-structured data
without turning a relational database into a slow, unqueryable document store.

`jsonb` stores JSON in a decomposed binary form: parsing happens on write, so reads and
operators are fast and it supports indexing. Its sibling `json` stores raw text, preserves
key order and duplicates, and cannot be indexed for containment — default to `jsonb`
unless you specifically need to round-trip the exact source text.

## Why It Matters

JSONB is the most misused feature in PostgreSQL. It is genuinely powerful for data whose
shape varies or is unknown ahead of time — but it is seductive as a way to "avoid
migrations", and teams end up storing structured, relational data as opaque blobs. The
cost is invisible at first and severe later: you cannot add a foreign key into a JSON
field, `NOT NULL` and `CHECK` constraints do not reach inside it, every query pays a parse
and traversal cost, and a whole class of typos becomes silent data instead of a schema
error. Choosing JSONB versus columns is an architectural decision, not a convenience.

## Core Principles

- **Use JSONB for data that is genuinely schemaless or variable** — third-party webhook
  payloads, user-defined fields, sparse attributes, event envelopes. Use real columns for
  anything you filter, join, sort, or constrain on.
- **A field you query deserves a column.** If you find yourself repeatedly extracting the
  same key, promote it to a typed column; you gain constraints, planner statistics, and a
  cheaper index.
- **Index for the access pattern, not reflexively.** A GIN index accelerates containment
  (`@>`) and key-existence; a B-tree expression index on one extracted path accelerates
  equality/range on that path. They are not interchangeable.
- **Validate on the way in.** JSONB accepts any valid JSON; add a `CHECK` constraint or
  application-side schema validation so garbage cannot enter a column you later depend on.
- **Prefer the `@>` containment and `->>`/`#>>` extraction operators** — they have clear
  index support. Avoid pulling the whole document into the app to filter in code.

## Best Practices

- Use `->` to get a `jsonb` value, `->>` to get `text`; use `#>`/`#>>` for a path array.
  Cast extracted text explicitly (`(data->>'age')::int`) before comparing numerically.
- For containment queries (`WHERE data @> '{"status":"active"}'`), create
  `CREATE INDEX ... USING GIN (data)`; for a smaller, faster index limited to containment
  and existence, use `GIN (data jsonb_path_ops)`.
- For a single hot key, index the expression:
  `CREATE INDEX ON events ((data->>'user_id'))` so equality on that key uses a B-tree.
- Update sub-fields with `jsonb_set(data, '{path}', value)`; remove with `data - 'key'` or
  `#-`. Remember every update rewrites the whole document (MVCC), so large JSONB rows churn.
- Add a `CHECK (jsonb_typeof(data) = 'object')` and validate required keys where correctness
  depends on them.
- Keep documents reasonably small; multi-megabyte JSONB triggers TOAST compression and
  makes every read and update expensive.

## Examples

**Good Example** — columns for structured fields, JSONB for the variable part

```sql
CREATE TABLE events (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id     bigint      NOT NULL REFERENCES users(id),  -- real column: FK + index
  type        text        NOT NULL,                       -- real column: filtered often
  occurred_at timestamptz NOT NULL DEFAULT now(),
  payload     jsonb       NOT NULL DEFAULT '{}'           -- genuinely variable per event type
    CHECK (jsonb_typeof(payload) = 'object')              -- reject non-object garbage
);

-- Containment query backed by a GIN index -> index scan, not a full parse of every row.
CREATE INDEX events_payload_gin ON events USING GIN (payload jsonb_path_ops);
SELECT id FROM events WHERE payload @> '{"source":"mobile"}';
```

**Bad Example** — relational data hidden in an unindexed blob

```sql
CREATE TABLE orders (
  id   bigint PRIMARY KEY,
  data jsonb   -- customer_id, total, status all buried in here
);

-- No FK on customer_id, no index, text compare on a numeric field.
-- Every row is parsed; a typo'd "statuss" key is stored silently, never errors.
SELECT * FROM orders
 WHERE data->>'status' = 'paid'
   AND (data->>'total') > '100';   -- string comparison: '9' > '100' is TRUE. Silent bug.
```

## Common Mistakes

- Storing structured, relational data as JSONB to "skip migrations", losing constraints and joins.
- Comparing extracted values without casting (`data->>'total' > '100'` compares text, not numbers).
- Expecting a GIN index to speed up `data->>'key' = 'x'` — GIN serves `@>`/existence, not `->>` equality.
- Confusing `->` (returns jsonb) with `->>` (returns text) and getting quoted results or type errors.
- Huge JSONB documents that TOAST and make every update rewrite megabytes.
- No validation, so misspelled keys and wrong types accumulate undetected.

## Production Tips

- Watch for JSONB columns that have grown a stable shape — that is the signal to migrate hot
  keys into typed columns and shrink the blob.
- `EXPLAIN` your JSONB queries; a GIN index that is not used usually means the operator
  (`->>` vs `@>`) does not match the index type. See [query planner](05-query-planner.md).
- Because updates rewrite the whole document, split rarely-changing and frequently-changing
  data so hot updates do not churn a large payload and bloat the table.

## AI Review Checklist

- Is JSONB used only for genuinely variable/schemaless data, not for fields that are queried or joined?
- Are frequently-filtered keys promoted to typed columns with proper constraints?
- Do numeric/date comparisons cast the extracted text before comparing?
- Does each JSONB query have a matching index (`GIN` for `@>`/existence, expression B-tree for `->>`)?
- Is there a `CHECK`/validation guarding the document's type and required keys?
- Is `->` vs `->>` used correctly for the intended return type?
- Are documents small enough to avoid TOAST-driven read/update costs?

## Related

- `knowledge/postgresql/03-data-types.md`
- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/09-arrays.md`
- `knowledge/postgresql/05-query-planner.md`
