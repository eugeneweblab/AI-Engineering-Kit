---
id: rest-api/100-common-antipatterns
topic: rest-api
slug: common-antipatterns
title: "REST API Common Antipatterns"
type: doc
order: 100
status: ready
tags: [rest-api, common-antipatterns]
related: [rest-api/02-rest-principles, rest-api/07-status-codes, rest-api/09-error-handling, rest-api/16-authorization, rest-api/18-idempotency]
when_to_use: "Read when designing or reviewing a REST endpoint to catch the recurring mistakes before they ship."
---
# REST API Common Antipatterns

## Purpose

This is a field guide to the REST API mistakes that recur most often and cost the most.
Each entry names the antipattern, explains *why it is wrong* (the concrete failure it
causes), and gives *the fix*. Use it as a lookup while writing or reviewing endpoints —
when a design matches one of these shapes, stop and apply the fix before it reaches a
client you cannot change.

## Why It Matters

These patterns are seductive because each one is locally reasonable — a verb in a URL
reads fine, a `200` on every response simplifies the client's first draft. The cost shows
up later and elsewhere: in the consumer's retry logic, in a double-charged customer, in an
outage when a table grows. Recognizing the shape early is far cheaper than migrating every
client off it after the fact.

## Antipatterns

### 1. Verbs in the URL

**Why it is wrong.** `POST /createOrder`, `GET /getUser?id=5`, `POST /order/cancel` reinvent
HTTP inside the path. The method already carries the action, so you end up with two
overlapping vocabularies and no consistency across the surface.

**The fix.** Name resources with nouns and let methods act on them:
`POST /orders`, `GET /users/5`, `POST /orders/5/cancellation` (or `PATCH /orders/5` with a
status change). See [rest-principles](02-rest-principles.md).

### 2. Returning `200 OK` for errors

**Why it is wrong.** A `200` with `{ "error": "declined" }` lies to every client, proxy,
and monitoring tool that checks status. Clients that trust the status treat a failure as a
success; your error-rate dashboards read zero while customers are failing.

**The fix.** Return the honest [status code](07-status-codes.md): `400` for bad input,
`402`/`409` for business failures, `500` for server faults, with the detail in the body.

### 3. Inconsistent response shapes

**Why it is wrong.** A bare array on one endpoint, `{ "data": [...] }` on another, and
`{ "results": [...] }` on a third forces every client to special-case each call. The
inconsistency becomes a permanent tax on integration.

**The fix.** Pick one envelope and one [error shape](09-error-handling.md) and apply them
everywhere. Consistency is worth more than any per-endpoint optimization.

### 4. No pagination on collections

**Why it is wrong.** `GET /events` returning every row works in development and falls over
in production once the table has millions of rows — slow queries, huge payloads, and
clients that now depend on receiving everything at once.

**The fix.** [Paginate](10-pagination.md) from day one with an enforced maximum page size.
Return page metadata (cursor or total) so clients can iterate.

### 5. Non-idempotent writes

**Why it is wrong.** A network hiccup drops the response to `POST /payments`; the client
retries and charges the card twice. Without idempotency, every retry is a potential
duplicate.

**The fix.** Accept an `Idempotency-Key` on create/payment endpoints and return the
original result on replay. Use `PUT`/`DELETE` where the semantics are naturally idempotent.
See [idempotency](18-idempotency.md).

### 6. Broken object-level authorization (IDOR)

**Why it is wrong.** Checking that a caller is logged in, but not that they own the record,
lets `GET /invoices/1234` return another tenant's invoice by guessing the id. The route is
authenticated; the object is not authorized.

**The fix.** Authorize the specific object on every request — scope the query to the
caller's tenant/owner. See [authorization](16-authorization.md).

### 7. Breaking the contract in place

**Why it is wrong.** Renaming `user_name` to `username` or changing a type on a live
endpoint breaks every deployed client instantly, with no warning and no migration path.

**The fix.** Only add fields to a published version. For breaking changes, ship a new
[version](14-versioning.md) and deprecate the old one with a `Sunset` header and a timeline.

### 8. Leaking internals in responses and errors

**Why it is wrong.** Returning stack traces, SQL, or database column names hands attackers
a map of your system and couples clients to your internal representation.

**The fix.** Map internal errors to a stable client-facing [error](09-error-handling.md)
code and message; log the detail server-side keyed by a `request_id`.

### 9. `GET` requests with side effects

**Why it is wrong.** `GET /orders/5/delete` mutates state, but `GET` is defined as safe —
so crawlers, prefetchers, and caches will "click" it, deleting data no user asked to delete.

**The fix.** Never mutate on `GET` or `HEAD`. Use `DELETE`/`POST`/`PATCH` for any change of
state.

### 10. Chatty endpoints and N+1 queries

**Why it is wrong.** Forcing a client to call `/orders`, then `/orders/{id}` per row, then
`/users/{id}` per order multiplies round trips; the server-side equivalent issues one query
per item and collapses under load.

**The fix.** Return the data a client needs in one well-shaped response, batch-load related
records, and offer field expansion (`?expand=customer`) instead of forcing many calls.

## AI Review Checklist

- Are any URLs carrying verbs instead of using HTTP methods?
- Does any endpoint return `200` for a failure, or an inconsistent response envelope?
- Is any collection endpoint missing enforced pagination?
- Can any write be retried without duplicating its effect?
- Is authorization checked on the object, not just the route?
- Do any responses or errors leak internal details or break a published field?

## Related

- `knowledge/rest-api/02-rest-principles.md`
- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/09-error-handling.md`
- `knowledge/rest-api/16-authorization.md`
- `knowledge/rest-api/18-idempotency.md`
