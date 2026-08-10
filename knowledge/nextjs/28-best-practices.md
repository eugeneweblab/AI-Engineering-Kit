---
id: nextjs/28-best-practices
topic: nextjs
slug: best-practices
title: "Next.js Best Practices"
type: doc
order: 28
status: ready
tags: [nextjs, best-practices, NextResponse, EventPage, ProductsPage, generateMetadata, getEvent, engineering, next, building]
related: [nextjs/29-engineering-principles, nextjs/100-common-antipatterns, nextjs/06-server-components]
when_to_use: "Read for a concise reference of engineering best practices when building a Next.js app."
---
# Next.js Best Practices

## Purpose

This document summarizes the engineering best practices for building production-grade Next.js applications.

The objective is to provide a concise reference that reinforces the architectural principles, development standards, and engineering guidelines defined throughout this knowledge base.

These practices should guide day-to-day development decisions.

---

## Core Principle

Optimize for long-term maintainability.

Good architecture is more valuable than short-term implementation speed.

---

## Architecture

Prefer:

- Server Components by default.
- Feature-based organization.
- Clear separation of responsibilities.
- Small, focused modules.
- Reusable shared components.

Avoid:

- monolithic pages;
- deeply nested component trees;
- duplicated business logic;
- tightly coupled features.

---

## Rendering

Prefer:

- Static Rendering whenever possible.
- Dynamic Rendering only when required.
- Streaming for slow content.
- Server-side data fetching.
- Minimal client-side hydration.

Avoid unnecessary Client Components.

Components are Server Components by default. Add `"use client"` only when a component needs interactivity, state, effects, or browser APIs. Keep the `"use client"` boundary as deep in the tree as possible so most of the page stays server-rendered.

Bad — the whole page opts into the client just to make one button interactive:

```tsx
"use client";

import { useState } from "react";

// Everything below now ships to the browser, including the product list
// that never needed to be interactive.
export default function ProductsPage({ products }: { products: Product[] }) {
    const [open, setOpen] = useState(false);

    return (
        <section>
            <ul>
                {products.map((p) => (
                    <li key={p.id}>{p.name}</li>
                ))}
            </ul>
            <button onClick={() => setOpen(!open)}>Toggle filters</button>
        </section>
    );
}
```

Good — the page stays a Server Component; only the interactive island is a Client Component:

```tsx
// app/products/page.tsx  (Server Component)
import { FiltersToggle } from "./filters-toggle";

export default async function ProductsPage() {
    const products = await getProducts();

    return (
        <section>
            <ul>
                {products.map((p) => (
                    <li key={p.id}>{p.name}</li>
                ))}
            </ul>
            <FiltersToggle />
        </section>
    );
}
```

```tsx
// app/products/filters-toggle.tsx  (Client Component)
"use client";

import { useState } from "react";

export function FiltersToggle() {
    const [open, setOpen] = useState(false);
    return <button onClick={() => setOpen(!open)}>Toggle filters</button>;
}
```

---

## Components

Components should:

- have a single responsibility;
- receive explicit props;
- avoid hidden side effects;
- remain reusable;
- remain easy to test.

Prefer composition over inheritance.

---

## Business Logic

Business logic belongs in:

- services;
- Server Actions;
- utility modules;
- domain-specific libraries.

Keep UI components focused on presentation.

Use Server Actions for mutations. A file or function marked `"use server"` runs only on the server; validate and authorize inside it, then revalidate affected caches.

```tsx
// app/actions/create-post.ts
"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { db } from "@/lib/db";

const CreatePost = z.object({
    title: z.string().min(1).max(200),
    body: z.string().min(1),
});

export async function createPost(formData: FormData) {
    const session = await auth();
    if (!session) throw new Error("Unauthorized");

    // Never trust the client — validate on the server.
    const data = CreatePost.parse({
        title: formData.get("title"),
        body: formData.get("body"),
    });

    await db.post.create({ data: { ...data, authorId: session.userId } });

    revalidatePath("/posts");
    redirect("/posts");
}
```

```tsx
// app/posts/new/page.tsx  (Server Component — no client JS needed)
import { createPost } from "@/app/actions/create-post";

export default function NewPostPage() {
    return (
        <form action={createPost}>
            <input name="title" required />
            <textarea name="body" required />
            <button type="submit">Publish</button>
        </form>
    );
}
```

---

## State Management

Keep state as close as possible to where it is used.

Prefer:

- server state on the server;
- local UI state locally;
- global state only when truly shared.

Avoid unnecessary global stores.

---

## Data Fetching

Prefer:

- server-side fetching;
- parallel requests;
- request caching;
- reusable data access layers.

Avoid request waterfalls.

In Next.js 15+, `fetch()` is **uncached by default** (`no-store`). Caching is opt-in — reach for it deliberately based on freshness requirements.

Bad — assuming the response is cached because it "always was":

```tsx
// Next 15 fetches this fresh on every request — no caching happens implicitly.
const res = await fetch("https://api.example.com/pricing");
```

Good — opt into the strategy the data actually needs:

