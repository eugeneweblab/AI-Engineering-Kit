---
id: nestjs/17-database
topic: nestjs
slug: database
title: "NestJS Database"
type: doc
order: 17
status: ready
tags: [nestjs, database, Injectable, IsInt, InjectRepository, Column, InjectDataSource]
applies_to: [typeorm]
related: [nestjs/06-repositories, nestjs/18-transactions, prisma/02-schema, databases/07-indexing]
when_to_use: "Read before integrating or reviewing database access, ORM setup, entities, or migrations in a NestJS application."
---
# NestJS Database

## Purpose

This document defines the engineering standards for integrating databases into NestJS applications.

The objective is to build reliable, scalable, and maintainable persistence layers while keeping business logic independent from database implementation details.

The database stores application state.

Business logic remains inside services.

---

## Core Principle

Treat the database as infrastructure.

Application architecture should not depend on a specific ORM or database engine.

---

## Database Goals

Every persistence layer should provide:

- data consistency;
- predictable performance;
- scalability;
- maintainability;
- observability;
- portability where practical.

Database code should remain isolated behind repositories.

---

## Architecture

Typical flow:

```
Controller

↓

Service

↓

Repository

↓

ORM / Query Builder

↓

Database
```

Business logic should never bypass repositories.

---

## Database Technologies

NestJS supports many persistence technologies.

Common choices include:

- PostgreSQL
- MySQL
- MariaDB
- SQL Server
- SQLite
- MongoDB
- Redis (for caching)
- Elasticsearch / OpenSearch (for search)

Technology selection should follow business requirements rather than framework preference.

---

## ORM Selection

Common options:

### Prisma

Strengths:

- excellent TypeScript support;
- generated client;
- simple migrations;
- strong developer experience.

Best suited for:

- modern TypeScript projects;
- greenfield development;
- API-first applications.

---

### TypeORM

Strengths:

- mature ecosystem;
- decorators;
- Active Record and Data Mapper support;
- extensive enterprise adoption.

Best suited for:

- legacy systems;
- applications already using TypeORM;
- teams requiring advanced ORM customization.

---

### Drizzle ORM

Strengths:

- SQL-first philosophy;
- lightweight;
- excellent type safety;
- predictable generated SQL.

Best suited for:

- teams preferring explicit SQL;
- performance-sensitive applications.

---

Choose an ORM based on project requirements rather than popularity.

---

## Repository Pattern

Repositories isolate persistence.

Services should communicate only with repositories.

Repositories should never contain business workflows.

Wire up the entity, register it with the feature module, and inject the repository into the service. The service holds business logic; the repository only persists.

```ts
// user.entity.ts
import {
  Column,
  CreateDateColumn,
  Entity,
  Index,
  PrimaryGeneratedColumn,
} from 'typeorm';

@Entity('users')
export class User {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Index({ unique: true })
  @Column({ type: 'varchar', length: 320 })
  email!: string;

  @Column({ type: 'varchar', length: 200 })
  name!: string;

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt!: Date;
}
```

```ts
// users.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from './user.entity';
import { UsersService } from './users.service';
import { UsersController } from './users.controller';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}
```

```ts
// ✅ Good — service depends on the injected repository, not on the ORM globally
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './user.entity';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly users: Repository<User>,
  ) {}

  async findById(id: string): Promise<User> {
    const user = await this.users.findOne({ where: { id } });
    if (!user) {
      throw new NotFoundException(`User ${id} not found`);
    }
    return user;
  }

  async create(email: string, name: string): Promise<User> {
    const user = this.users.create({ email, name });
    return this.users.save(user);
  }
}
```

```ts
// ❌ Bad — controller reads the ORM directly, bypassing the service and repository
@Controller('users')
export class UsersController {
  constructor(private readonly dataSource: DataSource) {}

  @Get(':id')
  findOne(@Param('id') id: string) {
    // Persistence detail leaks into transport; nothing is reusable or testable.
    return this.dataSource.getRepository(User).findOneBy({ id });
  }
}
```

---

## Migrations

All schema changes should be versioned.

Migration rules:

- deterministic;
- reversible when possible;
- reviewed;
- committed to source control.

Never modify production schemas manually.

---

## Transactions

Use transactions only when multiple operations must succeed or fail together.

Transactions should remain:

- short;
- atomic;
- isolated;
- consistent.

Avoid long-running transactions.

Use the injected `DataSource` to run a transaction. `dataSource.transaction` acquires a connection, commits on success, and rolls back if the callback throws. Do all writes through the supplied `EntityManager` so they share the same transaction.

