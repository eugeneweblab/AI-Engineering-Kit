---
id: redis/99-ai-review-checklist
topic: redis
slug: ai-review-checklist
title: "Redis AI Review Checklist"
type: doc
order: 99
status: ready
tags: [redis, ai-review-checklist]
related: [redis/30-engineering-principles, redis/98-production-checklist, redis/100-common-antipatterns, redis/10-transactions, redis/12-expiration]
when_to_use: "Read when reviewing any diff that reads from, writes to, or coordinates through Redis."
---
# Redis AI Review Checklist

## Purpose

A focused checklist for reviewing Redis code changes. Each item is a yes/no question an
agent can answer by reading the diff. It targets the failures that pass tests locally and
break at scale: blocking commands, missing TTLs, client-side races, and unsafe data models.
Use it alongside the [production checklist](98-production-checklist.md), which covers
infrastructure rather than code.

## Why It Matters

Redis bugs are usually invisible in review unless you know the shape of them. Correct-looking
code — a `GET` then a `SET`, a `KEYS` in a cleanup job, a write with no expiry — is exactly
what stalls the single-threaded server or leaks memory in production. Reviewing against a
concrete list catches these before they ship, when they cost minutes instead of an incident.

## Command Cost and Blocking

**Rules:** [Performance](23-performance.md) · [Data Types](02-data-types.md)

- [ ] No `KEYS` in production paths — pattern iteration uses `SCAN`/`HSCAN`/`SSCAN`.
- [ ] No O(N) command (`SMEMBERS`, `HGETALL`, `LRANGE 0 -1`, `ZRANGE 0 -1`) over a
      collection that grows with traffic.
- [ ] Lua scripts and pipelines are bounded; no single unit does unbounded work.
- [ ] No blocking command (`BLPOP`, `WAIT`) used in a way that stalls a shared connection.
- [ ] Large deletes rely on lazy-free or `UNLINK` rather than blocking `DEL` on huge keys.

## Atomicity and Concurrency

**Rules:** [Transactions](10-transactions.md) · [Lua Scripting](11-lua-scripting.md)

- [ ] Every read-modify-write (counter with cap, check-then-set, dequeue-and-ack) is atomic
      via a single command, `INCR`/`SETNX`-style primitives, `MULTI`/`WATCH`, or Lua.
- [ ] Locks use a unique token and release only if the token matches (compare-and-delete in
      Lua), never a bare `DEL`.
- [ ] Distributed locks carry a TTL so a crashed holder cannot deadlock the system.
- [ ] Code does not assume commands from different clients interleave in any order.

## Keys, TTLs, and Memory

**Rules:** [Expiration](12-expiration.md) · [Caching](13-caching.md)

- [ ] Every new key has a TTL or a clearly justified reason it must persist.
- [ ] Rate-limit and lock counters set their TTL atomically with creation (not a second
      round trip that can be skipped on crash).
- [ ] Keys follow the project's namespace convention (e.g. `app:domain:id`).
- [ ] Value and collection sizes are bounded; no unbounded list/set/stream growth.

## Data Model and Correctness

**Rules:** [Data Types](02-data-types.md) · [Sorted Sets](06-sorted-sets.md)

- [ ] The data type fits the access pattern (sorted set for ranking, hash for objects,
      stream for an event log, set for membership).
- [ ] Redis is not treated as the durable source of truth for non-recomputable data.
- [ ] Cache reads tolerate a miss (value absent/evicted) and fall back to the source.
- [ ] Serialization format is consistent between writer and reader; no ambiguous encodings.

## Resilience

**Rules:** [Replication](18-replication.md) · [Persistence](20-persistence.md)

- [ ] Redis calls are wrapped so a Redis outage degrades gracefully, not a hard 500.
- [ ] Connections come from a pool and are reused; timeouts are set on operations.
- [ ] Cluster-mode multi-key operations use hash tags to keep keys on one slot.
- [ ] Errors like `MOVED`, `ASK`, and connection resets are handled by the client layer.

## AI Review Checklist

- Is every keyspace scan using `SCAN`, and is no O(N) command run over a growing collection?
- Is every read-modify-write atomic, and does every lock use a token plus TTL?
- Does every new key have a TTL or a documented reason to persist?
- Does the code fall back correctly when a cached value is missing or evicted?
- Does a Redis outage degrade gracefully rather than crash the request path?

## Related

- `knowledge/redis/30-engineering-principles.md`
- `knowledge/redis/98-production-checklist.md`
- `knowledge/redis/100-common-antipatterns.md`
- `knowledge/redis/10-transactions.md`
- `knowledge/redis/12-expiration.md`
