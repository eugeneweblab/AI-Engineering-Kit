# NestJS Transactions

## Purpose

This document defines the engineering standards for implementing transactions in NestJS applications.

The objective is to ensure that business operations modifying multiple pieces of state remain atomic, consistent, reliable, and recoverable.

Transactions protect business consistency.

They should never become the default solution for every operation.

---

# Core Principle

A transaction should represent one business operation.

Not one HTTP request.

---

# Transaction Goals

Every transaction should provide:

- atomicity;
- consistency;
- isolation;
- durability;
- predictable rollback behavior;
- minimal execution time.

Transactions should be as small as possible.

---

# Responsibilities

Transactions are responsible for:

- grouping related persistence operations;
- preserving data consistency;
- coordinating commits;
- rolling back failures.

Transactions should not:

- perform long-running work;
- wait for external services;
- send emails;
- publish messages directly;
- perform expensive calculations.

---

# Transaction Lifecycle

```
Begin Transaction

↓

Business Operation

↓

Repository Operations

↓

Commit

↓

Success
```

If any operation fails:

```
Begin Transaction

↓

Business Operation

↓

Failure

↓

Rollback
```

---

# ACID Principles

Every engineer should understand ACID.

## Atomicity

Everything succeeds.

Or nothing succeeds.

---

## Consistency

Every committed transaction leaves the database in a valid state.

---

## Isolation

Concurrent transactions should not corrupt each other.

---

## Durability

Committed data survives failures.

---

# Transaction Boundaries

Transactions belong in the service layer.

Correct:

```
Controller

↓

Service

↓

Transaction

↓

Repositories
```

Avoid starting transactions inside controllers.

Avoid repositories creating independent transactions automatically.

---

# Unit of Work

Treat one transaction as one business unit.

Example:

```
Create Order

↓

Reserve Inventory

↓

Create Payment

↓

Commit
```

The entire workflow succeeds or fails together.

---

# Idempotency

Retryable operations should be idempotent.

Examples:

- payment callbacks;
- webhook processing;
- retry queues.

Running the same transaction twice should not create duplicate business effects.

---

# External Services

Never keep a database transaction open while calling:

- payment providers;
- email services;
- cloud storage;
- REST APIs;
- message brokers.

External systems are not part of the database transaction.

---

# Outbox Pattern

When both database changes and event publication are required:

```
Transaction

↓

Update Database

↓

Write Outbox Record

↓

Commit

↓

Background Worker

↓

Publish Event
```

This guarantees reliable event delivery.

---

# Saga Pattern

For distributed workflows:

```
Reserve Inventory

↓

Charge Payment

↓

Create Shipment

↓

Notify Customer
```

Failures trigger compensation instead of rollback.

Distributed systems cannot rely on a single database transaction.

---

# Compensation

Compensation should reverse completed business actions.

Example:

```
Payment Success

↓

Shipment Failure

↓

Refund Payment
```

Compensation is not the same as rollback.

---

# Isolation Levels

Choose the weakest isolation level that satisfies business consistency.

Higher isolation increases contention.

Review:

- dirty reads;
- non-repeatable reads;
- phantom reads.

---

# Deadlocks

Deadlocks may occur when concurrent transactions lock resources differently.

Reduce deadlocks by:

- consistent locking order;
- short transactions;
- avoiding unnecessary locks.

Applications should retry retryable deadlocks when appropriate.

---

# Retry Strategy

Retry only transient failures.

Examples:

- deadlocks;
- temporary connection failures;
- serialization conflicts.

Do not retry business validation failures.

---

# Long Transactions

Avoid transactions containing:

- file uploads;
- network calls;
- user interaction;
- expensive calculations.

Transactions should finish quickly.

---

# Nested Transactions

Avoid unnecessary nested transactions.

Prefer one clearly defined transaction boundary.

---

# Optimistic vs Pessimistic Locking

Optimistic locking:

Suitable when conflicts are rare.

Pessimistic locking:

Suitable when conflicts are expensive.

Choose according to business requirements.

---

# Event Consistency

Business events should represent committed state.

Never publish events before a successful commit.

---

# Error Handling

Rollback should occur automatically on unrecoverable failures.

Business exceptions should leave the database unchanged.

---

# Observability

Monitor:

- transaction duration;
- rollback frequency;
- deadlocks;
- lock contention;
- retry count.

Long-running transactions should be investigated.

---

# Performance

Review:

- transaction duration;
- locked rows;
- query count;
- blocking operations.

Transactions should remain lightweight.

---

# Security

Transactions do not replace authorization.

Validate permissions before beginning transactional work whenever practical.

---

# Testing

Verify:

- successful commit;
- rollback behavior;
- concurrent execution;
- retry logic;
- idempotency;
- compensation workflows.

Transaction behavior should remain deterministic.

---

# AI Decision Matrix

Use transactions for:

✓ Financial operations

✓ Inventory updates

✓ Multi-table consistency

✓ Critical business operations

Do **not** use transactions for:

✗ Sending emails

✗ Calling external APIs

✗ Long-running workflows

✗ Report generation

---

# AI Execution Checklist

## Investigation

☐ Identify business operation.

☐ Review consistency requirements.

☐ Review concurrency.

☐ Review external dependencies.

---

## Planning

☐ Keep transaction short.

☐ Define rollback behavior.

☐ Consider idempotency.

☐ Use Outbox when publishing events.

---

## Verification

☐ Transaction boundary correct.

☐ No external API calls inside transaction.

☐ Rollback verified.

☐ Retry strategy appropriate.

☐ Deadlock risk reviewed.

☐ Transaction independently testable.

---

# Common Mistakes

Avoid:

Opening transactions inside controllers.

Keeping transactions open during HTTP requests.

Sending emails before commit.

Publishing events before commit.

Creating long-running transactions.

Ignoring idempotency.

Retrying business validation errors.

---

# Completion Criteria

A transactional workflow is complete when:

- business consistency is preserved;
- transaction boundaries are well defined;
- transactions remain short;
- rollback behavior is predictable;
- external systems are coordinated safely;
- transaction behavior is fully tested.

---

# Summary

Transactions preserve business consistency across multiple persistence operations.

By keeping transactions short, defining clear boundaries, separating external integrations through patterns such as Outbox and Saga, and designing for idempotency and concurrency, NestJS applications remain reliable under real-world production workloads.