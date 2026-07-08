---
id: backend/12-error-handling
topic: backend
slug: error-handling
title: "Error Handling"
type: doc
order: 12
status: ready
tags: [backend, error-handling]
related: [backend/09-validation, backend/17-transactions, backend/22-observability, backend/19-performance, backend/100-common-antipatterns]
when_to_use: "Read before writing or reviewing any code that can fail — I/O, external calls, parsing, or business rules."
---
# Error Handling

## Purpose

This document defines how backend code should detect, propagate, and respond to
failures. It covers error taxonomy, propagation across layers, mapping errors to
transport responses (HTTP status, gRPC code), retries, and logging. The goal is
that an agent can write a handler or service method that fails *predictably* — the
caller always learns what went wrong and the system never ends up in a half-updated
state.

Error handling is not an afterthought bolted on at the controller. It is a design
concern that runs through every layer, and getting it wrong silently corrupts data
or hangs requests.

## Why It Matters

Most production incidents are not caused by the happy path breaking; they are caused
by the failure path being wrong. A swallowed exception hides a bug for weeks. A leaked
stack trace hands an attacker your file paths and library versions. A missing rollback
leaves an order paid-for but never shipped. Errors are where correctness, security, and
data integrity all intersect, so the failure path deserves the same rigor as the
feature itself. Assume every external call, every parse, and every write can fail.

## Core Principles

- **Fail fast, fail loud, recover deliberately.** Detect a bad state at the earliest
  point and stop; do not let a corrupt value flow deeper where the cause is unrecoverable.
- **Distinguish expected from unexpected errors.** Expected failures (validation,
  not-found, conflict) are part of the domain and map to 4xx. Unexpected failures (bugs,
  downstream outages) are 5xx and must be alerted on. Treating them alike hides bugs.
- **Never swallow an error.** Catching an exception only to log-and-continue, or to
  `catch {}` silently, converts a loud failure into silent data loss.
- **Preserve context as errors propagate.** Wrap a low-level error with domain meaning,
  but keep the original `cause` so the root is not lost.
- **Errors are a public contract.** The shape a client receives (code, message, fields)
  is an API surface. Keep it stable, typed, and free of internal detail.
- **Clean up on failure.** Any resource acquired (transaction, lock, file handle,
  connection) must be released on every path, including the throwing one.

## Best Practices

- Model domain failures as **typed error classes** (`NotFoundError`, `ConflictError`,
  `ValidationError`) rather than throwing raw strings or generic `Error`. Types let a
  central handler map each to the right status without string-matching messages.
- Map errors to transport at **one boundary** (an exception filter / middleware), not
  in every handler. This keeps status logic consistent and controllers thin.
- Return a **stable machine-readable error body**: a `code` field clients can branch on,
  a human `message`, and optional `details`. Do not make clients parse prose.
- **Never leak internals** to the client — no stack traces, SQL, or file paths in the
  response. Log the detail server-side, return a correlation id to the client.
- Retry only **idempotent** operations, and only on **transient** errors (timeouts, 503,
  deadlocks). Use exponential backoff with jitter and a hard cap. Retrying a
  non-idempotent write duplicates side effects.
- Attach a **correlation / request id** to every log line so one failure can be traced
  across services. See [observability](22-observability.md).
- Validate input at the edge so business logic can assume well-formed data; see
  [validation](09-validation.md).

## Examples

**Good Example** — typed error, preserved cause, central mapping

```ts
// Domain layer: throw meaning, not a status code. Keep the original cause.
class PaymentDeclinedError extends Error {
  readonly code = "PAYMENT_DECLINED";
  constructor(public readonly reason: string, cause?: unknown) {
    super(`Payment declined: ${reason}`);
    this.cause = cause; // root error is preserved for logs, hidden from client
  }
}

async function charge(order: Order): Promise<void> {
  try {
    await gateway.charge(order.total, order.token);
  } catch (err) {
    // Wrap the transport error in a domain error; do not swallow it.
    throw new PaymentDeclinedError(gateway.reasonFrom(err), err);
  }
}

// One boundary maps domain errors -> HTTP. Controllers stay clean.
function toHttp(err: unknown) {
  if (err instanceof PaymentDeclinedError) return { status: 402, body: { code: err.code, message: err.message } };
  if (err instanceof NotFoundError)        return { status: 404, body: { code: "NOT_FOUND", message: err.message } };
  logger.error({ err, cause: (err as Error).cause }); // full detail server-side only
  return { status: 500, body: { code: "INTERNAL", message: "Unexpected error", requestId } };
}
```

**Bad Example** — swallowed error, leaked internals, no cleanup

```ts
async function charge(order: Order) {
  const tx = await db.begin();
  try {
    await gateway.charge(order.total, order.token);
    await tx.commit();
  } catch (err) {
    // Swallows the failure: caller thinks it succeeded, money never moved.
    console.log("charge failed", err);
    // tx is never rolled back -> connection leaks, row stays locked.
    return { ok: true }; // lies to the caller
  }
}

// Elsewhere: sends the raw error to the client, leaking stack + DB schema.
res.status(500).send(err.stack);
```

## Common Mistakes

- `catch (e) {}` or catch-log-continue — turning a failure into silent data loss.
- Using HTTP status codes as the *only* error type, so non-HTTP callers can't branch.
- Returning `{ ok: true }` (or a default value) from a failed operation.
- Leaking stack traces, SQL, or exception messages straight to the client.
- Retrying a non-idempotent write, producing duplicate charges or emails.
- Catching `Error` broadly and mapping everything to 400, hiding real 500 bugs.
- Losing the original `cause` when wrapping, making the root failure untraceable.
- Not releasing transactions/locks on the throwing path.

## Production Tips

- Return a **correlation id** in every 5xx body and log it alongside the full error, so
  support can find the exact failure from a user's screenshot.
- Alert on **unexpected (5xx) rate**, not on 4xx — 4xx is normal client behavior.
- Keep a small **error-code catalog** in your API docs; clients depend on those codes.
- Add a **default/catch-all handler** so an unmapped exception still returns a clean 500,
  never a raw crash or an empty response.

## AI Review Checklist

- Are domain failures modeled as typed errors, not raw strings or bare `Error`?
- Is error-to-status mapping done at one boundary rather than scattered in handlers?
- Is every `catch` either recovering meaningfully or rethrowing — never swallowing?
- Are stack traces and internals kept out of client responses?
- Are retries limited to idempotent operations on transient errors, with backoff?
- Are transactions, locks, and handles released on the failure path?
- Is the original `cause` preserved when errors are wrapped?

## Related

- `knowledge/backend/09-validation.md`
- `knowledge/backend/17-transactions.md`
- `knowledge/backend/22-observability.md`
- `knowledge/backend/19-performance.md`
- `knowledge/backend/100-common-antipatterns.md`
