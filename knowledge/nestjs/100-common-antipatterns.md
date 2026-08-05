---
id: nestjs/100-common-antipatterns
topic: nestjs
slug: common-antipatterns
title: "Common Engineering Antipatterns"
type: doc
order: 100
status: ready
tags: [nestjs, common-antipatterns]
related: [nestjs/01-architecture, nestjs/05-services, nestjs/99-ai-review-checklist, nestjs/30-engineering-principles]
when_to_use: "Read when reviewing NestJS code to catch common antipatterns and design smells before they become technical debt."
---
# Common Engineering Antipatterns

## Purpose

This document defines common engineering antipatterns that reduce software quality, maintainability, reliability, and scalability.

The objective is to help engineers and AI recognize poor design decisions before they become long-term technical debt.

Avoiding antipatterns is as important as applying best practices.

---

## Core Principle

Every shortcut introduces future maintenance cost.

Engineering decisions should optimize long-term sustainability rather than short-term convenience.

---

## God Object

A single class or service becomes responsible for too many unrelated concerns.

Symptoms:

- excessive dependencies;
- thousands of lines of code;
- unrelated responsibilities.

Solution:

Split responsibilities into focused components.

---

## Fat Controller

Controllers contain business logic.

Symptoms:

- complex validation;
- database access;
- business rules;
- external API calls.

Solution:

Move business logic into services or domain components. The controller should only translate HTTP into a service call and back.

Bad — validation, persistence, and business rules live in the handler:

```ts
import { Controller, Post, Body, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './user.entity';

@Controller('users')
export class UsersController {
  constructor(
    @InjectRepository(User) private readonly repo: Repository<User>,
  ) {}

  @Post()
  async create(@Body() body: any) {
    // manual validation
    if (!body.email || !body.email.includes('@')) {
      throw new BadRequestException('Invalid email');
    }
    // business rule + direct database access in the controller
    const existing = await this.repo.findOne({ where: { email: body.email } });
    if (existing) {
      throw new BadRequestException('Email already taken');
    }
    return this.repo.save(this.repo.create({ email: body.email }));
  }
}
```

Good — a validated DTO handles input, the service owns the rule, the controller stays thin:

```ts
// create-user.dto.ts
import { IsEmail } from 'class-validator';

export class CreateUserDto {
  @IsEmail()
  email: string;
}
```

```ts
// users.controller.ts
import { Controller, Post, Body } from '@nestjs/common';
import { CreateUserDto } from './create-user.dto';
import { UsersService } from './users.service';

@Controller('users')
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Post()
  create(@Body() dto: CreateUserDto) {
    // no logic here — just delegate; a global ValidationPipe already ran
    return this.users.register(dto);
  }
}
```

```ts
// users.service.ts
import { Injectable, ConflictException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './user.entity';
import { CreateUserDto } from './create-user.dto';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User) private readonly repo: Repository<User>,
  ) {}

  async register(dto: CreateUserDto): Promise<User> {
    const existing = await this.repo.findOne({ where: { email: dto.email } });
    if (existing) {
      throw new ConflictException('Email already taken');
    }
    return this.repo.save(this.repo.create(dto));
  }
}
```

Enable the DTO validation once, globally, in `main.ts`:

```ts
// main.ts
import { ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useGlobalPipes(
    new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true }),
  );
  await app.listen(3000);
}
bootstrap();
```

---

## Anemic Domain Model

Business objects contain only data.

All business logic is placed elsewhere.

Solution:

Business behavior should remain close to the business data it operates on.

---

## Spaghetti Code

Control flow becomes difficult to understand.

Symptoms:

- deeply nested conditions;
- duplicated logic;
- unpredictable dependencies.

Solution:

Refactor into smaller, well-defined units.

---

## Circular Dependencies

Components depend on each other directly or indirectly.

Consequences:

- fragile architecture;
- difficult testing;
- poor maintainability.

Solution:

Introduce abstractions or redesign module boundaries. In NestJS a true cycle surfaces at boot as `Nest can't resolve dependencies ... (?)` or `A circular dependency has been detected`.

`forwardRef` is the escape hatch when two providers genuinely need each other, but treat it as a smell to remove, not a pattern to reach for:

```ts
// users.service.ts — depends on AuthService, which depends back on UsersService
import { Injectable, Inject, forwardRef } from '@nestjs/common';
import { AuthService } from '../auth/auth.service';

@Injectable()
export class UsersService {
  constructor(
    @Inject(forwardRef(() => AuthService))
    private readonly auth: AuthService,
  ) {}
}
```

```ts
// users.module.ts — the module import needs forwardRef on both sides too
import { Module, forwardRef } from '@nestjs/common';
import { AuthModule } from '../auth/auth.module';
import { UsersService } from './users.service';

@Module({
  imports: [forwardRef(() => AuthModule)],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}
```

The better fix is usually to break the cycle: extract the shared logic into a third provider (e.g. a `TokenService`) that both modules import in one direction only, so no `forwardRef` is needed.

---

## Tight Coupling

Components know too much about each other.

Solution:

Depend on abstractions rather than implementations.

---

## Primitive Obsession

Primitive types replace meaningful domain concepts.

Example:

Using raw strings for currencies, emails, or identifiers.

Solution:

Create explicit value objects where appropriate.

---

## Magic Numbers

Hardcoded numeric values appear without explanation.

Solution:

Replace with named constants.

---

## Magic Strings

Business logic depends on hardcoded strings.

Solution:

Use enums, constants, or strongly typed objects.

---

## Copy-Paste Programming

Logic is duplicated across multiple locations.

Consequences:

- inconsistent behavior;
- expensive maintenance.

