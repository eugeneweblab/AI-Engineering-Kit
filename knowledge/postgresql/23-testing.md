---
id: postgresql/23-testing
topic: postgresql
slug: testing
title: "PostgreSQL Testing"
type: doc
order: 23
status: ready
tags: [postgresql, testing]
related: [postgresql/22-migrations, postgresql/06-transactions, postgresql/19-roles-and-permissions, postgresql/24-debugging, postgresql/25-best-practices]
when_to_use: "Read before writing tests that touch the database, setting up a test database/fixtures, or reviewing whether data-access code is actually covered."
---
# PostgreSQL Testing

## Purpose

This document defines how to test code that uses PostgreSQL: choosing between a real database
and a fake, isolating tests so they do not interfere, seeding deterministic data, and testing
the things only a real database reveals — constraints, transactions, migrations, and
concurrency. It is written so an agent can write database tests that are both trustworthy and
fast.

Testing is where [migrations](22-migrations.md) and privilege models
([roles and permissions](19-roles-and-permissions.md)) are proven before production, and it
leans on understanding [transactions](06-transactions.md) for isolation.

## Why It Matters

The bugs that hurt most in data-access code are the ones a mock cannot catch: a missing unique
constraint, a foreign key that does not cascade the way you assumed, a `NULL` that violates a
`CHECK`, a migration that fails on real data, a race under concurrent writes. If tests run
against an in-memory stub or a different database engine, they pass while production breaks —
the test proved the mock behaves, not that PostgreSQL does. At the same time, naive database
tests are slow and flaky: shared state leaks between tests, ordering matters, and a truncate-
everything teardown turns a fast suite into a crawl. The goal is tests that exercise *real*
PostgreSQL semantics while staying isolated and fast.

## Core Principles

- **Test against real PostgreSQL, not a mock or a different engine.** Constraints, types,
  transactions, and SQL dialect only behave correctly on the real thing. Spin up a disposable
  instance (Testcontainers, a CI service container, or a local instance) rather than SQLite.
- **Isolate every test.** No test may depend on data another test created or on execution
  order. Isolation is what makes a suite trustworthy and parallelizable.
- **Prefer transaction rollback for isolation; use truncate/recreate when you can't.** Wrap
  each test in a transaction and roll it back — fast and complete. Fall back to truncating
  tables when the code under test manages its own transactions.
- **Seed deterministically.** Fixtures and factories must produce the same data every run; no
  reliance on `now()`, random IDs, or leftover rows. Flaky data is worse than no test.
- **Test the database-specific behavior explicitly.** Assert that constraints reject bad data,
  that cascades fire, and that migrations apply cleanly — these are the reasons to use a real
  database at all.

## Best Practices

- Provision the test database from the *same migrations* that build production, so the schema
  under test is the real schema. Test the migrations themselves by running up (and, where you
  support it, down) in CI.
- Give each test worker its own database (or schema) so parallel runs cannot collide. A
  per-worker template database cloned with `CREATE DATABASE … TEMPLATE` is fast.
- Wrap each test in a transaction and `ROLLBACK` in teardown for instant, total cleanup. When
  the code opens its own transactions, switch that test to truncate-based cleanup instead.
- Use factories/builders for data, keyed off explicit values, not global fixtures that every
  test silently shares. Insert only the rows the test needs.
- Write positive *and* negative assertions: that a valid insert succeeds, and that a
  duplicate, a null, or a bad foreign key raises the expected error.
- Test with a least-privilege role matching production so a test also verifies the app role
  actually has the grants it needs (and RLS policies behave).
- Keep the suite fast: pool connections, reuse the template database, and avoid a full
  drop-and-recreate per test.

## Examples

**Good Example** — real DB, transaction rollback, constraint assertion

```sql
-- schema (applied via the same migrations as production)
CREATE TABLE users (
  id    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email text NOT NULL UNIQUE          -- the constraint we want to prove is enforced
);
```

```ts
// Each test runs inside a transaction that is rolled back → no leakage, no ordering deps.
beforeEach(async () => { await db.query("BEGIN"); });
afterEach(async () => { await db.query("ROLLBACK"); });

test("email uniqueness is enforced by the database", async () => {
  await db.query("INSERT INTO users (email) VALUES ($1)", ["a@x.com"]);

  // Negative assertion: the DB — not the app — must reject the duplicate.
  await expect(
    db.query("INSERT INTO users (email) VALUES ($1)", ["a@x.com"]),
  ).rejects.toMatchObject({ code: "23505" }); // 23505 = unique_violation
});
```

**Bad Example** — mock the database, assert nothing real

```ts
// The repository is stubbed, so this test passes even if the real UNIQUE constraint
// is missing, the migration is broken, or the column allows NULL. It proves the mock
// returns what we told it to — not that PostgreSQL enforces anything.
const db = { insertUser: jest.fn().mockResolvedValue({ id: 1 }) };
test("creates a user", async () => {
  const u = await createUser(db, "a@x.com");
  expect(u.id).toBe(1);            // green forever, regardless of real schema behavior
});
```

## Common Mistakes

- Mocking the database or substituting SQLite, so constraint/transaction/dialect bugs slip
  through to production.
- Tests that share state or depend on execution order, causing flakiness and blocking parallel
  runs.
- Non-deterministic fixtures (random data, `now()`, leftover rows) that pass and fail at random.
- Only asserting the happy path; never verifying that constraints reject bad data or that
  cascades fire.
- Never running migrations in tests, so a broken migration is discovered only in production.
- Testing as a superuser, so missing grants and RLS misconfigurations pass in tests and fail
  live ([roles and permissions](19-roles-and-permissions.md)).
- A slow drop-and-recreate per test that makes the suite so slow people stop running it.

## Production Tips

- Run the full migration set (and a representative seed) in CI on every PR, against the same
  PostgreSQL major version as production.
- Add at least one concurrency test for code that relies on locking or unique constraints —
  fire two writers and assert exactly one wins.
- Snapshot-test critical query plans (`EXPLAIN`) for hot paths so an accidental index-losing
  change is caught in review.

## AI Review Checklist

- Do tests run against real PostgreSQL (same major version), not a mock or SQLite?
- Is every test isolated via transaction rollback or truncate, with no ordering dependency?
- Is the test schema built from the same migrations as production, and are migrations tested?
- Is seed data deterministic (no random/time-dependent values or leftover rows)?
- Are there negative tests proving constraints, foreign keys, and RLS reject bad access?
- Do tests use a least-privilege role matching production, not a superuser?
- Is the suite fast enough (template DB, pooled connections) that it actually gets run?

## Related

- `knowledge/postgresql/22-migrations.md`
- `knowledge/postgresql/06-transactions.md`
- `knowledge/postgresql/19-roles-and-permissions.md`
- `knowledge/postgresql/24-debugging.md`
- `knowledge/postgresql/25-best-practices.md`
