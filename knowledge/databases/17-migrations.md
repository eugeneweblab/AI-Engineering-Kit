---
id: databases/17-migrations
topic: databases
slug: migrations
title: "Migrations"
type: doc
order: 17
status: ready
tags: [databases, migrations]
related: [databases/06-schema-design, databases/09-transactions, databases/11-locking, databases/18-backup-and-recovery, databases/27-testing]
when_to_use: "Read before writing, reviewing, or deploying any schema change against a database that has data or live traffic."
---
# Migrations

## Purpose

This document defines how to evolve a database schema safely — adding columns,
changing types, backfilling data, dropping tables — without downtime or data loss. It
exists so an agent can write a migration that is reversible in effect, does not lock a
live table, and stays compatible with the code deployed alongside it.

A migration is a *versioned, ordered, forward change* to the schema and data. Unlike
ordinary code, a migration runs against production data exactly once and is very hard
to undo once it has destroyed information. That asymmetry — cheap to write, expensive
to get wrong — is why migrations are held to a higher bar.

## Why It Matters

A schema change is the one deploy that can take the whole database down or lose data
permanently. An `ALTER TABLE` that rewrites or long-locks a large table blocks every
query behind it, turning a routine deploy into an outage. A migration that drops a
column the still-running old code reads causes instant errors during the rollout. A
destructive change with no backup is unrecoverable. These failures hit at deploy time,
under production load, on data you cannot regenerate — so migrations must be planned as
carefully as the code they support, not treated as an afterthought.

## Core Principles

- **Migrations are ordered, versioned, and immutable once shipped.** Never edit a
  migration that has run in any shared environment; write a new one. Editing history
  desyncs environments.
- **Expand, then contract.** Change schema in backward-compatible steps so old and new
  code can both run during a rolling deploy: add the new shape, migrate reads/writes,
  then remove the old shape in a *later* deploy. Never break running code.
- **Additive changes are safe; destructive changes are one-way.** Adding a nullable
  column is low-risk; dropping a column or table destroys data. Separate them in time
  and back up before destructive steps.
- **Schema changes must not lock live tables.** On large tables, avoid operations that
  take a long exclusive lock or rewrite the table; use online/concurrent variants.
- **Backfills belong outside the schema transaction.** Rewriting millions of rows in
  one transaction holds locks and bloats; do it in batches, separately.
- **Every migration must be tested and rehearsed on production-like data**, because
  lock behavior and duration depend on table size, not on your laptop's ten rows.

## Best Practices

- Follow **expand/contract** for any breaking change:
  1. Add the new column/table (nullable, no forced rewrite).
  2. Deploy code that writes both old and new; backfill the new in batches.
  3. Deploy code that reads new only.
  4. In a *later* migration, drop the old column/table.
- Create indexes without locking writes: PostgreSQL `CREATE INDEX CONCURRENTLY`, MySQL
  `ALGORITHM=INPLACE, LOCK=NONE`. A plain `CREATE INDEX` locks the table.
- Add columns without a table rewrite: an added column should be nullable or have a
  constant default the engine can apply cheaply. Set `NOT NULL` only after backfill,
  validating the constraint separately (`ADD CONSTRAINT ... NOT VALID` then
  `VALIDATE`).
- Backfill in bounded batches (e.g. 5k rows) with a short pause, so you never hold a
  long transaction or overwhelm replication lag.
- Set a low `lock_timeout` on DDL so a migration that cannot get its lock fails fast
  instead of queueing behind and blocking all traffic.
- Make each migration idempotent/guarded (`IF NOT EXISTS`, existence checks) so a
  retry after a partial failure is safe.
- Take a backup (or verify one exists) immediately before any destructive or
  irreversible step. See [backup and recovery](18-backup-and-recovery.md).
- Run migrations in CI against a production-like snapshot to catch lock and duration
  problems before deploy.

## Examples

**Good Example** — expand/contract, no lock, batched backfill

```sql
-- Step 1 (deploy A): add nullable column, no table rewrite, no long lock.
ALTER TABLE users ADD COLUMN email_verified boolean;

-- Step 2 (background job): backfill in batches so no single long transaction
-- holds locks or spikes replication lag.
UPDATE users SET email_verified = false
 WHERE email_verified IS NULL AND id BETWEEN $1 AND $2;   -- repeat per batch

-- Step 3 (deploy B, after backfill completes): enforce the constraint without
-- a full-table blocking validation, then validate separately.
ALTER TABLE users ADD CONSTRAINT users_ev_nn
  CHECK (email_verified IS NOT NULL) NOT VALID;
ALTER TABLE users VALIDATE CONSTRAINT users_ev_nn;        -- non-blocking scan

-- Step 4 (a LATER migration, once no code reads it): drop the old column.
-- ALTER TABLE users DROP COLUMN legacy_verified;
```

**Bad Example** — rewrites and locks a live table, breaks running code

```sql
-- NOT NULL with a default on a large table forces a full rewrite under an
-- exclusive lock in many engines -> every query blocks until it finishes.
ALTER TABLE users ADD COLUMN email_verified boolean NOT NULL DEFAULT false;

-- Same migration drops a column the currently-deployed old code still reads,
-- so the instant this runs mid-rollout, the old pods throw. No backup taken;
-- the dropped data is gone for good.
ALTER TABLE users DROP COLUMN legacy_verified;

-- Plain index build locks the table against writes for its whole duration.
CREATE INDEX idx_users_email ON users (email);
```

## Common Mistakes

- Editing a migration that already ran somewhere, desyncing environments.
- Adding a `NOT NULL DEFAULT` or changing a column type on a large table in one step,
  forcing a locking rewrite.
- Dropping or renaming a column/table in the same deploy the code still uses it —
  breaking the rolling rollout.
- Building indexes non-concurrently, locking writes on a live table.
- Backfilling millions of rows in a single transaction, holding locks and lagging
  replicas.
- Running a destructive migration with no fresh backup and no rollback path.

## Production Tips

- Set `lock_timeout` (and a statement timeout) on migration sessions so a blocked DDL
  fails fast instead of stalling all traffic behind it.
- Decouple deploys from migrations: run additive migrations before the code deploy,
  destructive ones a full deploy later, once nothing references the old shape.
- Keep migrations in a versioned tool (Flyway, Liquibase, Prisma Migrate, Alembic,
  Rails) with a recorded, ordered history — never ad-hoc SQL in production.
- For truly irreversible steps, snapshot first and note the recovery procedure in the
  migration's description.

## AI Review Checklist

- Does the change follow expand/contract so old and new code both work during rollout?
- Are large-table `ALTER`s free of full rewrites and long exclusive locks (online/
  concurrent variants used)?
- Are indexes built concurrently / `LOCK=NONE`?
- Are backfills batched and run outside the schema transaction?
- Is `lock_timeout` set so a blocked migration fails fast rather than blocking traffic?
- Is there a backup and rollback path before any destructive or irreversible step?
- Is the migration immutable (not editing already-shipped history) and idempotent on
  retry?

## Related

- `knowledge/databases/06-schema-design.md`
- `knowledge/databases/09-transactions.md`
- `knowledge/databases/11-locking.md`
- `knowledge/databases/18-backup-and-recovery.md`
- `knowledge/databases/27-testing.md`
