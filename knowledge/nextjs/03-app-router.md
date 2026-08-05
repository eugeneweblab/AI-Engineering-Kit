---
id: nextjs/03-app-router
topic: nextjs
slug: app-router
title: "Next.js App Router"
type: doc
order: 3
status: ready
tags: [nextjs, app-router, NextResponse, ProductsPage, getUser, NextRequest, error.tsx, page.tsx]
related: [nextjs/06-server-components, nextjs/09-data-fetching, nextjs/10-caching, nextjs/12-api-routes, nextjs/18-metadata, nextjs/04-routing, nextjs/05-layouts, nextjs/08-rendering-strategies]
when_to_use: "Read before structuring routes and directories with the Next.js App Router."
---
# Next.js App Router

## Purpose

This document defines the engineering standards for building applications using the Next.js App Router.

The objective is to create predictable, scalable, and maintainable routing structures that leverage the App Router architecture introduced in Next.js 13+.

Routes should reflect the application's domain rather than its implementation details.

---

## Core Principle

The file system defines the routing structure.

Every route should have a single, well-defined responsibility.

---

## App Directory

All application routes should reside inside the `app/` directory.

Example:

```
app/

    layout.tsx

    page.tsx

    loading.tsx

    error.tsx

    not-found.tsx

    dashboard/

        page.tsx

    settings/

        page.tsx
```

The directory structure should mirror the URL hierarchy.

---

## Route Segments

Each folder inside `app/` represents a route segment.

Example:

```
app/

    products/

        page.tsx
```

Produces:

```
/products
```

Nested folders create nested routes.

```
app/

    products/

        [id]/

            page.tsx
```

Produces:

```
/products/123
```

---

## Pages

Every publicly accessible route must define a `page.tsx`.

Responsibilities:

- compose the page;
- fetch data;
- generate metadata;
- coordinate features.

Pages are Server Components by default. They may be `async`, so data is fetched
directly in the component body — no `getServerSideProps`/`getStaticProps`.

```tsx
// app/products/page.tsx
export default async function ProductsPage() {
  // In Next 15 fetch is UNCACHED by default. Opt in to caching explicitly.
  const res = await fetch("https://api.example.com/products", {
    next: { revalidate: 60 }, // ISR: re-fetch at most once per 60s
  });

  if (!res.ok) throw new Error("Failed to load products");

  const products: Product[] = await res.json();

  return (
    <ul>
      {products.map((p) => (
        <li key={p.id}>{p.name}</li>
      ))}
    </ul>
  );
}
```

In Next 15+, `params` and `searchParams` passed to a page are **Promises** and
must be awaited.

```tsx
// app/products/page.tsx
type PageProps = {
  searchParams: Promise<{ sort?: string }>;
};

export default async function ProductsPage({ searchParams }: PageProps) {
  const { sort } = await searchParams;
  // ...
}
```

Avoid placing large amounts of business logic directly inside pages.

---

## Layouts

Layouts provide shared UI between routes.

Typical responsibilities:

- navigation;
- sidebar;
- header;
- footer;
- providers.

Layouts persist between navigation and should avoid route-specific logic.

A layout receives its nested route tree as `children`:

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <section>
      <Sidebar />
      <main>{children}</main>
    </section>
  );
}
```

The root layout (`app/layout.tsx`) is required and must render the `<html>` and
`<body>` tags — this is the one place they belong.

```tsx
// app/layout.tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

---

## Nested Layouts

Use nested layouts when sections of the application require different structures.

Example:

```
app/

    layout.tsx

    dashboard/

        layout.tsx

        page.tsx

        analytics/

            page.tsx
```

Shared UI should live at the highest practical layout level.

---

## Route Groups

Use route groups to organize code without affecting URLs.

Example:

```
app/

    (marketing)/

    (dashboard)/
```

Route groups improve organization while preserving clean URLs.

---

## Dynamic Routes

Use dynamic segments for resource identifiers.

Example:

```
app/

    users/

        [id]/

            page.tsx
```

Avoid encoding business logic into route names.

In Next.js 15+, `params` is a **Promise**. Await it before reading the segment.

Good — `params` awaited:

```tsx
// app/users/[id]/page.tsx
export default async function UserPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const user = await getUser(id);
  return <h1>{user.name}</h1>;
}
```

Bad — treats `params` as a plain object (compiles, then `id` is `undefined`):

```tsx
// app/users/[id]/page.tsx
export default async function UserPage({
  params,
}: {
  params: { id: string }; // wrong: params is a Promise in Next 15+
}) {
  const user = await getUser(params.id); // params.id is undefined at runtime
  return <h1>{user.name}</h1>;
}
```

To pre-render dynamic pages at build time, export `generateStaticParams`.

```tsx
// app/users/[id]/page.tsx
export async function generateStaticParams() {
  const users = await getAllUsers();
  return users.map((u) => ({ id: u.id })); // string values, keyed by segment
}
```

---

## Catch-All Routes

Use catch-all segments only when necessary.

Examples:

```
[...slug]

[[...slug]]
```

Prefer explicit routing whenever possible.

---

## Parallel Routes

Use parallel routes for independent UI regions.

Examples:

- dashboards;
- side panels;
- modal content.

Do not introduce parallel routes without a clear architectural benefit.

---

## Intercepting Routes

Intercepting routes should be used sparingly.

Typical use cases:

- modal navigation;
- image previews;
- contextual overlays.

Avoid replacing normal navigation patterns unnecessarily.

---

## Special Files

The App Router recognizes special files.

Common examples:

```
page.tsx

layout.tsx

loading.tsx

error.tsx

not-found.tsx

template.tsx

default.tsx

route.ts
```

