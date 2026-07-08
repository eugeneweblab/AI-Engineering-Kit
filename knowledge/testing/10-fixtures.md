---
id: testing/10-fixtures
topic: testing
slug: fixtures
title: "Fixtures"
type: doc
order: 10
status: ready
tags: [testing, fixtures]
related: [testing/07-test-data, testing/08-test-organization, testing/03-integration-testing, testing/22-flaky-tests, testing/20-test-maintenance]
when_to_use: "Read before adding setup/teardown or shared state that more than one test depends on."
---
# Fixtures

## Purpose

This document defines how to manage the *lifecycle* of test setup and teardown — the code
that provisions a resource before a test and cleans it up after. Fixtures cover database
connections, temp directories, spun-up containers, a seeded clock, or an authenticated
client. It is distinct from [test data](07-test-data.md), which is about *constructing the
values*; a fixture is about *setting up and tearing down the environment* those values live
in.

The core tension of fixtures is sharing versus isolation: sharing an expensive resource
makes tests fast, but shared *state* makes them coupled and flaky. Getting this boundary
right is what a good fixture does.

## Why It Matters

Fixtures sit on the critical path of every test that uses them, so they drive both speed
and reliability. Recreate an expensive resource per test and the suite crawls; share
mutable state across tests and you get order-dependent [flaky failures](22-flaky-tests.md)
that pass in isolation and fail in the suite — the hardest class of test bug to diagnose.
And a fixture that fails to tear down leaks resources (open connections, temp files, stray
containers) that eventually break CI for reasons unrelated to any test. Fixtures are shared
infrastructure: a mistake in one is a mistake in every test that touches it.

## Core Principles

- **Share the connection, isolate the state.** Reuse the expensive handle (DB pool,
  browser, container) across tests; give each test a clean slate *within* it via
  transactional rollback or truncation.
- **Teardown must be guaranteed.** Register cleanup so it runs even when the test throws
  (`afterEach`, `try/finally`, `yield`). A leaked resource is a future flaky failure.
- **Scope fixtures as narrowly as correctness allows.** Prefer per-test; widen to
  per-suite only for genuinely expensive, read-only resources, and document why.
- **A fixture is invisible plumbing, not a test.** It provisions and cleans; it must not
  contain assertions or branching logic that belongs in a test.
- **Fixtures compose.** Build small, single-purpose fixtures (a db, a clock, a user) and
  combine them, rather than one god-fixture that sets up everything.

## Best Practices

- Use per-test transactions with rollback in teardown for database tests — it is faster
  than truncating and immune to leftover rows from a crashed test.
- Provision heavy external dependencies (Postgres, Kafka) once per run with an ephemeral
  container, and reset their *data* per test — share the process, not the state.
- Return the fixture's resource explicitly (a value, not a global) so a test's dependencies
  are visible in its signature, not hidden in ambient state.
- Make teardown idempotent and defensive: it may run after a partial setup, so it must
  tolerate a half-created resource.
- Fail loudly if setup can't complete; a fixture that silently yields a broken resource
  turns into a confusing assertion failure deep inside the test.
- Keep fixture scope explicit in the framework's terms (`function`/`module`/`session` in
  pytest, `beforeEach`/`beforeAll` in JS) and default to the narrowest.

## Examples

**Good Example** — shared connection, isolated state, guaranteed cleanup

```python
# Connection is created ONCE per session (expensive); each test gets a clean slate.
@pytest.fixture(scope="session")
def db():
    conn = connect(TEST_DATABASE_URL)
    yield conn
    conn.close()  # teardown runs even if a test fails, thanks to yield

@pytest.fixture()
def session(db):
    tx = db.begin()      # per-test transaction
    yield tx
    tx.rollback()        # every test starts from the same clean state — no leakage

def test_creates_user(session):
    repo = UserRepo(session)
    repo.add(a_user(email="x@example.com"))
    assert repo.count() == 1  # unaffected by any other test's writes
```

**Bad Example** — shared mutable state, no isolation, leaky teardown

```python
# Module-scoped connection AND data: tests see each other's rows.
db = connect(TEST_DATABASE_URL)

def test_creates_user():
    UserRepo(db).add(a_user(email="x@example.com"))
    assert UserRepo(db).count() == 1  # passes alone...

def test_starts_empty():
    # ...fails when test_creates_user ran first: leftover row from the previous test.
    assert UserRepo(db).count() == 0
    # No teardown anywhere — the connection and rows leak into the next test file.
```

## Common Mistakes

- Sharing mutable state (rows, files, globals) across tests, causing order dependence.
- Teardown that only runs on the happy path, so a thrown test leaks its resource.
- Recreating an expensive resource per test when a per-session share with state reset works.
- Over-broad fixture scope that couples unrelated tests to one setup.
- God-fixtures that provision everything, so a test's real dependencies are invisible.
- Assertions or conditional logic hidden inside a fixture instead of in the test.

## Production Tips

- Reset external state per test rather than trusting a clean starting environment — CI
  runners are reused and never start pristine.
- Cap and monitor fixture setup time; a slow session-scoped fixture is a hidden tax on the
  whole suite (see [test maintenance](20-test-maintenance.md)).
- In CI, provision heavy dependencies as ephemeral containers so runs are hermetic and no
  test depends on a shared, long-lived server.

## AI Review Checklist

- Is expensive setup shared while per-test *state* is isolated (rollback or reset)?
- Does teardown run even when the test throws (yield / afterEach / finally)?
- Is each fixture scoped as narrowly as correctness allows?
- Are dependencies passed to the test explicitly rather than through ambient globals?
- Is teardown idempotent and tolerant of a partially completed setup?
- Is the fixture free of assertions and test-level branching?

## Related

- `knowledge/testing/07-test-data.md`
- `knowledge/testing/08-test-organization.md`
- `knowledge/testing/03-integration-testing.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/20-test-maintenance.md`
