---
id: javascript/08-asynchronous-javascript
topic: javascript
slug: asynchronous-javascript
title: "Asynchronous JavaScript"
type: doc
order: 8
status: ready
tags: [javascript, asynchronous-javascript, fetchJson, loadDashboard, Promise.all, AbortController, AbortSignal, Promise.allSettled, await, callback, concurrent]
related: [javascript/09-promises, javascript/10-event-loop, javascript/13-fetch-api, javascript/14-error-handling]
when_to_use: "Read before writing or reviewing any `async`/`await`, callback, or concurrent I/O code."
---
# Asynchronous JavaScript

## Purpose

This document defines how to write correct asynchronous JavaScript with
`async`/`await`: sequencing vs concurrency, error propagation, cancellation, and the
common traps that turn parallel work into slow serial work or swallow errors. It
builds on [promises](09-promises.md) and the [event loop](10-event-loop.md), and is
written so an agent can implement async flows that are both fast and safe.

`async`/`await` is the standard way to consume promises in 2026. It reads like
synchronous code but does not behave like it — the function suspends and yields the
thread at every `await`. That gap is where most async bugs live.

## Why It Matters

JavaScript is single-threaded. Async is how one thread stays responsive while I/O
happens, but it also means execution can interleave in ways synchronous code never
does: state you read before an `await` may be stale after it. Get concurrency wrong
and you either serialize independent requests (slow) or fire unbounded parallel work
(resource exhaustion). Get error handling wrong and a rejected promise becomes an
unhandled rejection that crashes Node or silently drops in the browser. These
failures are timing-dependent and rarely reproduce in a debugger.

## Core Principles

- **`await` suspends; it does not block.** Other tasks run during the wait. Never
  assume state is unchanged across an `await`.
- **Independent work should run concurrently.** Sequential `await`s that do not
  depend on each other waste wall-clock time. Use `Promise.all` for fan-out.
- **Every async operation can reject.** An unhandled rejection is a bug, not a
  warning. Handle or propagate — never ignore.
- **`async` functions always return a promise.** Returning a value resolves it;
  throwing rejects it. A caller who forgets `await` gets a promise, not the value.
- **Cancellation is explicit.** Use `AbortController`/`AbortSignal`; there is no
  implicit way to stop in-flight work.

## Best Practices

- Run independent operations with `Promise.all` (fail-fast) or `Promise.allSettled`
  (collect all outcomes). Sequential `await` only when B genuinely needs A's result.
- Bound concurrency for large fan-outs (e.g. a pool or `p-limit`) so you do not open
  10,000 sockets at once. The cost of unbounded parallelism is resource exhaustion.
- Wrap `await`ed calls that can fail in `try/catch`, or let the rejection propagate to
  a caller that does. Do not leave a floating promise unattended.
- Pass an `AbortSignal` to cancellable operations (`fetch`, timers, DB drivers) and
  abort on timeout or user navigation to avoid leaking work.
- Never mark a function `async` if it does no `await` — it needlessly wraps the return
  in a promise and hides that it is synchronous.
- Do not mix `.then()` chains and `await` in the same function; pick one for readability.

## Examples

**Good Example** — concurrent fan-out, timeout, real error handling

```js
async function loadDashboard(userId, { signal } = {}) {
  // These three requests are independent — run them concurrently, not in series.
  const [profile, orders, notifications] = await Promise.all([
    fetchJson(`/users/${userId}`, { signal }),
    fetchJson(`/users/${userId}/orders`, { signal }),
    fetchJson(`/users/${userId}/notifications`, { signal }),
  ]);
  return { profile, orders, notifications };
}

async function withTimeout(promiseFactory, ms) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), ms); // cancel if too slow
  try {
    return await promiseFactory(ctrl.signal);
  } finally {
    clearTimeout(timer);                            // always clean up the timer
  }
}
```

**Bad Example** — accidental serialization and a swallowed rejection

```js
async function loadDashboard(userId) {
  // Each await blocks the next: 3x the latency for independent requests.
  const profile = await fetchJson(`/users/${userId}`);
  const orders = await fetchJson(`/users/${userId}/orders`);
  const notifications = await fetchJson(`/users/${userId}/notifications`);

  saveAnalytics(userId);   // floating promise: if it rejects, it is unhandled
  return { profile, orders, notifications };
}
```

## Common Mistakes

- Awaiting independent calls in sequence, tripling latency for no reason.
- Floating promises (`doThing()` without `await` or `.catch`) that reject unhandled.
- `forEach(async ...)` — the callback's promise is dropped; the loop does not wait.
  Use `for...of` with `await`, or `Promise.all(map(...))`.
- Assuming state read before an `await` is still valid after it.
- Unbounded `Promise.all` over a huge array, exhausting sockets/memory.
- `async` functions with no `await`, hiding that the work is synchronous.
- No timeout or cancellation, so a hung request hangs the whole flow.

## Production Tips

- Enable a lint rule for floating promises (`no-floating-promises`) and unhandled
  rejections; wire `process.on("unhandledRejection")` in Node to fail loudly, not silently.
- Use `Promise.allSettled` for batch jobs where one failure must not abort the rest,
  then inspect each result's `status`.
- Give every outbound call a timeout; a dependency that never responds should not be
  able to hang your request indefinitely.

## AI Review Checklist

- Are independent async operations run concurrently (`Promise.all`) rather than serially?
- Is every promise either `await`ed, returned, or `.catch`ed — no floating rejections?
- Are large fan-outs bounded so they cannot exhaust sockets or memory?
- Do cancellable operations accept and honor an `AbortSignal`, with timeouts set?
- Are there `forEach(async ...)` loops that silently fail to await?
- Is state re-validated after an `await` if it could have changed?
- Are `async` functions that never `await` demoted to synchronous?

## Related

- `knowledge/javascript/09-promises.md`
- `knowledge/javascript/10-event-loop.md`
- `knowledge/javascript/13-fetch-api.md`
- `knowledge/javascript/14-error-handling.md`
