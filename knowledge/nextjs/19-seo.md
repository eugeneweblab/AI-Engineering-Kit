---
id: nextjs/19-seo
topic: nextjs
slug: seo
title: "Next.js SEO"
type: doc
order: 19
status: ready
tags: [nextjs, seo]
related: []
when_to_use: "Read before optimizing a Next.js app for search engine discoverability and indexing."
---
# Next.js SEO

## Purpose

This document defines the engineering standards for Search Engine Optimization (SEO) in Next.js applications.

The objective is to build applications that are easily discoverable, correctly indexed, and optimized for both search engines and users.

SEO should be considered during architecture and development—not after deployment.

---

## Core Principle

Build pages for users first.

Help search engines understand the content.

SEO should naturally result from good architecture and high-quality content.

---

## SEO Goals

Every application should strive for:

- crawlable pages;
- meaningful URLs;
- high-quality metadata;
- fast loading;
- semantic HTML;
- excellent user experience.

Technical SEO should support business goals.

---

## Server-Side Rendering

Prefer rendering SEO-critical content on the server.

Suitable examples include:

- landing pages;
- documentation;
- blog articles;
- product pages;
- category pages.

Avoid relying on client-side rendering for primary page content.

In the App Router, Server Components are the default, so SEO-critical
markup is rendered on the server without any extra configuration. Only add
`"use client"` to the leaf components that genuinely need interactivity
(event handlers, `useState`, browser APIs) — never to the page shell that
holds the indexable content.

```tsx
// app/products/[slug]/page.tsx — Server Component by default
// No "use client": the title, description, and body are in the HTML.
import { notFound } from "next/navigation";
import { getProduct } from "@/lib/products";
import { AddToCartButton } from "./add-to-cart-button"; // "use client" lives here

export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>; // params is a Promise in Next 15
}) {
  const { slug } = await params;
  const product = await getProduct(slug);
  if (!product) notFound();

  return (
    <main>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <AddToCartButton productId={product.id} />
    </main>
  );
}
```

For content that rarely changes, pre-render every route at build time with
`generateStaticParams` so crawlers always hit fully-formed static HTML:

```tsx
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await getAllPostSlugs();
  return posts.map((slug) => ({ slug }));
}
```

---

## URL Structure

URLs should be:

- descriptive;
- readable;
- stable;
- hierarchical.

Good examples:

```
/products

/products/macbook-pro

/blog/server-components

/docs/getting-started
```

Avoid:

```
/page?id=123

/view/9384

/item?id=999
```

---

## Canonical URLs

Every indexable page should define a canonical URL.

Canonical URLs help:

- avoid duplicate content;
- consolidate ranking signals;
- improve indexing consistency.

Only one canonical URL should represent each resource.

Set `metadataBase` once in the root layout so every relative canonical and
Open Graph URL resolves to an absolute URL. Then declare the canonical per
page via `alternates.canonical`.

```tsx
// app/layout.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  metadataBase: new URL("https://example.com"),
  title: { default: "Example", template: "%s | Example" },
};
```

```tsx
// app/products/[slug]/page.tsx
import type { Metadata } from "next";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  return {
    // Resolves against metadataBase → https://example.com/products/<slug>
    alternates: { canonical: `/products/${slug}` },
  };
}
```

Good — one self-referencing canonical per page, always absolute.

Bad — hardcoded, host-specific canonicals scattered across pages that break
between preview and production environments:

```tsx
// Bad: absolute host baked in, easy to drift from the real deploy URL.
export const metadata = {
  alternates: { canonical: "http://localhost:3000/products/macbook-pro" },
};
```

---

## Metadata

Provide complete metadata for every public page.

Include:

- title;
- description;
- canonical URL;
- Open Graph;
- Twitter Card.

Metadata should accurately describe page content.

Export a static `metadata` object for fixed pages, or an async
`generateMetadata` function when the values depend on fetched content. Both
run only on the server. See `18-metadata` for the full field reference.

```tsx
// app/blog/[slug]/page.tsx
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getPost } from "@/lib/posts";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPost(slug); // deduped with the page's own call
  if (!post) return {};

  return {
    title: post.title,
    description: post.excerpt,
    alternates: { canonical: `/blog/${slug}` },
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: "article",
      url: `/blog/${slug}`,
      images: [{ url: post.coverImage, width: 1200, height: 630 }],
    },
    twitter: { card: "summary_large_image", title: post.title },
    robots: post.draft ? { index: false, follow: false } : undefined,
  };
}
```

