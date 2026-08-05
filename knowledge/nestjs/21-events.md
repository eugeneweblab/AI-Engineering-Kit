---
id: nestjs/21-events
topic: nestjs
slug: events
title: "Event-Driven Architecture"
type: doc
order: 21
status: ready
tags: [nestjs, events, Injectable, OrderCreatedEvent, emit, CreateDateColumn, OrderPlacedEvent, InjectRepository]
related: [nestjs/20-queues, nestjs/22-cqrs, architecture/08-event-driven-architecture, backend/14-events]
when_to_use: "Read before designing or reviewing event-driven flows that decouple components through emitted domain events."
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

In NestJS the in-process bus is `@nestjs/event-emitter`. The lesson below is timing: emit **after** the transaction commits, never inside it. A handler that runs while the transaction is still open can read state that never becomes durable if the commit later fails.

```ts
// orders/orders.service.ts
import { Injectable } from '@nestjs/common';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { DataSource } from 'typeorm';
import { Order } from './entities/order.entity';
import { CreateOrderDto } from './dto/create-order.dto';
import { OrderCreatedEvent } from './events/order-created.event';

@Injectable()
export class OrdersService {
  constructor(
    private readonly dataSource: DataSource,
    private readonly events: EventEmitter2,
  ) {}

  // GOOD — persist inside a transaction, publish only after it commits.
  async placeOrder(dto: CreateOrderDto): Promise<Order> {
    const order = await this.dataSource.transaction(async (manager) => {
      const created = manager.create(Order, {
        productId: dto.productId,
        quantity: dto.quantity,
        status: 'pending',
      });
      return manager.save(created);
    });

    // The commit already succeeded, so the fact is now durable.
    this.events.emit(
      'order.created',
      new OrderCreatedEvent(order.id, order.productId, order.quantity),
    );
    return order;
  }

  // BAD — emitting inside the transaction. Consumers may react to an order
  // that never commits if the transaction rolls back after this line.
  async placeOrderWrong(dto: CreateOrderDto): Promise<Order> {
    return this.dataSource.transaction(async (manager) => {
      const created = await manager.save(
        manager.create(Order, { productId: dto.productId, quantity: dto.quantity }),
      );
      this.events.emit('order.created', new OrderCreatedEvent(created.id, created.productId, created.quantity));
      return created; // if a later step throws, the event was still delivered
    });
  }
}
```

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

Register the bus once at the root. Enabling `wildcard` lets consumers subscribe to patterns such as `order.*`, and `maxListeners` guards against silent listener leaks.

```ts
// app.module.ts
import { Module } from '@nestjs/common';
import { EventEmitterModule } from '@nestjs/event-emitter';

@Module({
  imports: [
    EventEmitterModule.forRoot({
      wildcard: true, // allows @OnEvent('order.*')
      delimiter: '.', // namespace separator used for wildcards
      maxListeners: 20,
      verboseMemoryLeak: true,
    }),
  ],
})
export class AppModule {}
```

`@nestjs/event-emitter` is **in-process only** — events live and die inside a single Node.js process. For cross-service or cross-instance delivery, publish to a broker (BullMQ, Kafka, RabbitMQ, SNS/SQS) instead; see the queues and distributed-systems docs. Keep business services depending on your own typed event classes so the transport can be swapped without touching domain code.

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

Model the event as an immutable class so every emit carries the same envelope. Prefer identifiers over full entities — send `aggregateId`, not the hydrated order with its relations.

```ts
// orders/events/order-created.event.ts
import { randomUUID } from 'node:crypto';

export class OrderCreatedEvent {
  readonly eventId: string = randomUUID();       // unique per emit — used for idempotency
  readonly type = 'order.created' as const;      // stable event type
  readonly version = 1;                          // bump on breaking payload changes
  readonly occurredAt: string = new Date().toISOString();

  constructor(
    readonly aggregateId: string, // the order id — not the whole entity
    readonly productId: string,
    readonly quantity: number,
    readonly correlationId: string = randomUUID(), // propagate from the inbound request
  ) {}
}
```

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

Guard the handler with a persisted record of processed `eventId`s. A unique constraint makes the guard safe even under concurrent redelivery. `@OnEvent('...', { async: true })` marks the listener asynchronous so a rejected promise surfaces instead of being swallowed.

