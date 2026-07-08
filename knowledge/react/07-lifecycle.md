---
id: react/07-lifecycle
topic: react
slug: lifecycle
title: "Lifecycle"
type: doc
order: 7
status: ready
tags: [react, lifecycle]
related: [react/08-hooks, react/06-state, react/11-rendering, react/16-data-fetching, react/19-error-handling]
when_to_use: "Read before writing effects for mount/update/unmount behavior, subscriptions, or cleanup."
---
# Lifecycle

## Purpose

This document defines the component lifecycle in modern React and how to express it with
hooks. "Lifecycle" means the phases a component goes through — mounting, re-rendering
(updating), and unmounting — and the points where you run side effects and clean them up.
In function components, `useEffect` (and its siblings) are how you hook into these phases.

## Why It Matters

Lifecycle bugs are among the hardest to spot. A missing cleanup leaks subscriptions and
timers and causes "setState on unmounted component" and memory growth. A wrong dependency
array either freezes an effect with stale values or fires it in an infinite loop. A fetch
without cancellation delivers a slow response after the user navigated away, overwriting
newer data. And because React 18+ intentionally mounts, unmounts, and remounts components
in Strict Mode during development, effects that are not idempotent break in ways that only
appear later.

## Core Principles

- **Effects run after render, not during it.** Render stays pure; `useEffect` runs after
  the DOM is painted. That is where subscriptions, fetches, timers, and manual DOM work go.
- **Every effect that starts something must return cleanup.** Subscriptions, intervals,
  event listeners, and in-flight requests must be torn down in the returned function.
- **The dependency array is a contract, not a tuning knob.** List every value from render
  the effect reads. React re-runs the effect when they change; omit one and you get stale
  closures.
- **Effects must be idempotent.** Because React can run setup → cleanup → setup, running an
  effect twice must be safe. Design for it rather than suppressing it.

## Best Practices

- Model the three phases with `useEffect`: setup on mount/deps-change, cleanup on
  unmount/before-rerun. `useEffect(fn, [])` = mount + unmount only.
- Include the real dependencies; do not lie to the linter. If the array feels wrong, the fix
  is usually to move the value inside, wrap it in `useCallback`/`useMemo`, or use the updater
  form of `setState` — not to delete deps.
- Cancel async work in cleanup: use `AbortController` for fetch, or an `ignore` flag so a
  late response cannot set state after unmount.
- Do not use effects to transform props into state or to respond to a prop by setting
  state — compute during render instead. Effects are for synchronizing with systems
  *outside* React (network, DOM, subscriptions, timers).
- Reach for `useLayoutEffect` only when you must read/write layout before paint (measuring
  DOM); it blocks painting, so `useEffect` is the default.
- Wrap subtrees that can throw during render in an [error boundary](19-error-handling.md);
  effects' errors are not caught by boundaries and must be handled locally.

## Examples

**Good Example** — subscription with cleanup, cancellable fetch

```jsx
function Room({ roomId }) {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const controller = new AbortController();
    fetchMessages(roomId, { signal: controller.signal })
      .then(setMessages)
      .catch((e) => { if (e.name !== "AbortError") throw e; });

    const conn = connect(roomId);
    // Cleanup: runs on unmount AND before the next run when roomId changes.
    return () => {
      controller.abort();  // discard a response that would arrive too late
      conn.disconnect();   // no leaked socket when room changes or component unmounts
    };
  }, [roomId]); // re-subscribe whenever the room changes

  return <MessageList messages={messages} />;
}
```

**Bad Example** — no cleanup, lying dependency array

```jsx
function Room({ roomId }) {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    connect(roomId); // never disconnected → leaks a socket on every room change
    fetchMessages(roomId).then(setMessages); // late response overwrites newer data
  }, []); // empty deps but reads roomId → effect keeps the first room forever (stale)

  return <MessageList messages={messages} />;
}
```

## Common Mistakes

- Omitting cleanup for subscriptions, timers, or listeners, causing leaks and stale updates.
- An empty or incomplete dependency array that captures stale props/state.
- Fetching without cancellation, so out-of-order responses clobber current data.
- Using an effect to mirror props into state, creating a second source of truth.
- Suppressing the exhaustive-deps lint rule instead of fixing the underlying dependency.
- Assuming an effect runs once; Strict Mode runs it twice in dev to expose missing cleanup.

## Production Tips

- Keep exhaustive-deps as an error in ESLint; most lifecycle bugs are a dependency the
  linter already flagged.
- Prefer a data-fetching library ([data fetching](16-data-fetching.md)) over manual
  `useEffect` fetches — it handles cancellation, caching, and race conditions for you.

## AI Review Checklist

- Does every effect that subscribes, times, listens, or fetches return a cleanup function?
- Does the dependency array list every prop/state value the effect reads?
- Is async work in effects cancellable (AbortController or ignore flag)?
- Is the effect idempotent — safe to run setup/cleanup/setup twice?
- Is the effect synchronizing with something outside React, not mirroring props into state?
- Is `useLayoutEffect` reserved for pre-paint layout reads, with `useEffect` as the default?

## Related

- `knowledge/react/08-hooks.md`
- `knowledge/react/06-state.md`
- `knowledge/react/11-rendering.md`
- `knowledge/react/16-data-fetching.md`
- `knowledge/react/19-error-handling.md`