Note on data reuse: `generateMetadata` and the page component often need the
same record. Wrap the loader in React `cache()` so the two calls dedupe
within a single request instead of fetching twice.

```ts
// lib/posts.ts
import { cache } from "react";

export const getPost = cache(async (slug: string) => {
  // fetch is NOT cached by default in Next 15 — opt in explicitly when the
  // data can be revalidated on a schedule. React cache() only dedupes within
  // one request; next.revalidate controls cross-request freshness.
  const res = await fetch(`https://api.example.com/posts/${slug}`, {
    next: { revalidate: 3600 },
  });
  if (!res.ok) return null;
  return res.json();
});
```

---

## Headings

Use a logical heading hierarchy.

Example:

```
H1

↓

H2

↓

H3
```

Each page should contain a single primary heading.

Avoid skipping heading levels.

---

## Semantic HTML

Prefer semantic elements.

Examples:

- `<main>`;
- `<article>`;
- `<section>`;
- `<nav>`;
- `<header>`;
- `<footer>`.

Semantic HTML improves both accessibility and search engine understanding.

---

## Internal Linking

Create meaningful internal links.

Benefits include:

- improved navigation;
- stronger crawlability;
- better content discovery.

Avoid orphaned pages.

---

## Breadcrumbs

Provide breadcrumbs where appropriate.

Benefits:

- improved navigation;
- clearer hierarchy;
- enhanced search appearance.

Breadcrumbs should reflect the URL structure.

---

## Structured Data

Use structured data when it benefits search engines.

Examples:

- articles;
- products;
- organizations;
- FAQs;
- breadcrumbs.

Structured data should accurately represent page content.

Render JSON-LD as a `<script type="application/ld+json">` from a Server
Component. Build the object in JS and serialize it — do not hand-write the
JSON string.

```tsx
// app/blog/[slug]/page.tsx (inside the Server Component)
export default async function PostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = await getPost(slug); // deduped via cache()

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: post.title,
    datePublished: post.publishedAt,
    dateModified: post.updatedAt,
    author: { "@type": "Person", name: post.author },
    image: post.coverImage,
  };

  return (
    <article>
      {/* Good: serialized object, rendered server-side, in the initial HTML */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <h1>{post.title}</h1>
      {/* ...body... */}
    </article>
  );
}
```

Good — one script per entity, values pulled from the same data the page
renders, so the markup never drifts from what users see.

Bad — injecting structured data from the client after hydration. Crawlers
that read the initial HTML may miss it, and the values can contradict the
visible content:

```tsx
"use client";
import { useEffect } from "react";

// Bad: runs only in the browser, absent from server-rendered HTML.
export function BadJsonLd({ data }: { data: object }) {
  useEffect(() => {
    const el = document.createElement("script");
    el.type = "application/ld+json";
    el.textContent = JSON.stringify(data);
    document.head.appendChild(el);
  }, [data]);
  return null;
}
```

---

## Images

Optimize images for SEO.

Ensure:

- descriptive filenames;
- meaningful alternative text;
- responsive sizing;
- optimized formats.

Avoid embedding important text inside images.

Use `next/image`. It emits width/height (reserving space to avoid layout
shift, which protects the CLS Core Web Vital), serves modern formats, and
lazy-loads by default. Mark the above-the-fold hero with `priority` and
always provide meaningful `alt` text. See `16-images` for details.

```tsx
import Image from "next/image";

