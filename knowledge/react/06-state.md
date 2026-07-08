---
id: react/06-state
topic: react
slug: state
title: "State"
type: doc
order: 6
status: ready
tags: [react, state]
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
  should be computed in render. If you must initialize from a prop, understand it will not
  auto-update.
- Do not store derived data (totals, filtered lists, formatting) in state — recompute it,
  and memoize with `useMemo` only if profiling shows it is expensive.
- Group related fields into one state object or a reducer rather than a dozen `useState`
  calls that must stay in sync.

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

## Common Mistakes

- Mutating state directly (`arr.push`, `obj.x = 1`) and expecting a re-render.
- Reading a state variable immediately after `setState` and expecting the new value.
- Using `setX(x + 1)` in rapid succession instead of `setX(x => x + 1)`, dropping updates.
- Storing values that can be derived from other state/props, then keeping them in sync by hand.
- Copying props into `useState` and being surprised the copy ignores later prop changes.
- Lifting state to the top of the app when only two sibling components need it.

## Production Tips

- Reach for a reducer once state transitions have branches or invariants — it makes the
  logic testable in isolation and keeps components thin.
- For server data, prefer a data-fetching library's cache over hand-rolled `useState` +
  `useEffect`; server state has different rules (staleness, revalidation). See
  [data fetching](16-data-fetching.md).

## AI Review Checklist

- Is every state update immutable (new object/array), never an in-place mutation?
- Are dependent updates using the functional updater form `set(x => ...)`?
- Is any stored value actually derivable from existing state/props (and should be computed)?
- Is state lifted to the closest common ancestor, not higher than necessary?
- Does any code read a state value right after setting it, assuming the new value?
- Are related fields grouped (object/reducer) instead of many out-of-sync `useState` calls?

## Related

- `knowledge/react/08-hooks.md`
- `knowledge/react/05-props.md`
- `knowledge/react/11-rendering.md`
- `knowledge/react/18-state-management.md`
- `knowledge/react/04-components.md`
