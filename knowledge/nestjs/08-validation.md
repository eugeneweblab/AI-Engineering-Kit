---
id: nestjs/08-validation
topic: nestjs
slug: validation
title: "NestJS Validation"
type: doc
order: 8
status: ready
tags: [nestjs, validation, IsEmail, IsUUID, ValidateNested, IsInt, IsArray, IsOptional]
related: [nestjs/07-dto, nestjs/12-pipes, nestjs/11-exception-filters, backend/09-validation, security/09-input-validation]
when_to_use: "Read before adding or reviewing validation of incoming request data at the application boundary."
---
# NestJS Validation

## Purpose

This document defines the engineering standards for validating data in NestJS applications.

The objective is to ensure that all incoming data is validated consistently, securely, and predictably before reaching business logic.

Validation protects the application boundary.

Business rules remain inside services.

---

## Core Principle

Validate input immediately.

Reject invalid data before it enters the application.

---

## Validation Goals

Every validation strategy should provide:

- predictable behavior;
- fail-fast execution;
- clear error messages;
- consistent API responses;
- strong type safety;
- reusable validation rules.

Validation should reduce the number of invalid states the application can reach.

---

## Validation Layers

Validation exists at multiple layers.

```
HTTP Request

↓

Transport Validation

↓

Controller

↓

Business Validation

↓

Service

↓

Repository
```

Each layer validates different concerns.

---

## Transport Validation

Transport validation verifies:

- required fields;
- data types;
- formats;
- ranges;
- enums;
- array structure;
- nested objects.

Transport validation should not verify business rules.

---

## Business Validation

Business validation verifies rules such as:

- email uniqueness;
- account ownership;
- inventory availability;
- payment status;
- business constraints.

Business validation belongs inside services.

---

## ValidationPipe

Enable a global `ValidationPipe`.

Recommended production configuration:

- validate all DTOs;
- transform incoming values;
- reject unknown properties;
- forbid unexpected fields.

Validation should be centralized.

Register the pipe globally in `main.ts`:

```ts
// main.ts
import { ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // strip any property that has no validation decorator
      forbidNonWhitelisted: true, // reject requests that carry unknown properties
      transform: true, // instantiate the DTO class and coerce primitive types
      transformOptions: {
        // prefer explicit @Type() over guessing types from the route metadata
        enableImplicitConversion: false,
      },
    }),
  );

  await app.listen(3000);
}
bootstrap();
```

Prefer registering the pipe as an `APP_PIPE` provider when it needs
dependency injection (for example, async constraints that read from a
repository). This keeps the configuration testable and available inside the
DI container:

```ts
// app.module.ts
import { Module, ValidationPipe } from '@nestjs/common';
import { APP_PIPE } from '@nestjs/core';

@Module({
  providers: [
    {
      provide: APP_PIPE,
      useValue: new ValidationPipe({
        whitelist: true,
        forbidNonWhitelisted: true,
        transform: true,
      }),
    },
  ],
})
export class AppModule {}
```

---

## DTO Validation

Every request DTO should define validation rules.

Typical examples:

- string length;
- numeric range;
- email format;
- UUID format;
- enum values;
- nested DTO validation.

Every public endpoint accepting request data should use DTO validation.

A DTO is a plain class annotated with `class-validator` decorators. The
global `ValidationPipe` reads those decorators to validate and (with
`transform: true`) instantiate the class:

```ts
// create-user.dto.ts
import { IsEmail, IsInt, IsOptional, Length, Max, Min } from 'class-validator';

export class CreateUserDto {
  @IsEmail()
  email: string;

  @Length(2, 60)
  name: string;

  @IsOptional()
  @IsInt()
  @Min(18)
  @Max(120)
  age?: number;
}
```

```ts
// users.controller.ts
import { Body, Controller, Post } from '@nestjs/common';
import { CreateUserDto } from './create-user.dto';
import { UsersService } from './users.service';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  create(@Body() dto: CreateUserDto) {
    // `dto` is already validated and typed by the time it reaches here.
    return this.usersService.create(dto);
  }
}
```

