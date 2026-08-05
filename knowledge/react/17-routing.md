---
id: react/17-routing
topic: react
slug: routing
title: "React Routing"
type: doc
order: 17
status: ready
tags: [react, routing]
related: [react/16-data-fetching, react/19-error-handling, react/18-state-management, react/12-performance, react/28-production]
when_to_use: "Read before adding routes, navigation, route-level data loading, or protected pages."
---
# React Routing

## Purpose

This document defines how to structure client-side and server-side routing in a React
application: declaring routes, navigating, reading URL params, loading data per route,
guarding access, and splitting code by route. It targets modern React Router (v7 /
framework mode) and the equivalent conventions in Next.js and TanStack Router.

The URL is application state — the one piece of state users bookmark, share, and expect
the back button to respect. Routing is how you keep the URL and the rendered UI in sync.

## Why It Matters

Routing decisions ripple through the whole app: bundle size (code splitting is route-based),
data loading (fetch at the route boundary or waterfall inside components), auth (guard at
the edge or leak protected UI), and accessibility (focus and scroll management on
navigation). Get it wrong and you get flash-of-unauthenticated-content, broken back
buttons, giant initial bundles, and layout that re-mounts on every navigation. These are
architectural, not cosmetic — hard to retrofit once the app is built around them.

## Core Principles

- **The URL is the source of truth for navigational state.** Derive UI from route params
  and search params; do not shadow them in component state that can drift.
- **Load data at the route boundary.** Route loaders fetch in parallel before render,
  avoiding the request waterfall you get when each nested component fetches on mount.
- **Guard on the server or at the route, never only in the component.** A client-only
  check renders protected UI before redirecting — the data is already in the bundle.
- **Split code by route.** Lazy-load route components so the initial bundle carries only
  the landing route, not the whole app.
- **Navigation must be accessible.** Move focus and reset scroll on route change, or
  screen-reader and keyboard users are stranded on the old position.

## Best Practices

- Use `<Link>`/`<NavLink>` for internal navigation, never `<a href>` — anchors trigger a
  full page reload, discarding app state and re-downloading everything.
- Read params with the router's typed hooks (`useParams`, `useSearchParams`) rather than
  parsing `window.location`; the router keeps them in sync with renders.
- Keep filter/sort/pagination state in **search params**, not component state, so it is
  shareable and survives refresh. Read/write via `useSearchParams`.
- Put shared chrome (nav, sidebar) in a **layout route** so it does not re-mount on child
  navigation — this preserves scroll and avoids re-fetching layout data.
- Define an **error boundary / errorElement per route** so a failure in one route shows a
  local fallback instead of blanking the whole app (see [error handling](19-error-handling.md)).
- Enforce auth in a loader that throws a redirect *before* the protected component renders.

## Examples

**Good Example** — route loader, guard before render, lazy route, semantic nav

```tsx
import { createBrowserRouter, redirect, Link, useLoaderData } from "react-router";

const router = createBrowserRouter([
  {
    path: "/",
    Component: RootLayout, // shared chrome; does not re-mount on child nav
    children: [
      {
        path: "dashboard",
        // Guard + data run BEFORE the component renders; no protected UI leaks.
        loader: async () => {
          const user = await getUser();
          if (!user) throw redirect("/login");
          return { stats: await fetchStats(user.id) }; // parallel, no in-component waterfall
        },
        lazy: () => import("./routes/dashboard"), // route-level code split
      },
    ],
  },
]);

function Nav() {
  // <Link> does client navigation; no full reload, app state preserved.
  return <Link to="/dashboard">Dashboard</Link>;
}
```

**Bad Example** — anchor reload, client-only guard, fetch waterfall

```tsx
function Dashboard() {
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => { getUser().then(setUser); }, []);          // fetch 1
  useEffect(() => {
    if (user) fetchStats(user.id).then(setStats);             // fetch 2 waits on fetch 1 → waterfall
  }, [user]);

  // Client-only guard: the component already rendered and its code is in the bundle
  // before this redirect fires — a flash of protected UI.
  if (user === null) return null;
  if (!user.isAdmin) { window.location.href = "/login"; return null; }

  // Full page reload discards all app state and re-downloads the bundle.
  return <a href="/settings">Settings</a>;
}
```

**Good Example** — filter/sort/pagination live in the URL via `useSearchParams`