```tsx
// Static content: cache indefinitely until manually revalidated.
const docs = await fetch(url, { cache: "force-cache" });

// Frequently updated content: revalidate on a time interval (seconds).
const products = await fetch(url, { next: { revalidate: 3600 } });

// Tag-based revalidation, so a mutation can invalidate exactly this data.
const posts = await fetch(url, { next: { tags: ["posts"] } });
// elsewhere, after a mutation: revalidateTag("posts", "max") — or updateTag("posts")
// in a Server Action when the user must see their own write immediately.

// User-specific data: keep it fresh and never cache it publicly.
const cart = await fetch(url, { cache: "no-store" });
```

Run independent requests in parallel to avoid waterfalls:

```tsx
const [user, orders] = await Promise.all([getUser(id), getOrders(id)]);
```

---

## API Design

Design APIs that are:

- consistent;
- predictable;
- well documented;
- versioned when appropriate.

Validate every request.

Expose HTTP endpoints with Route Handlers (`app/**/route.ts`). Export one async function per HTTP method; use the Web `Request`/`Response` APIs and `NextResponse` for JSON.

```tsx
// app/api/posts/route.ts
import { NextResponse } from "next/server";
import { z } from "zod";
import { db } from "@/lib/db";

const NewPost = z.object({ title: z.string().min(1) });

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const limit = Number(searchParams.get("limit") ?? "20");
    const posts = await db.post.findMany({ take: limit });
    return NextResponse.json(posts);
}

export async function POST(request: Request) {
    const parsed = NewPost.safeParse(await request.json());
    if (!parsed.success) {
        return NextResponse.json(
            { error: parsed.error.flatten() },
            { status: 400 },
        );
    }
    const post = await db.post.create({ data: parsed.data });
    return NextResponse.json(post, { status: 201 });
}
```

Dynamic segments arrive via the second argument. In Next.js 15+, `params` is a `Promise` and must be awaited:

```tsx
// app/api/posts/[id]/route.ts
export async function GET(
    _request: Request,
    { params }: { params: Promise<{ id: string }> },
) {
    const { id } = await params;
    const post = await db.post.findUnique({ where: { id } });
    if (!post) return NextResponse.json({ error: "Not found" }, { status: 404 });
    return NextResponse.json(post);
}
```

Note: `params` and `searchParams` in Page/Layout components are also `Promise`-typed in Next.js 15+ and must be awaited.

For cross-cutting concerns (auth redirects, header rewrites), use `proxy.ts` at the project root — the file convention formerly called `middleware.ts` — with a `matcher` so it only runs where needed:

```ts
// proxy.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
    const token = request.cookies.get("session")?.value;
    if (!token) {
        return NextResponse.redirect(new URL("/login", request.url));
    }
    return NextResponse.next();
}

export const config = {
    matcher: ["/dashboard/:path*", "/account/:path*"],
};
```

---

## Security

Always:

- authenticate users;
- authorize every protected action;
- validate input;
- protect secrets;
- use HTTPS.

Never trust client-side validation.

Keep secrets on the server. Only variables prefixed with `NEXT_PUBLIC_` are inlined into the client bundle — everything else is server-only. Read secrets from `process.env` inside Server Components, Route Handlers, or Server Actions.

Bad — a secret prefixed `NEXT_PUBLIC_` is shipped to every browser:

```tsx
// NEXT_PUBLIC_STRIPE_SECRET_KEY leaks into the client bundle. Never do this.
const key = process.env.NEXT_PUBLIC_STRIPE_SECRET_KEY;
```

Good — the secret stays server-side; only the publishable key is exposed:

```tsx
// Server Action / Route Handler / Server Component only.
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

// Safe to use in a Client Component — it is meant to be public.
const publishable = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
```

---

## Performance

Continuously review:

- Core Web Vitals;
- bundle size;
- image optimization;
- font loading;
- caching;
- hydration;
- network requests.

Measure before optimizing.

Use `next/image` for automatic sizing, lazy loading, and modern formats. Provide `width`/`height` (or `fill`) to reserve layout space and avoid CLS; mark above-the-fold images `priority`.

```tsx
import Image from "next/image";

export function Hero() {
    return (
        <Image
            src="/hero.jpg"
            alt="Product hero"
            width={1200}
            height={600}
            priority
        />
    );
}
```

Load fonts with `next/font` — they are self-hosted at build time (no render-blocking request to a font CDN) and expose a stable class name:

```tsx
// app/layout.tsx
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"], display: "swap" });

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className={inter.className}>
            <body>{children}</body>
        </html>
    );
}
```

---

## Accessibility

Ensure every feature supports:

- keyboard navigation;
- semantic HTML;
- screen readers;
- focus management;
- sufficient color contrast.

Accessibility is a default requirement.

---

## SEO

Public pages should provide:

- meaningful titles;
- unique descriptions;
- canonical URLs;
- semantic HTML;
- structured metadata.

Search engines should clearly understand every page.

Export a static `metadata` object for fixed pages, or an async `generateMetadata` when the tags depend on data. For statically rendered dynamic routes, export `generateStaticParams` to pre-build the paths.