```ts
// notifications/processed-event.entity.ts
import { Column, CreateDateColumn, Entity, PrimaryColumn } from 'typeorm';

@Entity('processed_events')
export class ProcessedEvent {
  @PrimaryColumn('uuid')
  eventId: string; // the event's eventId — a duplicate insert throws

  @CreateDateColumn()
  processedAt: Date;
}
```

```ts
// notifications/order-created.listener.ts
import { Injectable, Logger } from '@nestjs/common';
import { OnEvent } from '@nestjs/event-emitter';
import { InjectRepository } from '@nestjs/typeorm';
import { QueryFailedError, Repository } from 'typeorm';
import { ProcessedEvent } from './processed-event.entity';
import { OrderCreatedEvent } from '../orders/events/order-created.event';
import { MailerService } from './mailer.service';

@Injectable()
export class OrderCreatedListener {
  private readonly logger = new Logger(OrderCreatedListener.name);

  constructor(
    @InjectRepository(ProcessedEvent)
    private readonly processed: Repository<ProcessedEvent>,
    private readonly mailer: MailerService,
  ) {}

  @OnEvent('order.created', { async: true })
  async handle(event: OrderCreatedEvent): Promise<void> {
    try {
      // Claim the event first; the PK conflict rejects a duplicate.
      await this.processed.insert({ eventId: event.eventId });
    } catch (err) {
      if (err instanceof QueryFailedError) {
        this.logger.debug(`Skipping duplicate event ${event.eventId}`);
        return;
      }
      throw err;
    }

    // Runs at most once per eventId, even under redelivery.
    await this.mailer.sendOrderConfirmation(event.aggregateId);
  }
}
```

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

## Examples

**Good Example** — events describe what happened, and are published after commit

```ts
// A past-tense fact with a stable shape, carrying ids rather than entities.
export class OrderPlacedEvent {
  constructor(
    readonly orderId: string,
    readonly userId: string,
    readonly occurredAt: Date,
  ) {}
}

@Injectable()
export class OrdersService {
  constructor(
    private readonly dataSource: DataSource,
    private readonly events: EventEmitter2,
  ) {}

  async place(command: PlaceOrder): Promise<Order> {
    const order = await this.dataSource.transaction((manager) =>
      manager.save(OrderEntity, { userId: command.userId, sku: command.sku }),
    );

    // Published only after the transaction commits: a subscriber can never react
    // to an order that was rolled back.
    this.events.emit('order.placed', new OrderPlacedEvent(order.id, order.userId, new Date()));

    return order;
  }
}
```

```ts
@Injectable()
export class OrderNotificationsListener {
  private readonly logger = new Logger(OrderNotificationsListener.name);

  // Subscribers must not break the publisher. Failures are contained and logged;
  // the work itself is handed to a queue so it can be retried independently.
  @OnEvent('order.placed', { async: true, suppressErrors: true })
  async handle(event: OrderPlacedEvent): Promise<void> {
    try {
      await this.emails.add('order-confirmation', { orderId: event.orderId });
    } catch (err) {
      this.logger.error({ event: 'order.placed', orderId: event.orderId, err });
    }
  }
}
```

**Bad Example** — a command dressed as an event, emitted before the write lands

```ts
@Injectable()
export class OrdersService {
  async place(command: PlaceOrder) {
    // Named as an instruction to one specific subscriber. This is a method call
    // with extra indirection: the caller now depends on a listener existing,
    // but the compiler cannot check that it does.
    this.events.emit('sendOrderEmail', { email: command.email });

    // Emitted before the order is saved. If the insert fails, the customer has
    // already been emailed about an order that does not exist.
    return this.repo.save({ userId: command.userId, sku: command.sku });
  }
}

@Injectable()
export class OrderListener {
  @OnEvent('sendOrderEmail')
  async handle(payload: { email: string }) {
    // Synchronous by default: this runs inside the publisher's call stack, so a
    // slow SMTP server adds its latency to the HTTP response, and a throw here
    // propagates into the caller as if the order itself had failed.
    await this.mailer.sendMail({ to: payload.email, subject: 'Order placed' });
  }
}
```

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

## Related

- `knowledge/nestjs/20-queues.md`
- `knowledge/nestjs/22-cqrs.md`
- `knowledge/architecture/08-event-driven-architecture.md`
- `knowledge/backend/14-events.md`
