---
id: tools/22-profilers
topic: tools
slug: profilers
title: "Profilers"
type: doc
order: 22
status: ready
tags: [tools, profilers, writeFile, measure, connect, XDEBUG_TRIGGER, stringify, DevTools]
related: [tools/21-debuggers, tools/29-observability-tools, tools/13-test-runners, tools/09-vite, tools/30-engineering-principles, performance/16-profiling, performance/24-optimization-workflow]
when_to_use: "Read before optimizing anything — capturing a CPU or memory profile in Node, PHP, or the browser, and reading the result correctly."
---
# Profilers

## Purpose

This document defines how to measure where time and memory actually go: capturing profiles in
Node, PHP, and the browser, and interpreting flame graphs without drawing the wrong conclusion.

## Why It Matters

Optimization without measurement is guesswork, and the guess is usually wrong. Engineers
consistently over-estimate the cost of code they can see — a nested loop, a large array
operation — and under-estimate what they cannot: a template rendering ten thousand times, a
serializer walking an object graph, an ORM issuing four hundred queries behind one method call.

A profile removes the argument. It also frequently shows that the code under review is not on
the critical path at all.

## Core Principles

- **Profile before changing anything.** The first profile establishes both the target and the
  baseline to compare against.
- **Profile something representative.** A profile on ten seed rows describes a system nobody
  uses.
- **Read total time, not self time, first.** Self time finds the hot function; total time finds
  the expensive call path — usually where the fix is.
- **Change one thing, re-profile.** Two simultaneous changes make the measurement
  uninterpretable.

## Browser

Chrome DevTools covers the two questions that matter for frontend work:

```js
// Mark the region of interest so the flame chart is labelled.
performance.mark('render-start');
renderDashboard(data);
performance.mark('render-end');
performance.measure('dashboard-render', 'render-start', 'render-end');
```

- **Performance panel** — record an interaction, then read the flame chart. Long tasks (>50ms)
  are what make an interface feel unresponsive; each one blocks input.
- **Memory panel** — take a heap snapshot, perform the suspect action, take another, and use
  "Objects allocated between snapshots" to find what is retained. That comparison is how leaks
  are found; a single snapshot rarely shows anything.
- **Coverage tab** — reports unused JavaScript and CSS on the current page, which is usually
  the fastest route to a smaller bundle.

For React specifically, the Profiler in React DevTools attributes render time to components
and shows why each re-rendered.

## Node

```bash
# Sampling profiler built into Node — no dependencies.
node --cpu-prof --cpu-prof-dir=./profiles dist/server.js
# → profiles/CPU.20260714.*.cpuprofile — open in chrome://inspect or the DevTools Performance panel

# Heap snapshot on demand: start with the signal handler, then signal the process.
node --heapsnapshot-signal=SIGUSR2 dist/server.js &
kill -USR2 "$!"          # or: pkill -USR2 -f dist/server.js
```

```js
// Programmatic capture around a specific operation.
import { Session } from 'node:inspector/promises';
import { writeFile } from 'node:fs/promises';

const session = new Session();
session.connect();

await session.post('Profiler.enable');
await session.post('Profiler.start');

await runExpensiveJob();

const { profile } = await session.post('Profiler.stop');
await writeFile('./job.cpuprofile', JSON.stringify(profile));
```

For a live process where restarting is not acceptable, `clinic.js` (`clinic doctor`,
`clinic flame`) wraps these APIs and produces annotated output, including a diagnosis of
event-loop blocking versus I/O waiting — the distinction that decides whether the fix is
algorithmic or architectural.

## PHP

```ini
; Xdebug in profile mode — never enable this permanently.
xdebug.mode=profile
xdebug.start_with_request=trigger
xdebug.output_dir=/tmp/profiles
```

```bash
# Trigger a profiled request, then read the cachegrind file.
curl 'http://localhost:8080/?XDEBUG_TRIGGER=1'
qcachegrind /tmp/profiles/cachegrind.out.*
```

Xdebug's profiler is precise and slow — appropriate for a single request in development. For
production-representative data, use a sampling profiler such as SPX or a hosted APM instead;
sampling costs a few percent rather than multiplying request time.

On WordPress, Query Monitor answers the most common question directly — which component issued
which queries, and how long each took — before any profiler is needed. See
[WordPress — Debugging](../wordpress/28-debugging.md).

## Reading a Flame Graph

Width is time. Height is stack depth, not cost.

- A **wide plateau** near the top is a function doing real work — optimize it directly.
- A **wide base with narrow spikes** means the cost is distributed across many calls: the fix
  is usually calling it less, not making it faster.
- **Repeating identical stacks** indicate an N+1 pattern — the fix is batching.
- A **wide frame with no children** is a leaf: I/O, a native call, or genuine computation.

The most common misreading is treating depth as expense. A deep stack that occupies 2% of the
width is irrelevant regardless of how alarming it looks.

## Examples

**Good Example** — a measured optimization

```
Baseline:  /dashboard  p95 = 1,840ms
Profile:   62% of total time in Order::getCustomer() — 412 calls, one query each

Change:    prime customers in a single query before the loop
After:     p95 = 210ms, 4 queries total
```

The record states what was measured, what the profile showed, what changed, and the result.
That is what makes the optimization reviewable and prevents its accidental reversal.

**Bad Example** — optimization by intuition

```ts
// "This map allocates, so let me hand-roll a loop."
const total = items.reduce((sum, i) => sum + i.price, 0);
// → replaced with a for loop, saving ~0.01ms
// The same request spends 1.6s in a database call three frames up the stack.
```

## Common Mistakes

- Optimizing without a baseline, so improvement cannot be demonstrated.
- Profiling a development build, where source maps, hot reload, and unminified code dominate
  the profile.
- Profiling with unrepresentative data volume.
- Reading self time only and missing the expensive call path.
- Xdebug profiling left enabled, making everything slow and hiding the real distribution.
- Interpreting stack depth as cost.
- Changing several things between profiles.
- Micro-optimizing what the profile shows to be below 1% of total time.

## Production Tips

- Keep a continuous profiler in production if the platform supports it — profiles from real
  traffic beat any local reproduction.
- Profile at the percentile that hurts. Averages are dominated by fast requests; p95 and p99
  contain the ones users complain about.
- Save profiles as artifacts alongside performance work so the before/after comparison survives
  in the pull request.
- For memory, compare snapshots rather than reading one; retention is only visible as a
  difference.
- Pair profiling with a performance budget so regressions are caught automatically rather than
  investigated after a complaint — see
  [Performance — Performance Budget](../performance/23-performance-budget.md).

## AI Review Checklist

- Was a baseline captured before the change?
- Was the profile taken on a production-like build with realistic data?
- Does the change target what the profile identified as dominant?
- Was a second profile taken to confirm the improvement?
- Is profiling disabled in normal development and production configurations?
- Are the before/after numbers recorded where a reviewer can see them?

## Related

- `knowledge/tools/21-debuggers.md`
- `knowledge/tools/29-observability-tools.md`
- `knowledge/tools/13-test-runners.md`
- `knowledge/tools/09-vite.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/performance/16-profiling.md`
- `knowledge/performance/24-optimization-workflow.md`
