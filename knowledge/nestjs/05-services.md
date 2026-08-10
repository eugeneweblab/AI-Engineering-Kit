---
id: nestjs/05-services
topic: nestjs
slug: services
title: "NestJS Services"
type: doc
order: 5
status: ready
tags: [nestjs, services, Injectable, OrderStatus, Column, OrdersService, IsInt, InjectRepository, class, service]
related: [nestjs/06-repositories, nestjs/03-dependency-injection, nestjs/18-transactions, backend/07-business-logic]
when_to_use: "Read before writing or reviewing any service or business-logic class."
---
# NestJS Services

## Purpose

This document defines the engineering standards for implementing Services in NestJS applications.

The objective is to encapsulate business logic inside reusable, testable, and framework-independent services that coordinate application workflows while remaining isolated from transport and infrastructure concerns.

Services are the core of the application's business layer.

---

## Core Principle

Business logic belongs in services.

Everything else should support them.

---

## Service Goals

Every service should strive for:

- a single responsibility;
- reusable business logic;
- explicit dependencies;
- framework independence where practical;
- high testability;
- predictable behavior.

Services should model business capabilities rather than technical operations.

---

## Responsibilities

Services are responsible for:

- implementing business rules;
- coordinating workflows;
- orchestrating repositories;
- invoking external services;
- enforcing business constraints;
- publishing domain events when appropriate.

Services should not manage HTTP requests or persistence details directly.

---

## Service Position

A typical execution flow:

```
HTTP Request

↓

Controller

↓

Service

↓

Repository

↓

Database

↓

Response
```

Services act as the boundary between transport and persistence.

---

## Single Responsibility

Each service should own one business capability.

Examples:

```
UsersService

OrdersService

PaymentsService

NotificationsService
```

Avoid creating generic services with unrelated responsibilities.

---

## Business Logic

Business logic includes:

- validation beyond DTO validation;
- business rules;
- calculations;
- workflow orchestration;
- authorization decisions at the domain level;
- consistency checks.

Business logic should not be duplicated across controllers.

### Shared domain model

The examples in this document use one small domain. DTO shape and validation
belong to the transport layer (see `07-dto` and `08-validation`); the service
owns rules that DTO validation cannot express.

```ts
// order.entity.ts
import { Column, Entity, PrimaryGeneratedColumn } from 'typeorm';

export enum OrderStatus {
  Pending = 'PENDING',
  Paid = 'PAID',
}

@Entity('orders')
export class Order {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column('jsonb')
  items!: Array<{ unitPrice: number; quantity: number }>;

  @Column('int')
  total!: number;

  @Column({ type: 'enum', enum: OrderStatus, default: OrderStatus.Pending })
  status!: OrderStatus;
}
```

```ts
// create-order.dto.ts
import { Type } from 'class-transformer';
import { ArrayNotEmpty, IsInt, Min, ValidateNested } from 'class-validator';

class OrderItemDto {
  @IsInt()
  @Min(0)
  unitPrice!: number;

  @IsInt()
  @Min(1)
  quantity!: number;
}

export class CreateOrderDto {
  @ArrayNotEmpty()
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)
  items!: OrderItemDto[];
}
```

### Good / Bad: where business logic lives

The controller must stay thin. Rules, calculations, and consistency checks
belong in the service so they can be reused and tested in isolation.

```ts
// ❌ Bad — rules, calculations, and queries jammed into the controller
@Controller('orders')
export class OrdersController {
  constructor(private readonly dataSource: DataSource) {}

  @Post()
  async create(@Body() dto: CreateOrderDto): Promise<Order> {
    const repo = this.dataSource.getRepository(Order);
    const total = dto.items.reduce((s, i) => s + i.unitPrice * i.quantity, 0);
    if (total > 10_000) {
      throw new BadRequestException('Order too large'); // HTTP leaks into logic
    }
    return repo.save(repo.create({ items: dto.items, total, status: OrderStatus.Pending }));
  }
}
```

```ts
// ✅ Good — controller delegates; the service owns the business capability
@Controller('orders')
export class OrdersController {
  constructor(private readonly orders: OrdersService) {}

  @Post()
  create(@Body() dto: CreateOrderDto): Promise<Order> {
    return this.orders.placeOrder(dto);
  }
}
```

```ts
// order-too-large.error.ts — a framework-independent domain exception
export class DomainError extends Error {}

export class OrderTooLargeError extends DomainError {
  constructor(
    readonly total: number,
    readonly limit: number,
  ) {
    super(`Order total ${total} exceeds the limit ${limit}`);
    this.name = 'OrderTooLargeError';
  }
}
```

```ts
// orders.service.ts
import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class OrdersService {
  constructor(
    private readonly orders: OrdersRepository,
    private readonly config: ConfigService,
  ) {}

  async placeOrder(dto: CreateOrderDto): Promise<Order> {
    // DTO validation already guaranteed non-empty items and valid numbers.
    // This is a *business* rule the DTO cannot express.
    const total = dto.items.reduce((sum, i) => sum + i.unitPrice * i.quantity, 0);
    const limit = this.config.get<number>('orders.maxTotal', 10_000);
    if (total > limit) {
      throw new OrderTooLargeError(total, limit);
    }

    return this.orders.create({
      items: dto.items,
      total,
      status: OrderStatus.Pending,
    });
  }
}
```

