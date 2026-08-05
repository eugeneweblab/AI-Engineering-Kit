---
id: mysql/16-migrations
topic: mysql
slug: migrations
title: "MySQL Migrations"
type: doc
order: 16
status: ready
tags: [mysql, migrations, CHAR, migrator, pt-online-schema-change, gh-ost, down, MySQL]
related: [mysql/13-users-and-roles, mysql/06-transactions, mysql/11-backups, mysql/17-testing]
when_to_use: "Read before writing or reviewing any schema-change migration against a live MySQL database."
---
# MySQL Migrations

## Purpose

This document defines how to evolve a MySQL schema safely on a running system:
versioned, reversible, forward-compatible changes that deploy without locking out
users or losing data. It is written so an agent can author a migration that is
safe to run against production with real traffic and real data volume.

Migrations touch the same locking and transaction mechanics covered in
[transactions](06-transactions.md), and they should be exercised the way
[testing](17-testing.md) describes. This file is about the change process itself:
how to make schema changes that are boring instead of dangerous.

## Why It Matters

A schema migration is the one operation that can lock your busiest table, block
every write, and corrupt or drop data — all in one statement, against live
traffic. Unlike application code, a bad migration cannot simply be rolled back by
redeploying the old binary; the data is already gone or the table is already
locked. The stakes make discipline non-negotiable: migrations must be versioned,
reviewed, forward-compatible, and tested against production-scale data before they
run for real.

## Core Principles

- **Every change is versioned and forward-only in intent.** Migrations live in the
  repo, run in order, and are tracked by a migration tool — never hand-applied `ALTER`s.
- **Expand, then contract.** Deploy schema changes so old and new application code
  both work during the rollout; never break the running version. Split destructive
  changes across releases.
- **Additive changes are safe; destructive changes are one-way.** Adding a nullable
  column is reversible; dropping a column or table is not. Treat destructive steps
  with extra ceremony and a backup.
- **Big tables need online DDL or a copy tool.** A naive `ALTER` on a large table can
  lock it for the whole operation. Use online DDL or `gh-ost`/`pt-online-schema-change`.
- **Test on production-shaped data.** Lock behavior and duration depend on row count;
  a migration that is instant on an empty table can lock a 100M-row table for an hour.

## Best Practices

- Use a migration framework (Flyway, Liquibase, Rails, Alembic, Prisma, etc.) that
  records applied versions; keep each migration small and single-purpose.
- Write and test a rollback (`down`) for reversible changes; for destructive ones,
  require a verified backup and an explicit runbook instead of pretending it reverts.
- Prefer InnoDB online DDL (`ALGORITHM=INPLACE, LOCK=NONE`) and verify the algorithm
  MySQL will actually use — some changes silently fall back to a table copy with a lock.
- For large tables or unsupported online DDL, use `gh-ost` or `pt-online-schema-change`
  to build a shadow table and swap it in with minimal locking.
- Follow expand/contract for renames and type changes: add new column, backfill,
  dual-write, switch reads, then drop the old column in a later release.
- Backfill data in bounded batches with commits between them, not one giant
  transaction that holds locks and bloats undo. See [transactions](06-transactions.md).
- Make migrations idempotent/guarded (`IF NOT EXISTS`, existence checks) so a retried
  or partially-applied run is safe.
- Run migrations with a dedicated `migrator` account that has DDL rights, separate
  from the runtime app account. See [users and roles](13-users-and-roles.md).

## Examples

**Good Example** — expand/contract, non-null column added safely

```sql
-- Release 1: add the column nullable with a default. Online, no long lock, and
-- old app code (which ignores the column) keeps working.
ALTER TABLE users
  ADD COLUMN country_code CHAR(2) NULL,
  ALGORITHM=INPLACE, LOCK=NONE;           -- verify MySQL honors this, not a copy

-- Release 1 (or a job): backfill in batches so no single txn holds locks for long.
UPDATE users SET country_code = 'US'
WHERE country_code IS NULL AND id BETWEEN 1 AND 10000;   -- repeat per range

-- Release 2, after backfill is complete and new code writes the column:
ALTER TABLE users
  MODIFY country_code CHAR(2) NOT NULL,
  ALGORITHM=INPLACE, LOCK=NONE;
```

**Bad Example** — destructive, locking, one-shot change on a live table

```sql
-- Renames a column in one step: old app code breaks instantly (no expand/contract).
-- On a large table this rewrites every row under a metadata lock, blocking all
-- writes for the duration. No backup, no batching, no rollback path.
ALTER TABLE users CHANGE COLUMN country iso_country CHAR(2) NOT NULL;
```

## Common Mistakes

- Hand-running `ALTER`s in production instead of versioned, reviewed migrations.
- A single-step rename or type change that breaks the currently-deployed app code.
- A naive `ALTER` on a huge table that silently copies it under a lock for hours.
- Backfilling in one enormous transaction that holds locks and bloats undo/redo.
- Dropping a column or table with no backup and no runbook, assuming it "reverts".
- Adding a `NOT NULL` column with no default on a large table, forcing a full rewrite.
- Skipping a test run against production-volume data, so the lock surprise is live.

## Production Tips

- Take (and verify) a backup before any destructive migration; it is the only real
  rollback for data loss. See [backups](11-backups.md).
- Rehearse the migration on a production-sized clone and measure its duration and lock
  behavior before scheduling it.
- Deploy schema and code in the expand/contract order so a rollback of the app never
  meets a schema it cannot handle.
- Keep destructive "contract" steps in a separate, later migration you can hold if the
  new code misbehaves.

## AI Review Checklist

- Is the change a versioned migration in the repo, not a hand-run statement?
- Does it follow expand/contract so the currently-deployed code keeps working?
- For large tables, is online DDL or a copy tool used, with the algorithm verified?
- Are backfills batched with commits between batches rather than one big transaction?
- Is there a tested `down`, or for destructive changes a verified backup and runbook?
- Was it rehearsed against production-scale data to measure lock and duration?
- Does it run as a dedicated `migrator` account, separate from the runtime app?

## Related

- `knowledge/mysql/13-users-and-roles.md`
- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/11-backups.md`
- `knowledge/mysql/17-testing.md`
