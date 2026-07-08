---
id: nestjs/26-security
topic: nestjs
slug: security
title: "Security"
type: doc
order: 26
status: ready
tags: [nestjs, security]
related: []
when_to_use: "Read before building or reviewing any code with security implications, or when hardening a NestJS application."
---
# Security

## Purpose

This document defines the engineering standards for building secure NestJS applications.

The objective is to reduce security risks by applying secure-by-default principles across application architecture, infrastructure, and development workflows.

Security is not a feature.

Security is a system property.

Every component contributes to the application's security posture.

---

## Core Principle

Assume every request is untrusted until verified.

Never trust:

- user input;
- client applications;
- internal network traffic;
- third-party services.

Every boundary must validate incoming data.

---

## Security Goals

Every application should provide:

- confidentiality;
- integrity;
- availability;
- authenticity;
- accountability;
- auditability.

Security decisions should prioritize risk reduction over convenience.

---

## Defense in Depth

Apply multiple independent security layers.

Example:

```
Internet

↓

WAF

↓

API Gateway

↓

Authentication

↓

Authorization

↓

Validation

↓

Business Logic

↓

Database
```

No single layer should be responsible for all security.

---

## Zero Trust

Assume that no client, service, or network segment is inherently trusted.

Verify:

- identity;
- permissions;
- request integrity;
- service identity.

Every request should be authenticated and authorized.

---

## Input Validation

Validate all external input.

Examples:

- request bodies;
- query parameters;
- route parameters;
- headers;
- uploaded files;
- queue messages;
- webhook payloads.

Reject invalid data immediately.

In NestJS, model every request body as a `class-validator` DTO and enable a
strict global `ValidationPipe`. `whitelist` strips unknown properties and
`forbidNonWhitelisted` rejects them, which is what closes mass-assignment /
over-posting holes (a client cannot smuggle an `isAdmin` field into a user
you persist).

```typescript
// create-user.dto.ts
import { IsBoolean, IsEmail, IsOptional, Length } from 'class-validator';

export class CreateUserDto {
  @IsEmail()
  email: string;

  @Length(12, 128)
  password: string;

  @IsOptional()
  @IsBoolean()
  marketingOptIn?: boolean;

  // Note: there is deliberately no `isAdmin` / `roles` field here.
  // Privilege is assigned by the server, never accepted from the client.
}
```

```typescript
// main.ts
import { ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // strip properties without a validation decorator
      forbidNonWhitelisted: true, // 400 when unknown properties are sent
      transform: true, // instantiate the DTO class, coerce declared types
      transformOptions: { enableImplicitConversion: false },
    }),
  );

  await app.listen(3000);
}
bootstrap();
```

```typescript
// GOOD: server owns privilege; DTO cannot carry it.
const user = this.repo.create({ ...createUserDto, roles: ['user'] });

// BAD: spreading a raw request body lets a client set any column,
// including roles/isAdmin, because nothing was whitelisted.
const user = this.repo.create({ ...request.body });
```

---

## Output Encoding

Encode data according to its destination.

Examples:

- HTML;
- JSON;
- JavaScript;
- SQL;
- URLs.

Never assume output is safe by default.

---

## Secrets Management

Secrets include:

- JWT signing keys;
- API keys;
- OAuth credentials;
- encryption keys;
- database passwords.

Secrets should:

- never appear in source code;
- never be logged;
- rotate periodically;
- be stored securely.

---

## Authentication

Authentication should verify identity before granting access.

Prefer:

- short-lived access tokens;
- refresh token rotation;
- MFA where appropriate.

Authentication should remain independent from authorization.

---

## Authorization

Every protected operation requires authorization.

Apply:

- least privilege;
- ownership verification;
- policy-based authorization;
- tenant isolation.

Default to deny access.

Enforce authorization inside a `CanActivate` guard, not scattered through
controllers. The guard resolves an ownership/tenant decision and denies by
default: any path that is not explicitly permitted throws
`ForbiddenException`. This assumes an upstream authentication guard has already
attached `request.user`.

```typescript
// resource-owner.guard.ts
import {
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  Injectable,
} from '@nestjs/common';
import { OrdersService } from './orders.service';

@Injectable()
export class ResourceOwnerGuard implements CanActivate {
  constructor(private readonly orders: OrdersService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const user = request.user; // set by the auth guard
    const orderId = request.params.id;

    if (!user) {
      throw new ForbiddenException();
    }

    const order = await this.orders.findById(orderId);

    // Scope the lookup to the caller's tenant AND ownership.
    // Anything that is not explicitly the owner is denied.
    if (!order || order.tenantId !== user.tenantId || order.userId !== user.id) {
      throw new ForbiddenException();
    }

    return true;
  }
}
```

```typescript
// orders.controller.ts
import { Controller, Delete, Param, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { ResourceOwnerGuard } from './resource-owner.guard';

@Controller('orders')
@UseGuards(JwtAuthGuard) // authenticate first
export class OrdersController {
  @Delete(':id')
  @UseGuards(ResourceOwnerGuard) // then authorize ownership
  remove(@Param('id') id: string) {
    // Reaching here means the caller provably owns this order.
  }
}
```

---

## OWASP Top 10

Review every application against the latest OWASP Top 10.

Typical risks include:

- broken access control;
- cryptographic failures;
- injection attacks;
- insecure design;
- security misconfiguration;
- vulnerable dependencies;
- identification failures;
- logging failures;
- SSRF.

Security reviews should be continuous.

---

## Injection Prevention

Always use:

- parameterized SQL;
- ORM parameter binding;
- safe shell execution.

