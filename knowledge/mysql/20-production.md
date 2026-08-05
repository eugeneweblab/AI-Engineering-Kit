---
id: mysql/20-production
topic: mysql
slug: production
title: "MySQL Production"
type: doc
order: 20
status: ready
tags: [mysql, production]
related: [mysql/02-configuration, mysql/11-backups, mysql/15-monitoring, mysql/21-high-availability, mysql/09-replication]
when_to_use: "Read before deploying MySQL to production or reviewing a production database's configuration and operational readiness."
---
# MySQL Production

## Purpose

This document defines what "production-ready" means for a MySQL server: durable
configuration, capacity, backups you have actually restored, monitoring, and safe change
procedures. It is the checklist between a database that works on a laptop and one you can
trust with real users and real money.

Production readiness is about the failure cases, not the happy path. Any config runs a
`SELECT`; a production config survives a power loss, a full disk, a runaway query, and a
3 a.m. schema change without losing or corrupting data.

## Why It Matters

The gap between development and production defaults in MySQL is enormous and silent. The
out-of-the-box buffer pool is tiny, durability may be relaxed, backups do not exist, and a
single unbounded query can exhaust connections and take the app down. None of this shows in
testing. The first time you learn a default was wrong is during an incident — a crash that
loses the last minute of writes, a disk that fills because binlogs never expire, a restore
that fails because no one tested it. Configuring for production up front converts those
incidents into non-events.

## Core Principles

- **Durability is not optional.** The default fully-durable settings must be deliberate,
  and any relaxation must be a documented, understood trade-off, not an accident.
- **A backup you have not restored is not a backup.** Recoverability is proven by drill,
  never assumed from a successful backup job.
- **Everything that can fill up must be bounded.** Connections, disk, binlogs, temp space,
  and query runtime all need explicit limits or they become the outage.
- **Change under load must be safe.** Schema changes on a live table need an online tool
  or a controlled rollout; a naive `ALTER` can lock the table for hours.
- **You cannot fix what you cannot see.** Metrics, slow logs, and alerting are part of the
  deployment, not an afterthought.

## Best Practices

- Size `innodb_buffer_pool_size` to roughly 50–75% of RAM on a dedicated database host so
  the working set stays in memory; the default (128 MB) is only for development.
- Keep `innodb_flush_log_at_trx_commit = 1` and `sync_binlog = 1` for full ACID durability.
  Relax to `2` only with an explicit, accepted risk of losing ~1 second of writes on crash.
- Cap `max_connections` to what the host can actually serve and put a connection pooler
  (ProxySQL) in front — thousands of direct connections thrash memory and CPU.
- Set `max_execution_time` and `innodb_lock_wait_timeout` so a pathological query fails
  fast instead of holding resources and cascading into an outage.
- Automate backups with `mysqldump`/`mydumper` for logical or Percona XtraBackup for
  physical, keep binary logs for point-in-time recovery, and **test a full restore on a
  schedule** — see [backups](11-backups.md).
- Expire binary logs (`binlog_expire_logs_seconds`) and monitor disk so binlogs and
  temp files cannot silently fill the volume.
- Use an online schema-change tool (`gh-ost`, `pt-online-schema-change`, or InnoDB
  `ALGORITHM=INPLACE, LOCK=NONE` where supported) for `ALTER`s on large live tables.
- Run replicas and never point the application at a single database with no failover — see
  [high availability](21-high-availability.md).

## Examples

**Good Example** — durable, bounded, observable config

```ini
# my.cnf — production baseline for a dedicated 64 GB host
[mysqld]
innodb_buffer_pool_size        = 40G   # ~60% of RAM; working set stays in memory
innodb_flush_log_at_trx_commit = 1     # full durability: no committed txn lost on crash
sync_binlog                    = 1     # binlog fsynced with the commit
innodb_flush_method            = O_DIRECT
max_connections                = 500   # bounded; a pooler fans out to app instances
max_execution_time             = 30000 # 30s ceiling: runaway SELECTs fail, not hang
binlog_expire_logs_seconds     = 604800 # 7 days, then reclaimed; disk cannot fill silently
slow_query_log                 = 1
long_query_time                = 1
```

**Bad Example** — dev defaults shipped to production

```ini
[mysqld]
# innodb_buffer_pool_size left at default 128M → constant disk I/O, cache misses
innodb_flush_log_at_trx_commit = 0   # flushes once/sec: a crash loses committed data
sync_binlog                    = 0   # binlog and data can diverge after a crash
# max_connections unbounded in practice; no pooler → memory exhaustion under a spike
# no slow log, no backups, binlogs never expire → disk fills, no way to recover
```

## Common Mistakes

- Leaving `innodb_buffer_pool_size` at the development default, so the working set never
  fits in memory and every read hits disk.
- Relaxing `innodb_flush_log_at_trx_commit` for speed without accepting — in writing — the
  data-loss window it creates.
- Having backup jobs that succeed but were never restore-tested; discovering they are
  unusable during a real recovery.
- Unbounded binary logs or temp space filling the disk and stopping all writes.
- Running a blocking `ALTER TABLE` on a large table during business hours and locking it.
- A single database instance with no replica and no failover plan.

## Production Tips

- Run a quarterly restore drill from real backups into an isolated host and time it; your
  recovery-time objective is only real if you have measured it.
- Alert on buffer pool hit ratio, replication lag, connection saturation, disk headroom,
  and long-running transactions — not just on "is the server up".
- Keep configuration in version control and apply it through automation so every node is
  identical and changes are reviewable and reversible.

## AI Review Checklist

- Is `innodb_buffer_pool_size` sized to the host, not left at the default?
- Are `innodb_flush_log_at_trx_commit` and `sync_binlog` set for full durability, or is any
  relaxation documented as an accepted risk?
- Are connections, binlog retention, disk, and query runtime all explicitly bounded?
- Do automated backups exist *and* has a full restore been tested recently?
- Are large-table schema changes performed with an online, non-blocking method?
- Is there a replica and a defined failover path, plus alerting on the key health metrics?

## Related

- `knowledge/mysql/02-configuration.md`
- `knowledge/mysql/11-backups.md`
- `knowledge/mysql/15-monitoring.md`
- `knowledge/mysql/21-high-availability.md`
- `knowledge/mysql/09-replication.md`
