---
id: nestjs/18-transactions
topic: nestjs
slug: transactions
title: "NestJS Transactions"
type: doc
order: 18
status: ready
tags: [nestjs, transactions, InjectDataSource, Column, save, Injectable, PrimaryGeneratedColumn, transaction]
related: [nestjs/17-database, nestjs/06-repositories, databases/09-transactions, prisma/08-transactions]
when_to_use: "Read before writing or reviewing any operation that must update multiple pieces of state atomically."
---
# NestJS Transactions

## Purpose

This document defines the engineering standards for implementing transactions in NestJS applications.

The objective is to ensure that business operations modifying multiple pieces of state remain atomic, consistent, reliable, and recoverable.

Transactions protect business consistency.

They should never become the default solution for every operation.

---

## Core Principle

A transaction should represent one business operation.

Not one HTTP request.

---

## Transaction Goals

Every transaction should provide:

- atomicity;
- consistency;
- isolation;
- durability;
- predictable rollback behavior;
- minimal execution time.

Transactions should be as small as possible.

---

## Responsibilities

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

## Transaction Lifecycle

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

## ACID Principles

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

## Transaction Boundaries

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

The idiomatic tool is TypeORM's `DataSource`. The callback form of
`dataSource.transaction()` opens a transaction, hands you a scoped
`EntityManager`, commits when the callback resolves, and rolls back
automatically if it throws. Every write inside the boundary must go through
that `manager` — a plain injected `Repository` uses its own connection and
would **not** participate in the transaction.

Good — the boundary lives in the service, and every write uses the scoped
manager:

```ts
// orders.service.ts
import { Injectable } from '@nestjs/common';
import { InjectDataSource } from '@nestjs/typeorm';
import { DataSource } from 'typeorm';

import { OrderEntity } from './order.entity';
import { InventoryEntity } from './inventory.entity';
import { OutboxEntity } from './outbox.entity';
import { PlaceOrderDto } from './dto/place-order.dto';

export class InsufficientStockError extends Error {
  constructor(productId: string) {
    super(`Insufficient stock for product "${productId}"`);
    this.name = 'InsufficientStockError';
  }
}

@Injectable()
export class OrdersService {
  constructor(
    @InjectDataSource() private readonly dataSource: DataSource,
  ) {}

  async placeOrder(dto: PlaceOrderDto): Promise<string> {
    // Resolves -> COMMIT. Throws -> ROLLBACK. No manual commit/rollback needed.
    return this.dataSource.transaction(async (manager) => {
      // Pessimistic write lock: valid only inside a transaction. It blocks
      // concurrent buyers from overselling the same row.
      const stock = await manager.findOne(InventoryEntity, {
        where: { productId: dto.productId },
        lock: { mode: 'pessimistic_write' },
      });

      if (!stock || stock.available < dto.quantity) {
        // A business exception -> automatic rollback, DB left unchanged.
        throw new InsufficientStockError(dto.productId);
      }

      stock.available -= dto.quantity;
      await manager.save(stock);

      const order = manager.create(OrderEntity, {
        productId: dto.productId,
        quantity: dto.quantity,
        status: 'CONFIRMED',
      });
      await manager.save(order);

      // Outbox row committed atomically with the order (see Outbox Pattern).
      await manager.save(OutboxEntity, {
        type: 'order.placed',
        payload: { orderId: order.id },
      });

      return order.id;
    });
  }
}
```

Bad — the transaction is opened in a controller, spans a network call, and
leaks its connection because nothing releases the `QueryRunner` on failure:

```ts
// ❌ orders.controller.ts — do NOT do this
@Controller('orders')
export class OrdersController {
  constructor(
    @InjectDataSource() private readonly dataSource: DataSource,
    private readonly mailer: MailerService,
  ) {}

  @Post()
  async place(@Body() dto: PlaceOrderDto) {
    const runner = this.dataSource.createQueryRunner();
    await runner.connect();
    await runner.startTransaction();

    const order = await runner.manager.save(OrderEntity, dto);
    await this.mailer.sendConfirmation(order); // holds DB locks during I/O
    await runner.commitTransaction();          // a throw above never rolls back
    // runner.release() is never reached on error -> connection pool leak
    return order;
  }
}
```

