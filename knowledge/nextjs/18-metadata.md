---
id: nextjs/18-metadata
topic: nextjs
slug: metadata
title: "Next.js Metadata"
type: doc
order: 18
status: ready
tags: [nextjs, metadata, generateMetadata, getPost, viewport, EventPage, URL]
related: [nextjs/19-seo, nextjs/05-layouts, seo/05-metadata]
when_to_use: "Read before configuring page metadata or Open Graph tags in a Next.js app."
---
# Next.js Metadata

## Purpose

This document defines the engineering standards for configuring metadata in Next.js applications.

The objective is to ensure every page provides accurate, complete, and search-engine-friendly metadata while supporting rich previews, accessibility, and modern web standards.

Metadata should be generated on the server and remain closely aligned with the content of each page.

---

## Core Principle

Metadata describes content.

Every page should provide metadata that accurately represents its purpose.

Avoid generic or duplicated metadata.

---

## Metadata Goals

Every page should strive for:

- meaningful titles;
- unique descriptions;
- accurate canonical URLs;
- rich social previews;
- proper indexing;
- accessibility.

Metadata should improve both user experience and discoverability.

---

## Metadata Hierarchy

Metadata follows the routing hierarchy.

```
Root Layout

↓

Nested Layout

↓

Page
```

Layouts provide defaults.

Pages override only what is necessary.

Metadata is exported from the module using either a static `metadata` object or an async `generateMetadata` function. Both live in a Server Component (a `layout.tsx` or `page.tsx`) — the Metadata API does not run in Client Components.

Set `metadataBase` once in the root layout so every relative `openGraph`/`twitter`/`alternates` URL resolves to an absolute URL. Use `title.template` so nested pages compose a consistent suffix without repeating the brand name.

```tsx
// app/layout.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
    metadataBase: new URL("https://example.com"),
    title: {
        template: "%s | Acme",
        default: "Acme — Ergonomic Office Furniture",
    },
    description: "Ergonomic office furniture engineered for long workdays.",
};
```

```tsx
// app/pricing/page.tsx
import type { Metadata } from "next";

// Renders as "Pricing | Acme" via the parent template.
export const metadata: Metadata = {
    title: "Pricing",
    description: "Simple, transparent pricing for teams of every size.",
    alternates: { canonical: "/pricing" },
};
```

---

## Page Title

Every page should define a unique and descriptive title.

A good title:

- identifies the content;
- remains concise;
- reflects user intent;
- supports SEO.

Avoid generic titles such as:

```
Home

Dashboard

Page

Index
```

---

## Meta Description

Provide a meaningful description for every indexable page.

Descriptions should:

- summarize the content;
- encourage clicks;
- remain accurate;
- avoid duplication.

Do not generate descriptions from unrelated content.

---

## Canonical URL

Every indexable page should define a canonical URL.

Canonical URLs help:

- prevent duplicate content;
- consolidate ranking signals;
- improve search engine understanding.

Only one canonical URL should exist for each resource.

Configure canonical URLs through `alternates.canonical`. With `metadataBase` set, a relative path resolves to an absolute canonical URL. Use `alternates.languages` to declare `hreflang` alternates for localized routes.

```tsx
export const metadata: Metadata = {
    alternates: {
        canonical: "/blog/nextjs-metadata",
        languages: {
            "en-US": "/en/blog/nextjs-metadata",
            "de-DE": "/de/blog/nextjs-metadata",
        },
    },
};
```

---

## Open Graph

Configure Open Graph metadata for social sharing.

Include:

- title;
- description;
- image;
- URL;
- type.

Open Graph metadata should accurately reflect page content.

```tsx
export const metadata: Metadata = {
    openGraph: {
        title: "Ergonomic Office Chairs",
        description: "Support that lasts the whole workday.",
        url: "/products/chairs", // resolved against metadataBase
        type: "website",
        images: [
            {
                url: "/og/chairs.png", // resolved against metadataBase
                width: 1200,
                height: 630,
                alt: "Charcoal ergonomic office chair",
            },
        ],
    },
};
```

---

## Twitter Cards

Configure Twitter Card metadata.

Typical properties include:

- title;
- description;
- image;
- card type.

Ensure previews remain visually consistent across platforms.

```tsx
export const metadata: Metadata = {
    twitter: {
        card: "summary_large_image",
        title: "Ergonomic Office Chairs",
        description: "Support that lasts the whole workday.",
        images: ["/og/chairs.png"],
    },
};
```

---

## Metadata Images

Social preview images should:

- represent the content;
- have appropriate dimensions;
- remain readable;
- avoid excessive text.

Maintain consistent branding across the application.

