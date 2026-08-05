---
id: divi/13-seo
topic: divi
slug: seo
title: "Divi SEO"
type: doc
order: 13
status: ready
tags: [divi, seo]
related: [divi/10-performance, divi/12-accessibility, divi/02-theme-builder, divi/07-dynamic-content, divi/25-production]
when_to_use: "Read before launching a Divi site or building templates that need to rank and render correctly in search."
---
# Divi SEO

## Purpose

This document defines how to make a **Divi** site technically sound for search engines:
correct document structure, crawlable content, fast rendering, and accurate metadata. It
is written so an agent can build or review Divi templates without introducing the SEO
regressions the builder makes easy — heading soup, `<div>`-wrapped content, render-blocking
bloat, and metadata set in two conflicting places.

SEO here means **technical and on-page** SEO, not content strategy. Divi does not manage
titles, meta descriptions, canonicals, or schema — a dedicated plugin (Rank Math, Yoast,
or SEOPress) does. Divi's job is to emit clean, fast, semantic HTML that the plugin and the
crawler can work with.

## Why It Matters

Divi's flexibility is exactly what hurts SEO when it is unmanaged. A page assembled from
nested sections/rows/columns can wrap the real content in a dozen `<div>`s, bury the `<h1>`,
or duplicate heading levels — all of which weaken the signals a crawler reads. Divi's default
asset loading is heavy, and Core Web Vitals (LCP, INP, CLS) are ranking inputs, so a slow
Divi page loses positions independent of its content quality. And because Divi and an SEO
plugin can both try to output a `<title>` or meta tags, misconfiguration produces duplicate
or empty tags that quietly suppress rankings while the page looks fine.

## Core Principles

- **One SEO source of truth.** Titles, descriptions, canonicals, Open Graph, and schema come
  from one SEO plugin. Do not also hand-code them in Divi's Integration/Code modules.
- **Semantic, crawlable HTML.** Content is real headings, paragraphs, and links — not text
  baked into background images or injected only by JavaScript after load.
- **Correct heading hierarchy.** Exactly one `<h1>` describing the page; `<h2>`–`<h4>` nested
  in order. Heading level communicates structure to crawlers, not just size.
- **Speed is a ranking factor.** Core Web Vitals must pass on mobile; Divi performance
  features are mandatory, not optional. See [performance](10-performance.md).
- **Every canonical URL resolves once.** No duplicate content across trailing-slash, `www`,
  or HTTP/HTTPS variants; one 200 response per canonical.

## Best Practices

- Install one SEO plugin and let it own the `<title>` and meta tags. Confirm the Divi Theme
  Options and any Code module are **not** also emitting them (duplicate `<title>` is common).
- Set the page `<h1>` once — normally the post title in a Theme Builder template — and use
  each module's **Heading Level** setting to keep the outline ordered. Style size in CSS.
- Enable Divi's performance suite: dynamic CSS, critical CSS, deferred/combined assets, and
  lazy-loaded images. Confirm above-the-fold images are **not** lazy-loaded (hurts LCP).
- Add descriptive **Alt Text** to images — it feeds image search and accessibility at once.
- Make every link a real `<a href>` with descriptive text. Avoid "click here" and JS-only
  navigation that crawlers may not follow.
- For dynamic templates (blog, products), verify each generated page has a unique title and
  description via the SEO plugin's template variables, using [dynamic content](07-dynamic-content.md).
- Add structured data (Article, Product, BreadcrumbList) through the SEO plugin or a Code
  module with valid JSON-LD — never invalid or duplicated schema.
- Keep a single canonical host and generate an XML sitemap; submit it in Search Console.

## Examples

**Good Example** — one owner for metadata, valid JSON-LD once

```php
// Make the SEO plugin the single source of truth for metadata.
// Modern Divi exposes no removable wp_head "SEO" action: its ePanel SEO tab writes
// meta inline, and <title> comes from WordPress title-tag support — so you disable
// Divi's output by configuration, not remove_action().
//   1. Divi > Theme Options > SEO: leave the Homepage/Single-post SEO fields blank
//      (or disable the tab) so Divi emits no title/description/keywords.
//   2. Ensure the theme declares title-tag support so the plugin can filter <title>:
add_theme_support( 'title-tag' ); // functions.php (child theme)
// Rank Math/Yoast then own <title>, meta description, canonical, OG, and schema
// via the document_title / wp_head filters — no duplicate or empty tags.
```

```html
<!-- Structured data emitted once, valid, matching visible content. -->
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Article","headline":"Real page heading"}
</script>
```

**Bad Example** — metadata set twice, heading misused

```html
<!-- Divi Code module ALSO outputs a title while the SEO plugin does too:
     two <title> tags → search engines pick one unpredictably. -->
<title>My Page | Site</title>

<!-- Chosen for its font size, not structure: two H1s, no H2 → broken outline. -->
<h1 class="hero">Big headline</h1>
<h1 class="subhead">Also big</h1>
```

## Common Mistakes

- Divi Theme Options and an SEO plugin both emitting `<title>`/meta, creating duplicates.
- Multiple `<h1>`s or heading levels chosen for size, producing an incoherent outline.
- Lazy-loading the LCP/hero image, delaying the largest paint and failing Core Web Vitals.
- Content that only exists after client-side JS runs, leaving crawlers with an empty page.
- Text rendered inside background images, so keywords are invisible to search engines.
- Duplicate content served on both `example.com` and `www.example.com` with no canonical.
- Invalid or copy-pasted JSON-LD that does not match the visible page content.

## Production Tips

- Validate every launch with Search Console URL Inspection (rendered HTML), the Rich Results
  Test (schema), and PageSpeed Insights (field + lab CWV) — not just a desktop Lighthouse run.
- Keep redirects clean: exactly one 301 hop from old URLs; audit for chains after migrations.
- Set the SEO defaults in Theme Builder templates so new posts inherit correct titles,
  canonicals, and OG tags instead of shipping blank.

## AI Review Checklist

- Is metadata owned by exactly one SEO plugin, with no duplicate `<title>`/meta from Divi?
- Is there one `<h1>` and an ordered, unbroken heading hierarchy?
- Are Divi performance features on and Core Web Vitals passing on mobile?
- Is the hero/LCP image excluded from lazy loading?
- Is primary content in real HTML, present without client-side JS?
- Do dynamic templates produce unique titles and descriptions per page?
- Is there a single canonical host, an XML sitemap, and valid structured data?

## Related

- `knowledge/divi/10-performance.md`
- `knowledge/divi/12-accessibility.md`
- `knowledge/divi/02-theme-builder.md`
- `knowledge/divi/07-dynamic-content.md`
- `knowledge/divi/25-production.md`
