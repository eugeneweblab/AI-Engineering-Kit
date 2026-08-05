---
id: react/06-state
topic: react
slug: state
title: "State"
type: doc
order: 6
status: ready
tags: [react, state, useState, dispatch, useOptimistic, setState, setItems, useReducer]
related: [react/08-hooks, react/05-props, react/11-rendering, react/18-state-management, react/04-components]
when_to_use: "Read before adding, updating, or lifting component state, or debugging a stale/lost-state bug."
---
# State

## Purpose

This document defines how to model and update state — the data a component remembers
between renders. State drives the UI: when it changes, React re-renders. The goal here is
state that is minimal, immutable in how you update it, and placed at the right level of the
tree so updates are correct and re-renders are contained.

## Why It Matters

State is the most common source of subtle React bugs. Mutating it directly means React
never re-renders and the screen goes stale. Deriving state into more state means two copies
that drift apart. Reading state right after `setState` gives you the old value because
updates are asynchronous and batched. Putting state too high re-renders half the app; too
low and siblings cannot share it. None of these throw an error — they just render the wrong
thing.

## Core Principles

- **State is immutable to you.** Never mutate the current state object or array. Always
  produce a new value and pass it to the setter, so React can detect the change by identity.
- **Updates are asynchronous and batched.** `setState` schedules a render; it does not
  change the variable now. When the next value depends on the previous, use the updater
  function form.
- **Keep state minimal.** Store the smallest source of truth. Anything computable from
  existing state or props should be computed during render, not stored.
- **Lift state only as high as needed.** Put shared state in the closest common ancestor of
  the components that use it — no higher, to keep re-renders local.

## Best Practices

- Use `useState` for independent values; use `useReducer` when several values change
  together or the next state depends on complex logic — a reducer centralizes transitions.
- For dependent updates, use the functional updater: `setCount(c => c + 1)`. It reads the
  latest queued value and is safe inside loops, effects, and batches.
- Update objects and arrays immutably: spread (`{ ...obj, x }`), `map`, `filter`, `concat`.
  Never `push`, `splice`, or assign to a field of existing state.
- Do not copy props into state unless you deliberately want a snapshot; a prop-derived value
  should be computed in render. If you must reset local state when a prop changes, give the
  component a `key` that changes with the prop instead of syncing inside an effect.
- Do not store derived data (totals, filtered lists, formatting) in state — recompute it,
  and memoize with `useMemo` only if profiling shows it is expensive.
- Group related fields into one state object or a reducer rather than a dozen `useState`
  calls that must stay in sync.
- Pass a function to `useState` for expensive initial values (`useState(() => build())`) so
  the initializer runs once, not on every render.
- For an optimistic UI during an async mutation, use React 19's `useOptimistic` rather than
  hand-managing a temporary "pending" copy in `useState`.

## Examples

**Good Example** — immutable update, functional updater

```jsx
function Cart() {
  const [items, setItems] = useState([]);

  function addItem(item) {
    // New array (immutable) so React sees a changed reference and re-renders.
    setItems((prev) => [...prev, item]); // updater form: safe if called repeatedly
  }

  // Derived, not stored: recomputed each render, can never go stale.
  const total = items.reduce((sum, i) => sum + i.price, 0);

  return <Summary total={total} onAdd={addItem} />;
}
```

**Bad Example** — mutation, stale read, redundant state

```jsx
function Cart() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0); // redundant: derivable from items → can drift

  function addItem(item) {
    items.push(item);          // mutates existing array → React sees no change, no re-render
    setItems(items);           // same reference → often ignored
    setTotal(total + item.price); // reads stale `total`; two sources of truth diverge
  }

  return <Summary total={total} onAdd={addItem} />;
}
```

**Good Example** — lazy initializer runs once, not every render

```jsx
function Editor({ documentId }) {
  // Passing a function: React calls it only on the first render.
  // `useState(parseDraft(documentId))` would re-parse on EVERY render and throw the result away.
  const [draft, setDraft] = useState(() => parseDraft(documentId));

  return <textarea value={draft.body} onChange={(e) => setDraft((d) => ({ ...d, body: e.target.value }))} />;
}
```

**Good Example** — grouped state with a reducer when fields change together

Reach for `useReducer` when the next state depends on the previous in branchy ways, or when
several fields must move as one. Transitions live in a pure function you can unit-test.

```jsx
import { useReducer } from "react";

const initial = { status: "idle", query: "", results: [], error: null };

function reducer(state, action) {
  switch (action.type) {
    case "search":
      return { ...state, status: "loading", query: action.query, error: null };
    case "success":
      return { ...state, status: "done", results: action.results };
    case "failure":
      return { ...state, status: "error", error: action.error, results: [] };
    case "reset":
      return initial;
    default:
      return state; // unknown action: return the same reference, no re-render
  }
}

function Search() {
  const [state, dispatch] = useReducer(reducer, initial);

  async function run(query) {
    dispatch({ type: "search", query });
    try {
      const results = await fetchResults(query);
      dispatch({ type: "success", results });
    } catch (error) {
      dispatch({ type: "failure", error });
    }
  }

  return <SearchView state={state} onSearch={run} onReset={() => dispatch({ type: "reset" })} />;
}
```

