---
id: nestjs/09-guards
topic: nestjs
slug: guards
title: "NestJS Guards"
type: doc
order: 9
status: ready
tags: [nestjs, guards]
related: []
when_to_use: "Read before writing or reviewing any guard that enforces authentication or access control on a route."
---
# NestJS Guards

## Purpose

This document defines the engineering standards for implementing authentication and authorization using Guards in NestJS applications.

The objective is to ensure every protected resource is accessed only by authorized identities while keeping authentication and authorization centralized, reusable, and independent from business logic.

Guards enforce access control.

They should not implement business workflows.

---

## Core Principle

Authenticate first.

Authorize second.

Execute business logic last.

---

## Guard Goals

Every Guard implementation should provide:

- centralized access control;
- reusable authorization logic;
- consistent behavior;
- minimal duplication;
- predictable request handling;
- security by default.

---

## Authentication vs Authorization

Authentication answers:

> Who is the user?

Authorization answers:

> What is the user allowed to do?

These concerns should always remain separate.

---

## Request Lifecycle

Typical request flow:

```
HTTP Request

↓

Middleware

↓

Authentication Guard

↓

Authorization Guard

↓

Interceptor

↓

Validation Pipe

↓

Controller

↓

Service
```

Authentication should complete before authorization begins.

---

## Authentication Guards

Authentication Guards verify identity.

Typical responsibilities:

- validate JWT access tokens;
- validate API keys;
- validate session cookies;
- attach authenticated user to the request.

Authentication Guards should not verify business permissions.

A Guard is a class annotated with `@Injectable()` that implements the
`CanActivate` interface. Returning `true` allows the request to proceed;
returning `false` (or throwing) rejects it. The example below validates a
bearer JWT and attaches the decoded principal to the request:

```typescript
// jwt-auth.guard.ts
import {
  CanActivate,
  ExecutionContext,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { Request } from 'express';

export interface AuthenticatedUser {
  sub: string;
  email: string;
  roles: string[];
}

@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(
    private readonly jwtService: JwtService,
    private readonly config: ConfigService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<Request>();
    const token = this.extractToken(request);

    if (!token) {
      throw new UnauthorizedException('Missing access token');
    }

    try {
      const payload = await this.jwtService.verifyAsync<AuthenticatedUser>(
        token,
        {
          secret: this.config.getOrThrow<string>('JWT_SECRET'),
          issuer: this.config.getOrThrow<string>('JWT_ISSUER'),
          audience: this.config.getOrThrow<string>('JWT_AUDIENCE'),
        },
      );
      // Attach the principal so downstream guards and handlers can read it.
      request['user'] = payload;
      return true;
    } catch {
      // Do not leak whether the token was expired, malformed, or forged.
      throw new UnauthorizedException('Invalid access token');
    }
  }

  private extractToken(request: Request): string | undefined {
    const [type, token] = request.headers.authorization?.split(' ') ?? [];
    return type === 'Bearer' ? token : undefined;
  }
}
```

Apply it to a route, a controller, or globally:

```typescript
// orders.controller.ts
import { Controller, Get, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from './jwt-auth.guard';

@UseGuards(JwtAuthGuard)
@Controller('orders')
export class OrdersController {
  @Get()
  findMine() {
    return { orders: [] };
  }
}
```

---

## Authorization Guards

Authorization Guards verify permissions.

Examples:

- administrator access;
- resource ownership;
- subscription level;
- feature access;
- tenant isolation.

Authorization decisions should remain centralized.

---

## RBAC

Role-Based Access Control assigns permissions through roles.

Example:

```
Admin

↓

Users

Orders

Reports
```

RBAC is appropriate when permissions are relatively stable.

Roles required by a handler are declared with a custom metadata decorator and
read back inside an authorization Guard via `Reflector`. Use
`getAllAndOverride` so a method-level `@Roles()` overrides a controller-level
one:

```typescript
// roles.decorator.ts
import { Reflector } from '@nestjs/core';

export const Roles = Reflector.createDecorator<string[]>();
```

