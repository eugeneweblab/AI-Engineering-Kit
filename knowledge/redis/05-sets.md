---
id: redis/05-sets
topic: redis
slug: sets
title: "Sets"
type: doc
order: 5
status: ready
tags: [redis, sets, SMEMBERS, SISMEMBER, SSCAN, SADD, SUNIONSTORE, membership, collections, tagging]
related: [redis/02-data-types, redis/04-lists, redis/06-sorted-sets, redis/07-hashes]
when_to_use: "Read before using Redis sets for membership tests, deduplication, tagging, or set algebra between collections."
---
# Sets

## Purpose

This document covers the Redis set: an unordered collection of unique strings with
`O(1)` add, remove, and membership tests, plus native union/intersection/difference. Sets
back membership checks ("has this user been seen?"), deduplication, tag systems, and
relationship queries ("mutual followers"). This doc shows how to use them for `O(1)`
lookups and cheap set algebra, and how to avoid the `O(N)` command that blocks the server.

## Why It Matters

The whole reason to use a set is `SISMEMBER` — an `O(1)` "is X in here?" that replaces an
`O(N)` scan through a list. Agents undermine this by using the wrong commands:
`SMEMBERS` pulls the *entire* set to the client (`O(N)`, blocking), and computing
intersections in application code re-implements, slowly and racily, what `SINTER` does
atomically on the server. Sets are fast only if you use their membership and algebra
commands, not if you fetch everything and process it yourself.

## Core Principles

- **Use sets for uniqueness and membership.** `SADD` dedups automatically; `SISMEMBER` is
  `O(1)`. If duplicates or order matter, use a [list](04-lists.md); if ranking matters,
  use a [sorted set](06-sorted-sets.md).
- **Test membership; do not fetch the whole set.** `SISMEMBER`/`SMISMEMBER` answer the
  question directly. `SMEMBERS` on a large set is `O(N)` and blocks the single thread.
- **Do set algebra on the server.** `SINTER`, `SUNION`, `SDIFF` (and their `...STORE`
  variants) run atomically in Redis; recomputing them client-side is slower and racy.
- **Iterate large sets with `SSCAN`, never `SMEMBERS`.** `SSCAN` is cursor-based and
  non-blocking; it trades a consistent snapshot for not freezing the server.
- **Bound cardinality.** A set with tens of millions of members makes `SMEMBERS`/`SINTER`
  expensive; attach a TTL or partition it.

## Best Practices

- Represent "seen / registered / active" flags as `SADD` + `SISMEMBER` rather than a list
  scan; it is `O(1)` in both directions.
- Check many members at once with `SMISMEMBER key m1 m2 ...` instead of N round trips of
  `SISMEMBER`.
- Use `SINTERSTORE`/`SUNIONSTORE` to cache an expensive set-algebra result under a new key
  with a TTL, so repeated queries reuse it.
- When counting approximate uniques at massive scale (unique visitors), prefer
  **HyperLogLog** (`PFADD`/`PFCOUNT`) — a set stores every member; HLL uses ~12 KB total.
- Enumerate members with `SSCAN` in production; reserve `SMEMBERS` for known-small sets.

## Examples

**Good Example** — O(1) membership and server-side algebra

```redis
# Track which users viewed an article; uniqueness is automatic.
SADD article:99:viewers "user:7"     # O(1), no duplicate even if repeated
SISMEMBER article:99:viewers "user:7"  # O(1) → correct, cheap membership test

# "Users who follow both A and B" computed atomically on the server.
SINTERSTORE mutuals:A:B followers:A followers:B  # O(N) but in-Redis, one round trip
EXPIRE mutuals:A:B 300               # cache the result briefly; bound its lifetime

# Iterate a large set without blocking other clients.
SSCAN article:99:viewers 0 COUNT 100
```

**Bad Example** — fetch-everything and compute in the client

```redis
# Pulls the entire set to the client just to test one member: O(N) + blocking.
SMEMBERS article:99:viewers          # transfers every viewer over the network
# ... application code then checks if "user:7" is in the returned array ...

# Intersection done in the app: two full O(N) fetches, then a client-side loop,
# with a race window where followers change between the two reads.
SMEMBERS followers:A
SMEMBERS followers:B
# ... nested loop in application code to find common members ...
```

## Common Mistakes

- Using `SMEMBERS` to test membership instead of `SISMEMBER`/`SMISMEMBER`.
- Running `SMEMBERS` on a large set in production, blocking the server; use `SSCAN`.
- Computing intersections/unions in application code instead of `SINTER`/`SUNION`.
- Using a set when order or duplicates matter (a set silently drops both) — use a list.
- Storing millions of members for a unique-count metric instead of HyperLogLog.
- Forgetting a TTL on derived/`...STORE` keys, leaking memory as they accumulate.

## Production Tips

- Alert on set cardinality (`SCARD`) for keys that can grow unboundedly, e.g. per-article
  viewer sets — cap or expire them.
- Materialize hot set-algebra results with `...STORE` + TTL to avoid recomputing on every
  request; treat it as a cache with an invalidation story.
- Reach for HyperLogLog or Bloom filters (RedisBloom) when exact membership isn't required
  and memory is the constraint.

## AI Review Checklist

- Is membership tested with `SISMEMBER`/`SMISMEMBER`, never `SMEMBERS`?
- Are large sets iterated with `SSCAN` instead of `SMEMBERS` in production?
- Is set algebra performed server-side (`SINTER`/`SUNION`/`SDIFF`), not in the client?
- Is a set the right choice (uniqueness/membership) vs a list (order) or sorted set (rank)?
- Do derived `...STORE` keys carry a TTL, and is set cardinality bounded?
- Is HyperLogLog used where only an approximate unique count is needed at scale?

## Related

- `knowledge/redis/02-data-types.md`
- `knowledge/redis/04-lists.md`
- `knowledge/redis/06-sorted-sets.md`
- `knowledge/redis/07-hashes.md`
