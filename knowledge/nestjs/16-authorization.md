---
id: nestjs/16-authorization
topic: nestjs
slug: authorization
title: "NestJS Authorization"
type: doc
order: 16
status: ready
tags: [nestjs, authorization]
related: []
when_to_use: "Read before building or reviewing roles, permissions, or any code that decides what an authenticated user may do."
---
# NestJS Authorization

## Purpose

This document defines the engineering standards for implementing authorization in NestJS applications.

The objective is to determine whether an authenticated identity is allowed to perform a specific action on a specific resource while keeping authorization centralized, consistent, and independent from authentication.

Authentication identifies users.

Authorization determines permissions.

---

## Core Principle

Never trust authenticated users automatically.

Every protected action must be authorized.

---

## Authorization Goals

Every authorization system should provide:

- centralized policy evaluation;
- consistent permission enforcement;
- reusable authorization logic;
- least privilege access;
- auditability;
- scalability.

Authorization should be deterministic and explicit.

---

## Authorization Flow

```
Request

↓

Authentication

↓

Authenticated Identity

↓

Authorization Policy

↓

Business Logic

↓

Response
```

Business logic should execute only after authorization succeeds.

---

## Responsibilities

Authorization is responsible for:

- permission evaluation;
- role evaluation;
- ownership verification;
- tenant isolation;
- policy enforcement;
- resource access decisions.

Authorization should not:

- authenticate users;
- validate passwords;
- issue tokens;
- implement business workflows.

---

## Authorization Models

Choose the simplest model that satisfies application requirements.

---

## Role-Based Access Control (RBAC)

Permissions are assigned to roles.

Example:

```
Administrator

↓

Create User

Delete User

Manage Roles
```

Suitable for applications with stable permission models.

In NestJS, RBAC is implemented with a metadata decorator plus a guard. The
decorator declares the required roles on a handler; the guard reads them with
`Reflector` and compares them against the authenticated identity. This keeps
role checks out of controllers and business services.

```typescript
// roles.enum.ts
export enum Role {
  Admin = 'admin',
  Manager = 'manager',
  Customer = 'customer',
}
```

```typescript
// roles.decorator.ts
import { SetMetadata } from '@nestjs/common';
import { Role } from './roles.enum';

export const ROLES_KEY = 'roles';
export const Roles = (...roles: Role[]) => SetMetadata(ROLES_KEY, roles);
```

```typescript
// roles.guard.ts
import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { ROLES_KEY } from './roles.decorator';
import { Role } from './roles.enum';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    // getAllAndOverride merges handler + class metadata, letting a method
    // override the controller-level roles.
    const requiredRoles = this.reflector.getAllAndOverride<Role[]>(ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);

    // No @Roles on this route: this guard makes no decision here.
    if (!requiredRoles || requiredRoles.length === 0) {
      return true;
    }

    // `user` is attached by the authentication guard that runs first.
    const { user } = context.switchToHttp().getRequest();
    return requiredRoles.some((role) => user?.roles?.includes(role));
  }
}
```

```typescript
// users.controller.ts
import { Body, Controller, Delete, Param, Post, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { RolesGuard } from './roles.guard';
import { Roles } from './roles.decorator';
import { Role } from './roles.enum';

// Authentication runs before authorization: JwtAuthGuard populates
// request.user, then RolesGuard evaluates the required roles.
@Controller('users')
@UseGuards(JwtAuthGuard, RolesGuard)
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  @Roles(Role.Admin)
  create(@Body() dto: CreateUserDto) {
    return this.usersService.create(dto);
  }

  @Delete(':id')
  @Roles(Role.Admin)
  remove(@Param('id') id: string) {
    return this.usersService.remove(id);
  }
}
```

---

## Attribute-Based Access Control (ABAC)

Permissions depend on attributes.

Examples:

- department;
- subscription plan;
- region;
- account status;
- project membership.

ABAC provides greater flexibility than RBAC.

---

## Relationship-Based Access Control (ReBAC)

Permissions depend on relationships.

Examples:

- document owner;
- project member;
- organization administrator;
- repository collaborator.

ReBAC is well suited for collaborative systems.

