---
id: nestjs/23-distributed-systems
topic: nestjs
slug: distributed-systems
title: "Distributed Systems"
type: doc
order: 23
status: ready
tags: [nestjs, distributed-systems]
related: []
when_to_use: "Read before designing or reviewing microservices, inter-service communication, or other distributed-system concerns."
---
# Distributed Systems

## Purpose

This document defines the engineering standards for designing distributed systems using NestJS and related technologies.

The objective is to build scalable, resilient, observable, and maintainable systems by applying proven distributed system patterns rather than relying on framework-specific features.

Distributed systems solve scaling and organizational problems.

They also introduce complexity.

Use them only when justified.

---

## Core Principle

A distributed system should behave predictably even when individual components fail.

Failures are expected.

Design for them.

---

## Goals

Distributed systems should provide:

- scalability;
- fault tolerance;
- resilience;
- observability;
- loose coupling;
- independent deployment.

Every additional service increases operational complexity.

---

## Architecture

Typical topology:

```
             Client

                │

          API Gateway

        ┌───────┴────────┐

        │                │

 Service A          Service B

        │                │

        └───────┬────────┘

                │

          Event Broker

                │

        Background Workers
```

Services communicate through well-defined contracts.

---

## Service Boundaries

Split services by business capability.

Examples:

- Identity
- Billing
- Orders
- Notifications
- Inventory

Never split services by database tables.

---

## Synchronous Communication

Examples:

- REST
- GraphQL
- gRPC

Advantages:

- simple
- immediate response
- request tracing

Disadvantages:

- higher coupling
- cascading failures
- increased latency

NestJS exposes request/response messaging through `@nestjs/microservices`. The
caller registers a `ClientProxy`; the callee handles a message pattern. The same
DI container wires both sides, so transports (TCP, NATS, Redis, gRPC, Kafka) stay
swappable without touching business logic.

Register the client (caller side):

```typescript
// clients.module.ts
import { Module } from '@nestjs/common';
import { ClientsModule, Transport } from '@nestjs/microservices';

@Module({
  imports: [
    ClientsModule.register([
      {
        name: 'BILLING_SERVICE',
        transport: Transport.TCP,
        options: { host: 'billing', port: 4001 },
      },
    ]),
  ],
  exports: [ClientsModule],
})
export class ClientsConfigModule {}
```

Call it. `send()` returns a cold `Observable`, so **every** remote call is wrapped
in `timeout` (never wait forever) and a bounded `retry` with exponential backoff
plus jitter. A `catchError` translates a hard failure into a domain-level error
the caller can reason about — this is the concrete shape of the timeout, retry,
and circuit-breaker sections below:

```typescript
// orders.service.ts
import {
  Inject,
  Injectable,
  ServiceUnavailableException,
} from '@nestjs/common';
import { ClientProxy } from '@nestjs/microservices';
import {
  catchError,
  firstValueFrom,
  retry,
  throwError,
  timeout,
  timer,
  TimeoutError,
} from 'rxjs';

interface ChargeResult {
  transactionId: string;
}

@Injectable()
export class OrdersService {
  constructor(
    @Inject('BILLING_SERVICE') private readonly billing: ClientProxy,
  ) {}

  async charge(orderId: string, amountCents: number): Promise<ChargeResult> {
    return firstValueFrom(
      this.billing
        .send<ChargeResult>({ cmd: 'charge' }, { orderId, amountCents })
        .pipe(
          timeout(3000),
          // Retry only transient failures; cap attempts and back off with jitter.
          retry({
            count: 2,
            delay: (_error, retryCount) =>
              timer(Math.min(2000, 200 * 2 ** retryCount) + Math.random() * 100),
          }),
          catchError((error: unknown) =>
            throwError(() =>
              error instanceof TimeoutError
                ? new ServiceUnavailableException('Billing service timed out')
                : error,
            ),
          ),
        ),
    );
  }
}
```

Handle the pattern on the callee. The handler must be idempotent because the
caller retries — the same `orderId` may arrive more than once:

```typescript
// billing.controller.ts
import { Controller } from '@nestjs/common';
import { MessagePattern, Payload } from '@nestjs/microservices';

interface ChargeRequest {
  orderId: string;
  amountCents: number;
}

@Controller()
export class BillingController {
  @MessagePattern({ cmd: 'charge' })
  async charge(@Payload() data: ChargeRequest): Promise<{ transactionId: string }> {
    // Deduplicate on data.orderId before charging, then return the result.
    return { transactionId: `txn_${data.orderId}` };
  }
}
```

Boot the callee as a microservice so it listens on the transport:

```typescript
// main.ts (billing service)
import { NestFactory } from '@nestjs/core';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.createMicroservice<MicroserviceOptions>(
    AppModule,
    { transport: Transport.TCP, options: { host: '0.0.0.0', port: 4001 } },
  );
  await app.listen();
}
void bootstrap();
```

Bad — an unbounded `await` on a remote call. One slow dependency ties up the
request thread pool and cascades the outage upstream:

```typescript
// No timeout, no retry, no fallback — the caller hangs until TCP gives up.
const result = await firstValueFrom(
  this.billing.send<ChargeResult>({ cmd: 'charge' }, { orderId, amountCents }),
);
```

---

## Asynchronous Communication

Examples:

- Kafka
- RabbitMQ
- SQS
- Pub/Sub

Advantages:

- loose coupling
- resilience
- scalability

Disadvantages:

- eventual consistency
- operational complexity

In NestJS, `ClientProxy.emit()` publishes an event and does **not** wait for a
consumer — the publisher's flow is decoupled from every subscriber. Publish the
event only after the local business state is committed, so subscribers never
observe an event for work that later rolls back:

```typescript
// order-publisher.service.ts
import { Inject, Injectable } from '@nestjs/common';
import { ClientProxy } from '@nestjs/microservices';

interface OrderCreatedEvent {
  orderId: string;
  userId: string;
  correlationId: string;
}

@Injectable()
export class OrderPublisher {
  constructor(@Inject('EVENTS_BROKER') private readonly events: ClientProxy) {}

  // Call this AFTER the order transaction has committed.
  publishOrderCreated(payload: OrderCreatedEvent): void {
    this.events.emit('order.created', payload);
  }
}
```

Subscribe with `@EventPattern`. Event handlers must be idempotent — most brokers
guarantee at-least-once delivery, so the same event can arrive twice:

```typescript
// notifications.controller.ts
import { Controller } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';

interface OrderCreatedEvent {
  orderId: string;
  userId: string;
  correlationId: string;
}

@Controller()
export class NotificationsController {
  @EventPattern('order.created')
  async handleOrderCreated(@Payload() event: OrderCreatedEvent): Promise<void> {
    // Guard on event.orderId so a redelivery does not send a second email.
    await this.sendConfirmation(event.userId, event.orderId);
  }

  private async sendConfirmation(userId: string, orderId: string): Promise<void> {
    // ...
  }
}
```

---

## API Gateway

Gateway responsibilities:

- routing;
- authentication;
- rate limiting;
- request aggregation;
- observability.

Business logic should remain inside services.

---

## Backend For Frontend (BFF)

Different clients may require different APIs.

Example:

```
Mobile

↓

Mobile BFF

──────────────

Web

↓

Web BFF
```

Avoid forcing every client through identical APIs.

---

## Service Discovery

Services should locate each other dynamically when infrastructure requires it.

Avoid hardcoding service addresses.

---

## Circuit Breaker

Protect services from cascading failures.

```
Failure

↓

Threshold Reached

↓

Circuit Open

↓

Fast Failure

↓

Recovery Test

↓

Circuit Closed
```

---

## Timeout

Every remote call should define a timeout.

Never wait indefinitely.

---

## Retry

Retry only transient failures.

Combine retries with:

- exponential backoff;
- jitter;
- retry limits.

---

## Bulkhead

Isolate resources.

Failure in one subsystem should not exhaust the entire application.

---

## Saga Pattern

Coordinate distributed business workflows.

