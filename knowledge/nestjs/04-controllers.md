---
id: nestjs/04-controllers
topic: nestjs
slug: controllers
title: "NestJS Controllers"
type: doc
order: 4
status: ready
tags: [nestjs, controllers, Controller, IsOptional, Param, HttpCode, MinLength, UseGuards]
related: [nestjs/07-dto, nestjs/08-validation, nestjs/12-pipes, nestjs/05-services, rest-api/04-endpoints]
when_to_use: "Read before writing or reviewing any controller, route handler, or HTTP endpoint."
---
# NestJS Controllers

## Purpose

This document defines the engineering standards for designing Controllers in NestJS applications.

The objective is to build APIs that are predictable, maintainable, and easy to test by keeping controllers focused exclusively on handling HTTP communication.

Controllers should coordinate requests—not implement business logic.

---

## Core Principle

Controllers translate HTTP requests into application actions.

Business decisions belong in services.

---

## Controller Goals

Every controller should provide:

- clear routing;
- predictable HTTP behavior;
- request validation;
- consistent responses;
- minimal business logic;
- proper error propagation.

Controllers should remain thin.

---

## Responsibilities

Controllers are responsible for:

- defining routes;
- receiving requests;
- extracting request data;
- invoking services;
- returning responses.

Controllers should not contain business workflows.

---

## Request Lifecycle

A typical request follows this flow:

```
HTTP Request

↓

Middleware

↓

Guard

↓

Interceptor

↓

Pipe

↓

Controller

↓

Service

↓

Response
```

Each layer should perform a single responsibility.

---

## Routing

Routes should be:

- predictable;
- resource-oriented;
- versionable;
- RESTful.

Example:

```
GET     /users

GET     /users/:id

POST    /users

PATCH   /users/:id

DELETE  /users/:id
```

Avoid action-oriented URLs.

A thin, idiomatic controller declares routes with decorators, extracts data with
parameter decorators, and delegates every decision to a service. It holds no
business logic and reaches for no database.

```ts
// users.controller.ts
import {
  Controller,
  Get,
  Post,
  Patch,
  Delete,
  Param,
  Query,
  Body,
  HttpCode,
  HttpStatus,
  ParseIntPipe,
  UseGuards,
} from '@nestjs/common';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { PaginationQueryDto } from './dto/pagination-query.dto';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

@UseGuards(JwtAuthGuard) // authentication enforced for every route below
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll(@Query() query: PaginationQueryDto) {
    return this.usersService.findAll(query);
  }

  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number) {
    return this.usersService.findOne(id);
  }

  @Post() // Nest returns 201 for POST by default
  create(@Body() dto: CreateUserDto) {
    return this.usersService.create(dto);
  }

  @Patch(':id')
  update(
    @Param('id', ParseIntPipe) id: number,
    @Body() dto: UpdateUserDto,
  ) {
    return this.usersService.update(id, dto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT) // 204: no body on success
  async remove(@Param('id', ParseIntPipe) id: number): Promise<void> {
    await this.usersService.remove(id);
  }
}
```

The anti-pattern below inlines validation, database access, password hashing, and
manual response formatting. It also uses `@Res()`, which opts out of Nest's
response pipeline and breaks interceptors and exception filters.

```ts
// BAD: fat controller — business logic, DB access, and manual responses
import { Controller, Post, Req, Res } from '@nestjs/common';
import { Request, Response } from 'express';
import { DataSource } from 'typeorm';
import * as bcrypt from 'bcrypt';
import { User } from './user.entity';

@Controller('users')
export class UsersController {
  constructor(private readonly dataSource: DataSource) {}

  @Post()
  async create(@Req() req: Request, @Res() res: Response) {
    const body = req.body;
    if (!body.email) {
      return res.status(400).json({ error: 'email required' }); // manual validation
    }
    const repo = this.dataSource.getRepository(User);
    if (await repo.findOne({ where: { email: body.email } })) {
      return res.status(409).json({ error: 'exists' }); // business rule in controller
    }
    const password = await bcrypt.hash(body.password, 10); // business logic
    const user = await repo.save(repo.create({ ...body, password }));
    return res.status(201).json(user); // leaks the password hash to the client
  }
}
```

---

## Resource Naming

Use plural resource names.

Examples:

```
/users

/products

/orders

/payments
```

Avoid inconsistent naming conventions.

---

## HTTP Methods

Use HTTP methods according to their intent.

GET

- retrieve resources.

POST

- create resources.

PUT

- replace resources.

PATCH

- partially update resources.

DELETE

- remove resources.

Do not overload endpoints with unrelated behavior.

---

## Request Parameters

Extract request data explicitly.

Typical sources:

- path parameters;
- query parameters;
- request body;
- headers.