---

## Ownership Authorization

Ownership is one of the most common authorization rules.

Example:

```
Authenticated User

↓

Own Resource

↓

Allow
```

```
Authenticated User

↓

Another User's Resource

↓

Deny
```

Ownership validation belongs in authorization policies—not controllers.

Ownership requires loading the resource, so it is enforced in a dedicated guard
that fetches the record and compares it against the authenticated identity.

**Bad — ownership check tangled inside the controller/service:**

```typescript
// orders.controller.ts — authorization mixed into business logic
@Controller('orders')
@UseGuards(JwtAuthGuard)
export class OrdersController {
  constructor(private readonly orders: OrdersService) {}

  @Get(':id')
  async findOne(@Param('id') id: string, @Req() req: Request) {
    const order = await this.orders.findById(id);
    // Ownership logic duplicated in every handler, easy to forget,
    // and impossible to reuse or test in isolation.
    if (order.customerId !== (req.user as AuthUser).id) {
      throw new ForbiddenException();
    }
    return order;
  }
}
```

**Good — ownership enforced in a reusable guard:**

```typescript
// order-ownership.guard.ts
import {
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  Injectable,
  NotFoundException,
} from '@nestjs/common';
import { OrdersService } from './orders.service';
import { Role } from '../users/roles.enum';

@Injectable()
export class OrderOwnershipGuard implements CanActivate {
  constructor(private readonly orders: OrdersService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const user = request.user;
    const order = await this.orders.findById(request.params.id);

    if (!order) {
      throw new NotFoundException('Order not found');
    }

    // Admins bypass ownership; everyone else must own the resource.
    if (order.customerId !== user.id && !user.roles.includes(Role.Admin)) {
      throw new ForbiddenException('You do not have access to this order');
    }

    return true;
  }
}
```

```typescript
// orders.controller.ts — handler stays free of authorization logic
@Controller('orders')
export class OrdersController {
  constructor(private readonly orders: OrdersService) {}

  @Get(':id')
  @UseGuards(JwtAuthGuard, OrderOwnershipGuard)
  findOne(@Param('id') id: string) {
    return this.orders.findById(id);
  }
}
```

---

## Policy-Based Authorization

Prefer policies over scattered permission checks.

Example:

```
OrderPolicy

↓

canRead()

canUpdate()

canCancel()

canRefund()
```

Policies should express business permissions clearly.

For anything beyond flat roles, centralize the rules in a single ability
definition rather than scattering `if` checks. CASL (`@casl/ability`) is the
common choice; the factory below returns the complete permission set for a user,
and a guard reuses it everywhere.

```typescript
// casl-ability.factory.ts
import { AbilityBuilder, createMongoAbility, MongoAbility } from '@casl/ability';
import { Injectable } from '@nestjs/common';
import { Role } from '../users/roles.enum';

export type Action = 'manage' | 'create' | 'read' | 'update' | 'delete';
export type Subject = 'User' | 'Order' | 'Report' | 'all';
export type AppAbility = MongoAbility<[Action, Subject]>;

interface AuthUser {
  id: string;
  roles: Role[];
}

@Injectable()
export class CaslAbilityFactory {
  createForUser(user: AuthUser): AppAbility {
    const { can, build } = new AbilityBuilder<AppAbility>(createMongoAbility);

    if (user.roles.includes(Role.Admin)) {
      can('manage', 'all'); // 'manage' == every action
    } else if (user.roles.includes(Role.Manager)) {
      can(['read', 'update'], 'Order');
      can('read', 'Report');
    } else {
      can('read', 'Order');
      can('create', 'Order');
    }

    return build();
  }
}
```

```typescript
// order-policy.guard.ts
import {
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  Injectable,
} from '@nestjs/common';
import { CaslAbilityFactory } from './casl-ability.factory';

@Injectable()
export class UpdateOrderPolicyGuard implements CanActivate {
  constructor(private readonly abilityFactory: CaslAbilityFactory) {}

  canActivate(context: ExecutionContext): boolean {
    const { user } = context.switchToHttp().getRequest();
    const ability = this.abilityFactory.createForUser(user);

    if (ability.cannot('update', 'Order')) {
      throw new ForbiddenException('Insufficient permissions');
    }

    return true;
  }
}
```

