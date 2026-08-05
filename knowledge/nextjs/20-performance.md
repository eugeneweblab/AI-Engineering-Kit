---
id: nextjs/20-performance
topic: nextjs
slug: performance
title: "Next.js Performance"
type: doc
order: 20
status: ready
tags: [nextjs, performance, DashboardPage, RevenueChart, AccountPage, AddToCartButton, ProductPage, setPending]
related: [nextjs/10-caching, nextjs/16-images, nextjs/08-rendering-strategies, performance/18-web-vitals]
when_to_use: "Read before diagnosing or optimizing performance and Core Web Vitals in a Next.js app."
---
# Next.js Performance

## Purpose

This document defines the engineering standards for optimizing performance in Next.js applications.

The objective is to deliver fast, responsive, scalable applications by making performance an architectural concern rather than a post-release optimization effort.

Every performance optimization should be measurable.

---

## Core Principle

Measure first.

Optimize second.

Every optimization should solve a verified performance problem.

---

## Performance Goals

Every application should optimize for:

- fast initial load;
- responsive interactions;
- smooth navigation;
- efficient rendering;
- minimal JavaScript;
- efficient network usage.

Performance should improve user experience rather than benchmark scores alone.

---

## Core Web Vitals

Optimize the following metrics:

- Largest Contentful Paint (LCP)
- Interaction to Next Paint (INP)
- Cumulative Layout Shift (CLS)

These metrics should guide architectural decisions.

---

## Server-First Rendering

Prefer Server Components whenever possible.

Benefits include:

- reduced JavaScript;
- faster rendering;
- improved SEO;
- smaller bundles.

Avoid converting Server Components into Client Components without necessity.

---

## Minimize Client JavaScript

Every Client Component increases:

- bundle size;
- hydration cost;
- JavaScript execution time.

Keep interactive boundaries as small as possible.

Push `"use client"` down to the smallest interactive leaf. A `"use client"` directive at the top of a file marks that module and every module it imports as part of the client bundle. Keep the page a Server Component and isolate only the interactive part.

Good:

```tsx
// app/products/[id]/page.tsx  — Server Component (no "use client")
import { AddToCartButton } from "./add-to-cart-button";

export default async function ProductPage({
    params,
}: {
    params: Promise<{ id: string }>;
}) {
    const { id } = await params;
    // Rendered on the server; no JS shipped for this markup.
    const product = await getProduct(id);

    return (
        <article>
            <h1>{product.name}</h1>
            <p>{product.description}</p>
            {/* Only this button and its dependencies hydrate on the client. */}
            <AddToCartButton productId={product.id} />
        </article>
    );
}
```

```tsx
// app/products/[id]/add-to-cart-button.tsx
"use client";

import { useState } from "react";

export function AddToCartButton({ productId }: { productId: string }) {
    const [pending, setPending] = useState(false);
    return (
        <button
            disabled={pending}
            onClick={async () => {
                setPending(true);
                await fetch("/api/cart", {
                    method: "POST",
                    body: JSON.stringify({ productId }),
                });
                setPending(false);
            }}
        >
            {pending ? "Adding…" : "Add to cart"}
        </button>
    );
}
```

Bad:

```tsx
// "use client" at the page root drags the entire subtree — description,
// layout, and every imported helper — into the client bundle just to make
// one button interactive.
"use client";

import { useState } from "react";

export default function ProductPage({ product }: { product: Product }) {
    const [pending, setPending] = useState(false);
    return (
        <article>
            <h1>{product.name}</h1>
            <p>{product.description}</p>
            <button disabled={pending} onClick={() => setPending(true)}>
                Add to cart
            </button>
        </article>
    );
}
```

`params` (and `searchParams`) are async in Next 15+ and must be awaited. A Client Component also cannot be `async` or `await params`; keep data loading in the Server Component and pass plain props down.

---

## Bundle Optimization

Review every dependency.

Ask:

