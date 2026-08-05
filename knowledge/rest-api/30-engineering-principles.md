---
id: rest-api/30-engineering-principles
topic: rest-api
slug: engineering-principles
title: "REST API Engineering Principles"
type: doc
order: 30
status: ready
tags: [rest-api, engineering-principles]
related: [rest-api/02-rest-principles, rest-api/07-status-codes, rest-api/14-versioning, rest-api/18-idempotency, rest-api/27-best-practices]
when_to_use: "Read before designing a new REST API or making a cross-cutting change that many endpoints will inherit."
---
# REST API Engineering Principles

## Purpose

This document defines the durable engineering principles that make a REST API correct,
predictable, and safe to evolve. It is not a syntax reference for HTTP verbs or status
codes — those live in [http](01-http.md) and [status-codes](07-status-codes.md). It is
the set of decisions an agent should make *before* writing a handler, so that every
endpoint in the surface behaves consistently and no single change breaks a client.

An API is a contract with code you do not control. Once a client depends on a response
shape, that shape is load-bearing. These principles exist so the contract stays stable
while the implementation behind it keeps changing.

## Why It Matters

API mistakes are expensive in a way internal-code mistakes are not: you cannot refactor
a client you do not own. A field renamed on a whim, a `200` returned for a failure, an
endpoint that charges a card twice on retry — each becomes a production incident that a
consumer discovers before you do. The failures are also spread out: a single inconsistent
error shape forces every client to write special-case handling, multiplying your bug
across the whole ecosystem. Because the blast radius is every consumer at once, API
design is held to a higher bar than ordinary application code.

## Core Principles

- **Design the resource model first, endpoints second.** Model nouns (resources) and let
  HTTP verbs supply the actions. `POST /users/{id}/deactivate` is a smell; `PATCH /users/{id}`
  with `{ "status": "inactive" }` uses the protocol you already have.
- **Be consistent before you are clever.** One pagination style, one error shape, one
  casing convention across the whole surface. A predictable API needs no documentation to
  guess correctly; an inconsistent one needs docs for every endpoint.
- **Make the contract explicit and versioned.** The response shape, status codes, and error
  format are the contract. Breaking changes require a new [version](14-versioning.md), never
  a silent edit.
- **Honor HTTP semantics.** Status codes, methods, and headers have defined meanings —
  use them. Never return `200` with an error body; never make `GET` mutate state.
- **Design for retries.** Networks fail mid-request. Mutating endpoints must be safe to
  retry via [idempotency](18-idempotency.md) so a dropped response never double-charges.
- **Never trust the client.** Validate and authorize every request at the boundary. The
  server is the only place a rule is actually enforced.

## Best Practices

- Use plural nouns for collections and stable identifiers: `GET /orders/{id}`, not
  `GET /getOrder?id=`. The URL names a thing; the method says what to do with it.
- Pick one casing (`snake_case` or `camelCase`) for JSON fields and apply it everywhere.
  Mixing them forces clients to remember per-field rules.
- Return the right status code with a machine-readable [error body](09-error-handling.md).
  `4xx` means the client must change the request; `5xx` means the server failed and a
  retry may succeed.
- Make writes idempotent: `PUT`/`DELETE` are idempotent by definition, and `POST` should
  accept an `Idempotency-Key` for money-moving operations.
- Paginate every list endpoint from day one; an unbounded list is a latent outage once
  the table grows.
- Validate input against an explicit schema and reject unknown fields you do not expect,
  so a typo like `amont` fails loudly instead of being silently ignored.
- Set `Cache-Control` and `ETag` deliberately; treat [caching](19-caching.md) as part of
  the contract, not an afterthought.
- Never break a published field. Add new fields (safe) instead of renaming or removing
  existing ones (breaking).

## Examples

**Good Example** — resource-oriented, honest status, retry-safe

```http
POST /v1/payments HTTP/1.1
Content-Type: application/json
Idempotency-Key: 5f2b9c1e-3a44-4d8e-9c11-7b6a1f0e2d33   # same key => same result on retry

{ "amount": 2000, "currency": "usd", "source": "card_abc" }

HTTP/1.1 201 Created                                     # 201 for a created resource
Location: /v1/payments/pay_9Kd3                          # where the new resource lives
Content-Type: application/json

{ "id": "pay_9Kd3", "amount": 2000, "currency": "usd", "status": "succeeded" }
```

**Bad Example** — verb in URL, lying status, unsafe on retry

```http
POST /v1/doPayment HTTP/1.1                              # action in the URL, not a resource
Content-Type: application/json

{ "amount": 2000, "currency": "usd", "source": "card_abc" }
# no idempotency key => a retried request charges the card twice

HTTP/1.1 200 OK                                          # 200 even on failure below
Content-Type: application/json

{ "error": true, "message": "card declined" }            # error hidden in a 200 body;
                                                         # clients that check status think it worked
```

## Common Mistakes

- Encoding actions in URLs (`/createUser`, `/user/delete`) instead of using HTTP methods.
- Returning `200 OK` for errors, forcing clients to parse the body to learn what happened.
- Inconsistent response shapes — a bare array here, a `{ data: [...] }` envelope there.
- No idempotency on `POST`, so a client retry double-creates or double-charges.
- Breaking the contract in place (renaming a field) instead of shipping a new version.
- Leaking internal representations (database column names, stack traces) into responses.
- Skipping pagination until the list "gets big" — by then clients depend on the full dump.

## Production Tips

- Publish an [OpenAPI](21-openapi.md) spec and generate it from the same source the server
  uses, so the docs cannot drift from the implementation.
- Add contract tests that assert status code and response schema for each endpoint; run
  them in CI so a breaking change fails the build, not a customer.
- Log a stable `request_id` on every response and error so support can trace one call.

## AI Review Checklist

- Are URLs resource-oriented (nouns) with actions expressed through HTTP methods?
- Does every response use the correct status code, never `200` for an error?
- Is the error body shape identical across all endpoints?
- Are mutating endpoints safe to retry (idempotent or `Idempotency-Key`)?
- Are list endpoints paginated and input validated against an explicit schema?
- Do changes add fields rather than rename or remove published ones?

## Related

- `knowledge/rest-api/02-rest-principles.md`
- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/14-versioning.md`
- `knowledge/rest-api/18-idempotency.md`
- `knowledge/rest-api/27-best-practices.md`