Next.js supports file-based Open Graph images. A static `opengraph-image.png` (or `twitter-image.png`) placed in a route segment is picked up automatically — no `metadata` entry required. For dynamic previews, export an image from `opengraph-image.tsx` using `ImageResponse`; the file runs on the server and its output is cached.

```tsx
// app/blog/[slug]/opengraph-image.tsx
import { ImageResponse } from "next/og";
import { getPost } from "@/lib/posts";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function OgImage({
    params,
}: {
    params: Promise<{ slug: string }>;
}) {
    const { slug } = await params;
    const post = await getPost(slug);

    return new ImageResponse(
        (
            <div
                style={{
                    display: "flex",
                    height: "100%",
                    width: "100%",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 64,
                    background: "#0b0b0f",
                    color: "#fff",
                    padding: 80,
                }}
            >
                {post.title}
            </div>
        ),
        size,
    );
}
```

Note that `params` is a Promise in Next.js 15+ and must be awaited, matching the page and `generateMetadata` signatures in the same segment.

---

## Robots

Configure robots metadata intentionally.

Examples:

- index;
- noindex;
- follow;
- nofollow.

Administrative and private pages should not be indexed.

```tsx
// A private dashboard segment: keep it out of the index.
export const metadata: Metadata = {
    robots: { index: false, follow: false },
};
```

Site-wide crawl rules belong in a `robots.ts` file at the app root, which Next.js serves at `/robots.txt`.

```ts
// app/robots.ts
import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
    return {
        rules: { userAgent: "*", allow: "/", disallow: "/admin/" },
        sitemap: "https://example.com/sitemap.xml",
    };
}
```

---

## Viewport

Viewport and theme color are configured through a **separate `viewport` export**, not through the `metadata` object.

Since Next.js 14, `viewport`, `themeColor`, and `colorScheme` were moved out of `metadata` into their own `Viewport` export. Placing them inside `metadata` logs a deprecation warning and they are ignored. Like `metadata`, `viewport` may be a static object or an async `generateViewport` function, and lives in a Server Component.

Good:

```tsx
// app/layout.tsx
import type { Viewport } from "next";

export const viewport: Viewport = {
    width: "device-width",
    initialScale: 1,
    themeColor: [
        { media: "(prefers-color-scheme: light)", color: "#ffffff" },
        { media: "(prefers-color-scheme: dark)", color: "#0b0b0f" },
    ],
};
```

Bad:

```tsx
// themeColor/viewport inside metadata is deprecated and ignored.
export const metadata: Metadata = {
    themeColor: "#0b0b0f",
    viewport: "width=device-width, initial-scale=1",
};
```

---

## Theme Color

Theme colors improve browser integration and mobile appearance. As shown above, declare them in the `viewport` export via `themeColor`, optionally keyed by `prefers-color-scheme` for light and dark modes.

---

## Icons

Configure application icons centrally.

Examples:

- favicon;
- Apple Touch Icon;
- shortcut icon.

The simplest approach is file-based: drop `icon.png`, `apple-icon.png`, or a `favicon.ico` into the `app/` directory and Next.js injects the correct `<link>` tags automatically. For finer control, declare icons in `metadata.icons`.

```tsx
export const metadata: Metadata = {
    icons: {
        icon: "/icon.png",
        apple: "/apple-icon.png",
        shortcut: "/favicon.ico",
    },
};
```

Keep branding consistent.

---

## Structured Metadata

Metadata should accurately describe:

- page type;
- language;
- author;
- publication date;
- modification date.

Structured metadata improves interoperability.

---

## Dynamic Metadata

Generate metadata dynamically when it depends on fetched content.

Examples:

- blog articles;
- products;
- user-generated content;
- CMS pages.

Metadata generation should reuse existing server-side data whenever practical.

Export an async `generateMetadata` function. It receives the resolved route `params` (a Promise in Next.js 15+) and returns a `Metadata` object. Because Next.js deduplicates identical `fetch()` calls within a single request, calling the same fetch in both `generateMetadata` and the page issues **one** network request, not two — so there is no need to hoist data into a shared store just to avoid a double fetch.

Good:

```tsx
// app/blog/[slug]/page.tsx
import type { Metadata } from "next";
import { notFound } from "next/navigation";

// Uncached in Next.js 15 by default; opt into revalidation explicitly.
async function getPost(slug: string) {
    const res = await fetch(`https://api.example.com/posts/${slug}`, {
        next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return res.json() as Promise<{ title: string; excerpt: string }>;
}

export async function generateMetadata({
    params,
}: {
    params: Promise<{ slug: string }>;
}): Promise<Metadata> {
    const { slug } = await params;
    const post = await getPost(slug);
    if (!post) return {};

    return {
        title: post.title,
        description: post.excerpt,
        alternates: { canonical: `/blog/${slug}` },
        openGraph: { title: post.title, description: post.excerpt },
    };
}

