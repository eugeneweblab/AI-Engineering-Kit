---
id: devops/20-scalability
topic: devops
slug: scalability
title: "DevOps Scalability"
type: doc
order: 20
status: ready
tags: [devops, scalability]
related: [devops/19-high-availability, devops/21-performance, devops/11-orchestration, devops/12-monitoring, devops/27-sre-principles]
when_to_use: "Read before designing autoscaling, capacity, or any system expected to grow in load or data."
---
# DevOps Scalability

## Purpose

This document defines how a system absorbs growth — more requests, more data, more
users — without a rewrite and without runaway cost. It is written so an agent can design
or review an architecture that scales along the axis that actually matters, and can tell
the difference between a scaling problem and a [performance](21-performance.md) problem.

Scalability answers "can we handle 10x the load by adding resources?". It is distinct
from performance (how fast a single request is) and from [high availability](19-high-availability.md)
(staying up through faults). A fast system can still fail to scale; a scalable system can
still be slow. You size each concern separately.

## Why It Matters

Scaling failures show up at the worst time — a launch, a viral moment, a Black Friday —
when load is highest and the fix is hardest. The cause is almost never CPU; it is a hidden
bottleneck that does not scale horizontally: a single primary database, a lock, an
in-memory cache, a queue with one consumer. Because Amdahl's law says the serial fraction
caps your speedup, one un-scalable component silently sets the ceiling for the entire
system no matter how many machines you add.

## Core Principles

- **Scale horizontally by default.** Prefer adding more small stateless instances over one
  bigger machine. Vertical scaling hits a hard hardware ceiling; horizontal scaling does
  not, and it gives you HA for free.
- **Statelessness is the enabler.** An instance that holds no session or local state can be
  cloned, load-balanced, and killed freely. Push state to a database, cache, or object store.
- **Find the real bottleneck before adding capacity.** The constraint is usually one shared
  resource (DB, lock, queue). Adding app servers behind a saturated database makes it worse.
- **Design for the growth axis you actually have.** Read-heavy, write-heavy, data-volume,
  and fan-out each demand different solutions (replicas, sharding, partitioning, queues).
- **Load must shed, not collapse.** Beyond capacity a system should reject or queue
  gracefully (backpressure), not tip into cascading failure.

## Best Practices

- Keep services **stateless**; externalize session state to Redis/DB so any instance is
  interchangeable and autoscaling can add/remove replicas at will.
- **Scale reads with replicas and caching; scale writes with partitioning/sharding.** These
  are different problems — replicas do nothing for a write bottleneck.
- Use **asynchronous queues** to decouple producers from slow consumers, absorb spikes, and
  let you scale consumers independently. The cost is eventual consistency — design for it.
- Configure **autoscaling on the metric that reflects load** (request rate, queue depth,
  p95 latency), not just CPU. CPU-based scaling misses I/O-bound and queue-bound bottlenecks.
- Apply **backpressure and rate limiting** at the edge so overload sheds cleanly instead of
  exhausting the database and taking everything down.
- **Cache deliberately** with explicit TTLs and invalidation, and guard against stampedes
  (request coalescing / jittered expiry). A cache that all expires at once is a load spike.
- **Load-test to the target** (2–3x expected peak) and find the knee of the curve *before*
  production does. Capacity you have not measured is capacity you do not have.
- Watch for **N+1 queries and unbounded fan-out**; they turn linear traffic growth into
  quadratic database load.

## Examples

**Good Example** — stateless worker scaled on queue depth, with backpressure

```ts
// Stateless consumer: no local state, so K replicas process the SAME queue safely.
async function handleJob(job: Job) {
  await processOrder(job.payload);   // all state lives in DB/queue, not the process
}

// Enqueue instead of doing slow work inline → spikes are absorbed, not dropped.
app.post("/orders", rateLimit({ max: 100, window: "1s" }), async (req, res) => {
  if (await queue.depth() > MAX_BACKLOG) return res.status(503).send("busy"); // shed load
  await queue.add("order", req.body);                                        // return fast
  res.status(202).send();            // 202 Accepted; work happens async, scale consumers up
});
```

```yaml
# Autoscale on queue depth (the real signal of pending work), not just CPU.
metrics:
  - type: External
    external:
      metric: { name: queue_messages_ready }
      target: { type: AverageValue, averageValue: "30" } # add workers when backlog grows
```

**Bad Example** — stateful, synchronous, and bottlenecked on one primary

```ts
const sessions = new Map(); // in-memory state → cannot add a second instance safely

app.post("/orders", async (req, res) => {
  const order = await db.insert(req.body); // synchronous heavy write, no backpressure
  for (const item of order.items) {
    await inventory.reserve(item);         // N+1 round-trips per request; fan-out explodes
  }
  res.send(order); // a traffic spike stampedes the single primary DB → cascading failure
});
```

## Common Mistakes

- Holding session or cache state in process memory, blocking horizontal scaling.
- Adding app servers in front of an already-saturated single database.
- Autoscaling on CPU only, missing I/O-, lock-, and queue-bound bottlenecks.
- Doing slow work synchronously in the request path instead of via a queue.
- No backpressure, so overload cascades into total collapse instead of shedding.
- Caches that all expire simultaneously (no jitter), causing stampede spikes.
- N+1 queries and unbounded fan-out that make load grow super-linearly.

## Production Tips

- Track **cost per request / per tenant** alongside throughput; "scalable but unaffordable"
  is still a failure. Autoscaling without a max bound is a budget incident waiting to happen.
- Set **autoscaling min, max, and cooldown** so you neither flap nor scale into a bill spike.
- Keep a **capacity model** (requests → DB connections → replicas) so you can predict the
  next bottleneck instead of discovering it under load.

## AI Review Checklist

- Are services stateless with session/local state externalized?
- Is the identified bottleneck the real constraint (DB/lock/queue), not just app CPU?
- Are reads scaled with replicas/cache and writes with partitioning/sharding, as needed?
- Is slow work moved to async queues with independently scalable consumers?
- Does autoscaling target a load-reflecting metric with sane min/max/cooldown?
- Is there backpressure/rate limiting so overload sheds instead of cascading?
- Has the system been load-tested to 2–3x expected peak?

## Related


- `knowledge/devops/19-high-availability.md`
- `knowledge/devops/21-performance.md`
- `knowledge/devops/11-orchestration.md`
- `knowledge/devops/12-monitoring.md`
- `knowledge/devops/27-sre-principles.md`