Never concatenate user input into:

- SQL;
- shell commands;
- file paths.

With TypeORM, pass user input as bound parameters, never as an interpolated
string. The parameterized form sends the value separately from the SQL text,
so it can never be parsed as SQL.

```typescript
// GOOD: parameterized — `:email` is bound, never parsed as SQL.
const user = await this.repo
  .createQueryBuilder('user')
  .where('user.email = :email', { email })
  .getOne();

// GOOD: raw query with positional parameters.
await this.repo.query('SELECT * FROM users WHERE email = $1', [email]);

// BAD: string interpolation — a crafted email such as
// "' OR '1'='1" is now executable SQL (injection).
const user = await this.repo
  .createQueryBuilder('user')
  .where(`user.email = '${email}'`)
  .getOne();
```

---

## XSS Prevention

Escape or sanitize all untrusted content rendered in browsers.

Prefer context-aware output encoding.

Never trust HTML submitted by users.

---

## CSRF Protection

Protect state-changing endpoints when using cookie-based authentication.

Use:

- CSRF tokens;
- SameSite cookies;
- origin validation.

---

## SSRF Protection

Validate outbound requests.

Restrict:

- internal IP ranges;
- metadata services;
- localhost access.

Never proxy arbitrary user-provided URLs.

---

## File Uploads

Validate:

- MIME type;
- extension;
- size;
- content when practical.

Store uploads outside executable directories.

Never execute uploaded files.

---

## Rate Limiting

Protect:

- authentication endpoints;
- password reset;
- search;
- public APIs.

Rate limiting reduces abuse.

---

## Encryption

Encrypt sensitive data:

- in transit (TLS);
- at rest when appropriate.

Never invent custom cryptographic algorithms.

Use proven libraries.

---

## Dependency Security

Continuously review dependencies.

Monitor:

- CVEs;
- abandoned packages;
- transitive vulnerabilities.

Apply updates regularly.

---

## Logging

Log:

- authentication failures;
- authorization failures;
- privilege changes;
- suspicious behavior.

Never log:

- passwords;
- tokens;
- secrets.

---

## Audit Trail

Record:

- administrative actions;
- permission changes;
- financial operations;
- sensitive data access.

Audit records should be immutable.

---

## Incident Response

Prepare procedures for:

- credential compromise;
- data breach;
- service abuse;
- dependency vulnerability.

Security incidents require predefined response plans.

---

## Security Headers

Enable appropriate HTTP security headers.

Examples:

- CSP;
- HSTS;
- X-Content-Type-Options;
- Referrer-Policy;
- Permissions-Policy.

Apply `helmet` as global middleware to set these headers, and register
`@nestjs/throttler` as a global guard so security-sensitive endpoints are
rate limited by default. In `@nestjs/throttler` v6, `ttl` is expressed in
milliseconds and named throttlers are passed as an array.

```typescript
// main.ts (add to the existing bootstrap)
import helmet from 'helmet';
// ...
const app = await NestFactory.create(AppModule);
app.use(helmet()); // CSP, HSTS, X-Content-Type-Options, etc.
```

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { ThrottlerGuard, ThrottlerModule } from '@nestjs/throttler';

@Module({
  imports: [
    ThrottlerModule.forRoot([
      { ttl: 60_000, limit: 100 }, // 100 requests / minute per client
    ]),
  ],
  providers: [
    { provide: APP_GUARD, useClass: ThrottlerGuard }, // rate-limit by default
  ],
})
export class AppModule {}
```

Tighten specific endpoints (login, password reset) with `@Throttle`:

```typescript
// auth.controller.ts
import { Controller, Post } from '@nestjs/common';
import { Throttle } from '@nestjs/throttler';

@Controller('auth')
export class AuthController {
  @Throttle({ default: { ttl: 60_000, limit: 5 } }) // 5 attempts / minute
  @Post('login')
  login() {
    // brute-force surface is now bounded
  }
}
```

---

## Testing

Include:

- dependency scanning;
- static analysis;
- security integration tests;
- penetration testing;
- secret scanning.

Security testing belongs in CI/CD.

---

## AI Decision Matrix

Always protect:

✓ Authentication

✓ Authorization

✓ Secrets

✓ User input

✓ Sensitive data

Never trust:

✗ Client validation

✗ Internal traffic

✗ Third-party payloads

✗ Uploaded files

---

## AI Execution Checklist

## Investigation

☐ Identify attack surface.

☐ Review sensitive assets.

☐ Review authentication.

☐ Review authorization.

---

## Planning

☐ Validate all input.

☐ Protect secrets.

☐ Apply least privilege.

☐ Enable security logging.

---

## Verification

☐ OWASP reviewed.

☐ Dependencies scanned.

☐ Security headers enabled.

☐ Secrets protected.

☐ Audit logging available.

☐ Incident response documented.

---

## Common Mistakes

Avoid:

Hardcoded secrets.

Trusting client validation.

Logging sensitive information.

Ignoring dependency vulnerabilities.

Disabling TLS.

Sharing privileged credentials.

Skipping authorization checks.

---

## Completion Criteria

Security implementation is complete when:

- authentication and authorization are enforced;
- secrets are protected;
- input validation is comprehensive;
- dependencies are monitored;
- audit logging is implemented;
- security reviews are part of the development lifecycle.

---

## Summary

Security is a continuous engineering discipline rather than a single feature.

By applying defense in depth, Zero Trust principles, strong authentication and authorization, secure dependency management, and continuous security validation, NestJS applications remain resilient against evolving threats while protecting users and business data.