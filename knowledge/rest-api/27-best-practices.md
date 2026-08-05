---
id: rest-api/27-best-practices
topic: rest-api
slug: best-practices
title: "REST API Best Practices"
type: doc
order: 27
status: ready
tags: [rest-api, best-practices, kebab-case, cursor, camelCase, Location, snake_case, PascalCase]
related: [rest-api/02-rest-principles, rest-api/03-resource-design, rest-api/07-status-codes, rest-api/14-versioning, rest-api/24-security]
when_to_use: "Read before designing a new REST API or reviewing one for consistency and long-term maintainability."
---
# REST API Best Practices

## Purpose

This document consolidates the design conventions that make a REST API predictable,
consistent, and stable over time. It is a synthesis, not a replacement, for the focused
docs: [REST principles](02-rest-principles.md), [resource design](03-resource-design.md),
[status codes](07-status-codes.md), and [versioning](14-versioning.md). Use it as the
default checklist when shaping endpoints, so every route in the API feels like it was
designed by one person on one day.

## Why It Matters

An API is a contract that outlives the team that wrote it. Once clients depend on a route,
its shape is frozen — you cannot rename a field or change a status code without breaking
them. Inconsistency is the tax clients pay forever: if `/users` paginates with `page` but
`/orders` uses `cursor`, every integration has to special-case each endpoint. Consistency
is what lets a developer guess the next endpoint correctly without reading the docs. The
cost of getting conventions right is a few minutes of thought; the cost of getting them
wrong is a permanent, versioned migration.

## Core Principles

- **Model resources as nouns, act with HTTP verbs.** `GET /orders/42`, not `GET /getOrder?id=42`.
  The URL names a thing; the method names the action. See [resource design](03-resource-design.md).
- **Use HTTP semantics as the contract.** Correct status codes, correct methods, correct
  idempotency. `GET` never mutates; `PUT`/`DELETE` are idempotent; `POST` creates.
- **Be consistent above all.** One naming style, one pagination style, one error shape, one
  date format across the whole API. Consistency beats local cleverness.
- **Design for evolution.** Add fields without breaking clients; version only for breaking
  changes. Clients must ignore unknown fields. See [versioning](14-versioning.md).
- **Make errors machine-readable.** Return a structured, documented error body with a
  stable code, not just a status and a prose string.
- **Secure and validate by default.** Every endpoint validates input and authorizes the
  caller; there is no "internal, so it's fine" route. See [security](24-security.md).

## Best Practices

- Name collections with plural nouns (`/users`, `/orders`) and nest to show relationships
  (`/users/42/orders`); do not nest more than one or two levels deep.
- Pick one casing convention and keep it everywhere: `snake_case` or `camelCase` for JSON
  fields, `kebab-case` in URL paths. Do not mix.
- Return the right status code: `200` for success with a body, `201` + `Location` for
  creation, `204` for success with no body, `400/422` for bad input, `401/403` for auth,
  `404` for missing, `409` for conflict. See [status codes](07-status-codes.md).
- Use a single, documented error envelope with a stable machine code, human message, and
  request id. See [error handling](09-error-handling.md).
- Use ISO 8601 UTC timestamps (`2026-07-07T14:58:00Z`) and standard field types; never
  invent ad-hoc date formats.
- Make writes idempotent where possible; support an idempotency key on `POST` for money-
  moving operations so retries do not double-charge. See [idempotency](18-idempotency.md).
- Paginate every collection with one consistent strategy, and cap page size.
- Publish an OpenAPI spec as the source of truth and keep it in sync with the code. See
  [OpenAPI](21-openapi.md).

## Examples

**Good Example** — resource-oriented, correct status, consistent shape

```http
POST /v1/orders
Content-Type: application/json
Idempotency-Key: 6f1c...   # safe to retry; the server dedupes on this key

{ "customer_id": "cus_123", "items": [{ "sku": "A1", "qty": 2 }] }

HTTP/1.1 201 Created
Location: /v1/orders/ord_789          # where the new resource lives
Content-Type: application/json

{ "id": "ord_789", "status": "pending", "total_cents": 4980,
  "created_at": "2026-07-07T14:58:00Z" }   # ISO UTC, consistent field naming
```

**Bad Example** — verb in URL, wrong method and status, inconsistent shape

```http
GET /v1/createOrder?customerId=cus_123&items=A1:2   # GET that mutates; verb in path

HTTP/1.1 200 OK                                      # created, but returns 200, no Location
{ "OrderID": 789, "Status": "PENDING",               # PascalCase here, snake elsewhere
  "created": "07/07/2026 2:58pm" }                    # ambiguous, non-ISO date, no timezone
```

## Common Mistakes

- Verbs in URLs (`/getUser`, `/deleteOrder`) instead of HTTP methods on noun resources.
- Returning `200 OK` for everything, including errors, forcing clients to parse the body.
- Inconsistent field casing, date formats, or pagination between endpoints.
- Breaking changes shipped without a version bump, silently breaking live clients.
- Prose-only error responses with no stable machine-readable code.
- Deeply nested resource paths that couple unrelated entities.
- A hand-written doc that has drifted from the actual API behavior.

## Production Tips

- Add a contract test (or spec-driven test) so the API cannot drift from its OpenAPI spec.
- Provide a changelog and deprecation policy; announce breaking changes with a sunset date.
- Lint the API design (e.g. Spectral) in CI to enforce naming and status conventions.

## AI Review Checklist

- Are resources nouns and actions expressed with HTTP methods?
- Are status codes semantically correct for each outcome?
- Is naming, casing, date format, and pagination consistent across all endpoints?
- Do responses use one documented error envelope with stable codes?
- Are new changes additive, with versioning reserved for breaking changes?
- Are money-moving `POST`s idempotent via an idempotency key?
- Does an OpenAPI spec exist and match the implemented behavior?

## Related

- `knowledge/rest-api/02-rest-principles.md`
- `knowledge/rest-api/03-resource-design.md`
- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/14-versioning.md`
- `knowledge/rest-api/24-security.md`
