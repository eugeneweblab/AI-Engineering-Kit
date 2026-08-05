---
id: performance/00-overview
topic: performance
slug: overview
title: "Performance Overview"
type: doc
order: 0
status: ready
tags: [performance, overview, architecture, security]
related: [performance/01-performance-fundamentals, performance/02-metrics, performance/16-profiling, performance/24-optimization-workflow, performance/23-performance-budget]
when_to_use: "Read first when starting any performance work, to see which doc in this topic answers your question."
---
# Performance Overview

## Purpose

This document is the map for the `performance` topic. It tells an agent *where to
look* before diving into a specific problem, and it fixes the shared vocabulary the
rest of the topic assumes: latency vs throughput, tail vs average, work vs wait.

Performance is not one subject. It is a stack of resources — CPU, memory, network,
disk, rendering — each with its own limits and its own tooling. The docs here are
organized so you can jump straight to the resource that is actually the bottleneck,
rather than guessing.

## Why It Matters

Performance work fails most often not because the fix is hard but because the *wrong
thing* gets optimized. An agent that rewrites a hot loop when the real cost is a
serial network round-trip has spent effort and changed nothing. The single most
valuable habit in this topic is: **measure first, find the dominant cost, then fix
that one thing.** This overview exists so you enter with a model of where costs live
and which document owns each one.

## Core Principles

- **Measure before you change.** Every doc here assumes you have a profile or a metric
  that names the bottleneck. Optimization without a measurement is a guess.
- **Optimize the dominant cost.** Amdahl's law is unforgiving: speeding up 5% of the
  runtime by 10x saves almost nothing. Find where the time actually goes.
- **Latency and throughput are different goals.** Tuning for one can hurt the other;
  know which one the requirement demands before you start.
- **The tail is the product.** Users experience p95 and p99, not the average. Most of
  this topic optimizes tails, not means.
- **A faster wrong answer is still wrong.** Correctness and safety constraints from the
  `security` and `architecture` topics are not negotiable for speed.

## How the Docs Fit Together

- **Foundations** — start here to build the mental model:
  - `01-performance-fundamentals.md` — latency, throughput, Amdahl's law, the
    measure-first loop.
  - `02-metrics.md` — what to measure (percentiles, RED/USE) and how to read it.
- **Resources** — the four places time and cost actually go:
  - `03-cpu.md` — compute-bound work, algorithms, hot paths, concurrency.
  - `04-memory.md` — allocation, leaks, GC pressure, cache locality.
  - `05-network.md` — round-trips, payload size, connection reuse, compression.
  - `13-database-performance.md`, `15-query-optimization.md` — the most common backend
    bottleneck.
- **Frontend delivery** — `06-rendering.md`, `07-loading.md`, `09-lazy-loading.md`,
  `10-code-splitting.md`, `11-images.md`, `12-fonts.md`, `18-web-vitals.md`.
- **Caching** — `08-caching.md`, `19-caching-strategies` (see `architecture`).
- **Method and workflow** — how to actually do the work:
  - `16-profiling.md`, `19-benchmarking.md`, `22-load-testing.md` — how to measure.
  - `24-optimization-workflow.md`, `26-debugging.md` — the loop to follow.
  - `23-performance-budget.md`, `20-capacity-planning.md`, `21-scalability.md`.
  - `17-monitoring.md`, `25-production-monitoring.md` — catching regressions in prod.
- **Guardrails** — `100-common-antipatterns.md`, `27-best-practices.md`,
  `98-production-checklist.md`, `99-ai-review-checklist.md`, `29-performance-review.md`.

## Best Practices

- Enter through `01-performance-fundamentals.md` and `02-metrics.md` before any
  resource-specific doc; they define the terms the others use.
- Identify which resource is saturated *first* (a profile or a saturation metric),
  then open only the matching resource doc. Do not optimize CPU because a request is
  slow — it may be waiting on the network.
- Treat `24-optimization-workflow.md` as the driver: it sequences measure → hypothesize
  → change → re-measure. The resource docs supply the specific techniques.
- Set a `23-performance-budget.md` before optimizing so you know when to stop.

## Common Mistakes

- Reading a technique doc (e.g. CPU) and applying it without first confirming CPU is the
  bottleneck.
- Optimizing the average latency when the requirement is about the p99 tail.
- Chasing micro-optimizations that the profiler shows are less than 1% of runtime.
- Skipping `02-metrics.md`, then reporting improvements with no baseline to compare to.

## AI Review Checklist

- Does the change cite a measurement (profile, benchmark, or metric) identifying the
  bottleneck it addresses?
- Is the optimized code path actually the dominant cost, per that measurement?
- Is the goal (latency vs throughput, mean vs tail) stated and matched by the change?
- Is there a before/after number, not just an assertion of "faster"?
- Was correctness preserved (tests still pass) after the optimization?

## Related

- `knowledge/performance/01-performance-fundamentals.md`
- `knowledge/performance/02-metrics.md`
- `knowledge/performance/16-profiling.md`
- `knowledge/performance/24-optimization-workflow.md`
- `knowledge/performance/23-performance-budget.md`
