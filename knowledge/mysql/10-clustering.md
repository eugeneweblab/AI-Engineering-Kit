---
id: mysql/10-clustering
topic: mysql
slug: clustering
title: "Clustering"
type: doc
order: 10
status: ready
tags: [mysql, clustering]
related: [mysql/09-replication, mysql/21-high-availability, mysql/11-backups, mysql/20-production]
when_to_use: "Read before choosing a clustering topology for HA or write scaling, or evaluating Group Replication vs Galera vs NDB."
---
# Clustering

## Purpose

This document defines the MySQL clustering options that provide automatic failover and,
in some cases, synchronous multi-node consistency: **Group Replication** (and its packaged
form, InnoDB Cluster), **Galera** (Percona XtraDB Cluster / MariaDB Galera), and **NDB
Cluster**. It is written so an agent picks a topology that matches the consistency,
availability, and write-scaling requirements — and understands what each one gives up.

Clustering builds on [replication](09-replication.md) and is the practical route to
[high availability](21-high-availability.md). It does not remove the need for
[backups](11-backups.md): a cluster replicates mistakes instantly to every node.

## Why It Matters

Clustering promises "no single point of failure," but each option makes a different
CAP-shaped trade-off, and choosing the wrong one produces outages or data loss under
exactly the conditions you bought the cluster to survive. A synchronous cluster can stall
all writes when one node is slow; a multi-primary cluster surfaces write conflicts your
application never handled; a naive setup can **split-brain** and accept divergent writes on
both sides of a network partition. These failures happen during incidents, when you least
want surprises. The clustering choice must be deliberate, quorum-aware, and understood.

## Core Principles

- **Quorum prevents split-brain.** A safe cluster needs an odd number of voting members
  (3, 5, ...) so a minority partition refuses writes rather than diverging.
- **Synchronous means certification, not free lunch.** Group Replication and Galera certify
  each transaction across the group; a slow or overloaded node applies backpressure to the
  whole cluster.
- **Multi-primary invites write conflicts.** Writing the same rows on two nodes causes
  conflict-abort (Galera) or rollback (Group Replication). Prefer single-primary unless the
  application is conflict-aware.
- **Clustering is availability, not a backup.** A `DROP TABLE` certifies and applies on
  every node in milliseconds.
- **The topology dictates the failure mode.** Pick based on how you need the system to
  behave during a partition, not on peak-throughput benchmarks.

## Best Practices

- Default to **InnoDB Cluster (Group Replication) in single-primary mode** for HA on modern
  MySQL: it is the vendor-supported path, provides automatic primary election, and uses
  MySQL Router for transparent client failover.
- Run an **odd number of members** (minimum 3) so the group can form a quorum and a
  partitioned minority correctly stops accepting writes.
- Keep members close (same region / low-latency network). Synchronous certification is
  latency-sensitive; cross-region members make every commit slow.
- Choose **single-primary** unless you can prove the workload has no cross-node write
  conflicts. Multi-primary is an expert mode, not a default.
- For Galera, tune `wsrep_sync_wait` when you need read-your-writes on a node, and monitor
  flow control (`wsrep_flow_control_paused`) — sustained pausing means a node is dragging
  the cluster.
- Reserve **NDB Cluster** for its niche: in-memory, high-write, auto-sharded workloads with
  simple access patterns. It is operationally distinct and not a drop-in for InnoDB.
- Automate client routing (MySQL Router, ProxySQL) so applications never hard-code a node
  address that becomes wrong at failover.

## Examples

**Good Example** — bootstrap a 3-node single-primary InnoDB Cluster

```sql
-- Run in MySQL Shell. Three members give quorum; single-primary means one
-- writable node and automatic election on failure. MySQL Router then routes
-- writes to the primary and reads to secondaries transparently.
dba.createCluster('prodCluster', {memberSslMode: 'REQUIRED'});
cluster = dba.getCluster('prodCluster');
cluster.addInstance('mysql-2:3306');   -- second member -> quorum needs a third
cluster.addInstance('mysql-3:3306');   -- odd member count avoids split-brain
cluster.status();                      -- verify all ONLINE, one R/W primary
```

**Bad Example** — two-node cluster with no quorum arbiter

```text
# A 2-node "cluster" cannot form a majority when the link between them breaks:
# each node sees the other as gone. Either both refuse writes (no availability)
# or, if misconfigured to proceed, both accept writes and SPLIT-BRAIN. You now
# have two divergent primaries and no automatic way to reconcile them.
node-1 <----X network partition X----> node-2
   (writes?)                              (writes?)
# Fix: add a third voting member (or an arbitrator) so a majority always exists.
```

## Common Mistakes

- Running an even number of nodes (especially two), making quorum impossible and split-brain
  likely.
- Enabling multi-primary and then discovering the application writes the same rows on
  multiple nodes, causing conflict aborts under load.
- Placing synchronous cluster members across regions and blaming MySQL for slow commits.
- Treating the cluster as a backup and having no point-in-time recovery when a bad migration
  replicates everywhere.
- Hard-coding a single node's address in the app, so failover leaves clients pointed at a
  dead or demoted node.
- Ignoring flow control / apply lag until one slow disk stalls the entire cluster's writes.

## Production Tips

- Test failover deliberately: kill the primary in staging and confirm election time, client
  reconnection, and no lost committed transactions before trusting it in production.
- Run an arbitrator/lightweight third member if a full third data node is too costly — you
  still need the vote.
- Keep a monitoring path for member state, quorum, and apply/flow-control lag; a cluster
  that has silently dropped to a single ONLINE member is one failure from an outage.

## AI Review Checklist

- Does the cluster have an odd number of voting members (>= 3) so quorum is always possible?
- Is single-primary mode used unless a conflict-aware multi-primary design is proven?
- Are synchronous members co-located to keep commit latency acceptable?
- Is client routing handled by Router/ProxySQL rather than hard-coded node addresses?
- Has failover been tested end-to-end (election, reconnection, zero committed-data loss)?
- Is there a separate backup/PITR strategy, since clustering replicates mistakes instantly?

## Related

- `knowledge/mysql/09-replication.md`
- `knowledge/mysql/21-high-availability.md`
- `knowledge/mysql/11-backups.md`
- `knowledge/mysql/20-production.md`
