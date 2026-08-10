---
id: nestjs/07-dto
topic: nestjs
slug: dto
title: "NestJS Data Transfer Objects (DTO)"
type: doc
order: 7
status: ready
tags: [nestjs, dto, IsString, IsInt, ValidateNested, MaxLength, IsOptional, contracts, response, defining]
related: [nestjs/08-validation, nestjs/12-pipes, nestjs/04-controllers, rest-api/06-request-response]
when_to_use: "Read before defining or reviewing request and response DTOs and API contracts."
---
# NestJS Data Transfer Objects (DTO)

## Purpose

This document defines the engineering standards for designing and using Data Transfer Objects (DTOs) in NestJS applications.

The objective is to establish a clear contract between the API and its consumers while keeping transport models independent from domain models and persistence models.

DTOs define the API contract.

They are not business objects or database entities.

---

## Core Principle

Separate transport models from business models.

Never expose persistence models directly through the API.

---

## DTO Goals

Every DTO should provide:

- explicit API contracts;
- request validation;
- predictable serialization;
- version compatibility;
- type safety;
- documentation support.

DTOs should describe data—not behavior.

---

## Responsibilities

DTOs are responsible for:

- defining API input;
- defining API output;
- validation metadata;
- serialization rules;
- API documentation.

DTOs should never contain:

- business logic;
- persistence logic;
- authorization logic;
- database annotations.

---

## Request Flow

Typical flow:

```
HTTP Request

↓

Request DTO

↓

Validation

↓

Controller

↓

Service

↓

Repository

↓

Database

↓

Domain Model

↓

Response DTO

↓

HTTP Response
```

Every layer has a dedicated responsibility.

---

## DTO Categories

A feature typically contains:

```
dto/

    create-user.dto.ts

    update-user.dto.ts

    login.dto.ts

    user-response.dto.ts

    pagination.dto.ts
```

Separate DTOs by purpose.

---

## Request DTOs

Request DTOs describe incoming data.

Examples:

- CreateUserDto
- UpdateUserDto
- LoginDto
- ChangePasswordDto

Every public endpoint accepting a request body should use a dedicated Request DTO.

A Request DTO is a plain class annotated with `class-validator` decorators. These decorators are the machine-readable API contract:

```ts
// users/dto/create-user.dto.ts
import { IsEmail, IsEnum, IsString, MaxLength, MinLength } from 'class-validator';

export enum UserRole {
  Admin = 'admin',
  Member = 'member',
}

export class CreateUserDto {
  @IsEmail()
  email: string;

  @IsString()
  @MinLength(2)
  @MaxLength(80)
  name: string;

  @IsString()
  @MinLength(12)
  @MaxLength(128)
  password: string;

  @IsEnum(UserRole)
  role: UserRole;
}
```

The controller declares the DTO as the `@Body()` type. Once a global `ValidationPipe` is registered, NestJS validates and instantiates the DTO before the handler runs:

```ts
// users/users.controller.ts
import { Body, Controller, Get, Param, Post } from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto';
import { UserResponseDto } from './dto/user-response.dto';
import { UsersService } from './users.service';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  async create(@Body() dto: CreateUserDto): Promise<UserResponseDto> {
    const user = await this.usersService.create(dto);
    return UserResponseDto.fromEntity(user);
  }
}
```

Register the pipe once, at bootstrap, so every DTO is enforced consistently:

```ts
// main.ts
import { ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // strip properties that have no validation decorator
      forbidNonWhitelisted: true, // 400 when unexpected properties are sent
      transform: true, // instantiate the DTO class and coerce primitive types
    }),
  );
  await app.listen(3000);
}
bootstrap();
```

---

## Response DTOs

Response DTOs define outgoing data.

Examples:

- UserResponseDto
- ProductResponseDto
- OrderSummaryDto

Never return ORM entities directly.

---

## Why Entities Must Not Be Returned

Returning the persistence model directly leaks whatever the ORM happens to load, including columns added later.

