---
id: databases/18-backup-and-recovery
topic: databases
slug: backup-and-recovery
title: "Backup And Recovery"
type: doc
order: 18
status: ready
tags: [databases, backup-and-recovery, pg_verifybackup, PostgreSQL, restore, schedule, readiness]
related: [databases/22-high-availability, databases/14-replication, databases/17-migrations, databases/19-security, databases/21-monitoring]
when_to_use: "Read before designing a backup schedule, running a restore, or reviewing disaster-recovery readiness for any datastore."
---
# Backup And Recovery

## Purpose

This document defines how to protect data against loss and how to get it back after a
failure: what to back up, how often, where to store it, and — most importantly — how to
restore it. It is written so an agent can design or review a backup strategy that
actually survives a disaster, not just one that produces files nobody has tried to read.

A backup you have never restored is not a backup; it is a hopeful guess. The goal is a
tested, timed, documented recovery path — not a cron job that writes a dump somewhere.

## Why It Matters

Data loss is one of the few failures a system may never recover from. A dropped table, a
buggy migration, a ransomware event, or a region outage can erase the business, not just
a request. Unlike a crashed process, lost data cannot be retried. Backups are the last
line of defense, and they fail silently: the dump job reports success for years while
writing corrupt or incomplete files, and you discover the truth only during the outage
when it is too late to fix. The cost of getting this wrong is unbounded, so backup and
recovery is held to a higher bar than ordinary operational code.

## Core Principles

- **Define RPO and RTO first, then design to them.** Recovery Point Objective is how much
  data you can afford to lose (backup frequency); Recovery Time Objective is how long you
  can afford to be down (restore speed). Every decision follows from these two numbers.
- **A backup is only real once you have restored it.** Test restores on a schedule; an
  untested backup has an unknown success rate, which is the same as no backup.
- **Store backups off the primary system and off-site.** A backup on the same disk, host,
  or account as the database dies with it. Follow 3-2-1: three copies, two media, one
  off-site.
- **Protect backups as strongly as the live data.** Encrypt at rest and in transit; a
  stolen backup leaks everything the database holds. See [security](19-security.md).
- **Prefer point-in-time recovery (PITR) for anything transactional.** Snapshots plus a
  continuous write-ahead/binary log let you restore to the second before a bad event.

## Best Practices

- Combine **periodic base backups** with **continuous log archiving** (WAL in PostgreSQL,
  binlog in MySQL) so you can replay to any moment, not just the last nightly dump.
- Use physical/snapshot backups for large databases (fast restore) and logical dumps for
  portability and single-table recovery. Know which each restore path needs.
- Automate backups and **automate verification**: after each backup, restore it to a
  throwaway instance and run integrity checks (row counts, checksums, `pg_verifybackup`).
- Set and enforce **retention** that matches legal/compliance needs; expire old backups so
  cost and blast radius stay bounded.
- Keep backups **immutable/versioned** (object-lock, WORM) so a compromised credential or
  ransomware cannot delete or overwrite your recovery path.
- Document a **runbook**: exact commands, credentials location, expected duration, and who
  to call. During an outage nobody should be improvising.
- Test restores against a **timed drill** at least quarterly and measure actual RTO — the
  number you rehearse is the only one you can promise.
- Replication is **not** a backup: it faithfully copies a `DELETE` or corruption to every
  replica. Keep independent backups alongside [replication](14-replication.md).

## Examples

**Good Example** — PITR-capable backup with verification

```bash
# PostgreSQL: base backup + continuous WAL archiving enables restore to any second.
# archive_command in postgresql.conf ships each WAL segment off-host:
#   archive_command = 'aws s3 cp %p s3://db-backups/wal/%f --sse aws:kms'

pg_basebackup \
  --pgdata=/backups/base-$(date +%F) \
  --wal-method=stream \
  --checkpoint=fast \
  --gzip --compress=9

# Verify immediately — a backup that fails pg_verifybackup is not a backup.
pg_verifybackup /backups/base-$(date +%F) || alert "base backup CORRUPT"

# Recovery drill (nightly, on a throwaway host): restore, replay WAL to a target time,
# and assert row counts. RTO is measured here, not guessed.
#   recovery_target_time = '2026-07-07 14:59:00'
```

**Bad Example** — an untested dump that will fail when it matters

```bash
# Nightly cron. Nobody has ever restored it. It has three fatal flaws.
pg_dump mydb > /var/lib/postgresql/backup.sql   # 1) same disk as the DB
                                                 # 2) overwrites last night's copy —
                                                 #    corruption becomes permanent
                                                 # 3) plaintext, unencrypted, no off-site
# No verification, no WAL, no retention. RPO = up to 24h; RTO = unknown.
# The first real restore is also the first test — during the outage.
```

## Common Mistakes

- Never testing a restore, so the backup's real success rate is unknown until an incident.
- Treating replicas or RAID as backups — they replicate deletes and corruption instantly.
- Storing backups on the same host, disk, or cloud account as the database.
- Overwriting the previous backup, so a corrupt run destroys the last good copy.
- Leaving backups unencrypted, turning a stolen archive into a total data breach.
- No continuous log archiving, so RPO is a full day even when the data changes constantly.
- Backing up the data but not the schema/roles/extensions needed to make it usable.
- No documented, timed runbook, so RTO balloons while engineers reverse-engineer the plan.

## Production Tips

- Alert on **backup age and size deltas**: a job that "succeeds" but produces a 0-byte or
  suddenly-smaller file is the classic silent failure. Monitor it like uptime.
- Track RPO/RTO as SLOs and review them after every drill and every real recovery.
- Keep at least one restore path that does not depend on the primary cloud provider's
  console being reachable — region and account outages happen.
- Rehearse the *human* path too: who has the keys, who is on call, how you communicate.

## AI Review Checklist

- Are RPO and RTO explicitly defined, and does the backup cadence meet the RPO?
- Is there continuous log archiving (WAL/binlog) for point-in-time recovery, not just dumps?
- Are backups stored off-host and off-site, and encrypted at rest and in transit?
- Is every backup automatically verified (restore + integrity check), not just written?
- Are backups immutable/versioned so ransomware or a bad credential cannot erase them?
- Is there a timed, documented restore runbook, and has it been drilled recently?
- Is replication being relied on as if it were a backup? (It is not.)

## Related

- `knowledge/databases/22-high-availability.md`
- `knowledge/databases/14-replication.md`
- `knowledge/databases/17-migrations.md`
- `knowledge/databases/19-security.md`
- `knowledge/databases/21-monitoring.md`
