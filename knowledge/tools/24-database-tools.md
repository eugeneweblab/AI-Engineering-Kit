---
id: tools/24-database-tools
topic: tools
slug: database-tools
title: "Database Tools"
type: doc
order: 24
status: ready
tags: [tools, database-tools]
related: [tools/20-local-environments, tools/23-api-clients, tools/22-profilers, tools/26-ai-coding-tools, tools/30-engineering-principles, databases/08-query-optimization, databases/17-migrations]
when_to_use: "Read before working with a database by hand — choosing a client, inspecting queries, running migrations, or moving data between environments safely."
---
# Database Tools

## Purpose

This document defines how to work with databases outside application code: clients for
inspection, command-line tools for automation, and the safeguards that keep a routine query
from becoming a production incident.

## Why It Matters

Every serious data-loss story starts with a person, a client connected to production, and a
statement that looked routine. `UPDATE` without `WHERE`, `DELETE` on the wrong tab, a
`search-replace` that corrupted serialized data — these are tooling failures as much as human
ones, and the mitigations are configuration, not carefulness.

The second theme is diagnosis: a query planner explains in seconds what profiling the
application only hints at.

## Core Principles

- **Read-only by default in production.** A separate read-only account for a GUI client makes
  the destructive class of accident impossible rather than unlikely.
- **Never write to production by hand.** Changes go through migrations, which are reviewed,
  versioned, and reversible.
- **Transaction-wrap anything manual.** `BEGIN`, verify, then `COMMIT` or `ROLLBACK`.
- **Back up before touching data.** An export takes a minute; a restore without one is
  impossible.

## Command Line

The vendor CLIs are always present and scriptable:

```bash
# PostgreSQL
psql "$DATABASE_URL" -c '\dt'                       # list tables
psql "$DATABASE_URL" -c 'SELECT * FROM orders LIMIT 5' -x   # expanded, readable rows
psql "$DATABASE_URL" -f migration.sql --single-transaction  # all-or-nothing

pg_dump "$DATABASE_URL" -Fc -f backup.dump          # custom format: compressed, selective restore
pg_restore -d "$TARGET_URL" --clean --if-exists backup.dump

# MySQL / MariaDB
mysql -u app -p app -e 'SHOW TABLE STATUS'
mysqldump --single-transaction --quick app > backup.sql

# WordPress — knows about serialization, which raw SQL does not
wp db export backup.sql
wp db query 'SELECT COUNT(*) FROM wp_posts WHERE post_type = "product"'
wp search-replace 'http://old.test' 'https://new.example' --dry-run
```

The `--single-transaction` flags matter: without them a dump is inconsistent under concurrent
writes, and a partially applied migration leaves the schema in an undefined state.

## Inspecting Query Plans

The planner is the fastest diagnostic available for a slow query:

```sql
-- PostgreSQL: ANALYZE executes the query and reports real timings.
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT o.id, o.total, c.email
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'pending' AND o.created_at > now() - interval '30 days'
ORDER BY o.created_at DESC
LIMIT 50;
```

```
Limit  (cost=... rows=50) (actual time=412.8..412.9 rows=50 loops=1)
  ->  Sort  (actual time=412.8..412.8 rows=50 loops=1)
        Sort Method: top-N heapsort  Memory: 41kB
        ->  Seq Scan on orders o  (actual time=0.3..389.1 rows=184,221 loops=1)
              Filter: (status = 'pending' AND created_at > ...)
              Rows Removed by Filter: 1,905,443
```

Two lines carry the diagnosis: `Seq Scan` on a large table with a selective filter, and
`Rows Removed by Filter` far exceeding the rows returned. The fix is an index on
`(status, created_at)`, and re-running `EXPLAIN ANALYZE` confirms it.

Run `EXPLAIN ANALYZE` inside a transaction you roll back when the statement writes:

```sql
BEGIN;
EXPLAIN ANALYZE UPDATE orders SET status = 'archived' WHERE created_at < '2024-01-01';
ROLLBACK;
```

## GUI Clients

TablePlus, DBeaver, pgAdmin, and Sequel Ace all work. What matters is configuration, not the
choice:

- **Colour-code connections.** Red for production, amber for staging, green for local. This
  single setting prevents the most common category of accident.
- **Connect to production with a read-only role.** Not a promise to be careful — a role that
  cannot write.
- **Disable auto-commit** for any writable connection, so a mistake can be rolled back.
- **Use SSH tunnelling** rather than exposing the database port publicly.

```sql
-- The read-only role every GUI connection to production should use.
CREATE ROLE analyst LOGIN PASSWORD '…';
GRANT CONNECT ON DATABASE app TO analyst;
GRANT USAGE ON SCHEMA public TO analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analyst;
```

## Migrations, Not Manual Edits

Schema changes belong in migration files regardless of how small they seem:

```bash
npx prisma migrate dev --name add_order_status_index    # generate and apply locally
npx prisma migrate deploy                                # apply in CI/production
wp db query < migrations/003-add-index.sql               # WordPress equivalent
```

A manual `ALTER TABLE` on production exists nowhere in version control. The next deploy from a
clean database will not have it, and the difference surfaces as an inexplicable production-only
bug.

## Examples

**Good Example** — a manual data fix done safely

```sql
BEGIN;

-- 1. See exactly what will change.
SELECT id, status FROM orders WHERE status = 'pendng';   -- the typo being corrected

-- 2. Apply, and confirm the count matches.
UPDATE orders SET status = 'pending' WHERE status = 'pendng';
-- UPDATE 47   ← matches the SELECT above

COMMIT;
```

**Bad Example** — the classic

```sql
UPDATE orders SET status = 'pending';   -- WHERE clause forgotten; every row updated
-- auto-commit was on, so there is nothing to roll back
```

This is why auto-commit off and a read-only production role are configuration decisions rather
than preferences.

## Common Mistakes

- A read-write connection to production in a desktop client.
- Auto-commit enabled on a writable connection.
- Schema changed by hand instead of by migration.
- No backup before a manual data operation.
- SQL `UPDATE` for WordPress URL changes, corrupting serialized values.
- `EXPLAIN` without `ANALYZE`, showing estimates rather than reality.
- Production credentials stored unencrypted in a client's saved connections.
- Database ports exposed to the internet instead of tunnelled.
- `SELECT *` on a large table in a GUI, pulling gigabytes to render a grid.

## Production Tips

- Test restores, not just backups. A dump that has never been restored is an assumption — see
  [WordPress — Maintenance](../wordpress/29-maintenance.md) for a cadence.
- Keep a `queries/` directory in the repository for diagnostic SQL people rerun; it beats
  reconstructing the same join every incident.
- Add `statement_timeout` to the read-only role so an accidental unbounded query cannot pin the
  database.
- Anonymize production data before copying it anywhere — a staging database full of real
  customer emails is a breach waiting for one misconfigured mail setting.
- Watch the slow query log continuously rather than investigating only after a complaint.

## AI Review Checklist

- Is the production connection read-only, colour-coded, and tunnelled?
- Is auto-commit disabled for writable connections?
- Do all schema changes exist as reviewed migrations?
- Is a backup taken before any manual data change?
- Are manual statements wrapped in a transaction and verified before commit?
- Are slow queries diagnosed with `EXPLAIN ANALYZE` before being optimized?
- Is copied production data anonymized?

## Related

- `knowledge/tools/20-local-environments.md`
- `knowledge/tools/23-api-clients.md`
- `knowledge/tools/22-profilers.md`
- `knowledge/tools/26-ai-coding-tools.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/databases/08-query-optimization.md`
- `knowledge/databases/17-migrations.md`