---

## Unit of Work

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

## Idempotency

Retryable operations should be idempotent.

Examples:

- payment callbacks;
- webhook processing;
- retry queues.

Running the same transaction twice should not create duplicate business effects.

---

## External Services

Never keep a database transaction open while calling:

- payment providers;
- email services;
- cloud storage;
- REST APIs;
- message brokers.

External systems are not part of the database transaction.

Bad — the payment provider is called while the transaction (and its row locks)
is still open; a slow or failing provider holds locks and can exhaust the pool:

```ts
// ❌ external I/O inside the transaction boundary
await this.dataSource.transaction(async (manager) => {
  const order = await manager.save(OrderEntity, dto);
  await this.paymentApi.charge(order.total); // network call holds locks open
  order.status = 'PAID';
  await manager.save(order);
});
```

Good — the database work commits first, then the external call happens outside
the boundary; the external result is persisted in its own short transaction:

```ts
async payForOrder(dto: PlaceOrderDto): Promise<void> {
  const orderId = await this.dataSource.transaction(async (manager) => {
    const order = await manager.save(OrderEntity, { ...dto, status: 'PENDING' });
    return order.id;
  });

  // No DB locks held during the network call.
  const receipt = await this.paymentApi.charge(orderId);

  await this.dataSource.transaction(async (manager) => {
    await manager.update(OrderEntity, orderId, {
      status: 'PAID',
      receiptId: receipt.id,
    });
  });
}
```

---

## Outbox Pattern

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

The outbox row is written inside the same transaction as the state change (see
`OrdersService.placeOrder` above), so it is impossible to commit the business
data without also recording the intent to publish. A separate worker drains
unpublished rows and marks them sent:

```ts
// outbox.entity.ts
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
} from 'typeorm';

@Entity('outbox')
export class OutboxEntity {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  type: string;

  @Column({ type: 'jsonb' })
  payload: Record<string, unknown>;

  @Column({ type: 'timestamptz', nullable: true })
  publishedAt: Date | null;

  @CreateDateColumn()
  createdAt: Date;
}
```

```ts
// outbox.worker.ts
import { Injectable } from '@nestjs/common';
import { Cron } from '@nestjs/schedule';
import { InjectDataSource } from '@nestjs/typeorm';
import { DataSource, IsNull } from 'typeorm';

import { OutboxEntity } from './outbox.entity';

@Injectable()
export class OutboxWorker {
  constructor(
    @InjectDataSource() private readonly dataSource: DataSource,
    private readonly broker: MessageBroker,
  ) {}

  @Cron('*/5 * * * * *')
  async drain(): Promise<void> {
    const repo = this.dataSource.getRepository(OutboxEntity);
    const pending = await repo.find({
      where: { publishedAt: IsNull() },
      order: { createdAt: 'ASC' },
      take: 100,
    });

    for (const message of pending) {
      // Publish is idempotent on the consumer side (dedupe by message.id),
      // so re-delivery after a crash is safe.
      await this.broker.publish(message.type, message.payload);
      await repo.update(message.id, { publishedAt: new Date() });
    }
  }
}
```

---

## Saga Pattern

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

## Compensation

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

## Isolation Levels

Choose the weakest isolation level that satisfies business consistency.

Higher isolation increases contention.

Review:

- dirty reads;
- non-repeatable reads;
- phantom reads.

---

## Deadlocks

Deadlocks may occur when concurrent transactions lock resources differently.

Reduce deadlocks by:

- consistent locking order;
- short transactions;
- avoiding unnecessary locks.

Applications should retry retryable deadlocks when appropriate.

---

## Retry Strategy

Retry only transient failures.

Examples:

- deadlocks;
- temporary connection failures;
- serialization conflicts.

