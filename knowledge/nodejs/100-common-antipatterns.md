---
id: nodejs/100-common-antipatterns
topic: nodejs
slug: common-antipatterns
title: "Node.js Common Antipatterns"
type: antipatterns
order: 100
status: ready
tags: [nodejs, common-antipatterns, pipe, save, execFile, charge]
related: [nodejs/02-event-loop, nodejs/16-error-handling, nodejs/06-streams, nodejs/30-engineering-principles, nodejs/19-performance]
when_to_use: "Read when writing or reviewing Node.js code to recognize and avoid the recurring failure patterns below."
---
# Node.js Common Antipatterns

## Purpose

This document catalogs the Node.js anti-patterns that most often cause production
incidents. Each entry names the pattern, explains **why it is wrong** in terms of the
runtime, and gives **the fix** with a short code contrast. These are the specific
mistakes an agent should refuse to write and should flag on sight during review.

## Why It Matters

Node's single-threaded, event-driven model rewards a handful of correct habits and
punishes a handful of tempting shortcuts. The patterns below all "work" in development
and under low load; they fail only when concurrency, payload size, or a slow dependency
arrives. Learning them by name is the fastest way to avoid the outages they cause.

## Anti-Patterns

### 1. Blocking the event loop with synchronous work

**Why it is wrong.** `fs.readFileSync`, `crypto.pbkdf2Sync`, `zlib.gzipSync`, and heavy
JSON/regex run on the one main thread. While they run, *every* other request in the
process is frozen — throughput collapses and health checks time out.

**The fix.** Use async APIs; push real CPU work to `worker_threads`.

```js
// Bad: freezes all concurrent requests for the duration of the hash
const key = crypto.pbkdf2Sync(pw, salt, 600000, 32, "sha256");
// Good: async, loop stays free for other requests
const key = await promisify(crypto.pbkdf2)(pw, salt, 600000, 32, "sha256");
```

### 2. Floating promises (missing `await`)

**Why it is wrong.** An async call with no `await`/`.catch` returns a promise nobody
handles. If it rejects, you get an `unhandledRejection` that can crash the process, and
the caller continues as if the work succeeded.

**The fix.** Await it, return it, or attach a `.catch` with an explicit policy.

```js
// Bad: rejection is unhandled; response is sent before the write finishes
audit.log(event);            res.end("ok");
// Good
await audit.log(event);      res.end("ok");
```

### 3. `async` callback in `forEach`

**Why it is wrong.** `Array.prototype.forEach` ignores the returned promise. The loop
completes synchronously while the async bodies are still pending, so "after the loop"
code runs too early and errors are lost.

**The fix.** Use `for...of` with `await`, or `Promise.all`/a bounded map for concurrency.

```js
// Bad: finishes before any save completes
items.forEach(async (i) => { await save(i); });
// Good: sequential and awaited
for (const i of items) { await save(i); }
// Good: bounded concurrency for independent work
await Promise.all(items.map((i) => save(i))); // only if `items` is bounded
```

### 4. `.pipe()` without error handling

**Why it is wrong.** A bare `readable.pipe(writable)` does not forward errors. An error
on either stream becomes an unheard `'error'` event, which throws and crashes the
process, and the destination is not cleaned up.

**The fix.** Use `pipeline`, which forwards errors and destroys streams on failure.

```js
// Bad
readable.pipe(gzip).pipe(writable);
// Good: errors propagate, all streams closed on failure, backpressure honored
import { pipeline } from "node:stream/promises";
await pipeline(readable, gzip, writable);
```

### 5. Swallowing errors with an empty catch

**Why it is wrong.** `catch {}` hides failures. The program continues on corrupt or
missing data, and the root cause becomes invisible in logs — turning a clear error into
a mysterious downstream bug.

**The fix.** Handle, or rethrow with context via `cause`.

```js
// Bad
try { await charge(order); } catch { /* ignore */ }
// Good
try { await charge(order); }
catch (err) { throw new Error(`charge failed for ${order.id}`, { cause: err }); }
```

### 6. Building shell commands from user input

**Why it is wrong.** `child_process.exec(`convert ${name}`)` runs a shell, so input like
`; rm -rf /` executes. This is command injection — one of the highest-severity bugs.

**The fix.** Use `execFile`/`spawn` with an argument array; no shell, no interpolation.

```js
// Bad
exec(`convert ${userFile} out.png`);
// Good: arguments passed literally, never parsed by a shell
execFile("convert", [userFile, "out.png"]);
```

### 7. String-concatenated SQL

**Why it is wrong.** Concatenating user input into a query allows SQL injection. It also
mishandles quoting and types even for benign input.

**The fix.** Use parameterized queries; let the driver bind values.

```js
// Bad
db.query("SELECT * FROM users WHERE email = '" + email + "'");
// Good
db.query("SELECT * FROM users WHERE email = $1", [email]);
```

### 8. Unbounded resource use

**Why it is wrong.** `Promise.all(ids.map(fetchOne))` over 100k ids opens 100k
connections at once; an unlimited body parser buffers gigabytes. Under load, this
exhausts sockets, file handles, or memory and OOM-kills the process.

**The fix.** Bound everything: concurrency limits, pool sizes, and body-size caps.

```js
// Bad: 100k concurrent requests
await Promise.all(ids.map(fetchOne));
// Good: bounded pool (e.g. p-limit or a simple worker queue)
const limit = pLimit(20);
await Promise.all(ids.map((id) => limit(() => fetchOne(id))));
```

### 9. Mutable state in module scope

**Why it is wrong.** A module-level cache, counter, or session map assumes one process
that never restarts. Scale to two instances or restart once and the state is wrong or
gone — a class of bug that never appears in single-instance testing.

**The fix.** Keep shared, durable state in a database or cache (Redis); keep only
process-local, reconstructable state in memory.

```js
// Bad: lost on restart, inconsistent across instances
let sessions = new Map();
// Good
await redis.set(`session:${id}`, data, { EX: 3600 });
```

### 10. No timeout on outbound calls

**Why it is wrong.** A `fetch` or DB call with no timeout waits forever if the dependency
hangs. Each pending call holds a request slot; a single slow upstream cascades into a
fully stalled service.

**The fix.** Give every outbound call a timeout via `AbortSignal`.

```js
// Bad: hangs indefinitely if upstream stalls
const res = await fetch(url);
// Good: fails fast, freeing the slot
const res = await fetch(url, { signal: AbortSignal.timeout(3000) });
```

### 11. Catching `uncaughtException` to "keep running"

**Why it is wrong.** After an uncaught exception, the process is in an unknown state —
open transactions, half-written data, leaked resources. Resuming risks silent
corruption.

**The fix.** Log, then exit; let a supervisor restart into a clean state.

```js
process.on("uncaughtException", (err) => {
  logger.fatal(err);
  process.exit(1); // do NOT resume
});
```

## AI Review Checklist

- [ ] No `*Sync` or heavy CPU work on a hot path (anti-patterns 1).
- [ ] No floating promises, `forEach(async)`, or bare `.pipe()` (2, 3, 4).
- [ ] No empty catches or resumed `uncaughtException` (5, 11).
- [ ] No user input in shell or SQL strings (6, 7).
- [ ] Concurrency, pools, and body sizes are bounded (8).
- [ ] Shared state is external, not module scope (9); outbound calls have timeouts (10).

## Related

- `knowledge/nodejs/02-event-loop.md`
- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/06-streams.md`
- `knowledge/nodejs/30-engineering-principles.md`
- `knowledge/nodejs/19-performance.md`
