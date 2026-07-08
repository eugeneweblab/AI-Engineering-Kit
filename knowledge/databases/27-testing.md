---
id: databases/27-testing
topic: databases
slug: testing
title: "Testing"
type: doc
order: 27
status: ready
tags: [databases, testing]
related: [databases/17-migrations, databases/09-transactions, databases/23-data-integrity, databases/10-concurrency, databases/08-query-optimization]
when_to_use: "Read before writing tests that touch a database, or when deciding how to test schema, queries, and migrations."
---
# Testing

## Purpose

This document defines how to test code that touches a database so the tests are trustworthy,
fast, and catch real defects — schema mistakes, broken queries, migration failures, constraint
violations, and concurrency bugs. It covers what to test against (the real engine, not a fake),
how to isolate tests from each other, and how to test the things that only fail at the database
layer, like unique constraints, foreign keys, and transaction behavior.

The goal is confidence that the persistence layer behaves correctly under the same rules
production enforces. A test suite that mocks the database proves your mocks work, not your SQL.

## Why It Matters

Database bugs are the expensive kind: they corrupt data, and corrupted data outlives the deploy
that caused it. A missing unique constraint, a migration that works on an empty table but locks a
100M-row table in production, an off-by-one in an `UPDATE ... WHERE`, a race between two
transactions — none of these are caught by unit tests that mock the query layer. They are only
caught by exercising the actual engine with the actual schema. Tests that hit a real database also
double as living documentation of what the data layer guarantees. The trade-off is speed and setup
cost, which is why isolation strategy matters: done wrong, DB tests are slow and flaky; done right,
they are fast and deterministic.

## Core Principles

- **Test against the real engine you run in production.** Postgres behaves differently from SQLite
  on types, constraints, and SQL dialect. An in-memory substitute tests a different database.
- **Each test starts from a known state and leaves no trace.** Isolation is what makes DB tests
  deterministic; without it, order-dependent flakiness is guaranteed.
- **Test the database's guarantees, not just the happy path.** Unique violations, foreign-key
  failures, `NOT NULL`, check constraints, and rollback are behavior — assert them explicitly.
- **Test migrations as first-class code.** A migration that has never been run against
  production-like data and volume is an untested change. See [migrations](17-migrations.md).
- **Prefer fewer, higher-value integration tests over many mocked ones.** A mocked repository test
  passes even when the SQL is wrong.

## Best Practices

- Run tests against a **real, ephemeral instance** — a disposable container (e.g. Testcontainers)
  or a per-run local database — pinned to the same major version as production.
- Isolate with **transaction rollback** (wrap each test in a transaction, roll back at teardown)
  for speed, or **truncate/recreate** when a test needs its own transactions/commits. Pick per test.
- Seed deterministically: explicit fixtures or factories, no reliance on ambient/global data, and
  no dependence on test execution order.
- Assert on **constraint behavior**: write a test that inserts a duplicate and expects a unique
  violation, that inserts an orphan and expects a foreign-key error. These protect [data
  integrity](23-data-integrity.md).
- Test migrations both ways: apply `up`, assert the resulting schema and a data backfill, then apply
  `down` (or a re-run) and confirm it is safe. Run them against a copy with realistic volume.
- Test concurrency for anything with locking or upserts: run two transactions in parallel and assert
  the outcome (deadlock handling, last-writer, or serialization error). See [concurrency](10-concurrency.md).
- Keep query assertions behavioral (rows returned) but add EXPLAIN checks for hot queries when
  regressions matter. See [query optimization](08-query-optimization.md).

## Examples

**Good Example** — real engine, transaction isolation, constraint asserted

```ts
// One disposable Postgres, same major version as prod. Each test runs in a transaction
// that is rolled back, so tests are independent and leave no residue.
let tx: Client;
beforeEach(async () => { tx = await pool.connect(); await tx.query("BEGIN"); });
afterEach(async () => { await tx.query("ROLLBACK"); tx.release(); });

test("email uniqueness is enforced by the database", async () => {
  await tx.query("INSERT INTO users(email) VALUES ('a@x.io')");
  // Assert the DATABASE rejects the duplicate — not that our code remembered to check.
  await expect(
    tx.query("INSERT INTO users(email) VALUES ('a@x.io')")
  ).rejects.toThrow(/unique constraint/);
});
```

**Bad Example** — mocked DB, no isolation, tests the mock

```ts
test("creates a user", async () => {
  const db = { insert: jest.fn().mockResolvedValue({ id: 1 }) }; // fake: proves nothing about SQL
  await createUser(db, { email: "a@x.io" });
  expect(db.insert).toHaveBeenCalled();  // green even if the real query is malformed
  // No real engine, so the missing unique constraint and the bad migration ship undetected.
  // Tests also share global rows and depend on run order → flaky in CI.
});
```

## Common Mistakes

- Mocking the database or using SQLite when production is Postgres, hiding dialect/constraint bugs.
- Sharing state between tests, producing order-dependent, intermittently failing suites.
- Only testing the happy path, never asserting that constraints and rollbacks actually fire.
- Never running migrations against production-like volume, so a locking `ALTER` surprises prod.
- Not testing the `down`/rollback path of migrations, so a bad deploy can't be reverted safely.
- Ignoring concurrency, so deadlocks and lost updates appear only under real load.
- Slow suites from recreating the whole schema per test instead of using transaction rollback.

## Production Tips

- Gate merges on the DB integration suite in CI, running the same engine version as production.
- Keep a "prod-shaped" seed (representative volume and distribution) for migration and performance
  tests; empty tables hide lock and plan problems.
- Run migrations in CI against a restored copy of a production backup where possible. Coordinate
  with [backup and recovery](18-backup-and-recovery.md).
- Track and fail on flaky DB tests immediately — flakiness here usually means real isolation gaps.

## AI Review Checklist

- Do tests run against the same database engine and major version as production?
- Is each test isolated (transaction rollback or truncate) and independent of execution order?
- Are database guarantees asserted — unique, foreign-key, `NOT NULL`, check, rollback?
- Are migrations tested up and down, against production-like data volume?
- Is concurrency covered for code that locks, upserts, or serializes?
- Are tests behavioral against real SQL rather than assertions on mocked query methods?
- Does CI block merges when the database integration suite fails?

## Related

- `knowledge/databases/17-migrations.md`
- `knowledge/databases/09-transactions.md`
- `knowledge/databases/23-data-integrity.md`
- `knowledge/databases/10-concurrency.md`
- `knowledge/databases/08-query-optimization.md`
