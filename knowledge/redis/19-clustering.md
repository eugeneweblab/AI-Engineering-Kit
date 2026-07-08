---
id: redis/19-clustering
topic: redis
slug: clustering
title: "Clustering"
type: doc
order: 19
status: ready
tags: [redis, clustering]
related: [redis/18-replication, redis/10-transactions, redis/17-distributed-locks, redis/23-performance]
when_to_use: "Read before sharding Redis across multiple primaries or when a single node can no longer hold the dataset."
---
# Clustering

## Purpose

This document defines how to run Redis Cluster: data sharded across many primaries
by hash slot, each primary backed by replicas. It covers the slot model, why
multi-key operations are constrained, hash tags, and how clients must handle
redirection. For a single primary with copies, see [replication](18-replication.md).

Clustering answers "my dataset or throughput exceeds one node — how do I scale
horizontally?". Reach for it only when you have that problem; it adds real
constraints that a single node does not have.

## Why It Matters

Redis Cluster partitions keys across **16384 hash slots**. Any command touching
multiple keys that land in **different slots** is rejected with a `CROSSSLOT`
error. Code that worked perfectly on a single node — an `MGET`, a `MULTI` across
two keys, a Lua script reading two keys — can throw the moment you shard. This is
not a bug to work around; it is the model. Designing key names *before* you shard
is far cheaper than rewriting access patterns after a `CROSSSLOT` outage.

## Core Principles

- **Keys map to slots by CRC16(key) mod 16384.** The cluster owns the mapping;
  slots move between nodes during resharding, and clients must follow.
- **Multi-key commands require all keys in one slot.** Otherwise `CROSSSLOT`.
  Group related keys with a **hash tag** `{...}` so they share a slot.
- **The topology changes under you.** Nodes return `MOVED` (permanent) and `ASK`
  (in-progress migration) redirects. A cluster-aware client must honour both.
- **Transactions and Lua are single-slot only.** Atomicity across shards does not
  exist in Redis Cluster; do not design for it.
- **Each shard is its own primary+replica group.** Failover is per-shard; losing a
  primary without a healthy replica loses that slice of the keyspace.

## Best Practices

- Use a **cluster-aware client** (redis-py in cluster mode, Lettuce, ioredis
  cluster) so `MOVED`/`ASK` redirects are handled automatically. Never parse them
  yourself.
- Co-locate keys that are used together with a **hash tag**: `user:{42}:profile`
  and `user:{42}:sessions` hash on `42` and share a slot, so `MGET`/`MULTI`/Lua
  work. Choose the tag deliberately to avoid hot slots.
- Keep tags **coarse enough to co-locate, fine enough to spread load.** Tagging
  everything with `{global}` puts the whole dataset on one shard.
- Run **at least 3 primaries with 1 replica each** (6 nodes). Fewer primaries
  cannot tolerate a failure without losing a slot range.
- Reshard with `redis-cli --cluster reshard`; let it move slots gradually. Watch
  for hot slots and rebalance rather than adding nodes blindly.
- Prefer clustering only when you actually exceed one node. A single primary with
  replicas is simpler and covers most workloads.

## Examples

**Good Example** — hash tag co-locates related keys into one slot

```python
from redis.cluster import RedisCluster

rc = RedisCluster(host="cluster.internal", port=6379)

# Braces make the hash tag: only "user:1042" is hashed, so both keys share a slot.
# WHY: MGET, MULTI, and Lua across these keys now stay within one node and are legal.
rc.mset({
    "user:{1042}:profile":  "...",
    "user:{1042}:sessions": "...",
})
profile, sessions = rc.mget("user:{1042}:profile", "user:{1042}:sessions")  # OK
```

**Bad Example** — unrelated keys in a multi-key op across slots

```python
# No hash tags: these two keys hash to (almost certainly) different slots.
rc.mget("user:1042:profile", "user:2087:profile")
# redis.exceptions.RedisClusterException: CROSSSLOT Keys in request don't hash
# to the same slot. The single-node code path that "just worked" now fails hard.

# "Fixing" it by tagging everything the same:
rc.mset({"user:{all}:a": 1, "user:{all}:b": 2})  # every key -> one hot shard
```

## Common Mistakes

- Assuming `MGET`, `MSET`, `SUNIONSTORE`, `MULTI`, or multi-key Lua work across
  shards. They only work within a single slot.
- Using a non-cluster client, so `MOVED`/`ASK` redirects surface as errors.
- Tagging keys too broadly (`{tenant}` for a huge tenant) and creating a hot slot
  that pins load to one node.
- Running a cluster with 1–2 primaries, which cannot survive a node loss.
- Expecting cross-shard transactions or atomicity. There is none.
- Hard-coding node IPs; the client must discover topology and follow resharding.

## Production Tips

- Monitor per-node key distribution and slot balance; alert on hot slots and on
  `cluster_state:fail` from `CLUSTER INFO`.
- Ensure a primary and its replica are on **different hosts / availability zones**
  so one failure cannot take both.
- Test resharding and node failure in staging; confirm the client transparently
  follows `MOVED` and that no slots are left unassigned.
- If you only need read scaling or HA, use replication + Sentinel first — it is
  simpler than a cluster and has no cross-slot constraints.

## AI Review Checklist

- Are related keys co-located with a hash tag so their multi-key ops stay in one
  slot?
- Is the client cluster-aware (handles `MOVED`/`ASK`), not a single-node client?
- Does any code assume cross-shard `MULTI`/Lua/`MGET` atomicity? (It must not.)
- Are hash tags scoped to avoid hot slots?
- Are there ≥3 primaries, each with a replica on a separate host?
- Is clustering actually justified, or would replication suffice?

## Related

- `knowledge/redis/18-replication.md`
- `knowledge/redis/10-transactions.md`
- `knowledge/redis/17-distributed-locks.md`
- `knowledge/redis/23-performance.md`
