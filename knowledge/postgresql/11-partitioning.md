---
id: postgresql/11-partitioning
topic: postgresql
slug: partitioning
title: "PostgreSQL Partitioning"
type: doc
order: 11
status: ready
tags: [postgresql, partitioning, VACUUM, pg_partman, DETACH, HASH, RANGE, EXPLAIN, time-series, growing, large]
related: [postgresql/04-indexes, postgresql/05-query-planner, postgresql/20-vacuum, postgresql/16-performance]
when_to_use: "Read before partitioning a large table, or when a growing time-series/multi-tenant table is becoming slow to query, vacuum, or prune."
---
# PostgreSQL Partitioning

## Purpose

This document defines when to partition a PostgreSQL table, how to choose a partition
strategy and key, and the operational rules that keep partitioning a win rather than a
liability. It is written so an agent can partition a table for the right reason and avoid
the common failure where partitioning makes performance worse.

Declarative partitioning splits one logical table into physical child tables by range, list,
or hash on a partition key. The planner can then skip (prune) partitions that cannot match a
query, and maintenance operations act on one small partition at a time.

## Why It Matters

Partitioning is a scaling tool with a narrow sweet spot, and it is frequently applied to
tables that do not need it. Its real benefits appear at large scale: dropping a whole
partition to expire old data is instant and lock-cheap versus a slow `DELETE`; `VACUUM` and
index maintenance run per-partition instead of over one enormous heap; and queries filtered
on the partition key touch only relevant partitions. But partition on the wrong key and
every query scans every partition — you have added planning overhead and complexity for
nothing. Too many partitions and planning time itself dominates. Partitioning is a
commitment that reshapes how you write queries, migrations, and indexes.

## Core Principles

- **Partition for a concrete operational reason, not table size alone.** Good reasons: cheap
  bulk expiry (`DROP` old partitions), per-partition maintenance to tame `VACUUM`/bloat, and
  pruning for queries always filtered on the key. A merely "big" table is often better served
  by good indexes.
- **The partition key must appear in almost every query's `WHERE`/`JOIN`.** Pruning only
  works when the planner can rule out partitions from the key. If most queries do not filter
  on the key, partitioning hurts.
- **Match strategy to intent.** RANGE for time-series and sequential data (expire by date),
  LIST for a small fixed set of categories/regions, HASH to spread write load evenly when no
  natural range exists.
- **Keep the partition count moderate.** Hundreds of partitions are fine; tens of thousands
  bloat planning time and system-catalog overhead. Size partitions so each is manageable
  (e.g. monthly, not hourly, unless volume demands it).
- **Automate partition lifecycle.** Missing a future partition means inserts fail (no default)
  or pile into a catch-all. Create ahead of need and drop on a schedule.

## Best Practices

- Define range partitions with explicit bounds and pre-create the next several periods, e.g.
  via `pg_partman` or a scheduled job, so writes never hit a missing partition.
- Put the partition key in the `PRIMARY KEY`/unique constraints — PostgreSQL requires the
  partition key to be part of any unique index on a partitioned table.
- Create indexes on the partitioned parent (`CREATE INDEX ON parent (...)`); PostgreSQL
  cascades them to every existing and future partition automatically.
- Attach/detach partitions with `ATTACH`/`DETACH PARTITION` (use `DETACH ... CONCURRENTLY`)
  to add or expire data with minimal locking; validate constraints before attaching.
- Confirm pruning is happening with `EXPLAIN` — look for far fewer partitions scanned than
  exist. Ensure `enable_partition_pruning` is on (default).
- Add a `DEFAULT` partition only deliberately; rows in it block adding new partitions whose
  range overlaps, so it can become an operational trap.

## Examples

**Good Example** — range partitioning on the always-filtered time key

```sql
-- Events are always queried by time window and expired monthly -> RANGE on occurred_at.
CREATE TABLE events (
  id          bigint GENERATED ALWAYS AS IDENTITY,
  occurred_at timestamptz NOT NULL,
  payload     jsonb NOT NULL,
  PRIMARY KEY (id, occurred_at)          -- partition key MUST be in the PK
) PARTITION BY RANGE (occurred_at);

CREATE TABLE events_2026_07 PARTITION OF events
  FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
CREATE TABLE events_2026_08 PARTITION OF events
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');   -- pre-created ahead of need

CREATE INDEX ON events (occurred_at);    -- cascades to all partitions

-- Filter on the key -> planner prunes to a single partition.
EXPLAIN SELECT * FROM events WHERE occurred_at >= '2026-07-10' AND occurred_at < '2026-07-11';

-- Expiring July is instant and lock-cheap, unlike a huge DELETE.
DROP TABLE events_2026_06;
```

**Bad Example** — partitioning on a key queries never filter by

```sql
-- Partitioned by hash of id, but the app searches by user_id and occurred_at.
CREATE TABLE events (id bigint, user_id bigint, occurred_at timestamptz, payload jsonb)
  PARTITION BY HASH (id);
-- ... 64 hash partitions ...

-- No query filters on id, so NOTHING can be pruned: every one of the 64 partitions
-- is scanned on every query. Slower than an unpartitioned table + a user_id index.
SELECT * FROM events WHERE user_id = 42 AND occurred_at > now() - interval '1 day';
```

## Common Mistakes

- Partitioning on a key that queries rarely filter on, so no pruning happens and every partition is scanned.
- Partitioning a table that is not large enough to benefit — pure overhead versus a good index.
- Too many tiny partitions, inflating planning time and catalog bloat.
- Forgetting to pre-create future partitions, so inserts fail or land in a `DEFAULT` catch-all.
- Trying to create a unique constraint that does not include the partition key (PostgreSQL rejects it).
- Using slow `DELETE` for expiry instead of `DROP`/`DETACH PARTITION`, defeating a main reason to partition.

## Production Tips

- Automate creation/retention with `pg_partman` or a scheduled job; a missing partition is a
  production incident, not a warning.
- Verify pruning after every schema or query change with `EXPLAIN (ANALYZE)`; a regression to
  "all partitions scanned" is silent and costly. See [query planner](05-query-planner.md).
- Per-partition `VACUUM`/`ANALYZE` is a major operational benefit — but ensure autovacuum is
  actually keeping up per partition; many small tables can each need attention. See [vacuum](20-vacuum.md).
- Detaching with `DETACH PARTITION CONCURRENTLY` avoids the long lock that plain `DETACH` takes.

## AI Review Checklist

- Is there a concrete operational reason (bulk expiry, per-partition maintenance, pruning), not just size?
- Does the partition key appear in the `WHERE`/`JOIN` of essentially every query?
- Does `EXPLAIN` confirm the planner prunes to a small subset of partitions?
- Is the strategy (RANGE/LIST/HASH) matched to the data and expiry pattern?
- Is the partition key included in the primary key and unique constraints?
- Is partition creation/retention automated so future writes never hit a missing partition?
- Is old data expired via `DROP`/`DETACH`, not slow `DELETE`?

## Related

- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/05-query-planner.md`
- `knowledge/postgresql/20-vacuum.md`
- `knowledge/postgresql/16-performance.md`
