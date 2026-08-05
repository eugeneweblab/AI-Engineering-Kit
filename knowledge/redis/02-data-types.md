---
id: redis/02-data-types
topic: redis
slug: data-types
title: "Redis Data Types"
type: doc
order: 2
status: ready
tags: [redis, data-types, ZADD, SISMEMBER, HSET, SADD, INCR, EXPIRE]
related: [redis/03-strings, redis/04-lists, redis/05-sets, redis/06-sorted-sets, redis/07-hashes]
when_to_use: "Read before choosing how to store a value in Redis, so the data type matches the access pattern."
---
# Redis Data Types

## Purpose

This document maps Redis's built-in data types to the access patterns they serve, so an
agent picks the right structure the first time. Choosing the type is the single most
important Redis decision: it determines whether a lookup is `O(1)` or an `O(N)` scan,
whether an operation is atomic, and whether memory stays bounded. Each type has its own
deep-dive doc; this page is the decision layer above them.

## Why It Matters

Redis is not "just strings." Its value is that the server understands the *shape* of your
data and executes operations on it atomically and efficiently. Store a JSON blob as a
string and every update becomes read-modify-write with a race condition; store the same
data as a hash and you get atomic field updates. The wrong type forces you to move work
to the client, adds round trips, and reintroduces the concurrency bugs Redis was meant to
eliminate. The type is the design.

## Core Principles

- **Pick the type from the query, not the data.** Ask "how will I read and mutate this?"
  A leaderboard needs ranking → sorted set. A dedup check needs membership → set.
- **Prefer types with atomic operations over client-side read-modify-write.** `INCR`,
  `HSET`, `SADD`, `ZADD` mutate in place with no race; loading a blob and rewriting it
  races.
- **Know the complexity of the operations you'll run.** A type is only right if its
  common operations are cheap at your scale. See each type's doc.
- **Keep values and collections bounded.** A single key holding millions of elements is a
  hot key that blocks the single thread; shard or cap it.

## The Types

| Type | Shape | Reach for it when | Deep dive |
|------|-------|-------------------|-----------|
| **String** | bytes / number | counters, flags, cached blobs, atomic `SET` | [Strings](03-strings.md) |
| **List** | ordered sequence | queues, stacks, recent-N feeds | [Lists](04-lists.md) |
| **Set** | unordered unique members | membership, dedup, tags, set algebra | [Sets](05-sets.md) |
| **Sorted Set** | members ranked by score | leaderboards, time indexes, priority queues | [Sorted Sets](06-sorted-sets.md) |
| **Hash** | field → value map | objects/records under one key | [Hashes](07-hashes.md) |
| **Stream** | append-only log w/ IDs | event logs, durable queues, consumer groups | [Streams](08-streams.md) |

Specialized types build on these: **bitmaps** and **HyperLogLog** are string encodings
for compact counting; **geospatial** indexes are sorted sets. Reach for them only when
the plain type's memory or precision cost is a proven problem.

## Best Practices

- Start from the deep-dive doc for the type you think fits, and confirm its operations are
  `O(1)` / `O(log N)` for your hot path before committing.
- Use a hash instead of a JSON string whenever you update individual fields — you get
  atomic per-field writes and lower serialization cost.
- Use a set, never a list, when membership or uniqueness matters; `SISMEMBER` is `O(1)`,
  scanning a list is `O(N)`.
- Use a sorted set whenever "top N", "rank of", or "items in a time/score range" is a
  requirement — nothing else gives you `O(log N)` ranked access.
- Attach an expiry (`EXPIRE`) at creation for anything transient; the type does not manage
  its own lifecycle. See [Expiration](12-expiration.md).

## Examples

**Good Example** — type matches the access pattern

```redis
# Requirement: "is this device already registered?" → membership test.
SADD registered:devices "device-abc"    # O(1) insert, dedups automatically
SISMEMBER registered:devices "device-abc"  # O(1) lookup → correct type

# Requirement: "top 10 players by score" → ranked access.
ZADD leaderboard 4200 "player:7"        # O(log N)
ZREVRANGE leaderboard 0 9 WITHSCORES    # O(log N + 10) → cheap top-N
```

**Bad Example** — wrong type forces O(N) work and races

```redis
# Membership stored as a list: every check scans the whole list.
RPUSH registered:devices "device-abc"
LRANGE registered:devices 0 -1          # O(N) pull to client, then scan there

# "Update one field" stored as a JSON string: read-modify-write race.
SET user:42 '{"name":"Ada","visits":10}'
# Two clients GET, both increment visits to 11, one write is lost.
```

## Common Mistakes

- Defaulting to strings for everything and rebuilding structure in the client.
- Using a list for uniqueness/membership, turning `O(1)` checks into `O(N)` scans.
- Storing an updatable record as a JSON string, creating read-modify-write races.
- Picking sorted sets for data that never needs ranking, paying `O(log N)` for nothing.
- Letting a single collection grow unbounded until it becomes a blocking hot key.

## AI Review Checklist

- Is each key's type justified by how the data is queried and mutated?
- Are mutations done with atomic type operations rather than client read-modify-write?
- Are the hot-path operations `O(1)` or `O(log N)` at production scale?
- Is a hash used (not a JSON string) wherever individual fields are updated?
- Is every transient key given an expiry, and every collection bounded?

## Related

- `knowledge/redis/03-strings.md`
- `knowledge/redis/04-lists.md`
- `knowledge/redis/05-sets.md`
- `knowledge/redis/06-sorted-sets.md`
- `knowledge/redis/07-hashes.md`