```ts
// transfers.service.ts
import { Injectable, BadRequestException } from '@nestjs/common';
import { InjectDataSource } from '@nestjs/typeorm';
import { DataSource } from 'typeorm';
import { Account } from './account.entity';

@Injectable()
export class TransfersService {
  constructor(
    @InjectDataSource()
    private readonly dataSource: DataSource,
  ) {}

  async transfer(fromId: string, toId: string, amount: number): Promise<void> {
    await this.dataSource.transaction(async (manager) => {
      // Pessimistic write lock prevents concurrent transfers on the same row.
      const from = await manager.findOne(Account, {
        where: { id: fromId },
        lock: { mode: 'pessimistic_write' },
      });

      if (!from || from.balance < amount) {
        // Throwing rolls the whole transaction back atomically.
        throw new BadRequestException('Insufficient funds');
      }

      await manager.decrement(Account, { id: fromId }, 'balance', amount);
      await manager.increment(Account, { id: toId }, 'balance', amount);
    });
  }
}
```

---

## Locking

Choose an appropriate locking strategy.

Optimistic locking:

Suitable for:

- low contention;
- collaborative editing.

Pessimistic locking:

Suitable for:

- financial systems;
- inventory management;
- high-contention resources.

Select the least restrictive strategy that guarantees consistency.

---

## Indexing

Indexes should support:

- primary lookups;
- foreign keys;
- filtering;
- sorting;
- unique constraints.

Avoid unnecessary indexes.

Every index increases write cost.

---

## Query Design

Queries should be:

- explicit;
- efficient;
- parameterized;
- explainable.

Avoid unnecessary complexity.

---

## N+1 Queries

Prevent repeated database access.

Bad:

```
Load users

↓

Load orders for each user

↓

1001 queries
```

Better:

```
Load users

↓

Load orders using JOIN or batching

↓

2 queries
```

Always review generated SQL.

```ts
// ❌ Bad — one extra query per user (the N+1 problem)
async listWithOrders(): Promise<User[]> {
  const users = await this.users.find();
  for (const user of users) {
    // Fires a separate SELECT for every single user.
    user.orders = await this.orders.find({ where: { userId: user.id } });
  }
  return users;
}
```

```ts
// ✅ Good — a single joined query loads users and their orders together
async listWithOrders(): Promise<User[]> {
  return this.users
    .createQueryBuilder('user')
    .leftJoinAndSelect('user.orders', 'order')
    .getMany();
}

// ✅ Also good — declarative relation loading, resolved in one round trip
async listWithOrdersRelations(): Promise<User[]> {
  return this.users.find({ relations: { orders: true } });
}
```

---

## Pagination

Never return unbounded collections.

Support:

- offset pagination;
- cursor pagination;
- sorting;
- filtering.

Large datasets should always be paginated.

Validate and bound the page parameters with a DTO, then translate them into `skip`/`take`. Return the total count so clients can render pagination.

```ts
// pagination-query.dto.ts
import { Type } from 'class-transformer';
import { IsInt, Max, Min } from 'class-validator';

export class PaginationQueryDto {
  @Type(() => Number)
  @IsInt()
  @Min(1)
  page = 1;

  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(100) // Hard upper bound so a client can never request an unbounded page.
  limit = 20;
}
```

```ts
// users.service.ts (excerpt)
async paginate(
  query: PaginationQueryDto,
): Promise<{ data: User[]; total: number }> {
  const [data, total] = await this.users.findAndCount({
    skip: (query.page - 1) * query.limit,
    take: query.limit,
    order: { createdAt: 'DESC' },
  });
  return { data, total };
}
```

The DTO requires `ValidationPipe` with transform enabled (typically `app.useGlobalPipes(new ValidationPipe({ transform: true, whitelist: true }))`) so query strings are coerced to numbers and bounded before they reach the repository.

---

## Bulk Operations

Prefer bulk operations when processing many records.

Examples:

- insertMany;
- updateMany;
- deleteMany.

Avoid unnecessary loops performing one query per record.

---

## Soft Deletes

Soft deletes should:

- preserve audit history;
- hide deleted records by default;
- support restoration when required.

Use only when business requirements justify additional complexity.

---

## Read and Write Separation

Large applications may separate:

```
Writes

↓

Primary Database

↓

Replication

↓

Read Replicas

↓

Reads
```

Services should remain unaware of replication topology.

---

## Connection Pooling

Configure connection pools appropriately.

Avoid:

- excessive connections;
- connection leaks;
- unnecessary reconnects.

Connection management should remain transparent to business logic.

---

## Database Constraints

Prefer enforcing integrity inside the database.

Examples:

- primary keys;
- foreign keys;
- unique constraints;
- check constraints.

Database constraints complement—not replace—business validation.

---

## Raw SQL

Use raw SQL only when necessary.

Examples:

- advanced reporting;
- complex analytics;
- database-specific optimizations.

Encapsulate raw SQL inside repositories.

Never concatenate user input into SQL.

---

## Observability

Monitor:

- slow queries;
- transaction duration;
- connection usage;
- deadlocks;
- lock contention;
- query frequency.

Database behavior should be measurable.

