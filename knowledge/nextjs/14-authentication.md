---
id: nextjs/14-authentication
topic: nextjs
slug: authentication
title: "Next.js Authentication"
type: doc
order: 14
status: ready
tags: [nextjs, authentication]
related: []
when_to_use: ""
---
# Next.js Authentication

## Purpose

This document defines the engineering standards for authentication and authorization in Next.js applications.

The objective is to build secure, scalable, and maintainable authentication systems that fully leverage the server-first architecture of the App Router.

Authentication verifies identity.

Authorization determines permissions.

These concerns must remain primarily on the server.

---

## Core Principle

Authenticate on the server.

Authorize on the server.

Never trust the client.

---

## Authentication Flow

Every authentication workflow should follow this sequence.

```
User

↓

Login Request

↓

Identity Provider

↓

Session Creation

↓

Session Validation

↓

Authorization

↓

Protected Resource
```

Every protected request should verify authentication before accessing business logic.

---

## Authentication Methods

Supported authentication mechanisms include:

- Auth.js (NextAuth.js);
- Clerk;
- OAuth 2.0;
- OpenID Connect (OIDC);
- JWT;
- Session Cookies;
- Enterprise SSO.

Choose the simplest solution that satisfies the project requirements.

---

## Sessions

Prefer secure server-side sessions whenever practical.

A session should contain only the minimum information required to identify the authenticated user.

Avoid storing business data inside sessions.

---

## Cookies

Authentication cookies should be:

- HttpOnly;
- Secure;
- SameSite protected;
- encrypted or signed where appropriate.

Never expose authentication cookies to client-side JavaScript.

---

## JWT

JWTs should be used when stateless authentication is required.

Verify:

- signature;
- expiration;
- issuer;
- audience.

Never trust an unsigned or expired token.

---

## OAuth

OAuth providers may include:

- Google;
- Microsoft;
- GitHub;
- Apple;
- Facebook.

Delegate identity verification to trusted providers whenever appropriate.

---

## User Identity

Every authenticated request should establish a trusted user identity before accessing protected resources.

Typical information includes:

- user ID;
- organization ID;
- roles;
- permissions.

Avoid repeatedly querying identity information during the same request.

---

## Authorization

Authentication answers:

```
Who are you?
```

Authorization answers:

```
What are you allowed to do?
```

Never confuse these responsibilities.

---

## Role-Based Access Control (RBAC)

Use roles to define broad access levels.

Examples:

- Admin;
- Manager;
- Editor;
- Customer;
- Guest.

Roles should remain stable and easy to understand.

---

## Permission-Based Access

Permissions provide fine-grained authorization.

Examples:

- create product;
- update order;
- delete user;
- publish article.

Permissions should remain independent of presentation logic.

---

## Resource Ownership

Verify ownership before allowing access.

Example:

```
User

↓

Order

↓

Owner?

↓

Allow / Deny
```

Ownership checks belong on the server.

---

## Protected Routes

Protect routes before rendering.

Examples:

- dashboard;
- profile;
- administration;
- billing.

Avoid rendering protected pages before authentication has been verified.

---

## Middleware

Middleware may perform lightweight authentication checks.

Typical responsibilities:

- verify session existence;
- redirect anonymous users;
- normalize authentication flow.

Complex authorization belongs inside Server Components, Route Handlers, or Server Actions.

---

## Server Components

Server Components should:

- read authentication context;
- fetch authenticated data;
- perform authorization checks;
- render protected content.

Keep sensitive operations on the server.

---

## Client Components

Client Components should only:

- display authenticated UI;
- collect user input;
- initiate authenticated actions.

They should not make authorization decisions.

---

## Server Actions

Every Server Action should verify:

- authentication;
- authorization;
- resource ownership.

Never assume that the client has already validated permissions.

---

## API Routes

Every protected API endpoint should:

- authenticate the request;
- authorize the action;
- validate the input.

Security should never depend on the client application.

---

## Logout

Logout should:

- invalidate the session;
- clear authentication cookies;
- invalidate cached authenticated content.

Users should immediately lose access to protected resources.

---

## Password Security

If passwords are stored:

- hash them using a modern algorithm;
- never store plaintext passwords;
- never log passwords;
- enforce strong password policies.

Credential handling must follow industry best practices.

---

## Multi-Factor Authentication (MFA)

Support MFA when appropriate.

Examples:

- TOTP;
- hardware security keys;
- passkeys;
- email verification.

Higher-risk operations should require stronger authentication.

---

## Rate Limiting

Protect authentication endpoints against abuse.

Examples:

- login attempts;
- password reset;
- verification requests.

Limit repeated failed attempts.

---

## Audit Logging

Log security-sensitive events.

Examples:

- successful login;
- failed login;
- permission denial;
- password change;
- role change.

Logs should never expose sensitive credentials.

---

## Security

Always verify:

- authentication;
- authorization;
- ownership;
- input validation.

Security should never rely on hidden client-side behavior.

---

## Accessibility

Authentication workflows should support:

- keyboard navigation;
- screen readers;
- accessible validation messages;
- clear recovery flows.

Security must remain accessible.

---

## AI Execution Checklist

## Investigation

☐ Identify authentication provider.

☐ Review authorization model.

☐ Review protected routes.

☐ Review session strategy.

---

## Planning

☐ Authenticate on the server.

☐ Authorize every protected action.

☐ Protect sensitive resources.

☐ Minimize session data.

---

## Verification

☐ Authentication verified.

☐ Authorization enforced.

☐ Cookies secured.

☐ Sessions protected.

☐ Audit logging implemented.

☐ Accessibility preserved.

---

## Common Mistakes

Avoid:

Trusting client-side authentication.

Skipping authorization.

Storing sensitive data inside JWTs.

Making authorization decisions in Client Components.

Using insecure cookies.

Exposing authentication tokens.

Failing to verify resource ownership.

Ignoring rate limiting.

---

## Completion Criteria

An authentication implementation is complete when:

- users are securely authenticated;
- authorization is enforced for every protected resource;
- sessions and cookies are protected;
- security best practices are followed;
- audit logging exists;
- accessibility has been verified.

---

## Summary

Authentication and authorization form the security foundation of every Next.js application.

By keeping identity verification, permission checks, and protected business logic on the server while minimizing trust in the client, applications remain secure, scalable, maintainable, and aligned with modern App Router best practices.