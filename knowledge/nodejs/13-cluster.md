---
id: nodejs/13-cluster
topic: nodejs
slug: cluster
title: "Node.js Cluster"
type: doc
order: 13
status: ready
tags: [nodejs, cluster, fork, cpus, availableParallelism, SIGTERM, close]
related: [nodejs/10-process, nodejs/12-worker-threads, nodejs/09-http, nodejs/26-deployment, nodejs/27-monitoring]
when_to_use: "Read before scaling a Node.js HTTP server across CPU cores with the cluster module or a process manager."
---
# Node.js Cluster

## Purpose

This document defines how to scale a Node.js server across all CPU cores using the
`node:cluster` module, which forks the [process](10-process.md) into a primary and multiple
workers that share a listening socket. Use it to turn a single-core, single-process server
into one that saturates the whole machine.

Cluster is about I/O-bound horizontal scaling within one host. It is distinct from
[worker threads](12-worker-threads.md), which run parallel JS inside one process for
CPU-bound work. Choose cluster to handle more concurrent connections; choose worker threads
to speed up computation.

## Why It Matters

A single Node.js process uses one core for JavaScript. On an 8-core box, a lone process
leaves 87% of the CPU idle while still being a single point of failure — one uncaught
exception takes the whole server down. Clustering forks one worker per core so requests
spread across all of them, and the primary can respawn a dead worker instantly. The result
is both higher throughput and resilience, with no code change to your request handlers
because the OS load-balances accepted connections across workers sharing the socket.

## Core Principles

- **One worker per core, not per request.** Workers are long-lived. Fork at startup from
  `availableParallelism()`; do not fork on demand.
- **Workers share nothing.** Each is a separate process with its own memory. In-process
  state (sessions, caches, rate-limit counters, timers) is per-worker and will be
  inconsistent. Push shared state to Redis or a database.
- **The primary supervises; workers serve.** The primary process must not handle requests.
  Its job is forking, health, graceful shutdown, and respawning dead workers.
- **Sticky sessions matter for stateful protocols.** Round-robin breaks WebSocket handshakes
  and session affinity unless the load balancer or `cluster` is configured for stickiness.
- **In production, prefer a process manager or the platform.** Kubernetes, PM2, or a
  systemd template usually supervises better than hand-written cluster code.

## Best Practices

- Size the fork count from **`os.availableParallelism()`** (respects cgroup CPU limits in
  containers) — not `os.cpus().length`, which reports host cores the container cannot use.
- **Respawn dead workers** in the primary's `exit` handler, with a crash-loop guard (back off
  if a worker dies within seconds of starting) so a persistent bug does not fork-bomb.
- Implement **graceful shutdown**: on `SIGTERM`, stop accepting new connections, drain
  in-flight requests, then exit — so deploys do not drop live requests.
- Keep **all shared state external** (Redis, Postgres). Never rely on a worker-local Map for
  correctness.
- In containers, **run one process per container and let the orchestrator scale replicas**
  instead of clustering inside the container — it gives you finer scheduling and rolling
  restarts. Cluster shines on bare metal or a single VM.
- Log the **worker id / pid** on every log line so you can trace which worker served a
  request.

## Examples

**Good Example** — supervise, respawn, graceful drain

```js
import cluster from "node:cluster";
import { availableParallelism } from "node:os";
import process from "node:process";

if (cluster.isPrimary) {
  const count = availableParallelism(); // cgroup-aware core count
  for (let i = 0; i < count; i++) cluster.fork();

  cluster.on("exit", (worker, code) => {
    // Respawn so the pool never silently shrinks after a crash.
    if (!worker.exitedAfterDisconnect) cluster.fork();
  });
} else {
  const server = startHttpServer(); // each worker binds the shared socket
  process.on("SIGTERM", () => {
    // Stop accepting, drain in-flight requests, then exit cleanly.
    server.close(() => process.exit(0));
  });
}
```

**Bad Example** — primary serves, no respawn, in-memory state

```js
import cluster from "node:cluster";
import { cpus } from "node:os";

// cpus().length reports HOST cores; in a 1-CPU container this over-forks.
for (let i = 0; i < cpus().length; i++) cluster.fork();

const sessions = new Map(); // per-worker: a login on worker A is invisible on worker B
startHttpServer(); // primary ALSO serves — mixes supervision with request handling
// No 'exit' handler: once a worker dies, that core is gone until a full restart.
```

## Common Mistakes

- Using `os.cpus().length` in a container, over-forking against a cgroup CPU quota.
- Storing sessions, caches, or rate-limit counters in worker-local memory.
- No respawn handler, so the worker pool decays with every crash.
- No crash-loop backoff, letting a startup bug spawn processes endlessly.
- Skipping graceful shutdown, dropping in-flight requests on every deploy.
- Clustering *inside* a container and also scaling replicas — double concurrency, wasted RAM.
- Assuming round-robin preserves WebSocket/session affinity without sticky routing.

## Production Tips

- Prefer the orchestrator (Kubernetes HPA) or PM2 `cluster` mode over bespoke code; both add
  health checks, rolling restarts, and metrics you would otherwise reimplement.
- Emit per-worker pid in structured [logs](17-logging.md) and export worker health to
  [monitoring](27-monitoring.md).
- Set `NODE_OPTIONS=--max-old-space-size` per worker so N workers do not collectively OOM.

## AI Review Checklist

- Is the fork count derived from `availableParallelism()` (cgroup-aware)?
- Does the primary supervise only, leaving request handling to workers?
- Are dead workers respawned, with a crash-loop backoff guard?
- Is all shared state external (Redis/DB), not in worker-local memory?
- Is graceful `SIGTERM` shutdown implemented to drain in-flight requests?
- In containers, is scaling done by replicas rather than clustering inside the container?

## Related

- `knowledge/nodejs/10-process.md`
- `knowledge/nodejs/12-worker-threads.md`
- `knowledge/nodejs/09-http.md`
- `knowledge/nodejs/26-deployment.md`
- `knowledge/nodejs/27-monitoring.md`
