---
id: databases/16-partitioning
topic: databases
slug: partitioning
title: "Database Partitioning"
type: doc
order: 16
status: ready
tags: [databases, partitioning, DETACH, EXPLAIN, HASH, RANGE, pg_partman, UNION, time-series, tables, splitting]
related: [databases/15-sharding, databases/07-indexing, databases/08-query-optimization, databases/20-performance, databases/24-soft-delete]
when_to_use: "Read before splitting a large table into partitions, especially for time-series or fast-growing tables."
---
# Database Partitioning

## Purpose

This document defines how to split one large table into partitions *inside a single
database server* so queries stay fast and old data is cheap to drop, and how to pick a
partition key and strategy that the planner can actually use. It exists so an agent can
decide when partitioning helps, choose range/list/hash correctly, and avoid the
mistakes that make it worse than one big table.

Partitioning divides one logical table into physical pieces on the *same* server. It
is distinct from [sharding](15-sharding.md), which spreads data across *different*
servers. Partitioning is the lighter, reach-for-it-first tool; sharding is the last
resort when one server is no longer enough.

## Why It Matters

For large, ever-growing tables — events, logs, orders, time-series — partitioning is
the difference between a query that scans one day and one that scans two years. Done
well, the planner prunes to a single partition and dropping old data is an instant
`DETACH`/`DROP` instead of a table-locking mass `DELETE`. Done badly — a partition key
the query never filters on, or per-row partitions — it adds planning overhead, bloats
the catalog, and speeds up nothing. The wrong key is also awkward to change, because it
requires rewriting the whole table. Because the payoff and the trap both hinge on one
key choice, it deserves deliberate reasoning.

## Core Principles

- **Partitioning helps when queries filter on the partition key** so the planner can
  *prune* — skip irrelevant partitions entirely. If your `WHERE` clauses don't include
  the key, you gain little and pay planning overhead.
- **Match the strategy to the data.** *Range* for ordered/time data (by month, by id
  range); *list* for discrete categories (by region, by tenant); *hash* for even
  spread when there is no natural range. Choosing wrong defeats pruning.
- **The biggest win is cheap data lifecycle.** Dropping an old range partition is
  near-instant and lock-light; deleting the same rows from one big table is slow and
  bloats it. Partition by time when you have retention windows.
- **Right-size partitions.** Too few and each is still huge; too many (thousands) and
  planning and maintenance costs dominate. Aim for partitions in a manageable range,
  not one per day forever without a cap.
- **Indexes and constraints are per-partition.** Unique constraints must include the
  partition key (or use a global mechanism); each partition carries its own indexes.

## Best Practices

- Choose a partition key that appears in the `WHERE` clause of your dominant queries —
  usually the same column you filter and range-scan on (e.g. `created_at`).
- Use **native declarative partitioning** (PostgreSQL `PARTITION BY RANGE`, MySQL
  `PARTITION BY`) rather than manual table-per-period plus a `UNION` view; the planner
  prunes native partitions automatically.
- Automate partition creation and retention with a scheduler (e.g. `pg_partman` or a
  cron job) so a missing future partition never rejects an insert.
- Include the partition key in primary keys and unique constraints, because the engine
  enforces uniqueness per partition — otherwise duplicates slip across partitions.
- Drop or `DETACH` old partitions for retention instead of bulk `DELETE`; it is faster
  and avoids bloat and vacuum pressure.
- Verify pruning with `EXPLAIN` after any query or key change — confirm the plan
  touches only the expected partitions.

## Examples

**Good Example** — range by time, prunes and drops cleanly

```sql
-- Native range partitioning: queries that filter created_at prune to one child.
CREATE TABLE events (
  id         bigint,
  created_at timestamptz NOT NULL,
  payload    jsonb,
  PRIMARY KEY (id, created_at)          -- key includes the partition column
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2026_07 PARTITION OF events
  FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');

-- Planner scans ONLY events_2026_07, not the whole history.
EXPLAIN SELECT * FROM events
 WHERE created_at >= '2026-07-05' AND created_at < '2026-07-06';

-- Retention: dropping July is instant and lock-light vs a mass DELETE.
DROP TABLE events_2025_07;
```

**Bad Example** — key the queries never filter on

```sql
-- Partitioned by a hash of id, but every real query filters by time.
CREATE TABLE events (
  id bigint, created_at timestamptz, payload jsonb
) PARTITION BY HASH (id);              -- id is not what we filter on

-- This query filters created_at, which the planner CANNOT use to prune,
-- so it scans EVERY partition -> slower than a single well-indexed table,
-- and old data can only be removed by an expensive full-table DELETE.
SELECT * FROM events
 WHERE created_at >= '2026-07-05' AND created_at < '2026-07-06';
```

## Common Mistakes

- Partitioning on a column the hot queries don't filter on, so pruning never happens.
- Creating one partition per day with no cap or cleanup, ending up with thousands of
  partitions that slow planning.
- Forgetting to include the partition key in unique constraints, allowing cross-
  partition duplicates.
- Not pre-creating future partitions, so inserts fail when data outruns the ranges.
- Using bulk `DELETE` for retention instead of `DROP`/`DETACH`, causing bloat.
- Reaching for partitioning when a proper index would have solved the query — verify
  with `EXPLAIN` first.

## Production Tips

- Automate creation of the next N future partitions and retention drops on a schedule;
  alert if the newest partition window is close to "now".
- Watch partition count and per-partition size; consolidate or coarsen ranges if
  counts explode.
- Re-check `EXPLAIN` plans after schema or query changes to confirm pruning still
  fires.

## AI Review Checklist

- Does the partition key match the column the dominant queries filter on, and does
  `EXPLAIN` confirm pruning?
- Is the strategy (range/list/hash) appropriate to the data's shape?
- Is partition creation and retention automated so inserts never hit a missing
  partition?
- Do unique constraints and primary keys include the partition key?
- Is old data removed with `DROP`/`DETACH` rather than bulk `DELETE`?
- Is the partition count bounded, avoiding thousands of tiny partitions?

## Related

- `knowledge/databases/15-sharding.md`
- `knowledge/databases/07-indexing.md`
- `knowledge/databases/08-query-optimization.md`
- `knowledge/databases/20-performance.md`
- `knowledge/databases/24-soft-delete.md`
