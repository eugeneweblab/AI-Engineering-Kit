---
id: sql/98-production-checklist
topic: sql
slug: production-checklist
title: "Production Checklist"
type: doc
order: 98
status: ready
tags: [sql, production-checklist]
related: [sql/14-transactions, sql/15-indexes, sql/22-security, sql/23-performance, sql/30-engineering-principles]
when_to_use: "Read before shipping a schema, migration, or query change to a production database."
---
# Production Checklist

## Purpose

A concrete, verifiable gate to run before any SQL change reaches production data:
new schema, a migration, or a query that will run at scale. Every item is a yes/no
you can check by reading the change, running `EXPLAIN`, or inspecting the deploy plan.
If an item cannot be answered "yes", the change is not ready.

## Why It Matters

Production data is the one thing you cannot recompute from source. A checklist turns
the diffuse "is this safe?" question into specific checks that catch the failures that
actually cause outages and corruption: locking migrations, unindexed hot paths,
unbounded writes, and roles with too much power. Working through it is minutes; the
incident it prevents is hours and irreversible data loss.

## Schema and Constraints

- [ ] Every table has a primary key.
- [ ] Every real relationship has a `FOREIGN KEY`, and the referencing column is indexed.
- [ ] Columns are `NOT NULL` unless a distinct "absent" state is genuinely needed.
- [ ] Types are precise: `TIMESTAMPTZ` for time, `NUMERIC` for money, enums/`CHECK` for
      fixed sets — never `VARCHAR` as a catch-all.
- [ ] Business invariants (ranges, mutually exclusive states) are enforced by `CHECK` or
      `UNIQUE` constraints, not only in application code.

## Migrations

- [ ] The migration is reversible, and the `down`/rollback path has been tested.
- [ ] Adding a column with a volatile default, backfilling, or changing a type does not
      take a long `ACCESS EXCLUSIVE` lock on a hot table (use non-blocking patterns:
      add nullable, backfill in batches, then set constraints).
- [ ] New indexes on large tables are built `CONCURRENTLY` (or the engine equivalent) so
      writes are not blocked.
- [ ] The migration is idempotent or guarded so a retry after partial failure is safe.
- [ ] A backup exists and a restore has been verified before any destructive step.

## Performance

- [ ] Every new or changed query on a large table has been run through `EXPLAIN
      (ANALYZE, BUFFERS)` against production-scale data.
- [ ] No sequential scan on a large table sits on a hot path; the driving predicate and
      join columns are indexed.
- [ ] Queries return only the needed columns and rows — no `SELECT *` shipped to the app
      to filter there.
- [ ] Pagination uses keyset/seek pagination, not large `OFFSET`, on big result sets.
- [ ] No N+1 pattern: related data is fetched with a join or batched, not per row.

## Transactions and Concurrency

- [ ] Writes that must be atomic are wrapped in a single transaction.
- [ ] The isolation level is chosen deliberately and matches the consistency the logic
      assumes.
- [ ] Transactions are short; no user think-time or external HTTP call happens inside one.
- [ ] Multi-row updates acquire locks in a consistent order to avoid deadlocks.
- [ ] `statement_timeout` and `lock_timeout` are set on the application role.

## Security and Access

- [ ] The application connects with a least-privilege role — not the schema owner, not a
      superuser.
- [ ] All values are parameterized; no SQL is built by string concatenation.
- [ ] Read-only workloads use a read-only role (and read replica where available).
- [ ] Secrets (connection strings, passwords) come from a secrets manager, not the repo.
- [ ] Access to PII columns is restricted and, where required, masked or encrypted.

## Operability

- [ ] Slow-query logging and `pg_stat_statements` (or equivalent) are enabled.
- [ ] Connection pooling is configured with a sane max that the database can serve.
- [ ] Backups run on a schedule and restores are tested, not assumed.
- [ ] Alerts exist for replication lag, connection saturation, and long-running queries.

## AI Review Checklist

- Does the change add or modify any query without an accompanying `EXPLAIN` result?
- Does any migration take a blocking lock on a large, hot table?
- Is there an `UPDATE`/`DELETE` whose `WHERE` clause was not verified?
- Does the app role hold more privilege than the change requires?
- Is there a rollback path, and has it actually been run once?

## Related

- `knowledge/sql/14-transactions.md`
- `knowledge/sql/15-indexes.md`
- `knowledge/sql/22-security.md`
- `knowledge/sql/23-performance.md`
- `knowledge/sql/30-engineering-principles.md`
