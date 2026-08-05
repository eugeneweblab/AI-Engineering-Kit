---
id: nestjs/02-modules
topic: nestjs
slug: modules
title: "NestJS Modules"
type: doc
order: 2
status: ready
tags: [nestjs, modules]
related: [nestjs/01-architecture, nestjs/03-dependency-injection, nestjs/14-configuration, nestjs/05-services, architecture/10-modular-monolith]
when_to_use: "Read before creating, splitting, or reviewing NestJS modules and their imports and exports."
---
# NestJS Modules

## Purpose

This document defines the engineering standards for designing and organizing modules in NestJS applications.

The objective is to build modular, maintainable, and scalable applications where each module represents a distinct business capability with clear boundaries and responsibilities.

Modules are the primary building blocks of a NestJS application.

---

## Core Principle

One module.

One business capability.

Modules should represent business domains rather than technical categories.

---

## Module Goals

Every module should provide:

- a clear responsibility;
- well-defined public APIs;
- minimal dependencies;
- isolated business logic;
- high cohesion;
- low coupling.

A module should be understandable independently from the rest of the application.

---

## Feature-Based Organization

Organize modules around business features.

Example:

```
modules/

    auth/

    users/

    products/

    orders/

    payments/

    notifications/
```

Avoid organizing the application by technical layers.

---

## Module Structure

A typical module may contain:

```
users/

    users.module.ts

    users.controller.ts

    users.service.ts

    users.repository.ts

    dto/

    entities/

    interfaces/

    events/

    policies/

    validators/

    mappers/
```

Keep the internal structure consistent across modules.

---

## Module Responsibilities

A module owns:

- business logic;
- controllers;
- providers;
- repositories;
- validation;
- feature-specific configuration.

A module should expose only what other modules require.

---

## Public API

Export only stable providers.

A feature module declares its controllers and providers, and exports only the
service that forms its stable public contract. The repository stays private.

```typescript
// users/users.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { UsersRepository } from './users.repository';
import { User } from './entities/user.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  exports: [UsersService], // only the stable public API leaves the module
})
export class UsersModule {}
```

Do not expose internal implementation details.

---

## Imports

Import only modules that are required.

Avoid creating large dependency graphs.

Review every import and justify its necessity.

---

## Exports

Export providers intentionally.

If another module does not require a provider, it should remain private.

Avoid exporting everything by default.

Good — export only the provider that other modules consume:

```typescript
@Module({
  controllers: [UsersController],
  providers: [UsersService, UsersRepository, UserPasswordHasher],
  exports: [UsersService], // consumers depend on the service, not the internals
})
export class UsersModule {}
```

Bad — leaking every internal provider couples other modules to implementation
details and makes the repository and hasher impossible to change safely:

```typescript
@Module({
  controllers: [UsersController],
  providers: [UsersService, UsersRepository, UserPasswordHasher],
  exports: [UsersService, UsersRepository, UserPasswordHasher], // over-exposed
})
export class UsersModule {}
```

---

## Shared Modules

Place generic functionality inside shared modules.

Examples:

```
shared/

    cache/

    logger/

    mail/

    config/

    storage/
```

Shared modules should remain independent from business features.

---

## Global Modules

Use global modules sparingly.

Suitable examples include:

- configuration;
- logging;
- metrics.

Mark the module with `@Global()` so its exports are available everywhere without
re-importing. It must still be imported once (typically in the root module) for
its providers to be instantiated.

```typescript
// logger/logger.module.ts
import { Global, Module } from '@nestjs/common';
import { LoggerService } from './logger.service';

@Global()
@Module({
  providers: [LoggerService],
  exports: [LoggerService],
})
export class LoggerModule {}
```

Business modules should not normally be global.

---

## Dynamic Modules

Use dynamic modules when runtime configuration is required.

Typical examples:

- authentication;
- database connections;
- caching;
- third-party integrations.

Expose static `forRoot`/`forRootAsync` methods that return a `DynamicModule`.
Pass options through an injection token so services can consume them, and use the
async variant when options depend on other providers such as `ConfigService`.

```typescript
// storage/storage.module.ts
import { DynamicModule, Module, Provider } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { StorageService } from './storage.service';

export interface StorageOptions {
  bucket: string;
  region: string;
}

// A unique token that both providers and services reference.
export const STORAGE_OPTIONS = Symbol('STORAGE_OPTIONS');

@Module({})
export class StorageModule {
  static forRoot(options: StorageOptions): DynamicModule {
    return {
      module: StorageModule,
      providers: [
        { provide: STORAGE_OPTIONS, useValue: options },
        StorageService,
      ],
      exports: [StorageService],
    };
  }

  static forRootAsync(): DynamicModule {
    const optionsProvider: Provider = {
      provide: STORAGE_OPTIONS,
      useFactory: (config: ConfigService): StorageOptions => ({
        bucket: config.getOrThrow<string>('STORAGE_BUCKET'),
        region: config.getOrThrow<string>('STORAGE_REGION'),
      }),
      inject: [ConfigService],
    };

    return {
      module: StorageModule,
      providers: [optionsProvider, StorageService],
      exports: [StorageService],
    };
  }
}
```

The service injects the resolved options through the same token:

```typescript
// storage/storage.service.ts
import { Inject, Injectable } from '@nestjs/common';
import { STORAGE_OPTIONS, StorageOptions } from './storage.module';

@Injectable()
export class StorageService {
  constructor(
    @Inject(STORAGE_OPTIONS) private readonly options: StorageOptions,
  ) {}
}
```

