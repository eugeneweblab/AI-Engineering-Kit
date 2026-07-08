---
id: databases/15-sharding
topic: databases
slug: sharding
title: "Sharding"
type: doc
order: 15
status: ready
tags: [databases, sharding]
related: [databases/16-partitioning, databases/14-replication, databases/13-eventual-consistency, databases/07-indexing, databases/20-performance]
when_to_use: "Read before splitting a dataset across multiple database servers, or when a single node can no longer hold the write load."
---
# Sharding

## Purpose

This document defines how to split one logical dataset across multiple independent
database servers (shards) to scale writes and storage beyond a single machine, and
how to choose a shard key that you will not regret. It exists so an agent can decide
whether sharding is warranted, pick a key, and avoid the queries that sharding makes
impossible.

Sharding splits *different rows onto different servers*. It is distinct from
[partitioning](16-partitioning.md), which splits one table into pieces *within a
single server*, and from [replication](14-replication.md), which copies the *same*
rows to many servers. Sharding is the heaviest of the three — reach for it last.

## Why It Matters

Sharding is the tool of last resort for horizontal write scale, and the shard key is
a near-irreversible decision. A good key spreads load evenly and keeps related data
together; a bad key creates hot shards, forces every query to fan out to all servers,
and makes cross-shard joins and transactions impossible. Worse, changing the key later
means re-sharding the entire dataset live. Teams routinely shard too early (adding
enormous operational cost to solve a problem indexing would have fixed) or shard on the
wrong key (locking themselves into fan-out queries forever). Because the mistake is
expensive and hard to undo, the decision must be reasoned about carefully.

## Core Principles

- **Shard only when a single node genuinely cannot cope.** Exhaust indexing, query
  tuning, read replicas, caching, and partitioning first. Sharding removes cross-node
  transactions and joins — a permanent tax.
- **The shard key determines everything.** It decides data distribution, which queries
  are cheap (single-shard) and which are catastrophic (fan-out), and whether load is
  even. Choose a high-cardinality key that matches your dominant access pattern.
- **Co-locate data that is queried together.** Put rows that a single request needs on
  the same shard (e.g. shard by `tenant_id` so a tenant's data lives together). This
  keeps common queries single-shard.
- **Prefer hash or range routing with a stable mapping.** Hashing spreads load evenly;
  range routing keeps ordered scans local but risks hotspots on monotonic keys.
  Consistent hashing minimizes data movement when shards are added.
- **Cross-shard operations lose ACID.** A transaction spanning shards needs a
  saga/2PC and is slow and failure-prone. Design so the common path never crosses
  shards.

## Best Practices

- Route with a lookup service or consistent-hash ring, not hardcoded modulo, so you
  can add shards without rehashing everything (`hash % N` reshuffles the world when N
  changes).
- Pick a shard key with even distribution and no natural hotspot: `tenant_id`,
  `user_id`, or a hash of them — never `created_at` (all new writes hit one shard) or
  a low-cardinality enum.
- Keep globally-unique ids without a central sequence: use UUIDv7/ULID or per-shard id
  ranges, so shards mint ids independently.
- Make the shard key part of every hot query's `WHERE` clause so the router targets
  one shard. Design secondary access paths (global secondary index, search service)
  for queries that lack the key.
- Handle cross-shard reads with scatter-gather explicitly and sparingly; handle
  cross-shard writes with idempotent sagas, not distributed 2PC where avoidable.
- Plan re-sharding before you need it: dual-write + backfill + cutover, executed
  online. Never assume the first key choice is final without a migration path.

## Examples

**Good Example** — tenant-co-located, stable routing

```ts
// Shard by tenant so every tenant-scoped query hits exactly one shard, and
// route through a consistent-hash ring so adding a shard moves ~1/N of data,
// not all of it.
function shardFor(tenantId: string): Pool {
  return ring.nodeFor(tenantId);          // consistent hashing, stable mapping
}

// The shard key is present -> single-shard, no fan-out.
async function listOrders(tenantId: string) {
  return shardFor(tenantId).query(
    "SELECT * FROM orders WHERE tenant_id = $1", [tenantId]);
}
```

**Bad Example** — modulo routing on a hot key, fan-out queries

```ts
// hash(id) % N: adding one shard changes N and remaps almost every row,
// forcing a full re-shard. And sharding by created_at means all of today's
// writes pile onto a single shard -> hotspot.
const shard = pools[hash(order.created_at) % pools.length];

// No shard key in the WHERE clause: must query EVERY shard and merge,
// so every lookup scales with the number of shards. This never gets faster.
async function findOrder(orderId: string) {
  const results = await Promise.all(
    pools.map(p => p.query("SELECT * FROM orders WHERE id = $1", [orderId])));
  return results.flat().find(Boolean);
}
```

## Common Mistakes

- Sharding before exhausting indexing, replicas, caching, and partitioning — paying a
  permanent complexity tax to solve a temporary load problem.
- Choosing a monotonic or low-cardinality shard key, creating a hot shard.
- Routing with `hash % N`, which forces a full reshuffle whenever N changes.
- Running the common query without the shard key, forcing fan-out on every request.
- Relying on cross-shard transactions/joins for the hot path, losing atomicity and
  performance.
- No re-sharding plan, so the first key choice becomes an unfixable ceiling.

## Production Tips

- Track per-shard size, QPS, and latency; rebalance before any shard becomes a
  hotspot.
- Keep a shard-map/lookup service as the single source of truth for routing, versioned
  and cached.
- Build the online re-shard (dual-write, backfill, verify, cutover) before you are
  forced to, not during an outage.

## AI Review Checklist

- Have cheaper options (indexing, replicas, caching, partitioning) been ruled out
  first?
- Is the shard key high-cardinality, hotspot-free, and aligned with the dominant
  access pattern?
- Does the hot query path always include the shard key (single-shard, no fan-out)?
- Is routing done via consistent hashing / a lookup service, not `hash % N`?
- Are ids globally unique without a central sequence (UUIDv7/ULID or id ranges)?
- Is there an online re-sharding plan, and are cross-shard writes idempotent sagas?

## Related

- `knowledge/databases/16-partitioning.md`
- `knowledge/databases/14-replication.md`
- `knowledge/databases/13-eventual-consistency.md`
- `knowledge/databases/07-indexing.md`
- `knowledge/databases/20-performance.md`
