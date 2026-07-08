---
id: linux/20-backups
topic: linux
slug: backups
title: "Backups"
type: doc
order: 20
status: ready
tags: [linux, backups]
related: [linux/11-storage, linux/14-cron, linux/17-security, linux/23-automation, linux/25-production]
when_to_use: "Read before designing, scripting, or reviewing any Linux backup or restore process."
---
# Backups

## Purpose

This document defines how to back up and — more importantly — restore data on Linux:
what to copy, how often, where to keep it, and how to prove it works. It is written so an
agent builds a backup that will actually recover data under pressure, not one that merely
runs and reports success.

A backup answers one question: "when this data is lost, can we get it back, intact, in
time?". If the restore has never been tested, the answer is no — regardless of how many
backups exist.

## Why It Matters

A backup that has never been restored is a hypothesis, not a safety net. The failure mode
is brutal and specific: the backup job runs green for months, then during a real incident
you discover the archive is truncated, the encryption key is gone, or the restore takes 30
hours you do not have. By then it is too late. Because the entire value of a backup is
realized only at restore time — the worst possible moment to find a bug — restores must be
tested continuously, not assumed.

## Core Principles

- **The restore is the product.** A backup only counts if a restore has been demonstrated
  to work. Test restores on a schedule, not after a disaster.
- **Follow 3-2-1.** Three copies, on two different media, with one off-site. A single copy
  on the same host is not a backup — it dies with the host.
- **Define RPO and RTO first.** Recovery Point Objective (how much data you can lose) and
  Recovery Time Objective (how long recovery may take) drive frequency and method. Design
  backwards from them.
- **Back up consistent state.** A file copied mid-write is corrupt. Use snapshots or
  database-native dumps to capture a coherent point in time.
- **Protect the backups themselves.** Encrypt at rest, and keep at least one copy that the
  production host cannot delete — or ransomware/`rm -rf` takes the backups too.

## Best Practices

- Automate backups with a scheduler (see [cron](14-cron.md) / systemd timers); manual
  backups get skipped exactly when they matter.
- Prefer incremental, deduplicated, encrypted tools — **restic** or **BorgBackup** — over
  hand-rolled `tar` + `scp`. They handle integrity, dedup, and encryption for you.
- Dump databases with their native tools (`pg_dump`, `mysqldump`, or a filesystem snapshot
  of a quiesced volume), never a raw file copy of live data files.
- Verify every backup after it is written: check the exit code AND run an integrity check
  (`restic check`, `borg check`). A zero exit does not mean the archive is readable.
- Enforce retention (e.g. keep 7 daily, 4 weekly, 12 monthly) so storage does not grow
  unbounded and old data expires predictably.
- Store credentials and encryption keys separately from the backups; a key lost with the
  server makes every encrypted backup useless.
- Alert on backup *absence*, not just failure — a job that silently stops running produces
  no error at all.

## Examples

**Good Example** — consistent dump, verified, off-host, scheduled

```bash
#!/usr/bin/env bash
set -euo pipefail                      # fail loudly; never back up half a job silently

export RESTIC_REPOSITORY="s3:s3.example.com/db-backups"
export RESTIC_PASSWORD_FILE=/etc/restic/key   # key lives off the backup target

# Dump a CONSISTENT snapshot via the DB's own tool, stream straight into restic.
pg_dump --format=custom app_production \
  | restic backup --stdin --stdin-filename app.dump

restic check --read-data-subset=5%    # actually verify the archive is readable
restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune
```

**Bad Example** — raw copy, no verify, same host, never restored

```bash
# Copies live database files while the DB is writing them -> corrupt, unrestorable.
tar czf /backups/db.tar.gz /var/lib/postgresql/data

# Same disk as production: one hardware failure loses data AND backup.
# No integrity check, no encryption, no off-site copy, and no restore has ever
# been attempted -- so nobody knows this archive cannot actually be restored.
```

## Common Mistakes

- Never testing a restore, so the first real recovery is also the first time it is tried.
- Keeping the only copy on the same host or disk as the source — not a backup, a mirror.
- Copying live database files instead of a consistent dump or snapshot, producing corrupt
  archives.
- Trusting the job's exit code alone without an integrity check of the archive.
- Storing the encryption key alongside the backups, so losing the server loses both.
- No retention policy, so the volume fills and new backups start failing silently.
- No alert when the job stops running, so a broken schedule goes unnoticed for months.

## Production Tips

- Run a scheduled automated restore into a scratch environment and assert on the result;
  this is the only real proof the pipeline works.
- Record and track actual restore time so you know whether you can still meet your RTO as
  data grows.
- Keep at least one immutable / append-only copy (object-lock, offline media) to survive
  ransomware and accidental deletion.
- Document the exact restore steps in a runbook; during an incident nobody should be
  reverse-engineering the backup tool.

## AI Review Checklist

- Has a restore actually been tested, and is it tested on a recurring schedule?
- Does the design satisfy 3-2-1 (three copies, two media, one off-site)?
- Are RPO and RTO defined, and does the frequency/method meet them?
- Are databases captured via native dump or snapshot, not raw file copy?
- Is each backup integrity-checked, not just exit-code-checked?
- Are backups encrypted, with the key stored separately from the archives?
- Is there an alert for a backup that stops running, not only for one that errors?

## Related

- `knowledge/linux/11-storage.md`
- `knowledge/linux/14-cron.md`
- `knowledge/linux/17-security.md`
- `knowledge/linux/23-automation.md`
- `knowledge/linux/25-production.md`
