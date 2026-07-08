---
id: nestjs/01-architecture
topic: nestjs
slug: architecture
title: "NestJS Architecture"
type: doc
order: 1
status: ready
tags: [nestjs, architecture]
related: []
when_to_use: "Read before designing or reviewing the layer boundaries, dependencies, or overall structure of a NestJS application."
---
# NestJS Architecture

## Purpose

This document defines the architectural principles for building backend applications with NestJS.

The objective is to create applications that are scalable, maintainable, testable, secure, and easy to evolve by enforcing consistent architectural boundaries and dependency management.

Architecture decisions should prioritize long-term maintainability over short-term implementation speed.

---

## Core Principle

Design around business domains.

Business logic should remain independent from frameworks and infrastructure.

---

## Architectural Goals

Every NestJS application should strive for:

- modular architecture;
- clear separation of responsibilities;
- dependency inversion;
- low coupling;
- high cohesion;
- testability;
- scalability;
- predictable request flow.

---

## High-Level Architecture

Applications should be organized into independent business modules.

```
Application

        ↓

Module

        ↓

Controller

        ↓

Service

        ↓

Repository

        ↓

Database / External Services
```

Each layer has a clearly defined responsibility.

---

## Feature-Based Organization

Organize code by business feature rather than technical type.

Example:

```
modules/

    auth/

    users/

    orders/

    products/

    payments/
```

Each module should own its business logic and expose a clear public API.

---

## Layer Responsibilities

## Module

Responsible for:

- feature composition;
- dependency registration;
- provider configuration;
- exported services.

---

## Controller

Responsible for:

- receiving requests;
- validating input (through Pipes);
- invoking services;
- returning responses.

Controllers should remain thin.

A controller receives the request, delegates to a service, and returns the result. Input shape is described by a DTO and enforced by a pipe; the controller itself contains no business rules.

```ts
// orders/dto/create-order.dto.ts
import { IsInt, IsPositive, IsUUID } from 'class-validator';

export class CreateOrderDto {
  @IsUUID()
  productId: string;

  @IsInt()
  @IsPositive()
  quantity: number;
}
```

```ts
// orders/orders.controller.ts
import { Body, Controller, Get, Param, ParseUUIDPipe, Post } from '@nestjs/common';
import { OrdersService } from './orders.service';
import { CreateOrderDto } from './dto/create-order.dto';

@Controller('orders')
export class OrdersController {
  constructor(private readonly ordersService: OrdersService) {}

  @Post()
  create(@Body() dto: CreateOrderDto) {
    return this.ordersService.placeOrder(dto);
  }

  @Get(':id')
  findOne(@Param('id', ParseUUIDPipe) id: string) {
    return this.ordersService.getById(id);
  }
}
```

`ParseUUIDPipe` and the DTO-driven `ValidationPipe` (registered globally, see the Validation doc) reject malformed input before the service is ever invoked.

---

## Service

Responsible for:

- business rules;
- workflows;
- orchestration;
- domain operations.

Services should not depend on HTTP concepts.

The service owns the domain workflow. It depends on an abstract repository (not a concrete database class) and raises framework-level exceptions only at the edges. Notice there is no `@Req`, `@Res`, status code, or header in sight.

```ts
// orders/orders.service.ts
import { Injectable, NotFoundException } from '@nestjs/common';
import { OrdersRepository } from './orders.repository';
import { CreateOrderDto } from './dto/create-order.dto';
import { Order } from './entities/order.entity';

@Injectable()
export class OrdersService {
  constructor(private readonly orders: OrdersRepository) {}

  async placeOrder(dto: CreateOrderDto): Promise<Order> {
    // Business rule lives here, not in the controller or repository.
    const order = Order.create(dto.productId, dto.quantity);
    return this.orders.save(order);
  }

  async getById(id: string): Promise<Order> {
    const order = await this.orders.findById(id);
    if (!order) {
      throw new NotFoundException(`Order ${id} not found`);
    }
    return order;
  }
}
```

---

## Repository

Responsible for:

- database access;
- persistence;
- query execution.

Repositories should not implement business rules.

Define the repository as an abstract class inside the domain and implement it with a persistence-specific adapter. The abstract class doubles as a DI token, so the service depends on the contract while the concrete driver (TypeORM here) stays replaceable.

```ts
// orders/entities/order.entity.ts
import { Column, CreateDateColumn, Entity, PrimaryGeneratedColumn } from 'typeorm';

@Entity('orders')
export class Order {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column('uuid')
  productId: string;

  @Column('int')
  quantity: number;

  @Column({ default: 'pending' })
  status: string;

  @CreateDateColumn()
  createdAt: Date;

  static create(productId: string, quantity: number): Order {
    const order = new Order();
    order.productId = productId;
    order.quantity = quantity;
    order.status = 'pending';
    return order;
  }
}
```

```ts
// orders/orders.repository.ts — the port (also the DI token)
import { Order } from './entities/order.entity';

export abstract class OrdersRepository {
  abstract save(order: Order): Promise<Order>;
  abstract findById(id: string): Promise<Order | null>;
}
```

```ts
// orders/orders.typeorm.repository.ts — the adapter
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Order } from './entities/order.entity';
import { OrdersRepository } from './orders.repository';

@Injectable()
export class TypeOrmOrdersRepository extends OrdersRepository {
  constructor(
    @InjectRepository(Order)
    private readonly repo: Repository<Order>,
  ) {
    super();
  }

  save(order: Order): Promise<Order> {
    return this.repo.save(order);
  }

  findById(id: string): Promise<Order | null> {
    return this.repo.findOne({ where: { id } });
  }
}
```

---

## Infrastructure

Responsible for:

