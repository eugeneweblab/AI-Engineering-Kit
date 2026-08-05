---
id: redis/26-best-practices
topic: redis
slug: best-practices
title: "Redis Best Practices"
type: doc
order: 26
status: ready
tags: [redis, best-practices, SCAN, MGET, maxmemory, hset, dumps, expire]
related: [redis/12-expiration, redis/13-caching, redis/23-performance, redis/27-production, redis/100-common-antipatterns]
when_to_use: "Read before writing any new Redis access code or reviewing how an app uses Redis."
---
# Redis Best Practices

## Purpose

This document defines the day-to-day rules for using Redis well: how to name keys,
pick data types, control memory, and structure access so the application is fast,
predictable, and cheap to operate. It is the baseline every Redis-touching change
should satisfy before more specialised concerns (locks, streams, clustering) apply.

## Why It Matters

Redis rewards discipline and punishes convenience. It holds data in RAM and runs
commands on a single thread, so a careless key ("cache everything forever") or a
lazy command (`KEYS *`) quietly becomes an outage: memory fills, eviction thrashes,
and one O(N) call blocks every client. None of this shows up in a code review that
only checks correctness. These practices exist because the failure mode is
operational, delayed, and system-wide — exactly the kind an agent must prevent up front.

## Core Principles

- **Every key needs an eviction story.** Either it has a TTL, or it is bounded and
  intentionally persistent. An unbounded, never-expiring keyspace is a memory leak.
- **Pick the data type that models the access.** A sorted set for a leaderboard, a
  hash for an object, a set for membership — not a JSON blob you re-parse each read.
- **Never scan the whole keyspace on a hot path.** `KEYS` and unbounded ranges are
  O(N) and block the server; use `SCAN` and bounded ranges.
- **Batch round-trips.** Pipeline or use multi-key commands so latency is one RTT,
  not N. Network round-trips, not Redis itself, are usually the bottleneck.
- **Namespace keys predictably.** `app:entity:id[:field]` makes keys greppable,
  debuggable, and safe to scan or expire by pattern.

## Best Practices

- Use a consistent key schema like `service:object:id`, e.g. `auth:session:{id}`.
  Colons are convention, and a stable prefix lets you `SCAN MATCH` and reason about
  ownership. Keep keys short — the name is stored per key and multiplies at scale.
- Set a TTL at write time (`SET k v EX 3600`) rather than in a second command, so a
  crash between the two cannot leave an immortal key.
- Prefer `SCAN`/`HSCAN`/`SSCAN` with a `COUNT` hint over `KEYS`/`SMEMBERS` on large
  collections, because they yield in small O(1)-ish chunks instead of blocking.
- Pipeline independent writes/reads; use `MGET`/`HMGET`/`MSET` for multi-key access.
  The cost of pipelining is you must not depend on seeing earlier results mid-batch.
- Keep values small (target < 100 KB, hard-avoid multi-MB). Split big collections;
  a single huge key blocks the thread on every access and complicates eviction.
- Reuse a connection pool sized to your concurrency; opening a connection per command
  destroys throughput. Set explicit socket and command timeouts.
- Use `SETNX`/`SET ... NX` and Lua for atomicity instead of read-modify-write races.

## Examples

**Good Example** — typed structure, TTL at write, pipelined reads

```python
# Model a user object as a hash, not a re-parsed JSON string.
pipe = r.pipeline()
pipe.hset("user:42", mapping={"name": "Ada", "plan": "pro"})
pipe.expire("user:42", 86400)          # bounded lifetime — key cannot leak
pipe.execute()                          # one round trip, not two

# Read many keys in a single RTT instead of a loop of GETs.
names = r.mget("user:42:name", "user:43:name")   # batched: latency = 1 RTT
```

**Bad Example** — blob values, no TTL, per-key round trips, KEYS scan

```python
import json
r.set("user:42", json.dumps({"name": "Ada"}))   # opaque blob; whole value rewritten per change
# no EXPIRE anywhere -> key lives forever -> memory grows unbounded

# N separate round trips, one per user — latency scales with N.
names = [r.get(k) for k in user_keys]

# O(N) over the entire keyspace, blocking every other client while it runs.
stale = r.keys("user:*")                          # use SCAN instead
```

## Common Mistakes

- Storing large JSON blobs and rewriting the whole value to change one field.
- Keys with no TTL and no size bound, so memory grows until eviction or OOM.
- `KEYS pattern` in application code instead of `SCAN`.
- A loop of single-key commands where a pipeline or `MGET` would do one round trip.
- Opening a new connection per request rather than using a pool.
- Encoding structure into the key value (`user:42:name:Ada`) instead of using hashes/sets.
- Read-modify-write on a counter or set without `INCR`/`SADD`/Lua, creating a race.

## Production Tips

- Set `maxmemory` and an eviction policy (`allkeys-lru` for a pure cache,
  `noeviction` for a datastore of record) so behaviour under pressure is defined.
- Track the cache hit ratio and evicted-key count; a falling hit ratio means the
  working set no longer fits and TTLs or sizing need attention.
- Add jitter to TTLs of items created together to avoid a synchronized expiry
  stampede that hammers the backing store.

## AI Review Checklist

- Does every written key get a TTL or is it explicitly bounded?
- Is the data type chosen to fit the access pattern (hash/set/zset), not a JSON blob?
- Is `SCAN` used instead of `KEYS` for any pattern lookup?
- Are multi-key operations pipelined or batched rather than looped?
- Are values kept small, with no unbounded-growth keys?
- Is a connection pool with explicit timeouts used?
- Is `maxmemory` and an eviction policy set appropriately for cache vs datastore?

## Related

- `knowledge/redis/12-expiration.md`
- `knowledge/redis/13-caching.md`
- `knowledge/redis/23-performance.md`
- `knowledge/redis/27-production.md`
- `knowledge/redis/100-common-antipatterns.md`
