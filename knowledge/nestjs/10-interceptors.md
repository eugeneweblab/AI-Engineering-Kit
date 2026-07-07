---
id: nestjs/10-interceptors
topic: nestjs
slug: interceptors
title: "NestJS Interceptors"
type: doc
order: 10
status: ready
tags: [nestjs, interceptors]
related: []
when_to_use: ""
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

Example:

```
{
    "data": ...,
    "meta": ...,
    "timestamp": ...
}
```

Response structure should remain consistent across the application.

Avoid formatting responses individually inside controllers.

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