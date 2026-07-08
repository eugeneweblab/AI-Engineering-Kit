---
id: nestjs/11-exception-filters
topic: nestjs
slug: exception-filters
title: "NestJS Exception Filters"
type: doc
order: 11
status: ready
tags: [nestjs, exception-filters]
related: []
when_to_use: "Read before building or reviewing exception filters and application-wide error handling."
---
# NestJS Exception Filters

## Purpose

This document defines the engineering standards for handling exceptions in NestJS applications.

The objective is to provide consistent, secure, and observable error handling across the entire application while separating business errors from infrastructure failures.

Exception Filters define how errors leave the application.

They should never contain business logic.

---

## Core Principle

Fail predictably.

Every error should produce a consistent response.

---

## Error Handling Goals

Every application should provide:

- consistent error responses;
- secure error messages;
- centralized error handling;
- structured logging;
- traceability;
- observability.

Errors should be understandable by both humans and machines.

---

## Error Flow

Typical execution flow:

```
Request

↓

Controller

↓

Service

↓

Repository

↓

Exception

↓

Exception Filter

↓

HTTP Response
```

All unhandled exceptions should pass through a centralized filter.

---

## Error Categories

Separate errors into categories.

## Validation Errors

Examples:

- invalid input;
- malformed request;
- missing required field.

Return:

```
400 Bad Request
```

or

```
422 Unprocessable Entity
```

---

## Authentication Errors

Examples:

- missing token;
- invalid token;
- expired token.

Return:

```
401 Unauthorized
```

---

## Authorization Errors

Examples:

- insufficient permissions;
- ownership violation.

Return:

```
403 Forbidden
```

---

## Resource Errors

Examples:

- user not found;
- product not found;
- order not found.

Return:

```
404 Not Found
```

---

## Business Errors

Examples:

- insufficient balance;
- duplicate email;
- invalid order state.

Return the status code that best represents the business failure.

---

## Infrastructure Errors

Examples:

- database unavailable;
- cache unavailable;
- external API timeout;
- message broker failure.

Return an appropriate server error.

Avoid exposing infrastructure details.

---

## Unexpected Errors

Unexpected exceptions should return:

```
500 Internal Server Error
```

Clients should never receive stack traces.

---

## Error Response Structure

Responses should remain consistent.

Example:

```json
{
  "status": 404,
  "code": "USER_NOT_FOUND",
  "message": "User was not found.",
  "requestId": "...",
  "timestamp": "...",
  "path": "/users/15"
}
```

Every response should follow the same structure.

A single global filter produces exactly this shape for every error. Catching
`unknown` (with a bare `@Catch()`) makes it the last-resort handler for both
`HttpException` subclasses and unexpected throws.

```ts
// filters/all-exceptions.filter.ts
import {
  ArgumentsHost,
  Catch,
  ExceptionFilter,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';
import { randomUUID } from 'node:crypto';

interface ErrorResponseBody {
  status: number;
  code: string;
  message: string;
  requestId: string;
  timestamp: string;
  path: string;
}

@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  private readonly logger = new Logger(AllExceptionsFilter.name);

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    const requestId =
      (request.headers['x-request-id'] as string | undefined) ?? randomUUID();

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let code = 'INTERNAL_ERROR';
    let message = 'An unexpected error occurred.';

    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const payload = exception.getResponse();

      if (typeof payload === 'string') {
        message = payload;
        code = this.codeFromStatus(status);
      } else if (typeof payload === 'object' && payload !== null) {
        const body = payload as Record<string, unknown>;
        code =
          typeof body.code === 'string' ? body.code : this.codeFromStatus(status);
        // Built-in exceptions (and ValidationPipe) may set `message`
        // to a string or an array of strings.
        const raw = body.message;
        message = Array.isArray(raw) ? raw.join(', ') : String(raw ?? message);
      }
    }

    // Only unexpected (5xx) failures deserve a full stack trace in the logs.
    // Expected 4xx errors are logged at a lower level without internals.
    if (status >= HttpStatus.INTERNAL_SERVER_ERROR) {
      this.logger.error(
        `[${requestId}] ${request.method} ${request.url} -> ${status}`,
        exception instanceof Error ? exception.stack : String(exception),
      );
    } else {
      this.logger.warn(
        `[${requestId}] ${request.method} ${request.url} -> ${status} ${code}`,
      );
    }

    const responseBody: ErrorResponseBody = {
      status,
      code,
      message,
      requestId,
      timestamp: new Date().toISOString(),
      path: request.url,
    };

    response.status(status).json(responseBody);
  }

  private codeFromStatus(status: number): string {
    switch (status) {
      case HttpStatus.BAD_REQUEST:
        return 'VALIDATION_ERROR';
      case HttpStatus.UNAUTHORIZED:
        return 'UNAUTHENTICATED';
      case HttpStatus.FORBIDDEN:
        return 'FORBIDDEN';
      case HttpStatus.NOT_FOUND:
        return 'NOT_FOUND';
      case HttpStatus.CONFLICT:
        return 'CONFLICT';
      default:
        return 'ERROR';
    }
  }
}
```

Register it once, application-wide, using the `APP_FILTER` token so Nest can
inject dependencies into it if needed. Prefer this over
`app.useGlobalFilters(new AllExceptionsFilter())`, which cannot use DI.

```ts
// app.module.ts
import { Module } from '@nestjs/common';
import { APP_FILTER } from '@nestjs/core';
import { AllExceptionsFilter } from './filters/all-exceptions.filter';

@Module({
  providers: [{ provide: APP_FILTER, useClass: AllExceptionsFilter }],
})
export class AppModule {}
```

