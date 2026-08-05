---
id: nodejs/28-best-practices
topic: nodejs
slug: best-practices
title: "Node.js Best Practices"
type: doc
order: 28
status: ready
tags: [nodejs, best-practices]
related: [nodejs/16-error-handling, nodejs/18-security, nodejs/21-testing, nodejs/29-tooling, nodejs/30-engineering-principles]
when_to_use: "Read before writing or reviewing any Node.js service code you intend to run in production."
---
# Node.js Best Practices

## Purpose

This document distills the highest-leverage habits for writing production-grade Node.js:
async correctness, error handling, resource discipline, and safe defaults. It is written
so an agent can apply a short set of concrete rules that prevent the most common classes
of Node.js failure, and cross-links to the deeper topic docs for each area.

It is a synthesis, not a replacement — [error handling](16-error-handling.md),
[security](18-security.md), [testing](21-testing.md), and [tooling](29-tooling.md) each go
deeper. This doc is the checklist you keep in your head while coding.

## Why It Matters

Node.js gives you a single-threaded, non-blocking runtime and very few guardrails. The
same design that makes it fast makes it unforgiving: one unhandled promise rejection can
crash the process, one synchronous call in a hot path blocks every user, one swallowed
error hides a data-corruption bug for months. Most Node incidents are not exotic — they are
a handful of repeated mistakes. Internalizing a small set of correct defaults eliminates
the majority of production failures before they are written.

## Core Principles

- **Never block the event loop.** One loop serves all requests. Synchronous CPU work,
  `fs.readFileSync`, or a huge `JSON.parse` in a handler stalls everyone. Offload or stream.
- **Every promise is awaited or explicitly handled.** A floating promise loses its result
  and its errors. `async` errors must reach a `try/catch` or a rejection handler.
- **Fail fast and loud in code, gracefully at the edge.** Validate inputs at the boundary,
  throw on programmer errors, and translate to a clean response — never swallow.
- **Own your resources.** Every connection, file handle, timer, and stream is closed in a
  `finally` or on shutdown. Leaks are the default; cleanup is deliberate.
- **Secure and configurable by default.** Read config from the environment, validate it at
  startup, and never trust or log untrusted input.

## Best Practices

- Write async code with `async/await`; avoid mixing callbacks and promises. Use
  `Promise.all` for independent work, but bound concurrency (`p-limit`) for large batches so
  you do not open ten thousand sockets at once.
- Handle `unhandledRejection` and `uncaughtException` by logging and exiting — the process
  is in an unknown state; let the orchestrator restart it, do not resume.
- Validate all external input (HTTP bodies, env vars, queue messages) with a schema (Zod)
  at the boundary; treat everything past validation as typed and trusted.
- Prefer streams for large payloads; buffering a big file or response into memory invites
  OOM and event-loop stalls (see [performance](19-performance.md)).
- Keep functions small and side-effect-explicit; pass dependencies in rather than importing
  singletons, so code is testable without a running database.
- Pin dependencies with a committed lockfile and run `npm audit` / a scanner in CI; a
  transitive vuln is your vuln.
- Use `node:` protocol imports for built-ins (`import fs from "node:fs"`) to avoid ambiguity
  with a same-named package.
- Centralize error handling and logging; do not scatter `console.log` — use a structured
  [logger](17-logging.md) so output is queryable.

## Examples

**Good Example** — bounded concurrency, awaited, resources released

```ts
import pLimit from "p-limit";

const limit = pLimit(10); // cap in-flight work so we don't exhaust sockets or memory

async function processAll(ids: string[]) {
  // Every task is awaited; a rejection here propagates instead of vanishing.
  const results = await Promise.all(
    ids.map((id) => limit(() => processOne(id))),
  );
  return results;
}

async function processOne(id: string) {
  const conn = await pool.acquire();
  try {
    return await conn.run(id);
  } finally {
    conn.release(); // released on success AND on throw — no leak
  }
}
```

**Bad Example** — floating promise, unbounded fan-out, leaked handle

```ts
function processAll(ids: string[]) {
  ids.forEach((id) => {
    processOne(id); // fire-and-forget: result lost, rejection becomes unhandledRejection → crash
  });
  // Opening N connections at once with no limit exhausts the pool for large N.
}

async function processOne(id: string) {
  const conn = await pool.acquire();
  const r = await conn.run(id); // if this throws, conn is never released → pool starvation
  conn.release();
  return r;
}
```

## Common Mistakes

- Floating promises (`someAsync()` with no `await`/`.catch`), silently dropping errors.
- Blocking the event loop with sync I/O or CPU work in a request handler.
- Unbounded `Promise.all` over a large array, exhausting sockets, file handles, or memory.
- Acquiring a resource outside `try/finally`, so a throw leaks the connection or handle.
- Swallowing errors (`catch (e) {}`) instead of handling or rethrowing.
- Resuming after `uncaughtException` instead of exiting, running on with corrupt state.
- Trusting unvalidated external input, or logging it verbatim (injection, PII leaks).

## Production Tips

- Enable `"use strict"` (implicit in ESM) and TypeScript in `strict` mode; most Node bugs
  are type or null mistakes a compiler catches for free.
- Set explicit timeouts on every outbound call and DB query; the default is often "forever."
- Run the same lint, type-check, and tests in CI as locally, so nothing merges unchecked
  ([tooling](29-tooling.md)).

## AI Review Checklist

- Is every promise awaited or given an explicit rejection handler?
- Is the event loop kept free of sync I/O and CPU-bound work in handlers?
- Is fan-out concurrency bounded, and is every resource released in `finally`?
- Is all external input validated at the boundary with a schema?
- Do `unhandledRejection`/`uncaughtException` log and exit rather than resume?
- Are built-ins imported via `node:` and dependencies pinned with a lockfile?
- Is error handling and logging centralized and structured, not scattered `console.log`?

## Related

- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/18-security.md`
- `knowledge/nodejs/21-testing.md`
- `knowledge/nodejs/29-tooling.md`
- `knowledge/nodejs/30-engineering-principles.md`