```tsx
// app/blog/[slug]/page.tsx
import type { Metadata } from "next";

export async function generateStaticParams() {
    const posts = await getAllPosts();
    return posts.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({
    params,
}: {
    params: Promise<{ slug: string }>;
}): Promise<Metadata> {
    const { slug } = await params;
    const post = await getPost(slug);
    return {
        title: post.title,
        description: post.excerpt,
        alternates: { canonical: `/blog/${slug}` },
        openGraph: { title: post.title, description: post.excerpt },
    };
}

export default async function BlogPostPage({
    params,
}: {
    params: Promise<{ slug: string }>;
}) {
    const { slug } = await params;
    const post = await getPost(slug);
    return <article>{post.body}</article>;
}
```

---

## Testing

Automate verification through:

- unit tests;
- integration tests;
- end-to-end tests;
- accessibility testing.

Test observable behavior rather than implementation details.

---

## Observability

Every production application should provide:

- structured logging;
- metrics;
- tracing;
- health checks;
- actionable alerts.

Production systems should always be diagnosable.

---

## Deployment

Prefer:

- automated deployments;
- immutable builds;
- environment isolation;
- rollback capability;
- deployment verification.

Manual production changes should be exceptional.

---

## Documentation

Maintain documentation for:

- architecture;
- APIs;
- environment variables;
- deployment;
- operational procedures.

Documentation should evolve with the codebase.

---

## Code Quality

Write code that is:

- readable;
- consistent;
- type-safe;
- modular;
- maintainable.

Optimize for the next developer—not just the current task.

---

## Review Checklist

Before merging code, verify:

☐ Architecture follows project standards.

☐ Business logic is properly separated.

☐ Components remain reusable.

☐ Performance impact reviewed.

☐ Accessibility verified.

☐ Security reviewed.

☐ Tests updated.

☐ Documentation updated when required.

---

## Engineering Mindset

Engineers should strive to:

- solve root causes rather than symptoms;
- keep solutions simple;
- reduce technical debt;
- improve consistency;
- automate repetitive work;
- leave the codebase better than they found it.

Long-term maintainability should guide engineering decisions.

---

## Examples

**Good Example** — a feature assembled from the framework's own defaults

```tsx
// app/events/[slug]/page.tsx
export const revalidate = 300;

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const event = await getEvent((await params).slug);   // deduplicated with the page fetch
  return event ? { title: event.name } : { title: 'Not found', robots: { index: false } };
}

export default async function EventPage({ params }: PageProps) {
  const { slug } = await params;
  const event = await getEvent(slug);
  if (!event) notFound();

  return (
    <article>
      <h1>{event.name}</h1>
      {/* Slow, non-critical region streams in; the article does not wait. */}
      <Suspense fallback={<AttendeesSkeleton />}>
        <Attendees eventId={event.id} />
      </Suspense>
      {/* The only interactive leaf. */}
      <RegisterButton eventId={event.id} />
    </article>
  );
}
```

Server by default, `notFound()` instead of a hand-rolled 404, metadata derived from the same
data, caching declared per route, and one small client boundary.

**Bad Example** — every default overridden

```tsx
'use client';

// force-dynamic on content that changes hourly: every request re-renders and
// nothing is cached, for no benefit.
export const dynamic = 'force-dynamic';

export default function EventPage({ params }: { params: { slug: string } }) {
  const [event, setEvent] = useState<Event | null>(null);
  const [attendees, setAttendees] = useState<Attendee[]>([]);

  // A waterfall the server could have parallelised, executed after hydration.
  useEffect(() => {
    fetch(`/api/events/${params.slug}`)
      .then((r) => r.json())
      .then((e) => {
        setEvent(e);
        return fetch(`/api/events/${e.id}/attendees`);
      })
      .then((r) => r.json())
      .then(setAttendees);
  }, [params.slug]);

  // A 404 rendered as a 200: crawlers index it, monitoring counts it as success.
  if (!event) return <p>Not found</p>;

  return <h1>{event.name}</h1>;
}
```

---

## Common Mistakes

Avoid:

- unnecessary complexity;
- premature optimization;
- duplicated code;
- oversized components;
- excessive global state;
- missing validation;
- inconsistent architecture;
- undocumented decisions.

---

## Completion Criteria

An implementation follows Next.js best practices when:

- architecture remains consistent;
- rendering strategy is appropriate;
- performance has been considered;
- security is enforced;
- accessibility is preserved;
- testing provides confidence;
- documentation reflects the implementation.

---

## Summary

Successful Next.js applications are the result of consistent engineering practices rather than isolated technical decisions.

By following the principles described throughout this knowledge base—server-first architecture, clear separation of responsibilities, secure development, performance optimization, accessibility, testing, observability, and disciplined deployment—teams can build applications that remain scalable, maintainable, and reliable as they evolve.

## Related

- `knowledge/nextjs/29-engineering-principles.md`
- `knowledge/nextjs/100-common-antipatterns.md`
- `knowledge/nextjs/06-server-components.md`
