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
when_to_use: ""
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

---

## Images

Optimize images for SEO.

Ensure:

- descriptive filenames;
- meaningful alternative text;
- responsive sizing;
- optimized formats.

Avoid embedding important text inside images.

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

---

## Sitemap

Generate a sitemap for public content.

Include:

- important pages;
- canonical URLs;
- update frequency where appropriate.

Keep the sitemap current.

---

## Internationalization

For multilingual applications:

- provide localized URLs;
- define language alternatives;
- maintain translated metadata.

Avoid mixing multiple languages on the same page.

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