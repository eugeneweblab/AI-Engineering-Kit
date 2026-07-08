---
id: performance/26-debugging
topic: performance
slug: debugging
title: "Performance Debugging"
type: doc
order: 26
status: ready
tags: [performance, debugging]
related: [performance/16-profiling, performance/25-production-monitoring, performance/24-optimization-workflow, performance/13-database-performance, performance/14-api-performance]
when_to_use: "Read when a system is slow and you need to find and confirm the root cause instead of guessing at fixes."
---
# Performance Debugging

## Purpose

This document defines how to diagnose a performance problem: how to reproduce it,
localize it to a component, confirm the root cause with evidence, and prove the fix. It is
written so an agent debugs slowdowns methodically rather than applying speculative fixes
that hide symptoms or move the bottleneck.

Performance debugging is a search: narrow "the system is slow" down to "this span, on this
input, for this reason." The discipline is refusing to change code until the evidence
points at a specific cause.

## Why It Matters

Slow is not broken, so performance bugs evade the tests and error alerts that catch
crashes. They are also intermittent — visible only under real load, real data, or a cold
cache — which makes them easy to "fix" by coincidence and hard to fix for real. A
speculative change that appears to help often just shifts the bottleneck or masks it until
traffic grows. Evidence-driven debugging is what separates a durable fix from a lucky one,
and it produces the before/after proof a reviewer needs.

## Core Principles

- **Reproduce before you fix.** A bug you cannot trigger on demand cannot be confirmed
  fixed. Pin the input, load, and environment that make it slow.
- **Bisect the request path.** Split the end-to-end time into stages (network, queue, app,
  DB) and measure each; the slow stage is where you dig next.
- **Follow the evidence, not the hunch.** Let a profile or trace point at the hotspot.
  Intuition names the wrong function most of the time.
- **Change one variable.** Isolate each hypothesis so a result is attributable. Multiple
  simultaneous changes destroy the signal.
- **Confirm with a measurement.** The fix is proven only when the same reproduction shows
  the metric back within budget and no new bottleneck appeared.

## Best Practices

- Build a **minimal, deterministic repro**: fixed input size, warmed or explicitly cold
  cache, representative concurrency. Note which of these is the trigger.
- Use a **trace first** to find the slow span, then a **profiler** to find the slow line
  within it. Top-down localization beats reading code. See [profiling](16-profiling.md).
- Distinguish **latency vs throughput** problems: a slow single request (algorithm, I/O
  wait) is different from a system that collapses under concurrency (contention, pool
  exhaustion, GC). The fixes are different.
- Check the usual heavy hitters explicitly: **N+1 queries, missing indexes, unbounded
  result sets, serial I/O that could be parallel, lock/pool contention, and GC pauses.**
- Compare a slow case against a **fast baseline** of the same operation to isolate the
  delta rather than reading absolute numbers cold.
- When production-only, use tracing and sampling profilers **in production**; do not try
  to reproduce a distributed timing bug entirely on a laptop.
- Revert speculative changes that do not move the measured number — they are noise and
  future confusion.

## Examples

**Good Example** — localize with a trace, confirm the cause, verify

```python
# Symptom: /orders p99 = 4.2 s. Trace shows 3.8 s inside get_line_items,
# split across 200 near-identical SELECTs -> classic N+1 on the DB stage.
def get_line_items(order_ids):
    # Hypothesis: N+1. Fix = one batched query. Change ONE thing.
    rows = db.query(
        "SELECT * FROM line_items WHERE order_id = ANY(%s)", [order_ids]
    )
    grouped = defaultdict(list)
    for r in rows:
        grouped[r.order_id].append(r)
    return grouped
    # Verify on the same repro: /orders p99 = 210 ms, DB stage now 40 ms.
    # Root cause confirmed, fix proven, no new hotspot in the trace.
```

**Bad Example** — speculative fix, no reproduction, masked symptom

```python
def get_line_items(order_ids):
    # "Maybe it's the DB being slow", so a cache was bolted on without a trace.
    key = tuple(order_ids)
    if key in _cache:                 # helps only on exact-repeat inputs
        return _cache[key]
    result = {i: fetch_items(i) for i in order_ids}  # N+1 still runs every miss
    _cache[key] = result              # unbounded cache -> new memory bug
    return result
    # The p99 was never reproduced or re-measured; the N+1 remains, and a
    # memory leak was added. The "fix" hides the symptom on warm paths only.
```

## Common Mistakes

- Fixing before reliably reproducing, so the fix can never be confirmed.
- Trusting a hunch about the slow function instead of a trace or profile.
- Confusing a latency problem (slow single request) with a throughput problem
  (contention under load) and applying the wrong remedy.
- Adding a cache to hide a slow query instead of fixing the query, creating a new memory
  or staleness bug.
- Changing several things at once, making the result unattributable.
- Debugging a production-only issue solely on a laptop that lacks the real load and data.
- Declaring victory without re-measuring against the original reproduction.

## Production Tips

- Keep sampling profilers and continuous tracing enabled in production so intermittent
  slowdowns are captured when they happen, not re-created later.
- Save the reproduction (input, load script, env) as a regression test so the bug cannot
  return silently. Tie it to [optimization workflow](24-optimization-workflow.md).
- When a slowdown correlates with a deploy, bisect by version first — it is often faster
  than reading code.

## AI Review Checklist

- Is there a deterministic reproduction of the slowdown before any fix?
- Was the slow stage localized with a trace/profile rather than guessed?
- Is the problem correctly classified as latency vs throughput?
- Does the fix address the root cause, not mask the symptom?
- Was exactly one variable changed per hypothesis?
- Is the improvement confirmed against the same reproduction, with no new hotspot?
- Is the reproduction captured as a regression test?

## Related

- `knowledge/performance/16-profiling.md`
- `knowledge/performance/25-production-monitoring.md`
- `knowledge/performance/24-optimization-workflow.md`
- `knowledge/performance/13-database-performance.md`
- `knowledge/performance/14-api-performance.md`
