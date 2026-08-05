---
id: react/26-best-practices
topic: react
slug: best-practices
title: "React Best Practices"
type: doc
order: 26
status: ready
tags: [react, best-practices, toggle, Cart, useCallback, useMemo, useEffect, setTotal]
related: [react/08-hooks, react/12-performance, react/06-state, react/100-common-antipatterns, react/23-code-style]
when_to_use: "Read before writing or reviewing any React component to check it against the baseline rules."
---
# React Best Practices

## Purpose

This document is the baseline checklist for everyday React code: how to structure
components, manage state, use hooks correctly, and keep renders predictable. It
consolidates the rules that appear across the deeper topic docs into one place an
agent can apply to any component. Where a rule needs full treatment it links out;
here it states the rule and the reason.

These are not stylistic preferences. Each one prevents a concrete class of bug —
stale closures, unnecessary re-renders, unmount crashes, or state that drifts out
of sync.

## Why It Matters

Most React bugs are not exotic. They come from breaking a small set of rules: mutating
state, misusing effects, missing keys, deriving state you should have computed. These
mistakes compile and often pass a quick manual test, then fail under real conditions —
concurrent renders, fast navigation, slow networks. Following the baseline is cheaper
than debugging the class of failure it prevents, because the failures are intermittent
and hard to reproduce.

## Core Principles

- **Keep components pure.** Rendering must not mutate props, state, or module
  variables, and must produce the same output for the same inputs. Side effects go in
  event handlers or effects — never in the render body.
- **Derive, don't duplicate.** If a value can be computed from existing state or props,
  compute it during render. Copying it into its own state guarantees it will drift.
- **State is immutable.** Never mutate state in place; create a new value so React can
  detect the change and re-render. Mutation causes skipped renders and shared-reference bugs.
- **Effects are for synchronization, not logic.** Use an effect only to sync with an
  external system (DOM, network, subscription). User actions belong in event handlers.
- **Lift state only as far as it must go.** Colocate state with the component that uses
  it; lift it to the closest common ancestor when siblings need to share it — no higher.

## Best Practices

- Give lists stable, data-derived `key`s (an id), never the array index for dynamic lists —
  index keys corrupt state on reorder or deletion. See [rendering](11-rendering.md).
- List every reactive value an effect reads in its dependency array; a lint-suppressed
  empty array hides stale-closure bugs. See [hooks](08-hooks.md).
- Reach for `useMemo`/`useCallback` only when profiling shows a real cost or a stable
  reference is required by a dependency array — premature memoization adds noise. See
  [performance](12-performance.md).
- Prefer controlled inputs with a single source of truth; mixing controlled and
  uncontrolled causes React warnings and lost keystrokes. See [forms](15-forms.md).
- Extract repeated stateful logic into [custom hooks](09-custom-hooks.md) rather than
  copy-pasting effects.
- Type props explicitly; avoid `any`. A precise prop type is the cheapest documentation
  and catches misuse at compile time.
- Handle loading, empty, and error states for every async view — not just the happy path.

## Examples

**Good Example** — derived value, immutable update, pure render

```tsx
function Cart({ items }: { items: Item[] }) {
  // Derived during render — always in sync, no extra state to keep consistent.
  const total = items.reduce((sum, i) => sum + i.price, 0);
  const [selected, setSelected] = useState<string[]>([]);

  function toggle(id: string) {
    // New array, not a mutation → React sees the change and re-renders.
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }
  return <Summary total={total} selected={selected} onToggle={toggle} />;
}
```

**Bad Example** — duplicated state, mutation, effect misused for derivation

```tsx
function Cart({ items }: { items: Item[] }) {
  const [total, setTotal] = useState(0);
  const [selected, setSelected] = useState<string[]>([]);

  // Extra render + a frame where total is stale; derive it instead.
  useEffect(() => {
    setTotal(items.reduce((s, i) => s + i.price, 0));
  }, [items]);

  function toggle(id: string) {
    selected.push(id);      // mutates state in place → React may skip the render
    setSelected(selected);  // same reference → no re-render
  }
  return <Summary total={total} selected={selected} onToggle={toggle} />;
}
```

## Common Mistakes

- Storing derived data in state and syncing it with an effect instead of computing it.
- Mutating arrays/objects in state (`push`, `x.y = z`) rather than replacing them.
- Using the array index as a key for a reorderable or filterable list.
- Omitting dependencies from `useEffect`/`useCallback` and suppressing the lint warning.
- Putting event-driven logic in an effect that watches a state flag.
- Wrapping everything in `useMemo`/`useCallback` before measuring.

## AI Review Checklist

- Is the render body free of mutations and side effects?
- Is every stateful value the single source of truth, with derived values computed?
- Are all state updates immutable?
- Do lists use stable, data-derived keys?
- Are effect dependency arrays complete and honest?
- Are memoization hooks justified by a real cost or a required stable reference?

## Related

- `knowledge/react/08-hooks.md`
- `knowledge/react/12-performance.md`
- `knowledge/react/06-state.md`
- `knowledge/react/100-common-antipatterns.md`
- `knowledge/react/23-code-style.md`
