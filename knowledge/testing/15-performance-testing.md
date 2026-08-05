---
id: testing/15-performance-testing
topic: testing
slug: performance-testing
title: "Performance Testing"
type: doc
order: 15
status: ready
tags: [testing, performance-testing, renderInvoice, toBeLessThan, measure, describe, pytest-benchmark]
related: [testing/16-load-testing, testing/26-observability, testing/25-production-testing, testing/21-cicd, testing/22-flaky-tests]
when_to_use: "Read before writing tests or benchmarks that assert on latency, throughput, or resource use of code or an endpoint."
---
# Performance Testing

## Purpose

This document defines how to measure and guard the *speed and resource cost* of code:
latency, throughput, memory, and allocations. It covers micro-benchmarks (one function)
and single-request performance assertions. It is distinct from
[load testing](16-load-testing.md), which measures behavior under many concurrent users;
performance testing asks "how fast is one operation, and did it get slower?"

A performance test turns "it feels slow" into a number you can assert on and a regression
you can catch in CI, before a user files the ticket.

## Why It Matters

Performance regressions accrete silently. No single commit makes the app slow; a hundred
commits each adding a few milliseconds do. By the time it is noticeable it is expensive to
find, because the cause is spread across months of history. A performance test pins a
budget to a specific operation so the *commit* that blows it fails immediately, while the
diff is small and the author is still in context. It also converts vague optimization work
into evidence: you can prove a change helped instead of guessing.

## Core Principles

- **Measure percentiles, never averages.** Tail latency (p95/p99) is what users feel; a
  mean hides the slow requests that drive complaints and timeouts.
- **Assert against a budget, not a snapshot.** "Under 200 ms at p95" is a stable
  contract; "same as last run" is noise that flakes on a busy machine.
- **A benchmark must be isolated and warmed up.** Run enough iterations to pass JIT
  warm-up and GC, discard outliers from noisy neighbors, and hold the environment fixed.
- **Change one variable.** Compare against a baseline on the same hardware and dataset;
  a number without a baseline means nothing.
- **Profile before you optimize.** A test tells you *that* it is slow; a profiler tells
  you *where*. Never optimize on a hunch.

## Best Practices

- Use a real benchmarking harness (`k6`, `benchmark.js`, `pytest-benchmark`, JMH,
  `Benchmark.NET`) that handles warm-up, iteration count, and statistical variance for
  you. A hand-rolled `Date.now()` loop reports noise.
- Set explicit budgets (thresholds) and fail the test when they are exceeded, so the
  benchmark gates rather than merely reports.
- Pin the environment: fixed CPU allocation, fixed dataset size, no other load. In CI use
  a dedicated runner — shared runners produce numbers too noisy to gate on.
- Report p50, p95, and p99, plus allocations or memory where relevant. Latency alone
  hides a change that trades speed for memory.
- Compare each run against a committed baseline and fail on a regression beyond a margin
  (for example, >10% slower at p95) rather than on absolute equality.
- Test with production-shaped data volume. An algorithm that is fine on 10 rows can be
  O(n²) on 10,000; small fixtures hide complexity bugs.
- Keep performance tests out of the fast unit suite; run them in a separate,
  reproducible job so their variance never flakes the main build.

## Examples

**Good Example** — warmed harness, percentile budget, realistic data

```js
import { bench, describe, expect } from "vitest";
import { renderInvoice } from "../invoice";
import { largeInvoice } from "./fixtures"; // production-shaped: hundreds of line items

describe("renderInvoice", () => {
  // The harness warms up and runs many iterations, reporting p95 rather than one sample.
  bench("renders a large invoice under budget", () => {
    renderInvoice(largeInvoice);
  }, { time: 2000, warmupTime: 500 });
});

// A separate gate asserts the budget so a regression fails CI instead of just printing.
test("p95 stays within budget", async () => {
  const { p95 } = await measure(() => renderInvoice(largeInvoice), { runs: 200 });
  expect(p95).toBeLessThan(200); // stable contract, not "equal to last run"
});
```

**Bad Example** — one cold sample, average, toy data

```js
test("renderInvoice is fast", () => {
  const t0 = Date.now();
  renderInvoice({ items: [{ id: 1 }] }); // toy input hides O(n^2) behavior
  const ms = Date.now() - t0;            // one cold, un-warmed sample = pure noise
  expect(ms).toBeLessThan(50);           // flakes on a busy CI box; catches nothing real
});
```

## Common Mistakes

- Reporting or asserting on the average instead of p95/p99, hiding the tail users feel.
- A single un-warmed iteration timed with `Date.now()`, dominated by JIT and GC noise.
- Comparing "this run vs last run," which flakes whenever the machine is busy.
- Benchmarking with tiny fixtures, so quadratic or N+1 behavior never appears.
- Running perf tests on shared CI runners and gating on the noisy result.
- Optimizing based on the benchmark without a profiler, so effort goes to the wrong line.

## Production Tips

- Pair CI micro-benchmarks with real-user monitoring (RUM) and server
  [observability](26-observability.md); lab numbers and field numbers must both be watched.
- Track budgets over time in a dashboard so slow accretion shows as a trend, not just a
  pass/fail on one commit.
- For frontend, assert on Core Web Vitals (LCP, INP, CLS) with a budget in the pipeline,
  and measure with throttled CPU/network to approximate real devices.

## AI Review Checklist

- Does the test assert on p95/p99 against a budget, not an average or "same as last run"?
- Does the harness warm up and run enough iterations to escape JIT/GC noise?
- Is the dataset production-shaped so complexity bugs actually surface?
- Is the environment pinned, and does the perf job run separately from the unit suite?
- Is each run compared to a committed baseline with a defined regression margin?
- Was a profiler, not a guess, used to locate the hot path before optimizing?

## Related

- `knowledge/testing/16-load-testing.md`
- `knowledge/testing/26-observability.md`
- `knowledge/testing/25-production-testing.md`
- `knowledge/testing/21-cicd.md`
- `knowledge/testing/22-flaky-tests.md`
