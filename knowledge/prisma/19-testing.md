---
id: prisma/19-testing
topic: prisma
slug: testing
title: "Prisma Testing"
type: doc
order: 19
status: ready
tags: [prisma, testing, PrismaClient, toBe, executeRawUnsafe, afterAll, disconnect, toMatchObject]
related: [prisma/05-migrations, prisma/12-seeding, prisma/08-transactions, prisma/20-debugging]
when_to_use: "Read before writing tests for any code that queries the database through Prisma."
---
# Prisma Testing

## Purpose

This document defines how to test code that uses Prisma Client: what to run against a
real database, what to mock, how to isolate tests from one another, and how to keep the
suite fast and deterministic. The goal is tests that fail when the query is wrong and
pass when it is right — nothing else.

## Why It Matters

Prisma's value is that it talks to a real database with real constraints, indexes, and
SQL semantics. A test that mocks `prisma.user.findMany` proves only that you called a
function you already stubbed — it cannot catch a broken `where` clause, a missing unique
index, a cascade you forgot, or a query that returns the wrong shape. Those are exactly
the bugs Prisma code has. Meanwhile a suite that shares one database across tests without
isolation produces flaky, order-dependent failures that erode trust until people stop
reading them. Getting the boundary right — real DB for query logic, isolation per test —
is what makes the suite worth running.

## Core Principles

- **Test queries against a real database.** Use a disposable Postgres (Docker or
  Testcontainers) that matches production, not SQLite and not a mock.
- **Isolate every test.** Each test must start from a known state and leave no trace.
  Transaction rollback or truncation between tests, never "hope the order works out".
- **Migrate, don't push, for the test schema.** Run `prisma migrate deploy` so the test
  DB is byte-identical to production's schema history.
- **Mock only to test error handling.** A mocked client is acceptable to simulate a
  thrown `P2002`; it is not acceptable to "verify" a `where` clause.
- **One client per suite, closed at the end.** Reuse the connection pool; call
  `$disconnect()` in teardown so the process exits cleanly.

## Best Practices

- Spin up the database with **Testcontainers** so CI and laptops get the same isolated
  instance; point `DATABASE_URL` at it and run `prisma migrate deploy` before the suite.
- Isolate with one of: wrap each test in a transaction and roll back (fastest, but no
  nested-transaction code under test), or `TRUNCATE ... RESTART IDENTITY CASCADE` all
  tables between tests (robust, slightly slower). Pick one and apply it uniformly.
- Seed only the rows a test needs, inside the test, so the arrange step documents the
  precondition. Keep global seed data minimal and immutable.
- For unit tests of pure logic that merely *receives* rows, inject an interface, not the
  client — then no database is needed at all.
- When you must mock the client (e.g. asserting your code maps `P2025` to a 404), use a
  typed mock so a schema change breaks the test instead of silently drifting.
- Run integration tests in a separate CI job with the DB service; keep them off the
  fast unit path so the inner loop stays quick.

## Examples

**Good Example** — real DB, per-test isolation, assert on stored state

```ts
import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient } from "@/generated/prisma/client";

const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL! });
const prisma = new PrismaClient({ adapter });

beforeEach(async () => {
  // Deterministic starting point: every test owns the whole schema, fresh.
  await prisma.$executeRawUnsafe(`TRUNCATE "User" RESTART IDENTITY CASCADE`);
});
afterAll(() => prisma.$disconnect()); // release the pool so the runner exits

test("create rejects a duplicate email via the unique index", async () => {
  await prisma.user.create({ data: { email: "a@x.com" } });

  // Exercises the REAL unique constraint — a mock could never catch a missing index.
  await expect(
    prisma.user.create({ data: { email: "a@x.com" } })
  ).rejects.toMatchObject({ code: "P2002" });

  const count = await prisma.user.count();
  expect(count).toBe(1); // assert on persisted state, not on a call spy
});
```

**Bad Example** — mocked client that tests nothing real

```ts
const prisma = { user: { findFirst: vi.fn() } } as any;

test("returns the active user", async () => {
  prisma.user.findFirst.mockResolvedValue({ id: 1, active: true });

  const user = await getActiveUser(prisma, 1);

  // This only proves the stub returns what we told it to. A wrong `where`,
  // a missing index, or a bad relation would all still pass green.
  expect(user.active).toBe(true);
  expect(prisma.user.findFirst).toHaveBeenCalled(); // asserting the mock, not behavior
});
```

## Common Mistakes

- Testing against SQLite while running Postgres in production — different SQL, different
  constraint behavior, false confidence.
- Sharing one database across tests with no reset, producing order-dependent flakiness.
- Mocking `prisma` and asserting on call spies, so query logic is never exercised.
- Using `prisma db push` for the test schema, diverging from the migration history.
- Forgetting `$disconnect()` in teardown, leaving the test process hanging on open pools.
- Seeding a large shared fixture that every test mutates, coupling tests invisibly.

## Production Tips

- Run migrations as a CI step before tests so a broken migration fails fast, separately
  from a broken query.
- Parallelize by giving each worker its own database (or schema) so isolation is free;
  Testcontainers makes this cheap.
- Keep a small `factory` layer that builds valid rows with sensible defaults, so tests
  specify only the fields they care about.

## AI Review Checklist

- Do integration tests run against a real Postgres that matches production, not SQLite?
- Is each test isolated by transaction rollback or truncation, with no shared mutable state?
- Is the test schema created with `prisma migrate deploy`, not `db push`?
- Are assertions made on persisted state, not on mock call spies?
- Is mocking limited to simulating thrown errors, using a typed mock?
- Is `$disconnect()` called in teardown so the runner exits cleanly?

## Related

- `knowledge/prisma/05-migrations.md`
- `knowledge/prisma/12-seeding.md`
- `knowledge/prisma/08-transactions.md`
- `knowledge/prisma/20-debugging.md`
