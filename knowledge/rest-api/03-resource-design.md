---
id: rest-api/03-resource-design
topic: rest-api
slug: resource-design
title: "Resource Design"
type: doc
order: 3
status: ready
tags: [rest-api, resource-design, subscription, password_hash, invoice, camelCase, snake_case, PATCH]
related: [rest-api/02-rest-principles, rest-api/04-endpoints, rest-api/05-routing, rest-api/10-pagination, rest-api/14-versioning]
when_to_use: "Read before turning a domain model into resources, URLs, and representations for a new or extended API."
---
# Resource Design

## Purpose

This document defines how to turn a domain into REST resources: choosing nouns, naming
URLs, structuring representations, and modeling relationships. It is written so an agent
can design a resource model that is consistent, stable, and independent of the database
behind it.

Resource design is the hardest-to-reverse part of an API. URLs and field names become
public contract the moment a client integrates. Getting the nouns and shapes right up
front avoids a painful `/v2`.

## Why It Matters

Resources are the vocabulary integrators learn. A clean, consistent model is
self-explanatory — a developer who has used `/users/{id}` can guess `/orders/{id}`
without reading docs. A model that leaks your schema (table names, join tables, ORM
column casing) welds every client to your database, so you can no longer refactor storage
without breaking them. The resource model is where you decide whether future you is free
or trapped.

## Core Principles

- **Resources are nouns.** A resource is a thing (`order`, `invoice`, `subscription`),
  not an action. Actions are HTTP methods on the thing.
- **Collections and items pair up.** `/orders` is a collection; `/orders/{id}` is one
  item. This two-level pattern is the backbone of every REST URL.
- **The representation is a contract, not a table row.** Expose fields the consumer
  needs, named for the domain — not raw columns, internal enums, or foreign keys.
- **Model relationships as nested paths or links, one level deep.** `/users/{id}/orders`
  reads naturally; `/users/{id}/orders/{oid}/items/{iid}/tax` does not.
- **Identifiers are opaque and stable.** A client should treat an ID as a token, not
  parse meaning from it. Never expose sequential DB IDs where enumeration is a risk.

## Best Practices

- Use plural nouns for collections (`/products`, not `/product`) and lowercase,
  hyphenated multi-word paths (`/purchase-orders`). Pick one casing for JSON fields
  (`camelCase` or `snake_case`) and apply it everywhere.
- Keep URL nesting to at most one parent level; beyond that, prefer a top-level resource
  with a filter (`/orders?userId=42`) so the resource stays addressable on its own.
- Design representations from the consumer's needs: include what clients read together,
  omit internal fields, and never leak `password_hash`, soft-delete flags, or tenant keys.
- Use ISO 8601 UTC timestamps (`2026-07-07T13:00:00Z`), typed values (numbers as numbers),
  and stable enum strings. Document every field in [OpenAPI](21-openapi.md).
- For actions that are not clean nouns (e.g. "publish"), prefer a state field via `PATCH`;
  fall back to a sub-resource verb (`POST /articles/{id}/publish`) only when no noun fits.
- Prefer UUIDs/ULIDs or hashed IDs over raw auto-increment integers to avoid leaking row
  counts and enabling ID enumeration attacks.

## Examples

**Good Example** — domain-shaped, stable resource

```json
// GET /v1/orders/8821  — named for the domain, no schema leakage
{
  "id": "ord_8821",                       // opaque, prefixed, non-enumerable
  "status": "shipped",                    // stable enum string
  "total": { "amount": 4200, "currency": "USD" }, // typed, self-describing
  "createdAt": "2026-07-07T13:00:00Z",    // ISO 8601 UTC
  "customer": { "id": "cus_42", "href": "/v1/customers/42" } // relationship as a link
}
```

**Bad Example** — leaks the database, unstable shape

```json
// GET /v1/getOrder?order_id=8821  — verb in URL, raw row dumped out
{
  "ORDER_ID": 8821,          // sequential int → enumerable; ALL_CAPS column casing
  "cust_fk": 42,             // exposes a foreign key; client now depends on the join
  "status_code": 3,          // magic number instead of a stable enum string
  "created": 1751889600,     // ambiguous epoch, no timezone contract
  "is_deleted": false,       // internal soft-delete flag leaks storage strategy
  "internal_notes": "..."    // field the consumer must never see
}
```

## Common Mistakes

- Mirroring the database: table names as paths, column names as fields, FKs in the body.
- Singular vs plural inconsistency (`/user` here, `/orders` there) so clients guess wrong.
- Deeply nested URLs that make a resource impossible to address on its own.
- Exposing sequential integer IDs, enabling enumeration of every record.
- Baking actions into URLs (`/createOrder`) instead of using resources plus methods.
- Returning different field casing or timestamp formats across endpoints.

## Production Tips

- Add a serialization/DTO layer between storage and the API so a schema change cannot
  silently alter the contract; the mapping is where you enforce field-level control.
- Reserve an `id` prefix scheme (`ord_`, `cus_`) early — it makes logs and support
  tickets self-explanatory and prevents cross-type ID confusion.
- Treat any new field as additive-only; renaming or removing one is a breaking change
  gated by [versioning](14-versioning.md).

## AI Review Checklist

- Are resources nouns, with actions expressed via HTTP methods?
- Are collections plural and URL casing/field casing consistent across the whole API?
- Does any representation leak table names, foreign keys, or internal-only fields?
- Is URL nesting kept to one parent level, with deeper relations exposed via filters?
- Are IDs opaque and non-enumerable rather than raw auto-increment integers?
- Are timestamps ISO 8601 UTC and enums stable strings, documented in the spec?

## Related

- `knowledge/rest-api/02-rest-principles.md`
- `knowledge/rest-api/04-endpoints.md`
- `knowledge/rest-api/05-routing.md`
- `knowledge/rest-api/10-pagination.md`
- `knowledge/rest-api/14-versioning.md`
