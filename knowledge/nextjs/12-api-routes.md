---
id: nextjs/12-api-routes
topic: nextjs
slug: api-routes
title: "Next.js API Routes"
type: doc
order: 12
status: ready
tags: [nextjs, api-routes]
related: [nextjs/11-server-actions, nextjs/13-middleware, rest-api/04-endpoints, rest-api/09-error-handling]
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

## Examples

**Good Example** — a Route Handler with an explicit contract and correct caching

```ts
// app/api/orders/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const CreateOrder = z.object({
  sku: z.string().min(1),
  quantity: z.number().int().min(1).max(100),
});

export async function POST(request: NextRequest) {
  const session = await auth();
  if (!session) {
    return NextResponse.json({ error: 'unauthorized' }, { status: 401 });
  }

  const parsed = CreateOrder.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    // A shape the client can act on, not a stack trace.
    return NextResponse.json(
      { error: 'validation_failed', fields: z.treeifyError(parsed.error) },
      { status: 400 },
    );
  }

  const order = await createOrder(session.userId, parsed.data);

  return NextResponse.json(
    { id: order.id, status: order.status },
    { status: 201, headers: { Location: `/api/orders/${order.id}` } },
  );
}

export async function GET() {
  const products = await getPublicProducts();
  // Public and slow-changing: let the CDN serve it.
  return NextResponse.json(products, {
    headers: { 'Cache-Control': 'public, s-maxage=300, stale-while-revalidate=60' },
  });
}
```

**Bad Example** — a route that returns 200 for everything and leaks internals

```ts
// app/api/orders/route.ts
export async function POST(request: Request) {
  try {
    const body = await request.json();       // untyped, unvalidated

    // No auth check, and the user id comes from the request body, so a caller
    // can create orders on anyone's account.
    const order = await db.order.create({ data: { ...body } });

    return Response.json({ success: true, order });   // whole row, every column
  } catch (e) {
    // 200 with an error inside: clients cannot use status codes, retries never
    // trigger, and monitoring sees a healthy endpoint.
    return Response.json({ success: false, error: String(e), stack: (e as Error).stack });
  }
}
```

Prefer a Server Action for form mutations from your own UI; use a Route Handler when the
endpoint is a real API consumed by something you do not render — a webhook, a mobile client,
or a third party.

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

## Related

- `knowledge/nextjs/11-server-actions.md`
- `knowledge/nextjs/13-middleware.md`
- `knowledge/rest-api/04-endpoints.md`
- `knowledge/rest-api/09-error-handling.md`
