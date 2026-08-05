---
id: performance/30-engineering-principles
topic: performance
slug: engineering-principles
title: "Performance Engineering Principles"
type: doc
order: 30
status: ready
tags: [performance, engineering-principles, build_report, cache]
related: [performance/01-performance-fundamentals, performance/27-best-practices, performance/24-optimization-workflow, performance/23-performance-budget, performance/100-common-antipatterns]
when_to_use: "Read before making any decision that trades speed against complexity, correctness, or cost."
---
# Performance Engineering Principles

## Purpose

This document defines the durable principles that govern *how* to make performance
decisions — the reasoning an agent applies before caching a value, adding a worker,
rewriting a loop, or accepting a slow path. Techniques change with the runtime; these
principles decide when a technique earns its place. Read this before the resource-specific
docs ([CPU](03-cpu.md), [memory](04-memory.md), [caching](08-caching.md)); they tell you
*what* to do, this tells you *whether* and *why*.

## Why It Matters

Most performance damage is self-inflicted. An engineer optimizes the wrong thing, adds a
cache that serves stale data, or parallelizes a path that was never the bottleneck — and
now the code is faster in a benchmark, slower in production, and harder to reason about.
Performance work uniquely multiplies risk: every optimization adds complexity (caches,
concurrency, precomputation) that creates correctness bugs. A wrong guess costs twice — no
real speedup *and* a more fragile system. These principles keep the effort pointed at the
dominant cost and keep the added complexity honest.

## Core Principles

- **Measure before you optimize; measure after to prove it.** Intuition about hot spots is
  wrong more often than right. A profile is the only admissible evidence, and a before/after
  number is the only proof a change worked. The cost is a few minutes of instrumentation;
  the payoff is not spending days on code that was 1% of runtime.
- **Attack the dominant cost first (Amdahl's law).** Making a section that is 20% of
  runtime infinitely fast caps your gain at 1.25x. Find the biggest slice, fix that, then
  re-profile — the bottleneck moves after every fix.
- **Every optimization must pay rent in complexity.** Speed bought with a cache, a
  denormalized column, or hand-rolled concurrency is speed you must maintain and debug
  forever. Add it only when a measurement shows the simple version misses the target. The
  cost of the complex version is real; make the requirement justify it.
- **Correctness outranks speed, always.** A fast wrong answer is worthless. Never trade a
  correctness guarantee (consistency, ordering, precision) for latency without an explicit,
  written decision that the looser guarantee is acceptable.
- **Optimize the tail, not the average.** Users feel p95/p99, not the mean. A page that
  makes ten calls is as slow as its slowest call. Set targets on percentiles.
- **The fastest work is the work you don't do.** Before speeding up an operation, ask if it
  can be eliminated, cached, batched, or deferred. Removing work beats optimizing it.
- **Design for the data size you will have, not the one you tested with.** An O(n²) loop is
  invisible at n=100 and fatal at n=100,000. Choose algorithms and access patterns that
  scale with realistic growth.

## Best Practices

- Establish a **baseline** and a **target** before the first change: "cut p95 checkout from
  800ms to under 300ms." Without a number, "faster" is not a result. See
  [performance budget](23-performance-budget.md).
- Change **one thing at a time** and re-measure. Two simultaneous changes make the result
  uninterpretable.
- Prefer **algorithmic** wins (O(n²) → O(n log n)) over micro-tuning; they scale with input,
  constant-factor tweaks do not.
- Do the cheap structural fixes first: remove N+1 queries, add a missing index, stop
  redundant work. These usually dwarf any inner-loop tuning.
- Keep the hot path **allocation-light and cache-friendly** only after profiling proves it
  is hot; premature memory tuning obscures logic for no gain.
- **Stop at the budget.** Further optimization has diminishing return and a rising
  complexity cost. Ship when the target is met.

## Examples

**Good Example** — eliminate the work, then measure the win

```python
# Baseline: profile shows 90% of request time is recomputing the same report per call.
# Principle applied: the fastest work is work you don't do -> cache the derived result,
# keyed by inputs, with an explicit TTL so staleness is bounded and intentional.
@cache(ttl_seconds=60)  # bounded staleness is a written, accepted trade-off
def monthly_report(team_id: int, month: str) -> Report:
    return build_report(team_id, month)  # expensive; now runs once per minute, not per call
```

**Bad Example** — optimize the wrong thing, break correctness

```python
# Profiler was never run. Engineer "optimized" by caching forever with no key on month,
# so callers get last month's numbers -> a fast, confidently wrong answer.
_report = None
def monthly_report(team_id: int, month: str) -> Report:
    global _report
    if _report is None:                 # cached across teams AND months
        _report = build_report(team_id, month)
    return _report                      # correctness sacrificed for a speedup nobody measured
```

## Common Mistakes

- Optimizing without a profile — tuning code the profiler shows is under 1% of runtime.
- Reporting a "win" with no baseline, so it is unmeasurable or just noise.
- Trading a correctness guarantee for latency without writing down the decision.
- Adding a cache with no invalidation or TTL, converting a speed problem into a staleness bug.
- Micro-optimizing an O(n²) algorithm instead of replacing it.
- Premature optimization: complicating code before any measurement shows a need.
- Testing at toy data sizes, so an algorithm that scales quadratically looks fine.

## Production Tips

- Keep the baseline, target, and after-number in the PR description so a reviewer can verify
  the claim rather than trust it.
- Wire a regression benchmark into CI for hot paths; a silent 2x slowdown is a defect that
  no test will catch (see [benchmarking](19-benchmarking.md)).
- When two goals conflict (latency vs throughput, freshness vs cost), state which you
  prioritized and why, so the trade-off is auditable in [review](29-performance-review.md).

## AI Review Checklist

- Is there a baseline and an after measurement, both cited, and does a profile confirm the
  optimized code was the dominant cost?
- Does every added cache, denormalization, or concurrency construct point at a measured
  bottleneck, and does it have bounded, correct invalidation?
- Was any correctness guarantee weakened for speed? If so, is that decision written down?
- Are targets set on the tail (p95/p99), not the mean?
- Is the algorithm chosen for realistic data size, not the test fixture's size?
- Was only one variable changed, so the result is interpretable, and did tests still pass?

## Related

- `knowledge/performance/01-performance-fundamentals.md`
- `knowledge/performance/27-best-practices.md`
- `knowledge/performance/24-optimization-workflow.md`
- `knowledge/performance/23-performance-budget.md`
- `knowledge/performance/100-common-antipatterns.md`
