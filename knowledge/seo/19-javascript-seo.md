---
id: seo/19-javascript-seo
topic: seo
slug: javascript-seo
title: "JavaScript SEO"
type: doc
order: 19
status: ready
tags: [seo, javascript-seo, robots, getPost, robots.txt, onClick, href, useEffect]
related: [seo/04-rendering, seo/02-crawling, seo/20-headless-seo, seo/13-core-web-vitals]
when_to_use: "Read before shipping any client-rendered content, SPA route, or JS-injected metadata that must be indexed."
---
# JavaScript SEO

## Purpose

This document defines how to build JavaScript-driven pages so search engines can
discover, render, and index them reliably. It focuses on the gap between "works in my
browser" and "the crawler sees content" — the failure that sinks most SPAs.

JavaScript SEO is the discipline of making sure content produced by client-side code is
actually present when the engine evaluates the page. It sits on top of
[rendering](04-rendering.md) (the mechanics of turning JS into HTML) and applies those
mechanics to routing, links, metadata, and status codes.

## Why It Matters

Googlebot renders JavaScript, but not on your timeline and not for free. It fetches the
raw HTML first, then queues the page for rendering — the "second wave" — which can lag by
seconds to days and is skipped when the render budget is tight. Other crawlers (many
social scrapers, some search engines, LLM fetchers) execute little or no JavaScript at
all. If your content, links, or `<title>` exist only after client-side execution, a
whole class of consumers sees a blank shell. The bug is invisible in a browser and only
appears when you inspect the rendered HTML the way a crawler does.

## Core Principles

- **Ship content in the initial HTML response, not after hydration.** Server-side
  rendering (SSR) or static generation (SSG) guarantees the crawler sees content on the
  first fetch, with no dependency on the render queue. This is the single highest-leverage
  decision.
- **Never gate content behind user interaction.** Anything that only appears after a
  click, scroll, or `onload` fetch may never be rendered by the crawler.
- **Links must be real `<a href>` elements.** Crawlers discover URLs from `href`
  attributes. `onClick` navigation and `router.push` in a `<div>` are not links.
- **Do not block your own JS/CSS.** If `robots.txt` disallows the bundles needed to
  render, the engine renders a broken page. Rendered content depends on fetchable assets.
- **State HTTP truth on the server.** A client-side "404 page" that returns `200 OK`
  gets indexed as a real page. Status codes come from the server, not the router.

## Best Practices

- Prefer SSR or SSG for indexable routes; reserve pure client rendering for
  authenticated or non-indexable app views. See [headless SEO](20-headless-seo.md).
- Render the `<head>` on the server: `<title>`, description, canonical, `robots`, and
  Open Graph tags must be in the initial HTML, because social/LLM scrapers do not run JS.
- Set canonical and `robots` values server-side per route. Injecting `<meta name="robots"
  content="noindex">` with JavaScript is unreliable — the first-wave HTML already showed
  the page as indexable.
- For SPA routing, ensure each route has a unique, server-resolvable URL that returns the
  correct status (`200`, `301`, `404`, `410`) — not a single `index.html` for everything.
- Verify with the tool the engine uses: Search Console URL Inspection "View crawled
  page" and "Test live URL", plus the Rich Results Test — not just your browser's view.
- Keep the JS bundle lean; heavy hydration hurts [Core Web Vitals](13-core-web-vitals.md)
  and can push the page down the render queue.
- If you must client-render indexable content, add prerendering/dynamic rendering as a
  bridge, but treat it as a migration step toward SSR, not a permanent architecture.

## Examples

**Good Example** — server-rendered content, real links, server-set head

```jsx
// Next.js App Router: content and metadata resolved on the server.
// The crawler's first fetch already contains the article and its <head> tags.
export async function generateMetadata({ params }) {
  const post = await getPost(params.slug); // runs on the server
  if (!post) return {}; // route handler below returns 404
  return {
    title: post.title,
    description: post.excerpt,
    alternates: { canonical: `https://example.com/blog/${post.slug}` },
  };
}

export default async function Page({ params }) {
  const post = await getPost(params.slug);
  if (!post) notFound(); // sends a real 404 status, not a 200 shell
  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.body}</p>
      {/* real anchor: crawlable */}
      <a href={`/blog/${post.nextSlug}`}>Next post</a>
    </article>
  );
}
```

**Bad Example** — content and status invented on the client

```jsx
// Client-only: initial HTML is an empty <div id="root">.
// Crawlers that skip the render queue index a blank page.
function Post() {
  const [post, setPost] = useState(null);
  useEffect(() => {
    fetch(`/api/post/${slug}`).then(r => r.json()).then(setPost);
  }, []);

  if (!post) return <div>Loading…</div>; // this is what the first-wave crawler sees

  // "Not found" that still returns HTTP 200 → indexed as a real page (soft 404).
  if (post.error) return <NotFoundScreen />;

  // <div onClick> instead of <a href>: the crawler finds no link to follow.
  return <div onClick={() => router.push(`/blog/${post.next}`)}>Next</div>;
}
```

## Common Mistakes

- Assuming Googlebot runs JS "like Chrome," ignoring the render-queue delay and the many
  crawlers that run no JS.
- Content that only appears after a `fetch` in `useEffect`, invisible in the first-wave
  HTML.
- Navigation via `onClick`/`router.push` on non-anchor elements, so no `href` exists to
  crawl.
- Client-side 404 screens that return `200 OK` — soft 404s that pollute the index.
- Injecting canonical/`robots`/title with JavaScript, which social and LLM scrapers never
  execute.
- Blocking `/_next/`, `/static/`, or JS/CSS in `robots.txt`, breaking the engine's render.

## Production Tips

- Diff raw HTML (`curl` / "View source") against rendered HTML (URL Inspection). Content
  present only in the rendered view is at risk with non-rendering consumers.
- Monitor the "Crawled – currently not indexed" bucket after shipping client-rendered
  routes; it is the tell for render-queue starvation.
- Add a CI check that fetches key routes without JS and asserts the `<h1>`, canonical,
  and `<title>` are present in the response body.

## AI Review Checklist

- Is indexable content present in the server response, not injected after hydration?
- Are canonical, `robots`, `title`, and Open Graph tags set server-side per route?
- Are all navigations real `<a href>` links a non-JS crawler can follow?
- Do error routes return real `404`/`410` status, not a `200` client screen?
- Are JS and CSS assets crawlable (not blocked by `robots.txt`)?
- Was the rendered output verified with URL Inspection, not just a browser?

## Related

- `knowledge/seo/04-rendering.md`
- `knowledge/seo/02-crawling.md`
- `knowledge/seo/20-headless-seo.md`
- `knowledge/seo/13-core-web-vitals.md`
