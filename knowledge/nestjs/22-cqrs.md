---
id: nestjs/22-cqrs
topic: nestjs
slug: cqrs
title: "CQRS (Command Query Responsibility Segregation)"
type: doc
order: 22
status: ready
tags: [nestjs, cqrs, InjectRepository, OrderCreatedEvent, constructor, execute, PlaceOrderCommand, OrderEntity]
related: [nestjs/21-events, nestjs/01-architecture, architecture/07-cqrs, architecture/06-domain-driven-design]
when_to_use: "Read before deciding on or reviewing a CQRS design that separates read and write operations."
---
# CQRS (Command Query Responsibility Segregation)

## Purpose

This document defines the engineering standards for implementing CQRS in NestJS applications.

The objective is to separate write operations from read operations when doing so improves scalability, maintainability, security, or business complexity.

CQRS is an architectural pattern.

It is not a requirement for every application.

---

## Core Principle

Commands change state.

Queries return state.

Never confuse the two.

---

## CQRS Goals

A CQRS architecture should provide:

- clear separation of responsibilities;
- simplified business logic;
- scalable read models;
- independent optimization of reads and writes;
- better support for complex domains.

CQRS introduces complexity.

Use it only when its benefits outweigh its costs.

---

## Basic Architecture

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

In NestJS the pattern is provided by the `@nestjs/cqrs` package. `CommandBus`,
`QueryBus`, and `EventBus` are injectable providers exposed once you import
`CqrsModule`. Handlers are ordinary providers annotated with
`@CommandHandler`, `@QueryHandler`, or `@EventsHandler` and registered in the
module's `providers` array:

```ts
// orders.module.ts
import { Module } from '@nestjs/common';
import { CqrsModule } from '@nestjs/cqrs';
import { TypeOrmModule } from '@nestjs/typeorm';
import { OrderEntity } from './order.entity';
import { OrderSummaryView } from './order-summary.view';
import { OrdersController } from './orders.controller';
import { CreateOrderHandler } from './commands/create-order.handler';
import { GetOrderHandler } from './queries/get-order.handler';
import { OrderCreatedHandler } from './events/order-created.handler';

const CommandHandlers = [CreateOrderHandler];
const QueryHandlers = [GetOrderHandler];
const EventHandlers = [OrderCreatedHandler];

@Module({
  imports: [
    CqrsModule,
    TypeOrmModule.forFeature([OrderEntity, OrderSummaryView]),
  ],
  controllers: [OrdersController],
  providers: [...CommandHandlers, ...QueryHandlers, ...EventHandlers],
})
export class OrdersModule {}
```

---

## Commands

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

## Queries

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

## Command Handler

Responsibilities:

- validate business rules;
- execute domain logic;
- coordinate repositories;
- publish events after successful persistence.

Command handlers should remain focused on one use case.

A command is a plain, immutable class describing an intention. The transport
layer validates a DTO, constructs the command, and dispatches it through the
`CommandBus`. The handler owns the business logic and returns the minimum the
caller needs—typically an identifier.

```ts
// commands/create-order.command.ts
export class CreateOrderCommand {
  constructor(
    public readonly customerId: string,
    public readonly items: ReadonlyArray<{ sku: string; quantity: number }>,
  ) {}
}
```

```ts
// dto/create-order.dto.ts
import { Type } from 'class-transformer';
import {
  ArrayNotEmpty,
  IsInt,
  IsPositive,
  IsString,
  IsUUID,
  ValidateNested,
} from 'class-validator';

class OrderItemDto {
  @IsString()
  sku: string;

  @IsInt()
  @IsPositive()
  quantity: number;
}

export class CreateOrderDto {
  @IsUUID()
  customerId: string;

  @ArrayNotEmpty()
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)
  items: OrderItemDto[];
}
```

