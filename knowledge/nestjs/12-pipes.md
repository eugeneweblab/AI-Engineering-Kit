---
id: nestjs/12-pipes
topic: nestjs
slug: pipes
title: "NestJS Pipes"
type: doc
order: 12
status: ready
tags: [nestjs, pipes, Injectable, Param, BadRequestException, MinLength, Controller, ParseUUIDPipe]
related: [nestjs/07-dto, nestjs/08-validation, nestjs/04-controllers]
when_to_use: "Read before building or reviewing pipes that transform or validate incoming request data."
---
# NestJS Pipes

## Purpose

This document defines the engineering standards for implementing Pipes in NestJS applications.

The objective is to transform and validate incoming request data before it reaches controllers while keeping data preparation separate from business logic.

Pipes operate at the application boundary.

They should prepare data—not implement business rules.

---

## Core Principle

Transform early.

Validate early.

Execute business logic only after input has been prepared.

---

## Pipe Goals

Every Pipe should provide:

- deterministic behavior;
- reusable transformations;
- predictable validation;
- framework consistency;
- minimal side effects.

Pipes should always produce the same output for the same input.

---

## Request Lifecycle

Typical request flow:

```
HTTP Request

↓

Middleware

↓

Guards

↓

Interceptors (before)

↓

Pipes

↓

Controller

↓

Service

↓

Interceptors (after)

↓

Exception Filter

↓

HTTP Response
```

Pipes execute immediately before controller method invocation.

---

## Responsibilities

Pipes are responsible for:

- transforming request values;
- validating transport-level input;
- parsing primitive types;
- normalizing incoming data.

Pipes should not:

- perform business validation;
- access repositories;
- execute workflows;
- send events;
- call external APIs.

---

## Pipe Types

NestJS provides several categories of Pipes.

Examples include:

- ValidationPipe;
- ParseIntPipe;
- ParseBoolPipe;
- ParseUUIDPipe;
- ParseArrayPipe;
- ParseEnumPipe;
- DefaultValuePipe.

Custom Pipes should follow the same design principles.

Bind built-in pipes at the parameter level. `DefaultValuePipe` runs before the
parse pipe, so an absent query string is filled before it is coerced:

```ts
import {
  Controller,
  Get,
  Param,
  Query,
  ParseUUIDPipe,
  ParseIntPipe,
  ParseBoolPipe,
  DefaultValuePipe,
} from '@nestjs/common';

@Controller('users')
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Get(':id')
  findOne(@Param('id', ParseUUIDPipe) id: string) {
    // id is a validated UUID string; a malformed value fails with 400 here
    return this.users.findByIdOrFail(id);
  }

  @Get()
  list(
    @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
    @Query('active', new DefaultValuePipe(false), ParseBoolPipe) active: boolean,
  ) {
    // page is a number, active is a boolean — no manual parsing in the handler
    return this.users.list({ page, active });
  }
}
```

---

## Transformation

Pipes may transform values.

Examples:

```
"42"

↓

42
```

```
"true"

↓

true
```

```
"2026-07-06"

↓

Date
```

Transformation should remain deterministic.

---

## Validation

Pipes may reject invalid transport data.

Examples:

- malformed UUID;
- invalid integer;
- unsupported enum;
- invalid array.

Business rules belong elsewhere.

---

## Normalization

Normalize request data consistently.

Examples:

- trim whitespace;
- lowercase email addresses;
- remove duplicate separators;
- convert empty strings to undefined (when appropriate).

Normalization should remain predictable.

A custom Pipe implements the `PipeTransform` interface and is decorated with
`@Injectable`. The two type parameters are the input and output types; the
`ArgumentMetadata` argument tells you which parameter is being processed:

```ts
import {
  PipeTransform,
  Injectable,
  ArgumentMetadata,
  BadRequestException,
} from '@nestjs/common';

@Injectable()
export class TrimPipe implements PipeTransform<unknown, string> {
  transform(value: unknown, metadata: ArgumentMetadata): string {
    if (typeof value !== 'string') {
      throw new BadRequestException(`${metadata.data ?? 'value'} must be a string`);
    }
    return value.trim(); // deterministic, no side effects, no I/O
  }
}
```