Do not retry business validation failures.

A retry helper inspects the driver error code and only retries genuinely
transient failures — serialization conflicts (`40001`) and deadlocks (`40P01`
on Postgres) — with a small backoff. Business exceptions like
`InsufficientStockError` are never caught here, so they surface immediately:

```ts
import { QueryFailedError } from 'typeorm';

const TRANSIENT_CODES = new Set(['40001', '40P01']); // serialization, deadlock

export async function withTransactionRetry<T>(
  fn: () => Promise<T>,
  maxAttempts = 3,
): Promise<T> {
  for (let attempt = 1; ; attempt++) {
    try {
      return await fn();
    } catch (err) {
      const code =
        err instanceof QueryFailedError
          ? (err.driverError as { code?: string }).code
          : undefined;

      if (!code || !TRANSIENT_CODES.has(code) || attempt >= maxAttempts) {
        throw err;
      }
      await new Promise((resolve) => setTimeout(resolve, 50 * attempt));
    }
  }
}
```

Usage — note the isolation level is passed as the first argument to
`transaction()`; the whole unit re-runs cleanly on a transient conflict because
a rolled-back transaction leaves no partial state:

```ts
async transfer(fromId: string, toId: string, amount: bigint): Promise<void> {
  await withTransactionRetry(() =>
    this.dataSource.transaction('SERIALIZABLE', async (manager) => {
      const from = await manager.findOneByOrFail(AccountEntity, { id: fromId });
      const to = await manager.findOneByOrFail(AccountEntity, { id: toId });

      from.balance = (BigInt(from.balance) - amount).toString();
      to.balance = (BigInt(to.balance) + amount).toString();

      await manager.save([from, to]);
    }),
  );
}
```

---

## Long Transactions

Avoid transactions containing:

- file uploads;
- network calls;
- user interaction;
- expensive calculations.

Transactions should finish quickly.

---

## Nested Transactions

Avoid unnecessary nested transactions.

Prefer one clearly defined transaction boundary.

---

## Optimistic vs Pessimistic Locking

Optimistic locking:

Suitable when conflicts are rare.

Pessimistic locking:

Suitable when conflicts are expensive.

Choose according to business requirements.

Optimistic locking with TypeORM uses a `@VersionColumn`. TypeORM adds the
loaded version to the `WHERE` clause on update and throws
`OptimisticLockVersionMismatchError` when another transaction changed the row
first — no locks are held between read and write:

```ts
// account.entity.ts
import { Entity, PrimaryGeneratedColumn, Column, VersionColumn } from 'typeorm';

@Entity('accounts')
export class AccountEntity {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'bigint' })
  balance: string;

  @VersionColumn()
  version: number; // incremented automatically on every save()
}
```

```ts
// accounts.service.ts
import { ConflictException, Injectable } from '@nestjs/common';
import { InjectDataSource } from '@nestjs/typeorm';
import { DataSource, OptimisticLockVersionMismatchError } from 'typeorm';

import { AccountEntity } from './account.entity';

@Injectable()
export class AccountsService {
  constructor(@InjectDataSource() private readonly dataSource: DataSource) {}

  async debit(id: string, amount: bigint): Promise<void> {
    try {
      await this.dataSource.transaction(async (manager) => {
        const account = await manager.findOneByOrFail(AccountEntity, { id });
        account.balance = (BigInt(account.balance) - amount).toString();
        // save() emits: UPDATE ... SET balance=?, version=version+1
        //               WHERE id=? AND version=? -> throws if 0 rows matched.
        await manager.save(account);
      });
    } catch (err) {
      if (err instanceof OptimisticLockVersionMismatchError) {
        throw new ConflictException('Account was modified concurrently; retry.');
      }
      throw err;
    }
  }
}
```

The `pessimistic_write` lock shown in `OrdersService.placeOrder` is the
opposite trade-off: it blocks competing writers up front instead of failing
late, which fits high-contention rows like inventory counters.

---

## Event Consistency

