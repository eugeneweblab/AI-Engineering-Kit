# NestJS Repositories

## Purpose

This document defines the engineering standards for implementing repositories in NestJS applications.

The objective is to isolate persistence concerns from business logic, making data access consistent, testable, and replaceable. Repositories should act as the application's gateway to persistent storage without exposing database implementation details to higher layers.

Repositories are responsible for persistence—not business decisions.

---

# Core Principle

Repositories persist data.

Services implement business logic.

Never mix these responsibilities.

---

# Repository Goals

Every repository should provide:

- encapsulated data access;
- predictable interfaces;
- reusable queries;
- database abstraction;
- efficient persistence;
- transaction compatibility.

Repositories should remain focused on storage concerns.

---

# Responsibilities

Repositories are responsible for:

- creating records;
- retrieving records;
- updating records;
- deleting records;
- executing queries;
- handling transactions delegated by services.

Repositories should not:

- implement business rules;
- send emails;
- call external APIs;
- perform authorization;
- coordinate workflows.

---

# Repository Position

Typical flow:

```
Controller

↓

Service

↓

Repository

↓

Database
```

Repositories should never be called directly by controllers.

---

# Repository Structure

Example:

```
users/

    users.repository.ts

    users.service.ts

    users.controller.ts
```

One repository should generally correspond to one aggregate or business entity.

---

# Repository Interface

Expose business-oriented methods.

Good examples:

```
findById()

findByEmail()

findActiveUsers()

create()

update()

delete()
```

Avoid exposing generic ORM methods directly.

Bad examples:

```
query()

execute()

raw()

runSql()
```

Repositories should express intent.

---

# Query Responsibility

Complex database queries belong inside repositories.

Examples:

- joins;
- filtering;
- pagination;
- sorting;
- aggregation.

Services should not construct SQL or ORM queries.

---

# ORM Isolation

Repositories should encapsulate ORM-specific code.

Whether using:

- Prisma;
- TypeORM;
- MikroORM;
- Sequelize;

the rest of the application should remain unaware of ORM implementation details.

Replacing the ORM should require minimal changes outside repositories.

---

# Transactions

Services coordinate transactions.

Repositories participate in transactions.

Repositories should not independently create transaction boundaries unless explicitly designed to do so.

---

# Pagination

Repositories should provide consistent pagination.

Support:

- offset pagination;
- cursor pagination;
- sorting;
- filtering.

Pagination behavior should remain predictable.

---

# Performance

Repositories should optimize:

- indexes;
- query count;
- eager loading;
- lazy loading;
- batching.

Avoid:

- N+1 queries;
- repeated lookups;
- unnecessary joins.

---

# Soft Deletes

If soft deletes are used:

- repositories should hide deleted records by default;
- explicit methods should retrieve archived data when required.

Behavior should remain consistent across the application.

---

# Domain Objects

Repositories should return:

- domain models;
- entities;
- typed objects.

Avoid returning raw database responses.

---

# Error Handling

Repositories should translate persistence failures into meaningful exceptions.

Avoid leaking ORM-specific errors into higher application layers.

---

# Caching

Repositories should not implement caching unless they are explicitly designed as cache-aware repositories.

Caching policies belong to dedicated infrastructure or service layers.

---

# External Storage

Repositories may represent:

- SQL databases;
- NoSQL databases;
- search engines;
- object storage;
- distributed storage.

The abstraction should remain consistent regardless of the backend.

---

# Security

Repositories should:

- use parameterized queries;
- prevent injection attacks;
- validate identifiers where appropriate;
- avoid exposing sensitive fields unintentionally.

Security begins at the persistence layer.

---

# Testing

Repositories should be tested with:

- integration tests;
- database fixtures;
- realistic queries.

Mock repositories when testing services.

---

# AI Execution Checklist

## Investigation

☐ Identify persistence requirements.

☐ Review entity relationships.

☐ Review transaction requirements.

☐ Review performance expectations.

---

## Planning

☐ Encapsulate ORM usage.

☐ Design meaningful methods.

☐ Optimize common queries.

☐ Support transactions.

---

## Verification

☐ Business logic absent.

☐ ORM isolated.

☐ Queries optimized.

☐ Pagination consistent.

☐ Repository independently testable.

☐ Security reviewed.

---

# Common Mistakes

Avoid:

Writing business logic inside repositories.

Returning ORM-specific objects everywhere.

Creating SQL inside services.

Duplicating queries across modules.

Ignoring transaction boundaries.

Using repositories as generic utility classes.

Performing authorization inside repositories.

---

# Completion Criteria

A repository implementation is complete when:

- persistence concerns are fully encapsulated;
- business logic remains outside the repository;
- ORM implementation details are isolated;
- queries are efficient and reusable;
- transaction support is compatible with service workflows;
- repositories can be independently tested.

---

# Summary

Repositories form the persistence boundary of a NestJS application.

By isolating database access, exposing meaningful domain-oriented methods, optimizing queries, and keeping business logic within services, repositories remain reusable, maintainable, and independent from the underlying database technology.