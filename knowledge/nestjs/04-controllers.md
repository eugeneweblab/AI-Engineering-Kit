# NestJS Controllers

## Purpose

This document defines the engineering standards for designing Controllers in NestJS applications.

The objective is to build APIs that are predictable, maintainable, and easy to test by keeping controllers focused exclusively on handling HTTP communication.

Controllers should coordinate requests—not implement business logic.

---

# Core Principle

Controllers translate HTTP requests into application actions.

Business decisions belong in services.

---

# Controller Goals

Every controller should provide:

- clear routing;
- predictable HTTP behavior;
- request validation;
- consistent responses;
- minimal business logic;
- proper error propagation.

Controllers should remain thin.

---

# Responsibilities

Controllers are responsible for:

- defining routes;
- receiving requests;
- extracting request data;
- invoking services;
- returning responses.

Controllers should not contain business workflows.

---

# Request Lifecycle

A typical request follows this flow:

```
HTTP Request

↓

Middleware

↓

Guard

↓

Interceptor

↓

Pipe

↓

Controller

↓

Service

↓

Response
```

Each layer should perform a single responsibility.

---

# Routing

Routes should be:

- predictable;
- resource-oriented;
- versionable;
- RESTful.

Example:

```
GET     /users

GET     /users/:id

POST    /users

PATCH   /users/:id

DELETE  /users/:id
```

Avoid action-oriented URLs.

---

# Resource Naming

Use plural resource names.

Examples:

```
/users

/products

/orders

/payments
```

Avoid inconsistent naming conventions.

---

# HTTP Methods

Use HTTP methods according to their intent.

GET

- retrieve resources.

POST

- create resources.

PUT

- replace resources.

PATCH

- partially update resources.

DELETE

- remove resources.

Do not overload endpoints with unrelated behavior.

---

# Request Parameters

Extract request data explicitly.

Typical sources:

- path parameters;
- query parameters;
- request body;
- headers.

Avoid ambiguous parameter handling.

---

# DTO Usage

Every request body should use a DTO.

DTOs should define:

- expected fields;
- validation rules;
- transformation behavior.

Avoid accepting untyped objects.

---

# Validation

Validate incoming requests before reaching business logic.

Examples:

- required fields;
- formats;
- ranges;
- enums;
- nested objects.

Invalid requests should fail early.

---

# Response Structure

Responses should remain consistent.

Typical response contains:

- requested resource;
- status information;
- pagination metadata (when applicable).

Avoid returning inconsistent response shapes.

---

# Status Codes

Use appropriate HTTP status codes.

Typical examples:

- 200 OK
- 201 Created
- 204 No Content
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 409 Conflict
- 422 Unprocessable Entity
- 500 Internal Server Error

Status codes should accurately reflect the outcome.

---

# Error Handling

Controllers should not swallow exceptions.

Allow application-level exception handling to produce consistent responses.

Avoid custom error formatting inside individual controllers.

---

# Authentication

Authentication should be enforced through Guards.

Controllers should assume authenticated identity has already been established.

---

# Authorization

Authorization should verify resource access before executing business logic.

Authorization rules should remain centralized and reusable.

---

# Pagination

Collection endpoints should support pagination.

Typical parameters:

- page;
- limit;
- cursor;
- sort;
- filter.

Avoid returning unbounded collections.

---

# Filtering

Filtering should be implemented using query parameters.

Examples:

```
GET /products?category=laptops

GET /orders?status=completed
```

Filtering behavior should remain predictable.

---

# Versioning

Public APIs should support versioning.

Example:

```
/v1/users

/v2/users
```

Versioning strategy should remain consistent throughout the application.

---

# File Uploads

Controllers handling uploads should:

- validate file type;
- validate file size;
- reject invalid uploads;
- delegate storage to dedicated services.

Avoid embedding storage logic inside controllers.

---

# Security

Controllers should:

- validate input;
- avoid exposing internal errors;
- never trust client input;
- protect sensitive endpoints.

Security should be enforced before business logic executes.

---

# Testing

Controllers should verify:

- routing;
- request validation;
- response codes;
- interaction with services.

Business rules should be tested within services rather than controllers.

---

# AI Execution Checklist

## Investigation

☐ Identify resource.

☐ Review API contract.

☐ Review validation rules.

☐ Review authorization requirements.

---

## Planning

☐ Create RESTful routes.

☐ Keep controller thin.

☐ Delegate business logic.

☐ Validate input.

---

## Verification

☐ Routes consistent.

☐ DTOs implemented.

☐ Status codes correct.

☐ Validation enforced.

☐ Authorization verified.

☐ Controller independently testable.

---

# Common Mistakes

Avoid:

Placing business logic inside controllers.

Accessing the database directly.

Returning inconsistent response formats.

Skipping validation.

Creating action-based endpoints.

Performing authorization manually inside methods.

Duplicating validation logic.

---

# Completion Criteria

A controller implementation is complete when:

- routes follow REST principles;
- request validation is enforced;
- business logic is delegated to services;
- responses are consistent;
- authentication and authorization are integrated;
- the controller remains small, predictable, and testable.

---

# Summary

Controllers provide the entry point into a NestJS application.

By keeping controllers focused on HTTP communication, delegating business logic to services, validating every request, and exposing a consistent REST API, applications remain easier to maintain, extend, and test as they grow.