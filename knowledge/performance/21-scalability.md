---
id: performance/21-scalability
topic: performance
slug: scalability
title: "Performance Scalability"
type: doc
order: 21
status: ready
tags: [performance, scalability]
related: [performance/20-capacity-planning, performance/22-load-testing, performance/08-caching, performance/13-database-performance, performance/05-network]
when_to_use: "Read before designing a system to handle growth, or when a service stops getting faster as you add hardware."
---
# Performance Scalability

## Purpose

This document defines how a system's capacity grows with the resources you give it:
horizontal vs vertical scaling, statelessness, and the bottlenecks that cap growth. It
exists so an agent designs services that get faster when you add machines — and
recognizes when they will not.

Scalability is the *how much more* to [capacity planning](20-capacity-planning.md)'s
*how much now*. Capacity planning sizes for known load; scalability is the property that
lets you meet load you have not sized for yet.

## Why It Matters

Adding hardware does not automatically add capacity. A system scales only as well as its
most contended shared resource — a single database, a global lock, a session store. Double
the app servers in front of a maxed-out database and throughput does not move; you have
spent money and changed nothing. Worse, some designs get *slower* as you add nodes, because
coordination overhead grows faster than the work. Understanding what bounds scaling is the
difference between growth being a config change and growth being a rewrite under fire.

## Core Principles

- **Horizontal beats vertical past a point.** Vertical scaling (a bigger machine) is
  simple but has a hard ceiling and a single failure domain. Horizontal scaling (more
  machines) is unbounded and fault-tolerant — but only if the workload is stateless.
- **Statelessness is the enabler.** A node that holds no request-specific state can be
  cloned, load-balanced, and killed freely. Push session/state to a shared store
  ([caching](08-caching.md)) or a client token so any node can serve any request.
- **The bottleneck moves; find the new one.** Relieve the app tier and the database
  becomes the limit; relieve the database and the network does. Scaling is iterative
  bottleneck removal, guided by [saturation metrics](02-metrics.md) (USE).
- **Shared mutable state is the enemy of scale.** Global locks, single-writer databases,
  and cross-node coordination serialize work — Amdahl's law caps you at the serial
  fraction no matter how many nodes you add.
- **Data is the hard part.** Stateless app tiers scale trivially; the
  [database](13-database-performance.md) does not. Read replicas, partitioning/sharding,
  and caching are how the data tier scales, and each adds real complexity.

## Best Practices

- Make services **stateless** so they scale horizontally behind a load balancer; store
  session and shared state in a database or distributed cache, never in process memory.
- Scale reads with a **cache** and **read replicas** before sharding — most workloads are
  read-heavy, and caching is far cheaper than partitioning.
- Shard/partition writes only when a single primary is genuinely the bottleneck; pick a
  partition key that spreads load evenly and avoids cross-shard transactions.
- Prefer **asynchronous** processing (queues) for spiky or slow work so a burst is
  buffered, not dropped, and consumers scale independently of producers.
- Design for **graceful degradation**: shed load, serve stale cache, or queue rather than
  collapse when a downstream saturates.
- Confirm scalability by [load testing](22-load-testing.md) at increasing node counts —
  linear-ish throughput gain proves it; a plateau names the next bottleneck.

## Examples

**Good Example** — stateless node, shared state externalized

```ts
// Session lives in a shared store, so ANY node can serve ANY request → clone freely.
app.use(async (req, res, next) => {
  const session = await redis.get(`sess:${req.cookies.sid}`); // shared, not in-process
  req.user = session?.user;
  next();
});
// Add 10 more identical nodes behind the LB; throughput scales with node count.
```

**Bad Example** — sticky in-process state caps horizontal scaling

```ts
const sessions = new Map(); // in-process state → this node is the only one that has it

app.post("/login", (req, res) => {
  sessions.set(req.sid, req.user); // now the load balancer must pin the user here (sticky)
  // Sticky sessions defeat horizontal scaling: load is uneven, a node death loses sessions,
  // and you cannot freely add/remove nodes. Throughput plateaus regardless of node count.
});
```

## Common Mistakes

- Scaling the app tier while the database stays a single saturated primary — no gain.
- Holding session or cache state in process memory, forcing sticky sessions and blocking
  horizontal scale.
- Sharding prematurely, adding cross-shard complexity before caching/replicas were tried.
- A global lock or single-writer path that serializes all requests (Amdahl's ceiling).
- Choosing a skewed partition key, creating a hot shard that carries most of the load.
- Assuming scaling is linear and never load-testing at higher node counts to confirm.

## Production Tips

- Watch per-resource saturation (USE) to see which tier will bottleneck *next*, and scale
  it before it does — the moved bottleneck is predictable.
- Load-test the scaled topology, not just one node; emergent bottlenecks (connection
  limits, lock contention) only appear at scale.
- Keep autoscaling policies per-tier — the app tier and the data tier scale on different
  signals and at different speeds.

## AI Review Checklist

- Are application services stateless, with session/shared state in an external store?
- Can the workload scale horizontally, or does sticky state force vertical-only growth?
- Is the data tier's scaling strategy (cache, replicas, sharding) explicit and justified?
- Is there a single shared resource (lock, primary DB) that serializes all requests?
- For sharding, is the partition key even and cross-shard transactions avoided?
- Has throughput been load-tested across node counts to confirm it actually scales?

## Related

- `knowledge/performance/20-capacity-planning.md`
- `knowledge/performance/22-load-testing.md`
- `knowledge/performance/08-caching.md`
- `knowledge/performance/13-database-performance.md`
- `knowledge/performance/05-network.md`
