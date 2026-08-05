---
id: postgresql/99-ai-review-checklist
topic: postgresql
slug: ai-review-checklist
title: "PostgreSQL AI Review Checklist"
type: doc
order: 99
status: ready
tags: [postgresql, ai-review-checklist, varchar, double, timestamp, timestamptz, lock_timeout, numeric]
related: [postgresql/30-engineering-principles, postgresql/100-common-antipatterns, postgresql/06-transactions, postgresql/04-indexes, postgresql/22-migrations]
when_to_use: "Read before reviewing or approving any change that touches schema, queries, transactions, or migrations."
---
# PostgreSQL AI Review Checklist

## Purpose

This is the checklist an AI agent applies when reviewing PostgreSQL-related changes:
schema definitions, queries, transaction logic, indexes, and migrations. Each item is a
concrete yes/no the reviewer can verify from the diff. It complements the
[production checklist](98-production-checklist.md) — that one governs the running
system; this one governs the code and DDL under review.

## Why It Matters

Database mistakes are the hardest class of bug to walk back: a wrong type or a missing
constraint corrupts data that then flows into everything downstream, and a blocking
migration takes production offline the moment it deploys. Catching these at review is
orders of magnitude cheaper than catching them in an incident. A reviewer who checks
these items stops correctness and availability defects before they reach `main`.

## Correctness and Types

**Rules:** [Data Types](03-data-types.md) · [JSONB](08-jsonb.md)

- [ ] Are time columns `timestamptz`, not naive `timestamp`?
- [ ] Is money/exact-decimal stored as `numeric`, never `float`/`double`?
- [ ] Does every new table have a primary key?
- [ ] Are invariants enforced by `NOT NULL`/`CHECK`/`UNIQUE`/`FOREIGN KEY`, not just app code?
- [ ] Does every foreign key declare an explicit `ON DELETE` action?
- [ ] Are enumerated values a lookup table or real enum, not free-text `varchar`?

## Concurrency and Transactions

**Rules:** [Transactions](06-transactions.md) · [Locking](07-locking.md)

- [ ] Is each read-modify-write protected by `SELECT ... FOR UPDATE` or a serializable transaction ([transactions](06-transactions.md))?
- [ ] Are transaction boundaries scoped to the smallest atomic unit and kept short?
- [ ] Are potentially-duplicating inserts made idempotent with `ON CONFLICT`?
- [ ] Is there no user input or network/HTTP call made *inside* an open transaction holding locks?
- [ ] Are lock-order and deadlock risks considered where multiple rows/tables are updated?

## Queries and Indexes

**Rules:** [Query Planner](05-query-planner.md) · [Indexes](04-indexes.md)

- [ ] Is there an index supporting the `WHERE`/`JOIN`/`ORDER BY` of any hot query ([indexes](04-indexes.md))?
- [ ] Are indexed columns used sargably (no function wrapping the column in the predicate)?
- [ ] Do new indexes trace to `EXPLAIN (ANALYZE, BUFFERS)` evidence, not guesswork ([query planner](05-query-planner.md))?
- [ ] Are all query parameters bound (parameterized), never string-concatenated (SQL injection)?
- [ ] Do queries select only needed columns instead of blanket `SELECT *`?
- [ ] Are large result sets paginated by keyset, not deep `OFFSET`?

## Migrations

**Rules:** [Migrations](22-migrations.md)

- [ ] Is the migration forward-only and reproducible from an empty database ([migrations](22-migrations.md))?
- [ ] Does index creation on a populated table use `CREATE INDEX CONCURRENTLY`?
- [ ] Does adding a `NOT NULL` column avoid a full-table rewrite (default handling, backfill in batches)?
- [ ] Is the migration safe to deploy *before* the code that depends on it (expand/contract)?
- [ ] Does any long-lived `ACCESS EXCLUSIVE` lock on a hot table have a `lock_timeout` and a plan?

## Security

**Rules:** [Security](18-security.md) · [Roles And Permissions](19-roles-and-permissions.md)

- [ ] Does the change avoid granting more privilege than the app role needs ([roles](19-roles-and-permissions.md))?
- [ ] Are secrets kept out of the diff (no inline passwords/connection strings)?
- [ ] Where multi-tenant, is row-level security or an equivalent tenant filter present?

## Related

- `knowledge/postgresql/30-engineering-principles.md`
- `knowledge/postgresql/100-common-antipatterns.md`
- `knowledge/postgresql/06-transactions.md`
- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/22-migrations.md`