export default async function Page({
    params,
}: {
    params: Promise<{ slug: string }>;
}) {
    const { slug } = await params;
    const post = await getPost(slug); // deduplicated with the fetch above
    if (!post) notFound();

    return <article>{post.title}</article>;
}
```

Bad:

```tsx
"use client";
import { useEffect } from "react";

// Metadata set from the client does not exist in the initial HTML, so
// crawlers and social scrapers never see it. The Metadata API is
// server-only — it does not run in Client Components.
export default function Page() {
    useEffect(() => {
        document.title = "Set too late for crawlers";
    }, []);
    return <article>…</article>;
}
```

---

## Localization

Localized pages should provide metadata in the appropriate language.

Ensure:

- translated titles;
- translated descriptions;
- correct language information.

Avoid mixing languages within metadata.

---

## Accessibility

Metadata should support accessibility by:

- providing meaningful document titles;
- identifying document language;
- improving navigation history.

Accessibility begins before the page is rendered.

---

## Performance

Metadata generation should:

- execute efficiently;
- avoid duplicate data requests;
- reuse cached data where possible.

Metadata should not become a performance bottleneck.

---

## Security

Do not expose:

- private identifiers;
- confidential information;
- internal implementation details.

Metadata is publicly visible.

---

## AI Execution Checklist

## Investigation

☐ Review page purpose.

☐ Determine indexing requirements.

☐ Review social sharing needs.

☐ Review localization.

---

## Planning

☐ Create unique title.

☐ Write meaningful description.

☐ Configure canonical URL.

☐ Configure social metadata.

---

## Verification

☐ Metadata unique.

☐ Canonical URL correct.

☐ Open Graph configured.

☐ Robots configured.

☐ Accessibility supported.

☐ Performance reviewed.

---

## Examples

**Good Example** — static defaults in the layout, per-page metadata generated from data

```ts
// app/layout.tsx — defaults every page inherits, with a title template.
import type { Metadata } from 'next';

export const metadata: Metadata = {
  metadataBase: new URL('https://example.com'),   // makes relative OG URLs absolute
  title: { default: 'Acme', template: '%s — Acme' },
  description: 'Event registration for engineering teams.',
  openGraph: { siteName: 'Acme', type: 'website', locale: 'en_GB' },
  robots: { index: true, follow: true },
};
```

```ts
// app/events/[slug]/page.tsx — derived from the same data the page renders.
export async function generateMetadata(
  { params }: { params: Promise<{ slug: string }> },
): Promise<Metadata> {
  const { slug } = await params;
  const event = await getEvent(slug);           // deduplicated with the page's own fetch

  if (!event) {
    return { title: 'Event not found', robots: { index: false } };
  }

  return {
    title: event.name,                          // becomes "Event name — Acme"
    description: event.summary.slice(0, 155),
    alternates: { canonical: `/events/${slug}` },
    openGraph: {
      title: event.name,
      description: event.summary,
      images: [{ url: event.imageUrl, width: 1200, height: 630, alt: event.name }],
    },
  };
}
```

**Bad Example** — tags injected on the client, and one description for the whole site

```tsx
'use client';

export default function EventPage({ event }: { event: Event }) {
  // Crawlers and social scrapers read the server response. Setting the title
  // after hydration means the shared preview and the indexed title are wrong.
  useEffect(() => {
    document.title = event.name;
    document.querySelector('meta[name="description"]')?.setAttribute('content', event.summary);
  }, [event]);

  return (
    <>
      {/* Hand-written tags in the body: duplicated, unmanaged, and ignored. */}
      <meta property="og:image" content="/og.png" />   {/* relative, no metadataBase */}
      <h1>{event.name}</h1>
    </>
  );
}
```

Every page sharing one description also means every search result looks the same, and
`og:image` without an absolute URL renders as a broken preview.

---

## Common Mistakes

Avoid:

Duplicated page titles.

Generic descriptions.

Missing canonical URLs.

Incorrect Open Graph images.

Indexing private pages.

Generating metadata on the client.

Exposing sensitive information.

Ignoring localization.

---

## Completion Criteria

Metadata implementation is complete when:

- every page has a unique title;
- descriptions accurately summarize content;
- canonical URLs are configured;
- social metadata is complete;
- indexing rules are appropriate;
- accessibility and performance have been considered.

---

## Summary

Metadata is an essential part of every modern web application.

By generating accurate server-side metadata, defining canonical URLs, configuring social previews, and maintaining consistency across layouts and pages, Next.js applications become more discoverable, accessible, and professional.

## Related

- `knowledge/nextjs/19-seo.md`
- `knowledge/nextjs/05-layouts.md`
- `knowledge/seo/05-metadata.md`
