---
id: javascript/10-event-loop
topic: javascript
slug: event-loop
title: "Event Loop"
type: doc
order: 10
status: ready
tags: [javascript, event-loop]
related: [javascript/08-asynchronous-javascript, javascript/09-promises, javascript/02-execution-context, javascript/25-performance]
when_to_use: "Read before reasoning about ordering, blocking, timers, or why async code runs in a surprising sequence."
---
# Event Loop

## Purpose

This document defines the JavaScript concurrency model: the single thread, the call
stack, the task (macrotask) and microtask queues, and the order in which callbacks,
promises, and timers actually run. It explains *why* the async ordering in
[promises](09-promises.md) and [async/await](08-asynchronous-javascript.md) is what it
is, so an agent can predict execution order and avoid blocking the thread.

The event loop is the mechanism that lets one thread juggle many operations: it runs
JavaScript to completion, then drains queued work between turns. Understanding it is
the difference between guessing at ordering bugs and knowing the answer.

## Why It Matters

JavaScript runs on a single thread, so any synchronous work you do delays *everything
else* — rendering, input, timers, network callbacks. A tight loop or a 200ms
synchronous parse freezes the UI or stalls the server's event loop, dropping
throughput to zero for that span. The subtler cost is ordering: microtasks (promises)
always run before the next macrotask (timers, I/O), so a promise chain can starve a
`setTimeout(…, 0)` you assumed would run "soon". Bugs that depend on this ordering are
invisible until timing shifts under load.

## Core Principles

- **One call stack, run to completion.** A function runs uninterrupted until it
  returns; nothing else on the thread executes meanwhile. Async does not mean parallel.
- **Microtasks drain before the next macrotask.** After each macrotask (and after the
  initial script), the engine empties the *entire* microtask queue before rendering or
  the next task.
- **Promises and `queueMicrotask` are microtasks; timers, I/O, and events are
  macrotasks.** `await` continuations are microtasks.
- **The loop cannot advance while the stack is non-empty.** Blocking the stack blocks
  timers, rendering, and I/O callbacks alike.
- **Rendering happens between macrotasks, after microtasks**, in the browser. Long
  synchronous work between frames drops frames.

## Best Practices

- Never do long synchronous CPU work on the main thread. Offload to a **Web Worker**
  (browser) or **worker thread** (Node), or chunk it and yield with `setTimeout`/
  `scheduler.yield()`. The cost of not yielding is a frozen UI or stalled server.
- Understand that an infinite microtask chain (a promise that re-queues itself)
  **starves macrotasks and rendering** — the loop never reaches the next task.
- Use `queueMicrotask()` when you need to run *after* the current stack unwinds but
  *before* any timer or I/O — e.g. batching state updates.
- Do not use `setTimeout(fn, 0)` to "wait for" DOM or async state; it only defers to
  the next macrotask, which may be after or before what you expect. Await the actual
  signal instead.
- In Node, know that `process.nextTick` runs *before* the promise microtask queue and
  can starve I/O if abused — prefer `queueMicrotask` for ordinary microtask needs.

## Examples

**Good Example** — predicting order, yielding for long work

```js
console.log("1: sync");

setTimeout(() => console.log("4: macrotask (timer)"), 0);

Promise.resolve().then(() => console.log("3: microtask (promise)"));

console.log("2: sync");
// Output order: 1, 2, 3, 4
// Both logs run first (sync). Then the microtask queue drains (3) BEFORE the
// timer macrotask (4), even though the timer was scheduled first.

// Chunk heavy work so the loop can render/handle input between slices.
async function processInChunks(items, work) {
  for (let i = 0; i < items.length; i++) {
    work(items[i]);
    if (i % 500 === 0) await new Promise((r) => setTimeout(r)); // yield the thread
  }
}
```

**Bad Example** — blocking the single thread

```js
function computeReport(rows) {
  let total = 0;
  // Synchronous loop over a huge array: the stack never unwinds, so during this
  // call NO timers fire, NO clicks are handled, and the UI is frozen solid.
  for (let i = 0; i < rows.length; i++) {
    total += expensiveScore(rows[i]);   // 100k iterations = a visibly locked page
  }
  return total;
}

button.addEventListener("click", () => computeReport(hugeDataset)); // freezes on click
```

## Common Mistakes

- Long synchronous loops or parsing on the main thread, freezing the UI or event loop.
- Assuming `setTimeout(fn, 0)` runs before an already-queued promise callback (it does not).
- A self-re-queuing promise/microtask that starves timers and rendering entirely.
- Believing async code runs in parallel; it interleaves on one thread.
- Overusing `process.nextTick` in Node, starving the I/O phase.
- Expecting timer delays to be exact — they are a *minimum*, delayed by a busy loop.

## Production Tips

- Watch **event loop lag** in Node (`perf_hooks.monitorEventLoopDelay`); rising lag
  means synchronous work is blocking I/O and needs offloading.
- In the browser, use the Performance panel's "Long Tasks" (>50ms) to find work that
  blocks input and rendering; move it to a worker or chunk it.
- Prefer `scheduler.postTask`/`scheduler.yield` (2026 baseline in modern browsers) for
  prioritized yielding over ad-hoc `setTimeout` hacks.

## AI Review Checklist

- Is any long synchronous CPU work on the main thread that should be a worker or chunked?
- Does the code assume a specific order between promises (microtasks) and timers (macrotasks)?
- Are there self-re-queuing microtasks that could starve macrotasks or rendering?
- Is `setTimeout(fn, 0)` used to "wait for" state instead of awaiting the real signal?
- In Node, is `process.nextTick` used where `queueMicrotask` would avoid starving I/O?
- Are timer delays treated as minimums, not guarantees?

## Related

- `knowledge/javascript/08-asynchronous-javascript.md`
- `knowledge/javascript/09-promises.md`
- `knowledge/javascript/02-execution-context.md`
- `knowledge/javascript/25-performance.md`
