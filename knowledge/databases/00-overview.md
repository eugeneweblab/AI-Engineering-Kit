---
id: databases/00-overview
topic: databases
slug: overview
title: "Database Overview"
type: doc
order: 0
status: ready
tags: [databases, overview]
related: [databases/01-database-fundamentals, databases/02-relational-vs-nosql, databases/03-data-modeling, databases/09-transactions, databases/07-indexing]
when_to_use: "Read first to orient yourself in the databases topic and find the right doc for the decision in front of you."
---
# Database Overview

## Purpose

This document is the map for the **databases** topic. It orients an agent to what
each doc covers, the order to read them in, and which one answers the question in
front of you. It is a router, not a concept doc — read the linked file for depth.

The database is where correctness lives or dies. Application code can crash and
restart; corrupted or lost data is forever. Every doc in this topic exists to keep
one property true: **the data on disk is always a faithful, consistent record of
what actually happened.**

## Why It Matters

Most production incidents that make the news are database incidents: a bad
migration that dropped a column, a missing index that melted the CPU under load, a
partial write that left two tables disagreeing, a backup that had never actually
restored. These failures are expensive because data is shared, long-lived, and hard
to reverse. An agent that treats the database as "just storage" will ship exactly
these bugs. This topic makes the reasoning explicit so they can be prevented.

## How These Docs Fit Together

Read them roughly in order; each builds on the last.

- **Foundations** — start here to build vocabulary.
  - [Database Fundamentals](01-database-fundamentals.md): tables, keys, indexes,
    the query lifecycle, what a database engine actually guarantees.
  - [Relational vs NoSQL](02-relational-vs-nosql.md): how to choose a data store
    from the access pattern, not from hype.

- **Design the data** — decide what the data looks like before writing code.
  - [Data Modeling](03-data-modeling.md): turning a domain into entities,
    relationships, and keys.
  - [Normalization](04-normalization.md): eliminating redundancy so each fact
    lives in exactly one place.
  - [Denormalization](05-denormalization.md): deliberately trading redundancy for
    read speed — and paying the consistency cost.
  - [Schema Design](06-schema-design.md): types, constraints, and defaults that
    make illegal states unrepresentable.

- **Make it fast and correct at runtime.**
  - [Indexing](07-indexing.md) and [Query Optimization](08-query-optimization.md):
    make reads fast without breaking writes.
  - [Transactions](09-transactions.md), [Concurrency](10-concurrency.md),
    [Locking](11-locking.md), [ACID](12-acid.md),
    [Eventual Consistency](13-eventual-consistency.md): keep concurrent writers
    from corrupting shared state.

- **Scale and operate.**
  - [Replication](14-replication.md), [Sharding](15-sharding.md),
    [Partitioning](16-partitioning.md): grow beyond one machine.
  - [Migrations](17-migrations.md), [Backup and Recovery](18-backup-and-recovery.md),
    [Security](19-security.md), [Monitoring](21-monitoring.md),
    [High Availability](22-high-availability.md): run it in production.

- **Cross-cutting concerns.**
  - [Data Integrity](23-data-integrity.md), [Soft Delete](24-soft-delete.md),
    [Multi-Tenancy](25-multi-tenancy.md), [Auditing](26-auditing.md),
    [Testing](27-testing.md), [Best Practices](28-best-practices.md).

- **Reference lists.** [Common Antipatterns](100-common-antipatterns.md),
  [Production Checklist](98-production-checklist.md), and
  [AI Review Checklist](99-ai-review-checklist.md) are the fast lookups when
  reviewing a change.

## How To Use This Topic

- **Designing a new schema?** Read 03 → 04 → 05 → 06 in order before writing DDL.
- **A query is slow?** Go straight to 07 and 08.
- **Two writers corrupt data under load?** 09 → 10 → 11 → 12.
- **Reviewing a database change?** Run the [AI Review Checklist](99-ai-review-checklist.md)
  and scan [Common Antipatterns](100-common-antipatterns.md).

## Core Principles

- **The schema is a contract, enforced by the engine.** Push invariants
  (uniqueness, foreign keys, NOT NULL, CHECK) into the database. Application code
  forgets; constraints do not.
- **Model for the queries you will run**, not for an abstract "clean" diagram.
  Normalization and denormalization are both tools serving real access patterns.
- **Every write is a transaction.** Reason about what happens when it half-fails
  or runs concurrently with another write.
- **Migrations are code and must be reversible and tested.** The schema evolves;
  plan the change, don't improvise it in production.

## AI Review Checklist

- Did you pick the store from the actual access pattern (02), not by default?
- Is the model driven by the queries the app runs (03)?
- Are invariants enforced by database constraints, not just app code (06, 23)?
- Are multi-row writes wrapped in transactions with the right isolation (09)?
- Is every schema change a reversible, tested migration (17)?

## Related

- `knowledge/databases/01-database-fundamentals.md`
- `knowledge/databases/02-relational-vs-nosql.md`
- `knowledge/databases/03-data-modeling.md`
- `knowledge/databases/09-transactions.md`
- `knowledge/databases/07-indexing.md`
