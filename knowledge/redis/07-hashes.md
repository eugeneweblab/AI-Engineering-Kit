---
id: redis/07-hashes
topic: redis
slug: hashes
title: "Hashes"
type: doc
order: 7
status: ready
tags: [redis, hashes]
related: [redis/03-strings, redis/06-sorted-sets, redis/12-expiration, redis/15-session-storage, redis/23-performance]
when_to_use: "Read before modeling an object or record in Redis, or when choosing between a hash and many separate string keys."
---
# Hashes

## Purpose

This document defines how to use the Redis **hash**: a single key holding a map of
field-value pairs. It is written so an agent can model a structured record (a user, a
session, a product) as one hash instead of scattering it across many keys, and can update
individual fields atomically.

A hash is Redis's answer to "store an object." Reach for it when you have one entity with
several named attributes that you read and update field-by-field. If you only ever read
and write the whole blob at once, a serialized [string](03-strings.md) is simpler; the
moment you need per-field updates, the hash wins.

## Why It Matters

The common mistake is representing an object as many top-level keys — `user:42:name`,
`user:42:email`, `user:42:age` — or as a JSON string that must be fetched, parsed,
mutated, and rewritten on every change. The first explodes key count and makes atomic
multi-field updates impossible; the second turns a one-field change into a full
read-modify-write with a lost-update race. A hash fixes both: one key per entity, atomic
`HSET`/`HINCRBY` on any field, and — under the small-object encoding threshold — dramatically
less memory than the equivalent separate keys. Get this right and objects are cheap and
race-free; get it wrong and you pay in memory, round trips, and corruption.

## Core Principles

- **One hash per entity.** The key names the entity (`user:42`); fields name its attributes.
  This keeps related data co-located and lets you `DEL` or [`EXPIRE`](12-expiration.md) the
  whole object atomically.
- **Fields update independently and atomically.** `HSET`, `HDEL`, and `HINCRBY` touch one
  field without reading the rest — no whole-object read-modify-write, no lost updates.
- **Fetch narrowly.** `HGET`/`HMGET` for known fields; `HGETALL` only when you truly need
  every field. `HGETALL` is `O(N)` in field count and copies everything.
- **Hashes have no per-field TTL by default.** Expiry is on the whole key. (Redis 7.4+ adds
  `HEXPIRE` for per-field TTL, but it is a niche feature — do not assume it is available.)
- **Values are strings.** Numbers are stored as strings and manipulated with `HINCRBY` /
  `HINCRBYFLOAT`. There is no nested structure — flatten or serialize sub-objects.

## Best Practices

- Model records as hashes: `HSET user:42 name "Ada" email "ada@x.io" logins 0`. Read hot
  fields with `HMGET user:42 name email` rather than pulling the whole object.
- Increment counters in place with `HINCRBY user:42 logins 1` — atomic, no race, one trip.
- Use `HSETNX` for create-if-absent semantics on a single field (e.g., seeding a default).
- Set expiry on the key, not the fields: `EXPIRE user:42 3600`. For [sessions](15-session-storage.md),
  refresh the TTL on each access to implement idle timeout.
- Keep hashes reasonably small. Redis stores hashes under `hash-max-listpack-entries`
  (default 128) and `hash-max-listpack-value` (default 64 bytes) as a compact listpack;
  beyond that it converts to a full hashtable and uses more memory per field.
- For huge field spaces, iterate with `HSCAN` (cursor-based), never `HGETALL` — the latter
  can block the server and flood the client.
- Store bulky or rarely-read payloads outside the hash; keep the hash to the fields you
  actually query.

## Examples

**Good Example** — one hash per object, atomic field update, narrow read

```bash
# Create the object in one round trip.
HSET user:42 name "Ada" email "ada@x.io" logins 0

# Atomic per-field increment — no read, no race, safe under concurrency.
HINCRBY user:42 logins 1

# Fetch only what this request needs, not the whole object.
HMGET user:42 name email

# Expire the whole entity atomically (e.g., a cached record).
EXPIRE user:42 3600
```

**Bad Example** — key explosion and a lost-update race

```bash
# One entity smeared across many keys: can't atomically expire or delete together,
# and multiplies key overhead and memory.
SET user:42:name  "Ada"
SET user:42:email "ada@x.io"
SET user:42:logins 0

# Counter update as read-modify-write: two concurrent requests both read 5,
# both write 6 — one increment is silently lost.
GET user:42:logins        # -> "5"
SET user:42:logins 6      # racy
```

## Common Mistakes

- Splitting one entity across many string keys, losing atomic delete/expire and wasting memory.
- Serializing an object to a JSON string, then read-modify-writing it for every field change
  (slow and race-prone) when per-field `HSET`/`HINCRBY` would be atomic.
- Calling `HGETALL` on a hash that can grow large, blocking Redis and copying every field.
- Doing `HGET` + application increment + `HSET` instead of atomic `HINCRBY`.
- Assuming a field can expire on its own — TTL is per key unless you use `HEXPIRE` (7.4+).
- Storing deeply nested data in one field and re-parsing it constantly; flatten instead.

## Production Tips

- Monitor the listpack thresholds: a hash that quietly crosses `hash-max-listpack-entries`
  jumps in memory. If you expect large hashes, budget for the hashtable encoding.
- Use `HRANDFIELD` for sampling fields without pulling the whole hash.
- When migrating from JSON-string objects, convert to hashes to unlock atomic field updates
  and cheaper partial reads — but keep a serializer for fields that are themselves structured.

## AI Review Checklist

- Is each entity a single hash keyed by its id, rather than many separate string keys?
- Are counters updated with `HINCRBY`, not `HGET`+`HSET`?
- Do reads use `HGET`/`HMGET` for known fields instead of `HGETALL` where possible?
- Is large or unbounded iteration done with `HSCAN`, not `HGETALL`?
- Is expiry set on the key (and refreshed for sessions) rather than assumed per-field?
- Are hashes kept under the listpack thresholds, or is the memory cost of conversion accepted knowingly?

## Related

- `knowledge/redis/03-strings.md`
- `knowledge/redis/06-sorted-sets.md`
- `knowledge/redis/12-expiration.md`
- `knowledge/redis/15-session-storage.md`
- `knowledge/redis/23-performance.md`