```ts
// orders.controller.ts
import { Body, Controller, Get, Param, Post } from '@nestjs/common';
import { CommandBus, QueryBus } from '@nestjs/cqrs';
import { CreateOrderCommand } from './commands/create-order.command';
import { GetOrderQuery } from './queries/get-order.query';
import { CreateOrderDto } from './dto/create-order.dto';
import type { OrderSummary } from './queries/get-order.handler';

@Controller('orders')
export class OrdersController {
  constructor(
    private readonly commandBus: CommandBus,
    private readonly queryBus: QueryBus,
  ) {}

  @Post()
  async create(@Body() dto: CreateOrderDto): Promise<{ id: string }> {
    const id = await this.commandBus.execute<CreateOrderCommand, string>(
      new CreateOrderCommand(dto.customerId, dto.items),
    );
    return { id };
  }

  @Get(':id')
  getOne(@Param('id') id: string): Promise<OrderSummary> {
    return this.queryBus.execute<GetOrderQuery, OrderSummary>(
      new GetOrderQuery(id),
    );
  }
}
```

The DTO is validated by the global `ValidationPipe` (see the validation
document); the command class is the internal contract and stays free of
transport decorators.

```ts
// commands/create-order.handler.ts
import { CommandHandler, EventBus, ICommandHandler } from '@nestjs/cqrs';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { OrderEntity } from '../order.entity';
import { CreateOrderCommand } from './create-order.command';
import { OrderCreatedEvent } from '../events/order-created.event';

@CommandHandler(CreateOrderCommand)
export class CreateOrderHandler
  implements ICommandHandler<CreateOrderCommand, string>
{
  constructor(
    @InjectRepository(OrderEntity)
    private readonly orders: Repository<OrderEntity>,
    private readonly eventBus: EventBus,
  ) {}

  async execute(command: CreateOrderCommand): Promise<string> {
    const order = this.orders.create({
      customerId: command.customerId,
      status: 'PENDING',
      items: command.items.map((i) => ({ sku: i.sku, quantity: i.quantity })),
    });

    const saved = await this.orders.save(order);

    // Publish ONLY after the write has committed.
    this.eventBus.publish(
      new OrderCreatedEvent(saved.id, saved.customerId, saved.items.length),
    );

    return saved.id;
  }
}
```

Good — the command returns the identifier:

```ts
async execute(command: CreateOrderCommand): Promise<string> {
  const saved = await this.orders.save(order);
  return saved.id; // caller re-reads through a query if it needs detail
}
```

Bad — the command leaks the full write-model entity, coupling callers to the
persistence shape and blurring the read/write boundary:

```ts
async execute(command: CreateOrderCommand): Promise<OrderEntity> {
  return this.orders.save(order); // avoid: entity escapes the write model
}
```

---

## Query Handler

Responsibilities:

- retrieve data efficiently;
- compose read models;
- optimize performance;
- avoid unnecessary domain logic.

Query handlers should not modify application state.

A query is a plain class describing the requested data. The handler reads from
a projection—here a denormalized `OrderSummaryView`—and returns a read model
shaped for the consumer, not the persistence layer. No `save`, no domain
logic, no transactions.

```ts
// queries/get-order.query.ts
export class GetOrderQuery {
  constructor(public readonly orderId: string) {}
}
```

```ts
// queries/get-order.handler.ts
import { NotFoundException } from '@nestjs/common';
import { IQueryHandler, QueryHandler } from '@nestjs/cqrs';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { OrderSummaryView } from '../order-summary.view';
import { GetOrderQuery } from './get-order.query';

export interface OrderSummary {
  orderId: string;
  customerId: string;
  status: string;
  itemCount: number;
}

@QueryHandler(GetOrderQuery)
export class GetOrderHandler
  implements IQueryHandler<GetOrderQuery, OrderSummary>
{
  constructor(
    @InjectRepository(OrderSummaryView)
    private readonly summaries: Repository<OrderSummaryView>,
  ) {}

  async execute(query: GetOrderQuery): Promise<OrderSummary> {
    const view = await this.summaries.findOne({
      where: { orderId: query.orderId },
    });

    if (!view) {
      throw new NotFoundException(`Order ${query.orderId} not found`);
    }

    return {
      orderId: view.orderId,
      customerId: view.customerId,
      status: view.status,
      itemCount: view.itemCount,
    };
  }
}
```

---

## Read Model

The read model exists to optimize queries.

Examples:

- denormalized tables;
- materialized views;
- Elasticsearch indexes;
- Redis caches.

Read models are optimized for consumers—not persistence.

---

## Write Model

The write model preserves business consistency.

Responsibilities:

- enforce invariants;
- execute business rules;
- coordinate transactions.

Write models prioritize correctness over query performance.

---

