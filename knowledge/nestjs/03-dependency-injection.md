---
id: nestjs/03-dependency-injection
topic: nestjs
slug: dependency-injection
title: "NestJS Dependency Injection"
type: doc
order: 3
status: ready
tags: [nestjs, dependency-injection, Injectable, Inject, Module, UsersRepository, charge, UsersService]
related: [nestjs/02-modules, nestjs/05-services, nestjs/25-testing, nestjs/01-architecture]
when_to_use: "Read before wiring providers, tokens, scopes, or custom factories, or when debugging DI resolution errors."
---
# NestJS Dependency Injection

## Purpose

This document defines the engineering standards for using Dependency Injection (DI) in NestJS applications.

The objective is to build loosely coupled, testable, and maintainable applications by relying on NestJS's Inversion of Control (IoC) container instead of manual dependency management.

Dependency Injection should simplify architecture rather than complicate it.

---

## Core Principle

Depend on abstractions.

Not implementations.

Dependencies should be injected, never created manually inside business logic.

---

## Dependency Injection Goals

Every application should strive for:

- loose coupling;
- high cohesion;
- testability;
- explicit dependencies;
- reusable services;
- maintainable architecture.

---

## Dependency Flow

Dependencies should flow in one direction.

```
Controller

↓

Service

↓

Repository

↓

Infrastructure
```

Lower layers must never depend on higher layers.

---

## Constructor Injection

Prefer constructor injection for all dependencies.

The `@Injectable()` decorator marks a class as a provider that the IoC
container can instantiate and inject. Declare each dependency as a
`private readonly` constructor parameter so it is explicit and immutable
after construction.

Good — dependencies are injected and the container owns their lifecycle:

```ts
import { Injectable } from '@nestjs/common';

@Injectable()
export class UsersService {
  constructor(
    private readonly usersRepository: UsersRepository,
    private readonly mailer: MailerService,
  ) {}

  async register(email: string): Promise<User> {
    const user = await this.usersRepository.create({ email });
    await this.mailer.sendWelcome(user.email);
    return user;
  }
}
```

Bad — dependencies are created with `new`, so they cannot be swapped,
mocked, or configured, and the container never manages their scope:

```ts
@Injectable()
export class UsersService {
  // Anti-pattern: hard-wired construction defeats DI entirely.
  private readonly usersRepository = new UsersRepository();
  private readonly mailer = new MailerService({ apiKey: process.env.MAIL_KEY });

  async register(email: string): Promise<User> {
    const user = await this.usersRepository.create({ email });
    await this.mailer.sendWelcome(user.email);
    return user;
  }
}
```

Dependencies should be explicit and immutable after object creation.

Avoid property injection (`@Inject()` on a field) — it hides dependencies
and breaks the guarantee that an object is fully constructed once created.

---

## Providers

Providers are the primary mechanism for dependency injection.

Typical providers include:

- services;
- repositories;
- factories;
- adapters;
- clients;
- utilities.

Providers should encapsulate a single responsibility.

---

## Provider Registration

Register providers inside the owning module. Export only what other
modules legitimately need; keep everything else private to the module.

```ts
import { Module } from '@nestjs/common';

@Module({
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  exports: [UsersService], // UsersRepository stays private to this module
})
export class UsersModule {}
```

A provider is only injectable where it is visible: either declared in the
consuming module's `providers`, or exported by an imported module. Adding a
class to another module's `providers` creates a second, independent
instance — import the owning module instead.

Avoid registering unrelated providers in the same module.

---

## Injection Tokens

Use injection tokens when:

- injecting interfaces;
- supporting multiple implementations;
- building reusable libraries;
- decoupling infrastructure.

TypeScript interfaces do not exist at runtime, so they cannot be used as
injection tokens directly. Define an abstraction as an abstract class (or a
`string`/`Symbol` token) and bind a concrete implementation to it. Consumers
depend on the abstraction; the module decides the implementation.

```ts
// payment.gateway.ts — the abstraction consumers depend on.
export abstract class PaymentGateway {
  abstract charge(amountCents: number, token: string): Promise<string>;
}

// stripe.gateway.ts — one concrete implementation.
import { Injectable } from '@nestjs/common';

@Injectable()
export class StripeGateway extends PaymentGateway {
  async charge(amountCents: number, token: string): Promise<string> {
    // ...call Stripe SDK, return the charge id
    return 'ch_123';
  }
}
```

```ts
// payments.module.ts — bind the abstraction to an implementation.
import { Module } from '@nestjs/common';

@Module({
  providers: [{ provide: PaymentGateway, useClass: StripeGateway }],
  exports: [PaymentGateway],
})
export class PaymentsModule {}
```

