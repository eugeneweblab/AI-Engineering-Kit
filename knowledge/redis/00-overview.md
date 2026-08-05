---
id: redis/00-overview
topic: redis
slug: overview
title: "Redis Overview"
type: doc
order: 0
status: ready
tags: [redis, overview]
related: [redis/02-data-types, redis/13-caching, redis/20-persistence, redis/26-best-practices, redis/100-common-antipatterns]
when_to_use: "Read first when starting any Redis work, to learn how the topic's docs fit together and which one to open next."
---
# Redis Overview

## Purpose

This document orients you to the Redis knowledge base. Redis is a single-threaded,
in-memory key/value data store that also durably persists to disk. It is used as a
cache, a session store, a message queue, a rate limiter, and a coordination layer for
distributed systems. These docs teach an agent to use Redis correctly: choosing the
right data type, respecting the single-threaded command model, and avoiding the
operational traps (unbounded memory, blocking commands, lost data) that only surface
in production.

Use this page as a map. Each concept has a dedicated doc; open the one that matches
your task rather than guessing at commands.

## Why It Matters

Redis is fast because it is simple: one thread executes one command at a time, entirely
in RAM. That model is also the source of every common mistake. A single `KEYS *` or a
large `SMEMBERS` blocks the whole server for every client. An unbounded list or a
missing `EXPIRE` fills memory until Redis starts evicting or refusing writes. A cache
without a persistence and invalidation strategy silently serves stale data. Getting
Redis right is less about knowing commands and more about respecting the constraints
this map lays out.

## The Documents

**Foundations** — read these before writing any command.
- [Installation](01-installation.md) — running Redis locally and in containers, and
  connecting a client.
- [Data Types](02-data-types.md) — the full type menu and how to pick the right one.

**Data types in depth** — one doc per type, with commands and complexity.
- [Strings](03-strings.md) — counters, cached blobs, atomic `SET` flags.
- [Lists](04-lists.md) — queues and stacks; the blocking pop commands.
- [Sets](05-sets.md) — membership, deduplication, set algebra.
- [Sorted Sets](06-sorted-sets.md) — leaderboards, time-ordered indexes, priority queues.
- [Hashes](07-hashes.md) — object/record storage under a single key.
- [Streams](08-streams.md) — append-only logs with consumer groups.

**Messaging and coordination.**
- [Pub/Sub](09-pub-sub.md), [Transactions](10-transactions.md),
  [Lua Scripting](11-lua-scripting.md), [Expiration](12-expiration.md).

**Application patterns.**
- [Caching](13-caching.md), [Rate Limiting](14-rate-limiting.md),
  [Session Storage](15-session-storage.md), [Message Queues](16-message-queues.md),
  [Distributed Locks](17-distributed-locks.md).

**Operations.**
- [Replication](18-replication.md), [Clustering](19-clustering.md),
  [Persistence](20-persistence.md), [Security](21-security.md),
  [Monitoring](22-monitoring.md), [Performance](23-performance.md).

**Engineering discipline.**
- [Testing](24-testing.md), [Debugging](25-debugging.md),
  [Best Practices](26-best-practices.md), [Production](27-production.md),
  [Common Antipatterns](100-common-antipatterns.md), and the
  [production](98-production-checklist.md) / [AI review](99-ai-review-checklist.md)
  checklists.

## Core Principles

- **Redis is single-threaded; every command has a cost.** Know the time complexity
  (Big-O) of each command you run. `O(N)` commands over large keys stall every client.
- **Model the access pattern first, then pick the type.** The right data type turns an
  `O(N)` scan into an `O(1)` lookup. See [Data Types](02-data-types.md).
- **In-memory means bounded.** Every key must have a lifecycle: an `EXPIRE`, a cap, or
  an explicit deletion. Memory that only grows is an outage waiting to happen.
- **Persistence is a choice, not a default guarantee.** Understand RDB vs AOF before you
  rely on Redis to survive a restart. See [Persistence](20-persistence.md).
- **Treat Redis as a shared, remote resource.** Network round trips dominate latency;
  batch with pipelines and avoid chatty per-item calls.

## Best Practices

- Namespace keys with a consistent scheme (`app:user:42:session`) so keys are debuggable
  and safe to scan by prefix. The cost is verbosity; the benefit is operability.
- Prefer `SCAN` over `KEYS`, and never run `O(N)` commands (`KEYS`, `SMEMBERS`,
  `HGETALL` on huge keys) against production.
- Set an expiry at write time for anything cache-like, so a forgotten key cannot leak.
- Pipeline or use server-side scripts for multi-command sequences to cut round trips.
- Decide persistence and eviction policy explicitly per deployment; do not inherit
  defaults blindly.

## Common Mistakes

- Reaching for Redis as a primary database without understanding its durability model.
- Storing large values or unbounded collections under one key, creating "hot keys" that
  block the server.
- Skipping expiry, so a cache grows into an out-of-memory incident.
- Using `KEYS` in application code because it worked on a small dev dataset.
- Ignoring command complexity and discovering the `O(N)` cost only under production load.

## AI Review Checklist

- Is the chosen data type justified by the actual access pattern?
- Does every command's time complexity scale safely with production data volume?
- Does every cache-like key have an expiry or explicit eviction plan?
- Is `SCAN` used instead of `KEYS` anywhere keys are enumerated?
- Is the persistence and durability requirement stated and matched by config?

## Related


- `knowledge/redis/02-data-types.md`
- `knowledge/redis/13-caching.md`
- `knowledge/redis/20-persistence.md`
- `knowledge/redis/26-best-practices.md`
- `knowledge/redis/100-common-antipatterns.md`