```tsx
import { useSearchParams } from "react-router";

function ProductList() {
  const [params, setParams] = useSearchParams();
  const category = params.get("category") ?? "all";
  const page = Number(params.get("page") ?? "1");

  // The URL is the single source of truth — bookmarkable, shareable, refresh-safe.
  function update(next: Record<string, string>) {
    setParams(
      (prev) => {
        for (const [k, v] of Object.entries(next)) prev.set(k, v);
        return prev; // functional update preserves unrelated params (e.g. sort)
      },
      { replace: true }, // don't push a history entry per keystroke/click
    );
  }

  return (
    <>
      <select value={category} onChange={(e) => update({ category: e.target.value, page: "1" })}>
        <option value="all">All</option>
        <option value="books">Books</option>
      </select>
      <Results category={category} page={page} />
    </>
  );
}
```

**Bad Example** — the same state duplicated into `useState`, so it drifts from the URL

```tsx
function ProductList() {
  // URL says ?category=books but this defaults to "all" on every mount:
  // sharing/refreshing the page silently loses the filter, and the back
  // button can't undo a filter change because history never recorded it.
  const [category, setCategory] = useState("all");
  const [page, setPage] = useState(1);
  return <Results category={category} page={page} />;
}
```

**Good Example** — streamed loader data unwrapped with React 19 `use()`

```tsx
import { redirect, useLoaderData } from "react-router";
import { Suspense, use } from "react";

// Await only the critical data (the guard); return the slow query as a bare
// promise so React Router streams it instead of blocking the whole navigation.
export async function loader() {
  const user = await getUser();
  if (!user) throw redirect("/login");
  return { user, activity: fetchActivity(user.id) }; // activity is a Promise, not awaited
}

export default function Dashboard() {
  const { user, activity } = useLoaderData<typeof loader>();
  return (
    <>
      <h1>Welcome, {user.name}</h1>
      <Suspense fallback={<ActivitySkeleton />}>
        <Activity promise={activity} />
      </Suspense>
    </>
  );
}

function Activity({ promise }: { promise: Promise<Item[]> }) {
  const items = use(promise); // React 19: suspends until the streamed promise resolves
  return <ul>{items.map((i) => <li key={i.id}>{i.label}</li>)}</ul>;
}
```

## Common Mistakes

- Using `<a href>` for internal links, forcing full reloads and losing app state.
- Guarding routes only in the component, leaking protected UI and code before redirect.
- Fetching in nested components, creating request waterfalls the route loader avoids.
- Storing filter/pagination in component state, so URLs are not shareable and refresh resets them.
- Shipping one giant bundle because routes are statically imported, not lazy-loaded.
- Not managing focus/scroll on navigation, breaking accessibility and back-button behavior.
- Duplicating URL state into `useState`, letting the two drift out of sync.

## Production Tips

- Add a scroll-restoration component and move focus to the main heading on navigation.
  React Router ships `<ScrollRestoration />`; pair it with a focus reset so keyboard and
  screen-reader users are not stranded at the old scroll position after a client navigation:

  ```tsx
  import { Outlet, ScrollRestoration, useLocation, useNavigation } from "react-router";
  import { useEffect, useRef } from "react";

  function RootLayout() {
    const { pathname } = useLocation();
    const navigation = useNavigation();
    const mainRef = useRef<HTMLElement>(null);

    // Move focus to the main region on every path change (skip the initial mount).
    const first = useRef(true);
    useEffect(() => {
      if (first.current) { first.current = false; return; }
      mainRef.current?.focus();
    }, [pathname]);

    return (
      <>
        <Nav />
        {/* aria-busy tells assistive tech a navigation is in flight */}
        <main id="main" ref={mainRef} tabIndex={-1} aria-busy={navigation.state === "loading"}>
          <Outlet />
        </main>
        <ScrollRestoration />
      </>
    );
  }
  ```

- Prefetch the likely next route on link hover/focus to hide latency without bloating the
  bundle. In framework mode this is one prop — `<Link to="/reports" prefetch="intent">` loads
  the route's module and loader data on hover/focus, with no manual `import()` juggling.
- In SSR/framework setups, keep secrets and auth checks in loaders/server code — never gate
  solely in client components that ship to the browser.

## AI Review Checklist

- Are internal links `<Link>`/`<NavLink>`, not `<a href>`?
- Is route data loaded in a loader at the boundary rather than via in-component waterfalls?
- Are protected routes guarded before the component renders (loader/server), not only client-side?
- Is filter/sort/pagination state kept in search params?
- Are route components lazy-loaded to split the bundle?
- Is focus and scroll handled on navigation, and does each route have an error fallback?

## Related

- `knowledge/react/16-data-fetching.md`
- `knowledge/react/19-error-handling.md`
- `knowledge/react/18-state-management.md`
- `knowledge/react/12-performance.md`
- `knowledge/react/28-production.md`