---

## Nested Validation

Validate nested objects explicitly.

Example hierarchy:

```
CreateOrderDto

↓

CustomerDto

↓

AddressDto
```

Every nested object should have its own DTO.

Nested objects require both `@ValidateNested()` and `@Type()` from
`class-transformer`. Without `@Type()`, the pipe cannot know which class to
instantiate and validation of the nested payload is silently skipped:

```ts
// create-order.dto.ts
import { Type } from 'class-transformer';
import {
  ArrayMaxSize,
  ArrayMinSize,
  IsArray,
  IsEmail,
  IsEnum,
  IsInt,
  IsOptional,
  IsUUID,
  Length,
  Max,
  Min,
  ValidateNested,
} from 'class-validator';

export enum ShippingSpeed {
  Standard = 'standard',
  Express = 'express',
}

export class AddressDto {
  @Length(1, 120)
  street: string;

  @Length(2, 2)
  countryCode: string;
}

export class CustomerDto {
  @IsEmail()
  email: string;

  @ValidateNested()
  @Type(() => AddressDto)
  address: AddressDto;
}

export class OrderItemDto {
  @IsUUID()
  productId: string;

  @IsInt()
  @Min(1)
  @Max(100)
  quantity: number;
}

export class CreateOrderDto {
  @ValidateNested()
  @Type(() => CustomerDto)
  customer: CustomerDto;

  // Validate every element of the array against OrderItemDto.
  @IsArray()
  @ArrayMinSize(1)
  @ArrayMaxSize(50)
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)
  items: OrderItemDto[];

  @IsOptional()
  @IsEnum(ShippingSpeed)
  shippingSpeed?: ShippingSpeed;
}
```

---

## Array Validation

Arrays should validate:

- item type;
- minimum length;
- maximum length;
- uniqueness when required.

Avoid accepting arbitrary arrays.

For arrays of primitives, combine `@IsArray()` with the `each: true` option so
the item constraint applies to every element:

```ts
import { ArrayMaxSize, ArrayUnique, IsArray, IsUUID } from 'class-validator';

export class AssignTagsDto {
  @IsArray()
  @ArrayMaxSize(20)
  @ArrayUnique()
  @IsUUID('4', { each: true })
  tagIds: string[];
}
```

For arrays of nested objects, use `@ValidateNested({ each: true })` together
with `@Type()` as shown in `CreateOrderDto` above.

---

## Custom Validators

Create custom validators for reusable domain-independent rules.

Examples:

- password strength;
- phone number format;
- tax identifier format;
- country code validation.

Keep custom validators focused and reusable.

Implement a reusable rule as a `ValidatorConstraintInterface` and expose it as
a decorator with `registerDecorator`. This one is synchronous and
dependency-free, so it stays at the transport boundary:

```ts
// is-strong-password.validator.ts
import {
  registerDecorator,
  ValidationOptions,
  ValidatorConstraint,
  ValidatorConstraintInterface,
} from 'class-validator';

@ValidatorConstraint({ name: 'isStrongPassword', async: false })
export class IsStrongPasswordConstraint
  implements ValidatorConstraintInterface
{
  validate(value: unknown): boolean {
    return (
      typeof value === 'string' &&
      value.length >= 12 &&
      /[a-z]/.test(value) &&
      /[A-Z]/.test(value) &&
      /[0-9]/.test(value)
    );
  }

  defaultMessage(): string {
    return 'password must be at least 12 characters and include upper, lower, and numeric characters';
  }
}

export function IsStrongPassword(options?: ValidationOptions) {
  return function (object: object, propertyName: string): void {
    registerDecorator({
      target: object.constructor,
      propertyName,
      options,
      validator: IsStrongPasswordConstraint,
    });
  };
}
```

```ts
// register.dto.ts
import { IsEmail } from 'class-validator';
import { IsStrongPassword } from './is-strong-password.validator';

export class RegisterDto {
  @IsEmail()
  email: string;

  @IsStrongPassword()
  password: string;
}
```

