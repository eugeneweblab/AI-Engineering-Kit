---
id: seo/readme
topic: seo
slug: readme
title: "SEO Engineering Standards"
type: index
order: -1
status: ready
tags: [seo, readme, noindex, Disallow]
related: []
when_to_use: "Read first when starting SEO work, to see how this section's docs fit together and which technical concern applies."
---
# SEO Engineering Standards

## Purpose

This section defines the engineering side of search visibility: making pages discoverable,
crawlable, indexable, and renderable, and describing their content in the structured formats
search engines and social platforms consume.

The scope is deliberately technical. Content strategy and keyword research are not engineering
problems; a JavaScript-rendered page that returns an empty document to a crawler is. Most
serious SEO failures are engineering failures — a `noindex` shipped to production, a
canonical pointing at staging, a migration that dropped every redirect.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Fundamentals: crawling, indexing, and rendering
- Page-level signals: metadata, canonicalization, structured data
- Social sharing: Open Graph and Twitter Cards
- Site-level infrastructure: sitemaps, robots.txt, pagination, links
- JavaScript and headless SEO
- Performance and Core Web Vitals as ranking inputs
- International and local SEO
- Images and content quality
- Analytics, Search Console, audits, and monitoring

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. [Overview](00-overview.md)
- 01. [SEO Fundamentals](01-seo-fundamentals.md)
- 02. [Crawling](02-crawling.md)
- 03. [Indexing](03-indexing.md)
- 04. [Rendering](04-rendering.md)
- 30. [Engineering Principles](30-engineering-principles.md)

## Page-Level Signals

- 05. [Metadata](05-metadata.md)
- 06. [Canonicalization](06-canonicalization.md)
- 09. [Structured Data](09-structured-data.md)
- 10. [Open Graph](10-open-graph.md)
- 11. [Twitter Cards](11-twitter-cards.md)

## Site Infrastructure

- 07. [Sitemaps](07-sitemaps.md)
- 08. [Robots.txt](08-robots-txt.md)
- 17. [Links](17-links.md)
- 18. [Pagination](18-pagination.md)

## Rendering and Delivery

- 19. [JavaScript SEO](19-javascript-seo.md)
- 20. [Headless SEO](20-headless-seo.md)
- 12. [Performance](12-performance.md)
- 13. [Core Web Vitals](13-core-web-vitals.md)
- 16. [Images](16-images.md)

## Reach

- 14. [International SEO](14-international-seo.md)
- 15. [Local SEO](15-local-seo.md)
- 25. [Content Quality](25-content-quality.md)

## Measurement

- 21. [Analytics](21-analytics.md)
- 22. [Search Console](22-search-console.md)
- 23. [Audits](23-audits.md)
- 24. [Monitoring](24-monitoring.md)

## Applied Guidance

- 26. [Best Practices](26-best-practices.md)
- 27. [Production Checks](27-production-checks.md)
- 28. [Real-World Patterns](28-real-world-patterns.md)
- 29. [SEO Review](29-seo-review.md)

## Verification

- 98. [Production Checklist](98-production-checklist.md)
- 99. [AI Review Checklist](99-ai-review-checklist.md)
- 100. [Common Antipatterns](100-common-antipatterns.md)

---

## Engineering Principles

Every page should satisfy the following principles:

- Serve meaningful HTML in the initial response; content that exists only after hydration may
  never be indexed.
- One canonical URL per piece of content, declared explicitly and pointing at the production
  host.
- Every page has a unique, descriptive `<title>` and meta description — generated, not
  duplicated.
- `noindex` and `Disallow` are deployment-critical: verify what production actually serves,
  not what the code intends.
- Preserve URLs across migrations, or ship 301s for every one that changes.
- Structured data must describe what is actually on the page, and validate against the schema.
- Semantic HTML and correct heading hierarchy serve search engines and assistive technology
  with the same markup.
- Core Web Vitals are a ranking input, so performance work is SEO work.
- Give every image a descriptive alt and an appropriate file size.
- Monitor after launch: Search Console coverage errors are the earliest signal that something
  regressed.

---

## Intended Audience

These standards are intended for:

- Frontend and Fullstack Engineers
- Technical SEO Specialists
- Content and Marketing Engineers
- Tech Leads
- AI Coding Assistants
- Code Reviewers

---

## Summary

Technical SEO is about making content reachable and describable: real HTML in the first
response, one canonical URL, accurate metadata and structured data, preserved URLs across
changes, and monitoring that catches regressions before rankings do.
