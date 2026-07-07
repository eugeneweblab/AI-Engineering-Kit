---
id: nestjs/15-authentication
topic: nestjs
slug: authentication
title: "NestJS Authentication"
type: doc
order: 15
status: ready
tags: [nestjs, authentication]
related: []
when_to_use: ""
---
# NestJS Authentication

## Purpose

This document defines the engineering standards for implementing authentication in NestJS applications.

The objective is to verify user identities securely while keeping authentication independent from authorization and business logic.

Authentication answers one question:

> Who is making this request?

It should not determine what the user is allowed to do.

---

## Core Principle

Authenticate identities.

Do not implement business rules.

Authorization belongs elsewhere.

---

## Authentication Goals

Every authentication system should provide:

- identity verification;
- secure credential handling;
- token lifecycle management;
- session independence;
- auditability;
- scalability.

Authentication should remain transport-independent whenever practical.

---

## Authentication Flow

Typical JWT flow:

```
Login Request

↓

Credential Validation

↓

Identity Verification

↓

Generate Access Token

↓

Generate Refresh Token

↓

Return Tokens

↓

Authenticated Requests

↓

Token Validation

↓

Authenticated User
```

Every stage should have a clearly defined responsibility.

---

## Responsibilities

Authentication is responsible for:

- verifying credentials;
- issuing tokens;
- validating tokens;
- refreshing sessions;
- revoking sessions;
- identifying users.

Authentication should not:

- evaluate permissions;
- enforce business policies;
- determine resource ownership.

---

## Identity Providers

Authentication may use:

- email and password;
- OAuth2;
- OpenID Connect;
- SAML;
- API keys;
- service accounts;
- enterprise identity providers.

Business logic should remain independent of the identity provider.

---

## Password Handling

Passwords should:

- never be stored in plain text;
- always be hashed using a modern password hashing algorithm;
- never be logged;
- never be returned by the API.

Password verification should occur only during authentication.

---

## Access Tokens

Access tokens should:

- have short lifetimes;
- contain only required claims;
- be cryptographically signed;
- remain stateless.

Avoid storing sensitive information inside tokens.

---

## Refresh Tokens

Refresh tokens should:

- have longer lifetimes;
- be stored securely;
- support revocation;
- support rotation.

Refresh tokens should never be treated as permanent credentials.

---

## Token Rotation

Implement refresh token rotation.

Flow:

```
Refresh Token

↓

Validate

↓

Invalidate Previous Token

↓

Issue New Refresh Token

↓

Issue New Access Token
```

Reusing an old refresh token should be treated as a security event.

---

## Token Revocation

Support revocation for:

- logout;
- password changes;
- compromised accounts;
- administrator actions.

Revoked tokens should no longer grant access.

---

## JWT Claims

Include only necessary claims.

Typical claims:

- subject (user ID);
- issuer;
- audience;
- issued at;
- expiration;
- token identifier.

Avoid embedding authorization rules inside JWTs unless explicitly required.

---

## Session Management

Authentication may remain stateless.

If sessions are required:

- define expiration;
- support revocation;
- monitor active sessions.

Session behavior should remain predictable.

---

## Multi-Factor Authentication

Support MFA when required.

Examples:

- authenticator applications;
- hardware security keys;
- email verification;
- SMS verification (only when appropriate).

MFA should complement—not replace—strong password security.

---

## OAuth Integration

When integrating OAuth:

- validate provider tokens;
- verify issuer;
- verify audience;
- retrieve trusted user information.

Never trust unverified identity data.

---

## API Keys

API keys should:

- identify clients;
- support expiration;
- support rotation;
- support revocation.

Treat API keys as secrets.

---

## Rate Limiting

Authentication endpoints should be protected against abuse.

Examples:

- login attempts;
- password reset;
- token refresh.

Protect against brute-force attacks.

---

## Account Lockout

Repeated authentication failures may trigger:

- temporary lockout;
- progressive delays;
- additional verification.

Avoid permanent lockout without administrative recovery.

---

## Audit Logging

Record security events.

Examples:

- successful login;
- failed login;
- logout;
- password reset;
- token refresh;
- MFA enrollment.

Audit logs should be immutable.

---

## Security

Always verify:

- token signature;
- expiration;
- issuer;
- audience;
- replay protection when applicable.

Never trust client-provided identity information.

---

## Testing

Verify:

- successful authentication;
- failed authentication;
- expired tokens;
- revoked tokens;
- refresh token rotation;
- logout behavior.

Authentication should remain deterministic.

---

## AI Decision Matrix

Authentication is responsible for:

✓ Identity verification

✓ Token issuance

✓ Token validation

✓ Session lifecycle

✓ Credential verification

Authentication is **not** responsible for:

✗ Permission checks

✗ Business rules

✗ Resource ownership

✗ Feature access

---

## AI Execution Checklist

## Investigation

☐ Identify authentication mechanism.

☐ Review token lifecycle.

☐ Review credential storage.

☐ Review security requirements.

---

## Planning

☐ Separate authentication from authorization.

☐ Issue short-lived access tokens.

☐ Rotate refresh tokens.

☐ Protect credentials.

---

## Verification

☐ Passwords securely handled.

☐ Tokens validated.

☐ Revocation supported.

☐ MFA considered.

☐ Security events logged.

☐ Authentication independently testable.

---

## Common Mistakes

Avoid:

Storing plain text passwords.

Using long-lived access tokens.

Returning sensitive user information.

Embedding business permissions inside authentication logic.

Skipping refresh token rotation.

Trusting unsigned JWTs.

Logging credentials or tokens.

---

## Completion Criteria

Authentication is complete when:

- user identities are verified securely;
- passwords are protected;
- access and refresh tokens follow secure lifecycle rules;
- authentication remains separate from authorization;
- revocation and rotation are supported;
- security events are logged.

---

## Summary

Authentication establishes the identity of every request.

By separating identity verification from authorization, protecting credentials, implementing secure token management, and supporting modern authentication workflows, NestJS applications remain secure, scalable, and maintainable.