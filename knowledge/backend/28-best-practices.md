---
id: backend/28-best-practices
topic: backend
slug: best-practices
title: "Best Practices"
type: doc
order: 28
status: ready
tags: [backend, best-practices]
related: [backend/09-validation, backend/12-error-handling, backend/17-transactions, backend/23-testing, backend/100-common-antipatterns]
when_to_use: "Read before writing or reviewing any backend endpoint, service, or data-access code."
---
# Best Practices

## Purpose

This document collects the cross-cutting habits that separate durable backend code from
code that merely passes the demo. It is a synthesis, not a new topic: the deeper rules live
in [validation](09-validation.md), [error handling](12-error-handling.md),
[transactions](17-transactions.md), and [testing](23-testing.md). Read this when you want a
single checklist of the defaults every endpoint and service should follow, and pointers to
where each rule is argued in full.

## Why It Matters

Most backend defects are not exotic; they are the same handful of omissions repeated:
untrusted input trusted, errors swallowed, a write that is not atomic, a query without a
limit, a secret in a log. Each is individually small and individually invisible in a happy-path
test. Together they are the majority of production incidents. Internalizing a short list of
non-negotiable defaults prevents the boring 80% of failures, so attention is left for the
genuinely hard problems.

## Core Principles

- **Trust nothing from outside the process.** Validate and normalize every input at the
  boundary; the type system does not stop a hostile client.
- **Make operations atomic and idempotent.** A request either fully happens or fully does not,
  and repeating it is safe. Networks retry; design for it.
- **Fail loudly and specifically.** Return the right status, log the cause with context, and
  never swallow an exception into silence.
- **Separate policy from mechanism.** Business rules live in the domain, not in the controller
  or the SQL. Framework code should be thin and replaceable.
- **Assume everything you write will be read under pressure.** Optimize code, logs, and errors
  for the person debugging them at 3 a.m., not for cleverness.

## Best Practices

- **Validate at the edge**, return `422`/`400` with field-level detail, and pass only typed,
  trusted data inward. (See [validation](09-validation.md).)
- **Wrap multi-step writes in a transaction**; never leave the database in a half-updated state
  on partial failure. (See [transactions](17-transactions.md).)
- **Paginate and bound every list query.** An unbounded `SELECT` is a latent outage the day the
  table grows.
- **Use structured logging with correlation IDs**; never log secrets, tokens, PII, or full
  request bodies. (See [observability](22-observability.md).)
- **Return correct status codes and a stable error shape**; distinguish client errors (`4xx`)
  from server errors (`5xx`). (See [error handling](12-error-handling.md).)
- **Make handlers thin**: parse/validate, call a domain service, map the result. Business logic
  does not belong in the controller.
- **Push work off the request path.** Anything slow or retryable (email, webhooks, exports) goes
  to a background job, not into the user's request.
- **Write tests for the failure paths**, not just the happy path — that is where the bugs are.

## Examples

**Good Example** — thin handler, validated input, atomic write, bounded query

```python
@router.post("/orders")
async def create_order(payload: CreateOrderIn):   # schema validates at the edge
    async with db.transaction():                  # all-or-nothing write
        order = await orders.place(payload.to_command())  # logic lives in the domain
    return OrderOut.from_domain(order), 201        # correct status, stable shape

@router.get("/orders")
async def list_orders(cursor: str | None = None, limit: int = Query(50, le=200)):
    # bounded page size (le=200) — the query can never scan the whole table
    return await orders.page(cursor, limit)
```

**Bad Example** — fat handler, unvalidated input, no transaction, unbounded query

```python
@router.post("/orders")
async def create_order(request):
    body = await request.json()                    # no validation; trusts the client
    order = await db.insert("orders", body)        # arbitrary fields straight to the DB
    await db.insert("line_items", body["items"])   # separate write; crash here = orphan order
    await email.send(body["email"], "thanks")      # slow I/O on the request path; blocks + can't retry
    return {"ok": True}                            # 200 for a create, no id, no error shape

@router.get("/orders")
async def list_orders():
    return await db.query("SELECT * FROM orders")  # unbounded — falls over as the table grows
```

## Common Mistakes

- Trusting request data because it is typed, skipping real validation at the boundary.
- Multi-step writes without a transaction, leaving orphaned or half-written records.
- List endpoints with no pagination or max limit.
- Catching exceptions and returning `200`, hiding failures from callers and monitoring.
- Business logic embedded in controllers or SQL, making it untestable and unreusable.
- Doing slow, retryable work (email, third-party calls) synchronously inside the request.
- Logging secrets, tokens, or full payloads.

## AI Review Checklist

- Is all external input validated and normalized at the boundary?
- Are multi-step writes wrapped in a transaction and safe to retry (idempotent)?
- Do all list queries have pagination and a hard maximum page size?
- Are status codes correct and error responses a consistent, documented shape?
- Are handlers thin, with business logic in a domain/service layer?
- Is slow or retryable work moved to background jobs off the request path?
- Do logs exclude secrets and PII, and include a correlation ID?

## Related

- `knowledge/backend/09-validation.md`
- `knowledge/backend/12-error-handling.md`
- `knowledge/backend/17-transactions.md`
- `knowledge/backend/23-testing.md`
- `knowledge/backend/100-common-antipatterns.md`
