---
id: nestjs/13-middleware
topic: nestjs
slug: middleware
title: "NestJS Middleware"
type: doc
order: 13
status: ready
tags: [nestjs, middleware]
related: [nestjs/09-guards, nestjs/10-interceptors, nestjs/24-observability]
when_to_use: "Read before adding or reviewing middleware that preprocesses requests before they reach the NestJS pipeline."
---
# NestJS Middleware

## Purpose

This document defines the engineering standards for implementing Middleware in NestJS applications.

The objective is to process every incoming request before it reaches the NestJS execution pipeline, handling application-wide concerns that should execute independently of business logic.

Middleware is responsible for request preprocessing.

It should never implement business rules.

---

## Core Principle

Middleware runs before NestJS evaluates authentication, validation, or business logic.

Its responsibility is to prepare the request context.

NestJS supports two forms. A **functional middleware** is a plain
`(req, res, next)` function — ideal for dependency-free concerns registered
globally in `main.ts`. A **class middleware** is a class annotated with
`@Injectable()` that implements the `NestMiddleware` interface, so it can
receive providers through constructor injection and be wired per-route through
a module's `configure(consumer: MiddlewareConsumer)` method.

```typescript
// correlation-id.middleware.ts — functional form, no dependencies.
import { randomUUID } from 'node:crypto';
import { Request, Response, NextFunction } from 'express';
import { requestContextStorage } from './request-context';

export function correlationIdMiddleware(
  req: Request,
  res: Response,
  next: NextFunction,
): void {
  const incoming = req.headers['x-correlation-id'];
  const correlationId =
    typeof incoming === 'string' && incoming.length > 0
      ? incoming
      : randomUUID();

  // Echo the id back so clients and downstream services can correlate logs.
  res.setHeader('x-correlation-id', correlationId);

  // Run the remainder of the request inside an isolated async context.
  requestContextStorage.run({ correlationId }, () => next());
}
```

```typescript
// main.ts — register truly global middleware before the app listens.
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { correlationIdMiddleware } from './correlation-id.middleware';

async function bootstrap(): Promise<void> {
  const app = await NestFactory.create(AppModule);
  // Global middleware runs before Nest's router, so the correlation id is
  // available to every guard, interceptor, and handler that follows.
  app.use(correlationIdMiddleware);
  await app.listen(3000);
}

void bootstrap();
```

---

## Middleware Goals

Every middleware should provide:

- predictable execution;
- minimal overhead;
- reusable behavior;
- framework-independent logic where practical;
- consistent request preprocessing.

Middleware should remain lightweight.

---

## Request Lifecycle

```
Incoming Request

↓

Express / Fastify

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

Repository

↓

Interceptors (after)

↓

Exception Filters

↓

Response
```

Middleware is always the earliest application-level execution point.

---

## Responsibilities

Middleware is appropriate for:

- request preprocessing;
- Correlation ID generation;
- request context initialization;
- request logging;
- security headers;
- CORS handling;
- rate limiting integration;
- tenant resolution;
- request timing initialization.

Middleware should not:

- implement business logic;
- authorize users;
- validate DTOs;
- access repositories;
- execute workflows.

---

## Middleware vs Guards

Use Middleware when answering:

> How should this request be prepared?

Use Guards when answering:

> Is this request allowed?

Authentication belongs in Guards.

---

## Middleware vs Pipes

Middleware prepares the request.

Pipes validate and transform controller arguments.

They solve different problems.

---

## Middleware vs Interceptors

Middleware executes before NestJS routing.

Interceptors wrap controller execution.

Use each according to its lifecycle position.

---

## Middleware vs Exception Filters

Middleware should not format application errors.

Unhandled exceptions should propagate to Exception Filters.

---

## Correlation ID

Generate a unique identifier for every request.

Example:

```
Incoming Request

↓

Correlation ID

↓

Logger

↓

Database

↓

External APIs

↓

Response
```

Every log entry related to a request should include this identifier.

---

## Request Context

Initialize request-scoped context.

Typical context includes:

- request ID;
- authenticated user (after authentication);
- tenant;
- locale;
- timezone;
- client metadata.

Context should remain immutable whenever possible.

---

## AsyncLocalStorage

For request-scoped context, prefer AsyncLocalStorage.

Possible use cases:

- correlation IDs;
- audit logging;
- tracing;
- multi-tenant applications.

Avoid passing context manually through every method.

Define a single `AsyncLocalStorage` instance and the shape of the store, then
expose an injectable service so any provider can read the current context
without prop-drilling it through every method signature:

```typescript
// request-context.ts — one storage instance shared across the process.
import { AsyncLocalStorage } from 'node:async_hooks';

export interface RequestContext {
  correlationId: string;
  tenantId?: string;
}

export const requestContextStorage =
  new AsyncLocalStorage<RequestContext>();
```

