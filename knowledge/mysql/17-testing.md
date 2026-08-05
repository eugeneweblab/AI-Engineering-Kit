---
id: mysql/17-testing
topic: mysql
slug: testing
title: "MySQL Testing"
type: doc
order: 17
status: ready
tags: [mysql, testing]
related: [mysql/16-migrations, mysql/06-transactions, mysql/05-query-optimization, mysql/14-performance]
when_to_use: "Read before writing tests that touch MySQL, or reviewing a test suite's database setup, isolation, and teardown."
---
# MySQL Testing

## Purpose

This document defines how to test code that talks to MySQL so the tests are
correct, isolated, fast, and trustworthy: what to test against, how to keep tests
independent, and how to catch database bugs — bad SQL, wrong indexes, broken
migrations — before production. It is written so an agent can build a database
test suite that actually protects the schema and queries it covers.

Migrations are validated with the same discipline described here; see
[migrations](16-migrations.md). Transaction and isolation behavior that tests must
respect lives in [transactions](06-transactions.md).

## Why It Matters

Database bugs are the ones mocks hide. A test that stubs the repository proves the
mock works, not that the SQL is valid, the index is used, or the migration applies.
Those failures surface only against a real MySQL engine — and if not in CI, then in
production. At the same time, careless database tests are the flakiest tests a team
owns: shared state, order dependence, and leftover rows produce failures that pass
on retry and erode trust in the whole suite. Getting isolation right is what makes
database testing worth doing.

## Core Principles

- **Test against real MySQL, not a substitute.** SQLite or an in-memory fake has
  different SQL, types, and locking. Use the same MySQL version as production so the
  test exercises the real engine.
- **Every test is isolated and order-independent.** A test must set up its own data
  and leave no trace. Tests that share state fail intermittently and block parallelism.
- **Roll back or truncate between tests.** Wrap each test in a transaction rolled back
  at teardown, or truncate tables — never rely on tests running in a fixed order.
- **Migrations are code under test.** Apply migrations to a clean database in CI so a
  broken or non-idempotent migration fails the build, not the deploy.
- **Assert on behavior, not incidental state.** Verify the rows and effects the code
  promises, not internal ordering or auto-increment values that may legitimately change.

## Best Practices

- Spin up a disposable MySQL matching the production version — Testcontainers or a
  dedicated CI service container — and run the real schema against it.
- Isolate each test by opening a transaction in setup and rolling it back in teardown;
  it is faster than re-truncating and guarantees a clean slate.
- Build fixtures with factories/builders that create only the rows a test needs, so
  intent is visible and tests do not depend on a shared seed dump.
- Apply the full migration chain from empty in CI on every run; this tests the
  migrations themselves and keeps the test schema honest.
- Test the SQL that matters: constraint violations (unique, FK), transaction rollback,
  concurrent-update/locking behavior, and that hot queries use their index via `EXPLAIN`.
- Keep the suite deterministic: no reliance on wall-clock ordering, no shared mutable
  rows between tests, and fixed inputs for anything time- or random-dependent.
- Run independent tests in parallel against separate schemas/transactions to keep the
  suite fast; slow DB suites get skipped, and skipped tests protect nothing.

## Examples

**Good Example** — real MySQL, per-test transaction rollback

```python
# Each test runs inside a transaction that is rolled back at teardown, so tests are
# fully isolated and order-independent — no leftover rows, no shared state.
@pytest.fixture
def db(mysql_container):                      # real MySQL, prod version, migrated
    conn = connect(mysql_container.dsn)
    conn.begin()
    yield conn
    conn.rollback()                           # undo everything this test did
    conn.close()

def test_unique_email_is_rejected(db):
    db.execute("INSERT INTO users (email) VALUES (%s)", ("a@x.com",))
    # Assert on the promised behavior: the second insert must violate the constraint.
    with pytest.raises(IntegrityError):
        db.execute("INSERT INTO users (email) VALUES (%s)", ("a@x.com",))
```

**Bad Example** — shared state, order-dependent, mocked engine

```python
# Uses a global connection with no isolation: rows from one test leak into the next,
# so tests only pass in a particular order and fail randomly under parallelism.
def test_create_user():
    GLOBAL_DB.execute("INSERT INTO users (email) VALUES ('a@x.com')")  # never cleaned up

def test_count_users():
    # Depends on the previous test having inserted a row — brittle and false-green
    # if run alone. And if GLOBAL_DB were a mock, it would test nothing real at all.
    assert GLOBAL_DB.query("SELECT COUNT(*) FROM users") == 1
```

## Common Mistakes

- Testing against SQLite or a mock, so real SQL, type, and locking bugs slip through.
- Sharing a database across tests without rollback/truncate, causing order dependence.
- Leaving rows behind in teardown, so the suite passes clean but fails on rerun.
- Never applying migrations in CI, so a broken migration is found during deploy.
- Asserting on auto-increment ids or row order that MySQL does not guarantee.
- Depending on wall-clock time or randomness, producing flaky pass/fail.
- A DB suite so slow it gets marked skip in CI, protecting nothing.

## Production Tips

- Pin the test MySQL image to the exact production major/minor version and bump them
  together, so tests catch version-specific behavior changes.
- Add a CI job that applies migrations to an empty DB and then loads a production-shaped
  data volume, catching lock and performance regressions early. See [performance](14-performance.md).
- Include at least one concurrency test (two transactions contending) so deadlock and
  isolation handling is covered, not assumed.

## AI Review Checklist

- Do tests run against real MySQL at the production version, not SQLite or a mock?
- Is each test isolated via transaction rollback or truncation, and order-independent?
- Does teardown leave the database clean so reruns and parallel runs pass?
- Are migrations applied from empty in CI to test the migrations themselves?
- Do tests cover constraints, rollback, locking/concurrency, and index usage?
- Are tests deterministic — no reliance on clock, randomness, or auto-increment values?
- Is the suite fast enough to run every build, not skipped for slowness?

## Related

- `knowledge/mysql/16-migrations.md`
- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/14-performance.md`
