# Next.js Middleware

## Purpose

This document defines the engineering standards for implementing Middleware in Next.js applications.

The objective is to execute lightweight request processing before routing, enabling authentication, authorization, localization, redirects, rewrites, and request normalization while keeping Middleware fast and predictable.

Middleware should solve request-level concerns—not business logic.

---

# Core Principle

Middleware intercepts requests.

It should make routing decisions, not application decisions.

Keep Middleware lightweight.

---

# Request Lifecycle

Middleware executes before a route is rendered.

```
Incoming Request

↓

Middleware

↓

Redirect / Rewrite / Continue

↓

Route Handler

↓

Page or API Response
```

Middleware should make decisions quickly and avoid unnecessary work.

---

# Appropriate Use Cases

Middleware is well suited for:

- authentication checks;
- authorization gates;
- locale detection;
- URL normalization;
- redirects;
- rewrites;
- A/B testing;
- security headers;
- bot detection;
- request logging.

If logic requires database queries or complex business rules, it likely belongs elsewhere.

---

# Avoid Business Logic

Do not perform:

- database mutations;
- payment processing;
- complex validation;
- heavy computations;
- report generation.

Middleware should not replace Server Actions or Route Handlers.

---

# Authentication

Middleware may determine whether a request is authenticated.

Typical workflow:

```
Read Cookie

↓

Validate Session

↓

Continue

or

Redirect to Login
```

Keep authentication checks efficient.

---

# Authorization

Only lightweight authorization should occur in Middleware.

Examples:

- protected route access;
- role presence;
- subscription existence.

Detailed permission checks should remain inside the application.

---

# Redirects

Middleware is an excellent place for redirects.

Examples:

- login redirects;
- legacy URLs;
- canonical URLs;
- locale redirects;
- trailing slash normalization.

Prefer server-side redirects over client-side redirects.

---

# Rewrites

Use rewrites when changing the destination without changing the visible URL.

Examples:

- multi-tenant routing;
- feature rollout;
- localization;
- proxy behavior.

Keep rewrite rules easy to understand.

---

# Internationalization

Middleware may detect:

- language;
- country;
- locale.

Typical workflow:

```
Request

↓

Detect Locale

↓

Rewrite

↓

Localized Route
```

Do not duplicate locale detection throughout the application.

---

# Security Headers

Middleware may attach security headers.

Examples:

- Content Security Policy;
- X-Frame-Options;
- Referrer-Policy;
- Permissions-Policy.

Security policies should remain centralized.

---

# Cookies

Middleware may:

- read cookies;
- set cookies;
- remove cookies.

Avoid storing sensitive business state inside cookies.

---

# Request Headers

Middleware may modify request headers when required.

Typical examples:

- tracing identifiers;
- localization;
- feature flags.

Avoid unnecessary header manipulation.

---

# Response Headers

Middleware may append response headers.

Examples:

- caching directives;
- security headers;
- diagnostics.

Headers should remain consistent across the application.

---

# Matchers

Use matchers to limit Middleware execution.

Example:

```
/dashboard/:path*

/admin/:path*
```

Avoid executing Middleware for routes that do not require it.

---

# Performance

Middleware should:

- execute quickly;
- minimize allocations;
- avoid unnecessary parsing;
- avoid blocking operations.

Every request passes through Middleware.

Small inefficiencies become expensive at scale.

---

# Logging

Log only meaningful request events.

Examples:

- denied access;
- unexpected failures;
- security events.

Avoid excessive logging on every request.

---

# Error Handling

Middleware should fail safely.

If recovery is impossible:

- redirect appropriately;
- return an appropriate response;
- avoid exposing internal implementation details.

---

# Testing

Verify:

- protected routes;
- redirects;
- rewrites;
- locale detection;
- security headers;
- matcher behavior.

Middleware should be covered by integration tests whenever practical.

---

# Security

Never expose:

- secrets;
- internal infrastructure;
- permission rules;
- sensitive diagnostics.

Treat every request as untrusted.

---

# Accessibility

Middleware should preserve accessible navigation.

Redirects and rewrites must not create confusing navigation flows or inaccessible user journeys.

---

# AI Execution Checklist

## Investigation

☐ Identify request-level concerns.

☐ Review authentication flow.

☐ Review redirect requirements.

☐ Review localization.

---

## Planning

☐ Keep Middleware lightweight.

☐ Restrict execution with matchers.

☐ Centralize request handling.

☐ Avoid business logic.

---

## Verification

☐ Middleware executes efficiently.

☐ Redirects function correctly.

☐ Security headers applied.

☐ Authentication verified.

☐ Error handling implemented.

☐ Performance reviewed.

---

# Common Mistakes

Avoid:

Performing database queries inside Middleware.

Executing heavy computations.

Running Middleware for every route unnecessarily.

Duplicating authorization logic.

Creating redirect loops.

Ignoring matcher configuration.

Placing business workflows inside request interception.

---

# Completion Criteria

A Middleware implementation is complete when:

- request-level concerns are centralized;
- authentication and routing decisions are efficient;
- matchers limit unnecessary execution;
- security headers are applied where required;
- redirects and rewrites behave predictably;
- performance impact remains minimal.

---

# Summary

Middleware provides a centralized mechanism for handling request-level concerns before the application is rendered.

By limiting Middleware to lightweight routing, security, and request processing responsibilities, applications remain fast, scalable, secure, and easier to reason about.