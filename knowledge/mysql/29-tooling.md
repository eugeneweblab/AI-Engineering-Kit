---
id: mysql/29-tooling
topic: mysql
slug: tooling
title: "Tooling"
type: doc
order: 29
status: ready
tags: [mysql, tooling]
related: [mysql/16-migrations, mysql/11-backups, mysql/15-monitoring, mysql/14-performance]
when_to_use: "Read before choosing tools for migrations, backups, online schema changes, or diagnosing a slow production database."
---
# Tooling

## Purpose

This document catalogs the tools an engineer should reach for when operating MySQL —
schema migrations, online DDL, backups, load, and diagnostics — and, crucially, which
native operation to avoid because a battle-tested tool exists. It is a decision guide, not
a tutorial for any single tool.

The theme is that the naive command is often a production hazard: a plain `ALTER TABLE`
can lock a large table, `mysqldump` can take hours to restore, and eyeballing the process
list is no substitute for the slow log. The right tool exists for each of these.

## Why It Matters

The gap between "works on my laptop" and "safe in production" is almost entirely tooling.
A blocking schema change on a hot table can take an outage; a backup you never test to
restore is not a backup; a slow query hunt by intuition wastes hours the slow log would
save. Choosing the wrong tool — or the raw native command when a safer wrapper exists —
converts routine maintenance into an incident. Standardizing on proven tools makes these
operations boring, which is exactly what you want.

## Core Principles

- **Never run a blocking `ALTER` on a large, hot table.** Use an online-schema-change tool
  (`gh-ost`, `pt-online-schema-change`) or verify the change qualifies for InnoDB
  `ALGORITHM=INPLACE, LOCK=NONE`. See [migrations](16-migrations.md).
- **A backup is only real once you have restored it.** Use a tool whose restore you have
  actually tested — physical (Percona XtraBackup / MySQL Enterprise Backup) for large
  datasets, logical (`mysqldump`/`mysqlpump`/`mydumper`) for small or portable ones. See
  [backups](11-backups.md).
- **Diagnose from data, not intuition.** The slow query log, `EXPLAIN ANALYZE`, and
  `performance_schema` tell you what is slow; guessing does not. See
  [performance](14-performance.md).
- **Migrations are code.** Run schema changes through a versioned migration tool
  (Flyway, Liquibase, or your framework's migrator), never ad-hoc SQL typed into a prompt.
- **Prefer proven tools over bespoke scripts.** Home-grown backup/migration scripts skip
  the edge cases (locking, foreign keys, replication) the mature tools already solved.

## Best Practices

- For schema changes on tables large enough to lock noticeably, use **gh-ost** (triggerless,
  replication-based) or **pt-online-schema-change**; both build a shadow table and cut over
  with minimal locking. Reserve native `ALTER` for small tables or verified in-place ops.
- Take **physical backups** with Percona XtraBackup for fast, low-impact full/incremental
  copies of large datasets; use logical dumps for portability and selective restore. Store
  backups off-host and **test-restore on a schedule**.
- Hunt slow queries with the **slow query log** (`long_query_time` set low temporarily)
  plus **pt-query-digest** to rank offenders, then confirm each fix with `EXPLAIN ANALYZE`.
- Use **performance_schema** and helper views (**sys schema**: `sys.statements_with_full_table_scans`,
  `sys.schema_unused_indexes`) for live diagnostics instead of parsing `SHOW PROCESSLIST`
  by eye.
- Keep a **client/driver connection pool** (application-side or ProxySQL) rather than
  opening a connection per request; connection churn is a common, avoidable bottleneck.
- Run migrations in CI against a production-like schema so a locking or long-running change
  is caught before it reaches production. See [testing](17-testing.md).

## Examples

**Good Example** — online schema change and a diagnosed slow query

```bash
# Add a column to a large hot table WITHOUT a long lock: gh-ost copies into a
# shadow table via the binlog stream and swaps at the end. Dry-run first.
gh-ost \
  --database=shop --table=orders \
  --alter="ADD COLUMN channel VARCHAR(20) NOT NULL DEFAULT 'web'" \
  --execute

# Rank the worst queries from the slow log instead of guessing:
pt-query-digest /var/log/mysql/slow.log | head -50
```

```sql
-- Confirm the fix with real execution data, not the estimated plan:
EXPLAIN ANALYZE SELECT id FROM orders WHERE channel = 'web' AND created_at > ?;
```

**Bad Example** — blocking DDL and an untested backup

```bash
# Plain ALTER on a large, busy table: depending on the change it rebuilds the
# table under a metadata/row lock, stalling every reader and writer for the
# duration -- a self-inflicted outage.
mysql shop -e "ALTER TABLE orders ADD COLUMN channel VARCHAR(20) NOT NULL DEFAULT 'web'"

# A dump that has never been restored: on a 500GB database the single-threaded
# restore can take many hours, and nobody knows until the outage is already happening.
mysqldump shop > shop.sql   # stored on the same host, restore never tested
```

## Common Mistakes

- Running a naive `ALTER TABLE` on a large hot table and locking out all traffic.
- Trusting backups that have never been restored, or storing them on the same host as the
  database.
- Restoring a huge dataset from a single-threaded logical dump when a physical backup would
  take minutes.
- Diagnosing slow queries by staring at `SHOW PROCESSLIST` instead of the slow log and
  `EXPLAIN ANALYZE`.
- Applying schema changes as ad-hoc SQL outside a versioned migration tool, with no review
  or rollback.
- Opening a fresh connection per request instead of pooling, exhausting `max_connections`.

## Production Tips

- Always run online-schema-change tools with `--dry-run`/`--execute` staged and a tested
  `--panic`/cut-over threshold; keep the shadow table's extra disk in mind.
- Automate restore drills: a scheduled job that restores last night's backup to a scratch
  host and runs a sanity query is the only proof your backups work. See [backups](11-backups.md).
- Standardize the toolset in your runbooks so on-call reaches for the same, known commands
  under pressure rather than improvising.

## AI Review Checklist

- Do schema changes on large tables use an online-schema-change tool or a verified in-place
  algorithm, never a blocking `ALTER`?
- Are backups taken with an appropriate tool, stored off-host, and restore-tested on a
  schedule?
- Are slow queries diagnosed from the slow log / `EXPLAIN ANALYZE`, not intuition?
- Are all schema changes applied through a versioned migration tool?
- Is there connection pooling rather than a connection per request?
- Are migrations exercised in CI against a production-like schema before release?

## Related

- `knowledge/mysql/16-migrations.md`
- `knowledge/mysql/11-backups.md`
- `knowledge/mysql/15-monitoring.md`
- `knowledge/mysql/14-performance.md`
