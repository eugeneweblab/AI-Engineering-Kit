---
id: performance/24-optimization-workflow
topic: performance
slug: optimization-workflow
title: "Optimization Workflow"
type: doc
order: 24
status: ready
tags: [performance, optimization-workflow]
related: [performance/16-profiling, performance/19-benchmarking, performance/02-metrics, performance/23-performance-budget, performance/29-performance-review]
when_to_use: "Read before starting any performance optimization so you measure, target, and verify instead of guessing."
---
# Optimization Workflow

## Purpose

This document defines the disciplined loop for making software faster: how to decide
*whether* to optimize, *what* to optimize, and how to *prove* the change worked. It is
written so an agent can improve real performance without churning code, hiding
regressions, or optimizing the wrong thing.

Optimization is a measurement problem before it is a coding problem. The workflow —
measure, target, change, verify — exists to keep every change tied to evidence.

## Why It Matters

Optimizing without data is guessing, and guesses are usually wrong: the slow part is
rarely where intuition points. Worse, "optimizations" have real costs — they add
complexity, obscure intent, and can introduce correctness bugs. A change that saves 2%
on code that runs 0.1% of the time is a net loss: you paid in readability and got nothing
measurable back. The workflow protects you from spending effort where it does not move a
user-visible metric, and it produces a before/after number you can defend in review.

## Core Principles

- **Measure first, always.** Never change code for speed without a profile or benchmark
  that identifies the actual bottleneck. See [profiling](16-profiling.md).
- **Optimize the critical path.** Amdahl's Law: total speedup is capped by the fraction
  of time you actually touch. Attack the biggest contributor to the slow path first.
- **One change at a time.** Batch edits make it impossible to attribute a delta. Isolate
  each change so you know what caused the result.
- **Set a target before you start.** "Fast enough" is a number (a budget or SLO), not a
  feeling. Stop when you hit it; over-optimizing past the target is waste.
- **Verify against a baseline.** A change is not done until a repeatable measurement shows
  the improvement and confirms no regression elsewhere.

## Best Practices

- Capture a **baseline** on representative data and hardware before touching anything.
  Record the metric, the input size, and the environment.
- Profile under **production-like load**, not a warm single-request loop. Cold caches,
  concurrency, and real payload sizes change where the time goes.
- Rank bottlenecks by **total time contribution** (calls x cost per call), not by how slow
  a single call feels. A cheap function called a million times outranks a slow one called
  once.
- Prefer **algorithmic wins** (O(n^2) to O(n log n), removing an N+1 query) over
  micro-optimizations. They are larger, safer, and easier to explain.
- Re-measure after each change and keep the diff small so a regression is trivial to
  bisect and revert.
- Guard the win with a **benchmark or budget check in CI** so it cannot silently rot. See
  [performance budget](23-performance-budget.md).
- Delete the optimization if the measured gain is within noise. Complexity without a
  proven payoff is a defect.

## Examples

**Good Example** — measure, target one bottleneck, verify

```python
# 1. Baseline on representative input (the number we must beat).
#    p95 render = 820 ms for a 5,000-row report.

# 2. Profiler shows 78% of time in a per-row DB lookup (an N+1 pattern) —
#    that is the critical path, so that is where we act.
def build_report(row_ids):
    users = fetch_users(row_ids)          # one batched query instead of N
    by_id = {u.id: u for u in users}      # O(1) lookup replaces per-row round trip
    return [render_row(by_id[i]) for i in row_ids]

# 3. Verify: re-run the same benchmark. p95 render = 140 ms (5.9x).
#    One change, attributable, and it clears the 200 ms budget. Stop here.
```

**Bad Example** — no baseline, batched guesses, no verification

```python
def build_report(row_ids):
    # "This loop felt slow", so several unrelated tweaks landed at once:
    rows = [render_row(fetch_user(i)) for i in row_ids]  # N+1 left untouched
    rows = list(map(str.strip, rows))     # micro-tweak on a cold path
    gc.disable()                          # cargo-cult "speed" trick with real risk
    return rows
    # No before/after number. Nobody can say which line helped, or if any did.
```

## Common Mistakes

- Optimizing from intuition instead of a profile — usually the wrong function.
- Measuring a single warm run, so caching hides the real cost.
- Bundling several changes, making the win (or regression) unattributable.
- Chasing micro-optimizations while an O(n^2) algorithm or N+1 query dominates.
- Having no stop condition, so effort continues long past "fast enough."
- Landing a speedup with no regression test, so it silently degrades later.
- Trading correctness or readability for gains that never got measured.

## Production Tips

- Keep a small, versioned benchmark suite in the repo so anyone can reproduce a number.
- Record the environment (CPU, data size, commit) alongside each result; results without
  context are not comparable.
- Automate a regression gate: fail CI if a key benchmark or budget worsens beyond a
  threshold. See [benchmarking](19-benchmarking.md).

## AI Review Checklist

- Is there a recorded baseline the change is measured against?
- Does a profile show the edited code is actually on the critical path?
- Is the change isolated so its effect can be attributed?
- Was the improvement re-measured and shown to exceed noise?
- Is there a stated target (budget/SLO), and did we stop at it?
- Is the win protected by a benchmark or budget check in CI?
- Did readability or correctness suffer for an unmeasured gain?

## Related

- `knowledge/performance/16-profiling.md`
- `knowledge/performance/19-benchmarking.md`
- `knowledge/performance/02-metrics.md`
- `knowledge/performance/23-performance-budget.md`
- `knowledge/performance/29-performance-review.md`
