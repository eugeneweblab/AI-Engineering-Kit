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
when_to_use: ""
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