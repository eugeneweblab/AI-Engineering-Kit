---
id: mysql/99-ai-review-checklist
topic: mysql
slug: ai-review-checklist
title: "MySQL AI Review Checklist"
type: checklist
order: 99
status: ready
tags: [mysql, ai-review-checklist, utf8mb4, InnoDB, FLOAT, DECIMAL, root, LIMIT]
related: [mysql/04-indexes, mysql/05-query-optimization, mysql/06-transactions, mysql/12-security, mysql/100-common-antipatterns]
when_to_use: "Read when reviewing any pull request that adds or changes MySQL schema, queries, or data-access code."
---
# MySQL AI Review Checklist

## Purpose

This is the checklist an AI agent runs when reviewing MySQL-related code: schema changes,
queries, transactions, and migrations. Each item is a concrete yes/no tied to a defect
class that causes data loss, corruption, or production slowdowns. Use it as a review gate,
not a style guide.

## Why It Matters

MySQL mistakes are hard to catch by eye and expensive to reverse. A missing index passes
every test at small scale and melts the server at large scale; a mis-scoped transaction
looks correct until two users hit it at once. A structured checklist catches these
classes before merge, when the fix is one line instead of an incident and a data-repair job.

## Schema and Types

**Rules:** [Data Types](03-data-types.md) · [Architecture](28-architecture.md)

- [ ] Does every new table use `InnoDB` and `utf8mb4`?
- [ ] Does every table have an explicit, compact primary key (not a random UUID)?
- [ ] Are `NOT NULL`, `UNIQUE`, and `CHECK` constraints applied wherever an invariant exists?
- [ ] Are foreign keys declared with an explicit `ON DELETE`/`ON UPDATE` action?
- [ ] Are columns the smallest correct type (money as `DECIMAL`/int, no `FLOAT`; no reflexive `VARCHAR(255)`)?
- [ ] Are timestamps stored in UTC?

## Queries and Indexes

**Rules:** [Query Optimization](05-query-optimization.md) · [Indexes](04-indexes.md)

- [ ] Can every `WHERE`, `JOIN`, and `ORDER BY` use an index, confirmed by `EXPLAIN`?
- [ ] Is the plan free of `type: ALL` (full scan) and `Using filesort`/`Using temporary` on large tables?
- [ ] Are queries parameterized, with no string-concatenated user input?
- [ ] Do `SELECT`s list explicit columns instead of `SELECT *` in application code?
- [ ] Is there no leading wildcard `LIKE '%x'` or function wrapping an indexed column (`WHERE DATE(col) = ?`) that defeats the index?
- [ ] Do large result sets use keyset pagination, not deep `OFFSET`?

## Transactions and Locking

**Rules:** [Transactions](06-transactions.md) · [Locking](07-locking.md)

- [ ] Is each transaction scoped to only the writes that must be atomic?
- [ ] Is there no network/API call or user wait held open inside a transaction?
- [ ] Do multi-statement transactions acquire locks in a consistent order to avoid deadlocks?
- [ ] Is deadlock retry handled (the app catches error 1213 and retries)?
- [ ] Is the isolation level appropriate and intentional (default `REPEATABLE READ` understood)?

## Migrations

**Rules:** [Migrations](16-migrations.md)

- [ ] Is the migration reversible, with a tested down path?
- [ ] Will it run online on a large table (no long metadata/exclusive lock)?
- [ ] Is it forward/backward compatible so the old and new app can both run mid-deploy?
- [ ] Does adding a `NOT NULL` column supply a default or backfill to avoid failing on existing rows?

## Security

**Rules:** [Security](12-security.md) · [Users And Roles](13-users-and-roles.md)

- [ ] Is all user input parameterized (no dynamic SQL) — no [injection](12-security.md) surface?
- [ ] Does the code use a least-privilege account, not `root`?
- [ ] Are credentials read from a secrets manager, not hard-coded?
- [ ] Are errors caught so raw SQL/schema details are not returned to the client?

## Correctness

**Rules:** [Testing](17-testing.md) · [Debugging](18-debugging.md)

- [ ] Are `NULL` semantics handled (`= NULL` is never true; use `IS NULL`)?
- [ ] Does `GROUP BY` list every non-aggregated selected column (no `ONLY_FULL_GROUP_BY` violation)?
- [ ] Are `DELETE`/`UPDATE` statements guaranteed to have a `WHERE` clause?
- [ ] Is `LIMIT` without `ORDER BY` avoided where ordering matters (rows are otherwise unordered)?

## Related

- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/12-security.md`
- `knowledge/mysql/100-common-antipatterns.md`
