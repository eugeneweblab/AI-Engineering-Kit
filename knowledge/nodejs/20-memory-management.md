---
id: nodejs/20-memory-management
topic: nodejs
slug: memory-management
title: "Node.js Memory Management"
type: doc
order: 20
status: ready
tags: [nodejs, memory-management]
related: [nodejs/19-performance, nodejs/06-streams, nodejs/07-buffers, nodejs/22-debugging, nodejs/27-monitoring]
when_to_use: "Read when a Node.js process grows in memory over time, OOM-crashes, or before handling large payloads."
---
# Node.js Memory Management

## Purpose

This document defines how memory works in a Node.js process and how to keep it
bounded. V8 manages the JavaScript heap with a garbage collector, but "garbage
collected" does not mean "leak proof": any value still referenced is never freed.
This doc covers the heap model, the reference patterns that cause leaks, native
memory outside the heap (Buffers), and how to diagnose growth with a heap snapshot.

## Why It Matters

A Node process has a hard heap ceiling (~2GB by default on 64-bit, set by
`--max-old-space-size`). Cross it and the process does not slow down — V8 aborts with
a fatal `JavaScript heap out of memory` and the process dies mid-request. Leaks are
insidious: the app runs fine in tests and for hours in production, then a slow drift
crashes it at 3am under real traffic. Because the failure is delayed and total,
memory discipline is not optional for long-lived services.

## Core Principles

- **Bound every collection.** Caches, queues, and maps that only grow are leaks with
  a delay. Give each an explicit maximum size or TTL and an eviction policy.
- **Understand what keeps a reference alive.** A value survives GC while any live
  object points at it — a module-level array, a closure, an unremoved listener.
- **Stream large data; never hold it all.** Buffering a big file or response in memory
  scales linearly with payload and will eventually OOM. Streams keep memory flat.
- **Buffers live outside the JS heap.** `Buffer` allocations are native memory, not
  bounded by `--max-old-space-size`; leaking them exhausts RSS, not the heap.
- **Diagnose with snapshots, not guesses.** Two heap snapshots and a diff show exactly
  which retained objects grow. Reasoning about leaks without data is a coin flip.

## Best Practices

- Use a bounded cache (`lru-cache` with `max`/`maxSize`/`ttl`), never a plain
  `Map` or object that accumulates keys for the process lifetime.
- Remove event listeners you add (`emitter.off`, `AbortController` for one-shots).
  Every `on` without a matching `off` on a long-lived emitter is a slow leak.
- Prefer `WeakMap`/`WeakRef` for caches keyed by objects so entries are collectible
  when the key is gone. Do not use them to keep things alive — that is backwards.
- Stream file and network I/O with `pipeline`; do not `readFile` a large file into a
  Buffer or accumulate chunks into one big array. See `nodejs/06-streams`.
- Set `--max-old-space-size` to match the container memory limit so V8's GC pressure
  matches reality, and trigger GC-friendly design rather than raising the ceiling to hide a leak.
- Watch `process.memoryUsage()` (`heapUsed`, `rss`, `external`) and alert on sustained
  upward slope, not just absolute value.

## Examples

**Good Example** — bounded cache, streamed I/O, cleaned-up listener

```js
import { LRUCache } from "lru-cache";
import { pipeline } from "node:stream/promises";
import { createReadStream, createWriteStream } from "node:fs";

// hard cap: at most 500 entries or 50MB, whichever comes first, with a TTL
const cache = new LRUCache({ max: 500, maxSize: 50_000_000, ttl: 60_000 });

async function copyLarge(src, dst) {
  // constant memory regardless of file size — chunks flow through, none retained
  await pipeline(createReadStream(src), createWriteStream(dst));
}
```

**Bad Example** — unbounded growth and full-file buffering

```js
const cache = new Map(); // never evicts → grows until OOM

function remember(key, value) {
  cache.set(key, value); // one entry per unique key, forever
}

async function copyLarge(src, dst) {
  const data = await fs.readFile(src); // whole file into one Buffer → OOM on big files
  await fs.writeFile(dst, data);
}
```

## Common Mistakes

- Module-level `Map`/array/object used as a cache with no size limit or eviction.
- Adding listeners in a request handler without removing them, leaking closures.
- `readFile`/`JSON.stringify` on large data, holding the whole payload in the heap.
- Raising `--max-old-space-size` to "fix" a leak instead of finding it — this only
  delays the crash and enlarges the eventual failure.
- Assuming `Buffer` memory counts against the JS heap; it exhausts RSS separately.
- Global caches that key on request/user data, so cardinality grows without bound.

## Production Tips

- Capture heap snapshots on demand in production (`v8.writeHeapSnapshot()` behind an
  admin guard, or a `SIGUSR2` handler) and diff two of them to find the growing retainer.
- Use `--heapsnapshot-near-heap-limit=2` to auto-dump a snapshot just before an OOM crash.
- Track RSS and `external` memory, not just heap, so Buffer/native leaks are visible.
- Set container memory limits and let the orchestrator restart on OOM as a safety net —
  but treat every OOM restart as a bug to fix, not normal operation.

## AI Review Checklist

- Does every cache/queue/map have an explicit size bound or TTL and eviction?
- Are all added event listeners removed, or scoped with `AbortController`?
- Is large file/network data streamed instead of fully buffered?
- Are object-keyed caches using `WeakMap`/`WeakRef` where appropriate?
- Is `--max-old-space-size` aligned with the container limit (not inflated to mask a leak)?
- Is there monitoring on memory *slope* over time, including RSS and `external`?
- Is there a way to capture a heap snapshot from production for diagnosis?

## Related

- `knowledge/nodejs/19-performance.md`
- `knowledge/nodejs/06-streams.md`
- `knowledge/nodejs/07-buffers.md`
- `knowledge/nodejs/22-debugging.md`
- `knowledge/nodejs/27-monitoring.md`