- Is it necessary?
- Is there a smaller alternative?
- Can it run on the server?
- Can it be lazy loaded?

Avoid adding large libraries for small tasks.

---

## Code Splitting

Split JavaScript by feature.

Examples:

- dashboard;
- editor;
- charts;
- administration.

Users should only download code required for the current page.

---

## Dynamic Imports

Use dynamic imports for:

- large editors;
- charting libraries;
- maps;
- media players;
- rarely used components.

Load code only when it becomes necessary.

Use `next/dynamic` to split a heavy Client Component out of the initial bundle. It returns a component that loads its code on demand and can render a lightweight fallback while the chunk downloads.

Good:

```tsx
"use client";

import dynamic from "next/dynamic";

// The chart library is not in the initial bundle; it loads when this
// component mounts. ssr: false skips server rendering for a browser-only lib.
const RevenueChart = dynamic(() => import("./revenue-chart"), {
    loading: () => <div aria-busy="true">Loading chart…</div>,
    ssr: false,
});

export function Dashboard() {
    return (
        <section>
            <h2>Revenue</h2>
            <RevenueChart />
        </section>
    );
}
```

Bad:

```tsx
"use client";

// Statically imported -> the entire charting library ships in the initial
// bundle and runs on every page load, even for users who never scroll to it.
import RevenueChart from "./revenue-chart";

export function Dashboard() {
    return <RevenueChart />;
}
```

`ssr: false` is only allowed inside a Client Component. In a Server Component, `next/dynamic` still code-splits but renders on the server; use it there to defer a large but server-renderable component. Do not wrap above-the-fold, critical content in a dynamic import — the extra request delays first paint.

---

## Lazy Loading

Lazy load:

- heavy components;
- dialogs;
- image galleries;
- analytics dashboards;
- administrative features.

Avoid delaying critical content.

---

## Images

Optimize images by:

- serving responsive sizes;
- using modern formats;
- lazy loading below-the-fold images;
- avoiding oversized assets.

Prefer the Next.js `Image` component.

---

## Fonts

Optimize fonts by:

- self-hosting;
- subsetting;
- preloading critical fonts;
- minimizing font variants.

Avoid layout shifts caused by late font loading.

Use `next/font` to self-host fonts automatically. At build time it downloads the font files, serves them from your own origin (no request to a third-party server at runtime), and computes fallback metrics that reduce layout shift while the web font loads.

Good:

```tsx
// app/layout.tsx
import { Inter } from "next/font/google";

// Downloaded and self-hosted at build time; subset to the characters used.
const inter = Inter({
    subsets: ["latin"],
    display: "swap",
    variable: "--font-inter",
});

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className={inter.variable}>
            <body>{children}</body>
        </html>
    );
}
```

Bad:

```tsx
// A blocking <link> to a third-party font host: extra DNS + connection on the
// critical path, no automatic fallback metrics, and a request that leaks to an
// external origin. next/font eliminates all three.
export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
            <head>
                <link
                    href="https://fonts.googleapis.com/css2?family=Inter&display=swap"
                    rel="stylesheet"
                />
            </head>
            <body>{children}</body>
        </html>
    );
}
```

Load fonts once in the root layout rather than per component, and keep the number of families and weights small — each variant is another file to download.

---

## Data Fetching

Reduce unnecessary requests.

Prefer:

- server-side fetching;
- parallel requests;
- request memoization;
- caching.

Avoid request waterfalls.

Independent requests should be issued together, not one after another. Awaiting each `fetch` in sequence forces the second request to wait for the first even when they do not depend on each other. Start them concurrently and await them with `Promise.all`.

Good:

```tsx
export default async function AccountPage() {
    // Both requests start immediately and resolve in parallel.
    // In Next 15+ fetch is uncached by default; opt in per request when the
    // data can tolerate staleness.
    const [profile, orders] = await Promise.all([
        fetch("https://api.example.com/profile", {
            next: { revalidate: 60 }, // cache + revalidate every 60s
        }).then((r) => r.json()),
        fetch("https://api.example.com/orders", {
            cache: "no-store", // always fresh
        }).then((r) => r.json()),
    ]);

    return <AccountView profile={profile} orders={orders} />;
}
```