Bad — the entity (with `passwordHash`, internal flags, ORM metadata) becomes the public contract:

```ts
// Bad: every column of UserEntity is now part of the API response.
@Get(':id')
async findOne(@Param('id') id: string) {
  return this.usersService.findById(id); // returns UserEntity
}
```

Good — the handler returns an explicit Response DTO, so only mapped fields leave the boundary:

```ts
// Good: the response shape is fixed and reviewable.
@Get(':id')
async findOne(@Param('id') id: string): Promise<UserResponseDto> {
  const user = await this.usersService.findById(id);
  return UserResponseDto.fromEntity(user);
}
```

Problems with returning entities include:

- leaking internal fields;
- accidental password exposure;
- ORM coupling;
- unstable API contracts;
- serialization inconsistencies.

Always map entities to Response DTOs.

---

## Mapper Pattern

Use dedicated mappers.

Example:

```
UserEntity

↓

UserMapper

↓

UserResponseDto
```

A Response DTO owns its own mapping through a static factory. This keeps the entity-to-DTO translation in one place and guarantees only whitelisted fields are ever assigned:

```ts
// users/dto/user-response.dto.ts
import { UserEntity } from '../entities/user.entity';

export class UserResponseDto {
  id: string;
  email: string;
  name: string;
  createdAt: Date;

  // Explicit whitelist: passwordHash and internal columns are never copied.
  static fromEntity(user: UserEntity): UserResponseDto {
    const dto = new UserResponseDto();
    dto.id = user.id;
    dto.email = user.email;
    dto.name = user.name;
    dto.createdAt = user.createdAt;
    return dto;
  }

  static fromEntities(users: UserEntity[]): UserResponseDto[] {
    return users.map((user) => UserResponseDto.fromEntity(user));
  }
}
```

Mapping should remain centralized.

Avoid performing mapping throughout controllers.

---

## Validation

Request DTOs should validate:

- required fields;
- formats;
- lengths;
- ranges;
- enums;
- nested objects.

Invalid input should never reach business logic.

---

## Nested DTOs

Nested objects should use dedicated DTOs.

Example:

```
CreateOrderDto

↓

CustomerDto

↓

AddressDto
```

Nested objects require `@ValidateNested()` plus `@Type()` from `class-transformer` — without `@Type()`, the validator cannot instantiate the nested class and the rules are silently skipped:

```ts
// orders/dto/create-order.dto.ts
import { Type } from 'class-transformer';
import {
  ArrayMinSize,
  IsArray,
  IsInt,
  IsString,
  Min,
  ValidateNested,
} from 'class-validator';

export class AddressDto {
  @IsString()
  street: string;

  @IsString()
  city: string;

  @IsString()
  postalCode: string;
}

export class OrderItemDto {
  @IsString()
  sku: string;

  @IsInt()
  @Min(1)
  quantity: number;
}

export class CreateOrderDto {
  @ValidateNested()
  @Type(() => AddressDto)
  shippingAddress: AddressDto;

  @IsArray()
  @ArrayMinSize(1)
  @ValidateNested({ each: true }) // validate every element of the array
  @Type(() => OrderItemDto)
  items: OrderItemDto[];
}
```

Avoid anonymous nested object definitions.

---

## Partial Updates

Use dedicated update DTOs.

Typical pattern:

```
CreateUserDto

↓

UpdateUserDto
```

Derive the update DTO from the create DTO with `PartialType` so validation rules stay in one place and every field becomes optional. Compose with `OmitType` to drop fields that must not be updated through this endpoint (for example, `password`, which belongs to a dedicated change-password flow):

```ts
// users/dto/update-user.dto.ts
import { OmitType, PartialType } from '@nestjs/mapped-types';
import { CreateUserDto } from './create-user.dto';

// All remaining fields become optional; password is excluded entirely.
export class UpdateUserDto extends PartialType(
  OmitType(CreateUserDto, ['password'] as const),
) {}
```