## Eventual Consistency

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

## Domain Events

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

An event is a plain class named in the past tense. An `@EventsHandler` reacts
to it—typically to update a projection, keeping the read model eventually
consistent with the write model:

```ts
// events/order-created.event.ts
export class OrderCreatedEvent {
  constructor(
    public readonly orderId: string,
    public readonly customerId: string,
    public readonly itemCount: number,
  ) {}
}
```

```ts
// events/order-created.handler.ts
import { EventsHandler, IEventHandler } from '@nestjs/cqrs';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { OrderSummaryView } from '../order-summary.view';
import { OrderCreatedEvent } from './order-created.event';

@EventsHandler(OrderCreatedEvent)
export class OrderCreatedHandler implements IEventHandler<OrderCreatedEvent> {
  constructor(
    @InjectRepository(OrderSummaryView)
    private readonly summaries: Repository<OrderSummaryView>,
  ) {}

  async handle(event: OrderCreatedEvent): Promise<void> {
    // Build the denormalized read model (projection).
    await this.summaries.save({
      orderId: event.orderId,
      customerId: event.customerId,
      status: 'PENDING',
      itemCount: event.itemCount,
      createdAt: new Date(),
    });
  }
}
```

When events belong to an aggregate, extend `AggregateRoot` and buffer them with
`apply()`. `EventPublisher.mergeObjectContext` attaches the publisher, and
`commit()` dispatches the buffered events—call it only after persistence
succeeds, so events never fire for a write that rolled back:

```ts
// order.aggregate.ts
import { AggregateRoot } from '@nestjs/cqrs';
import { OrderCreatedEvent } from './events/order-created.event';

export class Order extends AggregateRoot {
  private constructor(
    public readonly id: string,
    private readonly customerId: string,
    private readonly itemCount: number,
  ) {
    super();
  }

  static place(id: string, customerId: string, itemCount: number): Order {
    const order = new Order(id, customerId, itemCount);
    // Recorded now, dispatched only when commit() runs.
    order.apply(new OrderCreatedEvent(id, customerId, itemCount));
    return order;
  }
}
```

```ts
// commands/place-order.handler.ts (aggregate variant)
import { randomUUID } from 'node:crypto';
import { CommandHandler, EventPublisher, ICommandHandler } from '@nestjs/cqrs';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { OrderEntity } from '../order.entity';
import { Order } from '../order.aggregate';
import { CreateOrderCommand } from './create-order.command';

@CommandHandler(CreateOrderCommand)
export class PlaceOrderHandler
  implements ICommandHandler<CreateOrderCommand, string>
{
  constructor(
    @InjectRepository(OrderEntity)
    private readonly orders: Repository<OrderEntity>,
    private readonly publisher: EventPublisher,
  ) {}

  async execute(command: CreateOrderCommand): Promise<string> {
    const order = this.publisher.mergeObjectContext(
      Order.place(randomUUID(), command.customerId, command.items.length),
    );

    await this.orders.save({
      id: order.id,
      customerId: command.customerId,
      status: 'PENDING',
      items: command.items.map((i) => ({ sku: i.sku, quantity: i.quantity })),
    });

    order.commit(); // flush events to their @EventsHandler after the write
    return order.id;
  }
}
```

---

## Outbox Pattern

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

## Event Sourcing

CQRS does not require Event Sourcing.

Event Sourcing stores events as the source of truth.

CQRS separates reads from writes.

These patterns may be combined but remain independent.

---

## Aggregates

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

## Validation

Separate validation into:

Transport validation:

- DTOs;
- Pipes.

Business validation:

- Command handlers;
- Domain services;
- Aggregates.

---

## Transactions

Commands may use transactions.

Queries should avoid transactions unless explicitly required.

Keep transaction boundaries inside the write model.

---

## Read Optimization

Optimize queries independently.

Examples:

- custom SQL;
- projections;
- caching;
- search indexes.

Read optimization should not affect business rules.

---

## Scaling

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

## Monitoring

Measure:

- command latency;
- query latency;
- projection delay;
- event processing;
- consistency lag.

CQRS should remain observable.

---

## Security

Authorization rules apply equally to:

- commands;
- queries.

Read operations may expose sensitive information.

Protect both sides independently.

---

## Testing

Verify:

