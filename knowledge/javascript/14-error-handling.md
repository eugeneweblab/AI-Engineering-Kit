---
id: javascript/14-error-handling
topic: javascript
slug: error-handling
title: "JavaScript Error Handling"
type: doc
order: 14
status: ready
tags: [javascript, error-handling, NotFoundError, loadUser, err.message, super, window.onunhandledrejection, this.name]
related: [javascript/09-promises, javascript/08-asynchronous-javascript, javascript/13-fetch-api, javascript/30-engineering-principles, javascript/23-clean-code]
when_to_use: "Read before writing or reviewing any try/catch, Promise rejection handling, or custom error class."
---
# JavaScript Error Handling

## Purpose

This document defines how to signal, propagate, and handle failures in JavaScript —
`throw`, `try/catch`, Promise rejections, and error types — so an agent writes code that
fails loudly at the right layer instead of silently corrupting state. Good error handling
is not about catching everything; it is about deciding, for each failure, whether to
recover, translate, or let it propagate.

## Why It Matters

The default failure mode of bad error handling is **silent data corruption**: an
exception is swallowed by an empty `catch`, execution continues on invalid state, and the
damage surfaces hours later as wrong output or a corrupt record — with no stack trace
pointing back to the cause. Async makes it worse: an unhandled Promise rejection or a
missing `await` drops the error entirely, so the operation "succeeds" while having failed.
Errors are the primary signal that something is wrong; discarding or mangling that signal
is how small bugs become outages.

## Core Principles

- **Throw `Error` objects, never strings or plain objects.** Only `Error` instances carry
  a stack trace and work with `instanceof`. `throw "failed"` loses the origin.
- **Catch only what you can handle.** A `catch` block must recover, translate to a more
  meaningful error, or rethrow. Never leave it empty and never swallow silently.
- **Fail fast on programmer errors; handle operational errors.** Bad arguments and broken
  invariants (bugs) should crash loudly. Expected failures (network, validation, missing
  file) should be handled gracefully.
- **Preserve the cause when translating.** Wrap lower-level errors with
  `new Error(msg, { cause })` so the original stack survives.
- **Async rejects, it does not throw.** An `async` function's failure is a rejected
  Promise. You must `await` it (inside `try/catch`) or attach `.catch`, or it is lost.

## Best Practices

- Define typed error classes (`class ValidationError extends Error`) so callers branch on
  `instanceof`, not on brittle message-string matching. Set `this.name` in the
  constructor.
- Keep `try` blocks narrow — wrap only the statement that can fail — so the `catch` cannot
  accidentally catch and mask unrelated errors.
- In a `catch`, either handle the specific error you expect and rethrow the rest, or wrap
  it with `{ cause }` and throw a domain error. Do not flatten everything to a string.
- Always `await` Promises you depend on inside `try/catch`; a bare `try { doAsync() }`
  catches nothing because the function returned before rejecting.
- Use `finally` for cleanup (close file, release lock) that must run on both success and
  failure paths.
- Install last-resort handlers (`window.onunhandledrejection`, `process.on
  ("unhandledRejection")`) to log and alert — but treat every one that fires as a bug to
  fix, not a normal path.
- Validate inputs at boundaries and throw early; do not let bad data flow deep into the
  system before failing.

## Examples

**Good Example** — typed error, narrow try, preserved cause, real async handling

```js
class NotFoundError extends Error {
  constructor(id) {
    super(`User ${id} not found`);
    this.name = "NotFoundError"; // enables reliable instanceof / name checks
  }
}

async function loadUser(id) {
  let res;
  try {
    res = await fetch(`/users/${id}`); // awaited inside try → rejection is caught here
  } catch (cause) {
    // Translate a low-level network error into a domain error, keeping the original.
    throw new Error(`Failed to load user ${id}`, { cause });
  }
  if (res.status === 404) throw new NotFoundError(id);
  if (!res.ok) throw new Error(`Unexpected ${res.status} loading user ${id}`);
  return res.json();
}
```

**Bad Example** — swallowed error, string throw, unawaited async

```js
async function loadUser(id) {
  try {
    fetch(`/users/${id}`); // NOT awaited → rejection escapes this try entirely
    if (!id) throw "no id"; // string throw → no stack, no instanceof
  } catch (e) {
    // Empty catch: the error vanishes, code continues on undefined data,
    // and the corruption surfaces far away with no trace back to here.
  }
  return; // returns undefined "successfully" on failure
}
```

## Common Mistakes

- Empty `catch {}` blocks or `catch (e) { console.log(e) }` that swallow the failure and
  continue on invalid state.
- Throwing strings/objects instead of `Error`, losing the stack trace.
- Forgetting `await`, so the `try/catch` wraps nothing and the rejection is unhandled.
- Over-broad `try` blocks that catch and hide errors from unrelated statements.
- Branching on `err.message` text (breaks on any wording change) instead of error type.
- Losing the original error when re-throwing, instead of passing `{ cause }`.
- Catching programmer errors (a `TypeError` from a bug) and pretending the operation
  succeeded, masking the defect.

## Production Tips

- Report errors to a monitoring service (Sentry, etc.) with the `cause` chain intact;
  log the error object, not just `err.message`.
- Never leak internal messages or stack traces to end users or API responses — return a
  generic message and a correlation id, log the detail server-side.
- Add `unhandledRejection`/`uncaughtException` handlers that log and then exit the
  process in Node — an unknown-state process should not keep serving.

## AI Review Checklist

- Are all thrown values `Error` instances (or subclasses), never strings?
- Does every `catch` handle, translate, or rethrow — with no silent swallowing?
- Are dependent Promises `await`ed inside `try/catch`, with no missing `await`?
- Are errors distinguished by type/`instanceof`, not by message string matching?
- Is the original error preserved via `{ cause }` when wrapping?
- Are internal error details kept out of user-facing responses?

## Related

- `knowledge/javascript/09-promises.md`
- `knowledge/javascript/08-asynchronous-javascript.md`
- `knowledge/javascript/13-fetch-api.md`
- `knowledge/javascript/30-engineering-principles.md`
- `knowledge/javascript/23-clean-code.md`
