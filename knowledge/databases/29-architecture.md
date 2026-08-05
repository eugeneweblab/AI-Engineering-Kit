---
id: databases/29-architecture
topic: databases
slug: architecture
title: "Database Architecture"
type: doc
order: 29
status: ready
tags: [databases, architecture]
related: [databases/02-relational-vs-nosql, databases/14-replication, databases/15-sharding, databases/22-high-availability, databases/20-performance]
when_to_use: "Read before choosing a database, or when deciding how the data layer of a system should be structured, scaled, and made resilient."
---
# Database Architecture

## Purpose

This document defines how to structure the data layer of a system: choosing the right database
for each workload, deciding how many databases there are and who owns them, and shaping topology
for scale and resilience (replicas, partitioning, caching, connection management). It sits above
the individual technique docs and connects them into a coherent design.

Database architecture is where the biggest, least-reversible decisions live. A schema column is
easy to change; a choice to share one database across ten services, or to shard on the wrong key,
is expensive to unwind after data and code have grown around it. This doc is about getting those
decisions right the first time and knowing which trade-off you are actually buying.

## Why It Matters

The data layer is usually the hardest part of a system to change and the first part to fall over
under load. Pick the wrong store and you fight the database forever — modeling a graph in a
key-value store, or forcing strong consistency onto an eventually-consistent system. Share one
database across many services and every schema change becomes a cross-team negotiation and every
outage is everyone's outage. Scale prematurely (shard on day one) and you pay huge complexity for
load you don't have; scale too late and you're re-architecting during an incident. Because these
decisions calcify, architecture rewards deferring what you can, making irreversible choices
deliberately, and always knowing which point on the consistency/availability/cost triangle you
picked and why.

## Core Principles

- **Match the store to the workload.** Relational for transactional, relational data with
  invariants; a document/key-value/search/time-series store when its access pattern is your
  dominant one. Don't default to one engine for everything. See [relational vs NoSQL](02-relational-vs-nosql.md).
- **One service owns its data; others go through its API.** A shared database couples services at
  the schema and makes independent deploys impossible. Ownership is the boundary.
- **Consistency, availability, and partition tolerance trade off — choose per workload.** Payments
  need strong consistency; a feed can tolerate staleness. Name the choice explicitly. See
  [eventual consistency](13-eventual-consistency.md).
- **Scale reads and writes with different tools.** Read replicas and caching absorb read load;
  partitioning/sharding absorbs write and storage growth. They solve different problems.
- **Defer irreversible complexity until the load demands it.** Start with one well-indexed primary
  plus replicas; add sharding only when a single primary genuinely can't keep up.

## Best Practices

- Start with a single relational primary and one or more **read replicas**; route reads that
  tolerate slight lag to replicas, writes and read-after-write to the primary. See
  [replication](14-replication.md).
- Add a **cache** for expensive or hot reads, with an explicit invalidation strategy; treat it as
  disposable and never the source of truth. See [performance](20-performance.md).
- **Partition** large tables by a natural boundary (time, tenant) before reaching for cross-node
  **sharding**; choose a shard key that spreads load evenly and matches your query pattern, because
  a bad shard key is very hard to change. See [sharding](15-sharding.md) and [partitioning](16-partitioning.md).
- Give each service its **own schema/database** and integrate through APIs or events, not shared
  tables. Use the outbox pattern for reliable cross-service events, written in the same
  [transaction](09-transactions.md) as the business change.
- Manage connections with a **pooler** (PgBouncer or equivalent); databases have hard connection
  limits and unpooled app instances exhaust them under load.
- Design for failure: automated failover, multi-AZ replicas, and tested restores. Know your RPO/RTO.
  See [high availability](22-high-availability.md) and [backup and recovery](18-backup-and-recovery.md).

## Examples

**Good Example** — workload-matched, service-owned, primary + replica + cache

```text
Orders service      ──owns──►  Postgres (primary, strongly consistent)
                                   │ streaming replication
                                   ▼
                               Postgres (read replica)  ◄── reports/read-heavy queries
                                   ▲
                    cache ◄────────┘  (hot product lookups, explicit TTL + invalidation)

Search service      ──owns──►  OpenSearch   (full-text, its dominant access pattern)
Cross-service data  ──via──►   Orders API / events (outbox), never a shared table
```

- Each store fits its workload; each service owns its data; reads scale on the replica and cache;
  writes stay on one consistent primary. Complexity (sharding) is deferred until measured need.

**Bad Example** — one shared database, wrong store, no read/write separation

```text
Orders ─┐
Billing ─┼──► ONE shared Postgres, all services read/write each other's tables directly
Search ─┘        │
                 └─ full-text search done with LIKE '%term%' on the transactional primary
```

- Shared tables couple every service: one schema migration blocks all teams, one slow query starves
  everyone, and no service can deploy or fail independently. Search on the primary competes with
  transactional load and can't scale. There is no replica or cache, so all load lands on one node.

## Common Mistakes

- One database shared across many services, coupling schemas and making outages global.
- Defaulting every workload to a single engine, forcing a poor fit for search/analytics/time-series.
- Sharding prematurely, paying distributed-systems complexity for load that a single primary handles.
- Choosing a shard/partition key that skews load or doesn't match queries, then being unable to change it.
- Sending all reads to the primary when replicas could absorb them, or reading from a replica where
  read-after-write consistency is required.
- No connection pooler, exhausting the database's connection limit under load.
- Treating the cache as a source of truth, so a cache flush loses or corrupts data.
- No failover or untested restore, turning a single-node failure into an extended outage.

## Production Tips

- Capacity-plan against real growth curves; know the point at which the primary needs partitioning
  or the read tier needs more replicas *before* you hit it. See [monitoring](21-monitoring.md).
- Document each store's consistency guarantee and RPO/RTO so on-call knows what "recovered" means.
- Keep cross-service data flows asynchronous where possible (events/outbox) so one store's slowdown
  doesn't cascade synchronously into others.

## AI Review Checklist

- Does each workload use a store that fits its dominant access pattern?
- Does each service own its own schema/database, integrating via API/events rather than shared tables?
- Is the consistency/availability trade-off chosen explicitly per workload?
- Are reads scaled with replicas/caching and writes/storage with partitioning before sharding?
- Is the shard/partition key chosen to spread load and match queries?
- Is a connection pooler in place, respecting the database's connection limit?
- Are failover and restore designed and tested, with defined RPO/RTO?

## Related

- `knowledge/databases/02-relational-vs-nosql.md`
- `knowledge/databases/14-replication.md`
- `knowledge/databases/15-sharding.md`
- `knowledge/databases/22-high-availability.md`
- `knowledge/databases/20-performance.md`
