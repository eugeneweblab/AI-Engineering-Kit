---
id: nextjs/12-api-routes
topic: nextjs
slug: api-routes
title: "Next.js API Routes"
type: doc
order: 12
status: ready
tags: [nextjs, api-routes]
related: []
when_to_use: "Read before building HTTP endpoints or Route Handlers in a Next.js app."
---
# Next.js API Routes

## Purpose

This document defines the engineering standards for implementing HTTP endpoints using Route Handlers (`route.ts`) in Next.js applications.

The objective is to build APIs that are secure, maintainable, scalable, and aligned with the App Router architecture.

API Routes should expose resources and integrations, while Server Actions should handle application mutations initiated by the user interface.

---

## Core Principle

Use Server Actions for UI-driven mutations.

Use Route Handlers for HTTP APIs.

Choose the simplest interface that satisfies the use case.

---

## When to Use API Routes

API Routes are appropriate for:

- REST APIs;
- webhooks;
- third-party integrations;
- public APIs;
- mobile applications;
- external services;
- file downloads;
- file uploads;
- machine-to-machine communication.

Avoid creating API Routes solely for communication between Server Components and the same backend.

---

## When to Use Server Actions

Prefer Server Actions when:

- handling form submissions;
- updating application data;
- executing business workflows;
- interacting directly with the database;
- responding to user interactions inside the application.

Avoid replacing Server Actions with internal API calls.

---

## Route Handler Structure

Every endpoint should follow a predictable structure.

```
Request

↓

Validation

↓

Authentication

↓

Authorization

↓

Business Logic

↓

Database / Service

↓

Response
```

Each step should have a clearly defined responsibility.

---

## File Structure

API endpoints are implemented using `route.ts`.

Example:

```
app/

    api/

        users/

            route.ts

        products/

            route.ts

        webhooks/

            stripe/

                route.ts
```

Group endpoints by business domain rather than HTTP method.

---

## HTTP Methods

Support only the methods required by the resource.

Examples:

- `GET`
- `POST`
- `PUT`
- `PATCH`
- `DELETE`

Reject unsupported methods with appropriate HTTP responses.

---

## Request Validation

Validate every incoming request.

Examples:

- request body;
- query parameters;
- route parameters;
- headers;
- uploaded files.

Never trust client input.

---

## Authentication

Authenticate requests before accessing protected resources.

Examples:

- cookies;
- bearer tokens;
- JWTs;
- API keys.

Authentication should occur before business logic.

---

## Authorization

Verify permissions after authentication.

Examples:

- user ownership;
- organization membership;
- administrator role;
- subscription status.

Authorization decisions belong on the server.

---

## Response Format

Responses should remain predictable.

Typical structure:

```json
{
    "success": true,
    "data": {}
}
```

Error responses should provide useful information without exposing implementation details.

---

## Status Codes

Use appropriate HTTP status codes.

Examples:

- `200 OK`
- `201 Created`
- `204 No Content`
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `409 Conflict`
- `422 Unprocessable Entity`
- `500 Internal Server Error`

Avoid returning `200` for failed requests.

---

## Error Handling

Every endpoint should define:

- validation errors;
- authentication failures;
- authorization failures;
- business errors;
- unexpected exceptions.

Log unexpected failures for investigation.

---

## Database Access

Route Handlers may communicate directly with:

- Prisma;
- Drizzle;
- PostgreSQL;
- MongoDB;
- Redis;
- external services.

Keep persistence logic separated from request handling where practical.

---

## Webhooks

Use Route Handlers for webhook endpoints.

Examples:

- Stripe;
- GitHub;
- Slack;
- Customer.io;
- Clerk;
- Auth providers.

Always verify webhook signatures before processing payloads.

---

## File Uploads

Validate uploaded files.

Verify:

- size;
- MIME type;
- extension;
- authorization.

Store files outside the application bundle whenever appropriate.

---

## CORS

Configure CORS only when required.

Review:

- allowed origins;
- methods;
- headers;
- credentials.

Never allow unrestricted cross-origin access without justification.

---

## Caching

Choose caching behavior intentionally.

Examples:

- public responses;
- private responses;
- dynamic resources;
- static resources.

Avoid caching personalized API responses.

---

## Versioning

Version APIs that have external consumers.

Examples:

```
/api/v1/products

/api/v2/products
```

Internal application endpoints may not require versioning.

---

## Logging

Log:

- request failures;
- authorization failures;
- validation errors;
- unexpected exceptions.

Avoid logging sensitive information.

---

## Performance

Review:

- query count;
- payload size;
- response time;
- caching opportunities.

Avoid unnecessary database queries.

---

## Security

Protect:

- secrets;
- tokens;
- credentials;
- internal identifiers.

Validate every request regardless of client trust.

---

## Accessibility

Although APIs are not user interfaces, predictable error responses improve accessibility by enabling clients to present meaningful feedback.

---

## AI Execution Checklist

## Investigation

☐ Identify API consumers.

☐ Review authentication.

☐ Review authorization.

☐ Review validation.

---

## Planning

☐ Select HTTP methods.

☐ Validate requests.

☐ Structure responses consistently.

☐ Protect sensitive operations.

---

## Verification

☐ Authentication implemented.

☐ Authorization verified.

☐ Validation complete.

☐ Status codes correct.

☐ Errors handled safely.

☐ Performance reviewed.

---

## Common Mistakes

Avoid:

Creating internal API calls from Server Components.

Skipping validation.

Returning inconsistent response formats.

Ignoring HTTP status codes.

Trusting client-provided identifiers.

Caching personalized responses.

Logging sensitive information.

Combining multiple unrelated resources in a single endpoint.

---

## Completion Criteria

An API Route implementation is complete when:

- requests are validated;
- authentication and authorization are enforced;
- responses follow a consistent structure;
- correct HTTP status codes are returned;
- errors are handled safely;
- performance and security have been reviewed.

---

## Summary

Route Handlers provide a flexible foundation for building HTTP APIs in Next.js.

By reserving them for external communication, integrations, and resource-oriented APIs—while using Server Actions for UI-driven mutations—applications remain simpler, more maintainable, and better aligned with the App Router architecture.