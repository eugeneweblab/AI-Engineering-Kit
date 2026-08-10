---
id: sql/99-ai-review-checklist
topic: sql
slug: ai-review-checklist
title: "SQL AI Review Checklist"
type: checklist
order: 99
status: ready
tags: [sql, ai-review-checklist, EXPLAIN, SERIALIZABLE, NUMERIC, DECIMAL, OFFSET, CHECK, approving, migration, diff]
related: [sql/17-query-optimization, sql/22-security, sql/24-testing, sql/25-debugging, sql/30-engineering-principles]
when_to_use: "Read when reviewing any SQL diff — schema, query, or migration — before approving it."
---
# SQL AI Review Checklist

## Purpose

A focused checklist for an agent reviewing SQL: a schema change, a query, or a
migration. It concentrates on the mistakes that pass tests but fail in production —
correctness under concurrency, performance at scale, and data safety. Each item is a
yes/no an agent can confirm by reading the diff, running `EXPLAIN`, or checking the
surrounding code. Report any "no" as a blocking finding with the reason.

## Why It Matters

SQL defects are the expensive kind: they corrupt or lose data that cannot be
regenerated, and they often surface long after the change merged, when data volume or
concurrency crosses a threshold. Review is the last cheap place to catch them. A
disciplined pass over these items catches the injection, the missing index, and the
unbounded `UPDATE` that automated tests routinely miss.

## Correctness

**Rules:** [Joins](05-joins.md) · [Aggregate Functions](09-aggregate-functions.md)

- [ ] Does every `UPDATE`/`DELETE` have a `WHERE` clause, and is it the intended set?
- [ ] Are `JOIN` conditions complete, so no accidental cross join (Cartesian product)
      inflates rows?
- [ ] Is `NULL` handled correctly — no equality (`= NULL`) instead of `IS NULL`, and
      awareness that `NOT IN` with a NULL member returns no rows?
- [ ] Do aggregates account for `NULL` (which `COUNT(col)` skips) and for empty groups?
- [ ] Does `GROUP BY` list every non-aggregated selected column?
- [ ] Are floating types avoided for money in favor of `NUMERIC`/`DECIMAL`?

## Security

**Rules:** [Security](22-security.md)

- [ ] Are all user-supplied values parameterized, with zero string concatenation into SQL?
- [ ] Do dynamic identifiers (table/column names) come from an allowlist, never raw input?
- [ ] Does the query run with least privilege, not as a schema owner or superuser?
- [ ] Are PII/secret columns excluded from logs and from broad `SELECT *`?

## Performance

**Rules:** [Query Optimization](17-query-optimization.md) · [Indexes](15-indexes.md)

- [ ] Has the query been checked with `EXPLAIN` against realistic row counts?
- [ ] Is the driving predicate sargable — no function wrapping an indexed column
      (`WHERE date(col) = ...`) that defeats the index?
- [ ] Are the columns used in filters, joins, and sorts actually indexed?
- [ ] Is `SELECT *` replaced by the specific columns needed?
- [ ] Does pagination use keyset seek, not deep `OFFSET`?
- [ ] Is there no N+1 loop where a single join or batch would do?

## Transactions and Concurrency

**Rules:** [Transactions](14-transactions.md)

- [ ] Are writes that must be atomic inside one transaction?
- [ ] Is the isolation level correct for the assumed consistency (e.g. does a
      read-modify-write need `SERIALIZABLE` or `SELECT ... FOR UPDATE`)?
- [ ] Are locks taken in a consistent order to prevent deadlocks?
- [ ] Is the transaction free of external calls that would hold locks during I/O?

## Migrations

**Rules:** [DDL](12-ddl.md) · [DML](13-dml.md)

- [ ] Is the migration reversible, with a tested rollback?
- [ ] Does it avoid long blocking locks on hot tables (batched backfill, concurrent
      index build, nullable-then-constrain)?
- [ ] Is it safe to run against the current production data (existing rows satisfy any
      new `NOT NULL`/`CHECK`)?
- [ ] Is it idempotent or guarded against partial-failure retry?

## AI Review Checklist

- Did I run or request an `EXPLAIN` for every non-trivial query in the diff?
- Did I confirm no value reaches SQL by concatenation?
- Did I verify each `UPDATE`/`DELETE` boundary, not assume it?
- Did I check that new constraints hold for existing rows before approving the migration?

## Related

- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/22-security.md`
- `knowledge/sql/24-testing.md`
- `knowledge/sql/25-debugging.md`
- `knowledge/sql/30-engineering-principles.md`
