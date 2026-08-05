---
id: nestjs/10-interceptors
topic: nestjs
slug: interceptors
title: "NestJS Interceptors"
type: doc
order: 10
status: ready
tags: [nestjs, interceptors]
related: [nestjs/09-guards, nestjs/11-exception-filters, nestjs/24-observability, nestjs/19-caching]
when_to_use: "Read before building or reviewing interceptors for logging, response shaping, tracing, or other cross-cutting request concerns."
---
# NestJS Interceptors

## Purpose

This document defines the engineering standards for implementing Interceptors in NestJS applications.

The objective is to centralize cross-cutting concerns such as logging, response transformation, performance measurement, tracing, caching, and auditing without polluting controllers or services.

Interceptors should extend request processing.

They should not contain business logic.

---

## Core Principle

Business logic belongs in services.

Cross-cutting concerns belong in interceptors.

---

## Interceptor Goals

Every interceptor should provide:

- reusable behavior;
- minimal coupling;
- predictable execution;
- framework consistency;
- centralized cross-cutting functionality.

---

## Request Lifecycle

Typical execution order:

```
Incoming Request

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

Controller Result

↓

Interceptors (after)

↓

Exception Filters

↓

HTTP Response
```

Interceptors execute both before and after controller execution.

---

## Responsibilities

Interceptors are responsible for:

- logging;
- response transformation;
- execution timing;
- distributed tracing;
- caching;
- audit logging;
- timeout handling;
- retry orchestration (where appropriate).

Interceptors should never implement business rules.

---

## Response Mapping

Interceptors may normalize responses.

An interceptor is a class annotated with `@Injectable()` that implements the
`NestInterceptor` interface. Its single `intercept(context, next)` method wraps
handler execution: `next.handle()` returns an RxJS `Observable` of the value the
controller returned, and RxJS operators piped onto it run *after* the handler
completes. To reshape every response, `map` the emitted value into an envelope:

```ts
// transform.interceptor.ts
import {
  CallHandler,
  ExecutionContext,
  Injectable,
  NestInterceptor,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface ApiResponse<T> {
  data: T;
  meta: { timestamp: string };
}

@Injectable()
export class TransformInterceptor<T>
  implements NestInterceptor<T, ApiResponse<T>>
{
  intercept(
    context: ExecutionContext,
    next: CallHandler<T>,
  ): Observable<ApiResponse<T>> {
    return next.handle().pipe(
      map((data) => ({
        data,
        meta: { timestamp: new Date().toISOString() },
      })),
    );
  }
}
```

Register it once, globally, using the `APP_INTERCEPTOR` token so it applies to
every route without touching controllers. Because it is provided through the DI
container, it can inject other providers:

```ts
// app.module.ts
import { Module } from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import { TransformInterceptor } from './transform.interceptor';

@Module({
  providers: [{ provide: APP_INTERCEPTOR, useClass: TransformInterceptor }],
})
export class AppModule {}
```

Response structure should remain consistent across the application.

Avoid formatting responses individually inside controllers.

Good — the controller returns a domain value and the interceptor wraps it:

```ts
@Get(':id')
async findOne(@Param('id') id: string): Promise<User> {
  return this.usersService.findOne(id); // interceptor adds { data, meta }
}
```

Bad — the controller hand-builds the envelope, so the shape drifts per route:

```ts
@Get(':id')
async findOne(@Param('id') id: string) {
  const user = await this.usersService.findOne(id);
  return { data: user, meta: { timestamp: Date.now() } }; // duplicated everywhere
}
```

---

## Logging

Centralize request logging.

Typical information:

- request ID;
- HTTP method;
- route;
- authenticated user ID;
- execution time;
- response status;
- client IP.

Avoid logging sensitive information.

Use the `tap` operator to observe the stream without altering the response, and
supply both `next` and `error` callbacks so timing is recorded whether the
handler succeeds or throws. `tap` never suppresses the error—it flows on to the
Exception Filters:

```ts
// logging.interceptor.ts
import {
  CallHandler,
  ExecutionContext,
  Injectable,
  Logger,
  NestInterceptor,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Request, Response } from 'express';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger(LoggingInterceptor.name);

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const http = context.switchToHttp();
    const request = http.getRequest<Request>();
    const { method, originalUrl } = request;
    const startedAt = Date.now();

    return next.handle().pipe(
      tap({
        next: () => {
          const status = http.getResponse<Response>().statusCode;
          this.logger.log(
            `${method} ${originalUrl} ${status} +${Date.now() - startedAt}ms`,
          );
        },
        error: (err: Error) => {
          this.logger.error(
            `${method} ${originalUrl} failed +${Date.now() - startedAt}ms: ${err.message}`,
          );
        },
      }),
    );
  }
}
```

---

## Correlation ID

Every request should receive a unique correlation ID.

Example flow:

```
Incoming Request

↓

Correlation ID

↓

Logs

↓

Database

↓

External APIs

↓

Response
```

The same identifier should appear in all related logs.

---

## Performance Monitoring

Measure:

- controller execution time;
- database latency (when available);
- external API latency;
- total request duration.

Performance data should be consistent and actionable.

---

## Audit Logging

Audit interceptors should record important business events.

Examples:

- user login;
- permission changes;
- payment approval;
- account deletion.

Audit logs should be immutable.

---

## Caching

Interceptors may coordinate response caching.

Suitable scenarios:

- read-heavy endpoints;
- public resources;
- expensive computations.

Caching strategy should remain centralized.

---

## Timeout Handling

Long-running requests should fail predictably.

Timeout interceptors should:

- cancel execution when appropriate;
- return meaningful errors;
- log timeout events.

Avoid allowing requests to run indefinitely.