---

## Business Rules

Business rules should never be implemented as DTO validation.

Incorrect example:

```
Email must be unique
```

Correct location:

```
UsersService
```

Validation attributes cannot replace business logic.

A business rule such as email uniqueness needs the database, so it must not
live in a DTO validator.

Bad — uniqueness enforced with a database query at the transport boundary:

```ts
// BAD: an async constraint that queries the database inside validation.
import { Injectable } from '@nestjs/common';
import {
  ValidatorConstraint,
  ValidatorConstraintInterface,
} from 'class-validator';
import { UsersRepository } from './users.repository';

@ValidatorConstraint({ name: 'isEmailUnique', async: true })
@Injectable()
export class IsEmailUniqueConstraint implements ValidatorConstraintInterface {
  constructor(private readonly users: UsersRepository) {}

  async validate(email: string): Promise<boolean> {
    // A DB round-trip on every request, racy, and hard to test in isolation.
    return !(await this.users.findByEmail(email));
  }
}
```

Good — the DTO stays structural and the service owns the business rule:

```ts
// create-user.dto.ts — transport concerns only.
import { IsEmail } from 'class-validator';

export class CreateUserDto {
  @IsEmail()
  email: string;
}
```

```ts
// users.service.ts — business rule lives here.
import { ConflictException, Injectable } from '@nestjs/common';
import { CreateUserDto } from './create-user.dto';
import { UsersRepository } from './users.repository';
import { User } from './user.entity';

@Injectable()
export class UsersService {
  constructor(private readonly users: UsersRepository) {}

  async create(dto: CreateUserDto): Promise<User> {
    const existing = await this.users.findByEmail(dto.email);
    if (existing) {
      throw new ConflictException('Email already registered');
    }
    return this.users.save(dto);
  }
}
```

The `Good` version also lets the database enforce a unique constraint as the
final authority, closing the race window the validator approach leaves open.

---

## Fail-Fast

Reject invalid requests immediately.

Avoid allowing partially valid requests to continue through the application.

---

## Error Messages

Validation errors should be:

- consistent;
- human-readable;
- predictable;
- machine-consumable.

Do not expose internal implementation details.

---

## Sanitization

Normalize data before business processing when appropriate.

Examples:

- trimming whitespace;
- lowercasing email addresses;
- removing duplicate separators;
- converting numeric strings.

Sanitization should be deterministic.

Use `@Transform` from `class-transformer` to normalize a value before the
validation decorators run. The pipe applies the transform, then validates the
result:

```ts
import { Transform } from 'class-transformer';
import { IsEmail } from 'class-validator';

export class SignInDto {
  @Transform(({ value }) =>
    typeof value === 'string' ? value.trim().toLowerCase() : value,
  )
  @IsEmail()
  email: string;
}
```

---

## Transformation

Incoming values may be transformed into:

- numbers;
- booleans;
- dates;
- enums.

Transformation should occur before business logic executes.

---

## Unknown Fields

Unexpected request fields should be rejected.

Allowing arbitrary fields increases security risks and API ambiguity.

---

## Alternative Validators

Alternative validation libraries may be appropriate.

Examples:

- Zod;
- Joi;
- Yup.

When selected, validation strategy should remain consistent across the application.

---

## API Documentation

Validation rules should align with API documentation.

Consumers should understand:

- required fields;
- optional fields;
- constraints;
- formats.

Documentation and validation should never contradict each other.

---

## Performance

Validation should remain efficient.

Avoid:

- duplicate validation;
- unnecessary object transformations;
- repeated parsing.

Business logic should receive already validated data.

---

## Security

Validation helps prevent:

- malformed requests;
- injection attempts;
- oversized payloads;
- invalid identifiers;
- unexpected object structures.

Validation is part of the application's security model.

---

## Testing

Verify:

- valid input;
- invalid input;
- missing fields;
- nested validation;
- transformation;
- custom validators.

Validation should remain deterministic.

