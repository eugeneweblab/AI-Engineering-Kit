---
id: rest-api/06-request-response
topic: rest-api
slug: request-response
title: "Request Response"
type: doc
order: 6
status: ready
tags: [rest-api, request-response, Content-Type, Content-Length, Accept, user_id, userId, gzip]
related: [rest-api/07-status-codes, rest-api/08-validation, rest-api/09-error-handling, rest-api/19-caching, rest-api/03-resource-design]
when_to_use: "Read before designing request or response bodies, headers, or content negotiation for any endpoint."
---
# Request Response

## Purpose

This document defines the contract that travels over the wire: what a client sends
(method, headers, body) and what the server sends back (status, headers, body). It is
written so an agent can design or review a request/response shape that is predictable,
versionable, and safe to evolve.

The message is the API. Clients couple to the exact field names, types, and headers you
emit, so every choice here is a long-term commitment. Treat the payload shape as a
public interface, not an implementation detail.

## Why It Matters

Clients break on the smallest inconsistency: a field that is sometimes `null` and
sometimes absent, a date that is sometimes epoch millis and sometimes ISO-8601, a
`Content-Type` that lies about the body. These bugs surface in production, on other
teams' machines, long after the code shipped. A disciplined request/response contract is
what lets you add features without a coordinated redeploy of every consumer. The cost of
sloppiness is paid by everyone who integrates with you, forever.

## Core Principles

- **One representation per resource.** The object returned by `GET /orders/42` should be
  the same shape accepted by `POST`/`PUT`, minus server-owned fields. Divergent shapes
  force clients to maintain two mental models.
- **Always declare `Content-Type`.** Never let the client guess. Send
  `Content-Type: application/json; charset=utf-8` on every body-bearing response.
- **Be strict in what you accept, explicit in what you emit.** Reject unknown fields on
  input (fail fast on typos); never emit fields the contract does not document.
- **Fields are stable and typed.** A field never changes type or meaning across
  responses. Optional data is *omitted* or explicitly `null` — pick one policy and hold
  it API-wide.
- **Envelope collections, not single resources.** Wrap lists in an object so you can add
  pagination metadata later without a breaking change; return single resources bare.

## Best Practices

- Use JSON as the default. Pick a casing convention (`snake_case` or `camelCase`) and
  enforce it everywhere — mixed casing in one payload is a defect.
- Represent timestamps as ISO-8601 UTC strings (`2026-07-07T13:55:00Z`). Represent money
  as integer minor units plus a currency code, never floats.
- Honor `Accept` for content negotiation; return `406 Not Acceptable` if you cannot
  satisfy it rather than silently sending JSON.
- Require `Content-Type` on requests with a body and return `415 Unsupported Media Type`
  if it is missing or wrong. Do not sniff the body.
- Set `Content-Length` (or use chunked encoding) and relevant caching headers
  (`ETag`, `Cache-Control`) — see [caching](19-caching.md).
- Echo a correlation id (`X-Request-Id`) back to the client for tracing.
- Keep request bodies bounded: enforce a max body size and reject oversized payloads with
  `413 Content Too Large` before parsing.
- Version the media type or the path when the shape must change incompatibly — see
  [versioning](14-versioning.md).

## Examples

**Good Example** — enveloped collection, typed fields, explicit content type

```http
GET /v1/orders?limit=2 HTTP/1.1
Accept: application/json
```

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
ETag: "a1b2c3"
X-Request-Id: 6f1d...

{
  "data": [
    {
      "id": "ord_42",
      "status": "shipped",
      "total_minor": 1299,           // integer minor units, never a float
      "currency": "USD",
      "created_at": "2026-07-07T13:55:00Z"  // ISO-8601 UTC, unambiguous
    }
  ],
  "pagination": { "next_cursor": "b3z9", "limit": 2 }  // room to grow, no break
}
```

**Bad Example** — untyped, inconsistent, undeclared

```http
HTTP/1.1 200 OK

[                                  // bare array: cannot add metadata later
  {
    "id": 42,                      // number here, string elsewhere → client bug
    "Status": "shipped",           // PascalCase in a camelCase API
    "total": 12.99,                // float money → rounding errors accumulate
    "created": 1751896500          // epoch: which unit? UTC? undocumented
  }
]
// no Content-Type: the client is left to guess how to parse this
```

## Common Mistakes

- Returning a bare JSON array for a collection, then having no place to put pagination.
- Mixing `null` and "field absent" arbitrarily so clients cannot distinguish them.
- Floats for currency, unlabeled epoch timestamps, or booleans encoded as `"true"`.
- Omitting `Content-Type`, or sending `text/plain` for a JSON body.
- Silently ignoring unknown request fields, so a client's typo is never caught.
- Different field names for the same concept across endpoints (`userId` vs `user_id`).
- Leaking internal fields (DB row version, soft-delete flags) into the public response.

## Production Tips

- Validate outgoing responses against your OpenAPI schema in CI so drift is caught before
  release — see [openapi](21-openapi.md).
- Compress large responses (`gzip`/`br`) and set `Vary: Accept-Encoding`.
- Cap and paginate every list endpoint by default; an unbounded list is a latent outage.
- Log request/response *metadata* (id, size, status, latency) but never full bodies with
  secrets or PII.

## AI Review Checklist

- Does every body-bearing response declare an accurate `Content-Type`?
- Are collections enveloped in an object, and single resources returned bare?
- Are field names, casing, timestamp, and money formats consistent API-wide?
- Are unknown request fields rejected rather than silently ignored?
- Is request body size bounded, with `413` on overflow?
- Is the response shape covered by the schema/OpenAPI contract in CI?
- Are internal-only fields kept out of the public representation?

## Related

- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/08-validation.md`
- `knowledge/rest-api/09-error-handling.md`
- `knowledge/rest-api/19-caching.md`
- `knowledge/rest-api/03-resource-design.md`
