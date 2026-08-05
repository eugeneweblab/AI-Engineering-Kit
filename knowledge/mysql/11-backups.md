---
id: mysql/11-backups
topic: mysql
slug: backups
title: "MySQL Backups"
type: doc
order: 11
status: ready
tags: [mysql, backups, InnoDB, position, mysqlpump, binlog_expire_logs_seconds, mydumper]
related: [mysql/09-replication, mysql/06-transactions, mysql/20-production, mysql/08-storage-engines]
when_to_use: "Read before setting up a backup job, planning disaster recovery, or reviewing an existing backup strategy."
---
# MySQL Backups

## Purpose

This document defines how to back up MySQL so you can actually recover: consistent
snapshots, binary-log-based point-in-time recovery (PITR), and verified restores. It is
written so an agent builds a backup strategy that meets a stated **RPO** (how much data you
can lose) and **RTO** (how fast you must be back), not just a cron job that produces files
nobody has ever restored.

Backups are the safety net that [replication](09-replication.md) and
[clustering](10-clustering.md) do *not* provide — those replicate mistakes, they do not
undo them. A backup is only real once you have restored it.

## Why It Matters

Backups are the difference between a bad day and a company-ending one. The universal
failure is not "we had no backups" — it is "we had backups that could not be restored":
inconsistent dumps taken without a transaction, missing binary logs so PITR stops at
midnight, an encryption key nobody kept, or a restore procedure never tested until the
outage. Every one of these looks fine until you need it. Because the cost of a bad backup
is total and only revealed at the worst moment, backups are held to the same bar as
authentication: assume it will fail, and prove it will not.

## Core Principles

- **A backup you have not restored does not exist.** Test restores on a schedule; an
  untested backup is a hope, not a plan.
- **State an RPO and RTO, then design to them.** "Back up nightly" is meaningless without
  knowing you can lose up to 24 hours and take N hours to restore.
- **Full backup + binary logs = point-in-time recovery.** A periodic full snapshot plus
  continuously archived binlogs lets you restore to any second, not just backup time.
- **Backups must be consistent.** Use a single transaction or a hot-backup tool so the
  snapshot is a coherent point in time, not a smear across ongoing writes.
- **Store backups off-host and encrypted.** A backup on the same server (or unencrypted in
  a bucket) fails the exact disaster it exists for.

## Best Practices

- Use **Percona XtraBackup** (or MySQL Enterprise Backup) for physical, non-blocking hot
  backups of large InnoDB datasets; it copies data files while the server runs and captures
  the LSN for consistency.
- Use `mysqldump --single-transaction --source-data=2` (or `mysqlpump`/`mydumper`) for
  logical backups of small/medium InnoDB databases; the single transaction gives a
  consistent snapshot without locking writers. Never omit `--single-transaction` on InnoDB.
- Enable and **archive the binary logs** continuously, and record the binlog position/GTID
  in each backup, so you can replay from the snapshot up to the moment before an incident.
- Set `log_bin` retention (`binlog_expire_logs_seconds`) long enough to cover the window
  between two full backups; if binlogs expire first, your PITR chain is broken.
- Take backups from a **dedicated replica** to keep load off the primary, but confirm the
  replica is caught up when the backup starts.
- Encrypt backups at rest and in transit; store the keys in a secrets manager separate from
  the backups themselves.
- Automate **restore verification**: periodically restore the latest backup into a scratch
  instance, replay binlogs, and run a consistency check. Alert if it fails.
- Keep the 3-2-1 rule: 3 copies, 2 media/locations, 1 off-site.

## Examples

**Good Example** — consistent logical backup with a PITR anchor

```bash
# --single-transaction wraps the dump in one InnoDB transaction, so the snapshot
# is a consistent point in time without locking writers. --source-data=2 records
# the binlog file+position (as a comment) so PITR can replay from exactly here.
mysqldump --single-transaction --source-data=2 --routines --events \
  --databases app_production | gzip > backup-$(date +%F).sql.gz

# Later: restore the snapshot, then replay binlogs up to just before the mistake.
gunzip -c backup-2026-07-07.sql.gz | mysql
mysqlbinlog --stop-datetime="2026-07-07 14:29:00" mysql-bin.000042 | mysql
```

**Bad Example** — inconsistent dump, no PITR, never restored

```bash
# No --single-transaction on InnoDB: the dump is a smear across concurrent writes,
# so foreign-key relationships can be internally inconsistent. No binlog position
# is captured, so you can only ever restore to "whenever this ran" — losing every
# write since. And nobody has ever restored it, so it may not even load.
mysqldump --databases app_production > backup.sql   # hope for the best
```

## Common Mistakes

- Omitting `--single-transaction`, producing an inconsistent InnoDB dump that violates its
  own foreign keys on restore.
- Backing up the data but not archiving binary logs, so recovery can only reach the last
  full backup — an RPO of hours or a day, discovered too late.
- Storing backups on the same host or volume as the database, so a disk/host failure takes
  both.
- Never testing a restore; the first real restore is the first time anyone learns it does
  not work.
- Letting binary logs expire faster than the backup interval, silently breaking the PITR
  chain.
- Backing up from a lagging replica and capturing a snapshot older than believed.
- Losing or co-locating the encryption key, making an otherwise-good backup unreadable.

## Production Tips

- Document and rehearse the full restore runbook (RTO includes the time to *find and follow*
  the procedure under stress). A DR drill each quarter is cheap insurance.
- Monitor backup success/failure and size trends; a backup that silently shrank is often a
  backup that silently broke.
- For very large datasets, snapshot at the storage/volume layer (with an InnoDB-consistent
  flush) to hit RTO targets that a logical restore cannot meet.

## AI Review Checklist

- Are stated RPO and RTO targets, and does the strategy demonstrably meet them?
- Are InnoDB backups consistent (`--single-transaction` or a hot-backup tool)?
- Are binary logs archived continuously, with each backup recording its binlog/GTID position?
- Is binlog retention long enough to bridge two full backups (PITR chain intact)?
- Are backups stored off-host, encrypted, with keys kept separately?
- Is restore verification automated and alerted, and has a full DR restore been rehearsed?

## Related

- `knowledge/mysql/09-replication.md`
- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/20-production.md`
- `knowledge/mysql/08-storage-engines.md`
