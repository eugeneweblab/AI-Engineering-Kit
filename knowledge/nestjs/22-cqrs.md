# CQRS (Command Query Responsibility Segregation)

## Purpose

This document defines the engineering standards for implementing CQRS in NestJS applications.

The objective is to separate write operations from read operations when doing so improves scalability, maintainability, security, or business complexity.

CQRS is an architectural pattern.

It is not a requirement for every application.

---

# Core Principle

Commands change state.

Queries return state.

Never confuse the two.

---

# CQRS Goals

A CQRS architecture should provide:

- clear separation of responsibilities;
- simplified business logic;
- scalable read models;
- independent optimization of reads and writes;
- better support for complex domains.

CQRS introduces complexity.

Use it only when its benefits outweigh its costs.

---

# Basic Architecture

```
                Request

                   │

        ┌──────────┴──────────┐

        │                     │

     Command              Query

        │                     │

Command Handler       Query Handler

        │                     │

     Domain              Read Model

        │                     │

   Repository          Read Database

        │

    Database
```

Commands and queries should remain independent.

---

# Commands

Commands represent business intentions.

Examples:

```
CreateOrder

CancelOrder

ApproveInvoice

ReserveInventory
```

Commands:

- modify state;
- produce side effects;
- may publish events;
- return minimal information.

Avoid returning full entities from commands.

---

# Queries

Queries retrieve information.

Examples:

```
GetUserProfile

ListOrders

SearchProducts

GetDashboardStatistics
```

Queries:

- never modify state;
- optimize for reading;
- may use specialized projections.

Queries should remain side-effect free.

---

# Command Handler

Responsibilities:

- validate business rules;
- execute domain logic;
- coordinate repositories;
- publish events after successful persistence.

Command handlers should remain focused on one use case.

---

# Query Handler

Responsibilities:

- retrieve data efficiently;
- compose read models;
- optimize performance;
- avoid unnecessary domain logic.

Query handlers should not modify application state.

---

# Read Model

The read model exists to optimize queries.

Examples:

- denormalized tables;
- materialized views;
- Elasticsearch indexes;
- Redis caches.

Read models are optimized for consumers—not persistence.

---

# Write Model

The write model preserves business consistency.

Responsibilities:

- enforce invariants;
- execute business rules;
- coordinate transactions.

Write models prioritize correctness over query performance.

---

# Eventual Consistency

Read models may lag behind writes.

Example:

```
Command

↓

Database

↓

Event

↓

Projection

↓

Read Model
```

Applications should tolerate temporary inconsistency where appropriate.

---

# Domain Events

Command handlers may publish domain events.

Example:

```
CreateOrder

↓

OrderCreated

↓

Update Read Model

↓

Notify Customer
```

Events should represent completed business facts.

---

# Outbox Pattern

When publishing events:

```
Transaction

↓

Persist Changes

↓

Write Outbox Record

↓

Commit

↓

Publish Event
```

Never publish events before commit.

---

# Event Sourcing

CQRS does not require Event Sourcing.

Event Sourcing stores events as the source of truth.

CQRS separates reads from writes.

These patterns may be combined but remain independent.

---

# Aggregates

Aggregates protect business invariants.

Examples:

```
Order

Invoice

Subscription

Account
```

Aggregates should expose business behaviors—not database operations.

---

# Validation

Separate validation into:

Transport validation:

- DTOs;
- Pipes.

Business validation:

- Command handlers;
- Domain services;
- Aggregates.

---

# Transactions

Commands may use transactions.

Queries should avoid transactions unless explicitly required.

Keep transaction boundaries inside the write model.

---

# Read Optimization

Optimize queries independently.

Examples:

- custom SQL;
- projections;
- caching;
- search indexes.

Read optimization should not affect business rules.

---

# Scaling

CQRS allows independent scaling.

```
Write Service

↓

Primary Database

──────────────

Read Service

↓

Read Replicas

↓

Search Index

↓

Cache
```

Read-heavy systems benefit significantly.

---

# Monitoring

Measure:

- command latency;
- query latency;
- projection delay;
- event processing;
- consistency lag.

CQRS should remain observable.

---

# Security

Authorization rules apply equally to:

- commands;
- queries.

Read operations may expose sensitive information.

Protect both sides independently.

---

# Testing

Verify:

- command execution;
- query correctness;
- event publication;
- projections;
- eventual consistency;
- aggregate invariants.

Commands and queries should be tested independently.

---

# When to Use CQRS

Suitable for:

- complex business domains;
- high read/write asymmetry;
- event-driven systems;
- distributed architectures;
- systems requiring independent scaling.

---

# When NOT to Use CQRS

Avoid CQRS for:

- simple CRUD applications;
- prototypes;
- internal administration panels;
- small services with limited complexity.

Do not introduce CQRS without measurable benefit.

---

# AI Decision Matrix

Use CQRS when:

✓ Business rules are complex

✓ Reads and writes differ significantly

✓ Independent scaling is required

✓ Read models differ from write models

Do **not** use CQRS when:

✗ CRUD is sufficient

✗ Domain complexity is low

✗ Team experience is limited

✗ Simplicity is the primary goal

---

# AI Execution Checklist

## Investigation

☐ Review business complexity.

☐ Review read/write ratio.

☐ Review scalability requirements.

☐ Review consistency requirements.

---

## Planning

☐ Separate commands and queries.

☐ Design aggregates.

☐ Design read models.

☐ Plan event publication.

---

## Verification

☐ Commands modify state only.

☐ Queries remain side-effect free.

☐ Events published after commit.

☐ Read models optimized.

☐ Aggregate invariants protected.

☐ CQRS justified by business needs.

---

# Common Mistakes

Avoid:

Using CQRS for every application.

Returning entities from commands.

Executing writes inside query handlers.

Publishing events before commit.

Ignoring eventual consistency.

Duplicating business rules in read models.

Creating unnecessary complexity.

---

# Completion Criteria

A CQRS implementation is complete when:

- commands and queries are clearly separated;
- business rules remain inside the write model;
- read models are optimized independently;
- event publication is reliable;
- eventual consistency is understood and acceptable;
- CQRS is justified by measurable architectural needs.

---

# Summary

CQRS separates state modification from data retrieval to improve scalability, maintainability, and architectural clarity.

By introducing CQRS only where business complexity justifies it, keeping commands and queries independent, protecting aggregate invariants, and optimizing read models separately, NestJS applications remain both flexible and maintainable without unnecessary complexity.