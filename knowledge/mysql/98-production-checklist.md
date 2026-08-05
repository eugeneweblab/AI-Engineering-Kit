---
id: mysql/98-production-checklist
topic: mysql
slug: production-checklist
title: "MySQL Production Checklist"
type: doc
order: 98
status: ready
tags: [mysql, production-checklist]
related: [mysql/20-production, mysql/11-backups, mysql/09-replication, mysql/15-monitoring, mysql/12-security]
when_to_use: "Read before promoting a MySQL instance or schema change to production, or during a go-live review."
---
# MySQL Production Checklist

## Purpose

This is a verifiable, grouped checklist for taking a MySQL database to production and
keeping it there. Each item is a yes/no an agent or reviewer can confirm against the actual
configuration, not a guideline to interpret. If any box is unchecked, the system is not
production-ready.

## Why It Matters

Databases fail quietly and expensively. An unverified backup, a missing index, or a default
`sql_mode` will not fail in testing — it fails once, in production, with real customer data.
This checklist front-loads those failures into a review you can run before the pager goes
off. Treat unchecked items as blocking defects, not future work.

## Configuration and Engine

**Rules:** [Configuration](02-configuration.md) · [Storage Engines](08-storage-engines.md)

- [ ] All tables use the `InnoDB` storage engine (no MyISAM in the write path).
- [ ] Server, tables, and client connections all use `utf8mb4` character set.
- [ ] `sql_mode` includes `STRICT_TRANS_TABLES` (bad data errors instead of truncating).
- [ ] `innodb_buffer_pool_size` is set to ~60-75% of RAM on a dedicated DB host.
- [ ] `innodb_flush_log_at_trx_commit = 1` for durability (or a documented, accepted trade-off).
- [ ] `max_connections` is sized to load and a connection pool caps app-side connections.
- [ ] Time zone tables are loaded and the server runs in UTC.

## Schema and Indexes

**Rules:** [Data Types](03-data-types.md) · [Indexes](04-indexes.md)

- [ ] Every table has an explicit, compact primary key.
- [ ] Every hot query has a supporting index, verified with `EXPLAIN` (no `type: ALL` on large tables).
- [ ] Foreign keys are declared with an explicit `ON DELETE` / `ON UPDATE` action.
- [ ] No redundant or unused indexes (checked via `sys.schema_unused_indexes`).
- [ ] Money is stored as `DECIMAL` or integer minor units, never `FLOAT`/`DOUBLE`.

## Backups and Recovery

**Rules:** [Backups](11-backups.md)

- [ ] Automated backups run on a schedule and are stored off-host.
- [ ] A restore has been tested end-to-end within the last 30 days (an untested backup does not exist).
- [ ] Point-in-time recovery is possible (binary logs retained to cover the RPO).
- [ ] Documented RPO and RTO exist and the backup cadence meets them.
- [ ] Backups are encrypted at rest and access is restricted.

## Replication and High Availability

**Rules:** [Replication](09-replication.md) · [High Availability](21-high-availability.md)

- [ ] Replication topology is defined with at least one replica for failover/reads.
- [ ] Replica lag is monitored and alerts fire above the acceptable threshold.
- [ ] A tested failover/promotion procedure exists (manual or automated via Orchestrator/Group Replication).
- [ ] `GTID` mode is enabled for consistent, resumable replication.

## Security

**Rules:** [Security](12-security.md) · [Users And Roles](13-users-and-roles.md)

- [ ] Connections require TLS; plaintext is rejected.
- [ ] No application uses the `root` account; each app has a least-privilege user.
- [ ] No account has a blank password or a wildcard host it does not need.
- [ ] Secrets (DB passwords) come from a secrets manager, not source or config files.
- [ ] The database is not reachable from the public internet (network/security-group locked down).

## Observability

**Rules:** [Monitoring](15-monitoring.md)

- [ ] The slow query log is enabled with a defined `long_query_time` threshold.
- [ ] Metrics (connections, buffer pool hit rate, replication lag, QPS, errors) ship to a dashboard.
- [ ] Alerts exist for disk space, replication lag, connection saturation, and lock waits.
- [ ] `performance_schema` is enabled for query-level diagnosis.

## Deployment and Migrations

**Rules:** [Production](20-production.md) · [Migrations](16-migrations.md)

- [ ] Schema migrations run online (`gh-ost`, `pt-online-schema-change`, or `LOCK=NONE`) on large tables.
- [ ] Migrations are forward/backward compatible for rolling app deploys.
- [ ] Every migration has a tested rollback path.
- [ ] Disk headroom exists for the migration's temporary copy (online tools double table size).

## Capacity

**Rules:** [Performance](14-performance.md) · [Partitioning](22-partitioning.md)

- [ ] Disk usage and growth rate are tracked with a projected exhaustion date.
- [ ] Connection pool sizing has been load-tested against `max_connections`.
- [ ] The largest tables have a partitioning or archival plan before they become unmanageable.

## AI Review Checklist

- [ ] Have all boxes above been verified against the real running configuration, not assumed?
- [ ] Is there a tested restore, not merely a scheduled backup?
- [ ] Does every production query have an `EXPLAIN`-verified index?
- [ ] Are failover and rollback procedures documented and tested, not theoretical?

## Related

- `knowledge/mysql/20-production.md`
- `knowledge/mysql/11-backups.md`
- `knowledge/mysql/09-replication.md`
- `knowledge/mysql/15-monitoring.md`
- `knowledge/mysql/12-security.md`