Register `CaslAbilityFactory` as a provider so it can be injected into guards:

```typescript
// authorization.module.ts
import { Module } from '@nestjs/common';
import { CaslAbilityFactory } from './casl-ability.factory';

@Module({
  providers: [CaslAbilityFactory],
  exports: [CaslAbilityFactory],
})
export class AuthorizationModule {}
```

---

## Permission Matrix

Document permissions explicitly.

Example:

| Role | Users | Orders | Reports |
|------|------|------|------|
| Admin | Full | Full | Full |
| Manager | Read | Manage | Read |
| Customer | Own Only | Own Only | None |

Permission matrices improve maintainability.

---

## Multi-Tenant Authorization

Every request should verify tenant boundaries.

Typical checks:

- tenant membership;
- tenant ownership;
- organization hierarchy;
- resource isolation.

Never trust tenant identifiers supplied by clients.

---

## Resource-Level Authorization

Authorization should evaluate both:

- user;
- resource.

Permission depends on context.

Example:

```
User A

↓

Document B

↓

Update?

↓

Policy Evaluation
```

---

## Least Privilege

Grant only the permissions required.

Avoid:

- administrator by default;
- wildcard permissions;
- unnecessary global access.

Least privilege reduces security risk.

---

## Default Deny

If no authorization rule grants access:

```
Deny
```

Default deny should be the application's security posture.

---

## Frontend vs Backend Authorization

Frontend authorization improves user experience.

Backend authorization enforces security.

Never rely on frontend authorization alone.

---

## External Authorization Engines

Large systems may integrate with:

- CASL;
- Open Policy Agent (OPA);
- Cedar;
- custom policy engines.

Application code should remain independent of the authorization engine.

---

## Auditing

Record authorization decisions for sensitive operations.

Examples:

- permission denied;
- administrative actions;
- financial operations;
- privileged access.

Audit logs support incident investigations.

---

## Security

Always verify:

- authenticated identity;
- resource ownership;
- tenant isolation;
- current permissions.

Never cache authorization decisions longer than appropriate.

---

## Performance

Avoid:

- repeated permission queries;
- duplicated ownership checks;
- unnecessary database lookups.

Permission evaluation should remain efficient.

---

## Testing

Verify:

- authorized requests;
- unauthorized requests;
- ownership validation;
- tenant isolation;
- policy evaluation;
- role inheritance.

Authorization should remain deterministic.

---

## AI Decision Matrix

Authorization is responsible for:

✓ Permission checks

✓ Role evaluation

✓ Ownership verification

✓ Policy enforcement

✓ Tenant isolation

Authorization is **not** responsible for:

✗ Password validation

✗ Token generation

✗ Session management

✗ Business workflows

---

## AI Execution Checklist

## Investigation

☐ Identify protected resources.

☐ Review permission model.

☐ Review ownership rules.

☐ Review tenant boundaries.

---

## Planning

☐ Centralize authorization.

☐ Prefer policies.

☐ Enforce least privilege.

☐ Default to deny.

---

## Verification

☐ Authentication separated.

☐ Policies reusable.

☐ Ownership enforced.

☐ Tenant isolation verified.

☐ Permission checks consistent.

☐ Authorization independently testable.

---

## Common Mistakes

Avoid:

Checking permissions inside controllers.

Duplicating authorization logic.

Granting excessive permissions.

Trusting frontend authorization.

Skipping ownership checks.

Hardcoding roles throughout the application.

Mixing authentication with authorization.

---

## Completion Criteria

Authorization is complete when:

- every protected action is evaluated through a centralized policy;
- ownership and tenant isolation are enforced;
- least privilege is applied;
- authorization remains independent of authentication;
- permission decisions are auditable;
- authorization logic is independently testable.

---

## Summary

Authorization protects application resources by evaluating permissions after authentication succeeds.

By centralizing policy evaluation, enforcing ownership, applying least privilege, and separating authorization from authentication, NestJS applications become significantly more secure, maintainable, and adaptable to evolving business requirements.