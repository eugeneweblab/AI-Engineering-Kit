---
id: nodejs/01-nodejs-runtime
topic: nodejs
slug: nodejs-runtime
title: "Node.js Runtime"
type: doc
order: 1
status: ready
tags: [nodejs, nodejs-runtime, uncaughtException, unhandledRejection, engines, isInteger, "node:20"]
related: [nodejs/02-event-loop, nodejs/00-overview, nodejs/12-worker-threads, nodejs/14-environment, nodejs/10-process]
when_to_use: "Read before choosing a Node version, structuring startup code, or reasoning about how JavaScript actually executes in Node."
---
# Node.js Runtime

## Purpose

This document explains what the Node.js runtime *is* — the V8 engine, libuv, the
single-threaded execution model, and the release cadence — so an agent can make correct
decisions about versions, startup, and where CPU-bound work belongs. It is the
foundation the rest of this topic builds on.

Node.js embeds Google's V8 JavaScript engine and pairs it with **libuv**, a C library
that provides the event loop and a thread pool for asynchronous I/O. Your JavaScript
runs on one main thread; libuv does the waiting.

## Why It Matters

Choosing the wrong runtime version, or misunderstanding the single-threaded model, is
the root cause of a large fraction of Node incidents. Code that assumes threads will
silently serialize under load. Code written for a bleeding-edge Node version breaks in a
production image running LTS. Because the runtime is shared by every request in the
process, a single mistaken assumption about it degrades the whole service, not one
call. Understanding the runtime is a prerequisite for reasoning about correctness at all.

## Core Principles

- **One main thread runs your JavaScript.** V8 executes your code on a single thread;
  concurrency comes from *not waiting* on I/O, not from parallel JS execution.
- **libuv provides async I/O and a small thread pool.** File and DNS operations use a
  default 4-thread pool (`UV_THREADPOOL_SIZE`); sockets use the OS event notification.
- **Target Active LTS, not Current.** Even-numbered releases become LTS with ~30 months
  of support; use them in production for stability and security patches.
- **The runtime is the same everywhere or it is broken.** Pin the version so local, CI,
  and production execute identical semantics.
- **CPU work belongs off the main thread.** Heavy computation blocks everything; move it
  to [worker threads](12-worker-threads.md) or a [child process](11-child-process.md).

## Best Practices

- Declare the supported version in `package.json` `engines` and `.nvmrc`; enforce it in
  CI so an unsupported runtime fails the build instead of production.
- Read configuration from the environment at startup, validate it, and fail fast if
  something required is missing (see [environment](14-environment.md)).
- Keep the module's top level cheap. Work done at import time runs before your app is
  ready and cannot be error-handled by request logic.
- Register handlers for `uncaughtException` and `unhandledRejection` to log and exit;
  let a process manager restart. Do not use them to resume as if nothing happened.
- Prefer built-in globals now stable in LTS — `fetch`, `structuredClone`, `AbortController`
  — over adding dependencies for them.

## Examples

**Good Example** — validate the runtime and configuration, fail fast

```js
// Fail at startup with a clear message rather than crashing on a missing API later.
const [major] = process.versions.node.split(".").map(Number);
if (major < 20) {
  console.error(`Node 20+ required, running ${process.version}`);
  process.exit(1); // stop now; a half-supported runtime is not safe to serve
}

const port = Number(process.env.PORT);
if (!Number.isInteger(port)) {
  throw new Error("PORT must be set to an integer"); // fail fast, not on first request
}
```

**Bad Example** — assumes threads, blocks the one thread it has

```js
// This function is CPU-bound and synchronous. On the single main thread it freezes
// every other request until it returns — Node will NOT run these "in parallel".
function handleRequest(req, res) {
  let total = 0;
  for (let i = 0; i < 5_000_000_000; i++) total += i; // blocks the event loop for seconds
  res.end(String(total));
}
```

## Common Mistakes

- Assuming Node runs handlers on separate threads and that one slow call is isolated.
- Running CPU-heavy loops (crypto, image processing, large JSON) on the main thread.
- Pinning to `latest` or an odd-numbered Current release in production.
- Doing expensive or failure-prone work at module top level, before handlers exist.
- Swallowing `uncaughtException` to "keep the server up" — the process is now in an
  unknown state and may serve corrupt data.

## Production Tips

- Run under a supervisor (systemd, Kubernetes, PM2) that restarts on exit; combine with
  graceful shutdown on `SIGTERM` so in-flight requests drain.
- Set `UV_THREADPOOL_SIZE` deliberately if you do heavy file or DNS work; the default of
  4 can bottleneck throughput.
- Pin the exact runtime in your container base image (e.g. `node:20.18-slim`), not a
  floating `node:20` tag, so rebuilds are reproducible.

## AI Review Checklist

- Is the supported Node version pinned in `engines`, `.nvmrc`, and the container image?
- Is the target an Active LTS release rather than Current or `latest`?
- Is CPU-bound work kept off the main thread (worker/child process)?
- Are `uncaughtException` / `unhandledRejection` handled by logging and exiting?
- Is required configuration validated at startup with a fast, clear failure?

## Related

- `knowledge/nodejs/02-event-loop.md`
- `knowledge/nodejs/00-overview.md`
- `knowledge/nodejs/12-worker-threads.md`
- `knowledge/nodejs/14-environment.md`
- `knowledge/nodejs/10-process.md`
