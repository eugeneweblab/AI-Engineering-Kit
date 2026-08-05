---
id: seo/04-rendering
topic: seo
slug: rendering
title: "SEO Rendering"
type: doc
order: 4
status: ready
tags: [seo, rendering]
related: [seo/19-javascript-seo, seo/03-indexing, seo/13-core-web-vitals, seo/20-headless-seo, seo/02-crawling]
when_to_use: "Read before building or reviewing any page whose content is produced by client-side JavaScript."
---
# SEO Rendering

## Purpose

This document defines how a fetched page becomes the HTML a search engine actually indexes
— the stage between [crawling](02-crawling.md) and [indexing](03-indexing.md) that trips up
JavaScript-heavy sites. It covers server-side rendering (SSR), static generation (SSG),
client-side rendering (CSR), hydration, and the engine's two-wave rendering process, so an
agent can guarantee the crawler sees real content, not an empty shell.

Rendering answers "what HTML does the engine end up with after JavaScript runs?". For a
server-rendered page the answer is "the same HTML you sent." For a client-rendered page it
is "whatever the engine's headless browser produces later — if it runs your JS at all."
That *if* is the entire problem this doc exists to prevent.

## Why It Matters

Modern crawlers can execute JavaScript, but rendering is deferred, budgeted, and not
guaranteed. Google renders in a **second wave** that can lag the initial crawl by seconds
to days, other engines and most social/link-preview bots do not run JS at all, and a
single script error can leave the rendered DOM empty. A client-only SPA can therefore
appear as a blank `<div id="root"></div>` to the index — perfect for users, invisible to
search. This is the most common and most damaging modern SEO failure.

## Core Principles

- **Primary content and metadata must exist in the initial HTML response.** If the
  `<title>`, main copy, and links appear only after client JS runs, assume some bots
  never see them.
- **Rendering is a two-wave process for Google, single-wave (no JS) for many others.**
  Design for the worst consumer: content in the server response.
- **Hydration must not change what content exists, only make it interactive.** The
  server HTML and the post-hydration DOM must match; mismatches cause errors and flicker.
- **Do not block the resources needed to render.** CSS and JS blocked in
  [robots.txt](02-crawling.md) mean the engine renders a broken page.
- **Never gate content on user interaction.** Tabs, "load more," and modals whose
  content is fetched on click are invisible unless the content is in the DOM up front.

## Best Practices

- Prefer **SSR** or **SSG** for indexable content. Serve fully-formed HTML; hydrate for
  interactivity. Frameworks like Next.js, Nuxt, SvelteKit, and Astro do this by default.
- If a page must be client-rendered, add **prerendering** (dynamic rendering / a
  prerender service) so bots receive a static HTML snapshot — but treat it as a
  fallback, not a first choice, since it is another system to keep in sync.
- Set per-page `<title>`, meta description, and canonical *on the server* (see
  [Metadata](05-metadata.md)); do not rely on client JS to inject `<head>` tags.
- Include real content in the server HTML for tabs/accordions; hide with CSS, not by
  omitting it from the DOM.
- Verify with **URL Inspection → View Crawled/Rendered HTML** in Search Console — trust
  the engine's rendered output, not `view-source`.
- Keep rendering fast; slow JS hurts [Core Web Vitals](13-core-web-vitals.md) and can
  cause the renderer to time out.

## Examples

**Good Example** — server-rendered content, hydrate for interactivity

```jsx
// Next.js App Router: runs on the server, so the crawler receives real HTML.
export default async function ProductPage({ params }) {
  const product = await getProduct(params.id); // fetched on the server
  return (
    <main>
      <h1>{product.name}</h1>          {/* present in the initial HTML response */}
      <p>{product.description}</p>
      <AddToCartButton id={product.id} /> {/* only THIS hydrates for interactivity */}
    </main>
  );
}
```

**Bad Example** — content exists only after client fetch

```jsx
// Client-only: the server sends <div id="root"></div>. The crawler may index
// the empty shell if it does not run the JS, or runs it before the fetch resolves.
function ProductPage({ id }) {
  const [product, setProduct] = useState(null);
  useEffect(() => {
    fetch(`/api/products/${id}`).then(r => r.json()).then(setProduct); // runs in browser only
  }, [id]);
  if (!product) return <Spinner />; // WHY this is wrong: this spinner, not the
  return <h1>{product.name}</h1>;    // product, is what a non-JS bot indexes.
}
```

## Common Mistakes

- Shipping a CSR SPA and assuming Google (let alone Bing, or social preview bots) will
  reliably run the JavaScript and see the content.
- Injecting `<title>`/meta/canonical from client code, so link-preview and non-JS bots
  get defaults or nothing.
- Blocking `/_next/`, `/static/`, or `.js`/`.css` in robots.txt, breaking rendering.
- Hydration mismatches from time-, locale-, or random-dependent server output.
- Loading main content only on scroll or click, leaving it out of the crawlable DOM.
- Assuming social scrapers (Slack, WhatsApp, LinkedIn, Facebook) execute JS — they do
  not; they read the raw HTML `<head>`.

## Production Tips

- Add a CI check that fetches key routes with a plain HTTP client (no JS) and asserts the
  `<h1>`, `<title>`, and canonical are present in the raw HTML.
- Monitor Search Console's "Crawled – currently not indexed" and rendered-HTML view for
  pages that render empty.
- For headless/decoupled setups, confirm the delivery layer server-renders SEO-critical
  routes (see [Headless SEO](20-headless-seo.md)).

## AI Review Checklist

- Do the `<h1>`, primary content, and links appear in the raw server HTML (no JS)?
- Are `<title>`, meta description, and canonical set server-side, not injected by client JS?
- Are CSS and JS needed for rendering *allowed* in robots.txt?
- Is tab/accordion/modal content in the DOM, hidden with CSS, rather than fetched on click?
- Does hydration preserve content (no server/client DOM mismatch)?
- Has the rendered output been verified with Search Console's URL Inspection?

## Related

- `knowledge/seo/19-javascript-seo.md`
- `knowledge/seo/03-indexing.md`
- `knowledge/seo/13-core-web-vitals.md`
- `knowledge/seo/20-headless-seo.md`
- `knowledge/seo/02-crawling.md`