- external APIs;
- queues;
- storage;
- email;
- cloud services;
- third-party integrations.

Infrastructure should remain replaceable.

---

## Dependency Flow

Dependencies should move in one direction.

```
Controller

↓

Service

↓

Repository

↓

Database
```

Lower layers must never depend on higher layers.

---

## Dependency Injection

Register dependencies through NestJS providers.

Prefer constructor injection over manual instantiation.

The module composes the slice and binds the abstract port to a concrete implementation with `useClass`. This is where dependency inversion becomes real: `OrdersService` asked for `OrdersRepository` (the contract), and the module decides which adapter satisfies it. Swapping to a different persistence layer is a one-line change here, with no edit to the service.

```ts
// orders/orders.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { OrdersController } from './orders.controller';
import { OrdersService } from './orders.service';
import { OrdersRepository } from './orders.repository';
import { TypeOrmOrdersRepository } from './orders.typeorm.repository';
import { Order } from './entities/order.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Order])],
  controllers: [OrdersController],
  providers: [
    OrdersService,
    // Bind the port to its adapter. Injecting OrdersRepository resolves here.
    { provide: OrdersRepository, useClass: TypeOrmOrdersRepository },
  ],
  exports: [OrdersService], // Only the service is public; the repository stays internal.
})
export class OrdersModule {}
```

**Bad** — manual instantiation defeats DI: the dependency is hard-wired, cannot be swapped, and cannot be mocked in a unit test.

```ts
@Injectable()
export class OrdersService {
  // Hard dependency on a concrete class and a live DataSource.
  private readonly orders = new TypeOrmOrdersRepository(dataSource.getRepository(Order));
}
```

**Good** — declare the dependency in the constructor and let the container resolve it.

```ts
@Injectable()
export class OrdersService {
  constructor(private readonly orders: OrdersRepository) {}
}
```

Avoid:

- global singletons;
- static services;
- manual dependency creation.

---

## Business Logic

Business rules belong inside services.

**Bad** — the controller owns validation, persistence, and a side effect. It is now coupled to HTTP, the ORM, and the mailer all at once, and the rule cannot be reused or unit-tested without spinning up the web layer.

```ts
@Controller('orders')
export class OrdersController {
  constructor(
    @InjectRepository(Order) private readonly repo: Repository<Order>,
    private readonly mailer: MailerService,
  ) {}

  @Post()
  async create(@Body() dto: CreateOrderDto) {
    if (dto.quantity <= 0) {
      throw new BadRequestException('Quantity must be positive');
    }
    const order = await this.repo.save({ ...dto, status: 'pending' });
    await this.mailer.sendOrderConfirmation(order);
    return order;
  }
}
```

**Good** — the controller only translates HTTP to a service call. The rule and the orchestration live in `OrdersService.placeOrder`, which is testable in isolation and reusable from a queue consumer, a CLI command, or a GraphQL resolver.

```ts
@Controller('orders')
export class OrdersController {
  constructor(private readonly ordersService: OrdersService) {}

  @Post()
  create(@Body() dto: CreateOrderDto) {
    return this.ordersService.placeOrder(dto);
  }
}
```

Avoid placing business logic inside:

- controllers;
- repositories;
- DTOs;
- middleware.

Business logic should remain framework-independent whenever practical.

---

## Module Boundaries

Modules should communicate through explicit interfaces.

Avoid:

- direct access to internal providers;
- circular dependencies;
- shared mutable state.

Modules should remain independently maintainable.

---

## Shared Code

Place reusable code inside shared modules.

Examples:

```
shared/

    logger/

    cache/

    config/

    mail/

    validation/
```

Shared code should remain generic and reusable.

---

## Configuration

Centralize application configuration.

Typical categories:

- environment variables;
- database configuration;
- authentication;
- external services.

Avoid scattering configuration across modules.

---

## Error Handling

Define a consistent error handling strategy.

Examples:

- exception filters;
- domain errors;
- validation errors;
- infrastructure errors.

Errors should remain predictable.

---

## Scalability

Architecture should support:

- independent module growth;
- background workers;
- microservices;
- scheduled jobs;
- event-driven workflows.

Avoid designs that tightly couple unrelated features.

---

## Security

Sensitive operations should remain isolated.

Examples:

- authentication;
- authorization;
- credential management;
- secret handling.

Security should be enforced consistently across modules.

---

## Testing

Architecture should support:

- unit testing;
- integration testing;
- end-to-end testing.

Modules should remain testable in isolation.

---

## AI Execution Checklist

## Investigation

☐ Identify business domains.

☐ Review module boundaries.

☐ Review dependency graph.

☐ Review shared services.

---

## Planning

☐ Organize by feature.

☐ Keep controllers thin.

☐ Isolate business logic.

☐ Centralize infrastructure.

---

## Verification

☐ Module boundaries respected.

☐ Dependencies flow correctly.

☐ Business logic isolated.

☐ Shared code reusable.

☐ Architecture scalable.

☐ Testability preserved.

---

## Common Mistakes

Avoid:

Creating oversized modules.

Placing business logic inside controllers.

Mixing persistence with business rules.

Creating circular dependencies.

Sharing mutable state between modules.

Treating services as utility classes.

Ignoring module boundaries.

---

## Completion Criteria

The architecture is complete when:

- modules are organized by business domain;
- responsibilities are clearly separated;
- dependency flow is consistent;
- business logic is isolated from infrastructure;
- the application supports testing and scalability;
- security considerations are incorporated.

---

## Summary

A well-designed NestJS architecture is modular, predictable, and centered around business domains.

By enforcing clear boundaries, leveraging dependency injection, and separating business logic from infrastructure, applications remain easier to maintain, test, and scale as they evolve.