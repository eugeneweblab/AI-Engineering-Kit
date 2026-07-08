---
id: mysql/28-architecture
topic: mysql
slug: architecture
title: "Architecture"
type: doc
order: 28
status: ready
tags: [mysql, architecture]
related: [mysql/08-storage-engines, mysql/09-replication, mysql/06-transactions, mysql/21-high-availability]
when_to_use: "Read before designing how services talk to MySQL, or when reasoning about durability, buffer pool, or replication topology."
---
# Architecture

## Purpose

This document explains MySQL's internal architecture at the level an engineer needs to
make correct design decisions: the connection and SQL layers, the pluggable storage
engine (InnoDB), how the buffer pool and redo/undo logs deliver durability, and how the
binary log drives replication. It is a mental model for reasoning about performance and
failure, not an operations runbook.

Understanding this architecture is what separates guessing from knowing when you tune
durability, size memory, or choose a replication topology. Every trade-off below flows
from how these components actually work.

## Why It Matters

Most severe MySQL incidents come from a wrong mental model: assuming a `COMMIT` is durable
when `sync_binlog=0`, sizing the buffer pool at defaults so the working set never fits in
memory, or believing an asynchronous replica is a consistent read source. These are not
bugs in MySQL — they are the documented behavior of components the team did not
understand. Because architecture decisions (engine, durability settings, topology) are
baked in early and expensive to reverse, getting the model right up front prevents the
class of failure that surfaces only under production load or during a failover.

## Core Principles

- **Requests flow through layers.** Connection/auth → parser → optimizer → executor →
  **storage engine**. The upper layers are engine-agnostic; durability and locking live in
  the engine.
- **Use InnoDB.** It is the default transactional, row-locking, crash-safe engine. MyISAM
  and MEMORY lack transactions and crash safety — do not use them for real data. See
  [storage engines](08-storage-engines.md).
- **The buffer pool is where performance lives.** InnoDB serves reads and writes from an
  in-memory buffer pool and flushes to disk asynchronously. If the working set does not
  fit, you are disk-bound.
- **Durability is the redo log, not the data file.** A `COMMIT` writes the redo log; data
  pages flush later. `innodb_flush_log_at_trx_commit` and `sync_binlog` decide how much a
  crash can lose.
- **Replication is driven by the binary log.** The primary records changes to the binlog;
  replicas replay them. Default async replication means replicas lag and can lose the last
  transactions on failover. See [replication](09-replication.md).

## Best Practices

- Run **InnoDB** for all application data. Reserve special engines only for their narrow
  purpose, never for durable business data.
- Size `innodb_buffer_pool_size` to hold the hot working set — commonly ~50–75% of RAM on
  a dedicated database host. This is the single highest-impact tuning knob.
- For financial/critical data, set `innodb_flush_log_at_trx_commit = 1` and
  `sync_binlog = 1` (full ACID: every commit is flushed and fsynced). Relax to `2`/`0`
  only when you can afford to lose the last second of writes for throughput.
- Use **row-based binary logging** (`binlog_format = ROW`) for deterministic, safe
  replication; statement-based logging replicates non-deterministic statements incorrectly.
- Send reads that require the latest committed state to the **primary**; only route reads
  to replicas when bounded staleness is acceptable, and measure lag. See
  [high availability](21-high-availability.md).
- Keep transactions short. InnoDB holds row locks and undo for the life of a transaction;
  long transactions bloat undo (history list) and block purge. See [transactions](06-transactions.md).

## Examples

**Good Example** — durability and memory matched to the workload

```ini
# my.cnf for a dedicated host holding critical, transactional data
[mysqld]
default_storage_engine        = InnoDB
innodb_buffer_pool_size       = 48G   # ~70% of 64G RAM: hot set stays in memory
innodb_flush_log_at_trx_commit = 1    # every commit is fsynced -> no committed data lost on crash
sync_binlog                   = 1     # binlog fsynced per commit -> replica cannot lose acked txns
binlog_format                 = ROW   # deterministic replication of the actual row changes
```

```sql
-- Read that must be authoritative goes to the primary, not a lagging replica:
SELECT balance FROM accounts WHERE id = ? FOR UPDATE;  -- read the truth, then act
```

**Bad Example** — silent data loss and a disk-bound server

```ini
[mysqld]
default_storage_engine        = MyISAM   # no transactions, no crash recovery, table locks
innodb_buffer_pool_size       = 128M     # default-ish: working set never fits -> disk-bound
innodb_flush_log_at_trx_commit = 0       # commits are NOT fsynced -> a crash loses ~1s of "committed" data
sync_binlog                   = 0        # replica can lose transactions the primary acknowledged
```

```sql
-- Reading the balance from an async replica that lags behind the primary:
-- the value may be stale, so a subsequent debit can overdraw the account.
SELECT balance FROM accounts WHERE id = ?;   -- from a replica, treated as authoritative
```

## Common Mistakes

- Using MyISAM/MEMORY for durable data and losing transactions and crash safety.
- Leaving the buffer pool at its small default so the server is perpetually disk-bound.
- Believing `COMMIT` is durable while `innodb_flush_log_at_trx_commit`/`sync_binlog` are
  relaxed — a crash then loses acknowledged writes.
- Treating an asynchronous replica as a consistent read source and acting on stale data.
- Running long-lived transactions that bloat undo and stall InnoDB's purge thread.
- Using statement-based binlog with non-deterministic statements, drifting replicas apart.

## Production Tips

- Watch buffer pool hit ratio and free pages; a falling hit ratio means the working set no
  longer fits and reads are going to disk. See [monitoring](15-monitoring.md).
- Track replica lag (`Seconds_Behind_Source`) and the InnoDB history list length; growth
  in either signals a long transaction or overloaded replica.
- Prefer semi-synchronous replication or a consensus system (Group Replication / a
  Galera-based cluster) when you cannot tolerate losing acknowledged transactions on
  failover.

## AI Review Checklist

- Is all durable application data on InnoDB (not MyISAM/MEMORY)?
- Is the buffer pool sized to the working set rather than left at the default?
- Do durability settings (`innodb_flush_log_at_trx_commit`, `sync_binlog`) match the data's
  loss tolerance?
- Is `binlog_format = ROW` used for safe replication?
- Are authoritative reads sent to the primary, with replica staleness explicitly accounted
  for?
- Are transactions kept short to avoid undo/history bloat and lock contention?

## Related

- `knowledge/mysql/08-storage-engines.md`
- `knowledge/mysql/09-replication.md`
- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/21-high-availability.md`