```typescript
// roles.guard.ts
import {
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  Injectable,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { Roles } from './roles.decorator';
import type { AuthenticatedUser } from './jwt-auth.guard';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride(Roles, [
      context.getHandler(),
      context.getClass(),
    ]);

    // No @Roles metadata means this handler has no role requirement.
    if (!requiredRoles || requiredRoles.length === 0) {
      return true;
    }

    const request = context.switchToHttp().getRequest();
    const user = request.user as AuthenticatedUser | undefined;

    // Authentication must run first; without a principal there is nothing
    // to authorize.
    if (!user) {
      throw new ForbiddenException('Missing authenticated principal');
    }

    const allowed = requiredRoles.some((role) => user.roles.includes(role));
    if (!allowed) {
      throw new ForbiddenException('Insufficient role');
    }
    return true;
  }
}
```

```typescript
// admin.controller.ts
import { Controller, Delete, Param, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from './jwt-auth.guard';
import { RolesGuard } from './roles.guard';
import { Roles } from './roles.decorator';

// Guards run left to right: authenticate, then authorize.
@UseGuards(JwtAuthGuard, RolesGuard)
@Controller('admin/users')
export class AdminUsersController {
  @Roles(['admin'])
  @Delete(':id')
  remove(@Param('id') id: string) {
    return { deleted: id };
  }
}
```

The role list comes only from the verified token, never from a request body
or header.

---

## ABAC

Attribute-Based Access Control evaluates attributes.

Examples:

- department;
- organization;
- subscription;
- resource status;
- ownership.

ABAC provides more flexibility than RBAC.

---

## Ownership Validation

Ownership determines whether a user may access a resource.

Example:

```
User

↓

Own Order

↓

Allowed
```

```
User

↓

Another User's Order

↓

Denied
```

Ownership checks belong in authorization logic—not controllers.

**Bad** — ownership logic tangled into the controller and easy to forget on
the next endpoint:

```typescript
// orders.controller.ts (Bad)
@Get(':id')
async findOne(@Param('id') id: string, @Req() req: Request) {
  const order = await this.orders.findById(id);
  // Access-control logic duplicated into every handler.
  if (order.userId !== (req.user as AuthenticatedUser).sub) {
    throw new ForbiddenException();
  }
  return order;
}
```

**Good** — a dedicated Guard performs the ownership check. A Guard may inject
services, so it can load the resource and compare it to the principal. Throw
`NotFoundException` instead of `ForbiddenException` when hiding a resource's
existence matters:

```typescript
// order-owner.guard.ts (Good)
import {
  CanActivate,
  ExecutionContext,
  Injectable,
  NotFoundException,
} from '@nestjs/common';
import { OrdersService } from './orders.service';
import type { AuthenticatedUser } from './jwt-auth.guard';

@Injectable()
export class OrderOwnerGuard implements CanActivate {
  constructor(private readonly orders: OrdersService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const user = request.user as AuthenticatedUser;
    const order = await this.orders.findById(request.params.id);

    if (!order || order.userId !== user.sub) {
      // Return 404 rather than 403 so non-owners cannot probe for
      // existing resource IDs.
      throw new NotFoundException('Order not found');
    }

    // Cache the loaded entity so the handler need not re-query it.
    request.order = order;
    return true;
  }
}
```

```typescript
// orders.controller.ts (Good)
@UseGuards(JwtAuthGuard, OrderOwnerGuard)
@Get(':id')
findOne(@Req() req: Request) {
  return req['order'];
}
```

---

## Layer Responsibilities

Authentication Guard

Responsible for:

- identity verification;
- token validation;
- attaching principal information.

Authorization Guard

Responsible for:

- permission evaluation;
- policy enforcement;
- ownership checks.

Service

Responsible for:

- business rules.

Keep responsibilities separate.

---

## Composite Guards

Multiple Guards may be combined.

Example:

```
JWT Guard

↓

Verified Email Guard

↓

Subscription Guard

↓

Admin Guard
```

Each Guard should solve one problem.

---

## Policies

Complex authorization should use reusable policy objects.

Policies should:

- remain testable;
- avoid framework dependencies;
- express business permissions clearly.

Avoid embedding complex permission logic directly inside Guards.

