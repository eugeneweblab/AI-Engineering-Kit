---
id: mysql/09-replication
topic: mysql
slug: replication
title: "Replication"
type: doc
order: 9
status: ready
tags: [mysql, replication]
related: [mysql/10-clustering, mysql/11-backups, mysql/21-high-availability, mysql/06-transactions]
when_to_use: "Read before setting up read replicas, planning failover, or debugging replica lag."
---
# Replication

## Purpose

This document defines how MySQL replication works and how to run it safely: copying writes
from a primary ("source") to one or more replicas for read scaling, high availability, and
backups. It is written so an agent configures replication with the durability and
consistency guarantees the application actually needs, and does not mistake a lagging
replica for a consistent one.

Replication is the foundation for [clustering](10-clustering.md) and
[high availability](21-high-availability.md), and a common source for
[backups](11-backups.md). It is **asynchronous by default**, which means a replica can be
behind — a fact your read paths must account for.

## Why It Matters

Replication is where "the read returned stale data" and "we lost the last minute of
writes during failover" come from. Because standard replication is asynchronous, a
committed transaction on the primary is not guaranteed to be on any replica yet — so
reading your own write from a replica can miss it, and a primary crash can lose
un-replicated transactions. These are correctness bugs disguised as infrastructure. The
defaults optimize for throughput, not safety; you must opt into GTIDs, row-based logging,
and semi-synchronous replication to get guarantees you can reason about.

## Core Principles

- **Asynchronous replication can lag.** A replica reflects the primary's *past*. Never
  assume a read replica is current unless you have measured or enforced it.
- **Use GTIDs, not file-and-position.** Global Transaction Identifiers make failover and
  replica re-pointing deterministic; legacy binlog-file coordinates are error-prone.
- **Use row-based binary logging (`binlog_format=ROW`).** It replicates the exact row
  changes, avoiding the non-determinism of statement-based replication (`NOW()`, `RAND()`,
  triggers).
- **Replication is not a backup.** It faithfully replicates a `DROP TABLE` too. You still
  need point-in-time [backups](11-backups.md).
- **Failover has a data-loss window unless you make it synchronous.** Semi-synchronous
  replication trades a little latency for a bounded loss guarantee.

## Best Practices

- Enable GTIDs (`gtid_mode=ON`, `enforce_gtid_consistency=ON`) on every node so replicas
  can be re-pointed and failed over without hand-computing binlog positions.
- Set `binlog_format=ROW` and `binlog_row_image=MINIMAL` for deterministic, compact
  replication.
- For durability, set `sync_binlog=1` and `innodb_flush_log_at_trx_commit=1` on the
  primary so a committed transaction survives an OS crash — the default trades this for speed.
- Enable **semi-synchronous replication** when failover must not silently lose committed
  transactions: the primary waits for at least one replica to acknowledge the write.
- Route reads that require read-your-writes consistency to the **primary**, or gate them
  on GTID (`WAIT_FOR_EXECUTED_GTID_SET`) so the replica has caught up first.
- Monitor lag with `SHOW REPLICA STATUS` (`Seconds_Behind_Source`) and, more reliably, a
  heartbeat table; alert before lag affects users.
- Give each server a unique `server_id` and a unique `server_uuid`; duplicates break
  replication in subtle, data-corrupting ways.
- Make replicas `read_only` (or `super_read_only`) so application bugs cannot write to
  them and diverge from the primary.

## Examples

**Good Example** — GTID + row-based + durable + semi-sync (primary config)

```ini
# my.cnf on the primary: deterministic, crash-safe, and no silent data loss
# because at least one replica must acknowledge each commit.
server_id                        = 1
gtid_mode                        = ON        # deterministic failover / re-pointing
enforce_gtid_consistency         = ON
binlog_format                    = ROW       # avoids NOW()/RAND() non-determinism
sync_binlog                      = 1         # binlog fsynced on commit (durable)
innodb_flush_log_at_trx_commit   = 1         # redo log fsynced on commit (durable)
rpl_semi_sync_source_enabled     = ON        # wait for a replica ack -> bounded loss
```

**Bad Example** — reading stale data from an async replica

```sql
-- App writes to the primary, then immediately reads from a read replica.
-- Because replication is asynchronous, the replica may not have the row yet,
-- so the user sees their just-created record as missing. Read-your-writes is
-- violated. Either read from the primary here, or WAIT_FOR_EXECUTED_GTID_SET.
INSERT INTO comments (post_id, body) VALUES (42, 'first!');   -- on primary
SELECT * FROM comments WHERE post_id = 42;                    -- on lagging replica -> empty
```

## Common Mistakes

- Treating a read replica as strongly consistent and getting read-your-writes bugs.
- Leaving `binlog_format=STATEMENT`, so non-deterministic statements diverge the replica.
- Using file/position replication and mis-computing coordinates during a failover, breaking
  the replica.
- Relying on replication as the only backup, then replicating an accidental `DELETE` to
  every node.
- Duplicate `server_id`/`server_uuid` across nodes, causing silent replication corruption.
- Forgetting `read_only` on replicas, letting a stray write create divergence that manual
  reconciliation must later untangle.
- Ignoring `Seconds_Behind_Source` until a replica is minutes behind and serving stale reads.

## Production Tips

- Prefer a battle-tested orchestration layer (Orchestrator, MySQL Group Replication,
  Vitess) over hand-rolled failover scripts; correct failover is genuinely hard.
- Use a heartbeat (e.g., `pt-heartbeat`) rather than `Seconds_Behind_Source` alone — the
  latter reads 0 when a replica is stuck but idle.
- Take backups from a dedicated replica to avoid load on the primary, but verify that
  replica is not lagging when the backup starts.

## AI Review Checklist

- Are GTIDs enabled (`gtid_mode=ON`) on all nodes for deterministic failover?
- Is `binlog_format=ROW` set to avoid non-deterministic replication?
- Are `sync_binlog=1` and `innodb_flush_log_at_trx_commit=1` set where durability matters?
- Do read paths that need read-your-writes go to the primary or wait on a GTID?
- Are replicas `read_only`/`super_read_only` with unique `server_id` and `server_uuid`?
- Is replication lag monitored with a heartbeat and alerted on?
- Is there a real backup strategy in addition to replication?

## Related

- `knowledge/mysql/10-clustering.md`
- `knowledge/mysql/11-backups.md`
- `knowledge/mysql/21-high-availability.md`
- `knowledge/mysql/06-transactions.md`