Bind it exactly like a built-in pipe:

```ts
@Get()
search(@Query('q', TrimPipe) q: string) {
  return this.users.search(q);
}
```

---

## Pipes vs DTO Validation

DTO validation verifies object structure.

Pipes transform or validate individual values before business execution.

Use both together when appropriate.

`ValidationPipe` is the bridge between the two: it reads the `class-validator`
decorators on a DTO and, with `transform: true`, hands the controller a real
instance of the DTO class. Register it globally so every `@Body` is checked:

```ts
// main.ts
import { ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,            // strip properties with no decorator
      forbidNonWhitelisted: true, // reject payloads with unknown properties
      transform: true,            // instantiate the DTO class and coerce primitives
    }),
  );
  await app.listen(3000);
}
bootstrap();
```

```ts
// create-user.dto.ts
import { IsEmail, IsString, MinLength } from 'class-validator';
import { Transform } from 'class-transformer';

export class CreateUserDto {
  @Transform(({ value }) => (typeof value === 'string' ? value.trim().toLowerCase() : value))
  @IsEmail()
  email: string;

  @IsString()
  @MinLength(12)
  password: string;
}
```

```ts
// The handler receives a validated, normalized CreateUserDto instance.
@Post()
create(@Body() dto: CreateUserDto) {
  return this.users.create(dto);
}
```

---

## Pipes vs Services

Services answer business questions.

Example:

```
Can this user purchase this product?
```

Pipes answer transport questions.

Example:

```
Is this value a valid UUID?
```

Business logic should never move into Pipes.

---

## Pipes vs Guards

Guards answer:

```
Can this request proceed?
```

Pipes answer:

```
Is this request data valid?
```

Authorization does not belong in Pipes.

---

## Pipes vs Interceptors

Interceptors wrap request execution.

Pipes prepare request data.

They solve different problems.

---

## Database Access

Avoid database queries inside Pipes.

Incorrect:

```
Pipe

↓

Repository

↓

Database
```

Bad — the Pipe reaches into persistence and runs business validation on every
request. Existence ("does this user exist?") is a business question, not a
transport one:

```ts
// Bad: a pipe that queries the database
@Injectable()
export class UserExistsPipe implements PipeTransform<string, string> {
  constructor(
    @InjectRepository(UserEntity)
    private readonly repo: Repository<UserEntity>,
  ) {}

  async transform(id: string): Promise<string> {
    const user = await this.repo.findOne({ where: { id } });
    if (!user) throw new NotFoundException('User not found'); // business rule in a pipe
    return id;
  }
}
```

Good — the Pipe validates only the transport format; the service owns the
existence check and the not-found error:

```ts
// Good: pipe validates shape, service owns the business question
@Get(':id')
findOne(@Param('id', ParseUUIDPipe) id: string) {
  return this.users.findByIdOrFail(id);
}
```

Correct:

```
Pipe

↓

Controller

↓

Service

↓

Repository
```

Business validation belongs inside services.

---

## Exception Handling

Pipes should throw meaningful validation exceptions.

Avoid custom response formatting.

Exception Filters should format responses consistently.

---

## Composition

Prefer composing multiple focused Pipes rather than creating one large Pipe.

Example:

```
ParseUUIDPipe

↓

CustomTrimPipe

↓

ValidationPipe
```

Small Pipes are easier to reuse and test.

---

## Reusability

Reusable Pipes should remain independent of business features.

Examples:

- UUID parsing;
- string normalization;
- boolean conversion.

Feature-specific logic should remain inside services.

---

## Performance

Pipes execute on every request.

Avoid:

- database access;
- network requests;
- expensive computations;
- unnecessary object creation.

Keep execution lightweight.

---

## Security

Validate:

