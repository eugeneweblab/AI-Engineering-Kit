---
id: nextjs/08-rendering-strategies
topic: nextjs
slug: rendering-strategies
title: "Next.js Rendering Strategies"
type: doc
order: 8
status: ready
tags: [nextjs, rendering-strategies]
related: [nextjs/06-server-components, nextjs/10-caching, nextjs/09-data-fetching, nextjs/20-performance]
when_to_use: "Read before choosing a rendering strategy for a Next.js route."
---
# Next.js Rendering Strategies

## Purpose

This document defines the engineering standards for selecting and implementing rendering strategies in Next.js applications.

The objective is to deliver the best balance between performance, scalability, freshness of data, SEO, and infrastructure cost.

Rendering strategy is an architectural decision and should be selected intentionally for every route.

---

## Core Principle

Render as early as possible.

Render as late as necessary.

Choose the least dynamic solution that satisfies the business requirements.

---

## Rendering Decision Flow

Every route should follow this decision process.

```
Can the page be static?

        │

       Yes
        │
        ▼

Static Rendering

        │

        No
        │
        ▼

Can stale data be accepted?

        │

       Yes
        │
        ▼

Incremental Static Regeneration

        │

        No
        │
        ▼

Dynamic Rendering

        │

Need faster perceived loading?

        │

       Yes
        │
        ▼

Streaming
```

---

## Static Rendering

Static Rendering generates HTML during build time.

Best suited for:

- marketing pages;
- documentation;
- blog posts;
- pricing pages;
- legal pages;
- landing pages.

Benefits:

- fastest response time;
- excellent SEO;
- minimal server load;
- CDN friendly.

A route in the App Router is static by default as long as it uses no dynamic
APIs (`cookies()`, `headers()`, `draftMode()`, `searchParams`) and no uncached
data requests. Data read at build time makes the route eligible for static
rendering.

```tsx
// app/pricing/page.tsx
// Static: no dynamic APIs, and the fetch opts into the Data Cache.
export default async function PricingPage() {
  const res = await fetch("https://cms.example.com/pricing", {
    // Next.js 15: fetch is uncached by default. Opt in explicitly.
    cache: "force-cache",
  });
  const plans: Plan[] = await res.json();

  return <PricingTable plans={plans} />;
}
```

For dynamic segments, enumerate the pages to prerender at build time with
`generateStaticParams`.

```tsx
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await getAllPostSlugs(); // reads from the CMS/DB at build
  return posts.map((slug) => ({ slug }));
}

// In Next.js 15, params is a Promise and must be awaited.
export default async function PostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = await getPost(slug);

  return <Article post={post} />;
}
```

To force a route to remain static and fail the build if it accidentally opts
into dynamic behavior, set the route segment config:

```tsx
// app/docs/[slug]/page.tsx
export const dynamic = "force-static";
```

---

## Dynamic Rendering

Dynamic Rendering generates HTML for every request.

Use when content depends on:

- authentication;
- cookies;
- request headers;
- user permissions;
- highly dynamic data.

Examples:

- dashboards;
- account pages;
- admin panels;
- personalized content.

A route becomes dynamic the moment it reads a dynamic API. In Next.js 15 these
APIs are asynchronous and must be awaited.

```tsx
// app/dashboard/page.tsx
import { cookies, headers } from "next/headers";

export default async function DashboardPage() {
  const cookieStore = await cookies(); // async in Next.js 15
  const session = cookieStore.get("session")?.value;

  const requestHeaders = await headers();
  const locale = requestHeaders.get("accept-language") ?? "en";

  const user = await getUserFromSession(session);
  return <Dashboard user={user} locale={locale} />;
}
```

To opt an entire route out of static rendering explicitly, use the segment
config. Prefer letting the dynamic APIs signal intent; reach for
`force-dynamic` only when there is a concrete reason.

```tsx
// app/admin/page.tsx
export const dynamic = "force-dynamic";
```

Avoid Dynamic Rendering when static rendering is sufficient.

**Bad — forcing a route dynamic to avoid thinking about caching:**

```tsx
// app/blog/page.tsx
export const dynamic = "force-dynamic"; // every request re-renders on the server
// The blog changes a few times a day; this discards CDN and Data Cache benefits.
```

**Good — static shell with time-based revalidation (ISR):**

```tsx
// app/blog/page.tsx
export const revalidate = 300; // regenerate at most every 5 minutes
```

---

## Incremental Static Regeneration (ISR)

ISR combines static generation with periodic updates.

Suitable for:

- product catalogs;
- news sites;
- documentation;
- e-commerce;
- CMS-driven content.

Benefits:

- static performance;
- fresh content;
- reduced build times.

Define an appropriate revalidation interval. ISR can be expressed two ways.

Route-level revalidation regenerates the whole page on a schedule:

```tsx
// app/products/[id]/page.tsx
export const revalidate = 3600; // seconds — regenerate at most hourly

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const product = await getProduct(id);
  return <ProductDetail product={product} />;
}
```

Per-request revalidation scopes freshness to individual `fetch()` calls:

```tsx
const res = await fetch(`https://api.example.com/products/${id}`, {
  next: { revalidate: 3600, tags: [`product:${id}`] },
});
```

Tagged requests can be invalidated on demand from a Server Action or Route
Handler when the underlying data changes, instead of waiting for the interval:

```tsx
// app/actions.ts
"use server";
import { revalidateTag } from "next/cache";

export async function publishProduct(id: string) {
  await saveProduct(id);
  revalidateTag(`product:${id}`); // refresh only the affected cache entries
}
```

---

## Streaming

Streaming allows portions of a page to be delivered as they become available.

Recommended for:

- dashboards;
- analytics;
- search results;
- complex pages with multiple data sources.

Benefits:

- improved perceived performance;
- reduced waiting time;
- progressive rendering.

Stream slow sections by wrapping them in `<Suspense>`. The shell and fast
content render immediately; each boundary fills in as its data resolves.

```tsx
// app/dashboard/page.tsx
import { Suspense } from "react";

export default function DashboardPage() {
  return (
    <section>
      <h1>Dashboard</h1>
      {/* Fast: renders in the initial response */}
      <QuickStats />

      {/* Slow: streams in without blocking the rest of the page */}
      <Suspense fallback={<AnalyticsSkeleton />}>
        <Analytics />
      </Suspense>

      <Suspense fallback={<FeedSkeleton />}>
        <ActivityFeed />
      </Suspense>
    </section>
  );
}

// Each streamed child is an async Server Component that fetches its own data.
async function Analytics() {
  const data = await getAnalytics(); // uncached by default in Next.js 15
  return <AnalyticsChart data={data} />;
}
```

A route-level `loading.tsx` file wraps the whole page in an implicit Suspense
boundary and streams a fallback while the page renders.

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return <DashboardSkeleton />;
}
```

**Bad — one slow request blocks the entire response:**

```tsx
export default async function Page() {
  const analytics = await getAnalytics(); // 2s: nothing renders until this resolves
  return <Dashboard analytics={analytics} />;
}
```

**Good — the shell renders instantly and the slow part streams in** (see the
`<Suspense>` example above).

---

## Partial Prerendering (PPR)

When available for the project, Partial Prerendering combines:

- static shell;
- dynamic islands.

Benefits:

- fast initial response;
- selective dynamic rendering;
- reduced server work.

Prefer PPR over making an entire page dynamic when only small sections require personalization.

PPR is still experimental. Enable it in the config, then opt in per segment.
The static shell is prerendered; anything inside a `<Suspense>` boundary that
reads a dynamic API becomes a streamed dynamic island.

```ts
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    ppr: "incremental", // opt in per-route rather than globally
  },
};

export default nextConfig;
```

```tsx
// app/product/[id]/page.tsx
import { Suspense } from "react";
import { cookies } from "next/headers";

export const experimental_ppr = true;

export default function ProductPage() {
  return (
    <main>
      {/* Prerendered static shell */}
      <ProductHeader />
      <ProductDescription />

      {/* Dynamic island: streamed per request */}
      <Suspense fallback={<CartButtonSkeleton />}>
        <CartButton />
      </Suspense>
    </main>
  );
}

async function CartButton() {
  const cookieStore = await cookies(); // dynamic API -> this island is dynamic
  const cartId = cookieStore.get("cart")?.value;
  const cart = await getCart(cartId);
  return <AddToCart count={cart.items.length} />;
}
```

---

## Client Rendering

Client-side rendering should be limited to interactive UI.

Examples:

- modals;
- dropdowns;
- editors;
- drag-and-drop interfaces.

A Client Component is marked with the `"use client"` directive at the top of
the file. It can use hooks, state, effects, and browser APIs. Keep these
components small and push them to the leaves of the tree.

```tsx
// app/components/theme-toggle.tsx
"use client";

import { useState } from "react";

export function ThemeToggle() {
  const [dark, setDark] = useState(false);
  return (
    <button onClick={() => setDark((v) => !v)}>
      {dark ? "Light" : "Dark"} mode
    </button>
  );
}
```

A Server Component can render a Client Component and pass server-fetched data
into it as props, keeping data access on the server while enabling
interactivity on the client.

```tsx
// app/products/page.tsx  (Server Component — no "use client")
import { ProductFilters } from "./product-filters"; // Client Component

export default async function ProductsPage() {
  const products = await getProducts(); // stays on the server
  return <ProductFilters initialProducts={products} />;
}
```

**Bad — marking a whole page a Client Component to add one interactive button:**

```tsx
"use client"; // now data fetching, secrets, and SEO content are all client-side
export default function Page() {
  /* entire page, including primary content, ships to the browser */
}
```

**Good — server page for content, a small Client Component for the interaction**
(see the `ThemeToggle` and `ProductsPage` examples above).

Avoid using client rendering for primary content when server rendering is possible.

---

## Route-Level Strategy

Each route should explicitly define its rendering strategy.

Examples:

```
/

→ Static

/blog

→ ISR

/dashboard

→ Dynamic

/settings

→ Dynamic

/docs

→ Static
```

Route segment config makes the strategy explicit and reviewable. Export these
constants from a `page.tsx` or `layout.tsx`:

```tsx
// Force one strategy for the whole segment.
export const dynamic = "auto"; // "auto" | "force-dynamic" | "error" | "force-static"

// Revalidation window in seconds (false = cache indefinitely; 0 = never cache).
export const revalidate = 3600;

// Behavior for dynamic params not returned by generateStaticParams.
export const dynamicParams = true; // false -> unknown params return 404
```

Prefer the default (`dynamic = "auto"`) and let data-access choices drive the
outcome; override only with a documented reason.

Avoid mixing unrelated rendering strategies within the same feature without justification.

---

## Data Freshness

Consider:

- update frequency;
- business requirements;
- user expectations;
- infrastructure cost.

Not all data requires real-time updates.

---

## Caching

Rendering strategy and caching should complement each other.

Review:

- browser cache;
- CDN cache;
- Next.js cache;
- data cache.

Do not disable caching without a measurable reason.

---

## SEO

Prefer server-rendered content for pages that should be indexed.

Examples:

- marketing pages;
- blog articles;
- product pages;
- documentation.

Avoid relying on client rendering for SEO-critical content.

---

## Performance

Evaluate:

- Time to First Byte (TTFB);
- Largest Contentful Paint (LCP);
- Interaction to Next Paint (INP);
- Cumulative Layout Shift (CLS).

Rendering decisions should improve user-perceived performance rather than only backend metrics.

---

## Security

Keep sensitive rendering logic on the server.

Never expose:

- secrets;
- private business rules;
- authorization decisions.

Rendering strategy must not compromise application security.

---

## Accessibility

Rendering strategy must not affect accessibility.

Verify:

- semantic HTML;
- keyboard navigation;
- loading announcements;
- focus management during streamed updates.

---

## AI Execution Checklist

## Investigation

☐ Determine how frequently the data changes.

☐ Determine SEO requirements.

☐ Determine personalization requirements.

☐ Review performance objectives.

---

## Planning

☐ Select the simplest rendering strategy.

☐ Minimize dynamic rendering.

☐ Enable caching where appropriate.

☐ Consider streaming for slow content.

---

## Verification

☐ Rendering strategy documented.

☐ SEO requirements satisfied.

☐ Performance objectives met.

☐ Caching configured appropriately.

☐ Accessibility preserved.

☐ Security maintained.

---

## Examples

**Good Example** — the strategy chosen per route, and stated in code

```tsx
// app/blog/[slug]/page.tsx — static, revalidated in the background.
export const revalidate = 3600;                    // ISR: rebuild at most hourly

export async function generateStaticParams() {
  return (await getAllPostSlugs()).map((slug) => ({ slug }));
}

export default async function PostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <Article post={await getPost(slug)} />;
}
```

```tsx
// app/account/page.tsx — per-user, so it must be dynamic. Say so explicitly.
export const dynamic = 'force-dynamic';

export default async function AccountPage() {
  const session = await auth();                    // reads cookies → dynamic anyway
  return <Account user={await getUser(session.userId)} />;
}
```

```tsx
// A shell that renders immediately, with the slow part streamed in.
export default function OrdersPage() {
  return (
    <>
      <h1>Orders</h1>
      <Suspense fallback={<OrdersSkeleton />}>
        <OrdersTable />          {/* awaits a slow query without blocking the shell */}
      </Suspense>
    </>
  );
}
```

**Bad Example** — everything dynamic by accident, or static when it must not be

```tsx
// A single cookie read at the top of a shared layout makes EVERY route below it
// dynamic, silently turning a static site into a server-rendered one.
export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const theme = (await cookies()).get('theme')?.value ?? 'light';
  return <html data-theme={theme}><body>{children}</body></html>;
}
```

```tsx
// Force-static on a page whose content is per-user: the first visitor's data is
// cached and served to everyone else.
export const dynamic = 'force-static';

export default async function AccountPage() {
  const session = await auth();
  return <Account user={await getUser(session.userId)} />;
}
```

---

## Common Mistakes

Avoid:

Making every page dynamic.

Using Dynamic Rendering for static content.

Disabling caching unnecessarily.

Fetching identical data multiple times.

Rendering large interactive pages entirely on the client.

Ignoring SEO implications.

Choosing rendering strategies based solely on developer convenience.

---

## Completion Criteria

A rendering strategy is complete when:

- it matches business requirements;
- unnecessary server rendering has been avoided;
- caching strategy is aligned;
- SEO requirements are satisfied;
- performance has been considered;
- the implementation remains maintainable.

---

## Summary

Selecting the correct rendering strategy is one of the most important architectural decisions in a Next.js application.

By favoring Static Rendering whenever possible, introducing ISR for periodically changing content, reserving Dynamic Rendering for personalized experiences, and leveraging Streaming and Partial Prerendering where appropriate, applications achieve an optimal balance between performance, scalability, freshness, and maintainability.

## Related

- `knowledge/nextjs/06-server-components.md`
- `knowledge/nextjs/10-caching.md`
- `knowledge/nextjs/09-data-fetching.md`
- `knowledge/nextjs/20-performance.md`
