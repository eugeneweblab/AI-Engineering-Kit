---
id: rest-api/07-status-codes
topic: rest-api
slug: status-codes
title: "Status Codes"
type: doc
order: 7
status: ready
tags: [rest-api, status-codes]
related: [rest-api/09-error-handling, rest-api/06-request-response, rest-api/08-validation, rest-api/18-idempotency, rest-api/16-authorization]
when_to_use: "Read before choosing the HTTP status code an endpoint returns for success, redirect, client error, or server error."
---
# Status Codes

## Purpose

This document defines which HTTP status code an endpoint must return for each outcome.
It is written so an agent can pick the correct code every time, because the status line
is the first — and often only — thing clients, proxies, and monitors inspect.

The status code is machine-readable control flow. Load balancers retry on it, caches
store on it, dashboards alert on it. Getting it wrong silently breaks systems you do not
control.

## Why It Matters

A `200 OK` wrapping an error body is the single most damaging status mistake: clients
treat the call as successful, retries never fire, alerts never trigger, and a broken
system looks healthy on every dashboard. Conversely, returning `500` for a client's bad
input pages an on-call engineer for a non-bug and pollutes error budgets. Status codes
are the API's nervous system; miswiring them makes the whole system react to the wrong
signals.

## Core Principles

- **The class encodes responsibility.** `2xx` success, `3xx` redirect, `4xx` the client
  must change its request, `5xx` the server failed and the client may retry. Choose the
  class first, the exact code second.
- **Status and body must agree.** Never return `200` with an error payload, or `4xx`/`5xx`
  with a success payload. The status is the source of truth.
- **`4xx` means "do not retry unchanged."** The request itself is wrong; retrying it
  verbatim will fail again. `5xx` means "the server may recover," so it is retryable.
- **Be specific, but never wrong.** A precise code (`409`, `422`, `429`) helps clients,
  but a correct general code (`400`) beats a wrong specific one.
- **Reserve `5xx` for genuine server faults.** Validation failures, missing resources,
  and auth problems are the client's responsibility and are always `4xx`.

## Best Practices

- Use `201 Created` with a `Location` header for successful resource creation; `200` for
  reads and in-place updates; `204 No Content` for successful requests with no body.
- Use `202 Accepted` when work is queued asynchronously and not yet done.
- Distinguish `401 Unauthorized` (not authenticated — who are you?) from
  `403 Forbidden` (authenticated but not allowed) — see [authorization](16-authorization.md).
- Use `404 Not Found` for a missing resource; use `404` (not `403`) when you must hide a
  resource's very existence from an unauthorized caller.
- Use `409 Conflict` for state conflicts (duplicate, version mismatch) and `422
  Unprocessable Content` for well-formed requests that fail business validation.
- Use `429 Too Many Requests` with a `Retry-After` header for rate limiting.
- Use `412 Precondition Failed` with conditional headers for optimistic concurrency, and
  `304 Not Modified` for successful cache revalidation.
- Never invent non-standard codes (`299`, `450`); clients and proxies ignore or mishandle
  them.

## Examples

**Good Example** — creation and conflict signalled precisely

```http
POST /v1/users HTTP/1.1
Content-Type: application/json

{ "email": "ada@example.com" }
```

```http
HTTP/1.1 201 Created                       // resource made, not just "ok"
Location: /v1/users/usr_88                  // where the new resource lives
Content-Type: application/json

{ "id": "usr_88", "email": "ada@example.com" }
```

```http
// second POST with the same email:
HTTP/1.1 409 Conflict                       // client must change the request; not a 500
Content-Type: application/problem+json

{ "type": "/errors/email-taken", "title": "Email already registered" }
```

**Bad Example** — success status hiding a failure

```http
POST /v1/users HTTP/1.1
{ "email": "not-an-email" }
```

```http
HTTP/1.1 200 OK                             // lies: the request failed
Content-Type: application/json

{ "success": false, "error": "invalid email" }
// client sees 200, treats it as success, never retries or surfaces the error;
// monitoring shows 100% healthy while every signup silently fails
```

## Common Mistakes

- `200 OK` with `{ "error": ... }` in the body — the cardinal sin; breaks retries/alerts.
- Returning `500` for validation errors (should be `400`/`422`) — pages on-call for a
  client bug and burns the error budget.
- Using `401` when the user is authenticated but lacks permission (should be `403`).
- `200` instead of `201` on creation, or omitting the `Location` header.
- `403` for a missing resource that leaks its existence when `404` would hide it.
- Returning `400` for everything, forcing clients to parse prose to find the real cause.
- Inventing custom codes that proxies and HTTP clients do not understand.

## Production Tips

- Alert on `5xx` rate and treat any sustained `5xx` as an incident; alert on `4xx` spikes
  separately (often a client deploy, not your bug).
- Ensure your framework's default error handler maps uncaught exceptions to `500`, not to
  a stack trace with `200`.
- Set `Retry-After` on `429` and `503` so well-behaved clients back off correctly.
- Test the status code, not just the body, in integration tests — assert the exact code.

## AI Review Checklist

- Does every response's status class match reality (`2xx` only on real success)?
- Do status and body agree — no error payloads under `2xx`?
- Are validation and business-rule failures `4xx` (never `5xx`)?
- Is `401` used only for authentication and `403` only for authorization?
- Does creation return `201` with a `Location` header?
- Are `429`/`503` accompanied by `Retry-After`?
- Are all codes standard IANA codes, not invented ones?

## Related

- `knowledge/rest-api/09-error-handling.md`
- `knowledge/rest-api/06-request-response.md`
- `knowledge/rest-api/08-validation.md`
- `knowledge/rest-api/18-idempotency.md`
- `knowledge/rest-api/16-authorization.md`
