---
id: divi/18-headless
topic: divi
slug: headless
title: "Divi Headless"
type: doc
order: 18
status: ready
tags: [divi, headless, getPage, post_content, register_rest_field, save_post, dangerouslySetInnerHTML, decoupling, etc, site]
related: [divi/17-rest-api, divi/01-architecture, divi/10-performance, divi/15-custom-fields, divi/13-seo, security/11-xss]
when_to_use: "Read before decoupling a Divi site's front-end (Next.js, Nuxt, etc.) from WordPress."
---
# Divi Headless

## Purpose

This document defines how to build a **headless (decoupled) front-end** on top of a
Divi-powered WordPress site: a separate application (Next.js, Nuxt, Astro) that fetches
content over the [REST API](17-rest-api.md) or WPGraphQL and renders it, while WordPress
remains the editing backend. It tells an agent how to get *usable* content out of Divi —
whose content model is shortcode/JSON, not clean HTML — without shipping broken markup.

## Why It Matters

Divi is fundamentally a **server-side renderer**: page content is stored as Divi
shortcodes (Divi 4) or a JSON module tree (Divi 5) that only becomes HTML when Divi's PHP
runs against them. A naive headless build reads raw `post_content`, gets literal
`[et_pb_section]...[/et_pb_section]` text, and dumps it on the page. Even when you request
rendered HTML, that HTML depends on Divi's stylesheet and dynamic module CSS — omit them
and the page is unstyled and often unusable. Getting headless Divi right is mostly about
respecting where the rendering boundary is.

## Core Principles

- **Divi is the editor, not the runtime.** In a headless setup WordPress + Divi produce
  content; your front-end owns rendering, routing, and performance. Do not try to run the
  Visual Builder against a decoupled front-end — it requires the Divi theme active.
- **Never consume raw shortcodes on the client.** Raw `post_content` is Divi source, not
  output. Consume `content.rendered` (REST) or the equivalent GraphQL field, which runs
  shortcodes through Divi server-side.
- **Rendered HTML carries a styling contract.** Divi's rendered markup needs Divi's core
  CSS plus the page's dynamic module CSS. If you take the HTML you must take the styles.
- **Prefer structured data over rendered blobs for anything dynamic.** For lists, prices,
  or [custom fields](15-custom-fields.md), expose typed REST/GraphQL fields; reserve
  `content.rendered` for genuine long-form page bodies.

## Best Practices

- Enable Divi's **"Enable Static CSS File Generation"** and serve those static CSS files
  from your front-end for the rendered content, so styling matches the WordPress render.
- Register REST fields for the data your front-end needs (`register_rest_field`) instead
  of scraping rendered HTML for values that should be structured.
- Rewrite internal links and asset URLs in rendered HTML to your front-end domain before
  display, or all navigation dead-ends on the WordPress origin.
- Keep the WordPress origin private/behind auth for editing, and expose only a read API
  (cache it at the edge). Consider WPGraphQL for typed queries over the REST envelope.
- Handle [SEO](13-seo.md) yourself: Divi/Yoast meta must be re-emitted by the front-end;
  Divi does not render your `<head>` in a headless world.
- For new builds, prefer **Divi 5's JSON content model** — it is far more portable than
  Divi 4 shortcodes and easier to map to components.
- **Rendered content goes into an HTML sink, so name the trust boundary.** Passing
  `content.rendered` to `dangerouslySetInnerHTML` is the standard headless pattern and it
  is also the sink [XSS](../security/11-xss.md) warns about. WordPress filters markup only
  for users who lack `unfiltered_html` — administrators and editors usually have it — so
  this trusts everyone who can edit a page, plus every plugin that touches
  `the_content`. That is often acceptable for a site whose editors you employ. Decide it
  deliberately: if it is not acceptable, sanitize server-side with an allowlist wide
  enough for Divi's markup, and never widen the allowlist to make a layout work.

## Examples

**Good Example** — consume rendered content, ship the styling contract

```tsx
// Next.js: fetch the RENDERED body (Divi shortcodes already expanded server-side)
async function getPage(slug: string) {
  const [post] = await fetch(
    `${WP}/wp-json/wp/v2/pages?slug=${slug}&_fields=title,content`
  ).then((r) => r.json());
  return post;
}

export default async function Page({ params }) {
  const post = await getPage(params.slug);
  return (
    <>
      {/* Divi's static CSS is loaded globally in layout.tsx so this HTML is styled.
          `content.rendered` is trusted markup here — see the trust boundary above;
          sanitize server-side instead if your editors are not trusted. */}
      <article dangerouslySetInnerHTML={{ __html: post.content.rendered }} />
    </>
  );
}
```

**Bad Example** — raw shortcodes and no styles

```tsx
async function getPage(slug: string) {
  // WRONG: raw=1 / post_content is Divi SOURCE, not HTML
  const [post] = await fetch(`${WP}/wp-json/wp/v2/pages?slug=${slug}`)
    .then((r) => r.json());
  return post.content.raw; // "[et_pb_section]...[/et_pb_section]" as literal text
}

// Renders "[et_pb_section fb_built=1 ...]" onto the page, unstyled and broken,
// because Divi's PHP never ran and Divi's CSS was never loaded.
```

## Common Mistakes

- Reading `content.raw` / `post_content` and rendering literal shortcode text.
- Taking `content.rendered` HTML but not loading Divi's core + static module CSS.
- Leaving internal links pointing at the WordPress origin instead of the front-end.
- Expecting the Visual Builder to work against the decoupled site — it needs the theme.
- Scraping values out of rendered HTML instead of exposing them as structured API fields.
- Forgetting SEO meta, canonical, and Open Graph tags that Divi rendered on the monolith.

## Production Tips

- Cache the read API at the edge and invalidate on WordPress `save_post` via a webhook,
  so editors see updates without exposing an uncached origin.
- Version the styling contract: when Divi updates change rendered markup/CSS, re-pull the
  static CSS as part of your deploy, or the front-end drifts from the backend render.
- Keep a preview path that authenticates to the draft REST endpoint for editor review.

## AI Review Checklist

- Is the front-end consuming `content.rendered` (or GraphQL rendered HTML), never raw
  shortcodes?
- Are Divi's core and static module CSS files loaded wherever rendered content appears?
- Are internal links and asset URLs rewritten to the front-end domain?
- Is dynamic/structured data exposed as typed REST/GraphQL fields rather than scraped HTML?
- Are SEO meta tags re-emitted by the front-end?
- For new builds, is the portable Divi 5 JSON model preferred over Divi 4 shortcodes?

## Related

- `knowledge/divi/17-rest-api.md`
- `knowledge/divi/01-architecture.md`
- `knowledge/divi/10-performance.md`
- `knowledge/divi/15-custom-fields.md`
- `knowledge/divi/13-seo.md`
