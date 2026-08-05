---
id: performance/04-memory
topic: performance
slug: memory
title: "Memory"
type: doc
order: 4
status: ready
tags: [performance, memory, open]
related: [performance/03-cpu, performance/16-profiling, performance/01-performance-fundamentals, performance/26-debugging, performance/09-lazy-loading]
when_to_use: "Read when memory grows unbounded, GC pauses spike latency, or allocation shows up as a hot cost in a profile."
---
# Memory

## Purpose

This document covers memory performance: controlling how much a program allocates, avoiding
leaks and unbounded growth, reducing garbage-collection pressure, and keeping data
cache-friendly. It applies to both managed runtimes (GC pauses, retained heaps) and manual
ones (leaks, fragmentation).

Memory problems show up two ways: the process *grows* until it is killed, or *allocation
and GC* steal CPU and inflate the latency tail. This doc addresses both.

## Why It Matters

Memory failures are the ones that page you at 3 a.m. A slow leak looks perfectly healthy in
a code review and in a short test, then the container OOM-kills days later under real
traffic — losing in-flight requests with it. Even without a leak, allocation is rarely
free: in a GC runtime, high allocation rate means frequent collections, and GC pauses land
directly on p99 latency. Controlling memory is both a stability requirement and a latency
lever.

## Core Principles

- **Bounded by design.** Any collection, cache, queue, or buffer that grows with input
  must have an explicit cap or eviction policy. Unbounded is a leak waiting to happen.
- **Allocation is a cost.** Fewer, larger allocations beat many small ones. In GC runtimes,
  allocation rate drives pause frequency more than live-heap size does.
- **Stream, don't slurp.** Process large inputs incrementally; never load a whole file,
  result set, or upload into memory at once.
- **Retention is the enemy.** A leak is unintended retention — a reference that outlives its
  use (caches, closures, event listeners, module globals). Release references promptly.
- **Locality is speed.** Contiguous, compact data (arrays of values) trounces
  pointer-chasing (linked structures) because of CPU cache behavior — same complexity,
  very different real time.
- **Copy vs share deliberately.** Defensive copies cost memory and CPU; shared mutable
  state costs correctness. Choose on purpose.

## Best Practices

- Give every cache a **max size and TTL/eviction** (LRU). An unbounded cache is a leak.
- **Stream** large I/O: iterate rows/chunks with generators or cursors instead of
  materializing full lists. See [lazy-loading](09-lazy-loading.md).
- Reuse buffers and objects on hot paths (pools) instead of allocating per iteration, when
  a profile shows allocation dominates.
- Remove listeners, timers, and subscriptions on teardown; unregister what you register.
- Avoid capturing large objects in long-lived closures or module-level globals.
- Prefer compact, columnar, or primitive-typed structures for large datasets over arrays
  of heap objects.
- Track **RSS and heap over time** in load tests; a rising sawtooth that never returns to
  baseline is a leak.

## Examples

**Good Example** — streaming, bounded memory

```python
def sum_amounts(path: str) -> int:
    total = 0
    with open(path) as f:
        for line in f:                 # one line in memory at a time → O(1) memory
            total += int(line.split(",")[3])
    return total
```

**Bad Example** — slurps the whole file and leaks via an unbounded cache

```python
_CACHE = {}                            # module global, never evicted → grows forever

def sum_amounts(path: str) -> int:
    rows = open(path).read().splitlines()   # entire file in RAM → OOM on big input
    _CACHE[path] = rows                      # retains every file ever read (leak)
    return sum(int(r.split(",")[3]) for r in rows)
```

## Common Mistakes

- Caches, maps, or queues with no size bound or eviction — the most common leak.
- Reading an entire file, HTTP body, or query result into memory instead of streaming.
- Forgetting to remove event listeners/timers, retaining whole object graphs.
- Long-lived closures or globals capturing large or per-request data.
- Blaming the GC for pauses caused by a high allocation rate the code creates.
- Fetching `SELECT *` and hydrating full objects when only two fields are used.

## Production Tips

- Set container memory limits and alert on RSS approaching them *before* the OOM-killer
  fires; a graph trending up is an early warning.
- Capture a heap snapshot/dump on high memory and diff retained sizes to find the
  retaining reference. See [debugging](26-debugging.md).
- Run a soak test (steady load for hours) to expose slow leaks a short test hides.
- Tune GC only after profiling; most "GC problems" are really allocation-rate problems in
  application code.

## AI Review Checklist

- Does every cache, buffer, or queue that grows with input have a bound or eviction?
- Are large files/result sets/uploads streamed rather than fully materialized?
- Are listeners, timers, and subscriptions cleaned up on teardown?
- Do long-lived closures or globals avoid capturing large or per-request objects?
- Is the allocation rate on hot paths minimized where a profile shows it dominates?
- Are only the needed fields fetched and retained, not full objects?

## Related

- `knowledge/performance/03-cpu.md`
- `knowledge/performance/16-profiling.md`
- `knowledge/performance/01-performance-fundamentals.md`
- `knowledge/performance/26-debugging.md`
- `knowledge/performance/09-lazy-loading.md`
