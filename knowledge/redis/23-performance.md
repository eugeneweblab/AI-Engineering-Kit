---
id: redis/23-performance
topic: redis
slug: performance
title: "Redis Performance"
type: doc
order: 23
status: ready
tags: [redis, performance]
related: [redis/22-monitoring, redis/02-data-types, redis/13-caching, redis/12-expiration]
when_to_use: "Read before optimizing Redis throughput or latency, or when a command is blocking the server."
---
# Redis Performance

## Purpose

This document defines how to keep Redis fast: avoiding O(N) commands on the single
command thread, batching round trips with pipelining, choosing memory-efficient
data structures, and controlling key growth with expiry. The aim is that an agent
writes access patterns that stay fast as data grows, rather than ones that work in
a demo and collapse in production.

Performance in Redis is mostly about two things: not blocking the single thread,
and not paying a network round trip per operation. Most incidents trace back to
violating one of these.

## Why It Matters

Redis executes commands on **one thread**, so its throughput ceiling is "how fast
can each command return?". A single O(N) command over a large collection —
`KEYS *`, `LRANGE mylist 0 -1`, `SMEMBERS` on a million-member set — stalls every
other client for its full duration. Separately, doing 10,000 individual `GET`s is
10,000 network round trips; the same work pipelined is one. These are not micro-
optimizations — they are the difference between sub-millisecond latency and a
server that appears hung under load.

## Core Principles

- **Never run unbounded O(N) commands in production.** They block the single thread.
  Prefer O(1)/O(log N) commands and always bound ranges.
- **Round trips dominate latency.** Batch with pipelining or `MGET`/`MSET`; one
  round trip for N operations beats N round trips.
- **`SCAN`, never `KEYS`.** `SCAN` (and `HSCAN`/`SSCAN`/`ZSCAN`) iterate
  incrementally with a cursor and do not block; `KEYS` walks the whole keyspace.
- **Data structure choice is a performance decision.** The right type and encoding
  (small hashes/zsets use compact listpack encoding) cuts both memory and CPU.
- **Every key should have a reason to be small and, usually, a TTL.** Unbounded
  collections and never-expiring keys turn into O(N) hazards and memory leaks.

## Best Practices

- Replace `KEYS pattern` with `SCAN` using a cursor and `COUNT` hint; process in
  batches so you never block the server.
- **Pipeline** independent commands to collapse round trips; use `MGET`/`MSET` for
  bulk key access. For read-modify-write atomicity across keys, use a Lua script
  (single round trip, atomic) rather than a chatty transaction.
- Bound every range: `LRANGE key 0 99`, `ZRANGE ... LIMIT`, `HSCAN` — never `0 -1`
  on collections that can grow large.
- Keep collections small or shard them (e.g. bucket by hash). Redis's compact
  encodings (listpack) apply only below `hash-max-listpack-entries`,
  `zset-max-listpack-entries`, etc.; large collections switch to memory-heavier
  encodings.
- Set a `maxmemory` and an eviction policy (`allkeys-lru`/`allkeys-lfu` for caches);
  give cache keys TTLs so memory self-cleans. See [expiration](12-expiration.md).
- Use connection pooling; avoid opening a connection per request. Reuse clients.
- Move multi-step logic server-side with Lua to cut round trips, but keep scripts
  short — a slow script blocks the thread just like a slow command.

## Examples

**Good Example** — non-blocking iteration + one round trip

```python
# SCAN iterates in bounded chunks with a cursor: no single blocking call, and the
# server stays responsive to other clients between iterations.
cursor = 0
keys = []
while True:
    cursor, batch = r.scan(cursor, match="session:*", count=500)
    keys.extend(batch)
    if cursor == 0:
        break

# One pipelined round trip for all the reads instead of len(keys) round trips.
# WHY: network latency is paid once, not per key — often a 100x wall-clock win.
pipe = r.pipeline(transaction=False)
for k in keys:
    pipe.ttl(k)
ttls = pipe.execute()
```

**Bad Example** — blocking scan + a round trip per key

```python
# KEYS walks the ENTIRE keyspace in one O(N) call, blocking every other client
# for its full duration. On a large instance this is a self-inflicted outage.
keys = r.keys("session:*")

# Then a separate network round trip for each key: N round trips, N * RTT latency.
for k in keys:                 # 50k keys -> 50k round trips
    ttl = r.ttl(k)             # each call waits a full network hop
```

## Common Mistakes

- `KEYS *` in application code — the single most common Redis performance outage.
- Unbounded `LRANGE 0 -1`, `SMEMBERS`, `HGETALL`, `ZRANGE 0 -1` on large
  collections, blocking the thread.
- A round trip per item instead of pipelining or `MGET`/`MSET`.
- Storing huge values or ever-growing collections in a single key (big-key problem),
  making every touch O(N) and evictions/migrations expensive.
- No `maxmemory`/eviction policy and no TTLs, so memory grows until OOM.
- Opening a new connection per request, paying handshake cost every time.
- Long Lua scripts or `MULTI` blocks that hold the thread as long as a slow command.

## Production Tips

- Hunt big keys with `redis-cli --bigkeys` / `--memkeys` and `MEMORY USAGE key`;
  refactor any key whose size makes routine operations O(N).
- Keep the slowlog on (see [monitoring](22-monitoring.md)) so newly-introduced
  O(N) patterns show up immediately.
- Benchmark realistically with `redis-benchmark` and your actual value sizes and
  pipeline depth; tiny-value benchmarks overstate throughput.
- Prefer `UNLINK` over `DEL` for large keys — it frees memory in a background
  thread instead of blocking the command thread.

## AI Review Checklist

- Is `SCAN` used instead of `KEYS` for pattern iteration?
- Are all range reads bounded (no `0 -1` on growable collections)?
- Are bulk operations pipelined or done with `MGET`/`MSET` rather than per-item
  round trips?
- Are collections and values kept small (no big-key hazards)?
- Is `maxmemory` + an eviction policy set, and do cache keys have TTLs?
- Are connections pooled and reused, not opened per request?
- Is `UNLINK` used for deleting large keys?

## Related

- `knowledge/redis/22-monitoring.md`
- `knowledge/redis/02-data-types.md`
- `knowledge/redis/13-caching.md`
- `knowledge/redis/12-expiration.md`
