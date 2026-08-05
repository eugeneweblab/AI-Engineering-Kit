---
id: backend/06-api-design
topic: backend
slug: api-design
title: "API Design"
type: doc
order: 6
status: ready
tags: [backend, api-design, list, toISOString, OrderRow, Deprecation, Sunset]
related: [backend/09-validation, backend/12-error-handling, backend/11-authorization, backend/24-documentation, backend/07-business-logic]
when_to_use: "Read before designing or reviewing any HTTP/RPC endpoint, request/response shape, or public API contract."
---
# API Design

## Purpose

This document defines how to design the *contract* a backend exposes to its callers:
resource shapes, verbs, status codes, versioning, pagination, and errors. It is written
so an agent can add or review an endpoint without breaking existing clients or leaking
internal concerns.

An API is a promise. Every consumer — a mobile app, a partner integration, another
service — depends on its shape not changing underneath them. Design decisions here are
expensive to reverse because you do not control who is calling.

## Why It Matters

The API is the widest and longest-lived interface in the system. Internal code can be
refactored freely; a published endpoint cannot, because breaking it breaks callers you
cannot see or redeploy. A sloppy contract leaks database columns, invents inconsistent
error shapes, and forces every client to special-case each route. Consistency is not
cosmetic: it is what lets a client author write one HTTP layer instead of thirty.

## Core Principles

- **The contract is separate from the storage model.** Never serialize a database row
  directly. Map to an explicit response DTO so a schema change does not silently alter
  the API — the cost is one mapping layer, the payoff is freedom to refactor internals.
- **Be consistent over clever.** Same casing, same date format (RFC 3339 UTC), same
  error envelope, same pagination on every endpoint. A caller should never have to guess.
- **Model resources, use verbs correctly.** In REST, the URL names a noun; the HTTP
  method is the verb. `POST /orders`, not `POST /createOrder`.
- **Reads are safe, writes are explicit.** `GET` must never mutate. Make unsafe writes
  idempotent where possible so a retried request does not double-charge.
- **Design for evolution.** Add fields without breaking; never repurpose or remove one
  in place. Version the API when a break is unavoidable.

## Best Practices

- Use correct status codes: `200` read, `201` created (with `Location`), `204` no body,
  `400` bad input, `401` unauthenticated, `403` unauthorized, `404` missing, `409`
  conflict, `422` semantic validation failure, `429` rate-limited.
- Return one consistent error envelope everywhere: a stable machine-readable `code`, a
  human `message`, and per-field details. Never leak stack traces or SQL. See
  [error handling](12-error-handling.md).
- Paginate every list endpoint. Prefer **cursor** pagination for large or live datasets;
  offset pagination drifts and slows as pages grow.
- Validate and coerce input at the boundary before it reaches business logic. See
  [validation](09-validation.md).
- Make `POST`/`PATCH` idempotent via an `Idempotency-Key` header for money or side-effect
  operations, so client retries are safe.
- Version explicitly (URL prefix `/v1` or a media type). Publish the contract as OpenAPI
  and keep it in sync — see [documentation](24-documentation.md).
- Return created/updated resources in the response so clients need no follow-up read.
- Enforce a maximum request body size and a per-list result cap to bound resource use.

## Examples

**Good Example** — explicit DTO, correct codes, cursor pagination

```ts
// Response shape is an explicit contract, decoupled from the DB row.
type OrderDTO = { id: string; status: string; totalCents: number; createdAt: string };

function toOrderDTO(row: OrderRow): OrderDTO {
  return {
    id: row.id,
    status: row.status,
    totalCents: row.total_cents,        // snake_case column -> stable camelCase field
    createdAt: row.created_at.toISOString(), // RFC 3339 UTC, never a raw Date
  };
}

// GET /v1/orders?limit=20&cursor=... -> stable, bounded, paginated list
app.get("/v1/orders", async (req, res) => {
  const limit = Math.min(Number(req.query.limit ?? 20), 100); // hard cap
  const page = await orders.list({ cursor: req.query.cursor, limit });
  res.status(200).json({ data: page.rows.map(toOrderDTO), nextCursor: page.next });
});
```

**Bad Example** — leaks the table, wrong verb, unbounded list

```ts
// Verb in the URL, and it is a GET that also mutates — both wrong.
app.get("/getOrders", async (req, res) => {
  await orders.touchLastViewed(req.user.id);     // GET must be side-effect free
  const rows = await db.query("SELECT * FROM orders"); // no limit -> unbounded payload
  res.json(rows); // serializes raw columns: password_hash, internal_flags, snake_case...
});
```

## Common Mistakes

- Serializing database entities directly, coupling the public API to the schema.
- Verbs in URLs (`/createOrder`, `/deleteUser`) instead of proper HTTP methods.
- Inconsistent error shapes across endpoints, forcing clients to special-case each route.
- Returning `200 OK` for failures with an error hidden in the body.
- Unpaginated list endpoints that grow without bound and time out in production.
- Breaking changes shipped without a version bump, silently breaking existing clients.
- Mixing date formats or casing between endpoints.

## Production Tips

- Publish and lint the OpenAPI spec in CI; a diff that breaks the contract should fail
  the build.
- Log request id, route, status, and latency per call; alert on `5xx` and `429` spikes.
- Deprecate before removing: add a `Deprecation`/`Sunset` header and a migration window.
- Contract-test against the spec so server and client cannot drift apart.

## AI Review Checklist

- Does the endpoint return an explicit DTO rather than a raw database row?
- Are HTTP methods and status codes used correctly (no verbs in URLs, no mutating `GET`)?
- Do all endpoints share one error envelope and one date/casing convention?
- Is every list endpoint paginated and result-capped?
- Are write operations idempotent where a retry could cause harm?
- Is any breaking change gated behind a new API version?
- Is input validated at the boundary before reaching business logic?

## Related

- `knowledge/backend/09-validation.md`
- `knowledge/backend/12-error-handling.md`
- `knowledge/backend/11-authorization.md`
- `knowledge/backend/24-documentation.md`
- `knowledge/backend/07-business-logic.md`