- command execution;
- query correctness;
- event publication;
- projections;
- eventual consistency;
- aggregate invariants.

Commands and queries should be tested independently.

---

## When to Use CQRS

Suitable for:

- complex business domains;
- high read/write asymmetry;
- event-driven systems;
- distributed architectures;
- systems requiring independent scaling.

---

## When NOT to Use CQRS

Avoid CQRS for:

- simple CRUD applications;
- prototypes;
- internal administration panels;
- small services with limited complexity.

Do not introduce CQRS without measurable benefit.

---

## AI Decision Matrix

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

## AI Execution Checklist

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

## Examples

**Good Example** — a command that changes state, a query that does not

```ts
export class PlaceOrderCommand {
  constructor(readonly userId: string, readonly sku: string, readonly quantity: number) {}
}

@CommandHandler(PlaceOrderCommand)
export class PlaceOrderHandler implements ICommandHandler<PlaceOrderCommand, string> {
  constructor(
    private readonly orders: OrdersRepository,
    private readonly publisher: EventPublisher,
  ) {}

  // Returns the identifier only. The write model never leaves this handler.
  async execute(command: PlaceOrderCommand): Promise<string> {
    const order = this.publisher.mergeObjectContext(
      Order.place(command.userId, command.sku, command.quantity),
    );

    await this.orders.save(order);
    order.commit();          // domain events published after the write succeeds
    return order.id;
  }
}
```

```ts
export class GetOrderSummaryQuery {
  constructor(readonly orderId: string) {}
}

@QueryHandler(GetOrderSummaryQuery)
export class GetOrderSummaryHandler implements IQueryHandler<GetOrderSummaryQuery> {
  constructor(private readonly db: DataSource) {}

  // The read side is free to bypass the domain model entirely: a flat projection
  // shaped for the screen, with no aggregate to load or invariants to enforce.
  async execute(query: GetOrderSummaryQuery): Promise<OrderSummary | null> {
    const [row] = await this.db.query(
      `SELECT o.id, o.status, o.total_cents, u.email
         FROM orders o JOIN users u ON u.id = o.user_id
        WHERE o.id = $1`,
      [query.orderId],
    );
    return row ?? null;
  }
}
```

**Bad Example** — CQRS as a naming convention over the same model

```ts
@CommandHandler(GetOrderCommand)
export class GetOrderHandler implements ICommandHandler<GetOrderCommand> {
  // A "command" that reads. The separation now means nothing: there is no way to
  // route reads to a replica, or to reason about which operations mutate state.
  async execute(command: GetOrderCommand) {
    return this.repo.findOne({ where: { id: command.id } });
  }
}

@CommandHandler(PlaceOrderCommand)
export class PlaceOrderHandler implements ICommandHandler<PlaceOrderCommand> {
  async execute(command: PlaceOrderCommand) {
    const order = await this.repo.save({ sku: command.sku });

    // Returns the entity, so the caller depends on the write model's shape and
    // every schema change becomes an API change.
    return order;
  }
}
```

CQRS pays for itself when the read and write sides have genuinely different shapes or scaling
needs. Applied to a CRUD resource, it adds two classes per endpoint and buys nothing — see
[Architecture — CQRS](../architecture/07-cqrs.md).

---

## Common Mistakes

Avoid:

Using CQRS for every application.

Returning entities from commands.

Executing writes inside query handlers.

Publishing events before commit.

Ignoring eventual consistency.

Duplicating business rules in read models.

Creating unnecessary complexity.

---

## Completion Criteria

A CQRS implementation is complete when:

- commands and queries are clearly separated;
- business rules remain inside the write model;
- read models are optimized independently;
- event publication is reliable;
- eventual consistency is understood and acceptable;
- CQRS is justified by measurable architectural needs.

---

## Summary

CQRS separates state modification from data retrieval to improve scalability, maintainability, and architectural clarity.

By introducing CQRS only where business complexity justifies it, keeping commands and queries independent, protecting aggregate invariants, and optimizing read models separately, NestJS applications remain both flexible and maintainable without unnecessary complexity.

## Related

- `knowledge/nestjs/21-events.md`
- `knowledge/nestjs/01-architecture.md`
- `knowledge/architecture/07-cqrs.md`
- `knowledge/architecture/06-domain-driven-design.md`
