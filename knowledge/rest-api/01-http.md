---
id: rest-api/01-http
topic: rest-api
slug: http
title: "REST API HTTP"
type: doc
order: 1
status: ready
tags: [rest-api, http, PUT, PATCH, Last-Modified, Accept, ETag, Content-Type]
related: [rest-api/02-rest-principles, rest-api/07-status-codes, rest-api/06-request-response, rest-api/18-idempotency, rest-api/19-caching]
when_to_use: "Read before choosing an HTTP method, status code, or header, or when reviewing how an endpoint uses the protocol."
---
# REST API HTTP

## Purpose

This document defines the HTTP semantics every REST API depends on: methods, status
codes, headers, and the properties (safe, idempotent, cacheable) that make requests
behave predictably. It is written so an agent can pick the correct verb and code for an
operation without guessing.

HTTP is not a dumb transport for JSON. It is an application protocol with precise,
standardized meaning (RFC 9110). REST works *because* it uses that meaning; ignore it
and you lose caching, retries, and interoperability for free.

## Why It Matters

Clients, proxies, CDNs, and browsers all act on HTTP semantics automatically. A `GET`
may be cached and retried without asking; a `DELETE` may be retried after a network
blip. If your endpoint violates the contract — a `GET` that mutates state, a `200` that
hides an error — that automatic machinery turns against you: caches serve stale writes,
retries duplicate side effects, and monitoring reports success on failure. The protocol
only protects you when you obey it.

## Core Principles

- **Method conveys intent.** `GET` reads, `POST` creates or triggers, `PUT` replaces,
  `PATCH` partially updates, `DELETE` removes. The verb tells every intermediary what is
  safe to do with the request.
- **Safe methods never change state.** `GET`, `HEAD`, `OPTIONS` must have no
  side effects. Anything cacheable or crawlable will be called at will.
- **Idempotent methods can be retried.** `GET`, `PUT`, `DELETE`, `HEAD` must yield the
  same server state whether called once or five times. `POST` is not idempotent unless
  you make it so (see [idempotency](18-idempotency.md)).
- **Status codes are the outcome, not decoration.** The class (2xx/3xx/4xx/5xx) is the
  machine-readable result; clients branch on it before reading the body.
- **Headers carry metadata; the body carries the representation.** Content type,
  caching, auth, and conditional requests belong in headers, not invented body fields.

## Best Practices

- Map operations to methods honestly. Never use `GET` for a mutation or tunnel actions
  through `POST /doSomething` when a resource verb fits.
- Return the most specific correct status code: `201 Created` with a `Location` header
  for creation, `204 No Content` for a successful delete, `409 Conflict` for a state
  clash — not a blanket `200`. See [status codes](07-status-codes.md).
- Send and require `Content-Type: application/json` (or the negotiated type); reject
  bodies you cannot parse with `415 Unsupported Media Type`.
- Support conditional requests with `ETag`/`If-None-Match` and `Last-Modified` so
  clients and caches can revalidate cheaply (see [caching](19-caching.md)).
- Prefer `PUT` for full replacement and `PATCH` for partial updates; do not overload one
  to do both.
- Never put secrets, tokens, or PII in the URL/query string — URLs are logged by proxies
  and servers. Use headers for credentials.

## Examples

**Good Example** — correct verbs, codes, and headers

```http
POST /v1/orders HTTP/1.1
Content-Type: application/json
Idempotency-Key: 9f1c-...    # lets the client safely retry this non-idempotent POST

{ "sku": "A-100", "qty": 2 }

HTTP/1.1 201 Created          # created, not a generic 200
Location: /v1/orders/8821    # where the new resource lives
ETag: "v1"                   # enables later conditional GET/PUT
```

**Bad Example** — mutation over GET, lying status, secret in URL

```http
GET /v1/deleteOrder?id=8821&token=SECRET HTTP/1.1
# GET must be safe: a crawler or prefetch will now delete data.
# The action is tunneled into a verb-in-path instead of DELETE /orders/8821.
# The token is in the URL, so it lands in access logs and browser history.

HTTP/1.1 200 OK
{ "error": "not allowed" }
# 200 with an error body: caches store it, clients think it succeeded.
```

## Common Mistakes

- Using `GET` (or `POST`) for everything and encoding the real verb in the path.
- Returning `200 OK` for failures, hiding errors from clients and monitoring.
- Making `POST` retries duplicate orders because no idempotency mechanism exists.
- Putting tokens, passwords, or PII in query strings where they get logged.
- Ignoring `Content-Type` / `Accept`, so a client's format expectations are unmet.
- Treating `PATCH` and `PUT` as interchangeable, corrupting partial vs full semantics.

## Production Tips

- Log method, path template (not the raw path), and status class so dashboards can spot
  a spike in 5xx or a route that wrongly returns 2xx on error.
- Set sane timeouts and honor `Retry-After` on `429`/`503` so clients back off correctly.
- Enforce HTTPS everywhere and send `Strict-Transport-Security`; HTTP semantics assume a
  secure channel for credentials.

## AI Review Checklist

- Does each endpoint use the semantically correct method (no mutations behind `GET`)?
- Are safe methods free of side effects and idempotent methods truly retry-safe?
- Is the returned status code the most specific correct one, never a `200` on error?
- Are `Content-Type`/`Accept` validated and mismatches rejected with `415`?
- Are credentials and PII kept out of URLs and query strings?
- Are `ETag`/`Last-Modified` provided where conditional requests would help?

## Related

- `knowledge/rest-api/02-rest-principles.md`
- `knowledge/rest-api/06-request-response.md`
- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/18-idempotency.md`
- `knowledge/rest-api/19-caching.md`
