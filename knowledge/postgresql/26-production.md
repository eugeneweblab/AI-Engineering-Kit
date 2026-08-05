---
id: postgresql/26-production
topic: postgresql
slug: production
title: "PostgreSQL Production"
type: doc
order: 26
status: ready
tags: [postgresql, production]
related: [postgresql/13-high-availability, postgresql/14-backups, postgresql/17-monitoring, postgresql/12-replication, postgresql/98-production-checklist]
when_to_use: "Read before deploying a PostgreSQL database to production or reviewing its operational readiness."
---
# PostgreSQL Production

## Purpose

This document defines what a PostgreSQL database needs before it carries real traffic:
durability, recoverability, connection management, resource limits, and safe change
processes. It is written so an agent can judge whether a database is production-ready or
one incident away from data loss.

Production readiness is not a tuning task; it is a set of guarantees. The question is not
"is it fast?" but "when a disk, a network, or a deploy fails, do we lose data or availability,
and for how long?"

## Why It Matters

The database is the one component whose failure is usually unrecoverable. A crashed
stateless service restarts; a corrupted or unbackuped database is gone. Most production
disasters are not exotic — they are an untested backup, a connection pool exhausted at
peak, a migration that locked a hot table, or a single node with no failover. Each is
cheap to prevent and catastrophic to skip. Readiness means these failure modes were
handled *before* the traffic arrived.

## Core Principles

- **A backup you have never restored is not a backup.** Recoverability is proven by
  restore drills, not by the existence of a dump file.
- **Define your RPO and RTO, then engineer to them.** How much data you may lose (RPO)
  and how long you may be down (RTO) drive backup frequency and failover design.
- **Never connect applications directly at scale.** Each Postgres connection is a backend
  process; a pooler is mandatory, not optional.
- **Every setting has a limit; set it explicitly.** Unbounded connections, statements,
  and transactions are how a database falls over under load.
- **Change production the same way twice.** Migrations and config changes go through the
  same reviewed, reversible, tested path every time.

## Best Practices

- Run **continuous archiving (WAL archiving) plus base backups** (e.g. pgBackRest) for
  point-in-time recovery, not just periodic `pg_dump`. `pg_dump` cannot recover to an
  arbitrary moment before a bad delete.
- Restore a backup to a scratch instance on a schedule and verify row counts. An untested
  backup routinely fails exactly when you need it.
- Put a connection pooler (**PgBouncer** in transaction mode, or the platform's pooler) in
  front. Size the pool to the database's capacity, not the number of app instances.
- Run at least one streaming replica and rehearse promotion/failover. A single node has an
  RTO equal to "restore from backup" — hours, not seconds.
- Set `statement_timeout`, `idle_in_transaction_session_timeout`, and `lock_timeout` so no
  single client can hold resources forever.
- Keep `fsync = on`, `full_page_writes = on`, and `synchronous_commit` set deliberately —
  turning these off trades durability for speed and can corrupt data on crash.
- Monitor replication lag, connection count, transaction ID age (wraparound), disk, and
  cache hit ratio, with alerts and defined thresholds.
- Roll out schema changes with online, non-blocking migrations and a tested rollback.

## Examples

**Good Example** — bounded resources and PITR-capable durability

```ini
# postgresql.conf — durability kept on; resources bounded.
fsync = on
full_page_writes = on
synchronous_commit = on                 # confirmed durable before COMMIT returns
archive_mode = on
archive_command = 'pgbackrest --stanza=main archive-push %p'  # WAL -> PITR
statement_timeout = '30s'               # no runaway query
idle_in_transaction_session_timeout = '60s'  # no lock held by a forgotten transaction
lock_timeout = '5s'
max_connections = 200                   # sized to hardware; apps go through PgBouncer
```

```bash
# Recoverability is proven, not assumed: restore into a throwaway instance and verify.
pgbackrest --stanza=main --type=time --target='2026-07-07 12:00:00' restore
psql -c "SELECT count(*) FROM invoice;"   # confirm the data actually came back
```

**Bad Example** — hope-based durability

```ini
# "It's faster this way." It is also how you lose committed data on a crash.
fsync = off                       # crash can corrupt the entire cluster
synchronous_commit = off          # COMMIT returns before WAL is durable -> silent loss
# no archive_mode -> no point-in-time recovery, only whatever nightly dump exists
# no statement_timeout -> one bad query pins connections until manual intervention
```

```bash
# The entire backup strategy: a nightly dump nobody has ever restored.
pg_dump mydb > /backups/nightly.sql   # untested; RPO is "up to 24h"; may not even restore
```

## Common Mistakes

- Treating `pg_dump` as a disaster-recovery plan; it gives no PITR and is rarely tested.
- Connecting hundreds of app workers directly to Postgres, exhausting `max_connections`.
- Disabling `fsync`/`synchronous_commit` for speed and losing committed transactions.
- Running a single node and discovering the RTO is "several hours" during the outage.
- No `idle_in_transaction_session_timeout`, so a hung client blocks vacuum and locks.
- Ignoring transaction ID wraparound until autovacuum falls behind and the DB refuses writes.

## Production Tips

- Document RPO/RTO explicitly and test that the backup and failover setup actually meets
  them — numbers on paper are not a guarantee.
- Keep backups in a different failure domain (separate account/region) from the primary.
- Alert on `age(datfrozenxid)` approaching the wraparound threshold; it is a silent,
  cluster-halting failure if ignored.
- Practice failover during business hours before you need it during an incident.

## AI Review Checklist

- Is there WAL archiving plus base backups enabling point-in-time recovery, not just dumps?
- Has a restore actually been performed and verified, not just configured?
- Do applications connect through a pooler rather than directly at scale?
- Are `statement_timeout`, `idle_in_transaction_session_timeout`, and `lock_timeout` set?
- Are `fsync`/`synchronous_commit` durability settings deliberate and documented?
- Is there a replica with a rehearsed failover, meeting the stated RTO?
- Is transaction-ID-age (wraparound) monitored and alerted?

## Related

- `knowledge/postgresql/13-high-availability.md`
- `knowledge/postgresql/14-backups.md`
- `knowledge/postgresql/17-monitoring.md`
- `knowledge/postgresql/12-replication.md`
- `knowledge/postgresql/98-production-checklist.md`