```ts
// checkout.service.ts — depends only on the abstraction.
import { Injectable } from '@nestjs/common';

@Injectable()
export class CheckoutService {
  constructor(private readonly gateway: PaymentGateway) {}

  pay(amountCents: number, token: string): Promise<string> {
    return this.gateway.charge(amountCents, token);
  }
}
```

Swapping to a different provider (a fake in tests, a different vendor in
another environment) only changes the `useClass` binding — no consumer
changes. For `string`/`Symbol` tokens, inject with
`@Inject('PAYMENT_GATEWAY')` on the constructor parameter.

Prefer descriptive token names.

---

## Custom Providers

Use custom providers for:

- external SDKs;
- third-party clients;
- adapters;
- runtime configuration.

Keep custom provider configuration centralized.

---

## Factory Providers

Use factory providers when object creation requires:

- configuration;
- asynchronous initialization;
- conditional behavior;
- dependency composition.

A factory provider runs a `useFactory` function to build the value. Declare
its own dependencies in `inject` — they are passed to the factory in order.
Use `async` when initialization must await a connection or handshake.

```ts
import { Module } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { createClient, RedisClientType } from 'redis';

export const REDIS_CLIENT = 'REDIS_CLIENT';

@Module({
  providers: [
    {
      provide: REDIS_CLIENT,
      inject: [ConfigService],
      useFactory: async (config: ConfigService): Promise<RedisClientType> => {
        const client = createClient({ url: config.getOrThrow<string>('REDIS_URL') });
        await client.connect();
        return client;
      },
    },
  ],
  exports: [REDIS_CLIENT],
})
export class RedisModule {}
```

Inject the resulting client by its token:

```ts
import { Inject, Injectable } from '@nestjs/common';
import type { RedisClientType } from 'redis';

@Injectable()
export class SessionStore {
  constructor(@Inject(REDIS_CLIENT) private readonly redis: RedisClientType) {}

  // redis.set resolves to `string | null` (null when using GET/NX/XX modes),
  // so the return type must include null under strictNullChecks.
  save(id: string, data: string): Promise<string | null> {
    return this.redis.set(`session:${id}`, data);
  }
}
```

Factory logic should remain simple and predictable — build and return the
object; keep business rules out of the factory.

---

## Value Providers

Use value providers for:

- configuration objects;
- constants;
- immutable shared values.

Avoid placing business logic inside value providers.

---

## Existing Providers

Reuse existing providers when multiple tokens should resolve to the same implementation.

Avoid creating duplicate service instances unnecessarily.

---

## Provider Scope

Prefer singleton providers.

Use request-scoped providers only when request-specific state is required.

Use transient providers only when independent instances are necessary.

Choose the simplest scope that satisfies the requirement.

---

## Optional Dependencies

Mark dependencies as optional only when the application can function correctly without them.

Avoid excessive optional dependencies.

---

## Circular Dependencies

Avoid circular dependencies between providers.

If encountered:

- extract shared logic;
- redesign ownership;
- introduce abstractions.

When two providers genuinely must reference each other and the design cannot
be untangled, `forwardRef()` breaks the resolution cycle. It is a workaround,
not a fix — it must be applied on **both** sides.

```ts
import { Injectable, Inject, forwardRef } from '@nestjs/common';

@Injectable()
export class OrdersService {
  constructor(
    @Inject(forwardRef(() => InvoicesService))
    private readonly invoices: InvoicesService,
  ) {}
}

@Injectable()
export class InvoicesService {
  constructor(
    @Inject(forwardRef(() => OrdersService))
    private readonly orders: OrdersService,
  ) {}
}
```

Modules that depend on each other use the same helper:
`imports: [forwardRef(() => OtherModule)]`.

Using circular dependency workarounds should be a last resort.

---

## Service Design

Services should:

- expose clear public methods;
- avoid framework-specific logic;
- remain independently testable;
- encapsulate business rules.

Services should not create other services directly.

---

## Repository Injection

Repositories should be injected rather than instantiated manually.

Persistence concerns should remain isolated from business logic.

---

## Configuration Injection

Inject configuration through dedicated configuration providers.

Avoid reading environment variables directly throughout the application.

---

## External Integrations

Inject external services such as:

- email providers;
- payment gateways;
- storage providers;
- messaging systems.

Infrastructure should remain replaceable.

---

## Testing

Dependency Injection should simplify testing.

Replace dependencies with:

- mocks;
- stubs;
- fakes;
- test providers.

Because dependencies are injected, a test can supply a substitute for each
one. `Test.createTestingModule` builds an isolated container; override any
provider by re-binding its token with `useValue`, `useClass`, or `useFactory`.

