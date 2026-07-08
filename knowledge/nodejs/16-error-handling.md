---
id: nodejs/16-error-handling
topic: nodejs
slug: error-handling
title: "Error Handling"
type: doc
order: 16
status: ready
tags: [nodejs, error-handling]
related: [nodejs/17-logging, nodejs/10-process, nodejs/08-events, nodejs/09-http, nodejs/06-streams]
when_to_use: "Read before writing async error paths, process-level handlers, or deciding what to catch vs. crash on."
---
# Error Handling

## Purpose

This document defines how to handle errors in Node.js: throwing and catching across sync,
callback, Promise, and stream boundaries; the process-level safety nets; and the crucial
distinction between an *operational* error you recover from and a *programmer* error you crash
on. It is written so an agent can build error paths that fail predictably instead of silently.

Error handling and [logging](17-logging.md) are partners but distinct: this doc is about
*control flow* on failure; logging is about *recording* it.

## Why It Matters

Node.js has four different error channels — `throw`, error-first callbacks, rejected Promises,
and `error` events on emitters — and each fails differently if ignored. An unhandled Promise
rejection or an `error` event with no listener can crash the process; a swallowed error leaves
the system in a corrupt state that surfaces much later, somewhere unrelated. Because the
runtime is long-lived and single-process, one mishandled error can take down every in-flight
request. Disciplined error handling is what separates a service that degrades gracefully from
one that dies at 3 a.m. with no useful trace.

## Core Principles

- **Distinguish operational from programmer errors.** Operational errors (network timeout,
  invalid input, 404) are expected — handle and recover. Programmer errors (undefined is not a
  function, failed invariant) are bugs — let the process crash and restart clean; do not `try`
  your way around them.
- **`throw` only `Error` objects.** Throwing strings or plain objects loses the stack trace.
  Extend `Error` for typed, catchable failures.
- **Every Promise must be awaited or `.catch()`-ed.** An unhandled rejection is a crash (Node's
  default since v15). There is no such thing as fire-and-forget for a Promise that can reject.
- **Every stream and emitter needs an `error` listener.** An `error` event with no handler
  throws and can kill the process. See [events](08-events.md) and [streams](06-streams.md).
- **Fail fast and loud, not slow and silent.** Never swallow an error with an empty `catch`.
  If you cannot handle it, rethrow or propagate.
- **The last resort crashes deliberately.** `uncaughtException`/`unhandledRejection` handlers
  log and exit — they do not resume; the process is now in an unknown state.

## Best Practices

- Wrap `async` route handlers so rejected Promises reach your framework's error middleware
  (Express 5 and Fastify do this natively; Express 4 needs a wrapper).
- Define an **error taxonomy**: a base `AppError` with subclasses (`ValidationError`,
  `NotFoundError`, `ExternalServiceError`) carrying a stable `code` and an HTTP status. Map
  them centrally to responses so handlers stay clean.
- Attach a **single `unhandledRejection` and `uncaughtException` handler** that logs with full
  context, then exits non-zero so the supervisor restarts the process. Do not keep serving.
- Never expose internal error details (stack traces, SQL) to clients; return a generic message
  plus a correlation id, and log the detail server-side.
- Use `AbortController`/timeouts on external calls so a hung dependency surfaces as a
  handleable error instead of an indefinitely pending Promise.
- Preserve the cause chain with `new Error("...", { cause: err })` so you keep the original
  stack while adding context.

## Examples

**Good Example** — typed error, propagated, mapped centrally

```js
class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = "ValidationError";
    this.status = 400; // operational: expected, maps to a 4xx
  }
}

async function createUser(input) {
  if (!input.email) throw new ValidationError("email is required"); // propagate, don't swallow
  return db.users.insert(input); // a DB failure rejects and bubbles to the handler
}

// One place converts errors to responses; leaks nothing internal to the client.
app.use((err, req, res, next) => {
  logger.error({ err, reqId: req.id }); // full detail server-side
  res.status(err.status ?? 500).json({ error: err.message, reqId: req.id });
});

process.on("unhandledRejection", (err) => {
  logger.fatal({ err }); // last resort: log and exit; supervisor restarts clean
  process.exit(1);
});
```

**Bad Example** — swallowed errors, string throws, silent corruption

```js
async function createUser(input) {
  try {
    return await db.users.insert(input);
  } catch (e) {
    console.log("insert failed"); // stack trace and error type lost
    return null;                   // caller can't tell success from failure
  }
}

function validate(input) {
  if (!input.email) throw "email required"; // string throw: no stack, hard to catch by type
}

someAsyncTask(); // floating Promise: a rejection here is now an unhandled crash
// No process-level handlers: an unexpected rejection kills the server with no context.
```

## Common Mistakes

- Empty or log-only `catch` blocks that swallow errors and return corrupt state.
- Throwing strings or objects instead of `Error`, discarding the stack trace.
- Floating Promises (`doThing()` without `await`/`.catch`) causing unhandled rejections.
- Missing `error` listeners on streams and emitters, crashing the process.
- Trying to `catch` programmer errors and continue, hiding real bugs.
- Leaking stack traces or SQL to API clients.
- `uncaughtException` handlers that log and keep running, serving from a corrupt process.

## Production Tips

- Route all errors through structured [logging](17-logging.md) with a correlation/request id so
  a client-facing error id maps to the full server-side trace.
- Let a supervisor ([cluster](13-cluster.md), Kubernetes, PM2) restart on crash; a fast clean
  restart beats a limping process.
- Alert on `unhandledRejection`/`uncaughtException` rates and on error-code spikes in
  [monitoring](27-monitoring.md) — they signal new bugs before users report them.

## AI Review Checklist

- Are operational errors handled and programmer errors allowed to crash-and-restart?
- Are only `Error` (or subclasses) thrown, preserving stack traces?
- Is every Promise awaited or `.catch`-ed, with no floating rejections?
- Does every stream/emitter have an `error` listener?
- Are `unhandledRejection` and `uncaughtException` handlers present, logging then exiting?
- Are internal error details logged server-side but never returned to clients?

## Related

- `knowledge/nodejs/17-logging.md`
- `knowledge/nodejs/10-process.md`
- `knowledge/nodejs/08-events.md`
- `knowledge/nodejs/09-http.md`
- `knowledge/nodejs/06-streams.md`
