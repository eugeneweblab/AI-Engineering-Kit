---
id: testing/03-integration-testing
topic: testing
slug: integration-testing
title: "Integration Testing"
type: doc
order: 3
status: ready
tags: [testing, integration-testing, UserRepository, findByEmail, toBe, mockResolvedValue]
related: [testing/02-unit-testing, testing/04-e2e-testing, testing/05-test-doubles, testing/12-api-testing, testing/11-contract-testing]
when_to_use: "Read before testing code that crosses a real boundary such as a database, HTTP call, or message queue."
---
# Integration Testing

## Purpose

This document defines how to test that units work correctly *together* across a real
boundary — a database, an HTTP service, a message broker, a filesystem. Integration tests
sit in the middle of the pyramid: fewer than unit tests, slower, but they catch the class
of bug unit tests cannot — wrong SQL, mismatched serialization, broken wiring. It is
written so an agent knows what to integrate, what to fake, and how to keep these tests
from becoming slow and flaky.

The target is the *seam*: the place two components meet and make assumptions about each
other. Unit tests verify each side alone; integration tests verify the handshake.

## Why It Matters

Most production incidents are not wrong arithmetic inside one function — they are seams
that drifted: a column renamed, a JSON field the consumer never handled, a timeout no one
set. Unit tests pass right through these because both sides were mocked to agree with each
other. Integration tests use the *real* dependency (or a faithful equivalent), so they
fail when reality disagrees with the code. That is exactly the confidence a mock cannot
give. The cost is speed and setup complexity, so you write few of them and choose the
seams that actually carry risk.

## Core Principles

- **Use the real thing at the boundary you are testing.** Test against a real Postgres,
  not an in-memory stand-in that behaves differently. The dialect *is* the risk.
- **Fake what you are not testing.** Replace third-party APIs and other services you do
  not own with controllable fakes; you cannot make a payment gateway deterministic.
- **Each test owns its data.** Set up the exact rows a test needs and tear them down, so
  tests do not leak state into each other. Order-dependence is a defect.
- **Test the seam, not the whole app.** Integration is narrower than E2E: exercise one
  boundary at a time so a failure localizes.
- **Determinism still rules.** Real dependencies introduce clocks, ordering, and network
  — control them or the suite goes flaky.

## Best Practices

- Run real infrastructure in ephemeral containers (Testcontainers or equivalent) so every
  developer and CI job gets an identical, disposable database or broker. Avoid a shared
  staging DB — concurrent tests corrupt each other.
- Isolate data per test: a transaction rolled back at teardown, a unique schema, or a
  truncate-between-tests strategy. Never assume an empty or pre-seeded table.
- Apply real migrations to the test database, so schema drift is caught here, not in prod.
- For services you do not own, use a fake honored by a [contract test](11-contract-testing.md)
  so the fake cannot silently diverge from the real API.
- Assert on observable effects through the boundary: the row that was written, the message
  that was published, the HTTP status returned. See [API testing](12-api-testing.md).
- Keep the count small and the seams high-value; lean on [unit tests](02-unit-testing.md)
  for logic and reserve integration tests for wiring and I/O.

## Examples

**Good Example** — real database in a container, isolated per test

```ts
// Uses a real Postgres via Testcontainers; each test runs in a rolled-back transaction,
// so the DB dialect is exercised and no state leaks between tests.
test("findByEmail returns the persisted user", async () => {
  await withRollback(async (db) => {
    const repo = new UserRepository(db);
    await repo.insert({ email: "a@example.com", name: "Ada" }); // real INSERT

    const found = await repo.findByEmail("a@example.com");       // real SELECT

    expect(found?.name).toBe("Ada"); // verifies the actual SQL round-trip
  });
});
```

**Bad Example** — mocks the boundary it claims to test, shared state

```ts
test("findByEmail returns the persisted user", async () => {
  const db = { query: jest.fn().mockResolvedValue([{ name: "Ada" }]) }; // fakes the DB
  const repo = new UserRepository(db);

  const found = await repo.findByEmail("a@example.com");

  // The real SQL is never executed. A typo in the query would still pass green.
  expect(found.name).toBe("Ada");
});
```

## Common Mistakes

- Mocking the database or HTTP client in a test whose whole purpose is the DB or HTTP
  interaction — it then verifies nothing about the seam.
- Sharing one long-lived database across tests, so results depend on run order and
  parallelism corrupts them.
- Substituting an in-memory or SQLite stand-in for a different production database — its
  differing SQL dialect and constraints hide real bugs.
- Hitting a live third-party API in CI, making the suite slow, rate-limited, and flaky —
  use a contract-verified fake.
- Skipping migrations in the test DB, so schema changes break only in production.
- Growing integration tests to cover logic that a unit test could pin down faster.

## Production Tips

- Spin infrastructure up once per test run and reuse the container across tests; recreate
  only the *data*, not the server, to keep the suite fast.
- Run integration tests as a separate CI stage from unit tests so a slow DB does not block
  fast feedback on every push.
- Tag and time these tests; when one gets slow or flaky, fix it immediately — tolerated
  flakiness spreads.

## AI Review Checklist

- Does the test use the real dependency at the boundary under test, not a mock of it?
- Is the production-equivalent technology used (same database engine, same broker)?
- Does each test set up and tear down its own data, with no cross-test leakage?
- Are third-party services replaced with contract-verified fakes, not live calls?
- Are real migrations applied to the test database?
- Is this seam better tested here than pushed up to a slower E2E test?

## Related

- `knowledge/testing/02-unit-testing.md`
- `knowledge/testing/04-e2e-testing.md`
- `knowledge/testing/05-test-doubles.md`
- `knowledge/testing/11-contract-testing.md`
- `knowledge/testing/12-api-testing.md`