The RxJS `timeout` operator aborts the stream after a deadline and emits a
`TimeoutError`. Translate only that error into a `408 Request Timeout` and
re-throw everything else unchanged so real errors still reach the Exception
Filters:

```ts
// timeout.interceptor.ts
import {
  CallHandler,
  ExecutionContext,
  Injectable,
  NestInterceptor,
  RequestTimeoutException,
} from '@nestjs/common';
import { Observable, TimeoutError, throwError } from 'rxjs';
import { catchError, timeout } from 'rxjs/operators';

@Injectable()
export class TimeoutInterceptor implements NestInterceptor {
  private readonly timeoutMs = 5000;

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    return next.handle().pipe(
      timeout(this.timeoutMs),
      catchError((error) => {
        if (error instanceof TimeoutError) {
          return throwError(() => new RequestTimeoutException());
        }
        // Not a timeout — propagate to the Exception Filters untouched.
        return throwError(() => error);
      }),
    );
  }
}
```

---

## Retry Strategy

Retries should be limited to transient failures.

Examples:

- temporary network failures;
- unavailable external services;
- retryable infrastructure errors.

Never retry operations that are not idempotent unless explicitly designed for it.

---

## Exception Propagation

Interceptors should allow exceptions to propagate to Exception Filters.

Avoid catching exceptions solely to suppress them.

---

## Tracing

Integrate distributed tracing when supported.

Typical trace information:

- request duration;
- service boundaries;
- database calls;
- external API calls.

Tracing should support production diagnostics.

---

## Metrics

Collect metrics such as:

- request count;
- average latency;
- success rate;
- failure rate;
- timeout count.

Metrics should support operational monitoring.

---

## Security

Never log:

- passwords;
- authentication tokens;
- API keys;
- payment information;
- personal data unless explicitly required.

Review every logged field.

---

## Controller Independence

Controllers should remain unaware of interceptors.

Business logic should not depend on interceptor behavior.

---

## Testing

Verify:

- logging behavior;
- response transformation;
- execution timing;
- cache behavior;
- timeout handling;
- tracing integration.

Interceptors should be independently testable.

---

## AI Execution Checklist

## Investigation

☐ Identify cross-cutting concern.

☐ Review request lifecycle.

☐ Review logging requirements.

☐ Review monitoring requirements.

---

## Planning

☐ Keep interceptor focused.

☐ Avoid business logic.

☐ Preserve request flow.

☐ Centralize reusable behavior.

---

## Verification

☐ Response mapping consistent.

☐ Logging complete.

☐ Correlation ID propagated.

☐ Performance measured.

☐ Exceptions propagated correctly.

☐ Sensitive data protected.

---

## Examples

**Good Example** — cross-cutting concerns, added once, transparent to controllers

```ts
@Injectable()
export class TimingInterceptor implements NestInterceptor {
  private readonly logger = new Logger(TimingInterceptor.name);

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const started = process.hrtime.bigint();
    const req = context.switchToHttp().getRequest<Request>();

    return next.handle().pipe(
      tap({
        // Runs on success and on error, so slow failures are measured too.
        finalize: () => {
          const ms = Number(process.hrtime.bigint() - started) / 1e6;
          this.logger.log({
            route: `${req.method} ${context.getHandler().name}`,
            durationMs: Math.round(ms),
            correlationId: req.headers['x-correlation-id'],
          });
        },
      }),
    );
  }
}
```

```ts
@Injectable()
export class TimeoutInterceptor implements NestInterceptor {
  intercept(_: ExecutionContext, next: CallHandler): Observable<unknown> {
    return next.handle().pipe(
      timeout(5_000),
      // Translate the RxJS timeout into a meaningful HTTP status; let everything
      // else propagate untouched so the exception filter can classify it.
      catchError((err) =>
        err instanceof TimeoutError
          ? throwError(() => new RequestTimeoutException())
          : throwError(() => err),
      ),
    );
  }
}
```

Both are registered once in the module and no controller mentions them.

**Bad Example** — an interceptor that swallows failures and rewrites meaning

```ts
@Injectable()
export class WrapEverythingInterceptor implements NestInterceptor {
  intercept(_: ExecutionContext, next: CallHandler): Observable<unknown> {
    return next.handle().pipe(
      map((data) => ({ success: true, data })),
      catchError((err) => {
        // Every failure becomes a 200 with success: false. Clients cannot use
        // status codes, retries never trigger, and monitoring sees no errors.
        console.log('error', err);
        return of({ success: false, data: null });
      }),
    );
  }
}
```

```ts
// The same handler re-run on every failure, including the ones that must not repeat.
return next.handle().pipe(retry(3));   // a failed charge is now three charges
```

Retrying indiscriminately turns a non-idempotent write into duplicated side effects. Retry
belongs where idempotency is guaranteed, not around every handler in the application.

---

## Common Mistakes

Avoid:

Putting business logic inside interceptors.

Logging sensitive information.

Formatting responses in every controller.

Swallowing exceptions.

Using interceptors for authorization.

Creating large, multi-purpose interceptors.

Ignoring correlation IDs.

---

## Completion Criteria

An interceptor implementation is complete when:

- it addresses a single cross-cutting concern;
- business logic remains outside the interceptor;
- logging and tracing are consistent;
- response transformation is centralized;
- sensitive information is protected;
- the interceptor is independently testable.

---

## Summary

Interceptors provide a powerful mechanism for implementing cross-cutting concerns in NestJS.

By centralizing logging, response transformation, tracing, performance monitoring, caching, and auditing while keeping business logic within services, applications remain cleaner, more maintainable, and easier to operate in production environments.

## Related

- `knowledge/nestjs/09-guards.md`
- `knowledge/nestjs/11-exception-filters.md`
- `knowledge/nestjs/24-observability.md`
- `knowledge/nestjs/19-caching.md`