export default function Hero() {
  return (
    <Image
      src="/products/macbook-pro-16.jpg"
      alt="Space-grey MacBook Pro 16-inch, lid open on a desk"
      width={1200}
      height={800}
      priority // above the fold — opt out of lazy loading
    />
  );
}
```

---

## Performance

Performance directly affects SEO.

Review:

- Core Web Vitals;
- server response time;
- image optimization;
- JavaScript size;
- layout stability.

Fast websites improve user satisfaction and search visibility.

---

## Mobile Experience

Every page should provide a high-quality mobile experience.

Review:

- responsive layouts;
- readable typography;
- touch targets;
- loading speed.

Mobile usability is essential.

---

## Crawlability

Ensure search engines can:

- access pages;
- follow internal links;
- discover important resources.

Avoid unnecessary barriers to crawling.

---

## Robots

Configure robots directives intentionally.

Examples:

- index;
- noindex;
- follow;
- nofollow.

Private or administrative pages should not be indexed.

There are two independent controls, and they serve different purposes:

- Per-page indexing is set through the `robots` field of a page's metadata
  (`{ index: false, follow: false }`), which emits a `<meta name="robots">`
  tag — see the Metadata example above.
- Site-wide crawl rules and the sitemap pointer live in `app/robots.ts`,
  which Next serves at `/robots.txt`.

```ts
// app/robots.ts
import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow: ["/admin/", "/api/"] },
    ],
    sitemap: "https://example.com/sitemap.xml",
    host: "https://example.com",
  };
}
```

Note: `disallow` stops crawling but does not guarantee de-indexing of
already-known URLs. To keep a page out of the index, use the `noindex`
robots meta tag on the page itself (crawling must be allowed for the tag to
be read).

---

## Sitemap

Generate a sitemap for public content.

Include:

- important pages;
- canonical URLs;
- update frequency where appropriate.

Keep the sitemap current.

Generate the sitemap from `app/sitemap.ts`, which Next serves at
`/sitemap.xml`. Return typed entries; combine static routes with dynamic
ones loaded from your data source.

```ts
// app/sitemap.ts
import type { MetadataRoute } from "next";
import { getAllPosts } from "@/lib/posts";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = "https://example.com";

  const staticRoutes: MetadataRoute.Sitemap = [
    { url: base, lastModified: new Date(), changeFrequency: "daily", priority: 1 },
    { url: `${base}/products`, changeFrequency: "weekly", priority: 0.8 },
  ];

  const posts = await getAllPosts();
  const postRoutes: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${base}/blog/${post.slug}`,
    lastModified: post.updatedAt,
    changeFrequency: "monthly",
    priority: 0.6,
  }));

  return [...staticRoutes, ...postRoutes];
}
```

For very large catalogs (Next caps a single sitemap file at 50,000 URLs),
split into segments with `generateSitemaps` and index them. Include only
canonical, indexable URLs — never `noindex` or redirected pages.

---

## Internationalization

For multilingual applications:

- provide localized URLs;
- define language alternatives;
- maintain translated metadata.

Avoid mixing multiple languages on the same page.

Declare language alternates through `alternates.languages` so Next emits the
`hreflang` link tags that let search engines map equivalent pages across
locales. Resolve them against `metadataBase`.

```tsx
// app/[locale]/products/[slug]/page.tsx
import type { Metadata } from "next";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, slug } = await params;
  return {
    alternates: {
      canonical: `/${locale}/products/${slug}`,
      languages: {
        "en-US": `/en/products/${slug}`,
        "de-DE": `/de/products/${slug}`,
        "x-default": `/en/products/${slug}`,
      },
    },
  };
}
```

---

## Duplicate Content

Prevent duplicate content by:

- using canonical URLs;
- avoiding multiple public URLs for identical content;
- redirecting outdated URLs when appropriate.

Search engines should clearly identify the preferred version.

---

## Accessibility

Good accessibility supports SEO.

Verify:

- semantic HTML;
- meaningful headings;
- descriptive links;
- alternative text.

Users and search engines both benefit from well-structured content.

---

## Monitoring

Monitor:

- indexing status;
- crawl errors;
- Core Web Vitals;
- search performance;
- broken links.

SEO should be measured continuously.

---

## Security

Serve all public pages over HTTPS.

Avoid exposing sensitive information in:

- metadata;
- structured data;
- URLs.

Security contributes to user trust.

---

## AI Execution Checklist

## Investigation

☐ Review page purpose.

☐ Review indexing requirements.

☐ Review metadata.

☐ Review URL structure.

---

## Planning

☐ Render SEO-critical content on the server.

☐ Configure metadata.

☐ Improve semantic HTML.

☐ Optimize internal linking.

---

## Verification

☐ Metadata complete.

☐ Canonical URL defined.

☐ Headings structured correctly.

☐ Images optimized.

☐ Accessibility verified.

☐ Performance reviewed.

---

## Common Mistakes

Avoid:

Rendering primary content only on the client.

Duplicated page titles.

Missing canonical URLs.

Generic metadata.

Broken internal links.

Multiple H1 elements.

Ignoring structured data.

Blocking search engines unintentionally.

---

## Completion Criteria

SEO implementation is complete when:

- public pages are crawlable;
- metadata is complete and unique;
- canonical URLs are configured;
- semantic HTML is used consistently;
- structured data is added where appropriate;
- performance and accessibility requirements are satisfied.

---

## Summary

SEO is the result of good engineering, not isolated optimizations.

By combining server-side rendering, semantic HTML, meaningful metadata, logical URL structures, fast performance, and accessible content, Next.js applications become easier to discover, easier to navigate, and better positioned for long-term search visibility.