---
id: nodejs/22-debugging
topic: nodejs
slug: debugging
title: "Debugging"
type: doc
order: 22
status: ready
tags: [nodejs, debugging]
related: [nodejs/16-error-handling, nodejs/20-memory-management, nodejs/19-performance, nodejs/17-logging, nodejs/21-testing]
when_to_use: "Read when diagnosing a crash, hang, leak, or performance problem in a Node.js process."
---
# Debugging

## Purpose

This document defines how to diagnose defects in a Node.js process using the
runtime's built-in tooling: the Inspector protocol and Chrome DevTools, the
`node --inspect` debugger, async stack traces, heap and CPU profiles, and core
dumps. The goal is to replace guess-and-print debugging with direct observation of
what the process is actually doing, so the root cause is found rather than masked.

## Why It Matters

Node's asynchronous, single-threaded execution makes bugs non-obvious: a stack trace
may point at the event loop instead of your code, an error may surface far from its
origin, and a "hang" may be a blocked loop, an unresolved promise, or an exhausted
connection pool — three different fixes. Debugging by scattering `console.log` and
redeploying is slow and often misleading. Using the inspector, profilers, and proper
async traces turns a multi-hour hunt into a targeted fix, and prevents the classic
mistake of treating a symptom while the cause remains.

## Core Principles

- **Reproduce before you fix.** A bug you cannot trigger on demand cannot be verified
  as fixed. Capture the exact input, state, and version first.
- **Observe, do not guess.** Attach a debugger or profiler and watch real state.
  Guessing at cause and "fixing" it produces changes that mask, not resolve, the bug.
- **Find the origin, not the symptom.** An error caught three layers up tells you where
  it was noticed, not where it was made. Follow the async cause chain to the source.
- **Change one thing at a time.** Isolate variables so you know which change mattered.
  Shotgun edits make it impossible to attribute the fix.
- **Preserve evidence.** Keep the failing logs, snapshot, or core dump; a fix without a
  captured failure cannot be confirmed and may recur silently.

## Best Practices

- Use `node --inspect` (or `--inspect-brk` to break on the first line) and connect
  Chrome DevTools / VS Code for breakpoints, watches, and stepping instead of print debugging.
- Enable async stack traces (on by default in current Node) so a trace crosses `await`
  boundaries and shows where the async chain originated.
- For a CPU-bound slowdown, capture a CPU profile (`node --prof` + `--prof-process`,
  or `clinic flame`) and read the flame graph for the widest frame — that is the cost.
- For memory growth, take two heap snapshots (`v8.writeHeapSnapshot()`), diff them in
  DevTools, and inspect the retainer path of the growing object. See `nodejs/20-memory-management`.
- Diagnose hangs with `node --inspect` "pause" to see the current stack, or
  `process._getActiveHandles()` / `why-is-node-running` to find what keeps the loop alive.
- Surface silent failures: attach `process.on("unhandledRejection")` and
  `uncaughtException` handlers that log and exit, so swallowed async errors are visible.
- Debug production with `--heapsnapshot-signal=SIGUSR2` and structured logs; never
  attach an open `--inspect` port to a public host — it is remote code execution.

## Examples

**Good Example** — reproduce, inspect the real async cause, verify

```js
// 1. Reproduce deterministically with the captured input in a test
test("repro: negative balance underflows", async () => {
  const acct = makeAccount({ balance: 0 });
  // run under `node --inspect-brk --test` and set a breakpoint in withdraw()
  await assert.rejects(() => withdraw(acct, 5), /insufficient/);
});

// 2. Surface swallowed async errors instead of losing them
process.on("unhandledRejection", (err) => {
  logger.fatal({ err }, "unhandled rejection"); // full trace, then fail loud
  process.exit(1);
});
```

**Bad Example** — print debugging that hides the origin

```js
async function withdraw(acct, amount) {
  try {
    console.log("withdrawing", amount); // scattered prints, redeploy to iterate
    return await doWithdraw(acct, amount);
  } catch (e) {
    console.log("error!");   // no stack, no context, error swallowed
    return null;             // symptom masked: caller sees success-ish null
  }
}
```

## Common Mistakes

- Debugging with `console.log` + redeploy instead of attaching the inspector once.
- Catching an error and logging only `e.message`, discarding the stack and cause.
- "Fixing" a hang by adding a timeout without finding what blocks the loop.
- Swallowing rejected promises, so the real failure never appears in any log.
- Exposing an `--inspect` port on a production/public interface (remote RCE).
- Editing several things at once, then not knowing which change fixed it.
- Declaring a bug fixed without a reproduction that now passes.

## Production Tips

- Ship an admin-guarded endpoint or `SIGUSR2` handler to dump a heap snapshot or CPU
  profile from a live process without restarting it.
- Enable `--heapsnapshot-near-heap-limit` so an OOM leaves a snapshot to analyze post-mortem.
- Log with correlation IDs so a single request's async chain is reconstructable across services — see `nodejs/17-logging`.
- Keep source maps in production builds so traces point at original source, not transpiled output.

## AI Review Checklist

- Is the bug reproducible on demand before any fix is attempted?
- Was the root cause observed with a debugger/profiler, not guessed?
- Does error handling preserve the stack and cause, not just the message?
- Are `unhandledRejection` and `uncaughtException` handled so async failures are visible?
- For leaks/slowness, was a heap or CPU profile actually captured and read?
- Is no `--inspect` port exposed on a public interface?
- Does a test now reproduce the bug and pass, proving the fix?

## Related

- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/20-memory-management.md`
- `knowledge/nodejs/19-performance.md`
- `knowledge/nodejs/17-logging.md`
- `knowledge/nodejs/21-testing.md`