Keep dynamic configuration centralized.

---

## Circular Dependencies

Avoid circular dependencies between modules.

Instead:

- extract shared functionality;
- introduce interfaces;
- redesign ownership.

When two modules genuinely reference each other and the cycle cannot be removed
immediately, break it with `forwardRef()` on both the module import and the
provider injection. Treat this as a temporary measure, not a design goal.

```typescript
// orders/orders.module.ts
import { Module, forwardRef } from '@nestjs/common';
import { PaymentsModule } from '../payments/payments.module';
import { OrdersService } from './orders.service';

@Module({
  imports: [forwardRef(() => PaymentsModule)],
  providers: [OrdersService],
  exports: [OrdersService],
})
export class OrdersModule {}
```

```typescript
// orders/orders.service.ts
import { Inject, Injectable, forwardRef } from '@nestjs/common';
import { PaymentsService } from '../payments/payments.service';

@Injectable()
export class OrdersService {
  constructor(
    @Inject(forwardRef(() => PaymentsService))
    private readonly paymentsService: PaymentsService,
  ) {}
}
```

Circular dependencies often indicate architectural problems.

---

## Dependency Direction

Dependencies should flow toward lower-level services.

Example:

```
Orders

↓

Payments

↓

Infrastructure
```

Avoid bidirectional dependencies.

---

## Configuration

Each module should own only its feature-specific configuration.

Application-wide configuration belongs in centralized configuration modules.

---

## Validation

Validation should remain close to the feature.

Typical examples:

- DTO validation;
- custom validators;
- business rule validation.

Validation responsibilities should remain explicit.

---

## Events

Modules may communicate through domain events when direct dependencies become excessive.

Events should reduce coupling without obscuring application flow.

---

## Testing

Each module should be independently testable.

Verify:

- public providers;
- controllers;
- business workflows;
- repository interactions.

Modules should not require the entire application to execute tests.

---

## Scalability

Modules should support:

- independent development;
- isolated refactoring;
- future extraction into microservices if required.

Architecture should not assume a monolithic future.

---

## Security

Each module should enforce its own:

- authorization rules;
- validation;
- resource ownership;
- business constraints.

Do not rely solely on external modules for security.

---

## AI Execution Checklist

## Investigation

☐ Identify business capability.

☐ Review dependencies.

☐ Review exported providers.

☐ Review ownership.

---

## Planning

☐ Create a dedicated module.

☐ Keep responsibilities focused.

☐ Export only required providers.

☐ Minimize dependencies.

---

## Verification

☐ Module boundaries respected.

☐ Public API clear.

☐ No circular dependencies.

☐ Shared functionality centralized.

☐ Business logic isolated.

☐ Module independently testable.

---

## Examples

**Good Example** — a feature module with a deliberate public surface

```ts
// orders/orders.module.ts — imports what it needs, exports only what others may use.
@Module({
  imports: [
    TypeOrmModule.forFeature([OrderEntity]),
    PaymentsModule,                 // a sibling feature, imported explicitly
  ],
  controllers: [OrdersController],
  providers: [OrdersService, OrdersRepository, OrderPricing],
  exports: [OrdersService],         // the only thing other modules may depend on
})
export class OrdersModule {}
```

```ts
// billing/billing.module.ts — depends on the exported service, not on internals.
@Module({
  imports: [OrdersModule],
  providers: [InvoiceService],
})
export class BillingModule {}
```

`OrdersRepository` and `OrderPricing` cannot be injected outside `OrdersModule`, so a
refactor of either is contained. The dependency graph is visible in the decorators.

**Bad Example** — one module for everything, plus a `CommonModule` that exports it all

```ts
// app.module.ts — every provider in the application, in one list.
@Module({
  controllers: [OrdersController, UsersController, PaymentsController, ReportsController],
  providers: [
    OrdersService, OrdersRepository, OrderPricing,
    UsersService, UsersRepository,
    PaymentsService, StripeClient, InvoiceService, ReportBuilder,
  ],
})
export class AppModule {}

// common/common.module.ts — a bag with no boundary: importing it grants access
// to everything, so no dependency is ever explicit and nothing can be extracted.
@Global()
@Module({
  providers: [OrdersService, UsersService, PaymentsService, StripeClient],
  exports: [OrdersService, UsersService, PaymentsService, StripeClient],
})
export class CommonModule {}
```

With `@Global()` and a catch-all export list, every provider is reachable from everywhere.
The compiler can no longer tell you what breaks when `StripeClient` changes.

---

## Common Mistakes

Avoid:

Creating "utility" modules containing unrelated functionality.

Exporting every provider.

Using global modules unnecessarily.

Mixing multiple business domains in one module.

Creating circular dependencies.

Sharing repositories between unrelated modules.

Ignoring module ownership.

---

## Completion Criteria

A module implementation is complete when:

- it represents a single business capability;
- responsibilities are clearly defined;
- dependencies remain minimal;
- public APIs are explicit;
- business logic is encapsulated;
- the module can be developed and tested independently.

---

## Summary

Modules are the foundation of every NestJS application.

By organizing code around business capabilities, minimizing coupling, exposing only well-defined public APIs, and maintaining clear ownership boundaries, applications become significantly easier to understand, extend, and maintain over time.

## Related

- `knowledge/nestjs/01-architecture.md`
- `knowledge/nestjs/03-dependency-injection.md`
- `knowledge/nestjs/14-configuration.md`
- `knowledge/nestjs/05-services.md`
- `knowledge/architecture/10-modular-monolith.md`
