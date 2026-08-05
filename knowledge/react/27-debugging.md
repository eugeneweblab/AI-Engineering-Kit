---
id: react/27-debugging
topic: react
slug: debugging
title: "React Debugging"
type: doc
order: 27
status: ready
tags: [react, debugging]
related: [react/08-hooks, react/11-rendering, react/19-error-handling, react/12-performance, react/21-testing]
when_to_use: "Read when a React component renders the wrong thing, re-renders too often, crashes, or leaks."
---
# React Debugging

## Purpose

This document defines a systematic method for diagnosing React bugs: wrong output,
extra renders, stale values, unmount crashes, and effect leaks. It names the tools
(React DevTools, the Profiler, StrictMode) and the reasoning process so an agent can
find root cause instead of guessing. The goal is to locate the *cause*, not to
suppress the *symptom*.

Most React bugs reduce to one of four questions: What data drove this render? Why did
it render again? Is this value stale? Did this effect clean up? This doc is how to
answer them.

## Why It Matters

React bugs are often intermittent — they depend on timing, render order, or navigation
speed — so "it works on my machine" is nearly worthless as evidence. Guessing and
adding `useMemo` or a dependency-array tweak can make a symptom disappear while the real
defect (a stale closure, a mutation, a missing cleanup) survives and resurfaces
elsewhere. A disciplined method finds the cause once; guesswork finds it repeatedly.

## Core Principles

- **Reproduce before you fix.** Find the exact inputs and steps that trigger the bug.
  A fix you cannot verify against a repro is a guess.
- **Read the data flow, not the symptom.** Trace the prop or state value backward to
  its source. The bug is usually upstream of where it's visible.
- **Isolate the variable.** Change one thing at a time. Comment out effects, hardcode
  props, or render the component alone to shrink the search space.
- **Trust StrictMode's double-invoke.** In development React runs render and effects
  twice to surface impurity and missing cleanup. A bug that only appears there is a
  real bug, not a StrictMode artifact.
- **Console-logging is a tool, not a fix.** Remove diagnostics before committing.

## Best Practices

- Install React DevTools; use the Components tab to inspect live props/state/hooks and
  the Profiler to see what rendered, why, and how long it took.
- In the Profiler, enable "Record why each component rendered" to distinguish a
  props change from a parent re-render from a hook change.
- For "value is stale" bugs, check the effect/callback dependency array first — a
  missing dependency captures an old value in a closure. See [hooks](08-hooks.md).
- For "renders too often" bugs, check for new object/array/function props created inline
  each render, and unstable context values. See [performance](12-performance.md).
- For "crashes on unmount / setState after unmount," check that every subscription,
  timer, and fetch has a cleanup or `AbortController`.
- Wrap suspect subtrees in an [error boundary](19-error-handling.md) to capture the
  component stack instead of a blank screen.
- Reproduce in a test — a failing test is the most durable repro. See [testing](21-testing.md).

## Examples

**Good Example** — cleanup makes the effect safe and debuggable

```tsx
function useUser(id: string) {
  const [user, setUser] = useState<User | null>(null);
  useEffect(() => {
    const ac = new AbortController();
    fetch(`/api/users/${id}`, { signal: ac.signal })
      .then((r) => r.json())
      .then(setUser)
      .catch((e) => {
        if (e.name !== "AbortError") throw e; // ignore the expected cancel
      });
    return () => ac.abort(); // cancels in-flight fetch on id change / unmount
  }, [id]); // id listed → refetches correctly, no stale user
  return user;
}
```

**Bad Example** — stale closure and a leak that only shows up intermittently

```tsx
function useUser(id: string) {
  const [user, setUser] = useState<User | null>(null);
  useEffect(() => {
    // No cleanup: a slow response for an old id overwrites the new one (race),
    // and setUser after unmount warns. No repro on fast networks — a heisenbug.
    fetch(`/api/users/${id}`).then((r) => r.json()).then(setUser);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // id missing → user is stale for every id after the first
  return user;
}
```

## Common Mistakes

- Adding `useMemo`/`useCallback` to "fix" a bug without knowing why it renders.
- Suppressing the exhaustive-deps lint rule to silence a warning that is a real defect.
- Blaming StrictMode's double render/effect for a bug it merely exposed.
- Debugging the production build; source maps and DevTools work best in development.
- Removing a symptom (a crash) with a try/catch that swallows the real error.
- Leaving `console.log` statements in committed code.

## Production Tips

- Ship an error boundary that reports to an error tracker (Sentry) with component stack.
- Keep source maps for production builds (uploaded privately) so stack traces are readable.
- Reproduce production-only bugs by building with production mode locally first.

## AI Review Checklist

- Is there a documented reproduction for the bug being fixed?
- Does the fix address the data-flow cause, not just the visible symptom?
- Were dependency arrays checked for the stale value / extra render?
- Do effects with subscriptions, timers, or fetches have cleanup?
- Were diagnostic logs and lint suppressions removed?
- Is the bug captured by a regression test?

## Related

- `knowledge/react/08-hooks.md`
- `knowledge/react/11-rendering.md`
- `knowledge/react/19-error-handling.md`
- `knowledge/react/12-performance.md`
- `knowledge/react/21-testing.md`
