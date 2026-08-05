---
id: react/10-context-api
topic: react
slug: context-api
title: "Context API"
type: doc
order: 10
status: ready
tags: [react, context-api, useContext, ThemeProvider, dispatch, ReactNode, useState, useReducer]
related: [react/06-state, react/08-hooks, react/09-custom-hooks, react/18-state-management, react/12-performance]
when_to_use: "Read before sharing state across the tree with Context or when a Provider is causing re-render problems."
---
# Context API

## Purpose

This document defines how to use React Context to pass data through the component
tree without threading props at every level. It covers when Context is the right
tool, how to structure a Provider, and how to avoid the re-render and coupling
problems that make Context misused more often than it is used well.

Context solves *prop drilling* — passing a value through components that do not use
it just to reach one that does. It is not a state manager and not a substitute for
[global state libraries](18-state-management.md); it is a transport mechanism.

## Why It Matters

Context is deceptively simple to add and expensive to get wrong. Every component
that consumes a Context re-renders when the Context *value* changes — and a naive
Provider recreates its value object on every render, so the entire subtree re-renders
on every parent render. This turns a convenience into a performance sink that is
invisible until the app grows. Because Context also couples consumers to a specific
Provider, overusing it makes components hard to test and reuse in isolation.

## Core Principles

- **Reach for props first.** Context is justified when a value is genuinely global to
  a subtree (theme, current user, locale) or drilled through 3+ layers. One or two
  levels of props are clearer than a Context.
- **A Context value change re-renders every consumer.** Treat the value as a broadcast:
  keep it stable and split it by update frequency.
- **Separate state from dispatch.** Values that change often and functions that never
  change belong in different Contexts, so action-only consumers do not re-render.
- **Provide a typed default and a guard hook.** Never let a component silently consume
  a Context outside its Provider.
- **Context is not for server data.** Fetched, cached, revalidated data belongs in a
  data layer (see [data fetching](16-data-fetching.md)), not a Context.

## Best Practices

- Memoize the Provider `value` with `useMemo`, keyed on its real dependencies, so it is
  not a new object every render. The cost of skipping this is a full-subtree re-render.
- Wrap `useContext` in a custom hook that throws if the value is the sentinel default.
  This turns "renders nothing / undefined crash" into a clear error at the call site.
- Split a large Context into focused Contexts (`ThemeContext`, `AuthContext`) rather
  than one `AppContext`. Each consumer then subscribes only to what it uses.
- Keep the Provider close to where the value is needed, not always at the app root.
  A narrower Provider re-renders a smaller tree.
- For frequently-changing values with many consumers, prefer an external store
  (`useSyncExternalStore`, Zustand, Redux) that lets components subscribe to slices.
- In React 19, render the context object directly as the provider: `<ThemeContext value={x}>`.
  `<ThemeContext.Provider>` still works but is deprecated; new code should drop `.Provider`.
- Prefer React 19's `use(Context)` over `useContext` when you must read a Context conditionally
  (inside an `if` or early-return branch). `use` is exempt from the rules-of-hooks call-order
  restriction; `useContext` is not.

## React 19 Provider and `use`

React 19 lets the Context object *be* the Provider, and adds `use(Context)` — a reader
that, unlike `useContext`, may be called conditionally.

```tsx
import { createContext, use, useState } from "react";

const ThemeContext = createContext<"light" | "dark" | null>(null);

function App() {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  // React 19: no `.Provider`. `<ThemeContext.Provider>` still compiles but is deprecated.
  return (
    <ThemeContext value={theme}>
      <Toolbar showThemedIcon />
    </ThemeContext>
  );
}

function Toolbar({ showThemedIcon }: { showThemedIcon: boolean }) {
  // `use` can sit behind a condition — `useContext` here would violate rules of hooks.
  const theme = showThemedIcon ? use(ThemeContext) : "light";
  if (theme === null) throw new Error("Toolbar must render under <ThemeContext>");
  return <Icon variant={theme} />;
}
```

## Examples

**Good Example** — split value/dispatch, memoized value, guard hook

```tsx
type Theme = "light" | "dark";
const ThemeStateContext = createContext<Theme | null>(null);
const ThemeDispatchContext = createContext<(t: Theme) => void>(() => {});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light");
  // setTheme is stable, so dispatch consumers never re-render on theme change.
  // React 19 provider syntax: render the Context object directly, no `.Provider`.
  return (
    <ThemeStateContext value={theme}>
      <ThemeDispatchContext value={setTheme}>
        {children}
      </ThemeDispatchContext>
    </ThemeStateContext>
  );
}

// Guard hook: fail loudly if used outside the Provider.
export function useTheme() {
  const theme = useContext(ThemeStateContext);
  if (theme === null) throw new Error("useTheme must be used within <ThemeProvider>");
  return theme;
}
```

