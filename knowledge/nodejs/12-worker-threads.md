---
id: nodejs/12-worker-threads
topic: nodejs
slug: worker-threads
title: "Worker Threads"
type: doc
order: 12
status: ready
tags: [nodejs, worker-threads, Piscina, postMessage, availableParallelism, Worker, createHash, digest]
related: [nodejs/02-event-loop, nodejs/11-child-process, nodejs/13-cluster, nodejs/19-performance, nodejs/20-memory-management]
when_to_use: "Read before offloading CPU-bound work off the event loop with the worker_threads module."
---
# Worker Threads

## Purpose

This document defines when and how to use the `node:worker_threads` module to run
JavaScript in parallel on separate threads, sharing the same process. Use it to move
CPU-bound work (hashing, compression, image/PDF processing, parsing large payloads) off
the main thread so the [event loop](02-event-loop.md) stays responsive.

Worker threads are not a general concurrency tool. Node.js is single-threaded for JS by
design; reach for a worker only when a synchronous computation would otherwise block the
event loop for tens of milliseconds or more.

## Why It Matters

The event loop runs all your request handlers on one thread. A single CPU-heavy function
— a synchronous JSON parse of a 50 MB body, a `bcrypt` round, a regex over a huge string —
blocks *every* concurrent request until it finishes. Latency spikes, health checks time
out, and the process looks hung even though nothing crashed. Worker threads give you true
parallelism for that work without the memory cost and IPC overhead of a full
[child process](11-child-process.md), because workers share the same V8 isolate host and
can transfer memory instead of copying it.

## Core Principles

- **Only offload CPU-bound work.** I/O is already asynchronous; wrapping a database call in
  a worker adds overhead and buys nothing. Workers pay off when the work is pure computation.
- **Workers do not share JS memory.** Each worker has its own V8 heap and globals. Data
  crosses the boundary by structured-clone copy, `transfer`, or explicit `SharedArrayBuffer`.
- **Creating a worker is expensive.** Spawning costs several milliseconds and a fresh heap.
  Pool and reuse workers; never spawn one per request.
- **A worker crash is your problem to handle.** An unhandled error in a worker emits `error`
  and then `exit`; the main thread must react or the pool silently shrinks.
- **The worker file must be a real module path, not inline logic you forgot to isolate.**
  Keep worker code in its own file with a clear input/output contract.

## Best Practices

- Use a **fixed-size worker pool** sized to `os.availableParallelism()` (not a magic number).
  More workers than cores causes context-switch thrashing, not more throughput.
- Prefer **`Piscina`** or a small in-house pool over hand-rolling lifecycle management for
  anything beyond a one-off task; it handles queuing, backpressure, and recycling.
- Pass large binary payloads with the **`transferList`** argument so the buffer is moved,
  not copied — the sender loses access, which is the point.
- Use **`SharedArrayBuffer` + `Atomics`** only for genuine shared state; it is easy to get
  wrong and rarely needed.
- Always attach `error` and `exit` handlers, and treat a non-zero `exit` code as a failure
  that rejects the pending task.
- Set a **timeout** per task and terminate a worker that overruns; a runaway loop will never
  yield on its own.
- Keep the worker's dependency graph small — every `require` runs again per worker, adding
  startup cost and memory.

## Examples

**Good Example** — pooled worker, transferred buffer, error handling

```js
// pool.js (main thread)
import Piscina from "piscina";
import { availableParallelism } from "node:os";

const pool = new Piscina({
  filename: new URL("./hash-worker.js", import.meta.url).href,
  maxThreads: availableParallelism(), // match cores, not an arbitrary constant
});

export async function hashFile(bytes) {
  // ArrayBuffer is transferred (moved), so no multi-MB copy crosses the boundary.
  return pool.run(bytes, { transferList: [bytes] });
}
```

```js
// hash-worker.js
import { createHash } from "node:crypto";

export default function (bytes) {
  // Pure CPU work: this is exactly what belongs off the main thread.
  return createHash("sha256").update(Buffer.from(bytes)).digest("hex");
}
```

**Bad Example** — a worker per call, copied data, no error handling

```js
import { Worker } from "node:worker_threads";

function hashFile(bytes) {
  // New worker every call: pays multi-ms startup + a fresh heap each time.
  const worker = new Worker("./hash-worker.js");
  return new Promise((resolve) => {
    worker.postMessage(bytes); // structured clone COPIES the whole buffer
    worker.on("message", resolve);
    // No 'error'/'exit' handler: a worker crash leaves this Promise pending forever.
  });
}
```

## Common Mistakes

- Offloading I/O-bound work (DB, HTTP, disk) to a worker — pure overhead, zero benefit.
- Spawning a worker per request instead of pooling, so startup cost dominates.
- Using `postMessage` for large buffers without `transferList`, doubling memory and CPU.
- Forgetting `error`/`exit` handlers, so a crashed worker leaves promises hanging.
- Assuming workers share variables or module state with the main thread — they do not.
- Sizing the pool larger than available cores, causing scheduler thrashing.
- Reaching for workers when the real fix is streaming or an async library.

## Production Tips

- Expose pool metrics (queue depth, active threads, task duration) to
  [monitoring](27-monitoring.md); a growing queue means you are CPU-bound and need to scale.
- Set a hard per-task timeout and recycle workers after N tasks to bound memory leaks in
  native addons.
- Load-test with realistic payload sizes — transfer vs. copy behavior only shows up at scale.

## AI Review Checklist

- Is the offloaded work genuinely CPU-bound, not I/O that is already async?
- Are workers pooled and reused rather than spawned per request?
- Is the pool sized from `availableParallelism()` rather than a magic number?
- Are large buffers moved with `transferList`, not copied via structured clone?
- Are `error` and non-zero `exit` handled so tasks reject instead of hanging?
- Is there a per-task timeout and a recycle policy for long-lived workers?

## Related

- `knowledge/nodejs/02-event-loop.md`
- `knowledge/nodejs/11-child-process.md`
- `knowledge/nodejs/13-cluster.md`
- `knowledge/nodejs/19-performance.md`
- `knowledge/nodejs/20-memory-management.md`
