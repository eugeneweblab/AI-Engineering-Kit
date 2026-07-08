---
id: postgresql/22-migrations
topic: postgresql
slug: migrations
title: "Migrations"
type: doc
order: 22
status: ready
tags: [postgresql, migrations]
related: [postgresql/23-testing, postgresql/07-locking, postgresql/19-roles-and-permissions, postgresql/06-transactions, postgresql/26-production]
when_to_use: "Read before writing any schema-change migration, especially one that alters, locks, or backfills a large or high-traffic table."
---
# Migrations

## Purpose

This document defines how to evolve a PostgreSQL schema safely: writing versioned,
reversible migrations that apply without downtime, respecting locking, and staging changes so
old and new application code both keep working during a deploy. It is written so an agent can
author a migration that will not lock a hot table, corrupt data, or wedge a deploy.

Safe migrations depend on understanding [locking](07-locking.md) — which statements take
which locks and for how long — and on being able to verify the change before it ships, which
is [testing](23-testing.md).

## Why It Matters

A migration runs against live production data while users are online. Unlike application code,
you cannot simply roll it back after the fact — a `DROP COLUMN` that already executed took the
data with it, and a half-applied migration can leave the schema in a state neither the old nor
new code understands. Worse, the wrong DDL takes an `ACCESS EXCLUSIVE` lock that queues behind
in-flight queries and then blocks *every* new query on the table — a five-second migration
becomes a five-minute outage. The database will happily let you do all of this. Discipline in
how migrations are written is the only thing standing between a schema change and an incident.

## Core Principles

- **Every migration is versioned, ordered, and forward-only in production.** Use a migration
  tool (Flyway, Sqitch, Alembic, `node-pg-migrate`, Rails, Prisma) that records applied
  versions in a table. Never hand-edit production schema.
- **Migrations must be idempotent-safe to re-run and reversible in intent.** Provide a
  down/rollback path, but treat destructive down-migrations in production as a last resort —
  prefer rolling forward.
- **DDL locks matter more than DDL correctness.** Know the lock each statement takes and how
  long it holds it. A correct migration that locks a hot table for minutes is still an outage.
- **Expand, then contract.** Additive changes first (deploy code that tolerates both shapes),
  backfill, then remove the old shape in a later migration. Never change and remove in one step.
- **Backfills are batched, not one giant `UPDATE`.** A single `UPDATE` over millions of rows
  holds locks and bloats the table; batch it and commit between batches.
- **Set a lock timeout** so a blocked migration fails fast instead of freezing the table.

## Best Practices

- Add columns without a volatile default and without `NOT NULL` first; PostgreSQL 11+ makes a
  constant default a fast metadata-only change, but a `NOT NULL` on a new column still needs a
  validated backfill. Add the column nullable, backfill, then add the constraint.
- Create indexes with `CREATE INDEX CONCURRENTLY` so writes are not blocked. It cannot run
  inside a transaction block — configure the migration to run it non-transactionally, and
  clean up an `INVALID` index if it fails.
- Add constraints in two steps: `ADD CONSTRAINT … NOT VALID` (fast, takes a brief lock), then
  `VALIDATE CONSTRAINT` (scans the table but takes only a `SHARE UPDATE EXCLUSIVE` lock,
  allowing writes).
- Wrap each migration so DDL runs in a transaction where possible (PostgreSQL DDL is
  transactional), so a failure rolls the whole step back cleanly — except the concurrent
  operations that forbid transactions.
- Always `SET lock_timeout = '3s';` (and often `statement_timeout`) at the top of a migration
  touching a busy table, so it aborts rather than blocking the world.
- Backfill in bounded batches by primary key, sleeping briefly between batches to let
  autovacuum and replication keep up.
- Run the exact migration against a production-sized copy in CI/staging; measure the lock and
  duration before it touches production.

## Examples

**Good Example** — expand/contract, concurrent index, batched backfill

```sql
-- Step 1 (migration A): add the column nullable — metadata-only, no table rewrite.
ALTER TABLE orders ADD COLUMN status text;

-- Step 2 (migration B, runs outside a transaction): build the index without blocking writes.
SET lock_timeout = '3s';
CREATE INDEX CONCURRENTLY idx_orders_status ON orders (status);

-- Step 3 (application deploy): new code writes `status`; old code still works (column nullable).

-- Step 4 (migration C): backfill in batches so no single statement locks the whole table.
--   Run repeatedly until 0 rows updated (driven by the app/migration runner):
UPDATE orders SET status = 'legacy'
WHERE status IS NULL AND id IN (
  SELECT id FROM orders WHERE status IS NULL ORDER BY id LIMIT 5000
);

-- Step 5 (migration D): validate the constraint in two lock-friendly phases.
ALTER TABLE orders ADD CONSTRAINT orders_status_nn CHECK (status IS NOT NULL) NOT VALID;
ALTER TABLE orders VALIDATE CONSTRAINT orders_status_nn;   -- scans, but allows writes
```

**Bad Example** — one statement, exclusive lock, no timeout

```sql
-- On a large busy table this rewrites the whole table under ACCESS EXCLUSIVE lock:
-- every query on `orders` blocks until it finishes, and there is no lock_timeout to
-- bail out. A "quick migration" becomes a full outage, and there is no rollback for
-- the rows already rewritten if it is killed mid-way.
ALTER TABLE orders ADD COLUMN status text NOT NULL DEFAULT compute_status();
```

## Common Mistakes

- Adding a `NOT NULL` column with a *volatile* default (a function call), forcing a full table
  rewrite under `ACCESS EXCLUSIVE` lock.
- `CREATE INDEX` without `CONCURRENTLY` on a live table, blocking writes for the whole build.
- One massive `UPDATE`/`DELETE` backfill that holds locks, bloats the table, and lags replicas.
- No `lock_timeout`, so a migration queues behind a long query and then blocks everything.
- Changing and removing schema in one migration, breaking rolling deploys where old and new
  code run simultaneously.
- Hand-editing production schema outside the migration tool, so environments drift.
- Assuming `CREATE INDEX CONCURRENTLY` is transactional — it is not, and a failure leaves an
  `INVALID` index that must be dropped and rebuilt.

## Production Tips

- Test migrations against a clone of production (right size and data distribution); the lock
  and duration on an empty dev table tell you nothing.
- Have a rollback plan per migration and rehearse it; prefer roll-forward fixes for
  destructive changes.
- Run migrations as a dedicated migrator/owner role, separate from the app login
  ([roles and permissions](19-roles-and-permissions.md)).
- Gate deploys on migration success and monitor lock waits (`pg_locks`, `pg_stat_activity`)
  while a migration runs.

## AI Review Checklist

- Is the change versioned and applied through a migration tool, not by hand?
- Does it follow expand/contract, keeping old and new code working during the deploy?
- Are new indexes built with `CREATE INDEX CONCURRENTLY` (outside a transaction)?
- Are constraints added `NOT VALID` then `VALIDATE`d to avoid a long exclusive lock?
- Is `lock_timeout` (and where relevant `statement_timeout`) set on hot-table migrations?
- Are backfills batched and committed incrementally, not one giant statement?
- Was the migration tested against a production-sized dataset for lock time and duration?

## Related

- `knowledge/postgresql/23-testing.md`
- `knowledge/postgresql/07-locking.md`
- `knowledge/postgresql/19-roles-and-permissions.md`
- `knowledge/postgresql/06-transactions.md`
- `knowledge/postgresql/26-production.md`