Each file has a dedicated responsibility.

---

## Route Handlers

Use `route.ts` for HTTP endpoints.

Examples:

- webhooks;
- REST endpoints;
- internal APIs.

Export one async function per HTTP method. Handlers take the Web `Request`
(`NextRequest`) and return a Web `Response` (`NextResponse`).

```ts
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> }, // Promise in Next 15+
) {
  const { id } = await params;
  const user = await getUser(id);

  if (!user) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  return NextResponse.json(user);
}

export async function DELETE(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  await deleteUser(id);
  return new NextResponse(null, { status: 204 });
}
```

A `page.tsx` and a `route.ts` cannot coexist in the same segment — a segment
serves either UI or a handler, not both.

Do not mix UI rendering with request handling.

---

## Metadata

Generate metadata at the route level.

Examples:

- title;
- description;
- Open Graph;
- Twitter cards;
- robots;
- canonical URLs.

For static values, export a `metadata` object from a `page.tsx` or `layout.tsx`:

```tsx
// app/about/page.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About",
  description: "Who we are.",
};
```

For values that depend on route params or fetched data, export an async
`generateMetadata` instead. Its `params` is a Promise, like the page's.

```tsx
// app/products/[id]/page.tsx
import type { Metadata } from "next";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const product = await getProduct(id);

  return {
    title: product.name,
    openGraph: { images: [product.imageUrl] },
  };
}
```

Metadata should remain close to the route it describes.

---

## Navigation

Prefer Next.js navigation primitives.

Examples:

- `<Link>`
- `redirect()`
- `notFound()`

Avoid manipulating browser history manually unless required.

---

## Error Isolation

Each major route should define appropriate error boundaries.

Typical files:

```
error.tsx

not-found.tsx
```

An `error.tsx` must be a Client Component — it wraps the segment in a React error
boundary and receives the error plus a `reset` function to retry rendering.

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
      <p>Something went wrong.</p>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}
```

`error.tsx` does not catch errors thrown in the same segment's `layout.tsx` —
those bubble to the parent segment's boundary. Use a `global-error.tsx` at the
app root to catch failures in the root layout.

Failures should remain isolated to the affected route.

---

## Loading States

Provide route-specific loading experiences.

A `loading.tsx` is shown as a Suspense fallback while the segment's async
Server Component streams in.

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return <p aria-busy="true">Loading dashboard…</p>;
}
```

Avoid blank screens during navigation.

---

## AI Execution Checklist

## Investigation

☐ Review route hierarchy.

☐ Identify shared layouts.

☐ Identify dynamic routes.

☐ Review loading and error states.

---

## Planning

☐ Keep routes REST-like.

☐ Minimize nesting.

☐ Share layouts appropriately.

☐ Organize using route groups.

---

## Verification

☐ Routes remain predictable.

☐ Layouts are reusable.

☐ Error boundaries implemented.

☐ Loading states provided.

☐ Metadata generated correctly.

☐ URLs remain clean.

---

## Examples

**Good Example** — the file system expresses the UI states

```text
app/
├── layout.tsx                 root shell: html, body, providers
├── products/
│   ├── layout.tsx             sidebar, preserved across product pages
│   ├── loading.tsx            streamed instantly while page.tsx awaits
│   ├── error.tsx              'use client' — catches render errors in this segment
│   ├── page.tsx               the listing
│   └── [id]/
│       ├── page.tsx           one product
│       └── not-found.tsx      shown when notFound() is called
└── (marketing)/               route group: shares a layout, adds nothing to the URL
    ├── layout.tsx
    └── about/page.tsx
```

```tsx
// app/products/[id]/page.tsx
import { notFound } from 'next/navigation';

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;                    // params is a Promise in Next.js 15+
  const product = await getProduct(id);

  if (!product) {
    notFound();                                   // renders the nearest not-found.tsx
  }

  return <ProductDetail product={product} />;
}
```

**Bad Example** — one route that reimplements the router

```tsx
// app/page.tsx — every screen behind a query string, so nothing is linkable,
// nothing is cacheable per route, and the layout cannot differ per section.
'use client';

export default function Page() {
  const params = useSearchParams();
  const view = params.get('view');

  if (view === 'products') return <ProductList />;
  if (view === 'product') return <ProductDetail id={params.get('id')!} />;
  if (view === 'about') return <About />;
  return <Home />;
}
```

There is no `loading.tsx` to stream, no `error.tsx` boundary, no per-segment metadata, and
every navigation re-renders the whole tree on the client.

---

## Common Mistakes

Avoid:

Placing business logic inside layouts.

Creating deeply nested routes.

Duplicating layouts.

Using route groups unnecessarily.

Overusing catch-all routes.

Mixing API endpoints with UI.

Ignoring loading and error files.

---

## Completion Criteria

App Router implementation is complete when:

- routes reflect the application structure;
- layouts are shared appropriately;
- pages remain focused;
- metadata is implemented;
- loading and error handling are present;
- routing remains scalable and maintainable.

---

## Summary

The App Router provides a powerful file-based routing system that encourages server-first architecture, nested layouts, and predictable application structure.

By organizing routes around business domains and leveraging the built-in routing primitives, Next.js applications become easier to scale, easier to maintain, and more resilient as they evolve.

## Related

- `knowledge/nextjs/06-server-components.md`
- `knowledge/nextjs/09-data-fetching.md`
- `knowledge/nextjs/10-caching.md`
- `knowledge/nextjs/12-api-routes.md`
- `knowledge/nextjs/18-metadata.md`
- `knowledge/nextjs/04-routing.md`
- `knowledge/nextjs/05-layouts.md`
- `knowledge/nextjs/08-rendering-strategies.md`
