---
id: react/24-design-patterns
topic: react
slug: design-patterns
title: "React Design Patterns"
type: doc
order: 24
status: ready
tags: [react, design-patterns]
related: [react/14-patterns, react/13-component-composition, react/09-custom-hooks, react/10-context-api, react/02-component-architecture]
when_to_use: "Read before applying a classic design pattern (provider, factory, reducer, observer) in React code."
---
# React Design Patterns

## Purpose

This document maps classic, language-agnostic design patterns onto idiomatic React:
the Provider pattern, custom-hook (strategy/facade) pattern, reducer (command) pattern,
factory pattern for polymorphic rendering, and external-store observer pattern. It
explains the React-native form of each and warns where a Gang-of-Four pattern imported
literally becomes an anti-pattern.

This is the conceptual complement to [patterns](14-patterns.md), which covers concrete
React idioms. Here the emphasis is on the *design intent* behind a structure and its
React-native expression, so you reach for the pattern only when its intent applies.

## Why It Matters

Design patterns are solutions to recurring problems, but React's model — functions,
hooks, immutable data, unidirectional flow — changes what the right solution looks like.
Porting an OOP pattern verbatim (Singleton classes, inheritance hierarchies, observer
subscriptions built by hand) fights the framework and produces code that leaks, re-renders
wrong, or breaks under concurrent rendering. Knowing the React-native form lets you keep
the intent while working *with* React instead of against it.

## Core Principles

- **Prefer composition and hooks over inheritance.** React has no UI inheritance; every
  GoF pattern that relied on subclassing has a hooks-and-composition equivalent.
- **State lives in React or an external store, never a hand-rolled global.** For observer
  patterns use `useSyncExternalStore` so React stays consistent under concurrent rendering.
- **Encapsulate behavior behind a hook (facade).** A custom hook is React's way to hide a
  strategy, a subscription, or a service behind a stable, testable interface.
- **Model complex transitions as a reducer (command pattern).** A reducer centralizes
  state transitions as named actions, making them testable and predictable.
- **Match the pattern to its intent.** If you cannot state the problem the pattern solves,
  you are adding structure, not removing complexity.

## Best Practices

- Use the **Provider pattern** ([Context](10-context-api.md)) to inject cross-cutting
  dependencies (theme, auth, config) — the DI container of React. Memoize the value.
- Wrap third-party services (analytics, a WebSocket, an SDK) in a **hook facade** so
  components depend on your stable interface, not the vendor API. Swapping the vendor
  touches one file.
- Express polymorphic rendering with a **factory/registry map** (`{ type: Component }`)
  instead of a `switch` per call site; adding a variant means one map entry.
- Reach for the **reducer pattern** when state has many actions or interdependent fields;
  the cost is boilerplate, so keep `useState` for simple, independent values.
- For state shared widely and updated often, use an **external store** subscribed via
  `useSyncExternalStore` (or a library) rather than Context — components then re-render
  only on the slice they read.

## Examples

**Good Example** — factory map + hook facade

```tsx
// Factory/registry: adding a block type is one entry, no call-site switch to edit.
const BLOCKS = {
  text: TextBlock,
  image: ImageBlock,
  video: VideoBlock,
} as const;

function Block({ type, ...props }: { type: keyof typeof BLOCKS } & Record<string, unknown>) {
  const Cmp = BLOCKS[type] ?? UnknownBlock; // fail safe on unknown types
  return <Cmp {...props} />;
}

// Facade hook: components depend on this interface, not the analytics vendor's SDK.
function useAnalytics() {
  return useMemo(() => ({
    track: (event: string, data?: object) => vendorSdk.capture(event, data),
  }), []);
}
```

**Bad Example** — hand-rolled singleton store + switch factory

```tsx
// Singleton mutable global: invisible to React, so components do not re-render on change,
// and it breaks under concurrent rendering / SSR (shared across requests).
const store = { user: null as User | null, listeners: [] as (() => void)[] };
export const setUser = (u: User) => { store.user = u; store.listeners.forEach((l) => l()); };

function Profile() {
  // Manual subscription: misses updates, leaks listeners, and tears during concurrent render.
  const [, force] = useReducer((n) => n + 1, 0);
  useEffect(() => { store.listeners.push(force); }, []); // never cleaned up

  // Switch factory duplicated at every call site; each new type edits every switch.
  switch (store.user?.role) {
    case "admin": return <AdminView />;
    case "user": return <UserView />;
    default: return null;
  }
}
```

## Common Mistakes

- Building a mutable global singleton for state instead of an external store React can observe.
- Hand-writing observer subscriptions instead of `useSyncExternalStore`, causing tearing/leaks.
- Porting inheritance hierarchies into React where composition or hooks fit natively.
- Repeating a `switch (type)` at many call sites instead of a factory/registry map.
- Using a reducer for one simple value, or `useState` for a tangle of interdependent fields.
- Depending on a vendor SDK directly throughout the app instead of behind a hook facade.

## Production Tips

- When choosing an external store, prefer a maintained library (Zustand, Redux Toolkit,
  Jotai) over a bespoke one; they already handle `useSyncExternalStore` correctly.
- Keep facades thin — a facade that grows business logic has become a service layer and
  should move out of the component tree into a module you can unit-test.

## AI Review Checklist

- Is shared/observable state in React state or an external store, not a mutable global?
- Are external subscriptions done via `useSyncExternalStore`, with cleanup, not by hand?
- Is dependency injection done through a memoized Provider?
- Are vendor services wrapped behind a hook facade so swaps stay local?
- Is polymorphic rendering a factory/registry map rather than duplicated switches?
- Does each applied pattern have a stated problem it solves, using its React-native form?

## Related

- `knowledge/react/14-patterns.md`
- `knowledge/react/13-component-composition.md`
- `knowledge/react/09-custom-hooks.md`
- `knowledge/react/10-context-api.md`
- `knowledge/react/02-component-architecture.md`
