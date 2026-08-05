---
id: databases/14-replication
topic: databases
slug: replication
title: "Database Replication"
type: doc
order: 14
status: ready
tags: [databases, replication]
related: [databases/13-eventual-consistency, databases/22-high-availability, databases/12-acid, databases/18-backup-and-recovery, databases/15-sharding]
when_to_use: "Read before adding read replicas, configuring failover, or routing reads and writes across database nodes."
---
# Database Replication

## Purpose

This document defines how to copy a database across multiple nodes for
availability and read scale, and how to write code and configuration that stays
correct when it does. It exists so an agent can choose a replication mode, route
queries safely, and reason about what happens during failover.

Replication is *copying the same data* to more nodes. It is distinct from
[sharding](15-sharding.md), which *splits different data* across nodes. Replication
buys you redundancy and read throughput; it does not increase write capacity, and it
introduces [eventual consistency](13-eventual-consistency.md) on the read path.

## Why It Matters

Replication is the foundation of both high availability and read scaling — and the
place where "it worked in staging" fails hardest. A misrouted write to a read replica
throws or silently no-ops. A failover that promotes a replica which was seconds behind
loses committed-looking data. Asynchronous replication that everyone treated as
synchronous means a client got a `COMMIT` ack for a row that vanished when the primary
died. These failures are rare, catastrophic, and only appear under the exact
conditions replication exists to handle — node loss and lag. That is precisely why the
setup must be reasoned about, not copy-pasted.

## Core Principles

- **One writer, many readers (in leader-based replication).** All writes go to the
  primary; replicas are read-only copies. Writing to a replica is a bug.
- **Sync vs async is a durability/latency trade.** *Synchronous* replication waits for
  a replica to acknowledge before `COMMIT` returns — no data loss on primary failure,
  but higher write latency and a stall if the replica is down. *Asynchronous* returns
  immediately — fast, but a crashed primary can lose the last un-replicated writes.
- **Replicas lag.** A read replica reflects the primary as of some past moment. The lag
  is small until it isn't (long transactions, network, load).
- **Failover is not free or instant.** Promoting a replica takes time, may lose async
  writes, and requires clients to reconnect and re-discover the new primary.
- **Quorum bounds data loss.** With N replicas, requiring W acknowledgments (e.g.
  `synchronous_commit` to at least one) trades latency for a guarantee that a write
  survives the loss of up to some nodes.

## Best Practices

- Route writes and read-your-own-writes to the primary; route bulk/analytic and
  staleness-tolerant reads to replicas. Make this routing explicit in the data layer,
  not scattered.
- Use synchronous (or quorum) replication for data you cannot afford to lose on
  failover; accept the latency. Use async only where losing the last few writes is
  survivable.
- Configure automatic failover with a proven tool (Patroni, the managed provider's
  failover, orchestrator) — do not hand-roll leader election.
- Fence the old primary on failover (STONITH / leader lease) so a network partition
  cannot produce two primaries accepting writes ("split brain").
- Monitor replication lag and replica health; refuse to promote a replica whose lag
  exceeds your data-loss tolerance.
- Test failover regularly in a non-prod environment, including client reconnection —
  an untested failover is a liability, not a safety net.
- Keep replicas as a *complement* to backups, never a substitute: replication copies
  corruption and bad `DELETE`s instantly. See [backup and recovery](18-backup-and-recovery.md).

## Examples

**Good Example** — explicit routing, primary for its own writes

```ts
// The data layer decides target by intent, so callers can't accidentally
// write to a replica or read their own write from a lagging one.
class Db {
  write(sql: string, p: unknown[]) {
    return this.primary.query(sql, p);       // all writes -> primary
  }
  readStale(sql: string, p: unknown[]) {
    return this.replicaPool.query(sql, p);   // analytics, feeds: replica OK
  }
  readFresh(sql: string, p: unknown[]) {
    return this.primary.query(sql, p);       // read-your-writes: primary
  }
}
```

**Bad Example** — writes to a replica, promotes blindly

```yaml
# App points reads AND writes at a load balancer that fans out to all nodes.
# Writes that land on a read-only replica fail; ones that land on the primary
# succeed -> nondeterministic errors under load.
database_url: postgres://app@db-lb:5432/app   # LB includes replicas

# Failover config promotes the most-reachable replica with no lag check.
# If it was 8s behind, every write in that window is lost, and the old
# primary is never fenced -> split brain when it rejoins.
failover:
  promote: any_reachable_replica
  fencing: none
```

## Common Mistakes

- Sending writes to a read replica (directly or via a load balancer that includes
  replicas in the write path).
- Reading a user's own just-committed write from a lagging replica.
- Assuming async replication is durable and losing the last writes on failover.
- No fencing, allowing two primaries after a partition (split brain) and diverging
  data.
- Treating replicas as backups — they faithfully replicate corruption and accidental
  deletes.
- Never testing failover, then discovering at 3am that clients don't reconnect.

## Production Tips

- Alert on replication lag with a threshold below your failover data-loss tolerance.
- Use a connection proxy (PgBouncer/ProxySQL) or the cloud provider's endpoint so
  clients re-discover the new primary automatically after failover.
- Add read replicas to absorb reporting/analytics load and protect the primary's
  write latency.
- Record whether each write path is sync or async in code review — durability
  expectations should be visible.

## AI Review Checklist

- Do all writes and read-your-writes go to the primary, never a replica?
- Is the sync/async choice appropriate to the data's loss tolerance, and documented?
- Is failover automated with a proven tool, with fencing to prevent split brain?
- Is a replica refused promotion when its lag exceeds the data-loss budget?
- Are backups maintained separately, since replicas propagate corruption?
- Has failover (including client reconnection) actually been tested?

## Related

- `knowledge/databases/13-eventual-consistency.md`
- `knowledge/databases/22-high-availability.md`
- `knowledge/databases/12-acid.md`
- `knowledge/databases/18-backup-and-recovery.md`
- `knowledge/databases/15-sharding.md`
