---
id: nodejs/08-events
topic: nodejs
slug: events
title: "Node.js Events"
type: doc
order: 8
status: ready
tags: [nodejs, events]
related: [nodejs/06-streams, nodejs/16-error-handling, nodejs/02-event-loop, nodejs/20-memory-management, nodejs/11-child-process]
when_to_use: "Read before building or subscribing to any EventEmitter-based API, or before adding listeners in a long-lived process."
---
# Node.js Events

## Purpose

This document defines how to use the `EventEmitter` pattern in Node.js correctly:
emitting and subscribing to events, handling the special `'error'` event, cleaning up
listeners, and bridging events to `async`/`await`. It is written so an agent can build
event-driven APIs that do not leak memory or crash on an unhandled error.

`EventEmitter` is the backbone of Node's core: streams, servers, sockets, processes, and
timers are all emitters. Understanding it is prerequisite to using almost any Node API.

## Why It Matters

Events fail in two signature ways. First, the `'error'` event is special: if an emitter
emits `'error'` and no listener is registered, Node **throws** and, by default, crashes
the process. A single unlistened socket error takes down the whole server. Second,
listeners are strong references. Adding a listener on every request to a long-lived
emitter — and never removing it — is a textbook memory leak; the emitter and everything
its closures capture live forever. Both bugs are invisible until production: the happy
path emits no errors and the leak grows slowly. Event hygiene is not optional polish.

## Core Principles

- **Always handle `'error'`.** Every emitter that can emit `'error'` (sockets, streams,
  child processes) must have an `'error'` listener, or an unhandled emit crashes the
  process. There is no default no-op.
- **Listeners are references — remove what you add.** For long-lived emitters, pair every
  `on()` with a matching `off()`/`removeListener()`, or use `once()` for one-shot events.
- **The `MaxListenersExceededWarning` is a leak alarm, not noise.** Adding an 11th listener
  to one emitter warns because it usually means listeners are being added in a loop and
  never removed. Fix the leak; do not just raise the limit.
- **Emit is synchronous.** `emit()` calls listeners synchronously, in registration order,
  before returning. A slow listener blocks the emitter and the event loop.
- **Prefer `AbortSignal` for cancellation.** Node's event APIs accept `{ signal }` to
  auto-remove listeners when aborted, closing the cleanup gap.

## Best Practices

- Register an `'error'` handler on every socket, stream, and child process before you do
  anything else with it.
- Use `once(emitter, name)` and `on(emitter, name)` from `node:events` to consume events as
  promises / async iterables instead of nesting callbacks.
- Pass an `AbortSignal` (`emitter.on(name, fn, { signal })`) so listeners are cleaned up
  automatically when a request or task is cancelled.
- Keep listener functions small and non-blocking; if work is heavy, hand it to the next
  tick (`queueMicrotask`, `setImmediate`) so `emit` returns promptly.
- Name events with string constants shared between emitter and consumer to avoid typos
  that silently never fire.
- Extend `EventEmitter` for your own async-notification APIs, but document which events can
  emit `'error'`.

## Examples

**Good Example** — error handled, listener scoped and auto-removed via signal

```js
import { once } from "node:events";
import { createServer } from "node:net";

const server = createServer((socket) => {
  // A socket WILL emit 'error' on reset/timeout; without this the process crashes.
  socket.on("error", (err) => console.error("socket error", err.message));
  socket.end("hello\n");
});

async function firstConnection(signal) {
  // once() resolves on 'connection' and, with { signal }, removes its listeners
  // automatically if the caller aborts — no leak, no dangling handler.
  const [socket] = await once(server, "connection", { signal });
  return socket.remoteAddress;
}
```

**Bad Example** — no error handler, listener added per call and never removed

```js
import { createServer } from "node:net";

const server = createServer((socket) => {
  socket.end("hello\n"); // no 'error' listener → one reset crashes the process
});

function onEachRequest() {
  // Adds a new listener to the same long-lived emitter on every call and never
  // removes it → MaxListenersExceededWarning, then an unbounded memory leak.
  server.on("connection", (socket) => handle(socket));
}
```

## Common Mistakes

- Not attaching an `'error'` listener to a socket, stream, or child process, so one error
  crashes the whole process.
- Adding listeners in a request handler or loop without removing them, leaking memory and
  triggering `MaxListenersExceededWarning`.
- Raising `setMaxListeners` to silence the warning instead of fixing the leak it flagged.
- Assuming `emit()` is async and putting ordering-critical code after it, or blocking the
  loop inside a listener.
- Using `on()` where `once()` is correct, leaving a permanent listener for a one-time event.
- Typos in event names, so a listener silently never fires and there is no error.

## Production Tips

- In tests, assert listener counts (`emitter.listenerCount(name)`) around setup/teardown to
  catch leaks before they reach production.
- For app-level pub/sub across processes or instances, do not stretch `EventEmitter` — it is
  in-process only. Use a message broker or queue.
- Surface `'error'` events into your structured logger with context (connection id, remote
  address), not a bare stack trace.

## AI Review Checklist

- Does every emitter that can emit `'error'` (socket, stream, child process) have an
  `'error'` listener?
- Is every `on()` on a long-lived emitter paired with an `off()`, an `AbortSignal`, or
  replaced by `once()`?
- Is a `MaxListenersExceededWarning` treated as a leak to fix, not silenced with a higher
  limit?
- Are listeners non-blocking, given that `emit()` runs them synchronously?
- Is cross-process communication using a broker rather than an in-process emitter?

## Related

- `knowledge/nodejs/06-streams.md`
- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/02-event-loop.md`
- `knowledge/nodejs/20-memory-management.md`
- `knowledge/nodejs/11-child-process.md`
