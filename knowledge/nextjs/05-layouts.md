---
id: nextjs/05-layouts
topic: nextjs
slug: layouts
title: "Next.js Layouts"
type: doc
order: 5
status: ready
tags: [nextjs, layouts]
related: [nextjs/06-server-components, nextjs/07-client-components, nextjs/09-data-fetching, nextjs/10-caching, nextjs/18-metadata, nextjs/17-fonts]
when_to_use: "Read before building shared layouts or persistent UI across Next.js routes."
---
# Next.js Layouts

## Purpose

This document defines the engineering standards for using layouts in Next.js applications.

The objective is to build applications with consistent page structure, shared UI, predictable navigation, and efficient rendering while maximizing the benefits of the App Router.

Layouts should eliminate duplication and provide persistent user interface elements across related routes.

---

## Core Principle

Layouts define structure.

Pages define content.

Features define business functionality.

Each layer should have a single responsibility.

---

## What is a Layout

A Layout is a React Server Component that wraps one or more routes.

Layouts are designed to:

- provide shared page structure;
- persist UI between navigations;
- reduce duplicated code;
- improve navigation performance.

Unlike pages, layouts are preserved during navigation whenever possible.

---

## Layout Hierarchy

Layouts follow the route hierarchy.

Example:

```
app/

    layout.tsx

        dashboard/

            layout.tsx

                analytics/

                    page.tsx
```

Rendering hierarchy:

```
Root Layout

↓

Dashboard Layout

↓

Analytics Page
```

Each layout adds only the structure required for its route segment.

---

## Root Layout

Every application must define a single Root Layout.

Typical responsibilities include:

- `<html>`;
- `<body>`;
- global styles;
- fonts;
- global providers;
- application shell.

The Root Layout is required, must render `<html>` and `<body>`, and receives a
`children` prop. It is a Server Component by default — do not add `"use client"`.

```tsx
// app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

// next/font self-hosts the font at build time — no external request,
// no layout shift. Call the loader at module scope, never inside a component.
const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: {
    default: "Acme",
    template: "%s | Acme", // pages set `title` and it slots into `%s`
  },
  description: "Acme dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

The Root Layout should remain lightweight. Note that `layout` files cannot read
`searchParams` — only `params`. If a segment's UI depends on query strings, read
them in the `page`, not the layout.

---

## Nested Layouts

Use nested layouts to share UI within a specific application section.

Examples:

- dashboard;
- administration;
- customer portal;
- documentation.

A nested layout wraps every route in its segment and below. It renders its own
UI plus `children`, but never `<html>` or `<body>` (those belong only to the
Root Layout).

```tsx
// app/dashboard/layout.tsx
import { Sidebar } from "@/components/sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="dashboard-grid">
      <Sidebar />
      <main>{children}</main>
    </div>
  );
}
```

Avoid creating nested layouts for individual pages.

---

## Shared UI

Layouts are the correct location for persistent UI.

Examples:

- navigation;
- sidebar;
- footer;
- breadcrumbs;
- application header;
- global notifications.

Avoid duplicating these elements across multiple pages.

---

## Persistent State

Layouts preserve their rendered output between navigations.

Examples:

- expanded sidebar;
- navigation scroll position;
- active navigation state.

Take advantage of persistence to improve user experience.

---

## Data Fetching

Layouts may fetch server-side data.

Good examples:

- authenticated user;
- organization information;
- navigation menu;
- feature flags;
- localization.

A layout is an `async` Server Component, so it can `await` data directly. In
Next 15+ `fetch` is **uncached by default** — each request hits the origin
unless you explicitly opt in. Cache slow, stable data (navigation, feature
flags) with `next: { revalidate }` or `cache: "force-cache"`; leave
per-request data (the current user) uncached.

```tsx
// app/dashboard/layout.tsx
async function getNavigation() {
  // Stable data: revalidate at most once a minute across all requests.
  const res = await fetch("https://cms.example.com/nav", {
    next: { revalidate: 60 },
  });
  if (!res.ok) throw new Error("Failed to load navigation");
  return res.json() as Promise<NavItem[]>;
}

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const nav = await getNavigation();
  return (
    <div className="dashboard-grid">
      <Sidebar items={nav} />
      <main>{children}</main>
    </div>
  );
}
```

Layouts and their child pages render in parallel, so data fetched in a layout
is **not** passed down as props to pages. When a layout and a page need the
same data, call the same cached function in both — React's `cache()` and
`fetch` deduplication collapse the duplicate calls into one within a request.

Avoid loading page-specific business data inside layouts.

---

## Authentication

Authentication should generally occur at the highest practical layout level.

Examples:

```
Root Layout