```ts
import { Test, TestingModule } from '@nestjs/testing';

describe('UsersService', () => {
  let service: UsersService;
  const usersRepository = { create: jest.fn() };
  const mailer = { sendWelcome: jest.fn() };

  beforeEach(async () => {
    const moduleRef: TestingModule = await Test.createTestingModule({
      providers: [
        UsersService,
        { provide: UsersRepository, useValue: usersRepository },
        { provide: MailerService, useValue: mailer },
      ],
    }).compile();

    service = moduleRef.get(UsersService);
  });

  it('creates a user and sends a welcome email', async () => {
    usersRepository.create.mockResolvedValue({ email: 'a@b.com' });

    await service.register('a@b.com');

    expect(usersRepository.create).toHaveBeenCalledWith({ email: 'a@b.com' });
    expect(mailer.sendWelcome).toHaveBeenCalledWith('a@b.com');
  });
});
```

Tests should isolate the component under verification.

---

## Performance

Avoid unnecessary request-scoped providers.

Review:

- provider lifetime;
- initialization cost;
- dependency graph.

Dependency Injection should not introduce avoidable overhead.

---

## Security

Inject security-related services through well-defined providers.

Examples:

- authentication;
- authorization;
- encryption;
- secret management.

Sensitive functionality should remain centralized.

---

## AI Execution Checklist

## Investigation

☐ Identify required dependencies.

☐ Review provider ownership.

☐ Review module boundaries.

☐ Review provider scope.

---

## Planning

☐ Use constructor injection.

☐ Register providers correctly.

☐ Centralize configuration.

☐ Minimize coupling.

---

## Verification

☐ Dependencies explicit.

☐ No manual instantiation.

☐ Providers independently testable.

☐ No circular dependencies.

☐ Appropriate provider scope selected.

☐ Architecture remains maintainable.

---

## Examples

**Good Example** — depend on a token, let the container decide the implementation

```ts
// orders/payment-gateway.ts — the contract the service depends on.
export const PAYMENT_GATEWAY = Symbol('PAYMENT_GATEWAY');

export interface PaymentGateway {
  charge(orderId: string, amountCents: number): Promise<{ reference: string }>;
}
```

```ts
@Injectable()
export class OrdersService {
  constructor(
    @Inject(PAYMENT_GATEWAY) private readonly payments: PaymentGateway,
    private readonly orders: OrdersRepository,
  ) {}

  async pay(orderId: string, amountCents: number): Promise<string> {
    const { reference } = await this.payments.charge(orderId, amountCents);
    await this.orders.markPaid(orderId, reference);
    return reference;
  }
}

// orders.module.ts — the binding lives here, so it can differ per environment.
@Module({
  providers: [
    OrdersService,
    OrdersRepository,
    { provide: PAYMENT_GATEWAY, useClass: StripeGateway },
  ],
})
export class OrdersModule {}
```

```ts
// The unit test swaps one binding; nothing else changes.
const moduleRef = await Test.createTestingModule({
  providers: [
    OrdersService,
    { provide: OrdersRepository, useValue: { markPaid: jest.fn() } },
    { provide: PAYMENT_GATEWAY, useValue: { charge: async () => ({ reference: 'ch_1' }) } },
  ],
}).compile();
```

**Bad Example** — construct dependencies by hand, then discover they cannot be replaced

```ts
@Injectable()
export class OrdersService {
  // Hard-wired: the concrete class, its constructor arguments, and its configuration
  // are now part of this file. A test cannot substitute it without network access.
  private readonly payments = new StripeGateway(process.env.STRIPE_KEY!);

  // A module-level singleton reintroduces shared mutable state the container exists
  // to manage, and it is initialised at import time — before configuration is loaded.
  private readonly cache = GlobalCache.instance;

  async pay(orderId: string, amountCents: number): Promise<string> {
    const { reference } = await this.payments.charge(orderId, amountCents);
    return reference;
  }
}
```

Marking a provider `Scope.REQUEST` to work around this makes it worse: request scope
propagates up the whole injection chain, so every consumer is re-instantiated per request.

---

## Common Mistakes

Avoid:

Creating dependencies with `new`.

Using property injection.

Making every provider request-scoped.

Creating circular dependencies.

Reading configuration directly from environment variables throughout the codebase.

Placing business logic inside provider factories.

Injecting unnecessary dependencies.

---

## Completion Criteria

Dependency Injection is implemented correctly when:

- dependencies are injected through constructors;
- providers remain focused and reusable;
- abstractions separate business logic from infrastructure;
- configuration is centralized;
- testing is simplified through dependency replacement;
- the dependency graph remains easy to understand.

---

## Summary

Dependency Injection is one of the core architectural strengths of NestJS.

By depending on abstractions, using constructor injection consistently, organizing providers within their owning modules, and keeping dependencies explicit, applications become more modular, testable, scalable, and easier to maintain.

## Related

- `knowledge/nestjs/02-modules.md`
- `knowledge/nestjs/05-services.md`
- `knowledge/nestjs/25-testing.md`
- `knowledge/nestjs/01-architecture.md`
