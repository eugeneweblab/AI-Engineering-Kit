---
id: react/14-patterns
topic: react
slug: patterns
title: "Patterns"
type: doc
order: 14
status: ready
tags: [react, patterns]
related: [react/13-component-composition, react/24-design-patterns, react/09-custom-hooks, react/05-props, react/10-context-api]
when_to_use: "Read before choosing how to structure a reusable component or share logic across components."
---
# Patterns

## Purpose

This document catalogs the React-specific patterns an agent should know by name and
apply deliberately: controlled vs. uncontrolled components, container/presentational
separation, render props, compound components, and the state-reducer pattern. It
explains what each solves and, just as important, when *not* to use it.

These are idioms, not laws. Each exists to solve a concrete problem; applying one where
its problem does not exist adds indirection. For the broader, language-agnostic design
patterns as they map to React, see [design patterns](24-design-patterns.md).

## Why It Matters

Patterns are shared vocabulary. When code follows a recognized pattern, a reader knows
its shape before reading the details, and a reviewer can spot when it is applied wrong.
The failure mode is cargo-culting: reaching for a render prop or an HOC because it feels
advanced, when a plain prop or hook would be clearer. The best React code today uses the
*fewest* patterns that solve the problem — usually hooks plus composition.

## Core Principles

- **Prefer hooks and composition over older patterns.** Render props and HOCs mostly
  solved logic-sharing before hooks existed. In new code, a custom hook is clearer.
- **Controlled by default; uncontrolled for simple, isolated inputs.** Owning state in
  React makes it predictable; let the DOM own it only when nothing else needs to read it.
- **Separate what-to-render from how-to-get-data.** Presentational components take props
  and render; data/behavior lives in hooks or container components.
- **Use compound components when parts must coordinate.** They give the caller layout
  freedom while the parent manages shared state.
- **Name the pattern you use.** If you cannot say which problem it solves, you probably
  do not need it.

## Best Practices

- Make form inputs **controlled** (`value` + `onChange`) when their value is validated,
  submitted, or drives other UI. Use **uncontrolled** (`defaultValue` + ref) only for
  fire-and-forget inputs; the trade-off is you lose React-side visibility into the value.
- Extract logic-sharing into a **custom hook** rather than a Higher-Order Component or
  render prop. Hooks compose without wrapper nesting or prop-name collisions.
- Keep **presentational components pure**: props in, JSX out, no fetching or global reads.
  This makes them trivial to test and reuse. Put side effects in containers/hooks.
- Reach for the **state-reducer pattern** (expose a reducer so callers can override
  transitions) only for genuinely reusable, behavior-rich components; it is overkill
  for app-specific UI.
- Do not stack Higher-Order Components; each layer obscures the tree and the prop origin.

## Examples

**Good Example** — controlled input + logic in a custom hook

```tsx
// Reusable logic lives in a hook: no wrapper components, no prop collisions.
function useToggle(initial = false) {
  const [on, setOn] = useState(initial);
  const toggle = useCallback(() => setOn((v) => !v), []);
  return { on, toggle };
}

// Controlled input: React owns the value, so it can be validated and submitted.
function SearchBox({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return <input value={value} onChange={(e) => onChange(e.target.value)} />;
}

function Panel() {
  const { on, toggle } = useToggle();
  const [query, setQuery] = useState("");
  return (
    <>
      <button onClick={toggle}>{on ? "Hide" : "Show"}</button>
      {on && <SearchBox value={query} onChange={setQuery} />}
    </>
  );
}
```

**Bad Example** — render prop + HOC where a hook belongs

```tsx
// A render prop just to share toggle state — pure ceremony now that hooks exist.
function Toggle({ children }: { children: (api: { on: boolean; toggle: () => void }) => JSX.Element }) {
  const [on, setOn] = useState(false);
  return children({ on, toggle: () => setOn((v) => !v) });
}

// Then wrapped in an HOC that injects a prop — nesting and indirection for no benefit.
const withUser = (C: any) => (props: any) => <C {...props} user={useContext(UserContext)} />;

// Caller: two layers of wrapping to do what one hook call would.
const Panel = withUser(({ user }: any) => (
  <Toggle>{({ on, toggle }) => <button onClick={toggle}>{on ? user.name : "?"}</button>}</Toggle>
));
```

## Common Mistakes

- Using render props or HOCs for logic that a custom hook shares more cleanly.
- Making inputs uncontrolled and then needing their value elsewhere, forcing ref hacks.
- Merging data fetching into presentational components, killing their reusability and testability.
- Stacking multiple HOCs so prop origins and the component tree become unreadable.
- Applying the state-reducer pattern to one-off app UI, adding indirection with no reuse payoff.
- Inventing a "pattern" that is really just an under-designed component with too many props.

## Production Tips

- When you find the same `useState`/`useEffect` block in three components, extract a hook —
  that is the pattern earning its keep.
- Prefer patterns your team already uses; consistency beats cleverness for maintainability.

## AI Review Checklist

- Is logic-sharing done with a custom hook rather than an HOC or render prop?
- Are inputs controlled when their value is validated, submitted, or read elsewhere?
- Are presentational components free of fetching and global reads?
- Are compound components used where parts must coordinate, instead of prop drilling?
- Is each pattern tied to a concrete problem it solves, not applied speculatively?
- Are HOCs left un-stacked and shallow?

## Related

- `knowledge/react/13-component-composition.md`
- `knowledge/react/24-design-patterns.md`
- `knowledge/react/09-custom-hooks.md`
- `knowledge/react/05-props.md`
- `knowledge/react/10-context-api.md`