↓

Authenticated Layout

↓

Dashboard
```

Protected areas should not repeat authentication logic on every page.

A layout can gate a whole section by verifying the session and redirecting when
it is missing. `redirect()` from `next/navigation` throws, so code after it
never runs.

```tsx
// app/(app)/layout.tsx
import { redirect } from "next/navigation";
import { getSession } from "@/lib/auth";

export default async function AuthedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession(); // reads the session cookie server-side
  if (!session) redirect("/login");

  return <AppShell user={session.user}>{children}</AppShell>;
}
```

A layout is a defense-in-depth boundary, not the only one. Because layouts and
pages render in parallel and a layout does not re-run on every client-side
navigation between its child routes, still enforce authorization in the data
layer (Server Actions, Route Handlers, DB queries) — never rely on the layout
alone. See `13-middleware.md` for edge-level gating and `15-authorization.md`.

---

## Providers

Global providers belong as high as possible.

Examples:

- Theme Provider;
- Authentication Provider;
- Query Client;
- Internationalization;
- Analytics.

Feature-specific providers should remain inside their respective layouts or features.

Most providers rely on React Context, which requires a Client Component. Isolate
them in a dedicated `"use client"` file and render it from the Server Component
Root Layout. This keeps the layout itself on the server while still wrapping the
tree in client context.

```tsx
// app/providers.tsx
"use client";

import { ThemeProvider } from "next-themes";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  // useState ensures one QueryClient per client session, not one per render.
  const [queryClient] = useState(() => new QueryClient());
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class">{children}</ThemeProvider>
    </QueryClientProvider>
  );
}
```

**Good Example** — a small `"use client"` provider island; the layout stays a Server
Component and `children` (Server Components) still stream through untouched.

```tsx
// app/layout.tsx  — Server Component
import { Providers } from "./providers";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

**Bad Example** — marking the entire Root Layout as a client boundary. Every descendant
is now forced onto the client, disabling Server Components below it and
inflating the bundle.

```tsx
// app/layout.tsx  — DON'T
"use client";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{/* everything below is now client-only */}{children}</body>
    </html>
  );
}
```

Passing Server Components as `children` into a Client Component provider is the
key trick: the boundary applies to the provider, not to what it wraps.

---

## Metadata

Layouts may define shared metadata.

Examples:

- default title;
- Open Graph defaults;
- robots;
- viewport;
- icons.

Export a static `metadata` object for constant values, or an async
`generateMetadata` when the values depend on `params` or fetched data. Metadata
merges down the tree: a page's fields override the layout's, and the `title.template`
set in a parent wraps a child's `title` string.

```tsx
// app/blog/[slug]/page.tsx
import type { Metadata } from "next";

// In Next 15+, params is a Promise and must be awaited.
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPost(slug); // deduped with the page body's own call
  return {
    title: post.title, // becomes "Post Title | Acme" via the root template
    openGraph: { title: post.title, images: [post.coverImage] },
  };
}
```

Note: `viewport` and `themeColor` are configured via a separate `viewport`
export (`export const viewport: Viewport = { ... }`), not inside `metadata`.

Pages should override metadata only when necessary.

---

## Error Boundaries

Use route-level error boundaries together with layouts.

Typical structure:

