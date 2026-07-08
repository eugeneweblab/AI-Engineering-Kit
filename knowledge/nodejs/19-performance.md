---
id: nodejs/19-performance
topic: nodejs
slug: performance
title: "Performance"
type: doc
order: 19
status: ready
tags: [nodejs, performance]
related: [nodejs/02-event-loop, nodejs/06-streams, nodejs/12-worker-threads, nodejs/20-memory-management, nodejs/27-monitoring]
when_to_use: "Read before optimizing a slow Node.js service, or when latency/throughput regresses under load."
---
# Performance

## Purpose

This document defines how to reason about and improve the performance of a Node.js
process. The governing fact is that Node runs your JavaScript on a *single thread*:
throughput is determined by how quickly that thread returns to the event loop, not
by how fast any one function runs. This doc covers keeping the loop free, moving CPU
work off it, and measuring before you change anything.

## Why It Matters

In a single-threaded runtime, one slow synchronous operation blocks *every*
concurrent request, not just its own. A 200ms JSON parse or a synchronous crypto call
does not slow one user — it queues all users behind it, and tail latency explodes
under load while CPU sits mostly idle. Performance bugs in Node are usually not "slow
code" but "blocking code" and "unmeasured guesses." The fix is almost always
structural, and it must be driven by a profile, not intuition.

## Core Principles

- **Never block the event loop.** No synchronous I/O, no CPU-heavy loops, no huge
  synchronous JSON on the request path. Blocking the loop stalls all concurrency.
- **Measure first, optimize second.** Profile with real data before changing code;
  the bottleneck is rarely where you guess. Optimizing unmeasured code wastes effort.
- **Stream large data, do not buffer it.** Process bytes as they arrive so memory and
  latency stay flat regardless of payload size.
- **Move CPU work off the loop.** Offload hashing, parsing, and compression to worker
  threads or native addons so request handling stays responsive.
- **Optimize the hot path, tolerate the cold one.** Spend effort where the profiler
  shows the time going; a slow admin endpoint that runs hourly does not matter.

## Best Practices

- Establish a baseline with a load test (`autocannon`, `k6`) and a flame graph
  (`node --prof` or `clinic flame`) before optimizing. Compare against it after.
- Keep per-request synchronous work under ~1ms. Replace `fs.readFileSync`,
  `crypto.pbkdf2Sync`, and `JSON.parse` on large bodies with async/streamed variants.
- Reuse expensive resources: a single connection pool, one HTTP agent with
  `keepAlive: true`, cached compiled regexes and schemas. Do not construct them per request.
- Cache computed results (in-process LRU or Redis) with an explicit TTL and bound.
  A hot query answered from cache is 100x cheaper than the database round trip.
- Batch and paginate I/O. Avoid N+1 queries; fetch in one round trip and stream
  large result sets rather than materializing them in memory.
- Prefer `await Promise.all([...])` for independent async calls so they overlap
  instead of running serially.
- Set explicit timeouts on every outbound call so one slow dependency cannot pin
  event-loop resources indefinitely.

## Examples

**Good Example** — concurrent I/O, offloaded CPU, bounded

```js
import { Worker } from "node:worker_threads";

async function handleReport(req) {
  // independent calls overlap instead of running one-after-another
  const [user, orders] = await Promise.all([
    db.getUser(req.userId),
    db.getOrders(req.userId), // single query, not one-per-order
  ]);

  // CPU-heavy PDF generation runs off the event loop, keeping the thread free
  return runInWorker("./pdf.js", { user, orders });
}
```

**Bad Example** — serial I/O and a blocked loop

```js
function handleReport(req) {
  const user = await db.getUser(req.userId);    // waits...
  const orders = [];
  for (const id of req.orderIds) {
    orders.push(await db.getOrder(id));         // N+1: serial round trips
  }
  // synchronous CPU work freezes the event loop for every other request
  return renderPdfSync(user, orders);
}
```

## Common Mistakes

- Using `*Sync` filesystem or crypto APIs on the request path.
- `await` in a loop for independent operations instead of `Promise.all`.
- N+1 query patterns that issue one database round trip per item.
- Buffering an entire upload/response in memory instead of streaming it.
- Optimizing code without a profile, "fixing" a path that was never the bottleneck.
- Creating a new DB connection or HTTP agent per request instead of pooling.
- No timeouts, so a stalled dependency slowly exhausts loop capacity.

## Production Tips

- Monitor event-loop lag (`perf_hooks.monitorEventLoopDelay`) as a first-class SLI;
  rising lag is the earliest signal of a blocking regression — see `nodejs/27-monitoring`.
- Enable gzip/brotli compression and HTTP keep-alive at the edge or in-process.
- Set `--max-semi-space-size` / `--max-old-space-size` deliberately for your heap
  profile rather than accepting defaults on large-memory hosts.
- Load-test in CI against the baseline and fail on p99 regressions.

## AI Review Checklist

- Is there any synchronous I/O or CPU-heavy work on the request path?
- Are independent async calls run concurrently with `Promise.all`?
- Is large data streamed rather than fully buffered in memory?
- Are connection pools, HTTP agents, and compiled schemas reused, not recreated?
- Is heavy CPU work offloaded to a worker thread?
- Does every outbound call have a timeout?
- Is the change justified by a profile / benchmark, not a guess?

## Related

- `knowledge/nodejs/02-event-loop.md`
- `knowledge/nodejs/06-streams.md`
- `knowledge/nodejs/12-worker-threads.md`
- `knowledge/nodejs/20-memory-management.md`
- `knowledge/nodejs/27-monitoring.md`