A `DomainError` keeps the service transport-agnostic; an `ExceptionFilter`
(see `11-exception-filters`) maps it to the correct HTTP status at the edge.

---

## Collaboration

Services may collaborate with:

- repositories;
- other services;
- infrastructure adapters;
- event publishers.

Dependencies should remain explicit and intentional.

---

## Repository Usage

Services should delegate persistence to repositories.

Example:

```
Service

↓

Repository

↓

Database
```

Avoid embedding SQL or ORM queries directly inside services.

The repository is a thin persistence adapter. It exposes intent-revealing
methods and hides the ORM; the service depends on it, not on `Repository<T>`
or raw query builders.

```ts
// orders.repository.ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { DeepPartial, Repository } from 'typeorm';

@Injectable()
export class OrdersRepository {
  constructor(
    @InjectRepository(Order)
    private readonly repo: Repository<Order>,
  ) {}

  create(data: DeepPartial<Order>): Promise<Order> {
    return this.repo.save(this.repo.create(data));
  }

  findById(id: string): Promise<Order | null> {
    return this.repo.findOne({ where: { id } });
  }
}
```

```ts
// orders.module.ts — wiring the entity, repository, and service together
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';

@Module({
  imports: [TypeOrmModule.forFeature([Order])],
  controllers: [OrdersController],
  providers: [OrdersService, OrdersRepository],
  exports: [OrdersService],
})
export class OrdersModule {}
```

---

## Transactions

When multiple operations must succeed together, services should coordinate transactional boundaries.

Transactions should remain:

- minimal;
- atomic;
- consistent.

Avoid unnecessarily long-running transactions.

A service coordinates the transactional boundary while keeping the unit of work
small. Here the payment provider is reached through an injected port
(`PaymentGateway`) so business logic never depends on a vendor SDK, and the
early return makes a retried call idempotent.

```ts
// payment.gateway.ts — the port the service depends on
export abstract class PaymentGateway {
  abstract charge(amountCents: number, reference: string): Promise<void>;
}

// order-not-found.error.ts — another DomainError subclass
export class OrderNotFoundError extends DomainError {
  constructor(readonly orderId: string) {
    super(`Order ${orderId} was not found`);
    this.name = 'OrderNotFoundError';
  }
}
```

```ts
// checkout.service.ts
import { Injectable } from '@nestjs/common';
import { DataSource } from 'typeorm';

@Injectable()
export class CheckoutService {
  constructor(
    private readonly dataSource: DataSource,
    private readonly payments: PaymentGateway,
  ) {}

  async pay(orderId: string): Promise<void> {
    await this.dataSource.transaction(async (manager) => {
      const order = await manager.findOne(Order, {
        where: { id: orderId },
        lock: { mode: 'pessimistic_write' },
      });
      if (!order) {
        throw new OrderNotFoundError(orderId);
      }
      if (order.status === OrderStatus.Paid) {
        return; // already paid — safe to retry
      }

      await this.payments.charge(order.total, order.id);
      order.status = OrderStatus.Paid;
      await manager.save(order);
    });
  }
}
```

---

## Idempotency

Operations that may be retried should be idempotent whenever practical.

Examples:

- payment callbacks;
- webhook processing;
- scheduled jobs.

Repeated execution should not corrupt business data.

---

## External Integrations

Services should interact with external systems through dedicated adapters.

Examples:

- payment providers;
- email services;
- cloud storage;
- message brokers.

Avoid coupling business logic directly to SDK implementations.

---

## Error Handling

Services should throw meaningful domain exceptions.

Avoid:

- returning magic values;
- swallowing errors;
- leaking infrastructure-specific exceptions.

Failures should be predictable and actionable.

---

## Return Values

Services should return domain objects or well-defined result structures.

Avoid returning transport-specific objects such as:

- HTTP responses;
- Express request objects;
- framework-specific response wrappers.

---

## Asynchronous Operations

Use asynchronous operations where appropriate.

Review:

- database access;
- network calls;
- file operations;
- background processing.

Avoid blocking operations.

---

## Side Effects

Keep side effects explicit.

Typical side effects include:

- sending emails;
- publishing events;
- writing files;
- invoking third-party APIs.

Separate side effects from core business rules whenever practical.

---

## Domain Events

Use domain events to notify other modules about completed business operations.

Examples:

- UserRegistered
- OrderPaid
- InvoiceCreated

Events should reduce coupling between modules.

---

## Configuration

Services should receive configuration through dependency injection.

Avoid reading environment variables directly inside service methods.

---

## Security

Services should enforce business-level security rules.

Examples:

- ownership validation;
- permission checks;
- business constraints.

Never rely solely on controllers for security.

---

## Performance

Review:

- duplicate queries;
- unnecessary network requests;
- inefficient algorithms;
- repeated calculations.

Business workflows should remain efficient and scalable.

