---
id: postgresql/readme
topic: postgresql
slug: readme
title: "PostgreSQL Engineering Standards"
type: index
order: -1
status: ready
tags: [postgresql, readme, jsonb, uuid, bigint, timestamptz, numeric, pg_stat_statements]
related: []
when_to_use: "Read first when starting any PostgreSQL work, to see how this section's docs fit together."
---
# PostgreSQL Engineering Standards

## Purpose

This section defines the engineering standards, mental models, and best practices for
designing schemas and operating PostgreSQL in production. PostgreSQL is a relational
database with strong ACID guarantees, MVCC concurrency, a mature cost-based query planner,
and first-class extensibility. It rewards using its native features — real data types,
constraints, indexes, extensions — over pushing that logic into application code.

The objective is to treat the database as the highest-leverage correctness layer in the
system. The database outlives every service in front of it: application code is rewritten
every few years, but the schema and the data survive. A query mistake is a slow page; a
schema, index, or transaction-boundary mistake is data corruption, lock storms, or a
rewrite migration under load. From installation and modeling through concurrency, scaling,
and operations, these docs make schema and query design decisions carry the weight of an
API contract.

These standards are written for both human engineers and AI coding assistants, so that
either can design, review, and run PostgreSQL to the same bar.

---

## Scope

This documentation covers:

- Installation and configuration
- Data types, JSONB, and arrays
- Indexes, the query planner, performance, and tuning
- Transactions, locking, VACUUM, and ANALYZE
- Partitioning, replication, high availability, and backups
- Extensions and full-text search
- Monitoring, security, and roles and permissions
- Migrations, testing, and debugging
- Architecture, tooling, and engineering principles

---

## Learning Path

Study the documents in the following order.

### Set Up
- [00. Overview](00-overview.md)
- [01. Installation](01-installation.md)
- [02. Configuration](02-configuration.md)

### Model
- [03. Data Types](03-data-types.md)
- [08. JSONB](08-jsonb.md)
- [09. Arrays](09-arrays.md)
- [10. Full-Text Search](10-full-text-search.md)
- [15. Extensions](15-extensions.md)

### Make It Fast
- [04. Indexes](04-indexes.md)
- [05. Query Planner](05-query-planner.md)
- [16. Performance](16-performance.md)
- [27. Tuning](27-tuning.md)

### Concurrency & Correctness
- [06. Transactions](06-transactions.md)
- [07. Locking](07-locking.md)
- [20. VACUUM](20-vacuum.md)
- [21. ANALYZE](21-analyze.md)

### Scale & Availability
- [11. Partitioning](11-partitioning.md)
- [12. Replication](12-replication.md)
- [13. High Availability](13-high-availability.md)
- [14. Backups](14-backups.md)

### Operate
- [17. Monitoring](17-monitoring.md)
- [18. Security](18-security.md)
- [19. Roles and Permissions](19-roles-and-permissions.md)
- [22. Migrations](22-migrations.md)
- [23. Testing](23-testing.md)
- [24. Debugging](24-debugging.md)

### Ship Well
- [25. Best Practices](25-best-practices.md)
- [26. Production](26-production.md)
- [28. Architecture](28-architecture.md)
- [29. Tooling](29-tooling.md)
- [30. Engineering Principles](30-engineering-principles.md)

### Verification
- [98. Production Checklist](98-production-checklist.md)
- [99. AI Review Checklist](99-ai-review-checklist.md)
- [100. Common Anti-Patterns](100-common-antipatterns.md)

---

## Engineering Principles

Every PostgreSQL change should satisfy the following principles:

- Let the database enforce truth with `NOT NULL`, `CHECK`, `UNIQUE`, and foreign-key constraints.
- Model with real types (`timestamptz`, `numeric`, `uuid`, `jsonb`) instead of storing everything as `text`.
- Give every table a primary key; prefer `bigint` identity or UUID v7 keys.
- Measure, do not guess — `EXPLAIN (ANALYZE, BUFFERS)` is the source of truth for query behavior.
- Treat transactions as correctness boundaries and keep them short to avoid lock and MVCC bloat.
- Add indexes deliberately; each one speeds reads and slows writes, so verify usage and drop dead ones.
- Deliver every schema change as a versioned, reversible migration, never applied by hand.
- Pin a specific major version and read its release notes before upgrading.
- Enable `pg_stat_statements` early so query telemetry exists before you need it.
- Scope each change to the right concern and link the sibling doc that governs it.

---

## Intended Audience

These standards are intended for:

- Backend Engineers
- Database Engineers and DBAs
- Platform and DevOps Engineers
- Tech Leads
- Software Architects
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps PostgreSQL schemas correct by construction and queries
verifiably fast, protecting the data that outlives every service around it.
