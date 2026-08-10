---
id: mysql/21-high-availability
topic: mysql
slug: high-availability
title: "MySQL High Availability"
type: doc
order: 21
status: ready
tags: [mysql, high-availability, MySQL, topology, replication, failover]
related: [mysql/09-replication, mysql/10-clustering, mysql/20-production, mysql/11-backups, mysql/15-monitoring]
when_to_use: "Read before designing failover, choosing a replication topology, or reviewing a MySQL deployment's availability guarantees."
---
# MySQL High Availability

## Purpose

This document defines how to keep MySQL serving through the loss of a node, a network, or a
zone: replication topologies, automatic failover, and the consistency trade-offs each one
makes. It is about surviving failure without losing committed data or promoting a stale
replica by mistake.

High availability is not one feature you turn on; it is a set of deliberate choices about
what you will sacrifice — a little latency, a little consistency, or a little
simplicity — to stay up. This document makes those trade-offs explicit so the choice is
informed rather than default.

## Why It Matters

Hardware, networks, and zones fail on their own schedule, and a single MySQL primary is a
single point of failure for every write in the system. Worse than downtime is a botched
failover: promoting a replica that was behind loses committed transactions, and a
"split-brain" where two nodes both accept writes corrupts data in ways that are painful to
reconcile. The cost of getting HA wrong is not a slow app — it is lost or contradictory
data. That is why availability and data safety must be designed together.

## Core Principles

- **Define your objectives first.** RPO (how much data you may lose) and RTO (how long you
  may be down) drive every topology choice; without numbers you cannot judge a design.
- **A stale replica must never be promoted silently.** Failover must check replica position
  and refuse to promote one that is behind, or you trade downtime for data loss.
- **Prevent split-brain by construction.** Only one node may accept writes at a time;
  enforce this with quorum or fencing, never with hope.
- **Semi-sync or group replication buys durability at a latency cost.** Fully async
  replication can lose the last transactions on failover; know which you have chosen.
- **Failover must be automatic and tested.** A runbook a human executes at 3 a.m. is slower
  and more error-prone than an orchestrator you have rehearsed.

## Best Practices

- Prefer **MySQL InnoDB Cluster** (Group Replication + MySQL Router + MySQL Shell) or a
  managed equivalent for a quorum-based, split-brain-resistant setup out of the box.
- If using classic replication, enable **GTIDs** (`gtid_mode = ON`) so failover and replica
  re-pointing are position-safe, and run **semi-synchronous** replication so at least one
  replica acknowledges each commit before it is confirmed.
- Put a proxy (**MySQL Router** or **ProxySQL**) between the app and the database so
  failover is transparent — the app reconnects to a stable endpoint, not a specific host.
- Spread nodes across availability zones; co-locating every replica with the primary means a
  zone failure takes them all.
- Use an orchestrator (**Orchestrator**, or the cluster's built-in manager) to detect
  primary failure and promote the most up-to-date replica automatically.
- Monitor replication lag continuously and fail *reads* away from a lagging replica; route
  writes only to the current primary.
- Test failover on a schedule (game days), measuring actual RTO and confirming no committed
  transaction was lost.

## Examples

**Good Example** — GTID + semi-sync + safe promotion

```sql
-- On every node: position-safe replication so a replica can be promoted correctly.
SET GLOBAL gtid_mode = ON;
SET GLOBAL enforce_gtid_consistency = ON;

-- Require at least one replica to acknowledge each commit before it returns.
INSTALL PLUGIN rpl_semi_sync_source SONAME 'semisync_source.so';
SET GLOBAL rpl_semi_sync_source_enabled = 1;
SET GLOBAL rpl_semi_sync_source_timeout = 1000;  -- ms before falling back to async

-- Before promotion, the orchestrator verifies the replica has applied the primary's
-- GTID set (Retrieved == Executed and matching the old primary) so no committed
-- transaction is dropped. The app talks to MySQL Router, not a hard-coded host.
```

**Bad Example** — async, manual, split-brain-prone

```sql
-- Fully asynchronous replication, no GTIDs, no semi-sync:
CHANGE REPLICATION SOURCE TO SOURCE_HOST='primary', SOURCE_LOG_FILE='bin.000042',
  SOURCE_LOG_POS=1234567;  -- file/position failover is fragile and lossy
-- On primary failure an operator manually promotes a replica WITHOUT checking how far
-- behind it is, silently losing the last transactions. The app has the old primary's IP
-- hard-coded; when it returns, both nodes accept writes → split-brain and data corruption.
```

## Common Mistakes

- Treating async replication as HA and losing the last committed transactions on failover.
- Promoting a replica without verifying it has applied the primary's full GTID set.
- No fencing or quorum, so a network partition lets two nodes accept writes (split-brain).
- Hard-coding the primary's address in the app instead of routing through a proxy, so
  failover requires an application redeploy.
- All replicas in one availability zone, so a single zone failure removes the whole cluster.
- Never rehearsing failover, then discovering the runbook is wrong during a real outage.

## Production Tips

- Automate failover and rehearse it; record the measured RTO and compare it to your target.
- Keep backups and point-in-time recovery even with HA — replication propagates a bad
  `DELETE` to every replica instantly; only backups undo it. See [backups](11-backups.md).
- Alert on replication lag and on any replica that stops applying; a silently broken
  replica is not a spare, it is a surprise during failover.

## AI Review Checklist

- Are RPO and RTO defined, and does the topology actually meet them?
- Is replication position-safe (GTIDs) and durable (semi-sync or group replication)?
- Is split-brain prevented by quorum or fencing, not just convention?
- Does failover verify replica freshness before promoting, and is it automated and tested?
- Does the app connect through a proxy/router rather than a hard-coded primary host?
- Are nodes spread across zones, and do backups still exist alongside replication?

## Related

- `knowledge/mysql/09-replication.md`
- `knowledge/mysql/10-clustering.md`
- `knowledge/mysql/20-production.md`
- `knowledge/mysql/11-backups.md`
- `knowledge/mysql/15-monitoring.md`