Avoid ambiguous parameter handling.

---

## DTO Usage

Every request body should use a DTO.

DTOs should define:

- expected fields;
- validation rules;
- transformation behavior.

Avoid accepting untyped objects.

Define the create DTO with `class-validator` decorators, then derive the update
DTO with `PartialType` so its fields become optional without duplication.

```ts
// dto/create-user.dto.ts
import {
  IsEmail,
  IsEnum,
  IsOptional,
  IsString,
  MaxLength,
  MinLength,
} from 'class-validator';

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
  @MinLength(8)
  password: string;

  @IsOptional()
  @IsEnum(UserRole)
  role?: UserRole;
}
```

```ts
// dto/update-user.dto.ts
import { PartialType } from '@nestjs/mapped-types';
import { CreateUserDto } from './create-user.dto';

// Every field of CreateUserDto, now optional and still validated.
export class UpdateUserDto extends PartialType(CreateUserDto) {}
```

---

## Validation

Validate incoming requests before reaching business logic.

Examples:

- required fields;
- formats;
- ranges;
- enums;
- nested objects.

Invalid requests should fail early.

Register `ValidationPipe` globally so DTO rules run on every request before any
handler executes. `whitelist` strips unknown properties, `forbidNonWhitelisted`
rejects them with a 400, and `transform` produces real DTO class instances.

```ts
// main.ts
import { ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // remove properties without a DTO decorator
      forbidNonWhitelisted: true, // 400 when unexpected properties are sent
      transform: true, // instantiate the DTO class and coerce primitive types
    }),
  );
  await app.listen(3000);
}
bootstrap();
```

---

## Response Structure

Responses should remain consistent.

Typical response contains:

- requested resource;
- status information;
- pagination metadata (when applicable).

Avoid returning inconsistent response shapes.

---

## Status Codes

Use appropriate HTTP status codes.

Typical examples:

- 200 OK
- 201 Created
- 204 No Content
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 409 Conflict
- 422 Unprocessable Entity
- 500 Internal Server Error

Status codes should accurately reflect the outcome.

---

## Error Handling

Controllers should not swallow exceptions.

Allow application-level exception handling to produce consistent responses.

Avoid custom error formatting inside individual controllers.

---

## Authentication

Authentication should be enforced through Guards.

Controllers should assume authenticated identity has already been established.

---

## Authorization

Authorization should verify resource access before executing business logic.

Authorization rules should remain centralized and reusable.

---

## Pagination

Collection endpoints should support pagination.

Typical parameters:

- page;
- limit;
- cursor;
- sort;
- filter.

Avoid returning unbounded collections.

Query strings arrive as text, so a pagination DTO must coerce and bound them.
`@Type(() => Number)` (with `transform: true` on the pipe) converts the raw
string, and `@Max` caps the page size to protect the database.

```ts
// dto/pagination-query.dto.ts
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

---

## Filtering

Filtering should be implemented using query parameters.

Examples:

```
GET /products?category=laptops

GET /orders?status=completed
```

Filtering behavior should remain predictable.

---

## Versioning

Public APIs should support versioning.

Example:

```
/v1/users

/v2/users
```

Versioning strategy should remain consistent throughout the application.

Enable URI versioning once at bootstrap, then declare the version per controller.

```ts
// main.ts
import { VersioningType } from '@nestjs/common';

app.enableVersioning({
  type: VersioningType.URI, // routes are prefixed with /v1, /v2, ...
  defaultVersion: '1',
});
```

```ts
// users.v2.controller.ts
import { Controller, Get } from '@nestjs/common';

