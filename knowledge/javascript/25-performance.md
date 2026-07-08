---
id: javascript/25-performance
topic: javascript
slug: performance
title: "Performance"
type: doc
order: 25
status: ready
tags: [javascript, performance]
related: [javascript/10-event-loop, javascript/15-memory-management, javascript/08-asynchronous-javascript, javascript/27-browser-performance, javascript/24-testing]
when_to_use: "Read before optimizing JavaScript execution speed, throughput, or memory in Node or the browser."
---
# Performance

## Purpose

This document defines how to make JavaScript fast where it matters: algorithmic cost,
allocation and garbage-collection pressure, avoiding event-loop blocking, and doing less
work overall. It covers *language- and runtime-level* performance (Node and the engine);
rendering, layout, and network cost live in
[browser performance](27-browser-performance.md). It is written so an agent optimizes
based on measurement, not folklore.

## Why It Matters

Slow code is a correctness problem in disguise. A synchronous loop that blocks the event
loop stalls *every* concurrent request, not just the slow one. An unbounded cache leaks
memory until the process is OOM-killed. An O(n²) join looks fine on ten rows and melts on
ten thousand. Performance work has a sharp asymmetry: a few hot paths dominate the cost,
and micro-optimizing everything else wastes effort while obscuring the real bottleneck.
Measure first, or you optimize the wrong thing.

## Core Principles

- **Measure before you optimize.** Profile with real data (`node --prof`, `--cpu-prof`,
  Chrome DevTools). Intuition about JavaScript hot spots is usually wrong. The cost of
  guessing is a rewrite that changes nothing.
- **Algorithm beats micro-optimization.** Fixing O(n²) → O(n) dwarfs any constant-factor
  loop trick. Reach for a `Map`/`Set` before you tune a `for` loop.
- **Never block the event loop.** Long synchronous work (big loops, sync crypto, JSON on
  megabytes) freezes all concurrency. Break it up, defer it, or move it off-thread.
- **Allocation is not free.** Every object and closure is future GC work. In hot paths,
  reuse buffers and avoid creating garbage per iteration.
- **Do the work once.** Cache pure, expensive results — but bound the cache, or you have
  built a memory leak.

## Best Practices

- Use `Map`/`Set` for membership and keyed lookup (O(1)); reserve `Array.includes`/`indexOf`
  (O(n)) for small, cold arrays.
- Offload CPU-bound work to a **Worker thread** (Node `worker_threads`) or **Web Worker**
  so the main loop stays responsive.
- Stream large payloads (`ReadableStream`, Node streams) instead of buffering the whole
  thing into memory.
- Batch and coalesce I/O and network calls; use `Promise.all` for independent async work
  instead of awaiting serially.
- Memoize pure functions with a **bounded** cache (LRU); never an unbounded plain object
  keyed by user input.
- Prefer built-in, engine-optimized methods; avoid rebuilding arrays repeatedly inside a
  loop (`arr = [...arr, x]` in a loop is O(n²)).
- Set `AbortController` timeouts on outbound work so a slow dependency cannot pin resources.

## Examples

**Good Example** — O(n) lookup, parallel independent I/O

```js
// Build an index once: O(n). Lookups are then O(1).
const usersById = new Map(users.map((u) => [u.id, u]));
const enriched = orders.map((o) => ({ ...o, user: usersById.get(o.userId) }));

// Independent async calls run concurrently, not one-after-another.
const [profile, settings] = await Promise.all([
  loadProfile(id),   // these do not depend on each other,
  loadSettings(id),  // so awaiting them serially would double the latency
]);
```

**Bad Example** — O(n²) join, serial awaits, event-loop block

```js
const enriched = orders.map((o) => ({
  ...o,
  user: users.find((u) => u.id === o.userId), // .find scans all users per order → O(n·m)
}));

const profile = await loadProfile(id);
const settings = await loadSettings(id);      // waits for profile first for no reason

let total = 0;
for (let i = 0; i < 5_000_000_000; i++) total += i; // sync megaloop freezes the whole event loop
```

## Common Mistakes

- Optimizing before profiling, so effort lands on cold code.
- Nested `.find`/`.filter`/`.includes` creating hidden O(n²) work.
- `await` inside a loop for independent calls instead of `Promise.all`.
- Blocking the event loop with synchronous crypto, `JSON.parse` on huge strings, or big loops.
- Unbounded caches and memoization keyed by user input — a slow memory leak.
- Rebuilding arrays/objects with spread inside a loop, turning O(n) into O(n²).
- Premature micro-optimizations that hurt readability with no measured gain.

## Production Tips

- Load-test with production-shaped data volumes; small datasets hide quadratic behavior.
- Expose event-loop lag as a metric (e.g. `perf_hooks.monitorEventLoopDelay`) and alert on it —
  rising lag is the earliest sign of a blocking hot path.
- Capture CPU and heap profiles from production periodically; regressions are easier to see
  in a flame graph than in code review.

## AI Review Checklist

- Was a profiler used, or is the optimization a guess?
- Are keyed lookups done with `Map`/`Set` rather than repeated array scans?
- Do independent async operations run via `Promise.all` instead of serial `await`?
- Is CPU-bound work kept off the event loop (workers, chunking, streaming)?
- Are caches and memoization bounded (LRU/TTL), not unbounded on user input?
- Are large payloads streamed rather than buffered fully into memory?
- Do micro-optimizations have a measured justification, or do they just hurt readability?

## Related

- `knowledge/javascript/10-event-loop.md`
- `knowledge/javascript/15-memory-management.md`
- `knowledge/javascript/08-asynchronous-javascript.md`
- `knowledge/javascript/27-browser-performance.md`
- `knowledge/javascript/24-testing.md`
