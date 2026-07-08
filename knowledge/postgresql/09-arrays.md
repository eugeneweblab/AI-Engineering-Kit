---
id: postgresql/09-arrays
topic: postgresql
slug: arrays
title: "Arrays"
type: doc
order: 9
status: ready
tags: [postgresql, arrays]
related: [postgresql/08-jsonb, postgresql/03-data-types, postgresql/04-indexes, postgresql/05-query-planner]
when_to_use: "Read before adding an array column or modeling a one-to-many relationship as an array instead of a join table."
---
# Arrays

## Purpose

This document defines when a PostgreSQL array column is the right model, how to query and
index arrays, and when a proper join table is the correct choice instead. It is written so
an agent can use arrays where they simplify the schema without foreclosing referential
integrity or efficient querying.

PostgreSQL arrays are first-class typed columns (`text[]`, `int[]`, etc.) with operators
for containment, overlap, and element access, and GIN index support. They are excellent for
small, order-or-set-valued attributes and a trap for anything that wants to be a related
entity.

## Why It Matters

Arrays sit at the same decision point as [JSONB](08-jsonb.md): they let you avoid a join
table, and that convenience is exactly what makes them dangerous. An array of `user_id`s
cannot have a foreign key, so it silently accumulates references to deleted users. You
cannot attach per-element data (a "role" alongside each user) without abandoning the array.
Aggregations that are trivial with rows — counts, top-N, joins — become awkward with
arrays. Used for the wrong thing, an array column looks tidy in the schema and quietly
blocks every future requirement that needs integrity or relational querying.

## Core Principles

- **Use arrays for values, not for relationships.** Tags, phone numbers, ordered
  preference lists, embedding vectors — bounded sets of scalars that belong to exactly one
  row and carry no per-element attributes.
- **Use a join table when any of these are true:** the elements are entities with their own
  rows, you need a foreign key, you need per-element columns, or you must query "which rows
  contain X" at scale with joins and aggregation.
- **Index arrays with GIN for membership.** `@>` (contains), `<@` (contained by), and `&&`
  (overlaps) are the array operators a GIN index accelerates; ordinary `=` on an element is not.
- **Order is preserved and meaningful.** Unlike a set, an array keeps insertion order and
  allows duplicates. If order does not matter and duplicates are bugs, an array is a weak model.
- **Arrays are 1-indexed.** `arr[1]` is the first element; out-of-range access returns `NULL`,
  not an error — a common source of silent off-by-one bugs.

## Best Practices

- Query membership with `WHERE tags @> ARRAY['sql']` or `'sql' = ANY(tags)`; back the former
  with `CREATE INDEX ... USING GIN (tags)`. `ANY` is readable but does not use the GIN index.
- Use `&&` for "shares any tag with" and `@>`/`<@` for subset/superset checks — these are the
  set operations arrays do well.
- Append and remove with `array_append`, `array_remove`, or the `||` operator; deduplicate
  with a helper, since arrays do not enforce uniqueness.
- Expand to rows with `unnest()` when you need to join, group, or aggregate over elements —
  this is the bridge back to relational operations.
- Add a `CHECK (array_length(tags, 1) <= 20)` or a `CHECK (tags <> '{}')` when the domain has
  a natural bound, to stop unbounded growth in a single row.
- Prefer arrays of a concrete type (`int[]`, `text[]`) over `jsonb` arrays when elements are
  homogeneous scalars — you get type checking and simpler operators.

## Examples

**Good Example** — array for a bounded set of scalar tags, GIN-indexed

```sql
CREATE TABLE articles (
  id    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title text NOT NULL,
  tags  text[] NOT NULL DEFAULT '{}'
    CHECK (array_length(tags, 1) IS NULL OR array_length(tags, 1) <= 25)  -- bound growth
);

-- GIN index makes containment/overlap fast instead of scanning every row.
CREATE INDEX articles_tags_gin ON articles USING GIN (tags);

SELECT id FROM articles WHERE tags @> ARRAY['postgres'];     -- uses the GIN index
SELECT id FROM articles WHERE tags && ARRAY['sql','db'];     -- overlaps: any tag in common
```

**Bad Example** — a relationship modeled as an array

```sql
CREATE TABLE projects (
  id          bigint PRIMARY KEY,
  member_ids  bigint[]   -- references users, but NO foreign key is possible on array elements
);

-- Deleting a user leaves dangling ids here forever; nothing enforces validity.
-- You cannot store each member's role without abandoning the array.
-- "Projects per user" requires unnest + join anyway -- the join table you avoided.
SELECT * FROM projects WHERE 42 = ANY(member_ids);  -- ANY() cannot use a GIN index -> seq scan
```

## Common Mistakes

- Modeling a one-to-many/many-to-many relationship as an array, losing foreign keys and per-element data.
- Filtering with `= ANY(arr)` and expecting index usage — use `@>` with a GIN index instead.
- Assuming 0-based indexing; PostgreSQL arrays start at 1 and return `NULL` past the end.
- Relying on an array to enforce uniqueness or a set — it allows duplicates and preserves order.
- Letting an array grow unbounded in one row, making updates rewrite an ever-larger value.
- Reaching for `jsonb` arrays for homogeneous scalars and giving up type safety.

## Production Tips

- When you find yourself `unnest`-ing an array in most queries and joining back, that is the
  schema telling you it should have been a table — migrate before the pattern hardens.
- Every array update rewrites the whole array (MVCC), so high-churn, large arrays cause bloat;
  keep them small or move to rows. See [vacuum](20-vacuum.md).
- `EXPLAIN` array queries to confirm the GIN index is used; if you see a sequential scan, the
  operator is probably `ANY`/`=` rather than `@>`/`&&`.

## AI Review Checklist

- Does the array hold scalar values that belong to one row, not entities needing their own rows?
- Would a foreign key, per-element attributes, or relational aggregation be needed? If so, use a join table.
- Are membership queries written with `@>`/`&&` and backed by a GIN index?
- Is array indexing treated as 1-based, with out-of-range `NULL` handled?
- Is there a `CHECK` bounding array length where the domain allows?
- Are homogeneous scalar arrays typed (`int[]`/`text[]`) rather than `jsonb`?

## Related

- `knowledge/postgresql/08-jsonb.md`
- `knowledge/postgresql/03-data-types.md`
- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/05-query-planner.md`
