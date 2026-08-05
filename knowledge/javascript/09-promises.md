---
id: javascript/09-promises
topic: javascript
slug: promises
title: "Promises"
type: doc
order: 9
status: ready
tags: [javascript, promises, allSettled, fetchUser, resolve, reject, fetchOrders, readFile]
related: [javascript/08-asynchronous-javascript, javascript/10-event-loop, javascript/14-error-handling, javascript/13-fetch-api]
when_to_use: "Read before creating a Promise, chaining `.then`, or using `Promise.all/race/allSettled/any`."
---
# Promises

## Purpose

This document defines how to create, chain, combine, and settle promises correctly:
the state machine, error propagation, the combinators (`all`, `allSettled`, `race`,
`any`), and the anti-patterns that break chains or hide rejections. It underpins
[async/await](08-asynchronous-javascript.md), which is sugar over these mechanics, and
is written so an agent can reason about promise code even when it is not using `await`.

A promise is a placeholder for a value that will exist later. It is in exactly one
of three states — *pending*, *fulfilled*, or *rejected* — and once settled it never
changes. Almost every promise bug is a violation of that model or a broken chain.

## Why It Matters

Promises are the substrate of all modern async JavaScript. A dropped `return` inside
a `.then` silently breaks the chain so the next handler runs before the work
finishes. A missing `.catch` turns a rejection into an unhandled rejection that
crashes Node or vanishes in the browser. Choosing `Promise.all` where
`allSettled` was needed makes one failure abort every sibling. Because promises
compose, a subtle mistake in one link corrupts the whole chain's timing and error
handling.

## Core Principles

- **A promise settles once.** After fulfill or reject, its state and value are frozen.
  Resolving twice is a no-op, not an error — do not rely on it as a signal.
- **`.then` returns a new promise.** Chaining depends on *returning* the inner value
  or promise from each handler; forgetting to return breaks sequencing.
- **Rejections propagate down the chain** until a `.catch` (or the second `.then`
  argument) handles them. An unterminated chain leaks the rejection.
- **Handlers always run asynchronously**, as microtasks, even if the promise is
  already settled. Code after `.then(...)` runs before the handler.
- **A thrown error inside a handler becomes a rejection** of the returned promise —
  `throw` and `reject` are equivalent inside the chain.

## Best Practices

- Always terminate a chain with `.catch` (or `await` inside `try/catch`). An
  unhandled rejection is a defect, not a warning.
- Choose the right combinator: `Promise.all` (all must succeed, fail-fast),
  `Promise.allSettled` (want every outcome), `Promise.race` (first to settle, incl.
  rejection), `Promise.any` (first *fulfillment*, ignores rejections until all fail).
- Avoid the `new Promise(...)` constructor for anything already promise-returning;
  wrapping an existing promise in `new Promise` is the "explicit construction
  antipattern" and drops errors. Reserve the constructor for adapting callback APIs.
- Return values from `.then` handlers so the next link waits on them; never fire an
  inner async call without returning it.
- Do not `.catch` and then continue as if nothing failed unless you have a real
  fallback. Swallowing errors hides outages.
- Prefer `async`/`await` for sequential logic; reserve raw chains for simple
  transforms and combinator composition.

## Examples

**Good Example** — proper chaining, correct combinator, terminal catch

```js
// Adapt a callback API to a promise — a legitimate use of the constructor.
function readFile(path) {
  return new Promise((resolve, reject) => {
    fs.readFile(path, "utf8", (err, data) =>
      err ? reject(err) : resolve(data));   // reject on error, resolve on success
  });
}

// allSettled: collect every result even if some fail; one failure must not abort the batch.
async function importAll(paths) {
  const results = await Promise.allSettled(paths.map(readFile));
  return results
    .filter((r) => r.status === "fulfilled")
    .map((r) => r.value);
}

fetchUser(id)
  .then((user) => fetchOrders(user.id))     // RETURN the inner promise → chain waits
  .then((orders) => render(orders))
  .catch((err) => reportError(err));        // terminal catch handles any rejection
```

**Bad Example** — broken chain, explicit-construction antipattern, no catch

```js
function fetchUser(id) {
  // Wrapping an existing promise in new Promise: errors from the inner call are lost.
  return new Promise((resolve) => {
    api.get(`/users/${id}`).then((res) => resolve(res.data));
    // no reject handler → a failed request hangs this promise forever
  });
}

fetchUser(1).then((user) => {
  fetchOrders(user.id).then(render);  // inner promise not returned → chain does not wait,
                                      // and no .catch anywhere → rejection is unhandled
});
```

## Common Mistakes

- Forgetting to `return` the inner promise in a `.then`, so the chain does not wait.
- No terminal `.catch`, leaking unhandled rejections.
- The explicit-construction antipattern: `new Promise` around code that already
  returns a promise, dropping its errors.
- Using `Promise.all` when a single failure should not abort the rest (`allSettled`).
- Assuming `.then` runs synchronously — it is always a microtask.
- Calling `resolve`/`reject` twice and expecting the second to matter.
- Mixing `await` with un-awaited `.then` branches, creating race conditions.

## Production Tips

- Treat unhandled rejections as fatal in Node: log and exit, so a leaked rejection
  cannot leave the process in a corrupt state.
- When racing for a timeout, remember `Promise.race` does not cancel the loser —
  pair it with `AbortController` to actually stop the slow work.
- `Promise.any` is right for "first healthy replica wins"; its rejection is an
  `AggregateError` — inspect `.errors`.

## AI Review Checklist

- Does every `.then` that starts async work `return` the resulting promise?
- Is every chain terminated with `.catch` or awaited inside `try/catch`?
- Is the combinator correct for the intent (`all` vs `allSettled` vs `race` vs `any`)?
- Is `new Promise` used only to wrap non-promise (callback) APIs, with both resolve and reject?
- Are rejections propagated or genuinely recovered — never silently swallowed?
- Does any code assume `.then` handlers run synchronously?

## Related

- `knowledge/javascript/08-asynchronous-javascript.md`
- `knowledge/javascript/10-event-loop.md`
- `knowledge/javascript/14-error-handling.md`
- `knowledge/javascript/13-fetch-api.md`
