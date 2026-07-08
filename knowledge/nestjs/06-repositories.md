---
id: nestjs/06-repositories
topic: nestjs
slug: repositories
title: "NestJS Repositories"
type: doc
order: 6
status: ready
tags: [nestjs, repositories]
related: []
when_to_use: "Read before writing or reviewing any data-access or repository layer that reads from or writes to persistent storage."
---
# NestJS Repositories

## Purpose

This document defines the engineering standards for implementing repositories in NestJS applications.

The objective is to isolate persistence concerns from business logic, making data access consistent, testable, and replaceable. Repositories should act as the application's gateway to persistent storage without exposing database implementation details to higher layers.

Repositories are responsible for persistence—not business decisions.

---

## Core Principle

Repositories persist data.

Services implement business logic.

Never mix these responsibilities.

**Bad — the repository hashes passwords, enforces rules, and sends email:**

```ts
@Injectable()
export class UserRepository {
  constructor(
    @InjectRepository(UserEntity)
    private readonly repo: Repository<UserEntity>,
    private readonly mailer: MailerService,
  ) {}

  async register(email: string, password: string): Promise<UserEntity> {
    if (await this.repo.findOne({ where: { email } })) {
      throw new ConflictException('Email taken'); // HTTP concern in persistence
    }
    const passwordHash = await bcrypt.hash(password, 12); // business rule
    const user = await this.repo.save(this.repo.create({ email, passwordHash }));
    await this.mailer.sendWelcome(email); // side effect that is not persistence
    return user; // leaks the raw ORM entity, including passwordHash
  }
}
```

**Good — the service orchestrates; the repository only persists:**

```ts
@Injectable()
export class UsersService {
  constructor(
    @Inject(USER_REPOSITORY) private readonly users: UserRepository,
    private readonly mailer: MailerService,
  ) {}

  async register(email: string, password: string): Promise<User> {
    if (await this.users.findByEmail(email)) {
      throw new ConflictException('Email taken');
    }
    const passwordHash = await bcrypt.hash(password, 12);
    const user = await this.users.create({ email, passwordHash });
    await this.mailer.sendWelcome(user.email);
    return user;
  }
}
```

---

## Repository Goals

Every repository should provide:

- encapsulated data access;
- predictable interfaces;
- reusable queries;
- database abstraction;
- efficient persistence;
- transaction compatibility.

Repositories should remain focused on storage concerns.

---

## Responsibilities

Repositories are responsible for:

- creating records;
- retrieving records;
- updating records;
- deleting records;
- executing queries;
- handling transactions delegated by services.

Repositories should not:

- implement business rules;
- send emails;
- call external APIs;
- perform authorization;
- coordinate workflows.

---

## Repository Position

Typical flow:

```
Controller

↓

Service

↓

Repository

↓

Database
```

Repositories should never be called directly by controllers.

---

## Repository Structure

Example:

```
users/

    users.repository.ts

    users.service.ts

    users.controller.ts
```

One repository should generally correspond to one aggregate or business entity.

---

## Repository Interface

Expose business-oriented methods.

Good examples:

```
findById()

findByEmail()

findActiveUsers()

create()

update()

delete()
```

Avoid exposing generic ORM methods directly.

Bad examples:

```
query()

execute()

raw()

runSql()
```

Repositories should express intent.

### Worked example: a port + a TypeORM implementation

Define the repository as an interface (a *port*) owned by the domain, plus a token
so Nest can inject it. Higher layers depend on the interface, never on TypeORM.

```ts
// user.model.ts — the domain object returned to services (no ORM types)
export interface User {
  id: string;
  email: string;
  isActive: boolean;
  createdAt: Date;
}

export interface CreateUserData {
  email: string;
  passwordHash: string;
}

export interface PageQuery {
  page: number; // 1-based
  size: number;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}
```

```ts
// user.repository.ts — the port and its injection token
export const USER_REPOSITORY = Symbol('USER_REPOSITORY');

export interface UserRepository {
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  findActiveUsers(query: PageQuery): Promise<Page<User>>;
  create(data: CreateUserData): Promise<User>;
  update(id: string, changes: Partial<CreateUserData>): Promise<User>;
  softDelete(id: string): Promise<void>;
}
```

