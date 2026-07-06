# NestJS Pipes

## Purpose

This document defines the engineering standards for implementing Pipes in NestJS applications.

The objective is to transform and validate incoming request data before it reaches controllers while keeping data preparation separate from business logic.

Pipes operate at the application boundary.

They should prepare data—not implement business rules.

---

# Core Principle

Transform early.

Validate early.

Execute business logic only after input has been prepared.

---

# Pipe Goals

Every Pipe should provide:

- deterministic behavior;
- reusable transformations;
- predictable validation;
- framework consistency;
- minimal side effects.

Pipes should always produce the same output for the same input.

---

# Request Lifecycle

Typical request flow:

```
HTTP Request

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

Interceptors (after)

↓

Exception Filter

↓

HTTP Response
```

Pipes execute immediately before controller method invocation.

---

# Responsibilities

Pipes are responsible for:

- transforming request values;
- validating transport-level input;
- parsing primitive types;
- normalizing incoming data.

Pipes should not:

- perform business validation;
- access repositories;
- execute workflows;
- send events;
- call external APIs.

---

# Pipe Types

NestJS provides several categories of Pipes.

Examples include:

- ValidationPipe;
- ParseIntPipe;
- ParseBoolPipe;
- ParseUUIDPipe;
- ParseArrayPipe;
- ParseEnumPipe;
- DefaultValuePipe.

Custom Pipes should follow the same design principles.

---

# Transformation

Pipes may transform values.

Examples:

```
"42"

↓

42
```

```
"true"

↓

true
```

```
"2026-07-06"

↓

Date
```

Transformation should remain deterministic.

---

# Validation

Pipes may reject invalid transport data.

Examples:

- malformed UUID;
- invalid integer;
- unsupported enum;
- invalid array.

Business rules belong elsewhere.

---

# Normalization

Normalize request data consistently.

Examples:

- trim whitespace;
- lowercase email addresses;
- remove duplicate separators;
- convert empty strings to undefined (when appropriate).

Normalization should remain predictable.

---

# Pipes vs DTO Validation

DTO validation verifies object structure.

Pipes transform or validate individual values before business execution.

Use both together when appropriate.

---

# Pipes vs Services

Services answer business questions.

Example:

```
Can this user purchase this product?
```

Pipes answer transport questions.

Example:

```
Is this value a valid UUID?
```

Business logic should never move into Pipes.

---

# Pipes vs Guards

Guards answer:

```
Can this request proceed?
```

Pipes answer:

```
Is this request data valid?
```

Authorization does not belong in Pipes.

---

# Pipes vs Interceptors

Interceptors wrap request execution.

Pipes prepare request data.

They solve different problems.

---

# Database Access

Avoid database queries inside Pipes.

Incorrect:

```
Pipe

↓

Repository

↓

Database
```

Correct:

```
Pipe

↓

Controller

↓

Service

↓

Repository
```

Business validation belongs inside services.

---

# Exception Handling

Pipes should throw meaningful validation exceptions.

Avoid custom response formatting.

Exception Filters should format responses consistently.

---

# Composition

Prefer composing multiple focused Pipes rather than creating one large Pipe.

Example:

```
ParseUUIDPipe

↓

CustomTrimPipe

↓

ValidationPipe
```

Small Pipes are easier to reuse and test.

---

# Reusability

Reusable Pipes should remain independent of business features.

Examples:

- UUID parsing;
- string normalization;
- boolean conversion.

Feature-specific logic should remain inside services.

---

# Performance

Pipes execute on every request.

Avoid:

- database access;
- network requests;
- expensive computations;
- unnecessary object creation.

Keep execution lightweight.

---

# Security

Validate:

- identifiers;
- enum values;
- primitive types;
- array sizes;
- payload structure.

Reject malformed requests immediately.

---

# Testing

Verify:

- valid input;
- invalid input;
- transformation behavior;
- exception handling;
- edge cases.

Pipes should be deterministic.

---

# AI Decision Matrix

Use a Pipe when the task is:

✓ Parsing request data

✓ Converting primitive types

✓ Normalizing transport values

✓ Rejecting malformed input

Do **not** use a Pipe for:

✗ Database lookups

✗ Permission checks

✗ Business rules

✗ Sending emails

✗ Calling external APIs

---

# AI Execution Checklist

## Investigation

☐ Identify transport data.

☐ Review required transformations.

☐ Review validation needs.

☐ Review performance impact.

---

## Planning

☐ Keep Pipe focused.

☐ Avoid business logic.

☐ Normalize input.

☐ Throw consistent exceptions.

---

## Verification

☐ Transformation deterministic.

☐ Validation correct.

☐ No database access.

☐ No authorization logic.

☐ Independently testable.

☐ Lightweight execution.

---

# Common Mistakes

Avoid:

Querying the database inside Pipes.

Checking permissions.

Embedding business rules.

Creating large multi-purpose Pipes.

Calling external APIs.

Duplicating validation already handled by DTOs.

Adding side effects.

---

# Completion Criteria

A Pipe implementation is complete when:

- it transforms or validates transport data only;
- business logic remains outside the Pipe;
- execution is deterministic;
- malformed requests fail early;
- performance remains lightweight;
- the Pipe can be independently tested.

---

# Summary

Pipes define the transport boundary of a NestJS application.

By focusing exclusively on parsing, normalization, and transport-level validation while avoiding business logic and infrastructure concerns, Pipes keep controllers simple, services focused, and the request lifecycle clean and predictable.