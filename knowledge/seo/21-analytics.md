---
id: seo/21-analytics
topic: seo
slug: analytics
title: "Analytics"
type: doc
order: 21
status: ready
tags: [seo, analytics, Disallow, requestIdleCallback, robots.txt, remove, getElementById, addEventListener]
related: [seo/22-search-console, seo/24-monitoring, seo/12-performance, seo/13-core-web-vitals]
when_to_use: "Read before adding, changing, or reviewing analytics/tag code that could affect indexing, consent, or page performance."
---
# Analytics

## Purpose

This document defines how to instrument a site with analytics and tags without harming
SEO. The focus is the collision between measurement and search: analytics scripts that
slow the page, tag managers that inject unwanted content, tracking parameters that create
duplicate URLs, and consent tooling that hides content from crawlers.

Analytics here means the client- and server-side code that measures traffic and behavior
(GA4, server events, tag managers). The goal is accurate measurement that leaves the
page's crawlability, indexability, and performance untouched.

## Why It Matters

Analytics is additive code that runs on every page, so its mistakes scale to the whole
site. A heavy tag manager pushes [Core Web Vitals](13-core-web-vitals.md) past the
thresholds and drags rankings down. UTM parameters generate thousands of duplicate URLs
that split signals and waste crawl budget. A consent banner rendered as a blocking
overlay can hide content from the crawler or trip layout-shift penalties. And measurement
itself can lie: bot traffic and self-referrals corrupt the numbers you use to make SEO
decisions. None of this shows up as an error — it shows up as slow pages, messy index
coverage, and untrustworthy dashboards.

## Core Principles

- **Measurement must not change what the crawler sees.** Analytics is observational.
  Content, links, and metadata must be identical with tracking on or off.
- **Load third-party scripts asynchronously and off the critical path.** A synchronous or
  render-blocking tag delays first paint for every user and every crawler.
- **Tracking parameters create URLs — canonicalize them away.** `?utm_source=…`,
  `?gclid=…`, `?fbclid=…` are the same content as the clean URL. The canonical must point
  to the parameter-free version.
- **Consent gating is for tracking, not for content.** Blocking analytics until consent is
  correct; blocking article text or `<h1>` behind a consent wall is cloaking-adjacent and
  hurts indexing.
- **Instrument server-side where you can.** Server events and log analysis do not depend
  on JS execution, are not blocked by ad blockers, and cost the page nothing.

## Best Practices

- Load GA4 / tag manager with `async` and, where possible, defer initialization until
  after the page is interactive. Budget third-party JS explicitly.
- Set a self-referencing canonical so UTM/click-id variants collapse to the clean URL;
  see [canonicalization](06-canonicalization.md). Do not `Disallow` these params in
  `robots.txt` — that blocks crawling but not indexing of the dirty URL.
- Keep the consent banner as a non-blocking overlay that does not cause layout shift
  (reserve its space) and never hides primary content from the initial HTML.
- Exclude known bots and internal traffic from analytics views so SEO numbers reflect
  real users; enable GA4 bot filtering.
- Prefer first-party, server-side tagging (e.g., server-side GTM) to reduce client JS
  weight and improve data completeness.
- Use `<link rel="preconnect">` sparingly for analytics origins only if they are on the
  critical path; otherwise avoid adding connection overhead.
- Track SEO-relevant events deliberately: organic landing pages, Core Web Vitals field
  data (via the web-vitals library), and internal search — these feed real decisions.

## Examples

**Good Example** — async load, deferred init, clean canonical

```html
<head>
  <!-- Content and canonical are independent of analytics. UTM variants
       collapse to the clean URL so tracked links don't fragment the index. -->
  <link rel="canonical" href="https://example.com/pricing" />

  <!-- async: does not block parsing or first paint -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXX"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){ dataLayer.push(arguments); }
    // Defer non-essential init until the page is idle, off the critical path.
    window.addEventListener("load", () => {
      requestIdleCallback(() => { gtag("js", new Date()); gtag("config", "G-XXXX"); });
    });
  </script>
</head>
```

**Bad Example** — render-blocking tag, content hidden behind consent

```html
<head>
  <!-- Synchronous third-party script: blocks the parser, delays paint
       for every user and crawler, hurting LCP across the whole site. -->
  <script src="https://cdn.tracker.example/heavy-tag.js"></script>
</head>
<body>
  <!-- Primary content withheld until consent → crawler (which gives no consent)
       sees an empty page; also a large layout shift when it appears. -->
  <div id="app" hidden data-requires-consent>...article...</div>
  <script>if (!hasConsent()) document.getElementById("app").remove();</script>
</body>
```

## Common Mistakes

- Adding a synchronous or heavy tag manager that regresses LCP/INP site-wide.
- Letting UTM/`gclid`/`fbclid` parameters create indexable duplicate URLs with no
  canonical.
- `Disallow`-ing tracking params in `robots.txt`, which blocks crawling but leaves the
  dirty URL indexable with no snippet.
- Consent walls that hide article content from crawlers, or banners that cause layout
  shift.
- Trusting analytics numbers that include bots and internal traffic when making SEO
  calls.
- Injecting content or links via tag manager, so what ranks depends on a marketing tool
  outside code review.

## Production Tips

- Measure the performance cost of every tag in a Lighthouse/CrUX budget in CI; block PRs
  that add third-party JS beyond the budget.
- Collect Core Web Vitals *field* data with the `web-vitals` library and reconcile it
  against [Search Console](22-search-console.md) — lab scores alone mislead.
- Audit indexed URLs quarterly for tracking-parameter variants; add canonicals or
  parameter handling where they leaked in.

## AI Review Checklist

- Are analytics/tag scripts loaded `async`/deferred and within a performance budget?
- Is page content, and its crawlability, identical with tracking enabled or disabled?
- Do UTM/click-id parameter URLs canonicalize to the clean URL?
- Does the consent banner avoid hiding primary content and avoid layout shift?
- Are bots and internal traffic filtered out of SEO analytics views?
- Is any content or link injected by the tag manager (outside code review)? If so, move
  it into the app.

## Related

- `knowledge/seo/22-search-console.md`
- `knowledge/seo/24-monitoring.md`
- `knowledge/seo/12-performance.md`
- `knowledge/seo/13-core-web-vitals.md`
