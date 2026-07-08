---
id: typescript/18-asynchronous-programming
topic: typescript
slug: asynchronous-programming
title: "Asynchronous Programming"
type: doc
order: 18
status: ready
tags: [typescript, asynchronous-programming]
related: [typescript/17-error-handling, typescript/04-functions, typescript/08-generics, typescript/25-performance, typescript/28-best-practices]
when_to_use: "Read before writing or reviewing any code that uses Promises, async/await, timers, streams, or concurrent I/O."
---
# Asynchronous Programming

## Purpose

This document defines how to write correct asynchronous TypeScript: `Promise`,
`async`/`await`, concurrency, cancellation, and error propagation. It is written so an
agent can build or review an async flow without leaking rejections, serializing work
that should run in parallel, or losing errors across `await` boundaries.

JavaScript is single-threaded with an event loop. "Async" does not mean parallel
threads — it means work that yields control while waiting on I/O. Getting the types and
the ordering right is what separates a responsive service from one that deadlocks its
own connection pool.

## Why It Matters

Async bugs are the ones that pass every local test and then fall over in production.
An unhandled rejection crashes the Node process; a forgotten `await` returns a `Promise`
where a value was expected and corrupts state silently; a loop that awaits inside each
iteration turns a 200ms job into a 20s one under load. The type system catches some of
this, but only if you keep return types honest and never widen to `any`. Treat every
`await` as a point where the world may have changed and an error may arrive.

## Core Principles

- **Always `return` or `await` a Promise.** A Promise you neither return nor await is a
  floating promise: its rejection is invisible and its completion is unordered.
- **Type async functions as `Promise<T>`, never `any`.** The return type is the contract
  callers depend on to know they must await.
- **Parallelize independent work; serialize only true dependencies.** `await` in a loop
  over independent items is the most common performance defect in async code.
- **Errors cross `await` like `throw` crosses a call.** A rejected Promise you await
  throws at that point — wrap it or let it propagate, never swallow it silently.
- **Make cancellation explicit.** Long-running or user-triggered work must accept an
  `AbortSignal` so it can be stopped; unbounded async work is a resource leak.

## Best Practices

- Use `async`/`await` over raw `.then()` chains — it makes control flow and error scope
  read like synchronous code and prevents nested-callback mistakes.
- Run independent operations with `Promise.all` (fail-fast) or `Promise.allSettled`
  (collect every outcome). Reach for `all` when one failure should abort the batch.
- Never mix `await` inside a `.forEach` — `forEach` ignores the returned Promise, so the
  work runs unawaited. Use a `for...of` loop or `map` + `Promise.all`.
- Bound concurrency for large batches (e.g. a pool of N) so you do not open ten thousand
  sockets at once; unbounded `Promise.all` over a big array exhausts the pool.
- Attach a `.catch` or `try/catch` to every entry point. In Node, register a
  `process.on("unhandledRejection")` handler that logs and exits — do not let it slide.
- Pass `AbortSignal` through I/O calls (`fetch`, DB drivers that support it) and check
  `signal.aborted` in long loops.
- Avoid `async` constructors and `async` executor functions passed to `new Promise` —
  a throw inside the executor is lost. Prefer static async factory methods.

## Examples

**Good Example** — parallel independent work, typed, errors propagate

```ts
async function loadDashboard(userId: string, signal: AbortSignal): Promise<Dashboard> {
  // These three calls do not depend on each other, so run them concurrently.
  // If any rejects, Promise.all rejects immediately and the await below throws.
  const [profile, invoices, notes] = await Promise.all([
    fetchProfile(userId, signal),
    fetchInvoices(userId, signal), // signal lets a navigated-away user cancel the work
    fetchNotes(userId, signal),
  ]);
  return { profile, invoices, notes }; // return type is Promise<Dashboard>, so callers must await
}
```

**Bad Example** — serialized, floating promise, swallowed error

```ts
async function loadDashboard(userId: string) {
  const profile = await fetchProfile(userId);
  const invoices = await fetchInvoices(userId); // waits on profile for no reason
  const notes = await fetchNotes(userId);       // three round-trips run back-to-back

  logAccess(userId); // floating promise: not awaited, its rejection is lost forever

  try {
    return { profile, invoices, notes };
  } catch {
    return null; // this catch guards nothing — the awaits above already threw upstream
  }
}
```

## Common Mistakes

- Awaiting inside a loop over independent items, serializing work that could be parallel.
- Calling an async function without `await` or `return`, creating a floating promise
  whose rejection becomes an unhandled rejection.
- Using `await` inside `Array.prototype.forEach`, which discards the Promise entirely.
- `Promise.all` over an unbounded array, opening thousands of connections at once.
- Typing an async function's return as `any`, so callers forget it must be awaited.
- Catching an error, logging it, and returning a "success" value — swallowing the failure.
- Doing CPU-heavy work in an async function and expecting it not to block the event loop
  (it does; offload to a worker thread).

## Production Tips

- Register `unhandledRejection` and `uncaughtException` handlers that log with context
  and exit non-zero so the orchestrator restarts a poisoned process.
- Put timeouts on every outbound call (`AbortSignal.timeout(ms)`); an async call with no
  timeout can hang a request until the socket dies.
- Instrument slow awaits with timing spans so you can find serialized hot paths in prod.
- Test the rejection paths in CI: a rejected dependency, a timed-out call, an aborted
  signal — not just the happy path.

## AI Review Checklist

- Is every Promise either awaited or returned (no floating promises)?
- Do independent operations run with `Promise.all` instead of sequential `await`s?
- Is `await` absent from `forEach`, replaced by `for...of` or `map` + `Promise.all`?
- Does every async return type read `Promise<T>` rather than `any`?
- Are outbound calls given a timeout and, where cancellable, an `AbortSignal`?
- Are errors propagated or wrapped, never caught-and-swallowed into a fake success?
- Is large-batch concurrency bounded so the connection pool is not exhausted?

## Related

- `knowledge/typescript/17-error-handling.md`
- `knowledge/typescript/04-functions.md`
- `knowledge/typescript/08-generics.md`
- `knowledge/typescript/25-performance.md`
- `knowledge/typescript/28-best-practices.md`
