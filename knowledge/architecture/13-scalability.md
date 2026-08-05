---
id: architecture/13-scalability
topic: architecture
slug: scalability
title: "Architecture Scalability"
type: doc
order: 13
status: ready
tags: [architecture, scalability]
related: [architecture/14-performance, architecture/19-caching-strategies, architecture/16-high-availability, architecture/21-distributed-systems, architecture/09-microservices]
when_to_use: "Read before designing a service that must handle growth in traffic, data, or concurrency."
---
# Architecture Scalability

## Purpose

This document defines how a system absorbs more load — more requests, more data,
more users — without a rewrite. It covers horizontal vs vertical scaling, statelessness,
data partitioning, and the bottlenecks that decide the real ceiling. It is written so
an agent can design or review a component that will still work at 10x its current load.

Scalability is about the *shape* of growth, not raw speed. A fast system that can only
run on one bigger box is not scalable; a modest one that adds capacity by adding nodes
is. Do not confuse the two — see [performance](14-performance.md) for latency and
throughput of a single request.

## Why It Matters

Load rarely grows gently; it arrives in spikes — a launch, a campaign, a viral moment —
and the parts that cannot scale are exactly where the system falls over. The expensive
failure is architectural: a design that assumes one server, one writable database, or
in-process session state cannot be scaled by adding hardware, so the fix is a rewrite
under fire. Deciding statelessness and partitioning strategy early costs almost nothing;
retrofitting them into a live system costs months. Scalability is a property you design
in, not a setting you turn up.

## Core Principles

- **Scale out, not just up.** Vertical scaling (a bigger machine) has a hard ceiling and
  a single point of failure. Horizontal scaling (more machines) is the path to elasticity
  and redundancy — design for it first.
- **Keep the request path stateless.** Any node must handle any request. Push session and
  mutable state to a shared store (cache/DB) so instances are interchangeable and disposable.
- **Find the bottleneck; that is your real limit.** A system scales only as far as its
  most constrained shared resource — usually the database, a lock, or a single queue.
  Adding app servers past that point does nothing.
- **Partition data to scale writes.** Reads scale with replicas and caches; writes scale
  only by sharding data across independent partitions.
- **Prefer async for spikes.** A queue absorbs a burst and lets consumers drain it at a
  steady rate, converting a load spike into a latency increase instead of an outage.

## Best Practices

- Store no per-user state in application memory. Sessions, uploads, and in-flight data go
  to a shared cache, object store, or database so instances can be added and killed freely.
- Put stateless services behind a load balancer and enable autoscaling on a leading signal
  (CPU, queue depth, request rate) — not on a lagging one like error rate.
- Offload read pressure with caching before scaling the database
  (see [caching-strategies](19-caching-strategies.md)); most systems are read-heavy.
- Use read replicas for read scaling, and shard by a stable key (e.g. tenant or user ID)
  for write scaling. Choose the shard key so load spreads evenly and hot keys are rare.
- Make batch and background work idempotent and horizontally parallel, coordinated through
  a queue rather than a single cron on one box.
- Load-test to find the knee of the curve before production does. Know your capacity per
  instance so autoscaling targets are grounded in data, not guesses.
- Set connection-pool limits deliberately: a fleet of app servers can open more DB
  connections than the database can serve, and that becomes the bottleneck.

## Examples

**Good Example** — stateless node, shared session store

```python
# Session lives in Redis, keyed by a signed cookie. WHY: any instance can serve
# any request, so the load balancer can spread traffic and autoscaling can add or
# remove nodes with zero session loss.
def get_cart(request) -> Cart:
    session_id = verify_cookie(request.cookies["sid"])
    return redis.get(f"cart:{session_id}")  # shared state, not in-process
```

**Bad Example** — in-memory state pins users to one node

```python
# Cart stored in a per-process dict. WHY this fails at scale: the user must return
# to the SAME instance every time (sticky sessions), so load cannot be balanced
# evenly, autoscaling-down drops live carts, and a crash loses them entirely.
CARTS = {}  # process-local; dies with the process

def get_cart(request) -> Cart:
    return CARTS[request.user_id]  # only valid on the node that stored it
```

## Common Mistakes

- Keeping session, cache, or uploaded files in application memory, forcing sticky
  sessions and making instances non-interchangeable.
- Scaling app servers while the single-writer database stays the bottleneck — more
  nodes just pile more load onto the same constraint.
- Choosing a shard key with skew (e.g. country) so one shard gets a "hot" majority of
  traffic and the rest sit idle.
- Autoscaling on a lagging metric, so capacity arrives only after users are already failing.
- Ignoring connection-pool math, so a scaled fleet exhausts database connections.
- Treating scalability as a future problem and baking in stateful, single-node assumptions
  that require a rewrite to undo.

## Production Tips

- Track saturation of each shared resource (DB connections, CPU, queue depth), not just
  request rate — saturation predicts the wall before you hit it.
- Test scale-down as well as scale-up; graceful shutdown (drain in-flight requests) matters
  as much as fast startup.
- Cap autoscaling with a sane maximum to avoid a runaway cost spiral or self-inflicted
  DDoS on a downstream dependency.

## AI Review Checklist

- Is the request path stateless, with session/state in a shared store?
- Can the service scale horizontally behind a load balancer, or is it pinned to one node?
- Is the true bottleneck identified (usually the database or a lock), and does the design
  address it rather than just adding app servers?
- Are writes partitioned by a shard key chosen to avoid hot spots?
- Does autoscaling trigger on a leading signal with a sane maximum?
- Are load spikes absorbed by a queue instead of overwhelming synchronous handlers?

## Related

- `knowledge/architecture/14-performance.md`
- `knowledge/architecture/19-caching-strategies.md`
- `knowledge/architecture/16-high-availability.md`
- `knowledge/architecture/21-distributed-systems.md`
- `knowledge/architecture/09-microservices.md`
