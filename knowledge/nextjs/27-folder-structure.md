---
id: nextjs/27-folder-structure
topic: nextjs
slug: folder-structure
title: "Next.js Folder Structure"
type: doc
order: 27
status: ready
tags: [nextjs, folder-structure]
related: [nextjs/02-project-structure, nextjs/03-app-router, nextjs/04-routing, nextjs/05-layouts, nextjs/06-server-components]
when_to_use: "Read before creating routes, special files, or route groups inside the app/ directory."
---
# Next.js Folder Structure

## Purpose

This document defines the file and folder conventions *inside* the `app/` directory — the
special files (`page.tsx`, `layout.tsx`, `route.ts`, …), folder-based routing, route groups,
private folders, and dynamic segments. It is the routing-layer counterpart to
[project structure](02-project-structure.md), which covers the repository as a whole.

## Why It Matters

In the App Router, folder and file *names are the API*: a folder becomes a URL segment,
`page.tsx` makes a segment routable, `layout.tsx` wraps its subtree, and `(group)` or `_folder`
change behavior invisibly. An agent that misnames a file produces a route that 404s, a layout
that re-renders when it should not, or a component accidentally exposed as a public URL.
Getting the conventions exactly right is the difference between working routing and silent
breakage.

## Core Principles

- **Folders define routes; files define behavior.** A folder is a URL segment. It becomes
  navigable only when it contains a `page.tsx` (a `route.ts` makes it an API endpoint instead).
- **Special file names are reserved and load-bearing.** `page`, `layout`, `template`, `loading`,
  `error`, `not-found`, `route`, `default` each have defined semantics — use them for exactly
  that purpose and nothing else.
- **Layouts persist; pages do not.** A `layout.tsx` wraps its segment and children and does *not*
  re-render on navigation between its children — never put per-request auth or data that must
  refresh in a layout (see [authorization](15-authorization.md)).
- **Colocation is safe.** Any non-special file in a route folder (`components/`, `utils.ts`) is
  *not* routable — only `page`/`route` create URLs — so colocate freely without exposing files.

## Best Practices

- Use **route groups** `(name)` to organize routes and share a layout without adding a URL
  segment — e.g. `(marketing)/` and `(app)/` split concerns while keeping clean URLs.
- Use **private folders** `_name` for colocated non-route code you want unmistakably excluded
  from routing (the leading underscore opts the whole folder out).
- Use **dynamic segments** `[id]`, catch-all `[...slug]`, and optional catch-all `[[...slug]]`
  deliberately; validate their values as untrusted input in the page/handler.
- Add `loading.tsx` to stream a Suspense fallback and `error.tsx` (a client component) to catch
  render errors per segment, keeping failures local instead of blanking the whole app.
- Keep one `page.tsx` per routable segment; put shared UI in `layout.tsx`, and reset state
  across navigation with `template.tsx` only when you specifically need remount behavior.

## Examples

**Good Example** — route groups, colocation, special files

```text
app/
  layout.tsx                 # root layout: <html lang>, global providers
  (marketing)/               # route group — no URL segment
    layout.tsx               # marketing-only chrome
    page.tsx                 # "/"
  (app)/
    layout.tsx               # app shell (persists across child navigation)
    dashboard/
      page.tsx               # "/dashboard"
      loading.tsx            # streamed fallback for this segment
      error.tsx              # "use client" — catches errors here only
      _components/Chart.tsx  # private folder: colocated, never routable
  blog/
    [slug]/
      page.tsx               # "/blog/:slug" — validate slug as untrusted input
  api/
    invoices/route.ts        # "/api/invoices" — endpoint, not a page
```

**Bad Example** — misused names and misplaced logic

```text
app/
  dashboard/
    index.tsx                # WRONG: App Router uses page.tsx, not index.tsx → 404
    Chart.tsx                # accidentally reachable-looking; use _components/ to be explicit
    layout.tsx               # contains the auth check ↓
```

```tsx
// app/dashboard/layout.tsx — layout does not re-render on client navigation,
// so this auth gate is skipped when moving between dashboard pages. Enforce in the DAL instead.
export default async function Layout({ children }) {
  if (!(await getUser())) redirect('/login'); // false sense of protection
  return <>{children}</>;
}
```

## Common Mistakes

- Using `index.tsx` (Pages Router habit) instead of `page.tsx`; the segment is not routable.
- Putting per-request auth or must-refresh data in `layout.tsx`, which persists across navigation.
- Forgetting `error.tsx` must be a client component (`"use client"`), so it silently fails to catch.
- Confusing route groups `(x)` (no URL segment) with real folders `x` (adds a segment).
- Treating colocated helper files as private without `_` — they are harmless but read ambiguously.
- Not validating dynamic segment values (`[id]`, `[...slug]`) as untrusted user input.

## AI Review Checklist

- Is each routable segment defined by `page.tsx` (or `route.ts` for APIs), not `index.tsx`?
- Are route groups `(name)` and private folders `_name` used for organization vs. real segments?
- Is auth / per-request data enforced in the DAL, not in a persistent `layout.tsx`?
- Does each risky segment have `loading.tsx` and a client `error.tsx` boundary?
- Are dynamic segment values validated before use?

## Related

- `knowledge/nextjs/02-project-structure.md`
- `knowledge/nextjs/03-app-router.md`
- `knowledge/nextjs/04-routing.md`
- `knowledge/nextjs/05-layouts.md`
- `knowledge/nextjs/06-server-components.md`
