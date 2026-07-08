---
id: performance/03-cpu
topic: performance
slug: cpu
title: "CPU"
type: doc
order: 3
status: ready
tags: [performance, cpu]
related: [performance/01-performance-fundamentals, performance/16-profiling, performance/04-memory, performance/15-query-optimization, performance/19-benchmarking]
when_to_use: "Read when a profile shows work (not waiting) dominates — hot loops, high CPU, or a compute-bound path."
---
# CPU

## Purpose

This document covers compute-bound performance: reducing the *work* a program does per
request. It addresses algorithmic complexity, hot paths, redundant computation, and using
concurrency correctly. Apply it only after a [profile](16-profiling.md) shows the process
is CPU-bound — i.e. burning cycles, not waiting on I/O.

The single biggest CPU win is almost always doing less work, not doing the same work
faster.

## Why It Matters

CPU is the resource where bad algorithms hide until the input grows. Code that is instant
on 100 rows in a test can lock a core for seconds on 100,000 rows in production, and the
failure is sudden — an O(n²) path degrades gracefully right up until it doesn't. CPU is
also the resource you pay for directly at scale: halving CPU per request can halve the
fleet. Getting the complexity class and the hot path right is high-leverage and cheap
compared to renting more machines.

## Core Principles

- **Complexity class beats constant factors.** Replacing O(n²) with O(n log n) scales
  with the input; a hand-tuned inner loop does not. Fix the algorithm first.
- **Do less work.** The fastest computation is the one you skip — memoize, cache, dedupe,
  and short-circuit before you micro-optimize.
- **The hot path is small.** Profiles are lopsided: a few functions dominate. Optimize
  those and ignore the rest.
- **CPU-bound vs I/O-bound needs different tools.** Threads help I/O-bound work; for
  CPU-bound work in a GIL/single-threaded runtime you need multiple processes or native
  code, not more threads.
- **Batch and vectorize.** Per-item overhead (function calls, boxing, allocation)
  dominates tight loops; operating on batches amortizes it.
- **Cache-friendly beats cache-hostile.** Contiguous data and predictable access are far
  faster than pointer-chasing at the same complexity — see [memory](04-memory.md).

## Best Practices

- Profile with a sampling CPU profiler and optimize only the functions in the top of the
  flame graph. See [profiling](16-profiling.md).
- Hoist invariant work **out of loops**: compile a regex once, resolve a lookup once,
  precompute constants.
- Replace repeated linear scans with the right **data structure** — a set/hash for
  membership, a map for lookup — turning O(n) into O(1).
- **Memoize** pure, expensive functions and cache results of repeated identical calls.
- For CPU-bound parallelism, use a **process pool** (or native/SIMD code) sized to core
  count; measure — parallel overhead can lose on small inputs.
- Keep hot loops **allocation-free** and branch-predictable; move error handling and
  logging off the hot path.
- Re-benchmark after each change; some "optimizations" are slower on real data.

## Examples

**Good Example** — right data structure turns O(n·m) into O(n)

```python
def tag_active(users: list[User], active_ids: list[int]) -> None:
    active = set(active_ids)          # build once: O(m), membership is O(1)
    for u in users:
        u.active = u.id in active     # O(1) per user → O(n) total
```

**Bad Example** — quadratic scan hidden inside a loop

```python
def tag_active(users: list[User], active_ids: list[int]) -> None:
    for u in users:
        # `in` on a list is O(m); nested in the O(n) loop this is O(n*m).
        # Fine for 100 rows in a test, locks a core at 100k users in prod.
        u.active = u.id in active_ids
```

## Common Mistakes

- Micro-optimizing constants while leaving an O(n²) or worse algorithm in place.
- Membership tests against a list instead of a set, creating hidden quadratic loops.
- Recompiling regexes, re-parsing config, or rebuilding lookups inside a loop.
- Adding threads to a CPU-bound, GIL-limited program and expecting parallelism.
- Recomputing pure, expensive results instead of memoizing them.
- Doing work eagerly that is often thrown away, instead of computing lazily.
- Optimizing a cold path the profiler shows is negligible.

## Production Tips

- Add a benchmark for the hot function to CI so an accidental complexity regression fails
  the build. See [benchmarking](19-benchmarking.md).
- For heavy compute, consider offloading to a background job or a native extension rather
  than blocking the request thread.
- Watch CPU saturation (run-queue length), not just utilization; a saturated core queues
  work and inflates the latency tail.

## AI Review Checklist

- Is the algorithm's complexity class appropriate for the expected input size?
- Are membership/lookup operations using sets/maps rather than linear scans in a loop?
- Is invariant work hoisted out of hot loops (compiled regex, precomputed values)?
- Are pure, expensive computations memoized or cached?
- Does concurrency match the workload (processes/native for CPU-bound, not just threads)?
- Is there a profile confirming this code is actually the CPU hot path?

## Related

- `knowledge/performance/01-performance-fundamentals.md`
- `knowledge/performance/16-profiling.md`
- `knowledge/performance/04-memory.md`
- `knowledge/performance/15-query-optimization.md`
- `knowledge/performance/19-benchmarking.md`