```typescript
// request-context.service.ts — inject this wherever context is needed.
import { Injectable } from '@nestjs/common';
import { requestContextStorage } from './request-context';

@Injectable()
export class RequestContextService {
  getCorrelationId(): string | undefined {
    return requestContextStorage.getStore()?.correlationId;
  }

  getTenantId(): string | undefined {
    return requestContextStorage.getStore()?.tenantId;
  }
}
```

Because the correlation-id middleware wraps `next()` in
`requestContextStorage.run(...)`, every asynchronous continuation of that
request — services, repositories, and even `res.on('finish')` callbacks —
observes the same store.

---

## Request Logging

Middleware may log:

- HTTP method;
- URL;
- client IP;
- user agent;
- request start time.

Avoid logging sensitive request bodies.

A class middleware implements `NestMiddleware` and can inject providers. Here a
logger measures request duration and reads the correlation id from the context
service established earlier:

```typescript
// request-logger.middleware.ts
import { Injectable, Logger, NestMiddleware } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';
import { RequestContextService } from './request-context.service';

@Injectable()
export class RequestLoggerMiddleware implements NestMiddleware {
  private readonly logger = new Logger('HTTP');

  constructor(private readonly context: RequestContextService) {}

  use(req: Request, res: Response, next: NextFunction): void {
    const startedAt = process.hrtime.bigint();
    const { method, originalUrl } = req;

    // Log once the response is fully sent, not before the handler runs.
    res.on('finish', () => {
      const durationMs =
        Number(process.hrtime.bigint() - startedAt) / 1_000_000;
      this.logger.log(
        `${method} ${originalUrl} ${res.statusCode} ` +
          `${durationMs.toFixed(1)}ms ` +
          `correlationId=${this.context.getCorrelationId() ?? '-'}`,
      );
    });

    next();
  }
}
```

Because a class middleware participates in dependency injection, it is wired
through the owning module's `configure` method — not with `app.use()`. The
module implements `NestModule` and receives a `MiddlewareConsumer`:

```typescript
// app.module.ts
import { MiddlewareConsumer, Module, NestModule } from '@nestjs/common';
import { RequestContextService } from './request-context.service';
import { RequestLoggerMiddleware } from './request-logger.middleware';
import { UsersController } from './users.controller';

@Module({
  controllers: [UsersController],
  providers: [RequestContextService],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer): void {
    consumer
      .apply(RequestLoggerMiddleware)
      // Scope to a controller, specific paths, or use '*' for every route.
      .forRoutes(UsersController);
  }
}
```

---

## Security Headers

Configure security headers centrally.

Examples:

- Content Security Policy (CSP);
- Strict-Transport-Security;
- X-Content-Type-Options;
- Referrer-Policy;
- X-Frame-Options;
- Permissions-Policy.

Security headers should remain consistent.

---

## CORS

Configure CORS globally.

Review:

- allowed origins;
- credentials;
- allowed methods;
- allowed headers.

Avoid permissive production configurations.

---

## Rate Limiting

Middleware may integrate with rate limiting.

Typical dimensions:

- IP address;
- authenticated user;
- API key;
- tenant.

Rate limiting should protect application resources.

---

## Tenant Resolution

Multi-tenant applications may resolve tenant information in middleware.

Possible sources:

- subdomain;
- hostname;
- request header;
- JWT claims.

Never trust client input without verification.

---

## Request Size Limits

Reject oversized payloads early.

Configure limits appropriate to the application's requirements.

Avoid unnecessarily large request bodies.

---

## Compression

Enable compression for appropriate response types.

Avoid compressing already compressed assets.

---

## Performance

Middleware executes for every request.

Avoid:

- database queries;
- external API calls;
- expensive computations;
- unnecessary object allocation.

Keep execution fast.

---

## Error Handling

Middleware may reject malformed requests.

Do not centralize application error formatting here.

Allow Exception Filters to produce consistent responses.

---

## Testing

Verify:

- request preprocessing;
- correlation ID creation;
- context initialization;
- security headers;
- CORS configuration;
- rate limiting integration.

Middleware should be independently testable.

---

## AI Decision Matrix

Use Middleware for:

✓ Request context

✓ Logging

✓ Correlation ID

✓ Security headers

✓ CORS

✓ Tenant resolution

Do **not** use Middleware for:

✗ Business rules

✗ Authorization

✗ DTO validation

✗ Database queries

✗ External API orchestration

---

## AI Execution Checklist

## Investigation

☐ Identify request preprocessing needs.

☐ Review security requirements.

☐ Review logging requirements.

☐ Review request context.

---

## Planning

