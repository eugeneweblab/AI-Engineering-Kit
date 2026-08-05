---
id: typescript/25-performance
topic: typescript
slug: performance
title: "TypeScript Performance"
type: doc
order: 25
status: ready
tags: [typescript, performance]
related: [typescript/18-asynchronous-programming, typescript/19-collections, typescript/16-configuration, typescript/29-tooling]
when_to_use: "Read before optimizing TypeScript runtime hot paths or diagnosing slow compilation."
---
# TypeScript Performance

## Purpose

This document defines how to reason about performance in TypeScript projects. It covers
two distinct axes that are often confused: **runtime performance** (the JavaScript your
code becomes) and **build/type-checking performance** (how fast `tsc` and your bundler
run). An agent should optimize the right one, with evidence.

TypeScript's types vanish at runtime — they cost nothing when the program executes. So
runtime performance is a JavaScript problem, while type complexity is a *compile-time*
cost. Treat them separately.

## Why It Matters

Premature optimization wastes effort and obscures code; missing optimization ships slow
software. The way out is measurement. Most TypeScript "performance" bugs are ordinary
JavaScript problems — an O(n²) loop, an unbounded cache, a blocking synchronous call —
that types neither cause nor fix. Meanwhile, an over-engineered conditional type can make
`tsc` crawl and freeze the editor, hurting the whole team's velocity even though runtime
is unaffected. Knowing which cost you are paying is the whole skill.

## Core Principles

- **Measure before you optimize.** Profile with real inputs; never optimize on a hunch.
  The cost of guessing is that you complicate code with no gain.
- **Fix algorithms before micro-optimizing.** An O(n²) → O(n) change dwarfs any loop
  tweak. Reach for a `Map`/`Set` before hand-tuning.
- **Types are free at runtime.** Never contort runtime code for "type performance", and
  never assume a type annotation slows execution — it is erased.
- **Type complexity has a compile cost.** Deeply recursive conditional and mapped types
  can make `tsc` and the language server slow. Keep the type surface tractable.
- **Async is about throughput, not raw speed.** Parallelize independent I/O; do not
  serialize awaits that could run together.

## Best Practices

- Use `Map` and `Set` for membership and keyed lookup instead of `array.includes` or
  repeated `.find` in a loop — O(1) vs O(n). See [collections](19-collections.md).
- Run independent async work with `Promise.all`; sequential `await` in a loop serializes
  I/O and multiplies latency. See [asynchronous programming](18-asynchronous-programming.md).
- Avoid allocating in hot loops: hoist constants, reuse buffers, and prefer `for` over
  chained `.map().filter()` when the array is large and the path is hot.
- Set `incremental: true` and use project references / `tsc --build` for large repos so
  type-checking is cached across builds. See [configuration](16-configuration.md).
- Keep conditional and recursive types shallow; cap recursion depth and prefer a concrete
  helper type over an ever-more-clever generic that stalls the compiler.
- Use `skipLibCheck: true` to skip type-checking `.d.ts` files you do not own — a large,
  safe compile-time win.
- Bound every cache (size or TTL). An unbounded memoization map is a memory leak.
- Debounce or batch high-frequency work (events, DB writes) rather than processing each
  item eagerly.

## Examples

**Good Example** — O(n) lookup, parallel I/O

```ts
// Build a Set once: membership is O(1), so the whole filter is O(n).
const bannedIds = new Set(banned.map((u) => u.id));
const active = users.filter((u) => !bannedIds.has(u.id));

// Independent fetches run concurrently; total time ≈ the slowest one, not the sum.
const [profile, orders, prefs] = await Promise.all([
  getProfile(userId),
  getOrders(userId),
  getPreferences(userId),
]);
```

**Bad Example** — O(n²) lookup, serialized I/O

```ts
// .find scans `banned` for every user → O(n·m); quadratic on large inputs.
const active = users.filter(
  (u) => !banned.find((b) => b.id === u.id),
);

// Each await blocks the next; three round-trips run back-to-back for no reason.
const profile = await getProfile(userId);
const orders = await getOrders(userId);
const prefs = await getPreferences(userId);
```

## Common Mistakes

- Optimizing code that is not on the hot path, adding complexity for zero measured gain.
- Believing type annotations slow runtime — they are erased before execution.
- `await` inside a `for` loop over independent items, serializing what could be parallel.
- Repeated `array.includes`/`.find` inside a loop instead of a `Set`/`Map`.
- Unbounded caches and memoization maps that grow until the process runs out of memory.
- Deeply recursive conditional types that make the editor and CI type-check slow.

## Production Tips

- Profile with a real profiler (`node --prof`, `clinic`, Chrome DevTools), not `console.time`
  guesses, and optimize the top frames.
- Track `tsc` time in CI; a sudden jump usually traces to a new heavy generic type.
- Set a bundle-size budget in the bundler and fail the build when it regresses.

## AI Review Checklist

- Was the optimization justified by a measurement, or is it speculative?
- Are lookups in loops backed by `Map`/`Set` rather than linear scans?
- Do independent async operations run with `Promise.all` instead of serialized awaits?
- Are caches bounded by size or TTL?
- Is any runtime code contorted for a "type performance" reason that does not exist?
- Are heavy recursive/conditional types kept shallow to protect compile time?

## Related

- `knowledge/typescript/18-asynchronous-programming.md`
- `knowledge/typescript/19-collections.md`
- `knowledge/typescript/16-configuration.md`
- `knowledge/typescript/29-tooling.md`
