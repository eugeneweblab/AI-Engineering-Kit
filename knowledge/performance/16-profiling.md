---
id: performance/16-profiling
topic: performance
slug: profiling
title: "Profiling"
type: doc
order: 16
status: ready
tags: [performance, profiling, save, load_fixture, Profile, transform]
related: [performance/01-performance-fundamentals, performance/02-metrics, performance/17-monitoring, performance/03-cpu, performance/19-benchmarking]
when_to_use: "Read before optimizing any code, to locate the real bottleneck instead of guessing at it."
---
# Profiling

## Purpose

This document defines how to find *where* time and memory actually go before you
change any code. It covers the kinds of profiler (sampling vs instrumenting, CPU vs
allocation), how to read a flame graph, and the discipline of profiling under
realistic conditions. It is written so an agent optimizes the dominant cost instead of
the cost it assumed.

Profiling is the measurement half of every optimization. The
[fundamentals](01-performance-fundamentals.md) doc explains *why* to measure first;
this doc explains *how*. It works on code you can run; for production systems you
cannot pause, see [monitoring](17-monitoring.md).

## Why It Matters

Human intuition about performance is reliably wrong. The hot path is almost never the
code that looks expensive — it is a chatty logger, a repeated serialization, a lock
nobody suspected. Optimizing without a profile means optimizing the wrong thing:
effort is spent, complexity is added, and the number does not move. Amdahl's law makes
this concrete — making 5% of the runtime ten times faster saves under 5% overall. A
profile replaces a guess with a measured ranking of costs, so the first fix you make
is the one that matters. Every hour of profiling saves days of misdirected optimization.

## Core Principles

- **Profile before you optimize, always.** Without a profile you are guessing which
  line is slow, and you will usually guess wrong. A profile is not optional overhead;
  it is the input to the work.
- **Optimize the top of the profile.** Rank costs and fix the largest first. The tail
  of small costs is not worth the complexity of touching it.
- **Profile a realistic workload.** A profile of an empty database or a warm cache
  measures the wrong system. Use production-like data, size, and concurrency.
- **Measure the same thing before and after.** A speedup is only real if the same
  benchmark, on the same input, shows it. Confirm, do not assume.
- **Separate wall-clock from CPU time.** High wall time with low CPU means you are
  *waiting* (I/O, locks), not *computing* — a completely different fix.

## Best Practices

- Choose the right profiler for the cost: a **CPU/sampling** profiler for compute
  hot paths, an **allocation/heap** profiler for [memory](04-memory.md), and
  distributed **tracing** for time spread across services.
- Prefer **sampling profilers** in production-like settings — they add low overhead;
  instrumenting profilers are precise but perturb the very timing you measure.
- Read a **flame graph** by width, not color: the widest frames are where time is
  spent. Look for one wide frame (a hot function) or many repeated narrow ones (a hot
  loop or N+1).
- Capture a **baseline number** first, make **one** change, re-profile, and keep the
  change only if the number improved measurably.
- Watch for **wait**, not just work: a request that is slow with the CPU idle points at
  I/O, a lock, or a serial [network](05-network.md) round-trip, not an algorithm.
- Profile with **realistic data volume and concurrency**; contention and cache misses
  only appear under load, and they are often the real bottleneck.

## Examples

**Good Example** — measure, isolate, verify

```python
import cProfile, pstats

# Profile a realistic workload, then rank by cumulative time to find the hot path.
with cProfile.Profile() as pr:
    process_orders(load_fixture("prod_like_10k.json"))   # production-like input

stats = pstats.Stats(pr).sort_stats("cumulative")
stats.print_stats(10)   # top 10 costs — optimize the frame at the top, not a guess
# Change ONE thing, rerun the SAME workload, compare the top frame's time.
```

**Bad Example** — guessing and micro-optimizing

```python
# No profile was run. The author "knew" the loop was slow and rewrote it with a
# clever comprehension, adding complexity for a frame that was 2% of runtime.
result = [transform(x) for x in items]   # optimized the wrong 2%

# Meanwhile the real cost — a JSON re-serialization inside `save()` called per item —
# was 70% of the time and never looked at, because nobody measured.
for item in result:
    save(item)   # unprofiled hot path: the actual bottleneck, untouched
```

## Common Mistakes

- Optimizing from intuition without ever running a profiler.
- Profiling an unrealistic workload (empty data, warm cache, single request) and
  optimizing costs that do not exist in production.
- Reading flame graphs by color instead of width, missing the widest frame.
- Changing several things at once, so no single change can be credited or reverted.
- Ignoring wait time — chasing CPU when the request is actually blocked on I/O.
- Trusting an instrumenting profiler's absolute numbers when its overhead distorts them.
- Declaring victory without re-measuring the same benchmark to confirm the gain.

## Production Tips

- Use a **continuous / always-on** profiler (low-overhead sampling) in production to
  catch regressions and rare hot paths that never reproduce locally.
- Keep saved profiles and flame graphs alongside the change that fixed them, so the
  next regression starts from evidence, not from scratch.
- Pair profiling with [benchmarking](19-benchmarking.md): the profile finds the hot
  spot, the benchmark proves the fix and guards against regression.

## AI Review Checklist

- Was a profiler run to locate the bottleneck before any code was changed?
- Was the profile taken on a production-like workload, data size, and concurrency?
- Is the change aimed at the top of the profile, not a small or assumed cost?
- Was wall-clock separated from CPU time to tell "waiting" from "computing"?
- Was exactly one change made, then the same benchmark re-run to confirm the gain?
- Is there a saved baseline and after number proving the improvement is real?

## Related

- `knowledge/performance/01-performance-fundamentals.md`
- `knowledge/performance/02-metrics.md`
- `knowledge/performance/17-monitoring.md`
- `knowledge/performance/03-cpu.md`
- `knowledge/performance/19-benchmarking.md`
