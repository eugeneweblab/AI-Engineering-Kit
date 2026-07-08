---
id: mysql/04-indexes
topic: mysql
slug: indexes
title: "Indexes"
type: doc
order: 4
status: ready
tags: [mysql, indexes]
related: [mysql/05-query-optimization, mysql/03-data-types, mysql/14-performance, mysql/00-overview]
when_to_use: "Read before adding, removing, or ordering an index, or when a query is slow."
---
# Indexes

## Purpose

This document defines how to design InnoDB indexes: what an index is, when to add one, how
to order composite index columns, and how to confirm it is used. Indexes are the single
biggest lever on query performance — and each one is a standing tax on every write.

## Why It Matters

Without the right index, MySQL scans the whole table to answer a query; at a million rows
that is the difference between one millisecond and one second, and it degrades as the table
grows. But indexes are not free: every `INSERT`, `UPDATE`, and `DELETE` must also update every
affected index, and each index consumes memory in the buffer pool. An unused or redundant
index slows writes and wastes cache for zero benefit. The job is to add exactly the indexes
your queries need and no more — a judgment you can only make by looking at real query patterns
and `EXPLAIN` output.

## Core Principles

- **Index to match your `WHERE`, `JOIN`, and `ORDER BY` clauses.** An index earns its keep only
  if queries use it. Index the columns you actually filter, join, and sort on.
- **The clustered index is the table.** In InnoDB, rows are physically stored in primary-key
  order. A small, monotonic key (`BIGINT AUTO_INCREMENT`) keeps inserts append-only; a random
  key (UUID string) scatters writes and fragments the table.
- **Composite index order follows the leftmost-prefix rule.** An index on `(a, b, c)` can serve
  `WHERE a`, `WHERE a AND b`, and `WHERE a AND b AND c` — but not `WHERE b` alone. Order columns
  most-selective-and-equality-first, range-last.
- **Verify, don't assume.** `EXPLAIN` tells you whether an index is actually used. An index that
  exists but is never chosen is pure overhead.

## Best Practices

- Give every table an explicit, narrow, monotonic `PRIMARY KEY`. Let secondary indexes reference
  it implicitly.
- Put equality columns before range columns in a composite index. A range (`>`, `<`, `BETWEEN`,
  `LIKE 'x%'`) stops the index from using any column to its right for filtering.
- Build **covering indexes** for hot queries: include every column the query reads so MySQL
  answers it from the index alone (`Using index` in `EXPLAIN`), skipping the row lookup.
- Add a composite index that also satisfies `ORDER BY` to avoid a filesort — the sort direction
  and column order must match.
- Index foreign key columns; InnoDB requires it, and joins depend on it.
- Drop redundant indexes: `(a)` is redundant if `(a, b)` exists, since the composite already
  covers the prefix. Redundant indexes cost writes for nothing.
- For `LIKE`, only a **prefix** match (`'abc%'`) uses a B-tree index; a leading wildcard
  (`'%abc'`) cannot. Use FULLTEXT for real text search. See [full-text-search](23-full-text-search.md).

## Examples

**Good Example** — composite index ordered for the query

```sql
-- Query: recent orders for a user, newest first
SELECT id, total_cents, created_at
FROM orders
WHERE user_id = 42
ORDER BY created_at DESC
LIMIT 20;

-- Equality column (user_id) first, sort column (created_at) second.
-- This index filters by user_id AND supplies the sort order — no filesort.
-- Including total_cents makes it covering: EXPLAIN shows "Using index".
CREATE INDEX idx_orders_user_created
  ON orders (user_id, created_at, total_cents);
```

**Bad Example** — wrong order, unusable index, redundant duplicate

```sql
-- Column order puts the range/sort column first, so filtering by user_id
-- can't use the index efficiently and MySQL still does a filesort.
CREATE INDEX idx_bad ON orders (created_at, user_id);

-- Leading-wildcard LIKE: a B-tree index on email can't be used at all -> full scan.
SELECT * FROM users WHERE email LIKE '%@gmail.com';

-- Redundant: (user_id) is already the leftmost prefix of the composite above.
-- It costs write time on every insert/update and caches nothing new.
CREATE INDEX idx_orders_user ON orders (user_id);
```

## Common Mistakes

- Adding an index per column instead of one composite index that matches the query.
- Ordering composite columns wrong — range or sort column before the equality column.
- Assuming a leading-wildcard `LIKE '%x'` or a function on a column (`WHERE YEAR(created_at)=…`)
  uses an index; both force a full scan. Index the raw column and query it by range.
- Keeping redundant indexes whose prefix is already covered by a wider composite.
- Using a random/UUID-string primary key, scattering inserts across the clustered index.
- Over-indexing a write-heavy table, so every write updates a dozen indexes.
- Never checking `EXPLAIN`, so a dead index looks like a working one.

## Production Tips

- Find unused indexes via `sys.schema_unused_indexes` and redundant ones via
  `sys.schema_redundant_indexes`; drop them to speed up writes and reclaim cache.
- Adding an index on a large table is an online DDL operation in 8.0+ but still consumes I/O;
  do it in a low-traffic window or with a schema-change tool. See [migrations](16-migrations.md).
- Watch `Handler_read_rnd_next` and slow-query rows-examined to catch queries silently
  scanning tables despite an index existing.

## AI Review Checklist

- Does an index exist for each frequent `WHERE`, `JOIN`, and `ORDER BY` clause?
- In composite indexes, do equality columns come before range/sort columns?
- Are hot queries served by a covering index (`Using index` in `EXPLAIN`)?
- Is the primary key small, monotonic, and explicit (no random UUID strings)?
- Are foreign key columns indexed?
- Have redundant and unused indexes been dropped?
- Was `EXPLAIN` used to confirm the new index is actually chosen?

## Related

- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/03-data-types.md`
- `knowledge/mysql/14-performance.md`
- `knowledge/mysql/00-overview.md`
- `knowledge/mysql/23-full-text-search.md`
