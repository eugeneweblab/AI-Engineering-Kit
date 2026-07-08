---
id: nestjs/13-middleware
topic: nestjs
slug: middleware
title: "NestJS Middleware"
type: doc
order: 13
status: ready
tags: [nestjs, middleware]
related: []
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

---

## Request Logging

Middleware may log:

- HTTP method;
- URL;
- client IP;
- user agent;
- request start time.

Avoid logging sensitive request bodies.

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

## Common Mistakes

Avoid:

Checking permissions.

Loading users from the database.

Calling external services.

Implementing business validation.

Creating request-scoped business objects.

Logging passwords or tokens.

Duplicating functionality already provided by Guards or Interceptors.

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