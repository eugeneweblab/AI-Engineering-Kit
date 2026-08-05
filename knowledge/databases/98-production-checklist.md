---
id: databases/98-production-checklist
topic: databases
slug: production-checklist
title: "Database Production Checklist"
type: doc
order: 98
status: ready
tags: [databases, production-checklist, EXPLAIN, decimal, timestamptz, numeric, float, OFFSET]
related: [databases/18-backup-and-recovery, databases/14-replication, databases/21-monitoring, databases/19-security, databases/17-migrations]
when_to_use: "Read before promoting any database or data-access change to production, and during launch readiness reviews."
---
# Database Production Checklist

## Purpose

A concrete, verifiable checklist to run before a database goes live or before a
data-touching change ships. Every item is a yes/no you can actually confirm — not a
principle to interpret. If an item cannot be checked "yes", it is a launch blocker until
justified in writing. Pair this with the reasoning in
[engineering principles](30-engineering-principles.md).

## Why It Matters

Most database incidents are not exotic — they are a missing backup test, an unindexed hot
query, credentials in a config file, or a migration that locked a table at peak traffic.
These are all preventable by a checklist. Running one turns "we think it's fine" into
"we verified it", before real users and irreversible data are on the line.

## Schema and Integrity

**Rules:** [Schema Design](06-schema-design.md) · [Data Integrity](23-data-integrity.md)

- [ ] Every foreign key relationship has an actual `FOREIGN KEY` constraint with a defined
  `ON DELETE` / `ON UPDATE` action.
- [ ] `NOT NULL`, `UNIQUE`, and `CHECK` constraints encode the real business invariants.
- [ ] Money uses `numeric`/`decimal` (never `float`); timestamps use `timestamptz`.
- [ ] Primary keys are defined and stable; no table relies on implicit row order.
- [ ] Text columns that need it have a length/format constraint, not unbounded free text.

## Migrations

**Rules:** [Migrations](17-migrations.md)

- [ ] Every schema change ships as a version-controlled, reviewed migration — no manual DDL.
- [ ] Each migration has a tested rollback (or a documented forward-only recovery plan).
- [ ] Migrations are backward-compatible with the currently running app version
  (expand/contract, not breaking rename in one step).
- [ ] Index creation on large tables uses the concurrent/online path so it does not lock
  writes.
- [ ] Migrations were rehearsed against a production-scale data copy, and their runtime is
  known.

## Performance and Indexing

**Rules:** [Indexing](07-indexing.md) · [Performance](20-performance.md)

- [ ] Every query on the hot path has been checked with `EXPLAIN`/`EXPLAIN ANALYZE` — no
  unexpected sequential scans on large tables.
- [ ] Indexes exist for the columns real queries filter, join, and sort on.
- [ ] Large-result endpoints use keyset pagination, not deep `OFFSET`.
- [ ] Connection pooling is configured with a bounded max that the database can sustain.
- [ ] A statement timeout is set so a runaway query cannot hold resources indefinitely.
- [ ] The system was load-tested at expected peak with production-scale data volumes.

## Availability and Recovery

**Rules:** [High Availability](22-high-availability.md) · [Backup And Recovery](18-backup-and-recovery.md)

- [ ] Automated backups run on a schedule, and a restore has actually been performed and
  verified — an untested backup does not count.
- [ ] RPO (max data loss) and RTO (max downtime) targets are defined and met by the backup
  and replication setup.
- [ ] Replication and failover are configured, and failover has been rehearsed.
- [ ] Point-in-time recovery is available for the retention window the business requires.
- [ ] Backups are stored off the primary host/region and are encrypted at rest.

## Security

**Rules:** [Security](19-security.md)

- [ ] Connections require TLS; the database is not reachable from the public internet.
- [ ] The application connects with a least-privilege account — not a superuser/admin role.
- [ ] Credentials come from a secrets manager, not source code or committed config.
- [ ] Data at rest is encrypted; PII/sensitive columns have a documented handling policy.
- [ ] All access is parameterized; no dynamic SQL is built from untrusted input.

## Observability

**Rules:** [Monitoring](21-monitoring.md)

- [ ] Key metrics are collected and alerted on: connections, replication lag, error rate,
  p99 latency, disk usage.
- [ ] Slow-query logging is enabled with a sane threshold.
- [ ] Disk-full and replication-lag alerts fire before they become an outage.
- [ ] There is a dashboard and an owner for on-call to act on database alerts.

## AI Review Checklist

- Does the change add or alter any invariant that should be a database constraint?
- Is any new query verified with `EXPLAIN` and backed by an appropriate index?
- Is the migration reversible and backward-compatible with the running app?
- Does anything in the diff introduce string-built SQL or a broad-privilege connection?
- Would this change alter backup, replication, or recovery guarantees without an update to them?

## Related

- `knowledge/databases/18-backup-and-recovery.md`
- `knowledge/databases/14-replication.md`
- `knowledge/databases/21-monitoring.md`
- `knowledge/databases/19-security.md`
- `knowledge/databases/17-migrations.md`
