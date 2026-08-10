---
id: postgresql/28-architecture
topic: postgresql
slug: architecture
title: "PostgreSQL Architecture"
type: doc
order: 28
status: ready
tags: [postgresql, architecture, PgBouncer, RANGE, synchronous_commit, partitioning, topology, fits]
related: [postgresql/12-replication, postgresql/13-high-availability, postgresql/11-partitioning, postgresql/06-transactions, postgresql/20-vacuum]
when_to_use: "Read before designing how PostgreSQL fits into a system: replicas, partitioning, connection topology, and scaling boundaries."
---
# PostgreSQL Architecture

## Purpose

This document defines how PostgreSQL is deployed and scaled at the system level: primary
and replica topology, read/write routing, partitioning, connection layering, and where a
single database stops being enough. It is written so an agent can choose a topology that
matches the workload instead of copying a diagram.

It is about the shape *around* the database — how clients reach it, how it survives node
loss, and how it grows — not about internal query mechanics.

## Why It Matters

Architecture decisions are the hardest to reverse. Sharding a table, splitting a service's
database, or moving from a single node to a replicated cluster are multi-week migrations
under load, not config changes. Choosing the wrong topology early — sharding before you
need it, or running a single node past its ceiling — costs either wasted complexity or an
emergency migration during an outage. The goal is a topology matched to the actual read/write
ratio, durability requirement, and data size, chosen with room to grow.

## Core Principles

- **One primary accepts writes.** PostgreSQL streaming replication is single-primary;
  replicas are read-only. Any "multi-master" claim needs conflict resolution you must design.
- **Replicas are for reads and failover, and they lag.** A read replica can serve a stale
  snapshot; never route read-after-write consistency to a replica.
- **Scale vertically first.** A single well-tuned Postgres node handles very large
  workloads. Reach for replicas, then partitioning, then sharding — in that order, only when
  measured need appears.
- **Partition for manageability, not just speed.** Partitioning's biggest win is dropping
  old data instantly and vacuuming smaller units, not automatic query speedup.
- **Put a pooler between clients and the database.** Connection topology is part of the
  architecture; direct connections do not scale past the process ceiling.

## Best Practices

- Use streaming replication with at least one replica for HA; promote a replica on primary
  failure via an orchestrator (Patroni, or a managed service) rather than by hand.
- Route writes and read-after-write to the primary; route heavy analytic and eventually-
  consistent reads to replicas. Make routing explicit in the data layer.
- Use `synchronous_commit`/synchronous replication for the small set of transactions that
  must survive primary loss with zero data loss; accept its latency cost only where needed.
- Partition large tables by a key that matches how you query and expire data — usually
  time (range) for logs/events, so old partitions detach and drop in milliseconds.
- Keep one service's writes behind one owner. Multiple services writing the same tables
  makes schema change and consistency everyone's problem and no one's.
- Layer connections: app → pooler (PgBouncer transaction mode) → Postgres. Size the pool to
  the database, and let many app workers share it.
- Defer sharding until a single primary plus read replicas is genuinely exhausted; sharding
  removes cross-shard transactions and joins, a large permanent tax.

## Examples

**Good Example** — explicit routing over a primary/replica topology

```text
                    writes + read-after-write
   app workers  ───────────────────────────────▶  PgBouncer  ──▶  PRIMARY (rw)
        │                                                             │  streaming
        │            eventually-consistent reads                      ▼  replication
        └──────────────────────────────────────▶  PgBouncer  ──▶  REPLICA (ro, may lag)
```

```sql
-- Partition an events table by time so expiry is a metadata operation, not a mass DELETE.
CREATE TABLE events (id bigint, occurred_at timestamptz NOT NULL, payload jsonb)
  PARTITION BY RANGE (occurred_at);
CREATE TABLE events_2026_07 PARTITION OF events
  FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
-- Dropping July's data later: DROP TABLE events_2026_07;  -- instant, no bloat, no vacuum churn
```

**Bad Example** — stale reads and premature sharding

```sql
-- User just placed an order; reading it back from a lagging replica returns "not found".
INSERT INTO orders (...) VALUES (...);            -- goes to PRIMARY
SELECT * FROM orders WHERE id = $1;               -- routed to REPLICA -> may not exist yet

-- Sharding a 20 GB table across 8 nodes "for scale" it does not need:
--   loses cross-shard JOINs and transactions, adds a routing layer, complicates every query
--   for years — to solve a problem a single tuned node handles comfortably.
```

## Common Mistakes

- Routing read-after-write queries to a replica and serving stale or missing rows.
- Assuming replicas provide write scaling; they scale reads only.
- Sharding early, permanently losing cross-shard transactions and joins to solve a
  non-problem.
- Partitioning on a key you never filter by, adding overhead with no benefit.
- Multiple services writing the same tables, making every schema change a coordination
  crisis.
- Treating failover as automatic when no orchestrator is configured to actually promote.

## Production Tips

- Test failover and measure replica lag under real write load; lag is invisible until it
  causes a stale-read bug.
- Automate partition creation ahead of time; a missing future partition rejects inserts.
- Keep the routing decision (primary vs replica) in one place in the data layer so it can be
  audited and changed.

## AI Review Checklist

- Do all writes and read-after-write reads target the primary, never a replica?
- Is there a replica plus an automated promotion path for failover?
- Is vertical scaling and read-replica scaling exhausted before sharding is proposed?
- Is partitioning keyed to how data is queried and expired (usually time)?
- Does exactly one service own writes to each set of tables?
- Do clients connect through a pooler rather than directly?

## Related

- `knowledge/postgresql/12-replication.md`
- `knowledge/postgresql/13-high-availability.md`
- `knowledge/postgresql/11-partitioning.md`
- `knowledge/postgresql/06-transactions.md`
- `knowledge/postgresql/20-vacuum.md`
