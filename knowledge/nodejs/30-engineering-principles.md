---
id: nodejs/30-engineering-principles
topic: nodejs
slug: engineering-principles
title: "Node.js Engineering Principles"
type: doc
order: 30
status: ready
tags: [nodejs, engineering-principles]
related: [nodejs/02-event-loop, nodejs/16-error-handling, nodejs/28-best-practices, nodejs/06-streams, nodejs/19-performance]
when_to_use: "Read before designing a new Node.js service or reviewing how existing Node code is structured."
---
# Node.js Engineering Principles

## Purpose

This document defines the durable principles that separate correct, production-grade
Node.js code from code that merely runs on a laptop. It is the mental model an agent
should hold *before* writing any handler, worker, or CLI: how the runtime actually
executes work, where it breaks under load, and which defaults keep a process alive.

These principles are runtime truths, not style preferences. They apply whether you use
Express, Fastify, NestJS, or plain `node:http`, and whether the code is a request
handler or a background job.

## Why It Matters

Node.js runs your JavaScript on a **single main thread** driven by an event loop. That
one thread is the entire budget for every request in the process. A mistake that would
merely slow one request in a thread-per-request runtime (Java, Go) will freeze *all*
concurrent requests in Node. The failure mode is not a slow endpoint — it is a process
that stops responding to health checks and gets killed.

Because concurrency is cooperative, correctness in Node depends less on business logic
and more on *not blocking the loop*, *always handling async rejection*, and *bounding
resource use*. These are the errors that pass every unit test and only surface under
production traffic.

## Core Principles

- **Never block the event loop.** Synchronous CPU work (crypto, JSON of megabytes,
  `fs.*Sync`, regex backtracking, `bcrypt` sync) stalls every other request. Offload it
  to `worker_threads`, a child process, or an async library API.
- **Everything I/O is async, and every async path can reject.** An unhandled promise
  rejection or an unheard `'error'` event can crash the process. Model failure as a
  first-class path, not an afterthought.
- **Bound every resource.** Connections, in-flight requests, queue depth, payload size,
  and memory are all finite. Unbounded anything is an outage waiting for load.
- **Backpressure is not optional.** When you produce data faster than the consumer
  drains it, buffering fills memory until the process dies. Respect stream signals.
- **Processes are disposable.** Design to crash safely and restart fast. State belongs
  in a database or cache, never in a module-level variable that a restart erases.
- **Config comes from the environment, secrets never from code.** The same artifact must
  run in every environment, differing only by injected configuration.

## Best Practices

- Prefer **async APIs** (`fs.promises`, `await`) over `*Sync` variants everywhere except
  one-time startup before the server accepts traffic.
- Use **ES modules** (`"type": "module"`) and `node:`-prefixed core imports. Pin the
  runtime with an `engines` field and a `.nvmrc`.
- Attach an `'error'` listener to every `EventEmitter` and stream; an unheard `'error'`
  throws. Use `stream.pipeline`/`pipeline` from `node:stream/promises`, never bare `.pipe()`.
- Propagate cancellation with **`AbortSignal`**. Give every outbound call a timeout so a
  slow dependency cannot pin your event loop indefinitely.
- Register handlers for `SIGTERM`/`SIGINT` to **drain and close** gracefully; stop
  accepting new work, finish in-flight work, then exit.
- Let `unhandledRejection` and `uncaughtException` **crash the process** (after logging)
  and rely on a supervisor to restart. Do not swallow them to "keep running" — the
  process is now in an unknown state.
- Validate and bound all external input at the boundary (body size limits, schema
  validation) before it reaches business logic.

## Examples

**Good Example** — non-blocking, cancellable, backpressure-aware

```js
import { setTimeout as delay } from "node:timers/promises";
import { pipeline } from "node:stream/promises";

// Timeout via AbortSignal so a slow upstream cannot hold the loop forever.
async function fetchUser(id, { signal } = {}) {
  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), 3000);
  signal?.addEventListener("abort", () => ac.abort(), { once: true });
  try {
    const res = await fetch(`${API}/users/${id}`, { signal: ac.signal });
    if (!res.ok) throw new Error(`upstream ${res.status}`); // failure is a real path
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

// pipeline() propagates errors AND applies backpressure between streams.
await pipeline(readable, transform, writable);
```

**Bad Example** — blocks the loop, leaks the failure, unbounded

```js
import fs from "node:fs";
import crypto from "node:crypto";

app.get("/report", (req, res) => {
  // fs.readFileSync + a big pbkdf2Sync freeze EVERY concurrent request
  // for the whole duration, not just this one.
  const raw = fs.readFileSync("./huge.json", "utf8");
  const key = crypto.pbkdf2Sync(raw, "salt", 1_000_000, 64, "sha512");

  db.query(buildQuery(req.query)); // no await, no error handling → silent rejection
  res.end(key.toString("hex"));    // no timeout, no size bound
});
```

## Common Mistakes

- Calling `*Sync` file, crypto, or compression APIs inside a request handler.
- Firing an async call without `await` or `.catch`, producing an unhandled rejection.
- Using `.pipe()` without an `'error'` handler, so a source error crashes the process.
- Catching `uncaughtException` and continuing, running the process in a corrupt state.
- Storing sessions, counters, or caches in module scope and losing them on restart —
  and getting wrong results the moment a second instance runs.
- No timeout on outbound HTTP/DB calls, so one slow dependency cascades into a full stall.
- Reading config with `process.env.X` scattered through the code instead of validating
  it once at startup.

## Production Tips

- Run behind a supervisor (systemd, Kubernetes, PM2) that restarts on exit; make the
  process *want* to crash on unknown errors rather than limp along.
- Set `--max-old-space-size` to match the container memory limit so V8 GCs before the
  OOM killer strikes.
- Expose `/healthz` (liveness) and `/readyz` (readiness) so orchestrators route traffic
  only to warmed-up instances and evict frozen ones.
- Measure event-loop lag (`perf_hooks.monitorEventLoopDelay`); rising lag is the earliest
  signal that something is blocking.

## AI Review Checklist

- Is any `*Sync` or heavy CPU work running on the request path? Move it off-thread.
- Does every `async` call have an `await`, `.catch`, or explicit fire-and-forget policy?
- Does every stream and `EventEmitter` have an `'error'` handler?
- Do outbound calls carry a timeout and an `AbortSignal`?
- Is graceful shutdown wired to `SIGTERM`, draining in-flight work before exit?
- Is all mutable state external (DB/cache), so a restart or second instance is safe?
- Are inputs size-bounded and schema-validated at the boundary?

## Related

- `knowledge/nodejs/02-event-loop.md`
- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/06-streams.md`
- `knowledge/nodejs/28-best-practices.md`
- `knowledge/nodejs/19-performance.md`
