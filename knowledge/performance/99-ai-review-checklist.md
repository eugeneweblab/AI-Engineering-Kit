---
id: performance/99-ai-review-checklist
topic: performance
slug: ai-review-checklist
title: "AI Review Checklist"
type: doc
order: 99
status: ready
tags: [performance, ai-review-checklist]
related: [performance/29-performance-review, performance/27-best-practices, performance/30-engineering-principles, performance/100-common-antipatterns, performance/98-production-checklist]
when_to_use: "Read before reviewing or generating any change that touches a hot path, a query, a cache, or a loop over data."
---
# AI Review Checklist

## Purpose

This is the checklist an AI agent runs when reviewing (or self-reviewing) a change for
performance: a new query, loop, cache, endpoint, or hot-path edit. Every item is a
verifiable yes/no about the *change* and its evidence. It is the code-review counterpart to
the [production checklist](98-production-checklist.md), which covers operational readiness.
Use it during review and before opening a pull request that could affect latency,
throughput, or resource use.

## Why It Matters

Performance regressions pass CI green. The code is correct, the tests are fast on ten rows
of fixture data, and the O(n²) loop or the newly added N+1 only bites at production scale —
weeks later, as a slow, hard-to-localize creep. A concrete review checklist catches these at
the one moment they are cheap to fix, before merge, and gives the agent a reason to reject a
change rather than a vibe. It also stops the opposite mistake: needless optimization that
adds complexity for a speedup nobody measured.

## Evidence & Justification

- [ ] Is there a **profile or benchmark** showing the changed code is (or was) a real
  bottleneck — not a guess (see [profiling](16-profiling.md))?
- [ ] For an optimization, is there a **before/after number** proving it worked, measured the
  same way both times?
- [ ] Was **only one variable** changed, so the measurement is interpretable?
- [ ] Does any added complexity (cache, concurrency, denormalization) pay rent — justified by
  a measurement, not added speculatively (see [engineering principles](30-engineering-principles.md))?

## Algorithms & Data Access

- [ ] Is the algorithm's **complexity** appropriate for realistic input size — no accidental
  O(n²) over a collection that grows?
- [ ] Does the change avoid **N+1 queries** — related data batched, joined, or preloaded?
- [ ] Are queries **indexed** for their filter/sort, and do they return **bounded** rows
  (pagination, limits)?
- [ ] Is work done **once** where possible — no recomputation of the same value inside a
  loop or per request?

## Memory & Allocation

- [ ] Are collections, caches, and buffers **bounded**, so the change cannot grow memory
  without limit (see [memory](04-memory.md))?
- [ ] Does it avoid loading a large dataset **fully into memory** when it could stream or
  paginate?
- [ ] Are large or short-lived allocations on the hot path avoided or reused where a profile
  shows they matter?

## Caching & Concurrency

- [ ] Does every new cache have a defined **TTL or invalidation**, and can it ever serve
  **stale or wrong** data (see [caching](08-caching.md))?
- [ ] Is the **cache key** complete — including every input the result depends on?
- [ ] Does added concurrency preserve **correctness** (no data races, defined ordering) and
  actually target a wait-bound, not CPU-bound, path?
- [ ] Do outbound calls have **timeouts**, so a slow dependency cannot stall the caller?

## Blocking & Waiting

- [ ] Is the request path free of **blocking I/O** that could be async or offloaded?
- [ ] Is expensive or long-running work moved off the synchronous path where it does not need
  to be there?
- [ ] Are locks held for the **minimum** scope, not around I/O or long computation?

## Client Delivery (web)

- [ ] Does the change avoid **shipping more bytes** than needed — no unbounded bundle growth,
  new dependencies code-split (see [code splitting](10-code-splitting.md))?
- [ ] Is non-critical work **deferred / lazy-loaded** so it does not block first render (see
  [lazy loading](09-lazy-loading.md))?
- [ ] Do new images and fonts follow the size/format rules and not regress Core Web Vitals?

## How to Use This Checklist

Treat any "no" as a finding, not a formality. For each "no", either change the code or write
down why the exception is acceptable — an unexplained "no" blocks the merge. Rank findings by
blast radius: a shared hot-path regression or a correctness-breaking cache outranks a
micro-inefficiency in cold code, because it costs far more, to far more users.

## Related

- `knowledge/performance/29-performance-review.md`
- `knowledge/performance/27-best-practices.md`
- `knowledge/performance/30-engineering-principles.md`
- `knowledge/performance/100-common-antipatterns.md`
- `knowledge/performance/98-production-checklist.md`
