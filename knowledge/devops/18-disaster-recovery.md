---
id: devops/18-disaster-recovery
topic: devops
slug: disaster-recovery
title: "Disaster Recovery"
type: doc
order: 18
status: ready
tags: [devops, disaster-recovery]
related: [devops/19-high-availability, devops/25-incident-management, devops/27-sre-principles, devops/12-monitoring]
when_to_use: "Read before designing backups, restore procedures, or a recovery plan for any stateful system."
---
# Disaster Recovery

## Purpose

This document defines how a system survives a catastrophic loss — a deleted database,
a corrupted volume, a failed region, a ransomware event — and comes back within a
known, agreed time. It is written so an agent can design, implement, or review a
disaster recovery (DR) plan without shipping backups that cannot actually be restored.

Disaster recovery answers "how do we get back to a working state after data or
infrastructure is lost?". It is distinct from [high availability](19-high-availability.md),
which keeps the system running through *localized* failures. HA prevents outages; DR
recovers from disasters HA cannot absorb. You need both.

## Why It Matters

Backups fail silently. A cron job that "succeeds" for two years can be writing empty
files, encrypting to a lost key, or replicating the corruption it was meant to protect
against. You discover this only during the restore — the worst possible moment. The
difference between a scary afternoon and a company-ending event is whether recovery was
*tested*, not whether backups *exist*. Untested backups are not backups; they are hope.

## Core Principles

- **Define RPO and RTO first, then design to them.** RPO (Recovery Point Objective) is
  how much data you can afford to lose; RTO (Recovery Time Objective) is how long you can
  be down. Every DR decision is a trade-off against these two numbers and their cost.
- **A backup you have not restored does not exist.** Only a completed, verified restore
  proves the backup works. Test restores on a schedule, not after the disaster.
- **Isolate backups from the thing they protect.** Store them in a separate account,
  region, and credential scope so one compromise cannot delete both live data and backups.
- **Automate recovery, do not document it.** A runbook a stressed on-call must execute by
  hand at 3am will fail. Script it; the runbook should mostly be "run this."
- **Assume the disaster takes the humans too.** The person who knows the plan may be
  unreachable. The plan must work when executed by someone who has never run it.

## Best Practices

- Follow **3-2-1**: three copies of data, on two media/storage types, one off-site (a
  different region or provider). One copy must be logically isolated from production
  credentials.
- Make at least one backup **immutable / write-once** (object-lock, WORM) so ransomware
  or a rogue delete cannot destroy it. The cost is you cannot prune it early.
- **Encrypt backups** and store the keys in a secrets manager separate from the backup
  store. Test that you can decrypt — a lost key makes the backup worthless.
- Run **automated restore drills** (weekly to quarterly by tier) into a clean environment,
  and assert on the restored data, not just exit code 0.
- Keep **point-in-time recovery** for databases (WAL/binlog archiving) so RPO is minutes,
  not the age of the last full dump.
- Track **backup freshness and size** as monitored metrics; alert when a backup is missing,
  stale, or anomalously small. A silent gap is the common failure.
- Write a **runbook with concrete commands, credentials location, and escalation paths**,
  and record the last date each step was actually exercised.
- Replicate to a **second region** for anything with a region-level RTO; single-region
  backups do not survive a region outage.

## Examples

**Good Example** — verified, isolated, monitored restore drill

```bash
#!/usr/bin/env bash
set -euo pipefail  # fail fast; a partial restore that "passes" is worse than no restore

# Pull the latest immutable snapshot from an isolated, object-locked bucket.
snapshot=$(aws s3api list-objects-v2 --bucket dr-backups-isolated \
  --query 'sort_by(Contents,&LastModified)[-1].Key' --output text)

# Restore into a THROWAWAY database, never into production.
pg_restore --clean --if-exists --dbname="$RESTORE_TARGET" "/tmp/${snapshot}"

# Assert the restore is real: row counts and a business invariant, not just exit code.
rows=$(psql "$RESTORE_TARGET" -tAc "SELECT count(*) FROM orders")
[ "$rows" -gt 0 ] || { echo "RESTORE INVALID: orders empty"; exit 1; }

# Emit freshness + success so monitoring can alert if this drill stops running.
curl -s "$PUSHGATEWAY/metrics/job/dr_drill" \
  --data-binary "dr_restore_rows ${rows}"
```

**Bad Example** — a backup nobody has ever restored

```bash
# Runs nightly, "succeeds" nightly, has never been restored once.
pg_dump mydb > /backups/db.sql          # same host as prod: one disk loss kills both
gzip -f /backups/db.sql                 # overwrites yesterday: no history, no PITR
# No encryption, no off-site copy, no immutability, no restore test.
# Exit code 0 tells you nothing about whether the file is usable.
```

## Common Mistakes

- Measuring success by "backup completed" instead of "restore verified."
- Storing backups in the same account/region/credentials as production data.
- No point-in-time recovery, so RPO is silently 24 hours instead of minutes.
- Overwriting backups in place, leaving no history to recover from corruption.
- Encrypting backups with a key that lives only in the system being backed up.
- A runbook full of prose and tribal knowledge instead of runnable commands.
- Never testing a full region failover, then discovering DNS/TLS/secret gaps live.

## Production Tips

- Record **restore time** during drills and compare it to your RTO — RTO is a promise you
  must be able to keep, not a hope.
- Keep a **dependency-ordered recovery plan**: databases before app tier, secrets before
  services, DNS last. Recovering services before their data just fails louder.
- Rehearse a **full game-day** (declare a region gone) at least annually with the real
  on-call rotation, including comms and decision-making, not just the technical steps.

## AI Review Checklist

- Are RPO and RTO explicitly defined, and does the design provably meet them?
- Is there a tested, automated restore that asserts on data, not just exit status?
- Are backups off-site, encrypted, and at least one copy immutable?
- Are backup keys stored separately from the backup store?
- Is backup freshness/size monitored with alerting on gaps?
- Does the runbook contain runnable commands and a recorded last-tested date?
- Has a full region-level failover been exercised, not just single-service restore?

## Related

- `knowledge/devops/19-high-availability.md`
- `knowledge/devops/25-incident-management.md`
- `knowledge/devops/27-sre-principles.md`
- `knowledge/devops/12-monitoring.md`
- `knowledge/devops/17-secrets-management.md`