```
layout.tsx

error.tsx

loading.tsx

page.tsx
```

An `error.tsx` file wraps its sibling `page` (and nested segments) in a React
error boundary. It **must** be a Client Component and receives `error` plus a
`reset` function to retry rendering the segment. A sibling `error.tsx` does not
catch errors thrown by its own `layout.tsx` — put an `error.tsx` in the parent
segment to cover a layout's failures.

```tsx
// app/dashboard/error.tsx
"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div role="alert">
      <h2>Something went wrong in the dashboard.</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

Each layout should isolate failures within its own section of the application.

---

## Loading States

Loading UI should correspond to the layout hierarchy.

Examples:

- dashboard shell;
- sidebar skeleton;
- page placeholder.

A `loading.tsx` file automatically wraps its sibling `page` in a `<Suspense>`
boundary, so the layout and its shell render immediately while the page streams
in. Place `loading.tsx` at the segment whose content is slow, not at the root,
so only that section shows a skeleton.

```tsx
// app/dashboard/loading.tsx  — Server Component, no "use client" needed
export default function Loading() {
  return <SidebarSkeleton />; // shown while dashboard pages fetch
}
```

For finer control, wrap an individual slow component in `<Suspense>` inside the
page itself rather than blocking the whole segment.

Avoid replacing the entire application with a loading screen when only one section is loading.

---

## Performance

Layouts improve performance by:

- avoiding unnecessary rerenders;
- preserving shared UI;
- reducing repeated rendering work;
- minimizing layout shifts.

Do not introduce expensive computations into layouts.

---

## Client Components

Keep layouts as Server Components whenever possible.

Only introduce `"use client"` when required.

Examples:

- browser-only providers;
- interactive navigation;
- client-side theme switching.

Avoid making the Root Layout a Client Component unless absolutely necessary.

---

## Accessibility

Layouts should provide:

- semantic landmarks;
- logical heading structure;
- skip navigation links;
- keyboard-accessible navigation;
- predictable focus management.

Because a layout owns the page shell, it is the right place to add landmark
elements and a skip link so keyboard and screen-reader users can bypass
persistent navigation on every route.

```tsx
// app/(app)/layout.tsx
export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <header>
        <nav aria-label="Primary">{/* ... */}</nav>
      </header>
      <main id="main">{children}</main>
    </>
  );
}
```

Persistent UI should remain fully accessible.

---

## AI Execution Checklist

## Investigation

☐ Review application hierarchy.

☐ Identify shared UI.

☐ Identify global providers.

☐ Review authentication flow.

---

## Planning

☐ Keep layouts reusable.

☐ Minimize nesting.

☐ Keep layouts server-side.

☐ Separate page-specific logic.

---

## Verification

☐ Shared UI centralized.

☐ Providers correctly placed.

☐ Layouts remain lightweight.

☐ Authentication handled consistently.

☐ Accessibility preserved.

☐ Performance optimized.

---

## Common Mistakes

Avoid:

Making every layout a Client Component.

Fetching page-specific data inside layouts.

Duplicating navigation across pages.

Creating deeply nested layouts.

Placing business logic inside layouts.

Adding unnecessary providers to the Root Layout.

Ignoring accessibility of persistent navigation.

---

## Completion Criteria

A layout implementation is complete when:

- shared UI is centralized;
- page-specific logic remains inside pages or features;
- layouts remain Server Components whenever possible;
- providers are placed at the appropriate level;
- navigation is accessible;
- the layout hierarchy supports future scalability.

---

## Summary

Layouts are the structural foundation of a Next.js application.

By centralizing shared UI, preserving state across navigations, and maintaining a server-first architecture, layouts improve performance, reduce duplication, and provide a consistent user experience throughout the application.

## Related

- `knowledge/nextjs/03-app-router.md`
- `knowledge/nextjs/04-routing.md`
- `knowledge/nextjs/06-server-components.md`
- `knowledge/nextjs/18-metadata.md`
