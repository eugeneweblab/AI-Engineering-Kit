---
id: nodejs/99-ai-review-checklist
topic: nodejs
slug: ai-review-checklist
title: "Node.js AI Review Checklist"
type: doc
order: 99
status: ready
tags: [nodejs, ai-review-checklist]
related: [nodejs/30-engineering-principles, nodejs/100-common-antipatterns, nodejs/16-error-handling, nodejs/18-security, nodejs/06-streams]
when_to_use: "Read when reviewing a Node.js pull request or auditing a Node.js file for correctness."
---
# Node.js AI Review Checklist

## Purpose

This is the checklist an AI agent runs when reviewing Node.js code. Each item is a
concrete, verifiable check against a specific failure class in the Node runtime. It is
ordered by blast radius — the items most likely to take down the whole process come
first. Use it to review a diff, a file, or an entire service before approval.

## Why It Matters

Node.js code fails in ways that ordinary code review misses. A missing `await`, an
unheard `'error'` event, or a `readFileSync` in a hot path passes every unit test and
looks correct on the page, then freezes or crashes the process under production
concurrency. This checklist targets exactly those runtime-specific traps so a reviewer
catches them before they ship.

## Event Loop & Concurrency

**Rules:** [Event Loop](02-event-loop.md) · [Worker Threads](12-worker-threads.md)

- [ ] No `*Sync` file/crypto/zlib calls on the request or job hot path (startup-only is fine).
- [ ] No heavy synchronous CPU work (large JSON, regex backtracking, hashing) blocking the loop.
- [ ] `Promise.all` is not run over unbounded input; concurrency is bounded (e.g. a pool/limit).
- [ ] Long-running loops yield (`await`, `setImmediate`) instead of monopolizing the loop.

## Async Correctness

**Rules:** [Error Handling](16-error-handling.md) · [Streams](06-streams.md)

- [ ] Every `async` call is `await`ed, returned, or has an explicit `.catch` — no floating promises.
- [ ] No `async` function is passed where a sync callback is expected (rejections vanish silently).
- [ ] No mixing of callbacks and promises on the same operation (double-invoke / double-settle).
- [ ] `await` inside a loop is intentional; independent work uses bounded concurrency, not serial awaits.

## Error Handling

**Rules:** [Error Handling](16-error-handling.md)

- [ ] Every `EventEmitter` and stream has an `'error'` listener (an unheard `'error'` throws).
- [ ] Streams use `pipeline()` from `node:stream/promises`, not bare `.pipe()`.
- [ ] Errors are propagated with context, not swallowed by an empty `catch {}`.
- [ ] Custom errors preserve `cause` and are distinguishable (typed/coded), not stringly-typed.
- [ ] `uncaughtException`/`unhandledRejection` handlers log and **exit**, not resume.

## Resources & Lifecycle

**Rules:** [Process](10-process.md) · [Memory Management](20-memory-management.md)

- [ ] Every outbound HTTP/DB/cache call has a timeout and an `AbortSignal`.
- [ ] File handles, DB connections, timers, and listeners are released in a `finally`/`close` path.
- [ ] No `EventEmitter` listeners added per-request without removal (memory leak / max-listeners).
- [ ] No mutable state in module scope that assumes a single instance or survives restart.
- [ ] Input size (body, upload, array length) is bounded before processing.

## Security

**Rules:** [Security](18-security.md)

- [ ] User input never concatenated into SQL, shell (`exec`), or file paths — parameterized/escaped/validated.
- [ ] `child_process.exec` with user input is replaced by `execFile`/`spawn` with an argument array.
- [ ] External input is schema-validated at the boundary before use.
- [ ] No secrets, tokens, or full request bodies written to logs.
- [ ] Deserialization of untrusted data avoids prototype-pollution sinks (`__proto__`, unsafe merge).

## Configuration & Portability

**Rules:** [Configuration](15-configuration.md) · [Environment](14-environment.md)

- [ ] Config read from `process.env` is validated once at startup, not scattered and unchecked.
- [ ] No hard-coded hosts, ports, credentials, or absolute local paths.
- [ ] Uses `node:` core imports and current, non-deprecated APIs (no `new Buffer()`, no `domain`).

## Examples

**Good** — the pattern a reviewer wants to see

```js
// Floating rejection is impossible: awaited, timed out, and errors carry context.
try {
  const rows = await db.query(sql, [userId], { signal: AbortSignal.timeout(2000) });
  return rows;
} catch (err) {
  throw new Error(`load orders failed for ${userId}`, { cause: err });
}
```

**Bad** — what this checklist flags

```js
db.query("SELECT * FROM t WHERE id = " + userId) // SQL injection + no await
  .then(handle); // floating promise: a rejection here is unhandled and can crash
readable.pipe(writable); // no 'error' handler on either stream, no backpressure guarantee
```

## Common Mistakes

- Approving a diff whose tests pass but whose only failure path is an unhandled rejection.
- Treating `.catch(() => {})` as "handled" when it silently discards real errors.
- Missing that `array.forEach(async ...)` does not await — the loop finishes before the work.
- Overlooking a per-request `emitter.on(...)` that never gets removed.

## Related

- `knowledge/nodejs/30-engineering-principles.md`
- `knowledge/nodejs/100-common-antipatterns.md`
- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/18-security.md`
- `knowledge/nodejs/06-streams.md`