---

## AI Execution Checklist

## Investigation

☐ Identify request contract.

☐ Separate transport and business validation.

☐ Review nested objects.

☐ Review security requirements.

---

## Planning

☐ Validate DTOs.

☐ Reject unknown fields.

☐ Transform values.

☐ Centralize validation.

---

## Verification

☐ Validation complete.

☐ Business rules isolated.

☐ Error messages consistent.

☐ Unknown fields rejected.

☐ Transformation verified.

☐ Validation independently testable.

---

## Examples

**Good Example** — transport validation at the edge, business validation in the domain

```ts
// main.ts — one global pipe, configured to reject anything not declared.
app.useGlobalPipes(
  new ValidationPipe({
    whitelist: true,             // strip properties with no decorator
    forbidNonWhitelisted: true,  // and reject the request if any were sent
    transform: true,             // instantiate the DTO class, not a plain object
    transformOptions: { enableImplicitConversion: false },
    stopAtFirstError: false,     // report every field at once, not one per round trip
  }),
);
```

```ts
// The DTO answers "is this a well-formed request?" — nothing more.
export class TransferDto {
  @IsUUID()
  readonly fromAccountId!: string;

  @IsUUID()
  readonly toAccountId!: string;

  @IsInt()
  @Min(1)
  readonly amountCents!: number;
}

// The service answers "is this allowed right now?" — which needs state.
@Injectable()
export class TransfersService {
  async transfer(dto: TransferDto): Promise<Transfer> {
    const from = await this.accounts.findById(dto.fromAccountId);

    // Cannot live in a decorator: it depends on data, and on data at this instant.
    if (from.balanceCents < dto.amountCents) {
      throw new InsufficientFundsError(from.id, dto.amountCents);
    }
    if (from.frozen) {
      throw new AccountFrozenError(from.id);
    }

    return this.ledger.record(dto);
  }
}
```

**Bad Example** — validation split across everything, and a DTO that queries the database

```ts
// No global pipe, so decorators on DTOs are inert and never run.
export class TransferDto {
  @IsUUID()
  readonly fromAccountId!: string;      // decorated, but nothing validates it
}

@Controller('transfers')
export class TransfersController {
  @Post()
  async transfer(@Body() body: any) {
    // Hand-rolled checks, duplicated in every endpoint that touches an account,
    // and drifting from the DTO the moment either changes.
    if (typeof body.amountCents !== 'number' || body.amountCents <= 0) {
      throw new HttpException('bad amount', 400);
    }

    // A balance check in the controller: the same rule is re-implemented in the
    // queue consumer, and the two disagree within a release.
    const from = await this.repo.findOne({ where: { id: body.fromAccountId } });
    if (!from || from.balanceCents < body.amountCents) {
      throw new HttpException('insufficient funds', 400);
    }

    return this.service.transfer(body);
  }
}
```

A custom validator that reaches into the database is the same mistake in a different place:
it turns a stateless shape check into a stateful business rule with no transaction around it.

---

## Common Mistakes

Avoid:

Putting business validation inside DTOs.

Skipping validation on internal endpoints.

Accepting arbitrary JSON.

Duplicating validation in controllers.

Performing database lookups inside validators.

Returning inconsistent validation errors.

Trusting client-side validation.

---

## Completion Criteria

Validation is complete when:

- every public endpoint validates incoming data;
- transport validation is separated from business validation;
- unknown fields are rejected;
- data is normalized consistently;
- validation errors are predictable;
- business logic receives only validated input.

---

## Summary

Validation establishes the first line of defense for every NestJS application.

By validating all incoming requests, separating transport validation from business rules, rejecting unexpected input, and enforcing consistent validation behavior, applications become more secure, reliable, and easier to maintain.

## Related

- `knowledge/nestjs/07-dto.md`
- `knowledge/nestjs/12-pipes.md`
- `knowledge/nestjs/11-exception-filters.md`
- `knowledge/backend/09-validation.md`
- `knowledge/security/09-input-validation.md`
