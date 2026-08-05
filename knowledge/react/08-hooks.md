---
id: react/08-hooks
topic: react
slug: hooks
title: "Hooks"
type: doc
order: 8
status: ready
tags: [react, hooks]
related: [react/06-state, react/07-lifecycle, react/09-custom-hooks, react/12-performance, react/10-context-api]
when_to_use: "Read before using any use* hook or debugging a 'rules of hooks' or stale-closure error."
---
# Hooks

## Purpose

This document defines how to use React Hooks — the `use*` functions that let function
components hold state, run effects, and tap into React features. It covers the built-in
hooks, the non-negotiable Rules of Hooks, and when to reach for each. Custom hooks get
their own doc: [custom hooks](09-custom-hooks.md).

## Why It Matters

Hooks work by call order: React matches each hook call to its stored state by the sequence
in which hooks run, not by name. Break that order — call a hook conditionally or in a loop —
and state silently attaches to the wrong hook, producing corruption that no type checker
catches. Beyond ordering, hooks close over the render's values, so a stale closure serves
old state; an unstable dependency defeats memoization; overusing `useMemo`/`useCallback`
adds cost without benefit. These are the everyday hazards of hook-based code.

## Core Principles

- **Only call hooks at the top level.** Never inside conditions, loops, nested functions, or
  after an early return. React relies on a stable call order every render.
- **Only call hooks from React functions.** Call them from function components or other
  hooks — never from plain functions, class methods, or event handlers.
- **Hooks close over render values.** Each render's hooks see that render's props and state.
  To read the latest inside a callback or effect, use the updater form or a `ref`.
- **Memoization is a performance tool, not correctness.** `useMemo`/`useCallback` must not
  be relied on for behavior; the app must be correct if React recomputed everything.

## Best Practices

- `useState` for local values; `useReducer` when transitions are complex or interrelated.
- `useEffect` for synchronizing with external systems, always with correct deps and cleanup
  (see [lifecycle](07-lifecycle.md)); `useLayoutEffect` only for pre-paint layout reads.
- `useRef` for mutable values that must persist across renders without triggering a
  re-render (DOM nodes, timers, latest-value holders). Mutating `ref.current` never re-renders.
- `useContext` to consume context; keep contexts small so consumers do not re-render on
  unrelated changes (see [context](10-context-api.md)).
- `useMemo`/`useCallback` only to stabilize a reference passed to a memoized child or an
  effect's dependency, or to skip a genuinely expensive computation — profile first, because
  the memo itself has a cost.
- `useId` for stable SSR-safe ids (form labels), never `Math.random`.
- `useTransition` to mark non-urgent state updates so typing/clicks stay responsive; its
  `startTransition` accepts an async function (an Action) in React 19.
- `useActionState(action, initial)` for form submission state — it returns
  `[state, formAction, isPending]` and wires straight into `<form action={formAction}>`.
- `useOptimistic(actual, reducer)` to show a pending result immediately; it auto-reverts to
  `actual` when the surrounding Action settles.
- `use(resource)` to read a promise (suspends) or context — unlike other hooks it may be
  called conditionally and after an early return, but the promise must be created/cached
  outside render, not `new`'d each render.
- Extract a [custom hook](09-custom-hooks.md) when stateful logic repeats across components.
- Keep the exhaustive-deps ESLint rule on; most hook bugs are a dependency it already flags.

## Examples

**Good Example** — top-level calls, stable callback, ref for latest value

```jsx
function SearchBox({ onSearch }) {
  const [query, setQuery] = useState("");

  // useCallback stabilizes the reference so the debounced effect below
  // does not re-create its timer on every keystroke.
  const runSearch = useCallback((q) => onSearch(q.trim()), [onSearch]);

  useEffect(() => {
    const id = setTimeout(() => runSearch(query), 300);
    return () => clearTimeout(id); // cleanup cancels the pending debounce
  }, [query, runSearch]); // every read value is declared

  return <input value={query} onChange={(e) => setQuery(e.target.value)} />;
}
```

**Bad Example** — conditional hook, wrong deps

```jsx
function SearchBox({ enabled, onSearch }) {
  const [query, setQuery] = useState("");

  if (enabled) {
    // Hook called conditionally → hook order changes between renders → state corruption
    useEffect(() => {
      setTimeout(() => onSearch(query), 300); // no cleanup → stacked stale searches
    }, []); // empty deps but reads query/onSearch → always searches the first value
  }

  return <input value={query} onChange={(e) => setQuery(e.target.value)} />;
}
```

### Reading the latest value inside a persistent callback

An interval or subscription is set up once (`[]` deps) but its callback keeps running. The
closure it captured is frozen at the first render, so reading state directly serves a stale
value. Fix it with the updater form (or a ref) instead of adding the value to the deps, which
would tear down and recreate the interval on every change.

**Bad Example** — stale closure freezes `count` at its initial value

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    // This closure captured count === 0 and never sees a newer value.
    const id = setInterval(() => setCount(count + 1), 1000);
    return () => clearInterval(id);
  }, []); // runs once; count is permanently 0 in here → UI sticks at 1

  return <p>{count}</p>;
}
```

**Good Example** — updater form reads the latest state without re-subscribing

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    // The updater receives the current value each tick, so no dep on count is needed.
    const id = setInterval(() => setCount((c) => c + 1), 1000);
    return () => clearInterval(id);
  }, []); // interval created once and correctly increments forever

  return <p>{count}</p>;
}
```

