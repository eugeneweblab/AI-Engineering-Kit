---
id: redis/100-common-antipatterns
topic: redis
slug: common-antipatterns
title: "Common Antipatterns"
type: doc
order: 100
status: ready
tags: [redis, common-antipatterns]
related: [redis/30-engineering-principles, redis/17-distributed-locks, redis/13-caching, redis/14-rate-limiting, redis/23-performance]
when_to_use: "Read before writing Redis code, and when reviewing a diff that touches Redis, to catch known failure shapes."
---
# Common Antipatterns

## Purpose

A catalog of the Redis mistakes that most often reach production. Each entry names the
antipattern, explains why it is wrong (the concrete failure it causes), and gives the fix.
These are the recurring root causes behind Redis incidents: blocking the single thread,
leaking memory, and racing across clients.

## Why It Matters

Every antipattern here runs perfectly in development. They only fail under real traffic,
real data volumes, or real concurrency — which is why they slip through review. Learning
the shape of each one lets an agent reject it on sight instead of debugging it live.

## Antipatterns

### 1. `KEYS` in production

**Why it is wrong:** `KEYS pattern` is O(N) over the entire keyspace and runs on the single
thread, freezing every other client until it finishes. On a large keyspace this is a
multi-second stall — an effective outage.

**The fix:** Use `SCAN` (and `HSCAN`/`SSCAN`/`ZSCAN`), which returns a cursor and iterates
incrementally without blocking. Better, maintain an index set of the keys you need instead
of scanning at all.

### 2. Keys with no TTL and no deletion path

**Why it is wrong:** Every key consumes RAM until deleted. Session, cache, and counter keys
written without an expiry accumulate forever, ending in eviction storms or an OOM crash.

**The fix:** Set a TTL at write time (`SET k v EX 3600`, or `EXPIRE` inside the same atomic
unit). For anything cache-like, also set `maxmemory` and an LRU/LFU eviction policy as a
backstop.

### 3. Read-modify-write across client round trips

**Why it is wrong:** `GET` then compute then `SET` is not atomic. Two clients read the same
value and both write, losing an update. This corrupts counters, rate limits, and balances.

**The fix:** Use an atomic primitive (`INCR`, `INCRBYFLOAT`, `SETNX`), or wrap the logic in
a Lua script or `MULTI`/`WATCH` so it executes as one indivisible unit.

```lua
-- Fix for a capped counter: check and increment atomically, server-side.
local n = redis.call('INCR', KEYS[1])
if n == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
return n <= tonumber(ARGV[2]) and 1 or 0
```

### 4. Releasing a distributed lock with a bare `DEL`

**Why it is wrong:** If your lock's TTL expires and another client acquires it, your later
`DEL` deletes *their* lock — silently breaking mutual exclusion.

**The fix:** Store a unique token as the lock value and delete only if it still matches,
atomically in Lua:

```lua
-- Compare-and-delete: only the owner can release.
if redis.call('GET', KEYS[1]) == ARGV[1] then
  return redis.call('DEL', KEYS[1])
end
return 0
```

Always acquire with a TTL (`SET lock token NX EX 30`) so a crashed holder cannot deadlock.

### 5. Treating Redis as the durable source of truth

**Why it is wrong:** Default persistence can lose the last seconds of writes on a crash, and
a failover can drop unreplicated writes. Data that lives only in Redis can silently vanish.

**The fix:** Keep durable data in a database and use Redis as a rebuildable cache or
coordination layer. If Redis must be durable, enable AOF with `appendfsync everysec` and
accept the documented loss window — but prefer not to depend on it.

### 6. One giant key (the "hot big key")

**Why it is wrong:** A multi-megabyte value or a collection with millions of elements makes
every operation on it O(large N), blocks replication while it transfers, and blocks the
thread when deleted. It also creates a single hotspot that Cluster cannot shard.

**The fix:** Split the data across many keys (shard by id, bucket by time), bound collection
size, and delete large keys with `UNLINK` (lazy free) instead of `DEL`.

### 7. Cache stampede on expiry

**Why it is wrong:** When a hot key expires, every concurrent request misses at once and all
of them hit the backing store, overloading it — a "thundering herd" at each expiry.

**The fix:** Recompute with a short-lived lock (only one client rebuilds), or use probabilistic
early recomputation, or serve a stale value while a single background refresh runs.

### 8. Connecting per request instead of pooling

**Why it is wrong:** Opening a TCP (and TLS) connection per request adds latency and exhausts
file descriptors under load, and the handshake cost dwarfs the actual command time.

**The fix:** Use a connection pool, reuse connections, and set operation timeouts so a slow
Redis does not pile up requests indefinitely.

### 9. Ignoring `maxmemory` and eviction policy

**Why it is wrong:** With unbounded memory, Redis grows until the OS kills it. With the wrong
policy, it may evict keys you needed (e.g. `allkeys-lru` on data you treated as durable).

**The fix:** Always set `maxmemory` with headroom, and pick the policy for the workload:
`allkeys-lru`/`allkeys-lfu` for pure caches, `noeviction` where losing a key breaks correctness.

### 10. Non-atomic multi-key writes in Cluster mode

**Why it is wrong:** In Cluster, keys on different slots cannot participate in one transaction
or script; a `MULTI` or Lua touching them fails with a cross-slot error.

**The fix:** Co-locate related keys with a hash tag so they share a slot
(`user:{42}:profile`, `user:{42}:sessions`), so multi-key atomic operations stay valid.

## AI Review Checklist

- Is `SCAN` used instead of `KEYS`, and are large keys deleted with `UNLINK`?
- Does every key have a TTL, and is `maxmemory` plus an eviction policy configured?
- Are read-modify-write and lock-release operations atomic (single command or Lua)?
- Do distributed locks use a unique token plus a TTL?
- Are big values/collections split, and do Cluster multi-key ops use hash tags?
- Are connections pooled with timeouts, and is cache stampede mitigated on hot keys?

## Related

- `knowledge/redis/30-engineering-principles.md`
- `knowledge/redis/17-distributed-locks.md`
- `knowledge/redis/13-caching.md`
- `knowledge/redis/14-rate-limiting.md`
- `knowledge/redis/23-performance.md`
