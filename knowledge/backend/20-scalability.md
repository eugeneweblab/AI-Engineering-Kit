---
id: backend/20-scalability
topic: backend
slug: scalability
title: "Backend Scalability"
type: doc
order: 20
status: ready
tags: [backend, scalability, reserve, save]
related: [backend/19-performance, backend/13-caching, backend/15-message-brokers, backend/16-background-jobs, backend/17-transactions]
when_to_use: "Read before designing a service to run on multiple instances, adding horizontal scaling, or when a single node can no longer keep up."
---
# Backend Scalability

## Purpose

This document defines how to design backend services that grow with load: statelessness,
horizontal scaling, avoiding shared bottlenecks, and handling contention. It is written so
an agent builds a service that can run as many identical copies safely, rather than one
that only works as a single process.

Scalability is the ability to handle more load by adding resources, ideally in a straight
line. It is a different question from [performance](19-performance.md): performance makes
one request faster; scalability lets you serve more requests at once. A slow service can
scale; a fast service can fail to.

## Why It Matters

The instance you run in development is not the topology you run in production. Production
runs many copies behind a load balancer, restarts them on deploy, and moves requests
between them. Any assumption that "the same process handles the next request" — in-memory
sessions, a local cache treated as authoritative, a counter in a variable — breaks the
moment there are two instances, and it breaks intermittently, which is the worst kind of
bug. Designing for horizontal scale from the start costs almost nothing; retrofitting it
means rewriting state handling under production pressure.

## Core Principles

- **Keep the application tier stateless.** Any instance must be able to serve any request.
  Store session, cache, and coordination state in a shared backing store (database, Redis),
  never in process memory.
- **Scale horizontally by default.** Add more instances (scale out) rather than a bigger
  box (scale up). Scale-out has no ceiling and survives single-node failure; scale-up hits
  a wall and a single point of failure.
- **The shared resource is the bottleneck.** When you scale the app tier, load concentrates
  on whatever is still singular — usually the database. Plan its capacity first.
- **Design for concurrent writers.** With N instances, N requests hit the same row at once.
  Correctness must come from the database (locks, atomic operations, constraints), not from
  "only one process runs this."
- **Decouple with queues to absorb spikes.** A [message broker](15-message-brokers.md)
  lets a slow consumer drain a burst instead of the front end collapsing under it.

## Best Practices

- Hold no request-scoped state between requests in memory. If a value must survive, put it
  in a shared store keyed by user/session.
- Make write operations atomic at the database (`UPDATE ... SET n = n + 1`, unique
  constraints, `INSERT ... ON CONFLICT`) rather than read-modify-write in application code.
- Make endpoints idempotent where clients may retry (idempotency keys on POST); at scale,
  retries and duplicate deliveries are certain, not rare.
- Offload spiky or slow work to a queue and process it with independently scalable workers.
- Read-scale the database with replicas for read-heavy traffic; route writes to the primary
  and tolerate replica lag explicitly.
- Set per-instance resource limits (connection pool size, concurrency) so N instances do not
  exhaust the database's connection limit. Total connections = instances x pool size.
- Prefer stateless auth tokens or a shared session store so any instance can validate a
  request without sticky sessions.

## Examples

**Good Example** — atomic write, correct under concurrent instances

```ts
// The database performs the increment atomically, so N instances hitting the same
// row concurrently all produce the correct final count.
await db.query(
  `UPDATE inventory
     SET quantity = quantity - $1
   WHERE sku = $2 AND quantity >= $1`, // constraint prevents overselling
  [amount, sku],
);
// Zero rows updated => not enough stock; decide from the row count, not a prior read.
```

**Bad Example** — read-modify-write and in-memory state

```ts
const localCache = new Map();            // lives in ONE instance; others never see it

async function reserve(sku: string, amount: number) {
  const item = await db.getInventory(sku);   // read
  if (item.quantity >= amount) {             // check — another instance passed here too
    item.quantity -= amount;                 // modify in memory
    await db.save(item);                     // write — last writer wins, stock oversold
  }
  localCache.set(sku, item);                 // stale on every other instance
}
```

## Common Mistakes

- In-memory sessions, caches, or counters that silently break the moment a second instance
  starts.
- Read-modify-write races: two instances read the same value, both act, one update is lost.
- Sticky sessions used to paper over server-side state instead of removing the state.
- Ignoring database connection limits, so scaling the app tier exhausts the database.
- Assuming a message or webhook is delivered exactly once; without idempotency, duplicates
  corrupt data.
- Treating replica reads as immediately consistent, then reading your own write before it
  replicates.
- Scaling up (bigger machine) as the only lever until it hits a hard ceiling with no path out.

## Production Tips

- Autoscale on a leading signal (queue depth, CPU, p99 latency), not just raw request count.
- Put a connection pooler (e.g. PgBouncer) in front of the database so instance count and
  database connections scale independently.
- Load-test the whole topology, including the database, not a single instance in isolation.
- Make deploys and restarts safe: instances can be killed mid-request, so drain connections
  and rely on idempotency and retries.

## AI Review Checklist

- Is the application tier fully stateless (no session, cache, or counter in process memory)?
- Are concurrent writes made correct by the database (atomic updates, constraints), not by
  assuming a single writer?
- Are retryable operations idempotent, tolerating duplicate delivery?
- Will total connections (instances x pool size) stay within the database limit?
- Is spiky or slow work offloaded to a queue with independently scalable workers?
- Does the code tolerate replica lag rather than assuming read-after-write consistency?
- Can any instance serve any request without sticky sessions?

## Related

- `knowledge/backend/19-performance.md`
- `knowledge/backend/13-caching.md`
- `knowledge/backend/15-message-brokers.md`
- `knowledge/backend/16-background-jobs.md`
- `knowledge/backend/17-transactions.md`
