---
id: postgresql/14-backups
topic: postgresql
slug: backups
title: "PostgreSQL Backups"
type: doc
order: 14
status: ready
tags: [postgresql, backups, pg_verifybackup, backup, pg_basebackup, postgresql.conf, pg_dump]
related: [postgresql/12-replication, postgresql/13-high-availability, postgresql/22-migrations, postgresql/26-production]
when_to_use: "Read before designing a backup strategy, choosing pg_dump vs physical backups, or setting up point-in-time recovery."
---
# PostgreSQL Backups

## Purpose

This document defines how to make PostgreSQL backups you can actually restore: logical
dumps, physical base backups, WAL archiving, and point-in-time recovery (PITR). It is
written so an agent can design or review a backup strategy that survives disk loss,
region loss, and — critically — human error like a bad migration or an unqualified
`DELETE`.

Backups are not [replication](12-replication.md) and not [HA](13-high-availability.md).
Replication copies mistakes instantly to every replica; only a backup lets you go *back
in time*. A system with replicas and no backups is one bad `UPDATE` away from permanent
data loss.

## Why It Matters

A backup that has never been restored is a hope, not a backup. The recurring disaster is
discovering — during an incident, under pressure — that the dumps are corrupt, the WAL
archive has a gap, or nobody knows the restore procedure. The stakes are absolute: a
failed restore is unrecoverable data loss, often of the entire business's records.
Because the cost of getting this wrong is total and the failure surfaces only when you
need it most, backups are validated by *restoring*, on a schedule, not by checking that
a job exited zero.

## Core Principles

- **A backup is defined by a successful restore.** If you have not restored it, you do
  not have a backup. Test restores are the deliverable, not the dump file.
- **RPO and RTO drive the design.** How much data you can lose (RPO) and how long a
  restore may take (RTO) decide dump-vs-physical and how often you archive WAL. Set them
  before choosing tools.
- **Logical and physical serve different jobs.** `pg_dump` is portable, per-object,
  cross-version, and slow to restore at scale. Physical base backup + WAL is fast to
  restore and enables PITR, but is same-major-version and whole-cluster.
- **PITR is your defense against human error.** Continuous WAL archiving lets you restore
  to the second *before* a destructive statement — something no replica can do.
- **Backups must survive the thing that killed prod.** Store them off-host and
  off-region, encrypted, with immutability/retention locks so ransomware or a rogue
  credential cannot delete them.

## Best Practices

- Use a purpose-built tool — **pgBackRest** (preferred) or **barman** — rather than
  hand-rolled scripts. They handle WAL archiving, compression, encryption, retention,
  parallelism, and verification correctly.
- Keep **continuous WAL archiving** on for any database where losing more than a dump
  interval is unacceptable; that is what enables PITR.
- Run periodic **full** base backups plus **incremental/differential** backups to bound
  restore time and storage; PostgreSQL 17+ supports native incremental base backups via
  `pg_basebackup --incremental`.
- Store backups in at least **two locations, one off-region**, encrypted at rest, with
  object-lock/immutability so they cannot be deleted within the retention window.
- **Test-restore on a schedule** (weekly or monthly) into a scratch environment and run a
  data sanity check; verify PITR to an arbitrary timestamp, not just "latest".
- Verify backup integrity automatically (`pgbackrest verify`, or `pg_verifybackup` for
  `pg_basebackup` output) so corruption is caught before you need the backup.
- Keep a written, tested **restore runbook** with concrete commands and expected RTO; the
  restore must not depend on one person's memory.
- Match retention to real requirements (regulatory, business) and prune automatically —
  infinite retention is cost, not safety.

## Examples

**Good Example** — physical backup with WAL archiving enabling PITR

```ini
# postgresql.conf — stream every WAL segment to durable, off-host storage.
archive_mode = on
archive_command = 'pgbackrest --stanza=main archive-push %p'  # tool handles retries/compression/encryption
wal_level = replica
```

```bash
# Nightly incremental backup (fast, small); weekly full bounds restore chain length.
pgbackrest --stanza=main --type=incr backup

# Disaster recovery: restore to the instant BEFORE a bad DELETE at 14:32:07.
pgbackrest --stanza=main \
  --type=time --target='2026-07-07 14:32:06+00' \
  --delta restore     # replays WAL up to the target, recovering the deleted rows
# A replica could never do this — the DELETE had already replicated everywhere.
```

**Bad Example** — a cron dump nobody restores

```bash
#!/bin/sh
# "We have backups." Do we?
pg_dump mydb | gzip > /backup/mydb.sql.gz   # same host as the DB -> disk loss kills both
# - No off-host/off-region copy: one failed disk loses DB and backup together.
# - No WAL archiving: RPO is a full day; no PITR, cannot undo a mid-day mistake.
# - Overwrites yesterday's file: a silently corrupt dump destroys the only good copy.
# - Never restored: the first restore attempt is during the outage.
```

## Common Mistakes

- Calling a job "backup" because it exits zero, without ever restoring it.
- Storing backups on the same host, disk, or region as the database.
- No WAL archiving, so the best you can do is restore to last night — no PITR.
- Overwriting the previous backup, so one corrupt run leaves you with nothing.
- Unencrypted backups, or backups a compromised app credential can delete
  (no immutability).
- Assuming replicas or HA remove the need for backups — they replicate mistakes, they do
  not reverse them.
- Retention so short that a slow-to-notice corruption is already past the oldest backup.
- Backing up the database but not roles, extensions, and `postgresql.conf` needed to
  rebuild the cluster.

## Production Tips

- Alert on backup **freshness and WAL-archive continuity**, not just job success — a
  silent gap in the WAL archive breaks PITR across that window.
- Record the actual measured RTO from your last test-restore; if it exceeds the SLO,
  switch to physical/incremental or restore-into-a-standby strategies.
- For very large databases, keep a delayed standby (`recovery_min_apply_delay`) as a
  fast "undo" for recent human error, alongside real backups.
- Snapshot-based backups (cloud volume snapshots) are valid only if they are
  crash-consistent or paired with WAL — a naked filesystem copy of a running cluster is
  not restorable.

## AI Review Checklist

- Is there a documented RPO and RTO, and does the strategy meet both?
- Are backups stored off-host and off-region, encrypted, with immutability/retention
  locks?
- Is continuous WAL archiving enabled where PITR is required?
- Are restores tested on a schedule, including PITR to an arbitrary timestamp?
- Is backup integrity verified automatically (verify / `pg_verifybackup`)?
- Is there a written, tested restore runbook with an expected RTO?
- Are roles, extensions, and config captured, not just table data?

## Related

- `knowledge/postgresql/12-replication.md`
- `knowledge/postgresql/13-high-availability.md`
- `knowledge/postgresql/22-migrations.md`
- `knowledge/postgresql/26-production.md`