### React 19: form Actions with `useActionState` + `useOptimistic`

`useActionState` owns the async submission state (result and `isPending`); `useOptimistic`
paints the new item instantly and rolls back automatically if the Action throws. Because a
`<form action>` runs inside a transition, the optimistic value reverts on failure with no
manual cleanup.

**Good Example** — optimistic comment posting

```jsx
import { useActionState, useOptimistic } from "react";

function CommentForm({ postId, comments, sendComment }) {
  const [optimistic, addOptimistic] = useOptimistic(
    comments,
    (current, text) => [...current, { id: `temp-${text}`, text, pending: true }]
  );

  // action signature is (previousState, formData) => nextState
  const [error, submitAction, isPending] = useActionState(
    async (_prev, formData) => {
      const text = formData.get("text");
      addOptimistic(text); // shows immediately; reverts if sendComment rejects
      try {
        await sendComment(postId, text);
        return null; // cleared error
      } catch (e) {
        return e.message; // becomes the new state, surfaced below
      }
    },
    null
  );

  return (
    <form action={submitAction}>
      <ul>
        {optimistic.map((c) => (
          <li key={c.id} style={{ opacity: c.pending ? 0.5 : 1 }}>{c.text}</li>
        ))}
      </ul>
      <input name="text" required />
      <button disabled={isPending}>Post</button>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
```

### React 19: reading a promise with `use`

`use` unwraps a promise and suspends the component until it resolves — no `useEffect` +
`useState` + manual loading flags. The promise must be created outside render (passed as a
prop, or produced by a cache/framework loader); creating a fresh promise in render restarts
the fetch on every attempt and loops forever.

**Good Example** — suspend on data, catch errors with a boundary

```jsx
import { use, Suspense } from "react";

function Profile({ userPromise }) {
  const user = use(userPromise); // suspends until resolved
  return <h1>{user.name}</h1>;
}

function Page({ userPromise }) {
  return (
    <ErrorBoundary fallback={<p role="alert">Could not load profile.</p>}>
      <Suspense fallback={<Spinner />}>
        {/* userPromise created by a loader/cache, not inline here */}
        <Profile userPromise={userPromise} />
      </Suspense>
    </ErrorBoundary>
  );
}
```

`use` is also the one hook allowed past a conditional or early return, which lets you read a
context only when needed: `if (theme) { const t = use(ThemeContext); /* ... */ }`.

### React 19: `ref` is an ordinary prop

Function components receive `ref` as a normal prop — `forwardRef` is no longer required for
new code (it still works but is deprecated).

**Good Example** — forward a ref without `forwardRef`

```jsx
function TextInput({ label, ref, ...props }) {
  return (
    <label>
      {label}
      <input ref={ref} {...props} />
    </label>
  );
}

// Parent focuses the input via a ref, same as a DOM element.
function Form() {
  const inputRef = useRef(null);
  useEffect(() => inputRef.current?.focus(), []);
  return <TextInput label="Name" ref={inputRef} />;
}
```

## Common Mistakes

- Calling a hook conditionally, in a loop, or after an early `return`.
- Empty/incomplete dependency arrays that capture stale state or props.
- Using `useState` for a value that should be a `ref` (no render needed), causing extra renders.
- Reaching for `useMemo`/`useCallback` everywhere "for performance," adding overhead with no
  measured gain.
- Relying on memoization for correctness, so the app breaks when React discards the cache.
- Mutating `ref.current` and expecting the UI to update (refs do not trigger renders).
- Passing a freshly created promise to `use` on every render, restarting the fetch in a loop.
- Reaching for `useEffect` + `useState` for a submission that `useActionState` (with built-in
  `isPending`) or `useOptimistic` would handle more simply.
- Putting business logic in components instead of extracting a reusable custom hook.

## Production Tips

- Turn `react-hooks/rules-of-hooks` and `react-hooks/exhaustive-deps` into CI errors; they
  catch the two most common hook defects before review.
- When a dependency array fights you, prefer restructuring (updater form, move value inside,
  wrap in `useCallback`) over disabling the lint rule.

## AI Review Checklist

- Are all hooks called unconditionally at the top level of a component or custom hook?
- Does every effect/memo/callback dependency array list all values it reads?
- Are `useMemo`/`useCallback` justified by a memoized consumer or a proven-expensive cost?
- Is `useRef` used for cross-render mutable values that should not trigger a render?
- Is `useId` (not random) used for SSR-stable ids?
- Is any promise passed to `use` created outside render (prop/cache/loader), not inline?
- Do async submissions use `useActionState`/Actions instead of hand-rolled effect + flags?
- Is repeated stateful logic extracted into a custom hook rather than copy-pasted?

## Related

- `knowledge/react/06-state.md`
- `knowledge/react/07-lifecycle.md`
- `knowledge/react/09-custom-hooks.md`
- `knowledge/react/12-performance.md`
- `knowledge/react/10-context-api.md`