Business events should represent committed state.

Never publish events before a successful commit.

---

## Error Handling

Rollback should occur automatically on unrecoverable failures.

Business exceptions should leave the database unchanged.

---

## Observability

Monitor:

- transaction duration;
- rollback frequency;
- deadlocks;
- lock contention;
- retry count.

Long-running transactions should be investigated.

---

## Performance

Review:

- transaction duration;
- locked rows;
- query count;
- blocking operations.

Transactions should remain lightweight.

---

## Security

Transactions do not replace authorization.

Validate permissions before beginning transactional work whenever practical.

---

## Testing

Verify:

- successful commit;
- rollback behavior;
- concurrent execution;
- retry logic;
- idempotency;
- compensation workflows.

Transaction behavior should remain deterministic.

---

## AI Decision Matrix

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

## AI Execution Checklist

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

## Examples

**Good Example** — one transaction per use case, side effects after commit

```ts
@Injectable()
export class OrdersService {
  constructor(
    private readonly dataSource: DataSource,
    private readonly events: EventEmitter2,
  ) {}

  async place(command: PlaceOrder): Promise<Order> {
    // The unit of work is the business operation, not each repository call.
    const order = await this.dataSource.transaction('READ COMMITTED', async (manager) => {
      // Every write inside uses THIS manager, or it runs outside the transaction.
      const stock = await manager.findOne(StockEntity, {
        where: { sku: command.sku },
        lock: { mode: 'pessimistic_write' },   // serialise concurrent buyers
      });

      if (!stock || stock.available < command.quantity) {
        throw new OutOfStockError(command.sku);   // rolls back automatically
      }

      stock.available -= command.quantity;
      await manager.save(stock);

      return manager.save(OrderEntity, {
        userId: command.userId,
        sku: command.sku,
        quantity: command.quantity,
      });
    });

    // Outside the transaction: an email cannot be rolled back, and holding the
    // transaction open across a network call is how connection pools run dry.
    this.events.emit('order.placed', new OrderPlacedEvent(order.id));

    return order;
  }
}
```

**Bad Example** — a transaction that does not cover the writes, and I/O inside it

```ts
@Injectable()
export class OrdersService {
  async place(command: PlaceOrder) {
    return this.dataSource.transaction(async (manager) => {
      // Uses the global repository, not `manager`: this write is on a DIFFERENT
      // connection and is NOT part of the transaction. A rollback leaves it behind.
      await this.stockRepo.decrement({ sku: command.sku }, 'available', command.quantity);

      const order = await manager.save(OrderEntity, { sku: command.sku });

      // A network call with the transaction open: the row locks are held for the
      // full round trip, and a slow provider stalls every other writer.
      await this.stripe.charges.create({ amount: command.amountCents, currency: 'eur' });

      // An email inside the transaction: if the commit fails afterwards, the
      // customer has been told about an order that does not exist.
      await this.mailer.sendMail({ to: command.email, subject: 'Order confirmed' });

      return order;
    });
  }
}
```

---

## Common Mistakes

Avoid:

Opening transactions inside controllers.

Keeping transactions open during HTTP requests.

Sending emails before commit.

Publishing events before commit.

Creating long-running transactions.

Ignoring idempotency.

Retrying business validation errors.

---

## Completion Criteria

A transactional workflow is complete when:

- business consistency is preserved;
- transaction boundaries are well defined;
- transactions remain short;
- rollback behavior is predictable;
- external systems are coordinated safely;
- transaction behavior is fully tested.

---

## Summary

Transactions preserve business consistency across multiple persistence operations.

By keeping transactions short, defining clear boundaries, separating external integrations through patterns such as Outbox and Saga, and designing for idempotency and concurrency, NestJS applications remain reliable under real-world production workloads.

## Related

- `knowledge/nestjs/17-database.md`
- `knowledge/nestjs/06-repositories.md`
- `knowledge/databases/09-transactions.md`
- `knowledge/prisma/08-transactions.md`
