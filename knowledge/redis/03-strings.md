---
id: redis/03-strings
topic: redis
slug: strings
title: "Strings"
type: doc
order: 3
status: ready
tags: [redis, strings, INCR, MGET, EXPIRE, KEEPTTL, INCRBYFLOAT, MSET]
related: [redis/02-data-types, redis/07-hashes, redis/12-expiration, redis/13-caching, redis/17-distributed-locks]
when_to_use: "Read before using Redis strings for counters, cached values, flags, or atomic set-if-absent locks."
---
# Strings

## Purpose

This document covers the Redis string — the simplest type and the most misused. A string
is a binary-safe byte sequence up to 512 MB that can also be treated as an integer or
float. Strings back counters, cached serialized values, feature flags, and the atomic
`SET NX` primitive behind distributed locks. This doc shows how to use them atomically and
how to avoid the read-modify-write races that plague naive usage.

## Why It Matters

Strings look trivial, so agents reach for `GET`/`SET` and rebuild logic in the client that
Redis already does atomically. The classic bug is a counter implemented as
`GET` → increment in code → `SET`: under concurrency, two clients read the same value and
one increment is lost. Redis's `INCR` eliminates that race because the whole operation runs
on the single thread. Knowing which native command replaces a client-side read-modify-write
is the core skill for strings.

## Core Principles

- **Use atomic commands, not read-modify-write.** `INCR`, `INCRBY`, `INCRBYFLOAT`,
  `APPEND`, `SETRANGE`, and `GETSET`/`SET ... GET` mutate atomically. Reading then writing
  from the client is a race.
- **Set expiry and existence conditions in one command.** `SET key val EX 60 NX` is atomic;
  a `SET` followed by a separate `EXPIRE` has a window where the key lives forever if the
  process dies between them.
- **Strings are for values, not structure.** If you update individual fields, use a
  [hash](07-hashes.md); if you need uniqueness or ranking, use a set / sorted set.
- **Watch value size.** A 512 MB ceiling is not a target — large strings mean large
  `O(N)` transfers that block the thread and saturate the network.

## Best Practices

- Implement counters with `INCR`/`INCRBY`, never `GET`+`SET`. This is atomic and cheap
  (`O(1)`).
- Use `SET key val EX <ttl> NX` to atomically create-with-expiry (the lock/idempotency
  pattern); see [Distributed Locks](17-distributed-locks.md).
- Prefer `SET key val KEEPTTL` when updating a value whose expiry must survive the write,
  instead of re-setting and accidentally clearing the TTL.
- Batch multi-key reads/writes with `MGET`/`MSET` or a pipeline to cut round trips.
- For cached serialized blobs, always attach a TTL so stale data self-evicts; see
  [Caching](13-caching.md).

## Examples

**Good Example** — atomic counter, atomic set-with-expiry

```redis
# Page-view counter: one atomic command, no lost updates under concurrency.
INCR page:home:views          # O(1), returns the new value

# Idempotency / lock token: create only if absent, with a TTL, atomically.
SET lock:order:99 "worker-3" EX 30 NX
# → "OK" if acquired, nil if already held. No race, no orphaned key:
#   the EX guarantees release even if worker-3 crashes.

# Update a cached value but preserve its remaining TTL.
SET cache:user:42 "<json>" KEEPTTL
```

**Bad Example** — client-side race, non-atomic expiry

```redis
# Lost-update race: two clients both read 10, both write 11.
GET page:home:views           # client reads "10"
# ... increments to 11 in application code ...
SET page:home:views "11"      # the other client's increment is gone

# Non-atomic lock: if the process dies between the two commands,
# the key has NO expiry and the lock is held forever.
SETNX lock:order:99 "worker-3"
EXPIRE lock:order:99 30        # separate command — a crash here orphans the lock
```

## Common Mistakes

- Building counters with `GET`+`SET` instead of `INCR`, losing updates under load.
- Using `SETNX` then a separate `EXPIRE`, leaving a window that orphans the key on crash.
- Re-`SET`ting a value and silently wiping its TTL (use `KEEPTTL` or set `EX` again).
- Storing an updatable record as a JSON string, forcing read-modify-write; use a hash.
- Letting values grow toward the 512 MB limit and blocking the thread on transfer.
- Doing N sequential `GET`s in a loop instead of one `MGET`/pipeline.

## Production Tips

- Monitor for hot keys: a single frequently-mutated counter can serialize load. If a
  counter is extremely hot, shard it across N keys and sum on read.
- Prefer `INCRBYFLOAT` for monetary/rate math only when precision is acceptable; for exact
  currency, keep integer minor units and use `INCRBY`.
- Cap value sizes in application code; reject oversized payloads before they reach Redis.

## AI Review Checklist

- Are counters implemented with `INCR`/`INCRBY` rather than client read-modify-write?
- Is create-with-expiry done in one `SET ... EX ... NX`, not `SETNX` + `EXPIRE`?
- Do value updates preserve TTL intentionally (`KEEPTTL`) where required?
- Are multi-key accesses batched with `MGET`/`MSET`/pipelines?
- Is an updatable record stored as a hash rather than a JSON string?
- Do cached string values carry a TTL, and are value sizes bounded?

## Related

- `knowledge/redis/02-data-types.md`
- `knowledge/redis/07-hashes.md`
- `knowledge/redis/12-expiration.md`
- `knowledge/redis/13-caching.md`
- `knowledge/redis/17-distributed-locks.md`
