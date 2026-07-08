---
id: seo/20-headless-seo
topic: seo
slug: headless-seo
title: "Headless SEO"
type: doc
order: 20
status: ready
tags: [seo, headless-seo]
related: [seo/19-javascript-seo, seo/04-rendering, seo/05-metadata, seo/09-structured-data]
when_to_use: "Read before building or reviewing a decoupled front end backed by a headless CMS or API-first architecture."
---
# Headless SEO

## Purpose

This document defines how to keep SEO correct in a *headless* architecture — where a
front-end framework (Next.js, Nuxt, Astro, SvelteKit) renders content pulled from a
headless CMS or API, rather than a monolith that emits HTML directly. It covers where
SEO signals must live, who owns them, and how the decoupling introduces failure modes a
traditional CMS handled for you.

Headless SEO is the practice of ensuring that everything a search engine needs —
rendered content, `<head>` metadata, canonical URLs, structured data, redirects, status
codes — is produced correctly by the front end, because the CMS no longer controls the
final page.

## Why It Matters

Traditional CMSes (WordPress, Drupal) shipped SEO by default: server-rendered HTML,
plugins for metadata and sitemaps, redirects managed in one admin. Going headless throws
all of that away and hands responsibility to application code. The most common outcome is
a beautiful, fast, client-rendered site that ranks for nothing because content lives only
in JavaScript, metadata is missing or hardcoded, and there is no sitemap or redirect map.
The content team assumes SEO "just works" as it did before; the engineers assume the CMS
handles it. Nobody owns it, and it silently regresses.

## Core Principles

- **The front end owns every SEO signal now.** Rendering mode, `<head>` tags, canonicals,
  hreflang, structured data, sitemaps, redirects, and status codes are application
  responsibilities. Assign an owner explicitly.
- **Render on the server or at build time for indexable routes.** A headless site is
  still subject to the [JavaScript SEO](19-javascript-seo.md) rules — content must be in
  the initial HTML, not hydrated in.
- **Metadata is content, so model it in the CMS.** SEO title, description, canonical
  override, `noindex` flag, and Open Graph image should be editable fields, not values
  hardcoded in components — otherwise editors cannot fix a bad title without a deploy.
- **URL structure is decoupled from content structure — map it deliberately.** The CMS
  slug, the API path, and the public URL are three different things. Define the canonical
  public URL and enforce it.
- **Redirects and status codes must be reimplemented.** Deleting a CMS entry should yield
  a `404`/`410`; changing a slug should yield a `301`. Nothing does this for you now.

## Best Practices

- Use SSR or SSG (Astro, Next.js RSC, Nuxt) so content and `<head>` are server-rendered.
  Reserve client rendering for non-indexable, interactive views.
- Add SEO fields to every content type in the CMS: `metaTitle`, `metaDescription`,
  `canonicalUrl`, `noindex`, `ogImage`. Fall back to sensible defaults when empty, but
  never make them uneditable. See [metadata](05-metadata.md).
- Generate the sitemap and `robots.txt` dynamically from the CMS/API at build or request
  time, so new and removed content stays in sync automatically.
- Emit [structured data](09-structured-data.md) (JSON-LD) from CMS fields, server-side,
  so the markup matches the visible content and updates with it.
- Centralize a redirect map (CMS-managed or config) and apply it in middleware; on
  content deletion, return `410 Gone` or `404`, not a `200` fallback page.
- Handle preview/draft content with `noindex` and authentication so unpublished pages
  never reach the index.
- Invalidate caches/ISR on publish so the rendered page and its metadata reflect the
  latest CMS state without a full redeploy.

## Examples

**Good Example** — CMS-driven metadata, server-rendered, honest status

```jsx
// Metadata comes from editable CMS fields, resolved on the server.
export async function generateMetadata({ params }) {
  const page = await cms.getPage(params.slug); // API call at request/build time
  if (!page) return {}; // route returns 404 below
  return {
    title: page.seo.metaTitle ?? page.title,      // editable, with a fallback
    description: page.seo.metaDescription,
    robots: page.seo.noindex ? "noindex, follow" : "index, follow",
    alternates: { canonical: page.seo.canonicalUrl ?? `https://example.com/${page.slug}` },
    openGraph: { images: [page.seo.ogImage] },
  };
}

export default async function Page({ params }) {
  const page = await cms.getPage(params.slug);
  if (!page) notFound();                 // deleted entry → real 404
  if (page.status === "archived") gone(); // → 410, tells the engine to drop it
  return <Content blocks={page.body} />;  // server-rendered content
}
```

**Bad Example** — hardcoded head, client-only content, no status handling

```jsx
// Title/description hardcoded in the component: editors can't change them,
// and every page shares the same social preview.
export const metadata = {
  title: "My Site",
  description: "Welcome to my site",
};

export default function Page() {
  const [page, setPage] = useState(null);
  // Content fetched client-side → empty initial HTML → not indexed reliably.
  useEffect(() => { cms.getPage(slug).then(setPage); }, []);
  // Missing page renders a friendly screen but still returns HTTP 200 (soft 404).
  if (!page) return <div>Page not found</div>;
  return <Content blocks={page.body} />;
}
```

## Common Mistakes

- Assuming SEO "carried over" from the old CMS; nothing does unless the front end
  implements it.
- Hardcoding titles/descriptions in components so editors cannot fix them and every page
  looks identical in search and social.
- Client-only rendering of content pulled from the API, breaking indexation (see
  [JavaScript SEO](19-javascript-seo.md)).
- No dynamic sitemap or `robots.txt`, so new content is never announced and deleted
  content lingers.
- Slug changes with no `301`, and deletions returning `200` fallback pages instead of
  `404`/`410`.
- Draft/preview URLs indexable because they lack `noindex` and auth.

## Production Tips

- Add an end-to-end check per template that fetches a live URL and asserts the CMS-driven
  `<title>`, canonical, and JSON-LD appear in the server HTML.
- Wire publish webhooks to cache/ISR invalidation so metadata changes go live without a
  redeploy.
- Keep the redirect map in the CMS or a reviewed config file, versioned like code, so
  content editors and engineers share one source of truth.

## AI Review Checklist

- Are indexable routes server-rendered or statically generated, not client-only?
- Are SEO metadata fields editable in the CMS with sensible fallbacks, not hardcoded?
- Are sitemap and `robots.txt` generated dynamically from the content source?
- Is structured data emitted server-side from CMS fields and matching visible content?
- Do slug changes `301` and deletions return `404`/`410`, via a central redirect map?
- Are draft/preview pages `noindex` and access-controlled?

## Related

- `knowledge/seo/19-javascript-seo.md`
- `knowledge/seo/04-rendering.md`
- `knowledge/seo/05-metadata.md`
- `knowledge/seo/09-structured-data.md`