Solution:

Extract shared behavior carefully.

---

## Shotgun Surgery

A single change requires modifications in many files.

Solution:

Improve cohesion and responsibility boundaries.

---

## Over-Engineering

The solution is significantly more complex than the problem requires.

Examples:

- unnecessary abstractions;
- excessive patterns;
- speculative architecture.

Solution:

Apply KISS and YAGNI.

---

## Premature Optimization

Optimizing before identifying a real bottleneck.

Solution:

Measure first.

Optimize second.

---

## Leaky Abstraction

Implementation details escape through public interfaces.

Solution:

Hide internal implementation.

Expose only stable contracts.

---

## Hidden Side Effects

Functions unexpectedly modify state.

Solution:

Make side effects explicit.

Prefer predictable behavior.

---

## Shared Mutable State

Multiple components modify the same data.

Consequences:

- race conditions;
- unpredictable bugs.

Solution:

Reduce shared mutable state.

Prefer immutability when practical.

---

## Long Transactions

Transactions remain open longer than necessary.

Consequences:

- locking;
- reduced throughput;
- deadlocks.

Solution:

Keep transactions short.

---

## N+1 Queries

Applications repeatedly execute similar database queries.

Solution:

Use joins, eager loading, batching, or query optimization.

Bad — one query for the list, then one more query per row to load its author (the classic N+1):

```ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Post } from './post.entity';
import { Author } from './author.entity';

@Injectable()
export class PostsService {
  constructor(
    @InjectRepository(Post) private readonly posts: Repository<Post>,
    @InjectRepository(Author) private readonly authors: Repository<Author>,
  ) {}

  async listWithAuthors() {
    const posts = await this.posts.find(); // 1 query
    for (const post of posts) {
      // N extra queries — one round trip per post
      post.author = await this.authors.findOneBy({ id: post.authorId });
    }
    return posts;
  }
}
```

Good — load the relation in a single joined query with `relations` (or a query builder):

```ts
@Injectable()
export class PostsService {
  constructor(
    @InjectRepository(Post) private readonly posts: Repository<Post>,
  ) {}

  listWithAuthors() {
    // one query, author joined in via LEFT JOIN
    return this.posts.find({ relations: { author: true } });
  }

  // equivalent with the query builder when you need finer control
  listWithAuthorsQb() {
    return this.posts
      .createQueryBuilder('post')
      .leftJoinAndSelect('post.author', 'author')
      .getMany();
  }
}
```

---

## Chatty APIs

Clients perform excessive network requests.

Solution:

Design APIs around business use cases.

Reduce unnecessary round trips.

---

## Shared Database

Multiple services directly share the same database.

Consequences:

- tight coupling;
- deployment limitations;
- ownership confusion.

Solution:

Each service owns its data.

---

## Synchronous Distributed Chains

One service waits on many downstream services.

Consequences:

- cascading failures;
- increased latency.

Solution:

Prefer asynchronous communication where appropriate.

---

## Missing Timeouts

Remote calls wait indefinitely.

Solution:

Every external request should define a timeout.

---

## Missing Retry Strategy

Transient failures immediately fail.

Solution:

Retry transient failures using exponential backoff.

Avoid infinite retries.

---

## Exception Swallowing

Errors are ignored without logging or handling.

Solution:

Handle, log, or propagate exceptions appropriately.

---

## Silent Failures

Operations fail without notifying users or operators.

Solution:

Implement meaningful error reporting and monitoring.

---

## Hardcoded Configuration

Environment-specific values appear in source code.

Solution:

Externalize configuration.

---

## Logging Sensitive Data

Logs contain:

- passwords;
- tokens;
- secrets;
- personal information.

Solution:

Log only operationally necessary information.

---

## Ignoring Observability

Applications lack logs, metrics, or traces.

Consequences:

- difficult debugging;
- slow incident response.

Solution:

Implement comprehensive observability.

---

## Ignoring Tests

Code changes are made without adequate automated testing.

Solution:

Maintain balanced test coverage focused on behavior.

---

## AI Decision Matrix

Immediately review when detecting:

✓ Large classes

✓ Deep nesting

✓ Duplicate logic

✓ Circular dependencies

✓ Missing validation

✓ Hardcoded values

✓ Long transactions

✓ Poor observability

Avoid introducing:

✗ Hidden complexity

✗ Fragile architecture

✗ Premature optimization

✗ Tight coupling

✗ Operational blind spots

---

## AI Execution Checklist

## Investigation

☐ Identify architectural smells.

☐ Review dependency graph.

☐ Review database access.

☐ Review configuration.

---

## Planning

☐ Simplify design.

☐ Reduce coupling.

☐ Improve cohesion.

☐ Remove duplication.

---

## Verification

☐ Responsibilities remain focused.

☐ Business logic correctly located.

☐ Dependencies simplified.

☐ Configuration externalized.

☐ Observability preserved.

☐ Tests continue to pass.

---

## Completion Criteria

An implementation avoids common engineering antipatterns when:

- responsibilities are well defined;
- architecture remains maintainable;
- dependencies are intentional;
- operational concerns are addressed;
- complexity matches business requirements;
- future changes can be implemented with confidence.

---

## Summary

Engineering antipatterns are recurring design mistakes that increase complexity, reduce maintainability, and create long-term operational risk.

Recognizing these patterns early allows engineers and AI to build systems that remain understandable, scalable, and reliable throughout their lifecycle.

## Related

- `knowledge/nestjs/01-architecture.md`
- `knowledge/nestjs/05-services.md`
- `knowledge/nestjs/99-ai-review-checklist.md`
- `knowledge/nestjs/30-engineering-principles.md`