Use `@nestjs/mapped-types` for plain APIs, or the identically named helpers from `@nestjs/swagger` when you also generate OpenAPI documentation.

Update DTOs should clearly express optional fields.

---

## Serialization

Response DTOs should control serialization.

Typical responsibilities:

- hide internal fields;
- rename properties;
- transform values;
- expose computed values.

The static-mapper pattern above is the safest default because it never copies a sensitive field in the first place. When you instead return class instances and let NestJS serialize them, use `ClassSerializerInterceptor` with `class-transformer` decorators. Mark the class `@Exclude()` and opt fields in with `@Expose()`, so new columns are hidden by default:

```ts
// users/dto/user-response.dto.ts
import { Exclude, Expose } from 'class-transformer';

@Exclude() // opt-in serialization: only @Expose()-d members are emitted
export class UserResponseDto {
  @Expose() id: string;
  @Expose() email: string;
  @Expose() name: string;

  // Assigned internally, but excluded by the class-level @Exclude().
  passwordHash: string;

  @Expose()
  get displayName(): string {
    return this.name ?? this.email;
  }
}
```

```ts
// main.ts
import { ClassSerializerInterceptor } from '@nestjs/common';
import { Reflector } from '@nestjs/core';

app.useGlobalInterceptors(new ClassSerializerInterceptor(app.get(Reflector)));
```

`ClassSerializerInterceptor` only applies these rules when the controller returns an **instance** of the DTO class. Returning a plain object or a raw ORM entity bypasses the decorators entirely, so always return `plainToInstance(UserResponseDto, ...)` or a real DTO instance.

Serialization rules should remain predictable.

---

## Sensitive Data

Never expose:

- passwords;
- password hashes;
- API keys;
- refresh tokens;
- internal identifiers;
- security metadata.

Sensitive data should never leave the backend.

---

## Pagination DTOs

Collection endpoints should use dedicated DTOs.

Typical request:

```
page

limit

sort

filter
```

Typical response:

```
items

total

page

limit
```

