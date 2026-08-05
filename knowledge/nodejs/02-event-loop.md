---
id: nodejs/02-event-loop
topic: nodejs
slug: event-loop
title: "Node.js Event Loop"
type: doc
order: 2
status: ready
tags: [nodejs, event-loop, process.nextTick, once, setImmediate, JSON.parse, Worker, createHash]
related: [nodejs/01-nodejs-runtime, nodejs/12-worker-threads, nodejs/06-streams, nodejs/19-performance, nodejs/16-error-handling]
when_to_use: "Read before writing async code, doing any CPU-bound work, or diagnosing why a Node service is unresponsive under load."
---
# Node.js Event Loop

## Purpose

This document explains the Node.js event loop: its phases, the difference between
macrotasks and microtasks, and the single rule that governs almost all Node performance
— **never block the loop**. An agent that understands this section can predict execution
order and avoid the freezes that dominate Node incidents.

The event loop is libuv's mechanism for doing many things "at once" on one thread. It
cycles through phases, running callbacks whose I/O is ready, then draining a queue of
microtasks, then repeating. Your JavaScript only ever runs *between* waits.

## Why It Matters

Node's throughput comes entirely from the loop staying free to pick up the next ready
callback. Any synchronous work — a tight loop, a big `JSON.parse`, a synchronous file
read, a slow regex — holds the thread and every pending request waits behind it.
Latency spikes, health checks time out, and the process looks "hung" while using 100%
CPU. Unlike a thread-per-request server, Node has no other thread to absorb the stall.
The loop is the shared resource; protecting it is the core discipline of Node.

## Core Principles

- **The loop runs your code between I/O waits.** While a callback executes, nothing else
  in the process can run. Keep each callback short.
- **Microtasks drain fully between macrotasks.** Resolved promises and `queueMicrotask`
  run after the current operation and *before* the loop advances — starving the loop if
  they recurse.
- **`process.nextTick` jumps the queue.** It runs before other microtasks; recursive
  `nextTick` can block the loop entirely. Prefer `setImmediate` for "run soon."
- **Timers are a floor, not a guarantee.** `setTimeout(fn, 10)` runs *no sooner* than
  10ms; a busy loop delays it arbitrarily.
- **CPU-bound work does not belong here.** Offload it to a [worker thread](12-worker-threads.md)
  or child process so the loop stays responsive.

## Best Practices

- Prefer streaming and chunked processing over loading a whole payload into memory and
  processing it in one synchronous pass (see [streams](06-streams.md)).
- Break large synchronous computations into chunks yielded with `setImmediate`, or move
  them off-thread — the latter is usually cleaner.
- Use the async variants of every I/O API; reserve `*Sync` calls for startup scripts and
  CLIs that do nothing concurrently.
- Add `await` points in long loops that do async work so the loop can interleave other
  callbacks, but do not add fake awaits to "unblock" pure CPU work — that does not help.
- Monitor event-loop lag (e.g. `perf_hooks.monitorEventLoopDelay`) and alert on it; it
  is the earliest signal of a blocking regression.

## Examples

**Good Example** — offload CPU work so the loop stays responsive

```js
import { Worker } from "node:worker_threads";

// Heavy hashing runs on a worker thread; the main loop keeps serving requests
// while it computes, instead of freezing for the duration.
function hashInWorker(payload) {
  return new Promise((resolve, reject) => {
    const w = new Worker("./hash-worker.js", { workerData: payload });
    w.once("message", resolve);
    w.once("error", reject);
  });
}
```

**Bad Example** — synchronous CPU work blocks every other request

```js
import { createHash } from "node:crypto";

app.get("/report", (req, res) => {
  // Reading and hashing a large file synchronously on the main thread stalls the
  // event loop: all other connections hang until this finishes.
  const data = fs.readFileSync("./huge.bin");      // blocks on I/O
  const digest = createHash("sha256").update(data).digest("hex"); // blocks on CPU
  res.end(digest);
});
```

## Common Mistakes

- Using `fs.readFileSync`, `JSON.parse` on megabytes, or synchronous crypto in a request
  handler.
- Recursive `process.nextTick` or promise chains that never yield, starving I/O
  callbacks.
- Assuming `setTimeout(fn, 0)` runs "immediately" — it runs after the current phase and
  after microtasks.
- Believing `async`/`await` makes CPU-bound code non-blocking; `await` only yields at
  real async boundaries.
- Catching the symptom (raising timeouts) instead of the cause (a blocking call).

## Production Tips

- Track event-loop delay as a first-class metric; sustained lag over a few milliseconds
  under normal load indicates a blocking hot path.
- Profile with `--prof` or the Chrome DevTools inspector to find the synchronous
  function holding the thread.
- Cap request body sizes and paginate; unbounded input turns a small handler into a loop
  blocker.

## AI Review Checklist

- Are all I/O calls asynchronous, with no `*Sync` variants on request paths?
- Is CPU-bound work (crypto, parsing large data, image work) moved off the main thread?
- Are there any recursive `process.nextTick` / microtask chains that could starve I/O?
- Does the code avoid relying on timer delays as exact schedules?
- Is event-loop lag observable in production?

## Related

- `knowledge/nodejs/01-nodejs-runtime.md`
- `knowledge/nodejs/12-worker-threads.md`
- `knowledge/nodejs/06-streams.md`
- `knowledge/nodejs/19-performance.md`
- `knowledge/nodejs/16-error-handling.md`
