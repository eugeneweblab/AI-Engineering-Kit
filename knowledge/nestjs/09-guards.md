# NestJS Guards

## Purpose

This document defines the engineering standards for implementing authentication and authorization using Guards in NestJS applications.

The objective is to ensure every protected resource is accessed only by authorized identities while keeping authentication and authorization centralized, reusable, and independent from business logic.

Guards enforce access control.

They should not implement business workflows.

---

# Core Principle

Authenticate first.

Authorize second.

Execute business logic last.

---

# Guard Goals

Every Guard implementation should provide:

- centralized access control;
- reusable authorization logic;
- consistent behavior;
- minimal duplication;
- predictable request handling;
- security by default.

---

# Authentication vs Authorization

Authentication answers:

> Who is the user?

Authorization answers:

> What is the user allowed to do?

These concerns should always remain separate.

---

# Request Lifecycle

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

# Authentication Guards

Authentication Guards verify identity.

Typical responsibilities:

- validate JWT access tokens;
- validate API keys;
- validate session cookies;
- attach authenticated user to the request.

Authentication Guards should not verify business permissions.

---

# Authorization Guards

Authorization Guards verify permissions.

Examples:

- administrator access;
- resource ownership;
- subscription level;
- feature access;
- tenant isolation.

Authorization decisions should remain centralized.

---

# RBAC

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

---

# ABAC

Attribute-Based Access Control evaluates attributes.

Examples:

- department;
- organization;
- subscription;
- resource status;
- ownership.

ABAC provides more flexibility than RBAC.

---

# Ownership Validation

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

---

# Layer Responsibilities

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

# Composite Guards

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

# Policies

Complex authorization should use reusable policy objects.

Policies should:

- remain testable;
- avoid framework dependencies;
- express business permissions clearly.

Avoid embedding complex permission logic directly inside Guards.

---

# Resource Protection

Protect:

- REST endpoints;
- GraphQL resolvers;
- WebSocket gateways;
- background management endpoints.

Every public entry point should be evaluated.

---

# Public Endpoints

Explicitly mark public routes.

Avoid relying on missing Guards to indicate public access.

Public access should always be intentional.

---

# Error Responses

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

# Performance

Permission evaluation should remain efficient.

Avoid:

- repeated database queries;
- duplicated permission calculations;
- unnecessary external requests.

Cache authorization data when appropriate.

---

# Multi-Tenant Applications

Authorization should verify:

- tenant membership;
- tenant ownership;
- resource isolation.

Never trust client-provided tenant identifiers.

---

# External Identity Providers

Authentication may integrate with:

- OAuth providers;
- OpenID Connect;
- enterprise identity systems;
- SAML providers.

Business authorization should remain independent of identity provider implementation.

---

# Security

Always verify:

- token integrity;
- token expiration;
- issuer;
- audience;
- required permissions.

Never trust client-provided roles or permissions.

---

# Testing

Verify:

- authenticated access;
- unauthenticated access;
- authorized access;
- forbidden access;
- ownership rules;
- policy evaluation.

Authorization should remain deterministic.

---

# AI Execution Checklist

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

# Common Mistakes

Avoid:

Checking permissions inside controllers.

Combining authentication and authorization into one Guard.

Trusting client-provided roles.

Performing business workflows inside Guards.

Duplicating permission logic.

Skipping ownership verification.

Returning incorrect HTTP status codes.

---

# Completion Criteria

A Guard implementation is complete when:

- authentication and authorization are separated;
- permissions are evaluated consistently;
- ownership is enforced where required;
- policies are reusable;
- protected resources are secured;
- Guards remain independently testable.

---

# Summary

Guards provide the primary security boundary for NestJS applications.

By separating identity verification from permission evaluation, centralizing authorization logic, enforcing ownership, and keeping Guards focused on access control, applications become significantly more secure, maintainable, and easier to evolve.