---
id: react/04-components
topic: react
slug: components
title: "React Components"
type: doc
order: 4
status: ready
tags: [react, components]
related: [react/05-props, react/06-state, react/08-hooks, react/13-component-composition, react/11-rendering]
when_to_use: "Read before creating a new component or refactoring how one is structured."
---
# React Components

## Purpose

This document defines what a React component is and how to write one well. A component is
a function that takes props and returns a description of UI (React elements). Components
are the unit of composition, reuse, and testing in React. This page covers their contract,
boundaries, and the rules that keep them predictable.

## Why It Matters

Components are where the rendering model meets your code, so their discipline determines
whether the app is debuggable. A component that mutates props, runs side effects during
render, or does ten things at once produces bugs that look like React bugs but are yours:
stale UI, duplicated fetches, impossible-to-test tangles. Small, pure, single-purpose
components are the difference between an app you can reason about and one you can only poke.

## Core Principles

- **A component is a pure function of its inputs.** Same props and state → same output,
  with no side effects during render. This is what lets React call it whenever it needs to.
- **Props are read-only.** A component must never mutate its props; they belong to the
  parent. To change data, call a callback the parent passed down.
- **One responsibility per component.** If you cannot name what a component does in one
  phrase, split it. Composition, not size, is how React scales.
- **Function components only.** Hooks give function components everything classes offered.
  Do not write new class components.

## Best Practices

- Name components in `PascalCase`; the name should describe what it renders (`UserCard`,
  not `Card2`). React uses capitalization to distinguish components from DOM tags.
- Keep the render path pure: no fetching, no subscriptions, no DOM writes, no `Math.random`
  or `Date.now` that affects output. Move those into event handlers or effects.
- Destructure props in the signature for a readable contract:
  `function UserCard({ name, avatarUrl })`.
- Provide sensible defaults via default parameters, not by mutating props.
- Extract a child component when a piece of UI has its own state or is reused; extract a
  [custom hook](09-custom-hooks.md) when logic (not markup) is reused.
- Prefer composition (passing `children` / render props) over configuration flags that
  balloon into a dozen booleans. See [composition](13-component-composition.md).
- Wrap risky subtrees in an [error boundary](19-error-handling.md) so one failure does not
  blank the whole app.

## Examples

**Good Example** — pure, single-purpose, props read-only

```jsx
// Presentational: derives everything from props, causes no side effects in render.
function PriceTag({ cents, currency = "USD" }) {
  const formatted = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(cents / 100); // pure computation from props — safe during render

  return <span className="price">{formatted}</span>;
}
```

**Bad Example** — mutates props, side effect in render

```jsx
function PriceTag({ item }) {
  item.viewed = true;               // mutates a prop → corrupts parent's data
  fetch(`/track?id=${item.id}`);    // side effect on every render → duplicate requests
  return <span>{item.price}</span>; // also: does two jobs (display + tracking)
}
```

## Common Mistakes

- Mutating props or objects received from a parent instead of requesting a change via callback.
- Doing side effects (fetch, subscribe, log, navigate) directly in the component body.
- Lowercase component names, which React treats as literal HTML tags and renders wrong.
- One giant component holding unrelated state and markup, impossible to test in isolation.
- Defining child components inside another component's body, recreating them every render
  and destroying their state.
- Writing new class components when function components + hooks are the standard.

## Production Tips

- Co-locate a component with its test and styles; a component you cannot test alone is too
  entangled.
- Give components a clear presentational-vs-container split: dumb components render props,
  container components own state and data — it keeps the render tree easy to reason about.

## AI Review Checklist

- Is the component a pure function of props/state, with no side effects during render?
- Are props treated as read-only, with changes requested through callbacks?
- Does the component have a single, nameable responsibility?
- Is it a function component (not a new class component)?
- Are child components defined at module scope, not inside another component's body?
- Is the component name `PascalCase` and descriptive?

## Related

- `knowledge/react/05-props.md`
- `knowledge/react/06-state.md`
- `knowledge/react/08-hooks.md`
- `knowledge/react/13-component-composition.md`
- `knowledge/react/11-rendering.md`