@Controller({ path: 'users', version: '2' }) // serves GET /v2/users
export class UsersV2Controller {
  @Get()
  findAll() {
    return { data: [], version: 2 };
  }
}
```

---

## File Uploads

Controllers handling uploads should:

- validate file type;
- validate file size;
- reject invalid uploads;
- delegate storage to dedicated services.

Avoid embedding storage logic inside controllers.

Use `FileInterceptor` to receive the upload and `ParseFilePipe` to enforce size
and type before the handler runs. Storage itself is delegated to a service.

```ts
// avatars.controller.ts
import {
  Controller,
  Post,
  UploadedFile,
  UseInterceptors,
  ParseFilePipe,
  MaxFileSizeValidator,
  FileTypeValidator,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { AvatarsService } from './avatars.service';

@Controller('avatars')
export class AvatarsController {
  constructor(private readonly avatarsService: AvatarsService) {}

  @Post()
  @UseInterceptors(FileInterceptor('file'))
  upload(
    @UploadedFile(
      new ParseFilePipe({
        validators: [
          new MaxFileSizeValidator({ maxSize: 5 * 1024 * 1024 }), // 5 MB
          new FileTypeValidator({ fileType: /(jpe?g|png|webp)$/ }),
        ],
      }),
    )
    file: Express.Multer.File, // ambient type from @types/multer
  ) {
    return this.avatarsService.store(file);
  }
}
```

---

## Security

Controllers should:

- validate input;
- avoid exposing internal errors;
- never trust client input;
- protect sensitive endpoints.

Security should be enforced before business logic executes.

---

## Testing

Controllers should verify:

- routing;
- request validation;
- response codes;
- interaction with services.

Business rules should be tested within services rather than controllers.

A controller test provides a mock service and verifies delegation, not business
logic. Guards are replaced with `overrideGuard` so routing can be tested in
isolation.

```ts
// users.controller.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

describe('UsersController', () => {
  let controller: UsersController;
  const usersService = { findOne: jest.fn() };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [UsersController],
      providers: [{ provide: UsersService, useValue: usersService }],
    })
      .overrideGuard(JwtAuthGuard)
      .useValue({ canActivate: () => true })
      .compile();

    controller = module.get(UsersController);
  });

  it('delegates findOne to the service', async () => {
    const user = { id: 1, email: 'a@b.com' };
    usersService.findOne.mockResolvedValue(user);

    await expect(controller.findOne(1)).resolves.toEqual(user);
    expect(usersService.findOne).toHaveBeenCalledWith(1);
  });
});
```

---

## AI Execution Checklist

## Investigation

☐ Identify resource.

☐ Review API contract.

☐ Review validation rules.

☐ Review authorization requirements.

---

## Planning

☐ Create RESTful routes.

☐ Keep controller thin.

☐ Delegate business logic.

☐ Validate input.

---

## Verification

☐ Routes consistent.

☐ DTOs implemented.

☐ Status codes correct.

☐ Validation enforced.

☐ Authorization verified.

☐ Controller independently testable.

---

## Examples

**Good Example** — the controller translates HTTP and nothing else

```ts
@Controller('orders')
export class OrdersController {
  constructor(private readonly orders: OrdersService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @UseGuards(JwtAuthGuard)
  async create(
    @Body() dto: CreateOrderDto,          // validated by the global ValidationPipe
    @CurrentUser() user: AuthenticatedUser,
  ): Promise<OrderResponseDto> {
    const order = await this.orders.place(dto, user.id);
    return OrderResponseDto.from(order);  // never return the entity
  }

  @Get(':id')
  async findOne(@Param('id', ParseUUIDPipe) id: string): Promise<OrderResponseDto> {
    const order = await this.orders.findById(id);
    if (!order) {
      throw new NotFoundException(`Order ${id} not found`);
    }
    return OrderResponseDto.from(order);
  }
}
```

The same rule is reachable from a queue consumer or a CLI command, because it lives in
`OrdersService` rather than in the HTTP layer.

**Bad Example** — the controller is the application

```ts
@Controller('orders')
export class OrdersController {
  constructor(
    @InjectRepository(OrderEntity) private readonly repo: Repository<OrderEntity>,
    private readonly mailer: MailerService,
  ) {}

  @Post()
  async create(@Body() body: any, @Req() req: Request) {
    // Untyped body, hand-rolled validation, business rules, persistence, and a side
    // effect — all bound to HTTP and none of it reusable or unit-testable.
    if (!body.items || body.items.length === 0) {
      throw new HttpException('no items', 400);
    }

    let total = 0;
    for (const item of body.items) {
      total += item.price * item.qty;
    }
    if (total > 100_000 && !req.headers['x-approval']) {
      throw new HttpException('approval required', 403);
    }

    const order = await this.repo.save({ total, userId: (req as any).user.id });
    await this.mailer.sendMail({ to: (req as any).user.email, subject: 'Order placed' });

    return order;   // leaks every column, including internal ones
  }
}
```

---

## Common Mistakes

Avoid:

Placing business logic inside controllers.

Accessing the database directly.

Returning inconsistent response formats.

Skipping validation.

Creating action-based endpoints.

Performing authorization manually inside methods.

Duplicating validation logic.

---

## Completion Criteria

A controller implementation is complete when:

- routes follow REST principles;
- request validation is enforced;
- business logic is delegated to services;
- responses are consistent;
- authentication and authorization are integrated;
- the controller remains small, predictable, and testable.

---

## Summary

Controllers provide the entry point into a NestJS application.

By keeping controllers focused on HTTP communication, delegating business logic to services, validating every request, and exposing a consistent REST API, applications remain easier to maintain, extend, and test as they grow.

## Related

- `knowledge/nestjs/07-dto.md`
- `knowledge/nestjs/08-validation.md`
- `knowledge/nestjs/12-pipes.md`
- `knowledge/nestjs/05-services.md`
- `knowledge/rest-api/04-endpoints.md`
