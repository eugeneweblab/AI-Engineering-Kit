---
id: performance/01-performance-fundamentals
topic: performance
slug: performance-fundamentals
title: "Performance Fundamentals"
type: doc
order: 1
status: ready
tags: [performance, performance-fundamentals]
related: [performance/02-metrics, performance/16-profiling, performance/24-optimization-workflow, performance/03-cpu, performance/05-network]
when_to_use: "Read before any optimization work, to fix the mental model and the measure-first loop the rest of the topic assumes."
---
# Performance Fundamentals

## Purpose

This document defines the vocabulary and the method behind all performance work:
what latency and throughput mean, why the tail matters more than the average, and the
disciplined loop — measure, find the dominant cost, change one thing, re-measure — that
separates real optimization from guessing.

It answers "how do I *approach* a slow system?" rather than "how do I speed up X?". The
resource-specific docs ([CPU](03-cpu.md), [memory](04-memory.md),
[network](05-network.md)) assume you already think this way.

## Why It Matters

Most wasted performance effort comes from optimizing the wrong thing. Code *feels* slow,
an engineer rewrites the part they understand best, and the number does not move — because
the real cost was elsewhere. Optimization also carries risk: it adds complexity, caches,
and concurrency that create correctness bugs. So the cost of a wrong guess is doubled — no
speedup *and* more fragile code. A rigorous measure-first loop is what makes the effort pay
off and keeps the risk bounded.

## Core Principles

- **Measure before you optimize.** Intuition about hot spots is wrong more often than
  right. A profile or benchmark is the only admissible evidence.
- **Optimize the dominant cost (Amdahl's law).** If a section is 20% of runtime, making
  it infinitely fast caps your gain at 1.25x. Find the biggest slice first.
- **Latency ≠ throughput.** Latency is time per operation; throughput is operations per
  unit time. Batching improves throughput but usually *raises* per-item latency. Know
  which the requirement wants.
- **The tail is what users feel.** One request in a page load being at p99 makes the
  whole page feel at p99. Optimize percentiles, not the mean.
- **Work vs wait.** A slow request is either doing too much work (CPU/memory) or waiting
  (I/O, locks, network). The fix is completely different; identify which before touching
  code.
- **Change one thing at a time.** Two simultaneous changes make the measurement
  uninterpretable.

## Best Practices

- Establish a **baseline** measurement before the first change, and compare every change
  against it. "Faster" without a number is not a result.
- Reproduce the slowness in a **repeatable** scenario (a benchmark or load test) so
  results are not noise. See [profiling](16-profiling.md) and [benchmarking](19-benchmarking.md).
- State the **goal metric and target** up front: "reduce p95 checkout latency from 800ms
  to under 300ms." A [performance budget](23-performance-budget.md) makes this explicit.
- Prefer **algorithmic** wins (O(n²) → O(n log n)) over micro-optimizations; they scale
  with input size, micro-optimizations do not.
- Do the cheap structural fixes first: remove N+1 queries, add a missing index, stop
  redundant work. These usually dwarf hand-tuned inner loops.
- Stop when you hit the budget. Further optimization has a real cost (complexity) and
  diminishing return.

## Examples

**Good Example** — measure, then optimize the dominant cost

```python
import time

# Baseline first: profile shows 92% of time is in the per-row DB call, not the loop.
def total_price(order_ids: list[int]) -> int:
    # One query for all rows (dominant cost fixed) instead of one per id.
    rows = db.query(
        "SELECT id, price FROM orders WHERE id = ANY(%s)", (order_ids,)
    )
    return sum(r.price for r in rows)  # the loop was never the bottleneck
```

**Bad Example** — optimizing the visible-but-cheap part

```python
def total_price(order_ids: list[int]) -> int:
    total = 0
    for oid in order_ids:
        # "Optimized" with a tight loop and local var — but this line is an N+1
        # round-trip. The loop micro-tuning saves microseconds; each query costs ms.
        total += db.query("SELECT price FROM orders WHERE id = %s", (oid,)).price
    return total  # no baseline was taken, so nobody noticed the query dominates
```

## Common Mistakes

- Optimizing without a profile — fixing code that the profiler shows is under 1% of runtime.
- Reporting improvements with no baseline, so the "win" is unmeasurable or noise.
- Tuning the average when the requirement is about the p95/p99 tail.
- Confusing latency and throughput — adding batching to a latency-sensitive path.
- Micro-optimizing an O(n²) algorithm instead of replacing it.
- Premature optimization: complicating code before any measurement shows a need.
- Benchmarking in a debug build or a cold cache, producing numbers that do not reflect prod.

## Production Tips

- Keep the baseline and target in the PR description so reviewers can verify the claim.
- Wire a regression benchmark into CI for hot paths; a silent 2x slowdown is a defect.
- Warm up the JIT/cache before timing, and run enough iterations to beat noise.

## AI Review Checklist

- Is there a baseline measurement and an after measurement, both cited?
- Does a profile confirm the optimized code is the dominant cost?
- Is the goal (latency vs throughput, mean vs tail) stated and matched by the change?
- Was only one variable changed, so the result is interpretable?
- Is the optimization algorithmic where possible, not a micro-tune of a bad algorithm?
- Did tests still pass — was correctness preserved?

## Related

- `knowledge/performance/02-metrics.md`
- `knowledge/performance/16-profiling.md`
- `knowledge/performance/24-optimization-workflow.md`
- `knowledge/performance/03-cpu.md`
- `knowledge/performance/05-network.md`
