---
id: sql/24-testing
topic: sql
slug: testing
title: "SQL Testing"
type: doc
order: 24
status: ready
tags: [sql, testing, accounts, UNIQUE, CHECK, EXPLAIN, LEFT, INNER]
related: [sql/25-debugging, sql/12-ddl, sql/14-transactions, sql/23-performance, sql/29-tooling]
when_to_use: "Read before writing a migration, a stored routine, or any query whose result other code depends on."
---
# SQL Testing

## Purpose

This document defines how to test SQL: schema migrations, queries, constraints,
and stored logic (procedures, triggers, views). It is written so an agent can add
tests that actually catch regressions instead of merely asserting that the database
is reachable.

SQL is code. A query that returns the wrong rows, a migration that silently drops a
column, or a constraint that never fires is a defect exactly like a bug in
application code — and it usually corrupts data permanently. Test it with the same
rigor.

## Why It Matters

Database bugs are expensive in a way application bugs are not: they persist. A bad
`UPDATE` writes wrong values to disk, and no redeploy undoes them. By the time a
reporting query reveals the damage, the correct values are gone. Tests are the only
practical way to catch these before they touch production data.

SQL also fails silently. A `JOIN` that should be an `INNER` written as a `LEFT`
returns *more* rows, not an error. A missing `WHERE` clause updates every row. A
`NULL` in a `NOT IN` list returns zero rows with no warning. None of these throw —
they just return wrong answers. Only an assertion on the *result* catches them.

## Core Principles

- **Test against the real engine.** Run tests on the same database product and major
  version as production (Postgres 16 vs SQLite are different languages). SQL dialects
  diverge on `NULL` handling, casting, and locking; a test on the wrong engine proves
  nothing. Spin up the real engine in a container.
- **Each test owns its data.** A test must create the rows it needs and assert on a
  known result. Tests that read whatever happens to be in a shared database are
  non-deterministic and worthless.
- **Roll back, don't clean up.** Wrap each test in a transaction and roll it back at
  the end. This is faster and more reliable than `DELETE` statements, which can leave
  orphans and fight foreign keys.
- **Assert on rows, not on "no error."** The failure mode is a wrong result, not an
  exception. Compare the actual result set to an expected one.
- **Test the constraint, not just the happy path.** For every `CHECK`, `UNIQUE`, `NOT
  NULL`, and foreign key, write a test that *violates* it and asserts the write fails.

## Best Practices

- Test **migrations in both directions** where a down/rollback exists: apply, assert
  the new shape, roll back, assert the old shape. A migration you cannot reverse in a
  test is one you cannot reverse in an incident.
- Seed fixtures with the **smallest data that expresses the case** — three rows, not a
  production dump. Large fixtures hide which row drives the assertion.
- Test **`NULL` behavior explicitly**: comparisons, `NOT IN`, aggregates that skip
  `NULL`, and `LEFT JOIN` misses. `NULL` is where most SQL correctness bugs live.
- Verify **query plans for hot paths** in CI (`EXPLAIN`) so an accidental sequential
  scan is caught as a test failure, not a 3 a.m. page. See
  [query-planning](16-query-planning.md).
- Test at **realistic scale for anything performance-sensitive** — behavior at 10 rows
  and 10 million rows differs (the planner switches strategies).
- Keep test data setup in **transactions with `ROLLBACK`**; only use `TRUNCATE ...
  CASCADE` for suites that must commit (e.g., testing triggers that fire on commit).

## Examples

**Good Example** — isolated, rolled back, asserts the constraint fires

```sql
-- Each test runs inside its own transaction and is rolled back, so tests
-- never see each other's data and the database is left untouched.
BEGIN;

  INSERT INTO accounts (id, email, balance) VALUES (1, 'a@x.com', 100);

  -- Assert the UNIQUE constraint on email actually rejects a duplicate.
  -- We expect this INSERT to FAIL; a passing INSERT is the bug.
  SAVEPOINT before_dup;
  INSERT INTO accounts (id, email, balance) VALUES (2, 'a@x.com', 0);
  -- If we reach here without error, the UNIQUE constraint is missing.
  ROLLBACK TO before_dup;

  -- Assert the query returns exactly the expected row set, not "some rows".
  SELECT id, balance FROM accounts WHERE balance > 50;  -- expect: (1, 100)

ROLLBACK;  -- leave the database exactly as we found it
```

**Bad Example** — shared state, no rollback, asserts only "it ran"

```sql
-- Runs against whatever rows already exist; result depends on test order.
INSERT INTO accounts (id, email, balance) VALUES (1, 'a@x.com', 100);
-- ^ fails on the second run because id=1 already exists from last time.

-- "Test" only checks the query executes, not that it returns the right rows.
SELECT * FROM accounts WHERE balance > 50;
-- No expected result → a query that returns wrong or zero rows still "passes".

-- No cleanup: this row pollutes every subsequent test.
```

## Common Mistakes

- Testing against SQLite (or a mock) when production is Postgres/MySQL — dialect and
  `NULL` semantics differ, so green tests hide real bugs.
- Sharing a database across tests without transaction rollback, making results depend
  on execution order.
- Asserting the query *ran* instead of asserting *which rows* it returned.
- Never testing constraint violations, so a dropped `UNIQUE` or `CHECK` ships
  unnoticed.
- Fixtures so large that no one can tell which row makes the assertion pass or fail.
- Testing correctness at 10 rows and assuming the plan holds at production scale.

## Production Tips

- Run the test suite against a container of the **exact production engine version**
  in CI; pin the tag so an engine upgrade is a deliberate, reviewed change.
- Add a **query-plan regression gate**: capture `EXPLAIN` for critical queries and
  fail CI if a plan degrades to a sequential scan or loses an index.
- Test **migrations on a copy of production-shaped data** (anonymized) before
  release; empty-schema tests miss lock and volume problems.

## AI Review Checklist

- Do tests run against the same database product and major version as production?
- Does each test create its own data and roll back, with no dependence on order?
- Does every test assert on the specific result set, not just "no error"?
- Is there a negative test for each `UNIQUE`, `CHECK`, `NOT NULL`, and foreign key?
- Is `NULL` behavior (`NOT IN`, `LEFT JOIN` misses, aggregates) tested explicitly?
- Are migrations tested apply-and-rollback, and hot-path query plans gated in CI?

## Related

- `knowledge/sql/25-debugging.md`
- `knowledge/sql/12-ddl.md`
- `knowledge/sql/14-transactions.md`
- `knowledge/sql/23-performance.md`
- `knowledge/sql/29-tooling.md`
