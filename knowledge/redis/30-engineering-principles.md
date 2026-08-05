---
id: redis/30-engineering-principles
topic: redis
slug: engineering-principles
title: "Redis Engineering Principles"
type: doc
order: 30
status: ready
tags: [redis, engineering-principles, WATCH, MULTI, SCAN, maxmemory, HGETALL, SMEMBERS]
related: [redis/13-caching, redis/12-expiration, redis/17-distributed-locks, redis/23-performance, redis/10-transactions]
when_to_use: "Read before designing any feature that stores or coordinates state in Redis."
---
# Redis Engineering Principles

## Purpose

This document defines the mental model an agent must hold before writing Redis code.
Redis is a single-threaded, in-memory data structure server — not a general database.
Every design decision follows from those two facts. The principles here tell you what
Redis is good at, where it silently loses data, and how to keep a shared instance fast
and safe for every other client on it.

## Why It Matters

Redis is fast enough to hide mistakes until they scale. A single `KEYS *`, an unbounded
list, or a missing TTL runs fine in development and then stalls production, because the
server executes one command at a time and memory is finite. Redis also trades durability
for speed by default: an acknowledged write can vanish on a crash. Code that treats Redis
like a durable relational store will lose data and blame the wrong thing. Getting the
model right up front is far cheaper than diagnosing a frozen event loop under load.

## Core Principles

- **Redis is single-threaded — no command is free.** One slow command blocks every other
  client. Command cost is what matters, not round-trip count. Prefer O(1)/O(log N)
  commands; treat any O(N) over a large collection (`KEYS`, `SMEMBERS`, `HGETALL`,
  `LRANGE 0 -1`) as a production hazard.
- **Memory is the hard limit.** Every key costs RAM until it is deleted or expires. A key
  without an eviction path is a leak. Design the deletion story before the write.
- **Durability is opt-in, not default.** With default persistence a crash can lose the
  last seconds of writes. Never make Redis the source of truth for data you cannot
  recompute or reload.
- **Model with the right data type.** Redis is a data-structure server; picking the type
  (string, hash, set, sorted set, stream) is the core design act, not an afterthought.
- **Atomicity comes from the server, not the client.** Read-modify-write across clients
  races. Use a single command, `MULTI`/`WATCH`, or a Lua script to make it atomic.
- **Namespace and bound everything.** Keys need a consistent prefix scheme; collections
  need a size or time bound. Unbounded growth is the default failure mode.

## Best Practices

- Give every key a TTL unless you have a deliberate reason not to, and document that
  reason. Caches, sessions, locks, and rate-limit counters must all expire.
- Use a colon-delimited key convention (`app:users:42:session`) so keys are greppable and
  scannable by pattern. Keep values small; large values slow serialization and replication.
- Replace `KEYS` with `SCAN` in any code path that runs against production. `SCAN` is
  incremental and non-blocking; `KEYS` blocks the whole server.
- Pipeline independent commands to cut round trips, but keep each command cheap — a
  pipeline of O(N) commands still blocks the server for the sum of their work.
- Run multi-step atomic logic (check-then-set, counters with limits, dequeue-and-ack) as a
  Lua script or `MULTI`/`WATCH`, never as separate client round trips.
- Set `maxmemory` and an explicit eviction policy (e.g. `allkeys-lru` for a pure cache,
  `noeviction` when losing keys would corrupt state). Never run with memory unbounded.
- Keep a database behind Redis as the source of truth for anything durable; treat Redis as
  a rebuildable acceleration and coordination layer.

## Examples

**Good Example** — bounded, atomic, expiring

```lua
-- Atomic "increment a counter, cap it, and expire the window" as one server-side script.
-- Runs as a single unit: no other client can interleave between INCR and EXPIRE.
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])  -- set TTL only on first hit → self-cleaning
end
if current > tonumber(ARGV[2]) then
  return 0                                 -- over limit; caller rejects
end
return 1
```

**Bad Example** — O(N) scan, racy, unbounded

```python
# BAD: KEYS blocks the entire single-threaded server while it walks every key.
keys = r.keys("session:*")                 # O(N) over the whole keyspace → stalls prod

# BAD: read-then-write across two round trips → two clients can both pass the check.
count = int(r.get("rate:user:42") or 0)
if count < 100:
    r.set("rate:user:42", count + 1)       # lost updates under concurrency
    # no EXPIRE anywhere → counter lives forever, memory leak
```

## Common Mistakes

- Using `KEYS`, `SMEMBERS`, or `HGETALL` on collections that grow with traffic.
- Writing a key with no TTL and no other deletion path, so memory climbs until eviction
  or OOM.
- Doing check-then-set (locks, counters, dedup) in the client, creating a race window.
- Treating Redis as durable storage and losing data on the next failover or restart.
- Storing huge values or huge collections in one key, blocking replication and slow logs.
- Running with default unbounded `maxmemory`, so an OOM crash is only a matter of time.

## Production Tips

- Watch `INFO` for `used_memory`, `evicted_keys`, `blocked_clients`, and the `SLOWLOG`.
  Rising evictions or slowlog entries mean a command or dataset is too big.
- Cap Lua script and pipeline sizes; a script is atomic and therefore blocking for its
  full duration.
- Load-test with production-sized keyspaces — O(N) commands only reveal themselves at scale.

## AI Review Checklist

- Does every key have a TTL or an explicit, documented deletion path?
- Are all keyspace scans done with `SCAN`, never `KEYS`, in production code paths?
- Is every read-modify-write made atomic with a single command, `MULTI`/`WATCH`, or Lua?
- Is the chosen data type the natural fit for the access pattern?
- Is `maxmemory` and an eviction policy set, and is Redis never the sole source of truth
  for durable data?
- Are collections and values size-bounded so no command becomes O(large N)?

## Related

- `knowledge/redis/13-caching.md`
- `knowledge/redis/12-expiration.md`
- `knowledge/redis/17-distributed-locks.md`
- `knowledge/redis/23-performance.md`
- `knowledge/redis/10-transactions.md`
