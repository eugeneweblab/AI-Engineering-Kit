---
id: rest-api/04-endpoints
topic: rest-api
slug: endpoints
title: "Endpoints"
type: doc
order: 4
status: ready
tags: [rest-api, endpoints, Location, action, PATCH]
related: [rest-api/03-resource-design, rest-api/05-routing, rest-api/01-http, rest-api/07-status-codes, rest-api/10-pagination]
when_to_use: "Read before adding or changing an endpoint's method, path, or response shape on a REST API."
---
# Endpoints

## Purpose

This document defines how to specify individual endpoints: the method/path pairs that
make up an API, what each returns, and the conventions that keep the set coherent. It is
written so an agent can add an endpoint that fits the existing surface instead of
inventing a one-off.

Where [resource design](03-resource-design.md) picks the nouns, this doc governs the
concrete operations on them — the CRUD grid and the few justified exceptions to it.

## Why It Matters

An endpoint is the smallest unit a client actually calls. Consistency across endpoints is
what lets a developer learn the API once and reuse that knowledge everywhere: if
`GET /orders` paginates one way, they expect `GET /users` to paginate the same way. Every
endpoint that breaks the pattern costs every future integrator a lookup and a special
case. Coherence is a force multiplier; each inconsistency is a tax paid forever.

## Core Principles

- **Standard CRUD maps to standard verbs.** List `GET /things`, read `GET /things/{id}`,
  create `POST /things`, replace `PUT /things/{id}`, update `PATCH /things/{id}`, delete
  `DELETE /things/{id}`. Learn once, apply everywhere.
- **One operation, one endpoint.** A given method+path does exactly one thing. Do not
  branch on a body flag to do unrelated work.
- **The response shape is predictable.** Single items return an object; collections
  return a consistent envelope with the array plus pagination metadata.
- **Status code reflects the outcome.** `201` on create with `Location`, `204` on delete,
  `404` when the item is absent — see [status codes](07-status-codes.md).
- **Endpoints are additive.** New optional fields and new endpoints are safe; changing an
  existing endpoint's shape or semantics is a breaking change.

## Best Practices

- Follow the CRUD grid by default; only add a custom verb sub-resource
  (`POST /orders/{id}/cancel`) when the operation is a real state transition with side
  effects that no `PATCH` cleanly expresses. Document *why* in the spec.
- Always paginate list endpoints — never return an unbounded array. Return a consistent
  envelope so every collection reads the same way (see [pagination](10-pagination.md)).
- Return `201 Created` with a `Location` header (and usually the created body) so the
  client learns the new resource's URL without a second call.
- Make `DELETE` idempotent: deleting an already-gone resource returns `204` (or `404`
  consistently), never a `500`. Retried deletes must be safe.
- Validate input and return `400`/`422` with a machine-readable error body
  (see [validation](08-validation.md) and [error handling](09-error-handling.md)); never
  let a bad payload reach persistence.
- Scope every endpoint with [authorization](16-authorization.md): the caller must be
  allowed to touch *this specific* resource, not just be authenticated.

## Examples

**Good Example** — consistent CRUD, correct codes, paginated list

```http
POST /v1/orders            → 201 Created, Location: /v1/orders/8821   # returns new URL
GET  /v1/orders/8821       → 200 OK  { "id": "ord_8821", ... }        # one object
GET  /v1/orders?limit=20   → 200 OK  { "data": [...], "page": {...} } # envelope + paging
PATCH /v1/orders/8821      → 200 OK  { ...updated }                   # partial update
DELETE /v1/orders/8821     → 204 No Content                          # idempotent, no body
```

```json
// One collection envelope, reused by EVERY list endpoint
{
  "data": [ /* items */ ],
  "page": { "limit": 20, "nextCursor": "eyJpZCI6ODgyMX0" }
}
```

**Bad Example** — overloaded endpoint, wrong codes, unbounded list

```http
POST /v1/orders/manage
// One endpoint that creates, updates, OR deletes based on a body flag:
{ "op": "delete", "id": 8821 }
// - Verb hidden in the body → not resourceful, un-cacheable, un-routable.
// - Always returns 200, even on "create", so clients can't tell what happened.

GET /v1/orders
// Returns a bare array of ALL orders — no limit. First 100k-row tenant OOMs the server
// and the client, and the response shape differs from every other list endpoint.
```

## Common Mistakes

- A "do-everything" endpoint dispatching on a body `op`/`action` flag.
- List endpoints that return every row unbounded, risking timeouts and memory blowups.
- Returning `200` for creation and deletion instead of `201`/`204`, losing signal.
- Inconsistent collection envelopes, so each list endpoint must be parsed differently.
- `DELETE` that throws `500` on an already-deleted resource instead of being idempotent.
- Authenticating the caller but not checking they own the specific resource (IDOR).

## Production Tips

- Generate endpoint definitions from (or validate them against) the
  [OpenAPI](21-openapi.md) spec so path, method, and response codes cannot drift from docs.
- Emit per-endpoint metrics keyed by the route template, not the raw path, so
  `/orders/{id}` aggregates instead of exploding cardinality by ID.
- Contract-test each endpoint's status codes and envelope shape in CI, including the
  negative paths (missing item, bad body, unauthorized).

## AI Review Checklist

- Does the endpoint follow the standard CRUD verb/path mapping unless a real state
  transition justifies a custom sub-resource?
- Does each method+path do exactly one thing, with no body-flag branching?
- Do list endpoints paginate and return the same envelope as sibling collections?
- Are `201`+`Location`, `204`, and `404`/`409` used correctly per outcome?
- Is `DELETE` idempotent and safe to retry?
- Is per-resource authorization enforced, not just authentication?

## Related

- `knowledge/rest-api/03-resource-design.md`
- `knowledge/rest-api/05-routing.md`
- `knowledge/rest-api/01-http.md`
- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/10-pagination.md`
