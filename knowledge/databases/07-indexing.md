---
id: databases/07-indexing
topic: databases
slug: indexing
title: "Indexing"
type: doc
order: 7
status: ready
tags: [databases, indexing]
related: [databases/08-query-optimization, databases/06-schema-design, databases/20-performance, databases/11-locking, databases/17-migrations]
when_to_use: "Read before adding an index, diagnosing a slow query, or reviewing a query plan."
---
# Indexing

## Purpose

This document defines when and how to add indexes: what an index is for, which
columns and order to use, and the costs an index imposes. It is written so an
agent can add the right index for a slow query — and refuse to add ones that only
hurt.

Indexing is the physical companion to [query optimization](08-query-optimization.md):
the optimizer can only choose a fast plan if an index exists to support it. Both
depend on a sound [schema](06-schema-design.md).

## Why It Matters

Without a supporting index, the database must scan every row to answer a query.
That is fine at a thousand rows and catastrophic at ten million — the same query
degrades from milliseconds to minutes as data grows, with no code change to blame.
The correct index turns a sequential scan into a direct lookup and is usually the
single highest-leverage performance fix available.

But indexes are not free. Every index must be updated on every `INSERT`, `UPDATE`,
and `DELETE`, and it consumes storage and memory. An unused or redundant index
slows down writes and wastes cache for zero benefit. Indexing is a trade: read
speed bought with write cost, and it must be justified per index.

## Core Principles

- **Index to match query shape, not intuition.** Add an index because a real,
  frequent query filters, joins, or sorts on those columns — verified in the plan,
  not guessed.
- **Column order in a composite index matters.** A `(a, b)` index serves queries
  filtering on `a` or on `a AND b`, but not on `b` alone. Put equality columns
  first, then the range/sort column.
- **Selectivity decides usefulness.** An index on a column with few distinct values
  (e.g. boolean `is_active`) rarely helps; the engine still reads most rows.
- **Covering beats lookups.** If an index contains every column a query needs, the
  engine answers from the index alone (index-only scan) and never touches the table.
- **Every index is a write tax.** More indexes mean slower writes and more storage.
  Keep only indexes that a query actually uses.

## Best Practices

- Index foreign key columns. They are almost always used in joins and `WHERE`
  clauses, and un-indexed FKs also make parent deletes scan the child table.
- Build composite indexes in **equality → range → sort** order. `WHERE tenant_id = ?
  AND created_at > ?` wants `(tenant_id, created_at)`, not the reverse.
- Use a **partial index** for queries that always filter on a condition:
  `WHERE deleted_at IS NULL` indexes only live rows, keeping it small and hot.
- Add a **covering index** (via `INCLUDE` in Postgres/SQL Server) for hot read paths
  so they become index-only scans.
- Enforce uniqueness with a `UNIQUE` index/constraint — it both guarantees the
  invariant and accelerates lookups.
- Verify every new index with `EXPLAIN (ANALYZE)` before and after: confirm the plan
  switched from a scan and latency actually dropped.
- Drop indexes that monitoring shows are unused (`pg_stat_user_indexes`,
  `sys.dm_db_index_usage_stats`). They cost writes for nothing.

## Examples

**Good Example** — one composite index that serves filter, join, and sort

```sql
-- Query the index must serve:
--   SELECT id, total FROM orders
--   WHERE customer_id = $1 AND status = 'paid'
--   ORDER BY created_at DESC LIMIT 20;

CREATE INDEX idx_orders_customer_status_created
  ON orders (customer_id, status, created_at DESC)  -- equality cols first, sort col last
  INCLUDE (total);                                   -- covers SELECT -> index-only scan

-- Plan becomes an Index Scan (no sort, no heap fetch) instead of Seq Scan + Sort.
```

**Bad Example** — indexes that duplicate work and don't match queries

```sql
CREATE INDEX idx_orders_customer ON orders (customer_id);              -- redundant:
CREATE INDEX idx_orders_customer_status ON orders (customer_id, status); -- ...prefix of the next
CREATE INDEX idx_orders_status ON orders (status);   -- low selectivity: few distinct statuses
CREATE INDEX idx_orders_created ON orders (created_at); -- unused: no query sorts on it alone
-- Four indexes, three of them dead weight, all taxing every write to orders.
```

## Common Mistakes

- Adding an index per column instead of one composite index matching the query.
- Wrong column order — putting the range/sort column before the equality column.
- Indexing low-selectivity columns (booleans, a handful of statuses) on their own.
- Redundant indexes: `(a)` is already covered by the leading edge of `(a, b)`.
- A function or cast in the `WHERE` clause (`WHERE lower(email) = ?`) that bypasses
  a plain column index — needs an expression index instead.
- Forgetting to index foreign keys, slowing joins and cascading deletes.
- Never removing indexes, accumulating write-tax that no query redeems.

## Production Tips

- Build indexes on large live tables with `CREATE INDEX CONCURRENTLY` (Postgres) so
  writes are not blocked during the build; see [locking](11-locking.md).
- On write-heavy tables, batch or defer index creation — each new index slows every
  insert immediately.
- Review index usage stats quarterly; drop the ones with zero scans.

## AI Review Checklist

- Does each index correspond to a real, frequent query's filter/join/sort columns?
- Is composite column order equality → range → sort?
- Are foreign key columns indexed?
- Is the query verified with `EXPLAIN ANALYZE` to actually use the new index?
- Are there redundant indexes (a prefix already covered by a wider one)?
- Are low-selectivity single-column indexes justified, or dead weight?
- Could a partial or covering index shrink the index or enable an index-only scan?

## Related

- `knowledge/databases/08-query-optimization.md`
- `knowledge/databases/06-schema-design.md`
- `knowledge/databases/20-performance.md`
- `knowledge/databases/11-locking.md`
- `knowledge/databases/17-migrations.md`
