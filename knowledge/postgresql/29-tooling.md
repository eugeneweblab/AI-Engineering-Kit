---
id: postgresql/29-tooling
topic: postgresql
slug: tooling
title: "PostgreSQL Tooling"
type: doc
order: 29
status: ready
tags: [postgresql, tooling]
related: [postgresql/22-migrations, postgresql/17-monitoring, postgresql/14-backups, postgresql/23-testing, postgresql/24-debugging]
when_to_use: "Read before choosing tools for migrations, backups, monitoring, connection pooling, or local PostgreSQL development."
---
# PostgreSQL Tooling

## Purpose

This document defines the tools that belong in a PostgreSQL workflow and, more
importantly, the job each one does: migrations, pooling, backup, monitoring, and local
development. It is written so an agent picks a purpose-built tool instead of scripting a
fragile substitute.

The default answer to most Postgres operational needs is a mature, boring tool that
already handles the edge cases. This document names the categories and the trade-offs, not
a single mandated stack.

## Why It Matters

Hand-rolled scripts for backups, migrations, and pooling fail in exactly the situations
they exist for: the backup script that never handled WAL, the migration runner with no
locking that two deploys run at once, the homemade pool that leaks connections under load.
The mature tools encode years of edge cases — partial failures, retries, concurrency,
recovery — that a bespoke script rediscovers the hard way in production. Choosing the right
tool is a correctness decision, not a convenience one.

## Core Principles

- **Use a migration tool with ordered, versioned, transactional migrations.** Ad-hoc SQL
  applied by hand drifts across environments and cannot be audited or rolled back.
- **Pool connections with a dedicated pooler.** A pooler (PgBouncer) is infrastructure, not
  something to reimplement inside the app.
- **Back up with a PITR-capable tool, not a cron'd `pg_dump`.** Recovery requirements
  dictate the tool; dumps cannot do point-in-time recovery.
- **Make local Postgres match production's major version.** Version-specific planner and
  syntax differences cause "works on my machine" bugs otherwise.
- **Prefer the standard client (`psql`) and catalog views for diagnosis.** They are always
  present, scriptable, and match the server exactly.

## Best Practices

- Adopt one migration tool (Flyway, Liquibase, Alembic, golang-migrate, or an ORM's runner)
  and check migrations into version control. It must record applied versions and take a
  lock so concurrent deploys cannot double-apply.
- Run PgBouncer in transaction pooling mode for OLTP web workloads to multiplex many app
  connections onto few backends; know that transaction mode forbids session-level state
  (`SET`, advisory locks across statements).
- Use pgBackRest (or WAL-G) for backups: parallel, compressed, encrypted, with verified
  restore and PITR. Reserve `pg_dump`/`pg_restore` for logical exports and version upgrades.
- Load `pg_stat_statements` and export metrics with a Postgres exporter into your
  monitoring stack; alert on lag, connections, wraparound, and cache hit ratio.
- Run local and CI Postgres in a container pinned to the production major version
  (e.g. `postgres:17`), so tests exercise the same engine that runs in production.
- Use `EXPLAIN`-visualization and `psql` for debugging; keep a GUI (pgAdmin, DBeaver) for
  exploration but automate anything repeatable in SQL scripts.

## Examples

**Good Example** — versioned migration + pinned local engine

```sql
-- migrations/V014__add_invoice_status_index.sql  (tool-ordered, in version control)
-- CONCURRENTLY avoids an exclusive lock on a hot table during deploy.
CREATE INDEX CONCURRENTLY IF NOT EXISTS invoice_status_idx ON invoice (status);
```

```yaml
# docker-compose for local/CI: same major version as production, reproducible.
services:
  db:
    image: postgres:17          # matches prod -> planner and syntax behave identically
    environment:
      POSTGRES_PASSWORD: dev
    ports: ["5432:5432"]
```

```ini
# pgbouncer.ini — transaction pooling for a web OLTP app.
[pgbouncer]
pool_mode = transaction         # multiplex many clients onto few server connections
max_client_conn = 5000
default_pool_size = 25          # server-side connections per db/user; sized to the DB
```

**Bad Example** — hand-rolled substitutes that fail under stress

```bash
# "Migration system": raw SQL piped by hand. No version record, no lock, no rollback.
psql mydb < changes.sql          # two concurrent deploys both run it -> duplicate/failed DDL

# "Backup system": a dump with no PITR, no verification, no offsite copy.
pg_dump mydb | gzip > /tmp/db.sql.gz   # RPO up to 24h; never test-restored; on the same host

# "Pooler": the app opens a new connection per request and never bounds it.
#   -> max_connections exhausted at peak, database refuses new clients
```

## Common Mistakes

- Applying schema changes by hand or via unordered scripts, causing environment drift.
- Using `pg_dump` as the disaster-recovery tool when the requirement is point-in-time
  recovery.
- Running PgBouncer in transaction mode while relying on session state (`SET`, prepared
  statements, advisory locks) that transaction mode breaks.
- Developing on a different major version than production and hitting planner/syntax
  surprises.
- Building a custom connection pool inside the app instead of using a proven pooler.
- Creating indexes in a migration without `CONCURRENTLY`, locking a hot table during deploy.

## Production Tips

- Gate deploys on migrations having run successfully, and make every migration reversible or
  paired with a tested down-migration.
- Keep tool versions (migration runner, pgBackRest, PgBouncer) pinned and upgraded
  deliberately, like any other dependency.
- Run backup verification and a periodic restore drill as a scheduled job, not a manual task.

## AI Review Checklist

- Are migrations versioned, ordered, locked, and in source control?
- Do index-creating migrations use `CREATE INDEX CONCURRENTLY` to avoid deploy-time locks?
- Is backup done with a PITR-capable tool, with verified restores — not bare `pg_dump`?
- Is connection pooling handled by a dedicated pooler, with mode-compatible app usage?
- Do local and CI databases match the production major version?
- Is `pg_stat_statements` loaded and are key metrics exported and alerted?

## Related

- `knowledge/postgresql/22-migrations.md`
- `knowledge/postgresql/17-monitoring.md`
- `knowledge/postgresql/14-backups.md`
- `knowledge/postgresql/23-testing.md`
- `knowledge/postgresql/24-debugging.md`
