---
id: databases/02-relational-vs-nosql
topic: databases
slug: relational-vs-nosql
title: "Relational vs NoSQL"
type: doc
order: 2
status: ready
tags: [databases, relational-vs-nosql, JSONB, PostgreSQL]
related: [databases/01-database-fundamentals, databases/03-data-modeling, databases/12-acid, databases/13-eventual-consistency, databases/15-sharding]
when_to_use: "Read before choosing a data store for a new service or feature, so the choice follows the access pattern instead of habit or hype."
---
# Relational vs NoSQL

## Purpose

This document is a decision guide for choosing between a relational (SQL) database
and a NoSQL store — and among the NoSQL families. It exists so an agent picks a data
store from the **access pattern and consistency needs**, not from familiarity or
marketing. The wrong choice here is one of the most expensive mistakes to reverse,
because the data model, not just the vendor, becomes hard to change.

"NoSQL" is not one thing. It covers document stores, key-value stores, wide-column
stores, and graph databases — each with different trade-offs. Reason about the
specific family, never about "SQL vs NoSQL" as a slogan.

## Why It Matters

A store's model shapes every query you can cheaply run and every guarantee you get.
Relational engines give you joins, multi-row transactions, and enforced constraints;
you pay with a rigid schema and harder horizontal scaling. NoSQL stores give you
flexible schemas and easy horizontal scale; you pay by pushing joins, uniqueness,
and cross-document consistency into application code — where they are slower and
easier to get wrong. Choosing the model that fights your access pattern means every
feature afterward is harder than it needed to be.

## Core Principles

- **Default to a relational database.** For most applications, PostgreSQL (or
  MySQL) is the correct choice: strong consistency, joins, transactions, mature
  tooling. Choose NoSQL only when a concrete requirement demands it.
- **Choose from the access pattern.** List the queries and writes the app must
  serve, then pick the store that serves them cheaply — not the reverse.
- **Consistency needs decide the model.** If invariants must hold across records at
  all times (balances, inventory, bookings), you need transactions and strong
  consistency. If stale reads are acceptable, [eventual consistency](13-eventual-consistency.md)
  buys scale.
- **NoSQL trades a rigid schema for a rigid access path.** Document and wide-column
  stores are fast only along the keys you designed for. Ad-hoc queries across other
  fields are slow or impossible.
- **"Schemaless" means the schema moves into your code.** The structure still
  exists; the engine just stops enforcing it. You now enforce it, on every read.

## Best Practices

- Start relational. Reach for NoSQL when you hit a specific limit a relational store
  handles poorly: massive write throughput, huge horizontal scale, deeply nested or
  highly variable documents, or graph traversal.
- Match the NoSQL family to the shape of the data:
  - **Document** (MongoDB, DynamoDB): self-contained aggregates read/written as a unit.
  - **Key-value** (Redis, DynamoDB): caches, sessions, lookups by a single key.
  - **Wide-column** (Cassandra, ScyllaDB): high-volume time-series and event data,
    queried by a known partition key.
  - **Graph** (Neo4j): relationships are the primary query (social graph, fraud rings).
- Model a document store around the queries: embed data read together, reference
  data queried independently.
- Remember modern relational engines have `JSONB` columns — you can store flexible
  documents inside PostgreSQL and keep transactions and joins for the rest.
- Do not run a distributed NoSQL cluster to escape schema migrations; migrations are
  a solved problem ([Migrations](17-migrations.md)) and far cheaper than losing joins.

## Examples

**Good Example** — store chosen from the pattern, with reasoning

```text
Feature: orders with line items, inventory decrement, and financial reporting.
Access pattern:
  - Write: create order + decrement stock + charge — must be all-or-nothing.
  - Read: joins across orders, customers, products for reports.
Invariant: stock never goes negative; order total must match line items.

Decision: PostgreSQL.
Why: multi-row transactions guarantee the all-or-nothing write; foreign keys and
CHECK constraints enforce the invariants; joins serve the reports directly.
Cost accepted: schema changes require migrations; scaling past one node needs
read replicas or partitioning later.
```

**Bad Example** — store chosen by habit, fighting the pattern

```text
Same feature, built on a document store "because it scales."

Result:
  - No multi-document transaction across order + inventory + payment, so a crash
    mid-write leaves stock decremented for an order that was never charged.
  - Uniqueness of SKU and non-negative stock enforced in app code → races corrupt it.
  - Reporting joins reimplemented as N+1 application-side lookups → slow and fragile.
The store scales writes the app never had a throughput problem with, and loses the
consistency the app actually needed.
```

## Common Mistakes

- Choosing NoSQL for scale the application will never reach, and losing transactions
  and joins it needs today.
- Treating "schemaless" as "no data model," then discovering five inconsistent
  shapes of the same document in production.
- Assuming a document store gives cross-document transactions everywhere; support
  and scope vary sharply by engine — verify, don't assume.
- Using a key-value store for data you later need to query by a second attribute.
- Ignoring `JSONB` in a relational database and adopting a whole new store just for
  a few flexible fields.
- Running multiple specialized stores for a small app, multiplying operational cost.

## Production Tips

- Whichever you pick, understand its consistency model precisely: read-your-writes,
  quorum reads, replica lag. Bugs hide in the gap between assumed and actual guarantees.
- If you adopt NoSQL, write and enforce a schema in code (validation on write) so
  documents stay uniform even though the engine will not require it.
- Polyglot persistence (relational as source of truth, key-value cache, search
  index) is valid — but each store you add is another thing to back up, monitor,
  and keep consistent.

## AI Review Checklist

- Was the store chosen from the actual read/write pattern and consistency needs?
- If NoSQL, does a concrete requirement justify giving up joins and transactions?
- Are cross-record invariants enforceable in the chosen store, or pushed to app code?
- For a document store, is it modeled around the queries (embed vs reference)?
- Would `JSONB` in a relational database have met the flexibility need instead?
- Is the store's consistency model understood and matched to the requirement?

## Related

- `knowledge/databases/01-database-fundamentals.md`
- `knowledge/databases/03-data-modeling.md`
- `knowledge/databases/12-acid.md`
- `knowledge/databases/13-eventual-consistency.md`
- `knowledge/databases/15-sharding.md`
