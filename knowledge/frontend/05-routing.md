---
id: frontend/05-routing
topic: frontend
slug: routing
title: "Routing"
type: doc
order: 5
status: ready
tags: [frontend, routing]
related: [frontend/04-state-management, frontend/01-frontend-architecture, frontend/21-code-splitting, frontend/13-error-handling]
when_to_use: "Read before adding routes, building nested layouts, guarding pages, or wiring URL state and code-splitting."
---
# Routing

## Purpose

This document defines how to map URLs to views: route structure, nested layouts,
navigation guards, loading and error boundaries, and treating the URL as a first-
class piece of state. It lets an agent add a route that is shareable, splittable,
and correct on direct load and back/forward navigation.

The URL is the app's public API to the user. It should fully describe *what the user
is looking at*, so that a reload or a shared link reconstructs the same screen.

## Why It Matters

Routing bugs are the ones that break trust: a deep link that 404s, a filter that
resets on reload, a protected page that flashes its content before redirecting, a
back button that does the wrong thing. These come from treating the URL as an
afterthought rather than as state.

Routing is also the natural boundary for code-splitting and for loading and error
UI. Get the route structure right and performance and resilience follow; get it
wrong and every page pays.

## Core Principles

- **The URL is state.** Anything that determines the current view — the page, the
  selected id, filters, tab, pagination — belongs in the URL, not in memory. See
  [state management](04-state-management.md).
- **Every route must survive a direct load.** A user can arrive at any URL cold;
  the route must fetch what it needs and render, not assume prior navigation.
- **Guard on the server, reflect on the client.** Client route guards improve UX
  but are not security; the server must still authorize every request.
- **Routes are code-split boundaries.** Lazy-load route components so users download
  only the page they visit. See [code splitting](21-code-splitting.md).
- **Handle the unhappy paths in the router.** Loading, empty, error, and not-found
  states are route concerns, not per-component afterthoughts.

## Best Practices

- Define routes declaratively and colocate each route's data loading, layout, and
  error boundary so the whole page is described in one place.
- Use nested/layout routes for shared shells (nav, sidebar) instead of repeating
  layout in every page component.
- Store filters, search, sort, and pagination in query params via the router's
  API, so they are shareable and survive reload and back/forward.
- Lazy-load route modules and show a route-level loading state; pair with an error
  boundary so a failed chunk or loader does not blank the app. See
  [error handling](13-error-handling.md).
- Redirect with replace semantics for guards so the guarded URL does not pollute
  history and the back button behaves.
- Never render protected content before the auth check resolves; gate it, don't flash it.

## Examples

**Good Example** — lazy route, URL-driven state, guard that redirects cleanly

```tsx
const Orders = lazy(() => import("./features/orders")); // split: page loads on demand

const routes = [
  {
    path: "/orders",
    element: (
      <RequireAuth>          {/* resolves auth BEFORE rendering children */}
        <Suspense fallback={<PageSpinner />}>
          <Orders />
        </Suspense>
      </RequireAuth>
    ),
    errorElement: <RouteError />, // failed loader or chunk shows a real error, not blank
  },
];

function OrdersList() {
  // Filter lives in the URL: reload-safe, shareable, back/forward works for free.
  const [params, setParams] = useSearchParams();
  const status = params.get("status") ?? "open";
  const { data } = useOrders(status);
  return <Table rows={data} onFilter={(s) => setParams({ status: s })} />;
}
```

**Bad Example** — filter in memory, guard flashes content, no split or error UI

```tsx
function OrdersList() {
  const [status, setStatus] = useState("open"); // lost on reload, not shareable
  const { user } = useAuth();
  // Content renders first, THEN redirects — protected data flashes on screen.
  if (!user) navigate("/login"); // also pushes /orders onto history: back button loops
  const { data } = useOrders(status);
  return <Table rows={data} onFilter={setStatus} />;
  // Eagerly imported: every user downloads this page whether they visit it or not.
}
```

## Common Mistakes

- Keeping view-determining state (filters, selected id, tab) in component state, so
  reload and shared links lose it.
- Guarding routes by rendering then redirecting, flashing protected content.
- Treating client-side guards as security instead of enforcing on the server.
- No route-level error boundary, so a failed loader or lazy chunk blanks the app.
- Eagerly importing every page, shipping the whole app in the first bundle.
- Redirects that push instead of replace, breaking the back button.
- Not handling not-found (`*`) routes, so bad URLs render nothing.

## Production Tips

- Prefetch the likely-next route on link hover/focus to hide navigation latency.
- Preserve and restore scroll position on navigation where it matters (lists → detail → back).
- Test direct loads and back/forward in CI, not just in-app navigation — cold entry
  is where routing bugs hide.

## AI Review Checklist

- Does every route render correctly on a direct, cold load?
- Is view-determining state (filters, id, tab, pagination) stored in the URL?
- Are guards resolving auth before rendering, and redirecting with replace semantics?
- Is protected content also authorized on the server, not just guarded client-side?
- Are route components lazy-loaded with loading and error boundaries?
- Is there a not-found route for unmatched URLs?

## Related

- `knowledge/frontend/04-state-management.md`
- `knowledge/frontend/01-frontend-architecture.md`
- `knowledge/frontend/21-code-splitting.md`
- `knowledge/frontend/13-error-handling.md`
- `knowledge/frontend/06-data-fetching.md`
