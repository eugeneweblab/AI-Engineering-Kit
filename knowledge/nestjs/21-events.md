---
id: nestjs/21-events
topic: nestjs
slug: events
title: "Event-Driven Architecture"
type: doc
order: 21
status: ready
tags: [nestjs, events]
related: []
when_to_use: ""
---
# Event-Driven Architecture

## Purpose

This document defines the engineering standards for designing and implementing event-driven architectures in NestJS applications.

The objective is to decouple business components through events while maintaining consistency, observability, scalability, and reliability.

Events communicate facts.

They should never communicate intentions.

---

## Core Principle

An event represents something that has already happened.

Never publish events describing something that should happen.

Correct:

```
OrderCreated
```

Incorrect:

```
CreateOrder
```

Commands request work.

Events describe completed work.

---

## Event Goals

Every event-driven system should provide:

- loose coupling;
- scalability;
- extensibility;
- reliability;
- traceability;
- clear ownership.

---

## Event Lifecycle

```
Business Operation

↓

Transaction

↓

Commit

↓

Publish Event

↓

Event Bus

↓

Consumers

↓

Business Actions
```

Events should only be published after successful persistence.

---

## Event Categories

Separate events by purpose.

---

## Domain Events

Describe business facts.

Examples:

```
UserRegistered

OrderPaid

InvoiceGenerated

SubscriptionCancelled
```

Domain events remain inside the business domain.

---

## Integration Events

Communicate with external systems.

Examples:

```
CustomerCreated

PaymentSucceeded

ShipmentCreated
```

Integration events form public contracts.

They should be versioned carefully.

---

## Commands vs Events

Commands:

```
CreateInvoice

SendEmail

ReserveInventory
```

Commands expect execution.

Events:

```
InvoiceCreated

EmailSent

InventoryReserved
```

Events describe completed actions.

Never confuse the two.

---

## Event Bus

An Event Bus distributes events.

Responsibilities:

- routing;
- delivery;
- subscription management.

Business logic should remain independent of the Event Bus implementation.

---

## Synchronous Events

Execute immediately.

Suitable for:

- lightweight workflows;
- in-process communication.

Avoid long-running synchronous event handlers.

---

## Asynchronous Events

Execute independently.

Suitable for:

- notifications;
- analytics;
- integrations;
- reporting.

Asynchronous handlers improve scalability.

---

## Event Payload

Every event should include:

- event ID;
- event type;
- timestamp;
- correlation ID;
- aggregate identifier;
- version;
- payload.

Avoid oversized payloads.

---

## Event Versioning

Events are contracts.

Breaking changes require versioning.

Example:

```
OrderCreatedV1

OrderCreatedV2
```

Consumers should migrate gradually.

---

## Event Naming

Events should use past tense.

Correct:

```
PaymentProcessed

InvoiceSent

ProductPublished
```

Incorrect:

```
ProcessPayment

SendInvoice

PublishProduct
```

---

## Event Ordering

Do not assume global ordering.

If ordering matters:

- partition processing;
- document guarantees;
- design handlers accordingly.

---

## Idempotency

Every event handler should be idempotent.

Receiving the same event multiple times should not produce duplicate business effects.

Duplicate delivery is expected in distributed systems.

---

## Outbox Pattern

Reliable publication:

```
Transaction

↓

Database Update

↓

Outbox Record

↓

Commit

↓

Background Publisher

↓

Event Bus
```

Never publish events before commit.

---

## Event Consumers

Consumers should:

- perform one responsibility;
- remain independent;
- be retryable;
- be idempotent.

Avoid creating large event handlers.

---

## Event Chaining

Avoid deep event chains.

Poor example:

```
A

↓

B

↓

C

↓

D

↓

E
```

Long chains become difficult to understand and debug.

---

## Event Ownership

Every event should have:

- one producer;
- multiple consumers if necessary.

Ownership should remain explicit.

---

## Observability

Monitor:

- published events;
- failed handlers;
- processing latency;
- retry count;
- consumer lag.

Every event should be traceable.

---

## Correlation ID

Propagate the same correlation ID across:

```
HTTP Request

↓

Transaction

↓

Outbox

↓

Event

↓

Consumer

↓

Logs
```

Tracing should span the complete workflow.

---

## Security

Events should never expose:

- passwords;
- API keys;
- authentication tokens;
- internal implementation details.

Only publish information required by consumers.

---

## Performance

Review:

- event size;
- publication latency;
- consumer throughput;
- retry frequency.

Optimize based on measurements.

---

## Testing

Verify:

- event publication;
- idempotency;
- retry behavior;
- ordering assumptions;
- version compatibility.

Events should remain deterministic.

---

## AI Decision Matrix

Use events for:

✓ Notifications

✓ Integrations

✓ Analytics

✓ Background workflows

✓ Cross-module communication

Do **not** use events for:

✗ Immediate request validation

✗ Authentication

✗ Authorization

✗ Synchronous business decisions

---

## AI Execution Checklist

## Investigation

☐ Identify business facts.

☐ Review event consumers.

☐ Review delivery guarantees.

☐ Review consistency requirements.

---

## Planning

☐ Publish after commit.

☐ Design idempotent consumers.

☐ Include correlation IDs.

☐ Version public events.

---

## Verification

☐ Events represent completed facts.

☐ Payload minimal.

☐ Consumers independent.

☐ Outbox used when appropriate.

☐ Events observable.

☐ Event contracts documented.

---

## Common Mistakes

Avoid:

Publishing events before commit.

Treating commands as events.

Creating oversized payloads.

Ignoring duplicate delivery.

Building long event chains.

Embedding business workflows inside the Event Bus.

Breaking public event contracts.

---

## Completion Criteria

An event-driven implementation is complete when:

- events represent completed business facts;
- publication occurs after successful persistence;
- handlers are idempotent;
- event contracts are versioned;
- observability is implemented;
- consumers remain loosely coupled.

---

## Summary

Events allow independent parts of a system to communicate through completed business facts.

By publishing events only after successful transactions, designing idempotent consumers, versioning contracts, and maintaining strong observability, applications become more scalable, extensible, and resilient while preserving clear architectural boundaries.