---
id: frontend/11-seo
topic: frontend
slug: seo
title: "Frontend SEO"
type: doc
order: 11
status: ready
tags: [frontend, seo, noindex, robots.txt, "@type", "@context", generateMetadata, lastmod]
related: [frontend/07-rendering, frontend/08-performance, frontend/10-responsive-design, frontend/09-accessibility, frontend/05-routing]
when_to_use: "Read before building public, indexable pages or changing routing, rendering, or page metadata."
---
# Frontend SEO

## Purpose

This document defines how to make a frontend discoverable by search engines and shareable
on social platforms: crawlable HTML, correct metadata, structured data, canonical URLs, and
performance signals. It is written so an agent can build pages that rank and render correct
previews, without hidden crawl-blocking mistakes.

SEO for a modern frontend is mostly a rendering and correctness problem, not a keyword game.
If a crawler cannot get real HTML with the right metadata quickly, nothing else matters. This
doc scopes technical SEO — the part engineers own — not content strategy.

## Why It Matters

For most public products, organic search is the largest acquisition channel, and a single
technical mistake can silently deindex an entire site: a stray `noindex`, a robots block, or
a client-only render that serves crawlers a blank shell. These failures produce no error and
no visible symptom in the browser — traffic simply erodes over weeks while the app looks
perfectly healthy. Because the blast radius is the whole site and the failure is invisible,
technical SEO is checked deliberately, like a security control.

## Core Principles

- **Content must be in the HTML, server-rendered.** Crawlers index what the server returns.
  Client-only rendering risks an empty page being indexed; prefer SSR/SSG for public pages
  (see [rendering](07-rendering.md)).
- **One canonical URL per piece of content.** Duplicate URLs (trailing slash, query params,
  http/https) split ranking signals. Declare `<link rel="canonical">` to pick the winner.
- **Every indexable page has unique, accurate metadata.** A unique `<title>` and
  `<meta name="description">` per page; duplicated or missing titles waste ranking and clicks.
- **Don't block what you want ranked; do block what you don't.** `robots.txt` and `noindex`
  are load-bearing — one wrong line removes pages from search entirely.
- **Performance and mobile are ranking signals.** Core Web Vitals and mobile-friendliness feed
  ranking directly, so [performance](08-performance.md) and [responsive design](10-responsive-design.md) are SEO work.

## Best Practices

- Render meaningful HTML on the server with a unique `<title>` (~50-60 chars) and
  `<meta name="description">` (~150 chars) generated per route, not a single global default.
- Use one `<h1>` per page describing its main topic, with an ordered heading hierarchy and
  semantic HTML — the same structure that serves [accessibility](09-accessibility.md).
- Set `<link rel="canonical">` on every page to its preferred absolute URL, and 301-redirect
  duplicates (non-canonical host, trailing-slash variants) to it.
- Add **Open Graph** and Twitter Card tags (`og:title`, `og:description`, `og:image`) so shared
  links render rich previews instead of a bare URL.
- Provide **structured data** (JSON-LD, schema.org) for articles, products, breadcrumbs, and
  FAQs to earn rich results. Validate it; malformed markup earns nothing.
- Generate an accurate `sitemap.xml` (canonical URLs, `lastmod`) and a correct `robots.txt`;
  submit the sitemap in Search Console. Keep them in sync with real routes.
- Use descriptive, stable, lowercase-hyphenated URLs (`/blog/responsive-design`), and 301
  when a URL changes so ranking transfers instead of 404-ing.
- Give every meaningful image descriptive `alt` text and lazy-load below-the-fold images —
  good for accessibility, image search, and LCP alike.

## Examples

**Good Example** — per-page server metadata, canonical, and structured data

```tsx
// Metadata generated per route on the server, so crawlers get correct tags in the first byte.
export function generateMetadata({ post }: { post: Post }): Metadata {
  const url = `https://example.com/blog/${post.slug}`;
  return {
    title: `${post.title} — Example Blog`,   // unique per page
    description: post.excerpt,                // unique, accurate summary
    alternates: { canonical: url },          // one canonical URL, absolute
    openGraph: { title: post.title, description: post.excerpt, images: [post.cover], url },
  };
}

// JSON-LD lets search engines show a rich result for the article.
<script type="application/ld+json">
  {JSON.stringify({ "@context": "https://schema.org", "@type": "Article",
                    headline: post.title, datePublished: post.date })}
</script>
```

**Bad Example** — client-only render, global title, accidental noindex

```tsx
function BlogPost({ slug }: { slug: string }) {
  const [post, setPost] = useState<Post>();
  // Content fetched only on the client: the server returns an empty shell,
  // so crawlers may index a blank page with no title or body.
  useEffect(() => { fetchPost(slug).then(setPost); }, [slug]);
  return <article>{post?.body}</article>;
}
```

```html
<!-- Global, duplicated title across every page → no page ranks for its own topic. -->
<title>My App</title>
<!-- Left over from staging: silently removes the whole site from search. -->
<meta name="robots" content="noindex" />
```

## Common Mistakes

- Client-only rendering public pages, serving crawlers an empty HTML shell.
- A leftover `noindex` or a `robots.txt` `Disallow: /` deindexing the site.
- One global `<title>`/description reused across pages instead of unique per-page metadata.
- Missing or incorrect canonical tags, splitting ranking across duplicate URLs.
- Multiple or zero `<h1>` elements and non-semantic markup obscuring page structure.
- Changing URLs without 301 redirects, dropping accumulated ranking and creating 404s.
- No sitemap, or a sitemap listing stale/non-canonical URLs out of sync with real routes.

## Production Tips

- Monitor Google Search Console for coverage, indexing errors, and Core Web Vitals; it is the
  ground truth for what is actually indexed.
- Add a CI check that fails if any built page is missing a title, description, or canonical, or
  carries an unexpected `noindex`.
- Verify social previews with each platform's debugger before launch.
- After a migration or redesign, audit redirects and re-submit the sitemap immediately.

## AI Review Checklist

- Is content server-rendered so crawlers receive real HTML, not a blank shell?
- Does every indexable page have a unique `<title>`, description, and canonical URL?
- Is there exactly one `<h1>` and a correct heading hierarchy?
- Are Open Graph / Twitter tags and valid structured data present where applicable?
- Are `robots.txt` and `noindex` intentional, with no accidental site-wide block?
- Do changed URLs 301-redirect, and does `sitemap.xml` list current canonical routes?
- Are Core Web Vitals and mobile-friendliness in good standing?

## Related

- `knowledge/frontend/07-rendering.md`
- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/10-responsive-design.md`
- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/05-routing.md`