```ts
// user.entity.ts — the persistence model; stays inside the repository layer
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  DeleteDateColumn,
} from 'typeorm';

@Entity('users')
export class UserEntity {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  email: string;

  @Column()
  passwordHash: string;

  @Column({ default: true })
  isActive: boolean;

  @CreateDateColumn()
  createdAt: Date;

  @DeleteDateColumn()
  deletedAt: Date | null;
}
```

```ts
// typeorm-user.repository.ts — the concrete adapter
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, QueryFailedError } from 'typeorm';

export class EmailAlreadyExistsError extends Error {
  constructor(email: string) {
    super(`A user with email "${email}" already exists`);
    this.name = 'EmailAlreadyExistsError';
  }
}

@Injectable()
export class TypeOrmUserRepository implements UserRepository {
  constructor(
    @InjectRepository(UserEntity)
    private readonly repo: Repository<UserEntity>,
  ) {}

  async findById(id: string): Promise<User | null> {
    const row = await this.repo.findOne({ where: { id } });
    return row ? this.toDomain(row) : null;
  }

  async findByEmail(email: string): Promise<User | null> {
    const row = await this.repo.findOne({ where: { email } });
    return row ? this.toDomain(row) : null;
  }

  async findActiveUsers({ page, size }: PageQuery): Promise<Page<User>> {
    // Rows soft-deleted via @DeleteDateColumn are excluded automatically.
    const [rows, total] = await this.repo
      .createQueryBuilder('user')
      .where('user.isActive = :active', { active: true })
      .orderBy('user.createdAt', 'DESC')
      .skip((page - 1) * size)
      .take(size)
      .getManyAndCount();

    return { items: rows.map((r) => this.toDomain(r)), total, page, size };
  }

  async create(data: CreateUserData): Promise<User> {
    try {
      const row = this.repo.create(data);
      return this.toDomain(await this.repo.save(row));
    } catch (err) {
      // Translate the driver-specific error into a domain error so callers
      // never depend on Postgres error codes or TypeORM classes.
      if (
        err instanceof QueryFailedError &&
        (err.driverError as { code?: string }).code === '23505'
      ) {
        throw new EmailAlreadyExistsError(data.email);
      }
      throw err;
    }
  }

  async update(id: string, changes: Partial<CreateUserData>): Promise<User> {
    await this.repo.update({ id }, changes);
    const row = await this.repo.findOneByOrFail({ id });
    return this.toDomain(row);
  }

  async softDelete(id: string): Promise<void> {
    await this.repo.softDelete(id);
  }

  private toDomain(row: UserEntity): User {
    // Map to the domain shape; never leak passwordHash or ORM metadata.
    return {
      id: row.id,
      email: row.email,
      isActive: row.isActive,
      createdAt: row.createdAt,
    };
  }
}
```

Bind the token to the implementation and register the entity in the module:

```ts
// users.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';

@Module({
  imports: [TypeOrmModule.forFeature([UserEntity])],
  controllers: [UsersController],
  providers: [
    UsersService,
    { provide: USER_REPOSITORY, useClass: TypeOrmUserRepository },
  ],
})
export class UsersModule {}
```

The service depends only on the port. Swapping TypeORM for Prisma later means
writing a new adapter and rebinding the token — no service changes:

```ts
// users.service.ts
import { Inject, Injectable } from '@nestjs/common';

@Injectable()
export class UsersService {
  constructor(
    @Inject(USER_REPOSITORY)
    private readonly users: UserRepository,
  ) {}

  listActive(query: PageQuery): Promise<Page<User>> {
    return this.users.findActiveUsers(query);
  }
}
```

---

## Query Responsibility

Complex database queries belong inside repositories.

Examples:

- joins;
- filtering;
- pagination;
- sorting;
- aggregation.

Services should not construct SQL or ORM queries.

---

## ORM Isolation

Repositories should encapsulate ORM-specific code.

Whether using:

- Prisma;
- TypeORM;
- MikroORM;
- Sequelize;

the rest of the application should remain unaware of ORM implementation details.

Replacing the ORM should require minimal changes outside repositories.

---

## Transactions

Services coordinate transactions.

Repositories participate in transactions.

Repositories should not independently create transaction boundaries unless explicitly designed to do so.

---

## Pagination

Repositories should provide consistent pagination.

Support:

- offset pagination;
- cursor pagination;
- sorting;
- filtering.

Pagination behavior should remain predictable.

---

## Performance

Repositories should optimize:

- indexes;
- query count;
- eager loading;
- lazy loading;
- batching.

Avoid:

- N+1 queries;
- repeated lookups;
- unnecessary joins.

---

## Soft Deletes

If soft deletes are used:

- repositories should hide deleted records by default;
- explicit methods should retrieve archived data when required.

Behavior should remain consistent across the application.

---

## Domain Objects

Repositories should return:

- domain models;
- entities;
- typed objects.

Avoid returning raw database responses.

---

## Error Handling

Repositories should translate persistence failures into meaningful exceptions.

Avoid leaking ORM-specific errors into higher application layers.

---

## Caching

Repositories should not implement caching unless they are explicitly designed as cache-aware repositories.

Caching policies belong to dedicated infrastructure or service layers.

---

## External Storage

Repositories may represent:

- SQL databases;
- NoSQL databases;
- search engines;
- object storage;
- distributed storage.

The abstraction should remain consistent regardless of the backend.

---

## Security

Repositories should:

- use parameterized queries;
- prevent injection attacks;
- validate identifiers where appropriate;
- avoid exposing sensitive fields unintentionally.

Security begins at the persistence layer.

---

## Testing

Repositories should be tested with:

- integration tests;
- database fixtures;
- realistic queries.

Mock repositories when testing services. Because the service depends on the
`USER_REPOSITORY` port, the test binds a fake to that token — no database, no ORM:

```ts
import { Test } from '@nestjs/testing';

describe('UsersService', () => {
  it('rejects a duplicate email', async () => {
    const fake: jest.Mocked<UserRepository> = {
      findById: jest.fn(),
      findByEmail: jest.fn().mockResolvedValue({ id: 'u1' } as User),
      findActiveUsers: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      softDelete: jest.fn(),
    };

    const moduleRef = await Test.createTestingModule({
      providers: [
        UsersService,
        { provide: USER_REPOSITORY, useValue: fake },
        { provide: MailerService, useValue: { sendWelcome: jest.fn() } },
      ],
    }).compile();

    const service = moduleRef.get(UsersService);

    await expect(service.register('taken@example.com', 'pw')).rejects.toThrow(
      'Email taken',
    );
    expect(fake.create).not.toHaveBeenCalled();
  });
});
```

---

## AI Execution Checklist

## Investigation

☐ Identify persistence requirements.

☐ Review entity relationships.

☐ Review transaction requirements.

☐ Review performance expectations.

---

## Planning

☐ Encapsulate ORM usage.

☐ Design meaningful methods.

☐ Optimize common queries.

☐ Support transactions.

---

## Verification

☐ Business logic absent.

☐ ORM isolated.

☐ Queries optimized.

☐ Pagination consistent.

☐ Repository independently testable.

☐ Security reviewed.

---

## Common Mistakes

Avoid:

Writing business logic inside repositories.

Returning ORM-specific objects everywhere.

Creating SQL inside services.

Duplicating queries across modules.

Ignoring transaction boundaries.

Using repositories as generic utility classes.

Performing authorization inside repositories.

---

## Completion Criteria

A repository implementation is complete when:

- persistence concerns are fully encapsulated;
- business logic remains outside the repository;
- ORM implementation details are isolated;
- queries are efficient and reusable;
- transaction support is compatible with service workflows;
- repositories can be independently tested.

---

## Summary

Repositories form the persistence boundary of a NestJS application.

By isolating database access, exposing meaningful domain-oriented methods, optimizing queries, and keeping business logic within services, repositories remain reusable, maintainable, and independent from the underlying database technology.