---

## Testing

Services should be tested independently.

Verify:

- business rules;
- success scenarios;
- failure scenarios;
- edge cases;
- interaction with dependencies.

Replace external dependencies with mocks or fakes.

Because dependencies are injected through the constructor, a service can be
tested by plain instantiation — no `Test.createTestingModule` or database
required. This is the payoff of explicit dependencies.

```ts
// orders.service.spec.ts
import { ConfigService } from '@nestjs/config';

describe('OrdersService', () => {
  const orders = { create: jest.fn() } as unknown as OrdersRepository;
  const config = {
    get: jest.fn().mockReturnValue(10_000),
  } as unknown as ConfigService;
  let service: OrdersService;

  beforeEach(() => {
    jest.clearAllMocks();
    service = new OrdersService(orders, config);
  });

  it('persists an order within the limit', async () => {
    const saved = { id: 'o1', total: 300, status: OrderStatus.Pending } as Order;
    (orders.create as jest.Mock).mockResolvedValue(saved);

    const result = await service.placeOrder({
      items: [{ unitPrice: 100, quantity: 3 }],
    });

    expect(result).toBe(saved);
    expect(orders.create).toHaveBeenCalledWith(
      expect.objectContaining({ total: 300, status: OrderStatus.Pending }),
    );
  });

  it('rejects an order above the configured limit', async () => {
    await expect(
      service.placeOrder({ items: [{ unitPrice: 6_000, quantity: 2 }] }),
    ).rejects.toBeInstanceOf(OrderTooLargeError);
    expect(orders.create).not.toHaveBeenCalled();
  });
});
```

---

## AI Execution Checklist

## Investigation

☐ Identify business capability.

☐ Review dependencies.

☐ Review workflow.

☐ Review business rules.

---

## Planning

☐ Keep service focused.

☐ Delegate persistence.

☐ Isolate side effects.

☐ Handle failures consistently.

---

## Verification

☐ Business logic centralized.

☐ Dependencies injected.

☐ Repository abstraction respected.

☐ Domain rules enforced.

☐ Service independently testable.

☐ Performance reviewed.

---

## Examples

**Good Example** — business rules expressed without transport types

```ts
@Injectable()
export class OrdersService {
  constructor(
    private readonly orders: OrdersRepository,
    private readonly inventory: InventoryService,
    private readonly events: EventEmitter2,
  ) {}

  async place(command: PlaceOrder): Promise<Order> {
    const reserved = await this.inventory.reserve(command.items);
    if (!reserved.ok) {
      // A domain error, not an HTTP error. The controller maps it; a queue
      // consumer handles it differently, and neither has to change this method.
      throw new OutOfStockError(reserved.missingSku);
    }

    const order = await this.orders.create({
      userId: command.userId,
      items: command.items,
      totalCents: this.total(command.items),
    });

    // Side effects are announced, not performed here: no mailer, no HTTP client.
    this.events.emit('order.placed', new OrderPlacedEvent(order.id));

    return order;
  }

  private total(items: ReadonlyArray<OrderItem>): number {
    return items.reduce((sum, item) => sum + item.priceCents * item.quantity, 0);
  }
}
```

**Bad Example** — the service knows it is behind HTTP

```ts
@Injectable()
export class OrdersService {
  constructor(
    @Inject(REQUEST) private readonly request: Request,   // transport leaked into the rule
    @InjectRepository(OrderEntity) private readonly repo: Repository<OrderEntity>,
  ) {}

  async place(body: any) {
    // Reading the request here means this method only works inside a web request:
    // the same logic cannot run from a queue, a cron job, or a test.
    const userId = (this.request as any).user?.id;

    if (!body.items?.length) {
      throw new BadRequestException('no items');   // an HTTP status inside the domain
    }

    const saved = await this.repo.save({ userId, items: body.items });

    // Fire-and-forget: a failure here is silent, and the caller cannot compensate.
    void fetch('https://hooks.example.com/order', { method: 'POST' });

    return saved;
  }
}
```

Injecting `REQUEST` also forces the provider into request scope, which propagates to every
class that injects `OrdersService`.

---

## Common Mistakes

Avoid:

Putting business logic inside controllers.

Embedding database queries inside services.

Returning HTTP responses.

Reading `process.env` directly.

Creating "God Services" with unrelated responsibilities.

Calling third-party SDKs directly throughout business logic.

Duplicating business rules across services.

---

## Completion Criteria

A service implementation is complete when:

- it represents a single business capability;
- business logic is fully encapsulated;
- persistence is delegated to repositories;
- dependencies are injected explicitly;
- side effects are isolated;
- the service can be tested independently.

---

## Summary

Services are the heart of every NestJS application.

By centralizing business logic, coordinating workflows, depending on abstractions, and keeping infrastructure concerns separate, services remain reusable, testable, and maintainable as the application evolves.

## Related

- `knowledge/nestjs/06-repositories.md`
- `knowledge/nestjs/03-dependency-injection.md`
- `knowledge/nestjs/18-transactions.md`
- `knowledge/backend/07-business-logic.md`
