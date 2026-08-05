---
id: postgresql/98-production-checklist
topic: postgresql
slug: production-checklist
title: "PostgreSQL Production Checklist"
type: doc
order: 98
status: ready
tags: [postgresql, production-checklist, scram-sha-256, pg_stat_statements, pg_basebackup, idle_in_transaction, trust, password]
related: [postgresql/14-backups, postgresql/12-replication, postgresql/17-monitoring, postgresql/18-security, postgresql/27-tuning]
when_to_use: "Read before promoting a PostgreSQL database to production or signing off a go-live."
---
# PostgreSQL Production Checklist

## Purpose

This is a verifiable, pre-flight checklist for taking a PostgreSQL database to
production. Each item is a yes/no you can confirm against the running system or its
configuration. If any box is unchecked, the database is not production-ready — treat an
unchecked box as a launch blocker until it is resolved or explicitly risk-accepted.

## Why It Matters

A database that "works in staging" fails in production for boring, preventable reasons:
no tested restore, a connection storm with no pooler, a replica that silently fell
behind, wraparound autovacuum that never ran. These are not exotic — they are the
default outcome of skipping the checklist. The cost of each item here is minutes; the
cost of discovering it during an outage is measured in data loss and downtime.

## Backups and Recovery

**Rules:** [Backups](14-backups.md)

- [ ] Automated base backups run on a schedule (`pg_basebackup` or a tool like pgBackRest/Barman).
- [ ] WAL archiving is enabled (`archive_mode = on`) for point-in-time recovery.
- [ ] A full restore has been **performed** into a scratch environment, not just configured.
- [ ] Recovery Point Objective (RPO) and Recovery Time Objective (RTO) are documented and met.
- [ ] Backups are stored off-host and encrypted at rest.
- [ ] Backup jobs alert on failure (a silently failing backup is worse than none).

## High Availability and Replication

**Rules:** [High Availability](13-high-availability.md) · [Replication](12-replication.md)

- [ ] At least one streaming replica exists ([replication](12-replication.md)).
- [ ] Replication lag is monitored with an alert threshold.
- [ ] Automatic failover is configured and has been tested (Patroni, repmgr, or managed equivalent).
- [ ] `synchronous_commit` is set to the level the durability requirement demands.
- [ ] Client connection string uses the failover endpoint, not a single node's IP.

## Configuration and Capacity

**Rules:** [Configuration](02-configuration.md) · [Tuning](27-tuning.md)

- [ ] `shared_buffers`, `work_mem`, and `effective_cache_size` are tuned to the host, not defaults ([tuning](27-tuning.md)).
- [ ] `max_connections` is set below what the hardware supports, with a pooler (PgBouncer) in front.
- [ ] `statement_timeout` and `idle_in_transaction_session_timeout` are set to cap runaway sessions.
- [ ] `lock_timeout` is set for migration/DDL sessions.
- [ ] Autovacuum is enabled and tuned for high-churn tables ([vacuum](20-vacuum.md)).
- [ ] Transaction-ID wraparound headroom is monitored (`age(datfrozenxid)`).

## Security

**Rules:** [Security](18-security.md) · [Roles And Permissions](19-roles-and-permissions.md)

- [ ] `pg_hba.conf` requires `scram-sha-256`; no `trust` or `password` (cleartext) rules ([security](18-security.md)).
- [ ] TLS is enforced for all client connections (`ssl = on`, clients require it).
- [ ] The application connects as a least-privilege role, never `postgres`/superuser ([roles](19-roles-and-permissions.md)).
- [ ] Default and unused roles have no login or have been removed.
- [ ] Secrets (passwords, connection strings) live in a secrets manager, not in code or images.
- [ ] Row-level security is enabled where multi-tenant isolation depends on it.

## Observability

**Rules:** [Monitoring](17-monitoring.md) · [Vacuum](20-vacuum.md)

- [ ] `log_min_duration_statement` is set to capture slow queries ([monitoring](17-monitoring.md)).
- [ ] `pg_stat_statements` is enabled for query-level metrics.
- [ ] Metrics (connections, cache hit ratio, lag, deadlocks, bloat) feed a dashboard and alerts.
- [ ] Logs are shipped off-host and retained per policy.
- [ ] Alerts exist for disk-space-remaining, replication lag, and connection saturation.

## Schema and Migrations

**Rules:** [Migrations](22-migrations.md) · [Data Types](03-data-types.md)

- [ ] All migrations are forward-only, version-controlled, and tested against a prod-sized copy ([migrations](22-migrations.md)).
- [ ] Index creation on live tables uses `CREATE INDEX CONCURRENTLY`.
- [ ] Every foreign key column is indexed.
- [ ] `ANALYZE` runs after any bulk data load so the planner has fresh statistics.
- [ ] No migration takes a long-held `ACCESS EXCLUSIVE` lock on a hot table.

## AI Review Checklist

- Has a restore actually been executed, or only a backup configured?
- Is there a tested failover path, or a single point of failure?
- Are timeouts (`statement`, `idle_in_transaction`, `lock`) all set?
- Does the app connect as a least-privilege role over TLS with `scram-sha-256`?
- Are slow-query logging, `pg_stat_statements`, and lag/disk alerts all live?

## Related

- `knowledge/postgresql/14-backups.md`
- `knowledge/postgresql/12-replication.md`
- `knowledge/postgresql/17-monitoring.md`
- `knowledge/postgresql/18-security.md`
- `knowledge/postgresql/27-tuning.md`