Every response should follow the same structure.

---

## Error Codes

Every business error should have a stable code.

Examples:

```
USER_NOT_FOUND

EMAIL_ALREADY_EXISTS

ORDER_ALREADY_PAID

INSUFFICIENT_PERMISSIONS
```

Clients should depend on codes rather than localized messages.

---

## Correlation ID

Every error should include the request identifier.

Example:

```
requestId

↓

Logs

↓

Tracing

↓

Monitoring
```

This enables production debugging.

---

## Logging

Unexpected errors should be logged.

Include:

- request ID;
- route;
- authenticated user (when available);
- stack trace;
- execution time.

Never log sensitive information.

---

## Sensitive Data

Never expose:

- stack traces;
- SQL queries;
- passwords;
- tokens;
- API keys;
- internal implementation details.

Clients should receive safe error messages.

---

## Domain Exceptions

Business rules should throw domain-specific exceptions.

Model them as a small hierarchy that extends `HttpException` so the framework
still knows the HTTP status, while carrying a stable machine-readable `code`.

```ts
// domain/exceptions/domain.exception.ts
import { HttpException, HttpStatus } from '@nestjs/common';

export abstract class DomainException extends HttpException {
  protected constructor(
    public readonly code: string,
    message: string,
    status: HttpStatus,
  ) {
    // The object passed to super() becomes HttpException.getResponse(),
    // so the filter can read `code` and `message` back out.
    super({ code, message }, status);
  }
}

export class UserNotFoundException extends DomainException {
  constructor(userId: string) {
    super('USER_NOT_FOUND', `User ${userId} was not found.`, HttpStatus.NOT_FOUND);
  }
}

export class EmailAlreadyExistsException extends DomainException {
  constructor(email: string) {
    super(
      'EMAIL_ALREADY_EXISTS',
      `Email ${email} is already registered.`,
      HttpStatus.CONFLICT,
    );
  }
}

export class InsufficientBalanceException extends DomainException {
  constructor() {
    super(
      'INSUFFICIENT_BALANCE',
      'Account balance is insufficient for this operation.',
      HttpStatus.UNPROCESSABLE_ENTITY,
    );
  }
}
```

Avoid generic exceptions for business failures.

Compare how the two approaches read at the point where the rule is enforced:

```ts
import { Injectable } from '@nestjs/common';
import { UserNotFoundException } from '../domain/exceptions/domain.exception';

@Injectable()
export class UsersService {
  constructor(private readonly users: UserRepository) {}

  // Bad — a generic Error becomes a raw 500 with no stable code, and the
  // message leaks an internal table name to the client.
  async findByIdBad(id: string): Promise<User> {
    const user = await this.users.findOne({ where: { id } });
    if (!user) {
      throw new Error(`No row in "users" table for id=${id}`);
    }
    return user;
  }

  // Good — a typed domain exception carries the status (404) and a stable
  // code (USER_NOT_FOUND) that the filter turns into a safe response.
  async findById(id: string): Promise<User> {
    const user = await this.users.findOne({ where: { id } });
    if (!user) {
      throw new UserNotFoundException(id);
    }
    return user;
  }
}
```

---

## Infrastructure Exceptions

Infrastructure adapters should translate low-level failures into application-level exceptions.

Avoid leaking ORM or SDK-specific exceptions.

---

## Retryable Errors

Some failures may be retried.

Examples:

- temporary network failure;
- timeout;
- unavailable third-party service.

Business conflicts generally should not be retried automatically.

---

## API Consistency

Every endpoint should return errors using the same structure.

Consistency simplifies client implementation.

---

## GraphQL

GraphQL applications should translate internal exceptions into GraphQL-compatible responses while preserving error codes.

---

## WebSockets

WebSocket gateways should use the same domain exception strategy.

Transport changes.

Business errors do not.

---

## Observability

Exception Filters should integrate with:

- centralized logging;
- distributed tracing;
- monitoring;
- alerting.

Unexpected failures should always be observable.

---

## Testing

Verify:

- expected exceptions;
- unexpected exceptions;
- error response format;
- sensitive data protection;
- correlation ID propagation.

Error handling should remain deterministic.

---

## AI Execution Checklist

## Investigation

☐ Identify error categories.

☐ Review business failures.

☐ Review infrastructure failures.

☐ Review API contract.

---

## Planning

☐ Centralize exception handling.

☐ Define stable error codes.

☐ Protect sensitive data.

☐ Log unexpected failures.

---

## Verification

☐ Responses consistent.

☐ Error codes stable.

☐ Correlation ID included.

☐ Sensitive information protected.

☐ Logging complete.

☐ Exception handling independently testable.

---

## Common Mistakes

Avoid:

Returning stack traces.

Exposing SQL errors.

Throwing generic exceptions everywhere.

Logging passwords or tokens.

Using inconsistent response formats.

Returning different structures from different controllers.

Ignoring correlation IDs.

---

## Completion Criteria

Exception handling is complete when:

- all unhandled exceptions pass through centralized filters;
- error responses are consistent;
- business and infrastructure errors are separated;
- sensitive information is never exposed;
- structured logging and tracing are integrated;
- clients can reliably handle error codes.

---

## Summary

Exception Filters define the application's error boundary.

By centralizing exception handling, separating business failures from infrastructure errors, protecting sensitive information, and producing consistent error responses, NestJS applications become more secure, easier to debug, and more reliable in production.