☐ Keep middleware lightweight.

☐ Initialize request context.

☐ Generate correlation ID.

☐ Configure security centrally.

---

## Verification

☐ No business logic.

☐ No authorization.

☐ No database access.

☐ Correlation ID propagated.

☐ Performance acceptable.

☐ Middleware independently testable.

---

## Examples

**Good Example** — middleware establishes request context; guards decide access

```ts
// A correlation id and a request-scoped store, available everywhere downstream
// without threading a parameter through every function.
export const requestContext = new AsyncLocalStorage<{ correlationId: string; userId?: string }>();

@Injectable()
export class CorrelationIdMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction): void {
    const correlationId = (req.headers['x-correlation-id'] as string) ?? randomUUID();
    res.setHeader('x-correlation-id', correlationId);

    // Everything inside next() — services, repositories, the logger — can read this.
    requestContext.run({ correlationId }, () => next());
  }
}

@Module({})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer): void {
    consumer.apply(helmet(), CorrelationIdMiddleware).forRoutes('*');
  }
}
```

**Bad Example** — authentication and authorization implemented in middleware

```ts
@Injectable()
export class AuthMiddleware implements NestMiddleware {
  async use(req: Request, res: Response, next: NextFunction) {
    const token = req.headers.authorization?.replace('Bearer ', '');
    (req as any).user = await this.jwt.verifyAsync(token!);

    // Middleware runs before the router resolves the handler, so there is no
    // ExecutionContext: no @Roles() metadata, no handler reference, no way to
    // ask "what does this route require?". The rule ends up hardcoded to paths.
    if (req.path.startsWith('/admin') && (req as any).user.role !== 'admin') {
      res.status(403).json({ error: 'forbidden' });
      return;                                   // silently ends the request
    }

    next();
  }
}
```

Path-prefix matching drifts from the routes the moment one is renamed or versioned. Guards
receive the `ExecutionContext`, can read decorator metadata, and are testable against a
handler rather than a URL string.

---

## Common Mistakes

Avoid:

Checking permissions.

Loading users from the database.

Calling external services.

Implementing business validation.

Creating request-scoped business objects.

Logging passwords or tokens.

Duplicating functionality already provided by Guards or Interceptors.

The most common failure is pulling authorization and database access into
middleware. That runs a query on every request, formats errors in the wrong
layer, and hides the security decision from the guard pipeline:

```typescript
// BAD: middleware performing authentication, a DB lookup, and authorization.
import { Injectable, NestMiddleware } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';
import { UserRepository } from './user.repository';

@Injectable()
export class AuthMiddleware implements NestMiddleware {
  constructor(private readonly users: UserRepository) {}

  async use(req: Request, res: Response, next: NextFunction): Promise<void> {
    const token = req.headers.authorization?.split(' ')[1];
    const user = await this.users.findByToken(token); // DB call per request
    if (!user || user.role !== 'admin') {
      res.status(403).json({ message: 'Forbidden' }); // wrong layer for errors
      return;
    }
    req['user'] = user;
    next();
  }
}
```

The middleware should only prepare context. Identity and permission checks
belong in guards (see `09-guards.md`), which return the correct status codes
and let exception filters format the response:

```typescript
// GOOD: middleware prepares context only; the guard authorizes.
import {
  CanActivate,
  ExecutionContext,
  Injectable,
  NestMiddleware,
} from '@nestjs/common';
import { randomUUID } from 'node:crypto';
import { Request, Response, NextFunction } from 'express';
import { requestContextStorage } from './request-context';

@Injectable()
export class CorrelationIdMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction): void {
    const incoming = req.headers['x-correlation-id'];
    const correlationId =
      typeof incoming === 'string' && incoming.length > 0
        ? incoming
        : randomUUID();
    res.setHeader('x-correlation-id', correlationId);
    requestContextStorage.run({ correlationId }, () => next());
  }
}

@Injectable()
export class AdminGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const req = context.switchToHttp().getRequest<Request>();
    const user = req['user'] as { roles: string[] } | undefined;
    return user?.roles.includes('admin') ?? false;
  }
}
```

---

## Completion Criteria

Middleware implementation is complete when:

- request preprocessing is centralized;
- request context is initialized;
- correlation IDs are propagated;
- security headers are configured;
- middleware remains lightweight;
- business logic is completely absent.

---

## Summary

Middleware is the application's first processing layer.

By limiting Middleware to request preprocessing, context initialization, logging, security configuration, and other cross-cutting concerns, NestJS applications maintain a clean execution pipeline where each framework component has a single, well-defined responsibility.

## Related

- `knowledge/nestjs/09-guards.md`
- `knowledge/nestjs/10-interceptors.md`
- `knowledge/nestjs/24-observability.md`
