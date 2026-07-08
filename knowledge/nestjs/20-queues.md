---
id: nestjs/20-queues
topic: nestjs
slug: queues
title: "NestJS Queues"
type: doc
order: 20
status: ready
tags: [nestjs, queues]
related: []
when_to_use: "Read before building or reviewing background jobs, queues, or asynchronous work moved outside the request lifecycle."
---
# NestJS Queues

## Purpose

This document defines the engineering standards for implementing asynchronous job processing using queues in NestJS applications.

The objective is to move long-running, resource-intensive, and retryable work outside the synchronous request lifecycle while maintaining reliability, observability, and scalability.

Queues execute background work.

They should not replace synchronous business logic unnecessarily.

---

## Core Principle

Respond quickly.

Process expensive work asynchronously.

---

## Queue Goals

Every queue system should provide:

- reliability;
- scalability;
- fault tolerance;
- retry support;
- observability;
- predictable execution.

Background processing should never compromise business consistency.

---

## Responsibilities

Queues are responsible for:

- asynchronous processing;
- workload distribution;
- retrying transient failures;
- scheduling delayed work;
- smoothing traffic spikes.

Queues should not:

- replace transactions;
- implement authorization;
- become permanent storage;
- execute request validation.

---

## Processing Flow

```
HTTP Request

↓

Business Service

↓

Persist Business State

↓

Enqueue Job

↓

Worker

↓

Execute Background Task

↓

Complete
```

Business state should be committed before background processing begins.

---

## Typical Use Cases

Queues are appropriate for:

- sending emails;
- generating reports;
- image processing;
- video transcoding;
- webhook delivery;
- data synchronization;
- notifications;
- scheduled jobs.

Avoid queues for operations that must complete before responding to the client.

---

## Queue Technologies

Common implementations include:

- BullMQ;
- RabbitMQ;
- Kafka;
- Amazon SQS;
- Google Pub/Sub;
- Azure Service Bus.

Application architecture should remain independent of the queue provider.

---

## Job Design

Every job should have:

- unique identifier;
- payload;
- creation timestamp;
- retry metadata;
- execution status.

Jobs should contain only the data required for execution.

---

## Idempotency

Workers should be idempotent.

Running the same job multiple times should not produce duplicate business effects.

Examples:

- sending duplicate invoices → avoid;
- charging the same payment twice → avoid;
- creating duplicate records → avoid.

Idempotency is essential for reliable distributed systems.

---

## Retry Strategy

Retry only transient failures.

Examples:

- temporary network errors;
- unavailable external APIs;
- temporary database connectivity issues.

Do not retry:

- validation failures;
- authorization failures;
- permanent business rule violations.

---

## Backoff Strategy

Prefer exponential backoff.

Example:

```
Retry 1 → 5 seconds

Retry 2 → 15 seconds

Retry 3 → 45 seconds

Retry 4 → 2 minutes
```

Avoid aggressive retry loops.

---

## Dead Letter Queue (DLQ)

Failed jobs exceeding retry limits should move to a Dead Letter Queue.

```
Job

↓

Retries Exhausted

↓

Dead Letter Queue

↓

Manual Investigation
```

Never silently discard failed jobs.

---

## Poison Messages

A poison message consistently fails processing.

Detect:

- repeated failures;
- malformed payloads;
- incompatible schemas.

Move poison messages to the DLQ.

---

## Delayed Jobs

Use delayed execution for:

- reminders;
- scheduled notifications;
- retry scheduling;
- deferred processing.

Scheduling should remain predictable.

---

## Job Priorities

Support priorities when required.

Example:

High:

- payment processing;
- security events.

Medium:

- notifications.

Low:

- analytics;
- report generation.

Priorities should reflect business value.

---

## Worker Design

Workers should:

- perform one responsibility;
- remain stateless;
- be horizontally scalable;
- produce structured logs.

Avoid large, multi-purpose workers.

---

## Concurrency

Configure worker concurrency carefully.

Consider:

- CPU usage;
- database capacity;
- external API limits;
- memory consumption.

Higher concurrency is not always better.

---

## Ordering

Do not assume global ordering.

If ordering matters:

- partition work;
- serialize processing for affected entities.

Explicitly document ordering guarantees.

---

## Queue Monitoring

Monitor:

- queue length;
- processing rate;
- retry count;
- failed jobs;
- worker utilization;
- processing latency.

Healthy queues require continuous monitoring.

---

## Graceful Shutdown

Workers should:

- stop accepting new jobs;
- finish active jobs;
- acknowledge completed work;
- exit cleanly.

Avoid terminating active processing abruptly.

---

## Observability

Every job should include:

- correlation ID;
- execution duration;
- retry count;
- worker identifier;
- failure reason.

Background execution should be traceable.

---

## Security

Validate all job payloads.

Never trust queued data simply because it originated internally.

Protect:

- API keys;
- tokens;
- personal data.

Sensitive information should be minimized.

---

## Performance

Optimize:

- batch processing;
- payload size;
- worker concurrency;
- retry frequency.

Avoid oversized job payloads.

---

## Testing

Verify:

- successful execution;
- retries;
- dead-letter handling;
- idempotency;
- delayed jobs;
- graceful shutdown.

Queue behavior should remain deterministic.

---

## AI Decision Matrix

Use queues for:

✓ Email delivery

✓ Image processing

✓ Report generation

✓ Notifications

✓ External integrations

Do **not** use queues for:

✗ Authentication

✗ Authorization

✗ Request validation

✗ Immediate user responses

---

## AI Execution Checklist

## Investigation

☐ Identify asynchronous work.

☐ Review retry requirements.

☐ Review failure scenarios.

☐ Review scalability needs.

---

## Planning

☐ Design idempotent jobs.

☐ Configure retries.

☐ Configure DLQ.

☐ Plan observability.

---

## Verification

☐ Jobs idempotent.

☐ Retries appropriate.

☐ DLQ configured.

☐ Correlation IDs propagated.

☐ Graceful shutdown supported.

☐ Queue independently testable.

---

## Common Mistakes

Avoid:

Performing synchronous work inside request handlers.

Retrying permanent failures.

Ignoring duplicate job execution.

Creating oversized job payloads.

Dropping failed jobs.

Ignoring monitoring.

Blocking workers with long-running synchronous code.

---

## Completion Criteria

Queue implementation is complete when:

- asynchronous work is isolated from request processing;
- jobs are idempotent;
- retries and backoff are configured;
- failed jobs are recoverable through a Dead Letter Queue;
- observability is implemented;
- workers can scale horizontally.

---

## Summary

Queues enable reliable asynchronous processing in NestJS applications.

By designing idempotent jobs, configuring intelligent retry strategies, using Dead Letter Queues, monitoring worker health, and treating background processing as a first-class architectural component, applications become more scalable, resilient, and production-ready.