Query parameters arrive as strings, so a pagination query DTO must coerce them with `@Type(() => Number)` (honored by `ValidationPipe`'s `transform: true`) and bound the values. Defaults protect the database from unbounded scans:

```ts
// common/dto/pagination-query.dto.ts
import { Type } from 'class-transformer';
import { IsInt, IsOptional, Max, Min } from 'class-validator';

export class PaginationQueryDto {
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  page: number = 1;

  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(100) // never let a client request an unbounded page
  limit: number = 20;
}
```

Return a stable, reusable envelope for every collection endpoint:

```ts
// common/dto/paginated-response.dto.ts
export class PaginatedResponseDto<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;

  constructor(items: T[], total: number, query: { page: number; limit: number }) {
    this.items = items;
    this.total = total;
    this.page = query.page;
    this.limit = query.limit;
  }
}
```

Consume both in the controller with `@Query()`:

```ts
@Get()
async list(
  @Query() query: PaginationQueryDto,
): Promise<PaginatedResponseDto<UserResponseDto>> {
  const [users, total] = await this.usersService.findPage(query);
  return new PaginatedResponseDto(
    UserResponseDto.fromEntities(users),
    total,
    query,
  );
}
```

Maintain a consistent pagination contract.

---

## Versioning

Public APIs should support DTO versioning when breaking changes occur.

Example:

```
UserResponseV1Dto

UserResponseV2Dto
```

Avoid modifying existing public contracts incompatibly.

---

## Reusability

Share DTOs only when semantics are identical.

Avoid creating generic DTOs that attempt to satisfy unrelated endpoints.

---

## Documentation

DTOs should serve as the source of truth for API documentation.

Every public property should be:

- named clearly;
- typed correctly;
- documented when necessary.

---

## Performance

Avoid unnecessary DTO nesting.

Avoid excessively large response objects.

Transfer only the data required by clients.

---

## Security

Review every Response DTO for:

- sensitive fields;
- internal metadata;
- authorization leaks.

Assume every exposed property becomes part of the public API.

---

## Testing

Verify:

- validation rules;
- serialization;
- mapping;
- excluded fields;
- transformed properties.

DTO contracts should remain stable.

---

## AI Execution Checklist

## Investigation

☐ Identify API contract.

☐ Separate input from output.

☐ Review validation requirements.

☐ Review serialization rules.

---

## Planning

☐ Create dedicated Request DTOs.

☐ Create dedicated Response DTOs.

☐ Implement mappers.

☐ Hide sensitive fields.

---

## Verification

☐ ORM entities not exposed.

☐ Validation complete.

☐ Serialization correct.

☐ Mapping centralized.

☐ API contract documented.

☐ DTOs independently testable.

---

## Examples

**Good Example** — separate request, domain, and response shapes

```ts
// orders/dto/create-order.dto.ts — the input contract, validated at the boundary.
export class CreateOrderItemDto {
  @IsUUID()
  readonly sku!: string;

  @IsInt()
  @Min(1)
  @Max(100)
  readonly quantity!: number;
}

export class CreateOrderDto {
  @IsArray()
  @ArrayNotEmpty()
  @ValidateNested({ each: true })
  @Type(() => CreateOrderItemDto)         // required for nested validation to run
  readonly items!: CreateOrderItemDto[];

  @IsOptional()
  @IsString()
  @MaxLength(500)
  readonly note?: string;
}
```

```ts
// orders/dto/order-response.dto.ts — the output contract, built explicitly.
export class OrderResponseDto {
  readonly id!: string;
  readonly status!: string;
  readonly totalCents!: number;
  readonly createdAt!: string;

  static from(order: Order): OrderResponseDto {
    // Explicit mapping: adding a column to the entity cannot leak it to the API.
    return {
      id: order.id,
      status: order.status,
      totalCents: order.totalCents,
      createdAt: order.createdAt.toISOString(),
    };
  }
}
```

**Bad Example** — the entity used as both input and output

```ts
@Controller('orders')
export class OrdersController {
  @Post()
  async create(@Body() body: OrderEntity) {
    // The request body is typed as the entity, so a client can set `status`,
    // `totalCents`, `userId`, or any column the ORM maps. Nothing whitelists it.
    const order = await this.repo.save(body);

    // The response is the entity too: internal columns, soft-delete flags, and
    // whatever the next migration adds are all published automatically.
    return order;
  }

  @Patch(':id')
  async update(@Param('id') id: string, @Body() body: Partial<OrderEntity>) {
    // `Partial<Entity>` accepts every field as optional, so this endpoint quietly
    // allows changing the owner of an order.
    return this.repo.update(id, body);
  }
}
```

An entity carries persistence concerns and changes for persistence reasons. Publishing it as
the API contract means every schema change is a breaking API change — or a data leak.

---

## Common Mistakes

Avoid:

Returning Prisma models directly.

Returning TypeORM entities.

Sharing the same DTO for requests and responses.

Embedding business logic inside DTOs.

Skipping validation.

Duplicating mapping logic.

Leaking sensitive fields.

Treating DTOs as domain models.

---

## Completion Criteria

A DTO implementation is complete when:

- request and response models are separated;
- validation is comprehensive;
- ORM entities remain internal;
- mapping is centralized;
- serialization is predictable;
- the public API contract is stable and well documented.

---

## Summary

DTOs define the public language of a NestJS application.

By separating transport models from domain and persistence models, validating all incoming data, centralizing mapping, and carefully controlling serialization, applications become safer, easier to evolve, and more resilient to internal implementation changes.

## Related

- `knowledge/nestjs/08-validation.md`
- `knowledge/nestjs/12-pipes.md`
- `knowledge/nestjs/04-controllers.md`
- `knowledge/rest-api/06-request-response.md`
