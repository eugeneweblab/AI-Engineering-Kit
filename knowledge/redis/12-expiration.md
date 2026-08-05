---
id: redis/12-expiration
topic: redis
slug: expiration
title: "Expiration"
type: doc
order: 12
status: ready
tags: [redis, expiration, TTL, EXPIRE, KEEPTTL, evicted_keys, maxmemory, random]
related: [redis/13-caching, redis/15-session-storage, redis/03-strings, redis/20-persistence, redis/23-performance]
when_to_use: "Read before setting TTLs, building caches, or debugging keys that vanish or never disappear."
---
# Expiration

## Purpose

This document defines how Redis expires keys: how to set a TTL, when Redis
actually deletes an expired key, and the correctness traps around expiry. It is
written so an agent can set lifetimes on keys without leaking memory, losing data
early, or creating race conditions.

Expiration is the mechanism that turns Redis from an ever-growing store into a
bounded one. Every caching, session, and rate-limiting pattern in this topic
depends on getting it right.

## Why It Matters

A key with no TTL lives until something explicitly deletes it. Forget the TTL on
a cache and memory grows without bound until `maxmemory` eviction starts
discarding *random* keys — including ones you needed. Set the TTL too short and
you thrash the backing store. Set it non-atomically and a crash between "write"
and "expire" leaves an immortal key.

Expiry is also subtle: Redis does not delete a key the instant it expires. It
deletes lazily (on access) and via a background sampler. An expired key still
occupies memory until one of those fires, and — critically — read commands treat
it as already gone. Misreading this leads to "phantom" bugs that only appear
under load.

## Core Principles

- **Every ephemeral key gets a TTL at creation, atomically.** Use `SET key val
  EX 3600`, not `SET` followed by `EXPIRE`. Two commands means a window where a
  crash leaves the key immortal.
- **A read never returns an expired value.** Once the TTL passes, `GET` returns
  `nil` even before the key is physically deleted. Expiry is logical, not
  physical.
- **Writes can wipe the TTL.** `SET` without `KEEPTTL` replaces the value *and*
  clears any existing expiry. Know which of your commands are TTL-preserving.
- **TTL is not a scheduler.** Redis does not fire an event you can reliably act
  on at the exact expiry moment. Do not build workflows that depend on
  millisecond-accurate expiry timing.
- **Persistence preserves absolute expiry time, not remaining TTL.** After a
  restart from RDB/AOF, keys expire at their original wall-clock deadline.

## Best Practices

- Set expiry atomically with the write: `SET`/`GETEX` options `EX`, `PX`,
  `EXAT`, `PXAT`, or `SET ... KEEPTTL` when updating a value in place.
- Use `EXAT`/`PXAT` (absolute Unix time) when the deadline is a fixed clock
  time (e.g. "expire at midnight"), so re-writes do not slide the deadline.
- Add jitter to TTLs on bulk-populated keys (e.g. `3600 + rand(0..300)`) so they
  do not all expire in the same second and stampede the backing store.
- Check `TTL key` (seconds) or `PTTL key` (ms) when debugging. `-1` means "no
  expiry"; `-2` means "key does not exist".
- Use `PERSIST key` to remove a TTL and make a key permanent — deliberately, not
  by accident via a bare `SET`.
- Enable keyspace notifications (`notify-keyspace-events Ex`) only if you truly
  need expiry events, and treat them as best-effort, not guaranteed delivery.

## Examples

**Good Example** — atomic write-with-TTL, TTL-preserving update, jitter

```bash
# Value and expiry set in one atomic command: no immortal-key window.
SET session:42 "<payload>" EX 1800          # expires in 30 min

# Update the value but keep the remaining TTL (do NOT reset the clock):
SET session:42 "<newpayload>" KEEPTTL

# Cache fill with jitter so 10k keys don't all expire in the same second:
#   ttl = 3600 + random(0..300)  -> computed in app code, passed as EX
SET cache:user:99 "<json>" EX 3712
```

**Bad Example** — non-atomic TTL, accidental TTL wipe

```bash
# Two commands: if the process crashes between them, the key never expires
# and silently leaks memory forever.
SET job:lock "worker-7"
EXPIRE job:lock 30

# Later, an "update" that quietly makes the key immortal:
# plain SET drops the TTL, so this lock now never releases.
SET job:lock "worker-7"        # BUG: TTL cleared -> permanent lock
```

## Common Mistakes

- Using `SET` then `EXPIRE` instead of `SET ... EX`, leaving a crash window that
  leaks immortal keys.
- Re-writing a key with plain `SET` and not realizing it cleared the TTL — the
  classic cause of locks and caches that never expire.
- Assuming an expired key frees memory immediately; it does not until lazy access
  or the active sampler removes it. `used_memory` can lag expiry under low read
  traffic.
- Building logic that fires "when the key expires" and trusting keyspace
  notifications for correctness — they are best-effort and lost on disconnect.
- Giving thousands of keys the identical TTL, causing a synchronized expiry
  stampede that hammers the database.
- Setting a TTL on a key you meant to keep forever (or vice versa) and never
  checking `TTL` in tests.

## Production Tips

- Watch `expired_keys` and `evicted_keys` in `INFO stats`. Rising `evicted_keys`
  means eviction — not expiry — is reclaiming memory; your TTLs or `maxmemory`
  need tuning.
- If many keys share a deadline, the active-expiry cycle can spike CPU. Spread
  deadlines with jitter and keep the `maxmemory-policy` set intentionally
  (`allkeys-lru` or `volatile-ttl` for caches).
- On replicas, expiry is driven by the primary (via `DEL`/`UNLINK` propagation)
  in older setups; ensure your version handles replica reads of logically-expired
  keys correctly and do not rely on a replica to independently expire.

## AI Review Checklist

- Is the TTL set atomically with the write (`SET ... EX`), never as a separate
  `EXPIRE`?
- Does every value update use `KEEPTTL` (or intentionally reset the TTL) rather
  than silently wiping it?
- Do bulk-populated keys use jittered TTLs to avoid synchronized expiry?
- Does the code avoid depending on keyspace notifications for correctness?
- Are absolute deadlines expressed with `EXAT`/`PXAT` so re-writes don't slide
  them?
- Do tests assert `TTL`/`PTTL` for keys that must (or must not) expire?

## Related

- `knowledge/redis/13-caching.md`
- `knowledge/redis/15-session-storage.md`
- `knowledge/redis/03-strings.md`
- `knowledge/redis/20-persistence.md`
- `knowledge/redis/23-performance.md`
