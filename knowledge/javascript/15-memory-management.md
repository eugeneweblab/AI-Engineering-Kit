---
id: javascript/15-memory-management
topic: javascript
slug: memory-management
title: "Memory Management"
type: doc
order: 15
status: ready
tags: [javascript, memory-management]
related: [javascript/03-scope-and-closures, javascript/12-dom, javascript/10-event-loop, javascript/25-performance, javascript/19-symbols]
when_to_use: "Read before writing long-lived code with listeners, timers, caches, or closures — or when diagnosing a memory leak."
---
# Memory Management

## Purpose

This document defines how JavaScript memory is allocated and reclaimed, and how to avoid
the leaks that a garbage-collected language still allows. It is written so an agent can
build long-lived code — servers, SPAs, workers — that does not grow unboundedly in memory
until it is killed or the tab crashes.

## Why It Matters

Garbage collection reclaims only what is **unreachable**. Anything still referenced —
even accidentally, even forever-unused — is retained. In a short-lived script this never
matters; in a long-running server or a single-page app that never reloads, a small
per-request or per-navigation leak compounds until the process is OOM-killed or the tab
freezes. These leaks are invisible in unit tests and on the developer's machine; they
appear only under sustained real traffic, which makes them expensive to catch late.
Understanding *what keeps a reference alive* is the whole game.

## Core Principles

- **Reachability, not usage, decides retention.** The GC frees objects no live reference
  can reach. An object you will never touch again still lives if something points to it.
- **Long-lived containers are the leak surface.** Module-level arrays/maps, global caches,
  and event-emitter registries hold references indefinitely. Anything you `push`/`set`
  into them, you must eventually remove.
- **Every subscription needs an unsubscription.** `addEventListener`, `setInterval`,
  observers, and emitter `.on()` create references from a long-lived source to your
  object. Removing the object without removing the subscription leaks it.
- **Closures capture their entire scope.** A retained closure retains every variable it
  can reference, including large objects and DOM nodes, for as long as the closure lives.
- **Use weak references for "cache while alive" data.** `WeakMap`/`WeakSet` hold keys
  weakly, so entries vanish when the key is otherwise unreachable — no manual cleanup.

## Best Practices

- Pair every `addEventListener` with `removeEventListener` (or one `AbortController`
  `signal` for the whole group), and every `setInterval`/`setTimeout` with `clear*` on
  teardown.
- Store per-object metadata keyed by the object in a `WeakMap`, not a `Map` — it will not
  keep the object alive and needs no manual eviction.
- Bound every cache: cap size and evict (LRU), or use `WeakMap` keyed by the owning
  object. An unbounded cache is a guaranteed leak.
- Null out or scope large buffers so they leave scope promptly; do not park them on
  module-level or global variables.
- Detach DOM nodes fully: removing a node from the tree does not free it if a JS variable,
  closure, or listener still references it ("detached DOM tree" leak).
- Prefer local variables and small closures; avoid capturing large objects in callbacks
  that outlive the operation.
- Use `FinalizationRegistry` only for optional cleanup logging, never for required
  release — its timing is not guaranteed.

## Examples

**Good Example** — scoped listener, weak metadata, bounded lifetime

```js
const metadata = new WeakMap(); // entries auto-drop when the widget is GC'd

function mountWidget(el, data) {
  metadata.set(el, data);                 // no manual cleanup needed for this map
  const controller = new AbortController();

  window.addEventListener("resize", onResize, { signal: controller.signal });
  const timer = setInterval(poll, 1000);

  return function unmount() {
    controller.abort();   // removes the resize listener in one call
    clearInterval(timer); // stops the interval that referenced this closure
    el.remove();          // now nothing references el → it can be collected
  };
}
```

**Bad Example** — unremoved listener, unbounded global cache

```js
const cache = {}; // module-level, never evicted → grows forever

function mountWidget(el, data) {
  cache[el.id] = data;                    // stored permanently, never deleted → leak
  window.addEventListener("resize", () => layout(el)); // listener + closure keep `el`
  // No teardown: calling el.remove() elsewhere frees nothing, because the resize
  // listener (on the global window) still references el via the closure. Detached
  // DOM node + its data are retained for the life of the page.
}
```

## Common Mistakes

- Adding listeners/intervals/observers without a matching removal on teardown.
- Using a plain `Map`/object as a cache keyed by objects, keeping those objects alive
  forever; a `WeakMap` would have released them.
- Unbounded caches or arrays that only ever grow (append-only logs, memoization tables).
- Detached DOM nodes still referenced by a JS variable, closure, or listener.
- Closures on hot paths capturing large objects they do not need.
- Assuming setting a variable to `null` frees memory when other references still exist.
- Relying on `FinalizationRegistry`/`WeakRef` for mandatory cleanup — GC timing is not
  guaranteed.

## Production Tips

- Profile with Chrome DevTools **Memory** tab: take heap snapshots before/after a repeated
  action; a growing retained size across identical cycles is a leak. Use "Detached" filter
  to find orphaned DOM.
- In Node, watch `process.memoryUsage().heapUsed` under load and take `--heap-snapshot`
  dumps; a monotonically rising baseline across steady traffic indicates a leak.
- Instrument long-lived maps/caches with a size metric and alert if they exceed expected
  bounds.

## AI Review Checklist

- Does every `addEventListener`/`setInterval`/observer/subscription have a matching
  teardown?
- Are object-keyed caches using `WeakMap`, or are plain maps bounded and evicted?
- Are all caches and growing arrays capped, not append-only?
- Are removed DOM nodes free of lingering JS references, closures, and listeners?
- Do closures on hot or long-lived paths avoid capturing large unnecessary objects?
- Is `FinalizationRegistry`/`WeakRef` used only for optional, not required, cleanup?

## Related

- `knowledge/javascript/03-scope-and-closures.md`
- `knowledge/javascript/12-dom.md`
- `knowledge/javascript/10-event-loop.md`
- `knowledge/javascript/25-performance.md`
- `knowledge/javascript/19-symbols.md`