Bad:

```tsx
export default async function AccountPage() {
    // Waterfall: orders does not start until profile resolves, even though
    // the two requests are unrelated. Total latency is the sum, not the max.
    const profile = await fetch("https://api.example.com/profile").then((r) =>
        r.json(),
    );
    const orders = await fetch("https://api.example.com/orders").then((r) =>
        r.json(),
    );

    return <AccountView profile={profile} orders={orders} />;
}
```

Within a single render pass, `fetch` requests with identical URL and options are automatically memoized, so calling the same endpoint from several components does not issue duplicate network requests. This request memoization is separate from the Data Cache and applies whether or not the request is cached.

---

## Caching

Use caching intentionally.

Review:

- browser cache;
- CDN cache;
- Data Cache;
- Route Cache;
- revalidation.

Avoid disabling caches without justification.

---

## Streaming

Stream slow or independent content.

Examples:

- analytics;
- recommendations;
- reports;
- dashboards.

Streaming improves perceived performance.

Wrap a slow, independent section in `<Suspense>` so the fast shell streams to the browser immediately while the slow part renders. The page does not block on its slowest data source.

Good:

```tsx
import { Suspense } from "react";

export default function DashboardPage() {
    return (
        <main>
            {/* Shell and header stream immediately. */}
            <h1>Dashboard</h1>

            {/* The slow widget streams in when ready; its fallback shows first. */}
            <Suspense fallback={<p aria-busy="true">Loading analytics…</p>}>
                <Analytics />
            </Suspense>
        </main>
    );
}

async function Analytics() {
    // A slow, uncached request lives inside the boundary so it cannot
    // delay the rest of the page.
    const data = await fetch("https://api.example.com/analytics", {
        cache: "no-store",
    }).then((r) => r.json());

    return <AnalyticsView data={data} />;
}
```

A `loading.tsx` file in a route segment is sugar for wrapping that segment's `page` in a Suspense boundary, giving an instant loading state during navigation. Use explicit `<Suspense>` boundaries when only part of a page is slow.

Bad:

```tsx
// No boundary: the whole page blocks until the analytics request resolves,
// so nothing renders — the header, nav, and shell all wait on the slowest fetch.
export default async function DashboardPage() {
    const data = await fetch("https://api.example.com/analytics", {
        cache: "no-store",
    }).then((r) => r.json());

    return (
        <main>
            <h1>Dashboard</h1>
            <AnalyticsView data={data} />
        </main>
    );
}
```

---

## Partial Prerendering

When supported by the project, prefer Partial Prerendering (PPR) over fully dynamic rendering when only small sections require personalization.

---

## Hydration

Hydrate only interactive components.

Avoid hydrating:

- static content;
- marketing pages;
- documentation;
- read-only views.

Hydration is one of the largest client-side performance costs.

---

## Rendering

Avoid unnecessary rerenders.

Review:

- component boundaries;
- state ownership;
- memoization;
- prop changes.

Optimize only after identifying real bottlenecks.

---

## Third-Party Scripts

Review every third-party script.

Examples:

- analytics;
- chat widgets;
- marketing tools;
- advertisements.

Load scripts only when required.

---

## Network Performance

Reduce:

- request count;
- payload size;
- duplicate requests.

Compress assets and enable HTTP caching.

---

## Database Performance

Optimize:

- query count;
- indexes;
- pagination;
- selected columns.

Avoid N+1 query problems.

---

## Monitoring

Continuously monitor:

- Core Web Vitals;
- server response times;
- bundle size;
- cache hit ratio;
- rendering performance.

Performance should be continuously measured.

---

## Profiling

Use profiling tools before optimizing.

Examples:

- React DevTools Profiler;
- Chrome DevTools;
- Lighthouse;
- Next.js bundle analyzer.

Avoid premature optimization.

---

## Accessibility

Performance improvements must never reduce accessibility.

Verify:

- loading indicators;
- keyboard navigation;
- focus management;
- semantic HTML.

Accessibility and performance should improve together.

---

## Security

Performance optimizations must never weaken security.

Examples:

- disabling validation;
- exposing private data;
- bypassing authorization.

Security always takes priority.

---

## AI Execution Checklist

## Investigation

☐ Measure current performance.

☐ Identify bottlenecks.

☐ Review bundle size.

☐ Review rendering strategy.

---

## Planning

☐ Minimize client JavaScript.

☐ Optimize loading strategy.

☐ Improve caching.

☐ Reduce network requests.

---

## Verification

☐ Core Web Vitals improved.

☐ Bundle size reviewed.

☐ Caching configured.

☐ Accessibility preserved.

☐ Security maintained.

☐ Performance measurable.

---

## Examples

**Good Example** — ship less JavaScript, stream the slow parts, load heavy widgets on demand

```tsx
// The shell renders immediately; each slow region streams in independently.
export default function DashboardPage() {
  return (
    <>
      <h1>Dashboard</h1>
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />                     {/* awaits a 400 ms query */}
      </Suspense>
      <Suspense fallback={<ChartSkeleton />}>
        <RevenueChart />              {/* awaits a 2 s aggregation */}
      </Suspense>
    </>
  );
}
```

```tsx
// A 300 kB charting library, loaded only when the component actually renders,
// and never included in the server bundle.
const HeavyChart = dynamic(() => import('@/components/heavy-chart'), {
  ssr: false,
  loading: () => <ChartSkeleton />,
});
```

```ts
// next.config.ts — measure the budget in CI rather than describing it in a doc.
export default {
  experimental: { optimizePackageImports: ['lucide-react', 'date-fns'] },
  // ANALYZE=true npm run build prints the per-route first-load JS.
};
```

**Bad Example** — a client boundary at the root and barrel imports

```tsx
'use client';                       // the entire route becomes client-rendered

// A barrel file: importing one icon pulls the whole library into the bundle
// unless the package is tree-shakeable and side-effect free — most are not.
import { ChevronDown } from '@/components/index';
import moment from 'moment';        // 300 kB, all locales, for one date format

import HeavyChart from '@/components/heavy-chart';   // always in the first load

export default function DashboardPage() {
  const [stats, setStats] = useState(null);

  // Everything awaited before anything renders: the user sees a spinner for the
  // duration of the slowest query, with no streamed shell.
  useEffect(() => {
    Promise.all([fetch('/api/stats'), fetch('/api/revenue')]).then(/* … */);
  }, []);

  if (!stats) return <Spinner />;
  return <HeavyChart data={stats} />;
}
```

---

## Common Mistakes

Avoid:

Optimizing without measurement.

Making entire pages Client Components.

Disabling caching.

Loading unnecessary JavaScript.

Adding oversized dependencies.

Creating request waterfalls.

Hydrating static content.

Ignoring bundle growth.

---

## Completion Criteria

A performance optimization is complete when:

- measurable improvements have been achieved;
- rendering strategy has been reviewed;
- client JavaScript has been minimized;
- caching is appropriate;
- Core Web Vitals meet project targets;
- accessibility and security remain unaffected.

---

## Summary

Performance is a continuous engineering practice rather than a one-time task.

By prioritizing server rendering, minimizing client-side JavaScript, optimizing bundles, leveraging caching, and continuously measuring results, Next.js applications remain fast, scalable, and maintainable throughout their lifecycle.

## Related

- `knowledge/nextjs/10-caching.md`
- `knowledge/nextjs/16-images.md`
- `knowledge/nextjs/08-rendering-strategies.md`
- `knowledge/performance/18-web-vitals.md`
