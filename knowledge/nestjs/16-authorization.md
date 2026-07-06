# NestJS Authorization

## Purpose

This document defines the engineering standards for implementing authorization in NestJS applications.

The objective is to determine whether an authenticated identity is allowed to perform a specific action on a specific resource while keeping authorization centralized, consistent, and independent from authentication.

Authentication identifies users.

Authorization determines permissions.

---

# Core Principle

Never trust authenticated users automatically.

Every protected action must be authorized.

---

# Authorization Goals

Every authorization system should provide:

- centralized policy evaluation;
- consistent permission enforcement;
- reusable authorization logic;
- least privilege access;
- auditability;
- scalability.

Authorization should be deterministic and explicit.

---

# Authorization Flow

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

# Responsibilities

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

# Authorization Models

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

# Ownership Authorization

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

---

# Policy-Based Authorization

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

---

# Permission Matrix

Document permissions explicitly.

Example:

| Role | Users | Orders | Reports |
|------|------|------|------|
| Admin | Full | Full | Full |
| Manager | Read | Manage | Read |
| Customer | Own Only | Own Only | None |

Permission matrices improve maintainability.

---

# Multi-Tenant Authorization

Every request should verify tenant boundaries.

Typical checks:

- tenant membership;
- tenant ownership;
- organization hierarchy;
- resource isolation.

Never trust tenant identifiers supplied by clients.

---

# Resource-Level Authorization

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

# Least Privilege

Grant only the permissions required.

Avoid:

- administrator by default;
- wildcard permissions;
- unnecessary global access.

Least privilege reduces security risk.

---

# Default Deny

If no authorization rule grants access:

```
Deny
```

Default deny should be the application's security posture.

---

# Frontend vs Backend Authorization

Frontend authorization improves user experience.

Backend authorization enforces security.

Never rely on frontend authorization alone.

---

# External Authorization Engines

Large systems may integrate with:

- CASL;
- Open Policy Agent (OPA);
- Cedar;
- custom policy engines.

Application code should remain independent of the authorization engine.

---

# Auditing

Record authorization decisions for sensitive operations.

Examples:

- permission denied;
- administrative actions;
- financial operations;
- privileged access.

Audit logs support incident investigations.

---

# Security

Always verify:

- authenticated identity;
- resource ownership;
- tenant isolation;
- current permissions.

Never cache authorization decisions longer than appropriate.

---

# Performance

Avoid:

- repeated permission queries;
- duplicated ownership checks;
- unnecessary database lookups.

Permission evaluation should remain efficient.

---

# Testing

Verify:

- authorized requests;
- unauthorized requests;
- ownership validation;
- tenant isolation;
- policy evaluation;
- role inheritance.

Authorization should remain deterministic.

---

# AI Decision Matrix

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

# AI Execution Checklist

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

# Common Mistakes

Avoid:

Checking permissions inside controllers.

Duplicating authorization logic.

Granting excessive permissions.

Trusting frontend authorization.

Skipping ownership checks.

Hardcoding roles throughout the application.

Mixing authentication with authorization.

---

# Completion Criteria

Authorization is complete when:

- every protected action is evaluated through a centralized policy;
- ownership and tenant isolation are enforced;
- least privilege is applied;
- authorization remains independent of authentication;
- permission decisions are auditable;
- authorization logic is independently testable.

---

# Summary

Authorization protects application resources by evaluating permissions after authentication succeeds.

By centralizing policy evaluation, enforcing ownership, applying least privilege, and separating authorization from authentication, NestJS applications become significantly more secure, maintainable, and adaptable to evolving business requirements.