**Bad Example** — one Context, new value object every render, no guard

```tsx
const AppContext = createContext<any>(undefined);

export function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState("light");
  // New object every render → every consumer re-renders even if nothing they use changed.
  // Mixing user + theme + setters means a theme toggle re-renders user-only components.
  return (
    <AppContext.Provider value={{ user, setUser, theme, setTheme }}>
      {children}
    </AppContext.Provider>
  );
}

// No guard: outside the Provider this is `undefined` and crashes deep in render.
export const useApp = () => useContext(AppContext);
```

**Good Example** — `useReducer` with a stable `dispatch` in its own Context

The reducer scales the split-context pattern: state lives in one Context, and `dispatch`
(which React guarantees is stable for the component's lifetime) lives in another, so
action-only consumers never re-render when state changes.

```tsx
import { createContext, use, useReducer, type Dispatch, type ReactNode } from "react";

type CartItem = { id: string; qty: number };
type CartState = { items: CartItem[] };
type CartAction =
  | { type: "add"; id: string }
  | { type: "remove"; id: string };

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case "add": {
      const existing = state.items.find((i) => i.id === action.id);
      return existing
        ? { items: state.items.map((i) => (i.id === action.id ? { ...i, qty: i.qty + 1 } : i)) }
        : { items: [...state.items, { id: action.id, qty: 1 }] };
    }
    case "remove":
      return { items: state.items.filter((i) => i.id !== action.id) };
  }
}

const CartStateContext = createContext<CartState | null>(null);
const CartDispatchContext = createContext<Dispatch<CartAction> | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, { items: [] });
  // No useMemo needed: `state` is a new reference only when it actually changes,
  // and `dispatch` is referentially stable across renders.
  return (
    <CartStateContext value={state}>
      <CartDispatchContext value={dispatch}>{children}</CartDispatchContext>
    </CartStateContext>
  );
}

export function useCart() {
  const state = use(CartStateContext);
  if (state === null) throw new Error("useCart must be used within <CartProvider>");
  return state;
}

export function useCartDispatch() {
  const dispatch = use(CartDispatchContext);
  if (dispatch === null) throw new Error("useCartDispatch must be used within <CartProvider>");
  return dispatch;
}

// An "Add to cart" button reads only dispatch — it never re-renders when the cart changes.
function AddButton({ id }: { id: string }) {
  const dispatch = useCartDispatch();
  return <button onClick={() => dispatch({ type: "add", id })}>Add</button>;
}
```

**Bad Example** — a hot value in Context re-renders every consumer on every change

```tsx
const MouseContext = createContext({ x: 0, y: 0 });

function MouseProvider({ children }: { children: React.ReactNode }) {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  // Fires on every mousemove. Every consumer of MouseContext re-renders ~60x/sec,
  // even a component that only reads `pos.x` while `pos.y` changed.
  useEffect(() => {
    const onMove = (e: MouseEvent) => setPos({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, []);
  return <MouseContext value={pos}>{children}</MouseContext>;
}
```

For a value like this, expose an external store and let each component subscribe to the
exact slice it needs with `useSyncExternalStore`, so a change to `y` never re-renders an
`x`-only reader. Context has no built-in selector; every consumer gets the whole value.

## Common Mistakes

- Passing an inline object/array as `value` without `useMemo`, re-rendering the whole subtree.
- Bundling unrelated concerns into one "god Context," coupling and re-rendering everything.
- Using Context to hold server/cache data that needs revalidation and loading states.
- No default guard, so consuming outside the Provider fails cryptically instead of clearly.
- Reaching for Context to avoid two levels of props, adding indirection for no gain.
- Storing rapidly-changing values (mouse position, form keystrokes) in Context with many consumers.

## Production Tips

- Profile with the React DevTools "highlight updates" feature to catch Provider-wide
  re-renders before they reach users.
- Co-locate the Provider, its hooks, and its types in one module so consumers import a
  clean API and never touch the raw `createContext` object.

## AI Review Checklist

- Is the Provider `value` memoized with correct dependencies?
- Are frequently-changing state and stable dispatch split into separate Contexts?
- Does a guard hook throw when consumed outside its Provider?
- Is Context used for genuinely shared data, not to skip one or two prop levels?
- Is server/cache data kept out of Context and in a proper data layer?
- Are focused Contexts used instead of a single monolithic app Context?

## Related

- `knowledge/react/06-state.md`
- `knowledge/react/08-hooks.md`
- `knowledge/react/09-custom-hooks.md`
- `knowledge/react/18-state-management.md`
- `knowledge/react/12-performance.md`