```
Reserve Inventory

↓

Charge Payment

↓

Create Shipment

↓

Notify Customer
```

Failures require compensation.

---

## Eventual Consistency

Distributed systems cannot guarantee immediate consistency everywhere.

Applications should tolerate temporary inconsistency.

---

## Contracts

Service contracts should be:

- versioned;
- documented;
- backward compatible.

Breaking changes require migration strategies.

---

## Correlation ID

Every request should propagate the same correlation ID across services.

Tracing should span the entire request lifecycle.

A functional middleware reuses an inbound correlation ID or mints one, stores it
on the request, and echoes it on the response. Register it globally in `main.ts`
so it runs before every route — a functional middleware avoids the wildcard
route-pattern differences between NestJS 10 and 11:

```typescript
// correlation-id.middleware.ts
import { randomUUID } from 'node:crypto';
import type { NextFunction, Request, Response } from 'express';

export const CORRELATION_ID_HEADER = 'x-correlation-id';

export function correlationIdMiddleware(
  req: Request,
  res: Response,
  next: NextFunction,
): void {
  const incoming = req.headers[CORRELATION_ID_HEADER];
  const correlationId =
    (Array.isArray(incoming) ? incoming[0] : incoming) ?? randomUUID();

  req.headers[CORRELATION_ID_HEADER] = correlationId;
  res.setHeader(CORRELATION_ID_HEADER, correlationId);
  next();
}
```

```typescript
// main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { correlationIdMiddleware } from './correlation-id.middleware';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.use(correlationIdMiddleware);
  await app.listen(3000);
}
void bootstrap();
```

Forward the same `x-correlation-id` on every outbound HTTP call and include it in
each emitted event payload so one trace spans the entire request lifecycle.

---

## Observability

Monitor:

- latency;
- failures;
- retries;
- queue depth;
- service health;
- dependency failures.

Distributed systems require centralized observability.

---

## Health Checks

Expose health endpoints.

Verify:

- database;
- cache;
- queues;
- external dependencies.

Health checks should reflect real readiness.

---

## Security

Every service should:

- authenticate requests;
- authorize operations;
- validate input;
- encrypt communication.

Never trust internal traffic automatically.

Apply Zero Trust principles.

---

## Performance

Measure:

- network latency;
- serialization cost;
- request fan-out;
- queue delays.

Optimize based on measurements.

---

## Testing

Verify:

- service contracts;
- failure scenarios;
- retries;
- timeouts;
- compensation;
- network partitions.

Distributed systems should be tested under failure conditions.

---

## AI Decision Matrix

Use distributed architecture when:

✓ Independent scaling required

✓ Multiple teams

✓ Complex domains

✓ High availability requirements

Avoid when:

✗ Small applications

✗ Simple CRUD

✗ Limited operational capacity

✗ Monolithic architecture is sufficient

---

## AI Execution Checklist

## Investigation

☐ Identify service boundaries.

☐ Review communication patterns.

☐ Review consistency requirements.

☐ Review operational complexity.

---

## Planning

☐ Define contracts.

☐ Configure retries.

☐ Configure timeouts.

☐ Plan observability.

---

## Verification

☐ Service boundaries justified.

☐ Contracts versioned.

☐ Circuit breakers implemented.

☐ Correlation IDs propagated.

☐ Health checks available.

☐ Failure scenarios tested.

---

## Common Mistakes

Avoid:

Splitting services too early.

Sharing databases.

Ignoring retries.

Ignoring timeouts.

Ignoring observability.

Treating the network as reliable.

Creating synchronous dependency chains.

---

## Completion Criteria

A distributed architecture is complete when:

- service boundaries are business-driven;
- communication contracts are stable;
- failures are handled predictably;
- observability is comprehensive;
- resilience patterns are implemented;
- operational complexity is justified.

---

## Summary

Distributed systems enable independent scaling, resilience, and organizational flexibility.

By defining clear service boundaries, applying resilience patterns, embracing eventual consistency, and investing in observability, engineering teams can build reliable production systems that continue operating despite partial failures.