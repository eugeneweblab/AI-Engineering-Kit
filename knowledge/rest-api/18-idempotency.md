---
id: rest-api/18-idempotency
topic: rest-api
slug: idempotency
title: "Idempotency"
type: doc
order: 18
status: ready
tags: [rest-api, idempotency]
related: [rest-api/06-request-response, rest-api/07-status-codes, rest-api/09-error-handling, rest-api/17-rate-limiting, rest-api/25-performance]
when_to_use: "Read before building any write endpoint that a client may retry — payments, orders, sign-ups, or anything triggered over a flaky network."
---
# Idempotency

## Purpose

This document defines how to make write operations safe to retry. An operation is
*idempotent* when calling it once and calling it many times with the same input
produce the same result and the same side effects. This guide covers which HTTP
methods are idempotent by spec, and how to add idempotency to methods that are not —
chiefly `POST` — using an idempotency key.

Idempotency answers "what happens if the client sends this request twice?". On the
public internet the answer is not hypothetical: retries happen constantly.

## Why It Matters

Networks fail after the server has already acted. A client sends `POST /charges`,
the charge succeeds, and the response is lost to a dropped connection. The client,
seeing no reply, retries — and without idempotency the customer is charged twice.
Load balancers, mobile clients, and background job queues all retry automatically.
Duplicate orders, double emails, and double payments are not edge cases; they are the
default behavior of a distributed system unless you design them out. The cost of
getting this wrong is measured in refunds, support tickets, and lost trust.

## Core Principles

- **`GET`, `PUT`, and `DELETE` are idempotent by contract; `POST` and `PATCH` are
  not.** `GET` has no side effects. `PUT` replaces a resource with an absolute state.
  `DELETE` leaves the resource gone whether called once or ten times. Honor these
  guarantees — clients and proxies rely on them to retry safely.
- **Idempotency is about final state, not response bytes.** A repeated `DELETE`
  may return `404` the second time; that is fine. What must not change is the
  server-side effect: the resource is gone either way.
- **Make unsafe operations idempotent with a client-supplied key.** For `POST`,
  require an `Idempotency-Key` header. The first request does the work; identical
  retries return the stored original response without repeating the side effect.
- **Bind the key to the request, not just the endpoint.** Store the key with a hash
  of the request body so a reused key with a *different* payload is rejected, not
  silently served the wrong cached result.
- **Persist the result atomically with the side effect.** The record "this key was
  processed, here is the response" must be committed in the same transaction as the
  charge or order — otherwise a crash between them reopens the double-execution window.

## Best Practices

- Accept an `Idempotency-Key` header (a client-generated UUID) on every non-idempotent
  write. Reject requests missing it with `400` on endpoints where duplicates are costly.
- Return `409 Conflict` when the same key arrives with a different request body — the
  client is reusing a key incorrectly, and silently succeeding would hide a bug.
- Return the *original* status code and body on a replay, plus a header such as
  `Idempotent-Replay: true` so the client can tell a retry was deduplicated.
- Give idempotency records a TTL (24 hours is common). Retries happen within minutes;
  a bounded window keeps the store small and lets keys be reused later legitimately.
- Handle the in-flight case: if a second request arrives while the first is still
  processing, return `409` (or block briefly) rather than starting the work twice.
- Design new writes as `PUT` to a client-chosen ID where feasible — it is idempotent
  for free, no key infrastructure required.

## Examples

**Good Example** — idempotent `POST` keyed on a client UUID

```ts
// POST /charges  with header: Idempotency-Key: 4f1a...
async function createCharge(req: Request) {
  const key = req.header("Idempotency-Key");
  if (!key) throw new HttpError(400, "Idempotency-Key header required");

  const bodyHash = sha256(canonicalize(req.body));
  const existing = await idempotency.get(key);

  if (existing) {
    // Same key, different payload → the client is misusing the key. Fail loudly.
    if (existing.bodyHash !== bodyHash) throw new HttpError(409, "Key reused with different body");
    return existing.response; // replay the ORIGINAL result; no second charge
  }

  // Reserve the key and perform the charge in ONE transaction so a crash cannot
  // leave a charge without its idempotency record (which would allow a re-charge).
  return db.transaction(async (tx) => {
    const charge = await gateway.charge(req.body, tx);
    const response = { status: 201, body: charge };
    await idempotency.put(tx, { key, bodyHash, response, ttl: "24h" });
    return response;
  });
}
```

**Bad Example** — `POST` with no dedupe; retries double-charge

```ts
async function createCharge(req: Request) {
  // No key, no dedupe. A dropped response makes the client retry, and this
  // runs a SECOND real charge. The database and the customer both diverge.
  const charge = await gateway.charge(req.body);
  return { status: 201, body: charge };
}
```

## Common Mistakes

- Treating `POST` as if retries were impossible — they are the norm, not the exception.
- Caching the response by key but running the side effect *before* checking the key,
  so a concurrent retry still executes twice.
- Storing the idempotency record in a separate transaction from the side effect,
  leaving a crash window that permits re-execution.
- Ignoring the request body, so a reused key with new data returns a stale response.
- Making `DELETE` non-idempotent by throwing `500` (instead of `404`/`204`) on a
  second call, which breaks safe client retries.
- Keeping idempotency keys forever, letting the store grow without bound.

## Production Tips

- Store keys in a fast, durable store (Postgres with a unique constraint, or Redis
  with persistence). The unique constraint on the key column is your last line of
  defense against a race.
- Emit a metric for replayed requests; a sudden spike often signals client retry
  storms or an upstream timeout that needs tuning.
- Document the required header and TTL in your [OpenAPI](21-openapi.md) spec so
  clients implement retries correctly.

## AI Review Checklist

- Are `GET`, `PUT`, and `DELETE` handlers free of non-idempotent side effects?
- Does every costly `POST`/`PATCH` accept and enforce an `Idempotency-Key`?
- Is the key stored with a hash of the request body and checked on replay?
- Is the idempotency record committed atomically with the side effect?
- Does a reused key with a different body return `409`, not a stale result?
- Do idempotency records have a bounded TTL?

## Related

- `knowledge/rest-api/06-request-response.md`
- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/09-error-handling.md`
- `knowledge/rest-api/17-rate-limiting.md`
- `knowledge/rest-api/25-performance.md`
