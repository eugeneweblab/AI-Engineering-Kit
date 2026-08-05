---
id: redis/24-testing
topic: redis
slug: testing
title: "Redis Testing"
type: doc
order: 24
status: ready
tags: [redis, testing]
related: [redis/25-debugging, redis/26-best-practices, redis/12-expiration, redis/13-caching, redis/17-distributed-locks]
when_to_use: "Read before writing or reviewing tests for any code that reads from or writes to Redis."
---
# Redis Testing

## Purpose

This document defines how to test code that depends on Redis so the tests are
trustworthy: they must catch real bugs (wrong data type, missing TTL, race in a
lock) without becoming slow, flaky, or coupled to a mock that lies about how Redis
behaves. It covers what to run against, how to isolate state, and which behaviours
are worth asserting.

## Why It Matters

Redis code fails in ways that unit tests with mocks never see: `SETEX` vs `SET`
semantics, `INCR` overflow, eviction under `maxmemory`, `WATCH`/`MULTI` aborts,
and TTL precision. A hand-written mock encodes your *assumptions* about Redis, so
it passes exactly when your assumptions are wrong. Because Redis is single-threaded
and fast, running tests against a real instance is cheap — there is little reason to
fake it. The cost of faking it is bugs that only appear in production.

## Core Principles

- **Test against a real Redis, not a mock.** Use an ephemeral instance
  (Testcontainers, or a throwaway container/`redis-server` in CI). Reserve mocks
  only for simulating connection failures you cannot easily produce.
- **Isolate every test's state.** Never share keys between tests. Use a dedicated
  database index or a unique key prefix, and clean up deterministically.
- **Make time controllable.** TTL and expiry tests must not depend on wall-clock
  sleeps. Assert on `PTTL`/`TTL`, or inject a clock so you can advance it.
- **Assert behaviour, not implementation.** Check the observable effect (value,
  type, TTL, membership), not the exact command sequence.
- **Cover the failure paths.** Test what happens when a key is missing, expired,
  the wrong type, or the connection drops — that is where real defects hide.

## Best Practices

- Prefer a fresh container per test suite and a `FLUSHDB` (not `FLUSHALL`) between
  tests, because it resets only the selected DB and cannot wipe an unrelated one.
- Give each test worker its own DB index (`SELECT n`) or a `test:{uuid}:` prefix so
  parallel runs cannot collide.
- For expiry logic, drive time explicitly: set a short TTL and assert `PTTL`, or use
  a fake clock in application code rather than `sleep(1)`, which is slow and flaky.
- Test type mismatches on purpose — e.g. `GET` on a key holding a list should raise
  `WRONGTYPE`; your error handling must survive it.
- For locks and rate limiters, write a concurrency test that runs N clients in
  parallel and asserts the invariant (only one holder; count never exceeds the cap).
- Keep integration tests hermetic: no dependency on a shared/staging Redis, whose
  state other jobs mutate.

## Examples

**Good Example** — real Redis, isolated, deterministic TTL assertion

```python
import pytest, redis
from testcontainers.redis import RedisContainer

@pytest.fixture
def r():
    with RedisContainer("redis:7.4") as c:          # real server, pinned version
        client = redis.Redis(host=c.get_container_host_ip(),
                             port=int(c.get_exposed_port(6379)), decode_responses=True)
        yield client
        client.flushdb()                            # reset only this DB, not FLUSHALL

def test_session_has_ttl(r):
    save_session(r, "sess:1", "u42", ttl=3600)
    assert r.get("sess:1") == "u42"
    # Assert the TTL was set, without sleeping for an hour.
    assert 3590 < r.pttl("sess:1") / 1000 <= 3600   # verifies expiry is applied
```

**Bad Example** — mock that lies, and a real sleep

```python
def test_session(mocker):
    fake = mocker.Mock()
    fake.get.return_value = "u42"        # mock always returns success...
    save_session(fake, "sess:1", "u42")  # ...so a missing SETEX / wrong TTL is never caught
    assert fake.get("sess:1") == "u42"

def test_expiry(r):
    r.set("k", "v", ex=1)
    time.sleep(1.1)                       # slow, and flaky under CI load
    assert r.get("k") is None
```

## Common Mistakes

- Mocking the Redis client, so the test passes even when the command or TTL is wrong.
- Using `FLUSHALL` in a shared environment and wiping another suite's data.
- `sleep()`-based expiry tests that are slow and intermittently fail under load.
- Sharing one Redis DB across parallel test workers, causing cross-test key collisions.
- Only testing the happy path, never the `WRONGTYPE`, missing-key, or dropped-connection cases.
- Asserting on the exact command sequence, so a harmless refactor breaks the test.

## Production Tips

- Run the same test suite against the Redis *major version* you deploy; behaviour of
  eviction and expiry differs across versions.
- Add a smoke test that runs against a Cluster-mode instance if you deploy clustered —
  cross-slot multi-key commands fail there and must be caught before release.
- Include a connection-loss test (kill the container mid-test) to verify retries and
  timeouts behave, not just the happy path.

## AI Review Checklist

- Do integration tests run against a real Redis, not a hand-written mock?
- Is state isolated per test (dedicated DB or unique prefix) and cleaned with `FLUSHDB`?
- Are TTL/expiry tests asserted via `PTTL`/`TTL` or a fake clock, not `sleep()`?
- Are failure paths (missing key, `WRONGTYPE`, dropped connection) covered?
- Do lock/rate-limit tests assert their invariant under real concurrency?
- Is the tested Redis version pinned to match production?

## Related

- `knowledge/redis/25-debugging.md`
- `knowledge/redis/26-best-practices.md`
- `knowledge/redis/12-expiration.md`
- `knowledge/redis/13-caching.md`
- `knowledge/redis/17-distributed-locks.md`