---

## Resource Protection

Protect:

- REST endpoints;
- GraphQL resolvers;
- WebSocket gateways;
- background management endpoints.

Every public entry point should be evaluated.

---

## Public Endpoints

Explicitly mark public routes.

Avoid relying on missing Guards to indicate public access.

Public access should always be intentional.

The safest default is a globally registered authentication Guard plus an
explicit `@Public()` opt-out, so a forgotten decorator fails closed (protected)
rather than open. Register the Guard with `APP_GUARD` and teach it to honor the
metadata:

```typescript
// public.decorator.ts
import { Reflector } from '@nestjs/core';

export const Public = Reflector.createDecorator<boolean>();
```

```typescript
// jwt-auth.guard.ts
// Inject Reflector alongside JwtService/ConfigService, then check the
// metadata at the top of canActivate:
canActivate(context: ExecutionContext) {
  const isPublic = this.reflector.getAllAndOverride(Public, [
    context.getHandler(),
    context.getClass(),
  ]);
  if (isPublic) {
    return true;
  }
  // ...token verification as shown earlier
}
```

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { JwtAuthGuard } from './jwt-auth.guard';

@Module({
  providers: [
    // Every route is authenticated unless it opts out with @Public().
    { provide: APP_GUARD, useClass: JwtAuthGuard },
  ],
})
export class AppModule {}
```

```typescript
// auth.controller.ts
import { Controller, Post } from '@nestjs/common';
import { Public } from './public.decorator';

@Controller('auth')
export class AuthController {
  @Public()
  @Post('login')
  login() {
    return { accessToken: '...' };
  }
}
```

Registering the Guard via `APP_GUARD` keeps it in the DI container, so it can
inject `JwtService`, `ConfigService`, or `Reflector` normally.

---

## Error Responses

Unauthorized identity:

```
401 Unauthorized
```

Authenticated but insufficient permission:

```
403 Forbidden
```

Use status codes consistently.

---

## Performance

Permission evaluation should remain efficient.

Avoid:

- repeated database queries;
- duplicated permission calculations;
- unnecessary external requests.

Cache authorization data when appropriate.

---

## Multi-Tenant Applications

Authorization should verify:

- tenant membership;
- tenant ownership;
- resource isolation.

Never trust client-provided tenant identifiers.

---

## External Identity Providers

Authentication may integrate with:

- OAuth providers;
- OpenID Connect;
- enterprise identity systems;
- SAML providers.

Business authorization should remain independent of identity provider implementation.

---

## Security

Always verify:

- token integrity;
- token expiration;
- issuer;
- audience;
- required permissions.

Never trust client-provided roles or permissions.

---

## Testing

Verify:

- authenticated access;
- unauthenticated access;
- authorized access;
- forbidden access;
- ownership rules;
- policy evaluation.

Authorization should remain deterministic.

---

## AI Execution Checklist

## Investigation

☐ Identify protected resources.

☐ Separate authentication from authorization.

☐ Review permission model.

☐ Review ownership rules.

---

## Planning

☐ Implement authentication Guards.

☐ Implement authorization Guards.

☐ Reuse policies.

☐ Keep Guards focused.

---

## Verification

☐ Authentication isolated.

☐ Authorization centralized.

☐ Ownership enforced.

☐ Status codes correct.

☐ Public endpoints explicit.

☐ Guards independently testable.

---

## Common Mistakes

Avoid:

Checking permissions inside controllers.

Combining authentication and authorization into one Guard.

Trusting client-provided roles.

Performing business workflows inside Guards.

Duplicating permission logic.

Skipping ownership verification.

Returning incorrect HTTP status codes.

---

## Completion Criteria

A Guard implementation is complete when:

- authentication and authorization are separated;
- permissions are evaluated consistently;
- ownership is enforced where required;
- policies are reusable;
- protected resources are secured;
- Guards remain independently testable.

---

## Summary

Guards provide the primary security boundary for NestJS applications.

By separating identity verification from permission evaluation, centralizing authorization logic, enforcing ownership, and keeping Guards focused on access control, applications become significantly more secure, maintainable, and easier to evolve.