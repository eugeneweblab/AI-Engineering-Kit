---
id: redis/18-replication
topic: redis
slug: replication
title: "Redis Replication"
type: doc
order: 18
status: ready
tags: [redis, replication, WAIT, "master_link_status:down", master_repl_offset, FLUSHALL]
related: [redis/19-clustering, redis/20-persistence, redis/22-monitoring, redis/27-production]
when_to_use: "Read before deploying Redis with replicas, adding read scaling, or configuring failover."
---
# Redis Replication

## Purpose

This document defines how to run a Redis primary with one or more replicas: how
data flows, what guarantees you get, and how to avoid the two classic failures —
serving stale reads and losing acknowledged writes during failover. It covers
plain replication and Sentinel-managed failover. For horizontal sharding across
many primaries, see [clustering](19-clustering.md).

Replication answers "how do I keep a copy of the data and survive a node dying?".
It is not a backup ([persistence](20-persistence.md) is) and it is not sharding.

## Why It Matters

Replication is **asynchronous by default**, so a primary acknowledges a write to
the client *before* the replica has it. If the primary crashes in that window, the
write is gone even though the client was told it succeeded. Teams discover this
during their first failover, in production, with real data. The blast radius is
every write in flight at the moment of failure. Understanding the exact guarantee
Redis gives you — and where it stops — is the difference between a resilient system
and silent data loss.

## Core Principles

- **Replication is asynchronous; treat acknowledgement as "primary has it", not
  "the cluster has it".** The replica lags by a network round trip or more.
- **Replicas are read-only and eventually consistent.** A read from a replica can
  return a value older than a write you just made to the primary.
- **Failover is not free.** Promoting a replica loses any writes the old primary
  had not yet shipped. `WAIT` and `min-replicas-*` reduce the window; they do not
  close it.
- **A replica is not a backup.** It faithfully replicates deletes, flushes, and
  corruption. You still need RDB/AOF snapshots stored off-box.
- **Never let clients pick the primary manually.** Use Sentinel or Cluster so the
  topology has a single source of truth for "who is primary right now".

## Best Practices

- Configure replicas with `replicaof <primary-host> <primary-port>` (or via the
  managed service). Keep `replica-read-only yes` — the default — so a stray write
  to a replica cannot diverge the dataset.
- Set `min-replicas-to-write` and `min-replicas-max-lag` on the primary so it
  **refuses writes** when too few replicas are caught up. This trades availability
  for durability; choose deliberately.
- Use `WAIT <numreplicas> <timeout-ms>` after critical writes to block until N
  replicas acknowledge. It bounds — but never eliminates — the loss window.
- Enable **diskless replication** (`repl-diskless-sync yes`) on fast networks to
  avoid a full RDB dump to disk on the primary during resync.
- Size `repl-backlog-size` large enough that a briefly disconnected replica does a
  cheap **partial** resync instead of a full one. Full resyncs stall the primary.
- Run **Sentinel** (odd number, ≥3, on separate hosts) for automatic failover, or
  use a managed service that does this for you. Never build failover by hand.
- Route read-only traffic to replicas only when your app tolerates staleness. Route
  read-after-write and any counter/lock logic to the primary.

## Examples

**Good Example** — durability-aware write path

```bash
# On the primary: refuse writes unless at least 1 replica is within 10s of lag.
# WHY: if all replicas fall behind or die, accepting writes guarantees loss on
# the next failover. Failing closed surfaces the problem instead of hiding it.
CONFIG SET min-replicas-to-write 1
CONFIG SET min-replicas-max-lag 10
```

```python
# Critical write: confirm a replica has it before we report success upstream.
r.set("order:1042:status", "paid")
acked = r.execute_command("WAIT", 1, 1000)  # block up to 1s for >=1 replica
if acked < 1:
    raise DurabilityError("write not replicated; do not confirm the order")
```

**Bad Example** — assumes ack means durable, reads own write from a replica

```python
primary.set("order:1042:status", "paid")   # async ack — replica may not have it
# ... primary crashes here, before the replica receives the write ...

# App reads from a replica pool for "scaling", expecting its own write back:
status = replica.get("order:1042:status")   # returns None or old value
# The order silently reverts to unpaid. No error was ever raised.
```

## Common Mistakes

- Treating a `SET` reply as durable. It only means the primary buffered it.
- Reading your own recent writes from a replica, then acting on stale data.
- Writing to a replica (after clearing `replica-read-only`), causing permanent
  divergence that the next resync silently overwrites or preserves inconsistently.
- Running Sentinel with an even number of nodes or co-locating it with Redis, so a
  single host failure loses quorum.
- Using a replica as your only backup and being surprised when a `FLUSHALL`
  replicates instantly to every copy.
- Undersized `repl-backlog-size`, so every brief disconnect triggers a full resync
  that saturates the primary's CPU and network.

## Production Tips

- Alert on `master_link_status:down` and on `master_repl_offset` minus the
  replica's `slave_repl_offset` (replication lag) from `INFO replication`.
- Test failover in staging: kill the primary, confirm Sentinel promotes a replica,
  and measure how many writes were lost with your `WAIT`/`min-replicas` settings.
- Keep primary and replicas on the same Redis version to avoid resync issues.
- Do not point application writes at Sentinel's IPs directly; ask Sentinel (or the
  client's Sentinel support) for the current primary each reconnect.

## AI Review Checklist

- Does the code assume a write is durable after `SET`, or does it use `WAIT` /
  `min-replicas-*` for writes that must survive failover?
- Are read-after-write paths routed to the primary, not a replica?
- Is `replica-read-only` left enabled so replicas cannot diverge?
- Is failover handled by Sentinel or the managed service, never by client logic?
- Is there a real backup (RDB/AOF off-box), separate from replicas?
- Is replication lag monitored and alerted on?

## Related

- `knowledge/redis/19-clustering.md`
- `knowledge/redis/20-persistence.md`
- `knowledge/redis/22-monitoring.md`
- `knowledge/redis/27-production.md`
