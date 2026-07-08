---
id: architecture/02-system-design
topic: architecture
slug: system-design
title: "System Design"
type: doc
order: 2
status: ready
tags: [architecture, system-design]
related: [architecture/01-software-architecture, architecture/13-scalability, architecture/16-high-availability, architecture/17-fault-tolerance, architecture/21-distributed-systems]
when_to_use: "Read before designing a new service or feature that must meet concrete scale, latency, or availability targets."
---
# System Design

## Purpose

This document defines how to design a system to meet explicit non-functional requirements:
capacity, latency, availability, and consistency. Where [software architecture](01-software-architecture.md)
is about *internal* structure, system design is about *external* behavior under load — how
the pieces are sized, connected, and made to survive failure.

It is written so an agent can turn a vague "build X" into a design with named numbers,
identified bottlenecks, and stated trade-offs.

## Why It Matters

A system that is correct for one user can fail completely for a million, and the failure
mode is rarely graceful — it is cascading timeouts, exhausted connection pools, and data
corruption under contention. These outcomes are determined at design time by choices about
data storage, statelessness, and failure handling. Retrofitting them after launch means a
rewrite under production pressure. Designing against explicit numbers up front is the
difference between scaling by adding machines and scaling by rebuilding.

## Core Principles

- **Start from numbers, not components.** Estimate reads/writes per second, payload sizes,
  data volume, and the latency budget *before* drawing boxes. The numbers dictate the
  design; guessing the design first inverts the process.
- **Identify the bottleneck resource.** Every system is limited by one thing first — CPU,
  memory, disk I/O, network, or a database lock. Design for that constraint; optimizing
  anything else is wasted effort.
- **Make services stateless; push state to dedicated stores.** Stateless compute scales
  horizontally by adding instances. State (sessions, caches, data) belongs in databases and
  caches built to hold it, so any instance can serve any request.
- **You cannot have consistency, availability, and partition tolerance all at once.**
  Networks partition, so you are choosing between consistency and availability under
  failure. Decide per-operation which one matters and design accordingly.
- **Design for failure as the normal case.** At scale, something is always broken. Timeouts,
  retries with backoff, circuit breakers, and graceful degradation are requirements, not
  polish. See [fault-tolerance](17-fault-tolerance.md).

## Best Practices

- Write down the SLOs first: target p99 latency, requests/sec, and availability (e.g.
  99.9%). Every later decision is measured against these; without them "fast enough" is
  undefined.
- Set an explicit end-to-end latency budget and allocate it across hops. If the budget is
  200 ms, a call chain of five 100 ms services cannot meet it — the math is the design.
- Cache the read-heavy, expensive, and rarely-changing. Pick an invalidation strategy up
  front (TTL, write-through, or explicit purge); a cache without an invalidation plan serves
  stale data. See [caching-strategies](19-caching-strategies.md).
- Prefer asynchronous processing (queues, events) for work that does not need an immediate
  answer. It smooths traffic spikes and decouples producer from consumer, at the cost of
  eventual consistency the client must tolerate.
- Add a bottleneck-relief plan before you need it: read replicas, sharding key, or a
  partition strategy. Retrofitting a shard key onto live data is a migration nightmare.
- Design idempotent operations for anything that can be retried, so a duplicate request
  (from a retry or at-least-once queue) does not double-charge or double-write.

## Examples

**Good Example** — capacity estimate drives the design

```text
Requirement: URL shortener, 100M new links/month, 10:1 read:write, links live 5 years.

Writes:  100M / (30·86400s) ≈ 40 writes/sec  → single primary DB handles this easily.
Reads:   ≈ 400 reads/sec, key-value by short code → cache hot codes; DB is the fallback.
Storage: 100M/mo · 60mo · ~500 B ≈ 3 TB → exceeds one node comfortably → shard by code.
Latency budget 50 ms p99 → redirect served from cache, never a cold multi-hop path.

Design follows the numbers: stateless redirect service + Redis cache + sharded KV store.
```

**Bad Example** — pattern chosen before the numbers

```text
"Let's use microservices with Kafka, event sourcing, and a service mesh."

- No estimate of traffic, data size, or latency budget — the design answers no question.
- 40 writes/sec does not need Kafka or sharding; it fits in one Postgres instance.
- Every added component adds failure modes and latency the requirement never asked for.
Result: a distributed system's operational cost for a single-node problem.
```

## Common Mistakes

- Skipping the back-of-the-envelope estimate and choosing components by reputation.
- Building stateful application servers, then discovering they cannot scale horizontally.
- Treating the database as infinitely fast — ignoring lock contention, connection limits,
  and the N+1 query pattern until it melts under load.
- Ignoring the consistency/availability trade-off and being surprised by stale reads or
  write conflicts during a partition.
- Adding retries without idempotency or backoff, turning a blip into a retry storm that
  amplifies the outage.

## Production Tips

- Load-test against the SLO numbers before launch; a design validated only on paper is a
  hypothesis. Measure p99, not just the average — the average hides the tail that pages you.
- Instrument the bottleneck resource explicitly (DB connections, queue depth, cache hit
  rate) and alert on it. See [observability](18-observability.md).
- Keep a capacity model that maps traffic growth to the next scaling action, so you scale
  before saturation, not during the incident.

## AI Review Checklist

- Are there explicit SLO numbers (throughput, p99 latency, availability) driving the design?
- Is the primary bottleneck resource identified and designed for?
- Are application services stateless, with state in purpose-built stores?
- Is the consistency-vs-availability choice made deliberately per operation?
- Are retried operations idempotent, with backoff to prevent retry storms?
- Is there a documented plan for the next order-of-magnitude of growth?

## Related

- `knowledge/architecture/01-software-architecture.md`
- `knowledge/architecture/13-scalability.md`
- `knowledge/architecture/16-high-availability.md`
- `knowledge/architecture/17-fault-tolerance.md`
- `knowledge/architecture/21-distributed-systems.md`