**Good Example** — reset state on prop change with `key`, not an effect

```jsx
// Parent: changing the key remounts ProfileForm, so its internal useState
// re-initializes cleanly. No effect that "syncs" a prop into state.
function ProfilePage({ userId }) {
  return <ProfileForm key={userId} userId={userId} />;
}

function ProfileForm({ userId }) {
  // Fresh state per userId because the key change remounts this component.
  const [name, setName] = useState("");
  return <input value={name} onChange={(e) => setName(e.target.value)} />;
}
```

**Bad Example** — syncing a prop into state with an effect

```jsx
function ProfileForm({ userId, initialName }) {
  const [name, setName] = useState(initialName);

  // Anti-pattern: an extra render, a flash of stale input, and easy to get the deps wrong.
  useEffect(() => {
    setName(initialName);
  }, [initialName]);

  return <input value={name} onChange={(e) => setName(e.target.value)} />;
}
```

**Good Example** — optimistic UI with React 19 `useOptimistic`

`useOptimistic` shows the expected result immediately, then React automatically reverts to the
real `messages` value once the awaited action resolves (or fails) — no manual rollback state.

```jsx
import { useOptimistic, useState } from "react";

function Thread({ initialMessages, send }) {
  const [messages, setMessages] = useState(initialMessages);
  const [optimistic, addOptimistic] = useOptimistic(
    messages,
    (current, text) => [...current, { text, pending: true }]
  );

  async function formAction(formData) {
    const text = formData.get("text");
    addOptimistic(text);                 // shows instantly with pending: true
    const saved = await send(text);      // real network round-trip
    setMessages((prev) => [...prev, saved]); // commit the confirmed message
  }

  return (
    <form action={formAction}>
      {optimistic.map((m, i) => (
        <div key={i} style={{ opacity: m.pending ? 0.5 : 1 }}>{m.text}</div>
      ))}
      <input name="text" />
    </form>
  );
}
```

## Common Mistakes

- Mutating state directly (`arr.push`, `obj.x = 1`) and expecting a re-render.
- Reading a state variable immediately after `setState` and expecting the new value.
- Using `setX(x + 1)` in rapid succession instead of `setX(x => x + 1)`, dropping updates.
- Storing values that can be derived from other state/props, then keeping them in sync by hand.
- Copying props into `useState` and being surprised the copy ignores later prop changes.
- Writing a `useEffect` that calls `setState` to mirror a prop — prefer a `key` to reset, or
  compute the value during render.
- Calling `useState(expensiveInit())` instead of `useState(() => expensiveInit())`, so the
  expensive call runs on every render.
- Lifting state to the top of the app when only two sibling components need it.

## Production Tips

- Reach for a reducer once state transitions have branches or invariants — it makes the
  logic testable in isolation and keeps components thin.
- For server data, prefer a data-fetching library's cache over hand-rolled `useState` +
  `useEffect`; server state has different rules (staleness, revalidation). See
  [data fetching](16-data-fetching.md).
- In React 18+, all updates inside events, promises, timeouts, and native handlers are
  batched into one render automatically — you rarely need to combine setters by hand. If you
  ever need to opt out (e.g. read a fresh DOM measurement between updates), reach for
  `flushSync` from `react-dom`, sparingly.
- For form submissions that drive state, prefer a form `action` with `useActionState`
  (pending flag + result) over a manual `isSubmitting` boolean in `useState`; pair it with
  `useOptimistic` for instant feedback. See [forms](15-forms.md).
- Keep reducers pure: no fetches, no `Date.now()`, no mutation of `state`. Side effects belong
  in the action creator/handler, not the reducer — that is what keeps transitions testable.

## AI Review Checklist

- Is every state update immutable (new object/array), never an in-place mutation?
- Are dependent updates using the functional updater form `set(x => ...)`?
- Is any stored value actually derivable from existing state/props (and should be computed)?
- Is state lifted to the closest common ancestor, not higher than necessary?
- Does any code read a state value right after setting it, assuming the new value?
- Are related fields grouped (object/reducer) instead of many out-of-sync `useState` calls?
- Is prop-driven reset done with a `key` rather than a `setState`-in-`useEffect` mirror?
- Do expensive initial values use the lazy form `useState(() => ...)`?
- Are reducers pure (no fetches, timers, or mutation of the incoming state)?

## Related

- `knowledge/react/08-hooks.md`
- `knowledge/react/05-props.md`
- `knowledge/react/11-rendering.md`
- `knowledge/react/18-state-management.md`
- `knowledge/react/04-components.md`
