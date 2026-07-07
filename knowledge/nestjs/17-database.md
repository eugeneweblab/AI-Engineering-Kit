---
id: nestjs/17-database
topic: nestjs
slug: database
title: "NestJS Database"
type: doc
order: 17
status: ready
tags: [nestjs, database]
related: []
when_to_use: ""
---
# NestJS Database

## Purpose

This document defines the engineering standards for integrating databases into NestJS applications.

The objective is to build reliable, scalable, and maintainable persistence layers while keeping business logic independent from database implementation details.

The database stores application state.

Business logic remains inside services.

---

## Core Principle

Treat the database as infrastructure.

Application architecture should not depend on a specific ORM or database engine.

---

## Database Goals

Every persistence layer should provide:

- data consistency;
- predictable performance;
- scalability;
- maintainability;
- observability;
- portability where practical.

Database code should remain isolated behind repositories.

---

## Architecture

Typical flow:

```
Controller

↓

Service

↓

Repository

↓

ORM / Query Builder

↓

Database
```

Business logic should never bypass repositories.

---

## Database Technologies

NestJS supports many persistence technologies.

Common choices include:

- PostgreSQL
- MySQL
- MariaDB
- SQL Server
- SQLite
- MongoDB
- Redis (for caching)
- Elasticsearch / OpenSearch (for search)

Technology selection should follow business requirements rather than framework preference.

---

## ORM Selection

Common options:

### Prisma

Strengths:

- excellent TypeScript support;
- generated client;
- simple migrations;
- strong developer experience.

Best suited for:

- modern TypeScript projects;
- greenfield development;
- API-first applications.

---

### TypeORM

Strengths:

- mature ecosystem;
- decorators;
- Active Record and Data Mapper support;
- extensive enterprise adoption.

Best suited for:

- legacy systems;
- applications already using TypeORM;
- teams requiring advanced ORM customization.

---

### Drizzle ORM

Strengths:

- SQL-first philosophy;
- lightweight;
- excellent type safety;
- predictable generated SQL.

Best suited for:

- teams preferring explicit SQL;
- performance-sensitive applications.

---

Choose an ORM based on project requirements rather than popularity.

---

## Repository Pattern

Repositories isolate persistence.

Services should communicate only with repositories.

Repositories should never contain business workflows.

---

## Migrations

All schema changes should be versioned.

Migration rules:

- deterministic;
- reversible when possible;
- reviewed;
- committed to source control.

Never modify production schemas manually.

---

## Transactions

Use transactions only when multiple operations must succeed or fail together.

Transactions should remain:

- short;
- atomic;
- isolated;
- consistent.

Avoid long-running transactions.

---

## Locking

Choose an appropriate locking strategy.

Optimistic locking:

Suitable for:

- low contention;
- collaborative editing.

Pessimistic locking:

Suitable for:

- financial systems;
- inventory management;
- high-contention resources.

Select the least restrictive strategy that guarantees consistency.

---

## Indexing

Indexes should support:

- primary lookups;
- foreign keys;
- filtering;
- sorting;
- unique constraints.

Avoid unnecessary indexes.

Every index increases write cost.

---

## Query Design

Queries should be:

- explicit;
- efficient;
- parameterized;
- explainable.

Avoid unnecessary complexity.

---

## N+1 Queries

Prevent repeated database access.

Bad:

```
Load users

↓

Load orders for each user

↓

1001 queries
```

Better:

```
Load users

↓

Load orders using JOIN or batching

↓

2 queries
```

Always review generated SQL.

---

## Pagination

Never return unbounded collections.

Support:

- offset pagination;
- cursor pagination;
- sorting;
- filtering.

Large datasets should always be paginated.

---

## Bulk Operations

Prefer bulk operations when processing many records.

Examples:

- insertMany;
- updateMany;
- deleteMany.

Avoid unnecessary loops performing one query per record.

---

## Soft Deletes

Soft deletes should:

- preserve audit history;
- hide deleted records by default;
- support restoration when required.

Use only when business requirements justify additional complexity.

---

## Read and Write Separation

Large applications may separate:

```
Writes

↓

Primary Database

↓

Replication

↓

Read Replicas

↓

Reads
```

Services should remain unaware of replication topology.

---

## Connection Pooling

Configure connection pools appropriately.

Avoid:

- excessive connections;
- connection leaks;
- unnecessary reconnects.

Connection management should remain transparent to business logic.

---

## Database Constraints

Prefer enforcing integrity inside the database.

Examples:

- primary keys;
- foreign keys;
- unique constraints;
- check constraints.

Database constraints complement—not replace—business validation.

---

## Raw SQL

Use raw SQL only when necessary.

Examples:

- advanced reporting;
- complex analytics;
- database-specific optimizations.

Encapsulate raw SQL inside repositories.

Never concatenate user input into SQL.

---

## Observability

Monitor:

- slow queries;
- transaction duration;
- connection usage;
- deadlocks;
- lock contention;
- query frequency.

Database behavior should be measurable.

---

## Performance

Review:

- indexes;
- execution plans;
- query count;
- data transfer volume;
- unnecessary eager loading.

Optimize based on measurements—not assumptions.

---

## Security

Always:

- use parameterized queries;
- enforce least privilege for database users;
- encrypt sensitive data when appropriate;
- avoid exposing internal identifiers unnecessarily.

Never trust user input.

---

## Testing

Test:

- migrations;
- repository behavior;
- transactions;
- concurrency scenarios;
- rollback behavior.

Use realistic datasets whenever practical.

---

## AI Decision Matrix

Use the database for:

✓ Persistent application state

✓ Transactions

✓ Relationships

✓ Querying

✓ Constraints

Do **not** use the database for:

✗ Application configuration

✗ Temporary request state

✗ In-memory caching

✗ Business workflows

---

## AI Execution Checklist

## Investigation

☐ Review data model.

☐ Review consistency requirements.

☐ Review expected workload.

☐ Review scalability requirements.

---

## Planning

☐ Design repositories.

☐ Optimize indexes.

☐ Define transactions.

☐ Plan migrations.

---

## Verification

☐ No N+1 queries.

☐ Queries parameterized.

☐ Pagination implemented.

☐ Transactions minimal.

☐ Constraints enforced.

☐ Repository independently testable.

---

## Common Mistakes

Avoid:

Putting business logic inside repositories.

Skipping indexes.

Returning unlimited collections.

Ignoring transaction boundaries.

Using one query per record.

Writing raw SQL everywhere.

Reading directly from ORM inside controllers.

Keeping long-running transactions open.

---

## Completion Criteria

Database integration is complete when:

- persistence is isolated behind repositories;
- schema changes are versioned;
- transactions are minimal and reliable;
- queries are optimized;
- observability is in place;
- performance and security have been reviewed.

---

## Summary

The database is one of the most critical infrastructure components of a NestJS application.

By isolating persistence behind repositories, designing efficient queries, enforcing constraints, minimizing transactions, and continuously monitoring performance, applications remain scalable, reliable, and maintainable as they grow.