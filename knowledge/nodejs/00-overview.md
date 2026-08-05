---
id: nodejs/00-overview
topic: nodejs
slug: overview
title: "Node.js Overview"
type: doc
order: 0
status: ready
tags: [nodejs, overview]
related: [nodejs/01-nodejs-runtime, nodejs/02-event-loop, nodejs/03-modules, nodejs/04-package-management, nodejs/16-error-handling]
when_to_use: "Read first when starting or reviewing any Node.js codebase, to orient yourself before diving into specific docs."
---
# Node.js Overview

## Purpose

This document is the map for the `nodejs` topic. It orients an agent to what Node.js
is, the mental models that make Node code correct, and how the sibling docs in this
topic fit together. Read it first, then jump to the specific doc for the task at hand.

Node.js is a single-threaded, event-driven JavaScript runtime built on V8. That one
sentence explains most of what goes right and wrong in Node code: work is fast when it
stays non-blocking, and everything grinds to a halt when it does not. The docs here
exist to keep an agent on the non-blocking, production-safe path.

## Why It Matters

Node.js runs a huge share of production backends, CLIs, and build tooling. Its
concurrency model is unusual: there is no per-request thread, so a single blocking call
or an unhandled promise rejection can stall or crash the *entire* process — every user,
not one request. Most Node bugs are not logic errors; they are model errors: blocking
the event loop, leaking file descriptors, mixing module systems, or trusting the
network to be fast. Getting the model right is what separates code that survives
production from code that only works on a developer's laptop.

## Core Principles

- **Never block the event loop.** One thread serves all requests. CPU-bound or
  synchronous work freezes everything; offload it (see [event loop](02-event-loop.md)).
- **Everything I/O is async.** Prefer promises and `async/await`; treat synchronous
  APIs (the `*Sync` variants) as startup-only.
- **Fail loud, fail closed.** An unhandled rejection or uncaught exception should crash
  the process and let a supervisor restart it — never swallow it.
- **Pin what you ship.** Reproducible installs from a committed lockfile are the
  difference between "works here" and "works everywhere" (see [package management](04-package-management.md)).
- **The runtime is not the browser.** No DOM, real file/network/process access, and a
  different security surface. Treat all external input as hostile.

## How the Docs Fit Together

- **Foundations** — [01 Runtime](01-nodejs-runtime.md), [02 Event Loop](02-event-loop.md),
  [03 Modules](03-modules.md): the execution model. Read these before anything else.
- **Project setup** — [04 Package Management](04-package-management.md),
  [14 Environment](14-environment.md), [15 Configuration](15-configuration.md): how a
  Node project is assembled and configured.
- **I/O building blocks** — [05 File System](05-file-system.md), [06 Streams](06-streams.md),
  [07 Buffers](07-buffers.md), [08 Events](08-events.md), [09 HTTP](09-http.md): the core
  library surface most code touches.
- **Concurrency & processes** — [10 Process](10-process.md), [11 Child Process](11-child-process.md),
  [12 Worker Threads](12-worker-threads.md), [13 Cluster](13-cluster.md): scaling past one core.
- **Operability** — [16 Error Handling](16-error-handling.md), [17 Logging](17-logging.md),
  [18 Security](18-security.md), [19 Performance](19-performance.md), [20 Memory](20-memory-management.md),
  [27 Monitoring](27-monitoring.md): keeping it alive in production.
- **Delivery** — [21 Testing](21-testing.md), [22 Debugging](22-debugging.md),
  [26 Deployment](26-deployment.md), [28 Best Practices](28-best-practices.md),
  [98 Production Checklist](98-production-checklist.md), [99 AI Review Checklist](99-ai-review-checklist.md),
  [100 Anti-patterns](100-common-antipatterns.md).

## Best Practices

- Target an **Active LTS** Node version and record it in `.nvmrc` and `package.json`
  `engines`, so local, CI, and production all run the same runtime.
- Reach for the standard library first — Node ships fetch, a test runner, and a
  WebSocket client. Add a dependency only when the built-in genuinely falls short.
- Write ESM (`"type": "module"`) for new projects; it is the standard module system and
  the direction the ecosystem is moving.
- Keep the process stateless where possible so it can be restarted or scaled
  horizontally without data loss.

## Common Mistakes

- Treating Node like a multi-threaded server and assuming one slow request cannot affect
  others — it can, they share the loop.
- Skipping the foundational docs and copying HTTP/file examples without understanding
  the async model underneath them.
- Choosing a Node version at random; version drift between environments hides bugs.
- Adding heavy dependencies for tasks the standard library now covers.

## AI Review Checklist

- Does the code target a supported LTS Node version, pinned in config?
- Is all I/O asynchronous, with no synchronous calls on the hot path?
- Are unhandled rejections and uncaught exceptions surfaced (crash + restart), not
  swallowed?
- Is the module system (ESM vs CommonJS) consistent across the project?
- Did you consult the specific sibling doc for the subsystem you are changing?

## Related

- `knowledge/nodejs/01-nodejs-runtime.md`
- `knowledge/nodejs/02-event-loop.md`
- `knowledge/nodejs/03-modules.md`
- `knowledge/nodejs/04-package-management.md`
- `knowledge/nodejs/16-error-handling.md`
