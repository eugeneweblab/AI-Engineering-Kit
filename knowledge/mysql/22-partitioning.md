---
id: mysql/22-partitioning
topic: mysql
slug: partitioning
title: "MySQL Partitioning"
type: doc
order: 22
status: ready
tags: [mysql, partitioning, AUTO_INCREMENT, InnoDB, HASH, EXPLAIN, RANGE, MySQL, scheme, time-series, proposed]
related: [mysql/04-indexes, mysql/05-query-optimization, mysql/14-performance, mysql/03-data-types, mysql/16-migrations]
when_to_use: "Read before adding table partitioning to manage very large tables or time-series data, or when reviewing a proposed partitioning scheme."
---
# MySQL Partitioning

## Purpose

This document defines when and how to partition a MySQL table: splitting one logical table
into physical partitions so the engine can prune irrelevant data and so you can drop old
data instantly. It also defines when *not* to partition, which is more often than teams
expect.

Partitioning is a data-management tool, not a general performance button. It pays off for
large, time-based tables where queries filter on the partition key and old partitions get
dropped wholesale. Applied without those conditions, it adds complexity and can make queries
slower.

## Why It Matters

Teams reach for partitioning hoping it will speed up a slow table, then discover it did
nothing — or made things worse — because their queries do not filter on the partition key,
so MySQL scans every partition anyway. Meanwhile the real, reliable win of partitioning
(dropping a month of data with an instant `DROP PARTITION` instead of a multi-hour `DELETE`
that bloats the table and lags replicas) goes unused. Understanding what partitioning
actually does prevents both the wasted effort and the missed win.

## Core Principles

- **Partition to manage data lifecycle, not to replace indexes.** The killer feature is
  `DROP`/`TRUNCATE PARTITION` for aging out data; a good index is what speeds up lookups.
- **Pruning only works when the query filters on the partition key.** If the partition
  column is not in the `WHERE` clause, every partition is scanned — no benefit, extra cost.
- **The partition key must be part of every unique key,** including the primary key. This
  is an InnoDB requirement and it constrains your whole schema design.
- **Fewer, larger partitions beat many tiny ones.** Each partition has overhead; hundreds
  or thousands of partitions slow the optimizer and metadata operations.
- **Partitioning is not sharding.** All partitions live on one server; it does not
  distribute load across machines.

## Best Practices

- Use `RANGE` partitioning on a time column (e.g. by month) for append-mostly, expire-old
  data such as logs, events, and metrics — this is the sweet spot.
- Keep a `MAXVALUE` catch-all partition and manage partitions ahead of time: add next
  month's partition before you need it, drop the oldest when it ages out.
- Verify pruning with `EXPLAIN` — check the `partitions` column shows only the partitions
  the query needs, not all of them.
- Include the partition column in the primary key and every unique index, and design
  queries to always filter on it.
- Prefer `DROP PARTITION` over `DELETE ... WHERE created_at < ...` to purge old data; it is
  near-instant, reclaims space immediately, and does not generate massive binlog/undo.
- Measure first. If a single well-indexed table serves your queries, do not partition — the
  complexity is only justified by data-lifecycle needs or genuine multi-terabyte scale.

## Examples

**Good Example** — RANGE by time, prunable, instant purge

```sql
CREATE TABLE events (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  created_at DATETIME        NOT NULL,
  payload    JSON            NOT NULL,
  -- Partition key MUST be in every unique key, so created_at joins the PK:
  PRIMARY KEY (id, created_at)
) ENGINE=InnoDB
PARTITION BY RANGE COLUMNS (created_at) (
  PARTITION p2026_06 VALUES LESS THAN ('2026-07-01'),
  PARTITION p2026_07 VALUES LESS THAN ('2026-08-01'),
  PARTITION p_future VALUES LESS THAN (MAXVALUE)
);

-- Query filters on the partition key, so the optimizer prunes to one partition:
EXPLAIN SELECT * FROM events WHERE created_at >= '2026-07-01';  -- partitions: p2026_07

-- Purge June instantly instead of a slow, bloating DELETE:
ALTER TABLE events DROP PARTITION p2026_06;
```

**Bad Example** — partitioning that never prunes

```sql
CREATE TABLE events (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id    BIGINT UNSIGNED NOT NULL,
  created_at DATETIME        NOT NULL
) ENGINE=InnoDB
PARTITION BY HASH (id) PARTITIONS 64;  -- hashing the PK gives no pruning for real queries

-- The app queries by user_id and time, never by id:
SELECT * FROM events WHERE user_id = 42 AND created_at >= '2026-07-01';
-- created_at/user_id are not the partition key → MySQL scans ALL 64 partitions.
-- Result: extra overhead, no pruning, and still no way to drop old data cheaply.
```

## Common Mistakes

- Partitioning to "make the table faster" when the fix is a proper index; pruning requires
  the partition key in the `WHERE` clause.
- Choosing a partition key (like a hash of the PK) that queries never filter on, so no
  partition is ever pruned.
- Forgetting that the partition column must be in the primary key and every unique index,
  then hitting a schema error or being forced to weaken uniqueness.
- Creating hundreds or thousands of partitions, slowing the optimizer and DDL.
- Confusing partitioning with sharding and expecting it to spread load across servers.
- Not pre-creating future partitions, so inserts fall into `MAXVALUE` and lose pruning.

## Production Tips

- Automate partition maintenance (an event scheduler job or external cron) to add upcoming
  partitions and drop expired ones, so the scheme never falls behind the data.
- Watch for the `MAXVALUE` partition growing — it means new data is not landing in a
  dedicated partition and pruning has silently degraded.
- Roll partitioning onto a large existing table with an online schema-change tool; a naive
  repartition rebuilds the whole table under lock.

## AI Review Checklist

- Is there a concrete data-lifecycle or scale reason to partition, versus just indexing?
- Do the real queries filter on the partition key so `EXPLAIN` shows actual pruning?
- Is the partition column included in the primary key and every unique index?
- Is old data purged via `DROP PARTITION` rather than large `DELETE`s?
- Is the partition count reasonable (tens, not thousands), with future partitions pre-created?
- Is the design not being mistaken for sharding / horizontal scale-out?

## Related

- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/14-performance.md`
- `knowledge/mysql/03-data-types.md`
- `knowledge/mysql/16-migrations.md`