- identifiers;
- enum values;
- primitive types;
- array sizes;
- payload structure.

Reject malformed requests immediately.

---

## Testing

Verify:

- valid input;
- invalid input;
- transformation behavior;
- exception handling;
- edge cases.

Pipes should be deterministic.

---

## AI Decision Matrix

Use a Pipe when the task is:

✓ Parsing request data

✓ Converting primitive types

✓ Normalizing transport values

✓ Rejecting malformed input

Do **not** use a Pipe for:

✗ Database lookups

✗ Permission checks

✗ Business rules

✗ Sending emails

✗ Calling external APIs

---

## AI Execution Checklist

## Investigation

☐ Identify transport data.

☐ Review required transformations.

☐ Review validation needs.

☐ Review performance impact.

---

## Planning

☐ Keep Pipe focused.

☐ Avoid business logic.

☐ Normalize input.

☐ Throw consistent exceptions.

---

## Verification

☐ Transformation deterministic.

☐ Validation correct.

☐ No database access.

☐ No authorization logic.

☐ Independently testable.

☐ Lightweight execution.

---

## Examples

**Good Example** — a pipe transforms and validates one value, statelessly

```ts
// Built-in pipes cover most parameter needs and produce correct 400s.
@Controller('orders')
export class OrdersController {
  constructor(private readonly orders: OrdersService) {}

  @Get(':id')
  findOne(
    @Param('id', ParseUUIDPipe) id: string,
    @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
    @Query('limit', new DefaultValuePipe(20), ParseIntPipe) limit: number,
  ) {
    return this.orders.findPage(id, { page, limit: Math.min(limit, 100) });
  }
}
```

```ts
// A custom pipe when the transformation is genuinely reusable and self-contained.
@Injectable()
export class TrimPipe implements PipeTransform<string, string> {
  transform(value: string, metadata: ArgumentMetadata): string {
    if (typeof value !== 'string') {
      throw new BadRequestException(`${metadata.data} must be a string`);
    }
    return value.trim();
  }
}
```

No I/O, no database, no request state — so the pipe is a pure function of its input and can
be unit-tested with a single call.

**Bad Example** — a pipe that queries the database and enforces a business rule

```ts
@Injectable()
export class LoadAndAuthorizeOrderPipe implements PipeTransform {
  constructor(
    private readonly repo: OrdersRepository,
    @Inject(REQUEST) private readonly request: Request,   // forces request scope
  ) {}

  async transform(id: string): Promise<Order> {
    // I/O in a pipe: the query runs outside any transaction the handler opens,
    // and the same order is loaded twice per request.
    const order = await this.repo.findById(id);
    if (!order) {
      throw new NotFoundException();
    }

    // Authorization in a pipe: invisible to anyone reading the controller, and
    // unreachable from the queue consumer that needs the same rule.
    if (order.userId !== (this.request as any).user.id) {
      throw new ForbiddenException();
    }

    return order;
  }
}
```

Ownership checks belong in a Guard; loading the aggregate belongs in the service. A pipe that
does both makes the request pipeline the place business rules hide.

---

## Common Mistakes

Avoid:

Querying the database inside Pipes.

Checking permissions.

Embedding business rules.

Creating large multi-purpose Pipes.

Calling external APIs.

Duplicating validation already handled by DTOs.

Adding side effects.

---

## Completion Criteria

A Pipe implementation is complete when:

- it transforms or validates transport data only;
- business logic remains outside the Pipe;
- execution is deterministic;
- malformed requests fail early;
- performance remains lightweight;
- the Pipe can be independently tested.

---

## Summary

Pipes define the transport boundary of a NestJS application.

By focusing exclusively on parsing, normalization, and transport-level validation while avoiding business logic and infrastructure concerns, Pipes keep controllers simple, services focused, and the request lifecycle clean and predictable.

## Related

- `knowledge/nestjs/07-dto.md`
- `knowledge/nestjs/08-validation.md`
- `knowledge/nestjs/04-controllers.md`