---

## Performance

Review:

- indexes;
- execution plans;
- query count;
- data transfer volume;
- unnecessary eager loading.

Optimize based on measurements—not assumptions.

---

## Security

Always:

- use parameterized queries;
- enforce least privilege for database users;
- encrypt sensitive data when appropriate;
- avoid exposing internal identifiers unnecessarily.

Never trust user input.

---

## Testing

Test:

- migrations;
- repository behavior;
- transactions;
- concurrency scenarios;
- rollback behavior.

Use realistic datasets whenever practical.

---

## AI Decision Matrix

Use the database for:

✓ Persistent application state

✓ Transactions

✓ Relationships

✓ Querying

✓ Constraints

Do **not** use the database for:

✗ Application configuration

✗ Temporary request state

✗ In-memory caching

✗ Business workflows

---

## AI Execution Checklist

## Investigation

☐ Review data model.

☐ Review consistency requirements.

☐ Review expected workload.

☐ Review scalability requirements.

---

## Planning

☐ Design repositories.

☐ Optimize indexes.

☐ Define transactions.

☐ Plan migrations.

---

## Verification

☐ No N+1 queries.

☐ Queries parameterized.

☐ Pagination implemented.

☐ Transactions minimal.

☐ Constraints enforced.

☐ Repository independently testable.

---

## Examples

**Good Example** — explicit relations, bounded reads, migrations under review

```ts
@Injectable()
export class OrdersRepository {
  constructor(
    @InjectRepository(OrderEntity) private readonly repo: Repository<OrderEntity>,
  ) {}

  // One query loads the orders and their items. Selecting explicit columns keeps
  // the row size — and the cache footprint — predictable.
  async recentWithItems(userId: string, limit = 20): Promise<OrderEntity[]> {
    return this.repo.find({
      where: { userId },
      relations: { items: true },
      select: { id: true, status: true, totalCents: true, createdAt: true },
      order: { createdAt: 'DESC' },
      take: limit,
    });
  }
}
```

```ts
// Migrations are generated, reviewed, and committed — never synchronised at boot.
// CONCURRENTLY keeps the write path unblocked while the index builds — but Postgres
// refuses it inside a transaction block, and TypeORM wraps migrations in one by
// default. Run this migration with transactions off:
//
//   typeorm migration:run -t none
//
// or set `migrationsTransactionMode: 'none'` on the DataSource. Because the setting
// is per-run and not per-migration, keep index builds in their own migration,
// separate from schema changes that do need a transaction.
export class AddOrderStatusIndex1735689600000 implements MigrationInterface {
  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(
      `CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_created
       ON orders (user_id, created_at DESC)`,
    );
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`DROP INDEX CONCURRENTLY IF EXISTS idx_orders_user_created`);
  }
}
```

On a small table a plain `CREATE INDEX` inside the normal transactional migration is the
simpler choice; `CONCURRENTLY` earns its extra handling only when the table is large enough
that an `ACCESS EXCLUSIVE` lock would be an outage.

**Bad Example** — schema synchronised at boot, N+1 on every list

```ts
TypeOrmModule.forRoot({
  type: 'postgres',
  url: process.env.DATABASE_URL,
  autoLoadEntities: true,
  // Rewrites the production schema to match the entities on every deploy.
  // A renamed property drops the column — and the data in it.
  synchronize: true,
  logging: true,          // every query to stdout, in production
});
```

```ts
@Injectable()
export class OrdersService {
  async listWithItems(userId: string) {
    const orders = await this.repo.find({ where: { userId } });   // unbounded

    // One query per order, then one per customer: 2N+1 round trips, and the
    // number grows with the user's history rather than staying constant.
    for (const order of orders) {
      order.items = await this.itemRepo.find({ where: { orderId: order.id } });
      order.customer = await this.userRepo.findOne({ where: { id: order.userId } });
    }

    return orders;
  }
}
```

---

## Common Mistakes

Avoid:

Putting business logic inside repositories.

Skipping indexes.

Returning unlimited collections.

Ignoring transaction boundaries.

Using one query per record.

Writing raw SQL everywhere.

Reading directly from ORM inside controllers.

Keeping long-running transactions open.

---

## Completion Criteria

Database integration is complete when:

- persistence is isolated behind repositories;
- schema changes are versioned;
- transactions are minimal and reliable;
- queries are optimized;
- observability is in place;
- performance and security have been reviewed.

---

## Summary

The database is one of the most critical infrastructure components of a NestJS application.

By isolating persistence behind repositories, designing efficient queries, enforcing constraints, minimizing transactions, and continuously monitoring performance, applications remain scalable, reliable, and maintainable as they grow.

## Related

- `knowledge/nestjs/06-repositories.md`
- `knowledge/nestjs/18-transactions.md`
- `knowledge/prisma/02-schema.md`
- `knowledge/databases/07-indexing.md`
