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

Examples:

```
UserAlreadyExistsException

PaymentAlreadyProcessedException

InsufficientBalanceException
```

Avoid generic exceptions for business failures.

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