---
id: sql/29-tooling
topic: sql
slug: tooling
title: "SQL Tooling"
type: doc
order: 29
status: ready
tags: [sql, tooling, pg_stat_statements, migrate, log_min_duration_statement, EXPLAIN]
related: [sql/12-ddl, sql/16-query-planning, sql/24-testing, sql/25-debugging, sql/23-performance]
when_to_use: "Read when setting up migrations, linting, or observability for a SQL codebase."
---
# SQL Tooling

## Purpose

This document defines the tooling that keeps a SQL codebase safe to change: migration
managers, linters and formatters, query analysis, and observability. It is written so
an agent sets up the guardrails that catch mistakes automatically instead of relying
on reviewers to spot them by hand.

Good tooling turns whole classes of SQL error into a build failure. A migration tool
makes "which changes have been applied?" answerable. A linter catches the missing
`WHERE`. A slow-query log surfaces the regression before a user does. Each replaces
vigilance with automation.

## Why It Matters

The most damaging SQL problems are the ones that are invisible in review: a migration
applied to staging but not production, a query that was fast on a small table and now
does a sequential scan, an ad-hoc `UPDATE` run straight against production with no
record of what changed. None of these are logic errors a careful author would catch —
they are operational failures that only tooling prevents.

Without tooling, the database becomes the one part of the system with no version
control, no CI, and no monitoring — mutated by hand and understood by no one. With it,
schema changes are as reviewable, testable, and reversible as any other code.

## Core Principles

- **Schema lives in version control, changed only by migrations.** Every DDL change is
  a numbered, immutable migration file committed to the repo — never an ad-hoc `ALTER`
  typed into a console. This is the non-negotiable foundation; everything else builds
  on it. See [DDL](12-ddl.md).
- **Migrations are forward-only and idempotent to apply.** A migration tool records
  which versions ran, so applying the same set twice is a no-op and every environment
  converges to the same schema. Never edit a migration that has shipped; add a new one.
- **Automate what a reviewer would check.** Lint and format SQL in CI so style,
  missing `WHERE` clauses, and dangerous patterns fail the build rather than depending
  on human attention.
- **Make the database observable.** You cannot fix what you cannot see: slow-query
  logs, `pg_stat_statements`, and connection/lock metrics are prerequisites, not
  extras. See [query-planning](16-query-planning.md).
- **Never run destructive statements by hand against production.** Route every change
  through a reviewed migration; keep an audit trail of what ran and when.

## Best Practices

- Use a **dedicated migration tool** — Flyway, Liquibase, Alembic, or your ORM's
  migrations — that maintains a schema-version table. Roll it forward in CI/CD, not by
  hand, so staging and production never diverge.
- Add a **SQL linter** (`sqlfluff`) and formatter to pre-commit and CI. Configure it to
  the target dialect so it catches non-portable syntax and enforces a single style; a
  consistently formatted query is one whose bug shows up in a diff.
- Gate **`EXPLAIN` on critical queries in CI** (or a plan-diff tool) so a change that
  turns an index scan into a sequential scan fails the build. See
  [performance](23-performance.md).
- Run tests against the **real engine in a container** (Testcontainers or a service
  container), pinned to the production major version, so dialect and `NULL` behavior
  match. See [testing](24-testing.md).
- Enable **query observability in every environment**: `log_min_duration_statement` and
  `pg_stat_statements` on Postgres, the slow query log and performance schema on MySQL.
  Rank queries by total time, not just peak latency.
- Keep **credentials and connection strings in a secrets manager**, and give the
  application a least-privilege role — the app user should not own DDL rights. See
  [security](22-security.md).
- Use a **connection pooler** (PgBouncer, the driver's pool, or a proxy like RDS Proxy)
  sized to the database's connection limit; unbounded connections are a common outage
  cause.

## Examples

**Good Example** — versioned migration, applied by tool, reversible

```sql
-- migrations/0042_add_orders_status_index.sql  (committed, immutable, numbered)
-- Applied by the migration tool in CI/CD; recorded in the schema_version table.
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status
  ON orders (status);          -- CONCURRENTLY: no long write lock in production
-- IF NOT EXISTS keeps re-application safe if a deploy is retried.
```

```bash
# The tool tracks which versions ran, so every environment converges deterministically.
flyway migrate            # applies only the migrations not yet recorded
flyway info               # shows pending vs applied — "is prod up to date?" is answerable
```

**Bad Example** — hand-run change, no record, no review

```sql
-- Typed directly into a production console over SSH. Not in version control,
-- not reviewed, not recorded. Staging now differs from prod and no one knows.
ALTER TABLE orders ADD COLUMN status TEXT;
UPDATE orders SET status = 'open';   -- ran against live data with no migration, no audit
-- Next deploy's migration assumes the column does NOT exist and fails.
```

## Common Mistakes

- Changing schema with hand-typed `ALTER`/`UPDATE` instead of committed migrations, so
  environments drift and there is no audit trail.
- Editing a migration that already shipped, so environments that ran the old version
  never get the fix.
- No SQL linting or formatting in CI, leaving dangerous patterns for humans to catch.
- Testing against SQLite while shipping to Postgres/MySQL, so tooling validates the
  wrong dialect.
- No slow-query logging or `pg_stat_statements`, so regressions are invisible until an
  outage.
- Unbounded connections with no pooler, exhausting the database's connection limit
  under load.

## Production Tips

- Make **`migrate` a gated step in the deploy pipeline**, with `info`/`status` checked
  before and after, so a deploy cannot proceed against an out-of-date schema.
- Alert on the **observability signals that predict outages**: connection saturation,
  lock wait time, replication lag, and the top queries by total time.
- Keep a **read-only analytics role and a separate least-privilege app role**; never
  let application code connect as a superuser or schema owner.

## AI Review Checklist

- Is all schema change done through committed, numbered migrations applied by a tool?
- Does the migration tool record applied versions so environments converge?
- Are SQL lint and format enforced in CI, configured to the target dialect?
- Do tests run against the real engine and version, and are hot-path plans gated?
- Are slow-query logging and `pg_stat_statements` (or equivalents) enabled everywhere?
- Are credentials in a secrets manager, with a least-privilege app role and a pooler?

## Related

- `knowledge/sql/12-ddl.md`
- `knowledge/sql/16-query-planning.md`
- `knowledge/sql/24-testing.md`
- `knowledge/sql/25-debugging.md`
- `knowledge/sql/23-performance.md`
