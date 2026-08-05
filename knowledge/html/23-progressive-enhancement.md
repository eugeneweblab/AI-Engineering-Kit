---
id: html/23-progressive-enhancement
topic: html
slug: progressive-enhancement
title: "Progressive Enhancement"
type: doc
order: 23
status: ready
tags: [html, progressive-enhancement, method, action, toggle, querySelector, addEventListener, "display:none"]
related: [html/08-forms, html/04-links, html/21-best-practices, html/11-accessibility, html/18-performance]
when_to_use: "Read before building any interactive feature, to ensure the core experience works without JavaScript."
---
# Progressive Enhancement

## Purpose

This document defines progressive enhancement: build the core experience in HTML so it
works everywhere, then layer CSS and JavaScript on top for browsers and networks that can
use them. It is the strategy that makes a page resilient — usable when a script fails to
load, a browser is old, or JavaScript is disabled or still downloading.

It is the counterpart of graceful degradation: instead of starting rich and hoping it
survives, you start correct and add capability.

## Why It Matters

JavaScript is the most fragile part of the stack: it can fail to download on a flaky
network, error out on one browser, be blocked by an extension, or simply not have run yet
when the user taps a link. When the experience is built script-first, any of those turns
the page into a blank screen or a dead button. When it is built HTML-first, the same
failures degrade to a plain-but-working page — the form still submits, the link still
navigates. Progressive enhancement is what separates a site that is merely usually-fast
from one that is reliably usable, and it directly benefits SEO and accessibility because
crawlers and assistive tech see real HTML.

## Core Principles

- **Content and core actions live in HTML.** Text, links, and forms must work with zero
  CSS and zero JS. Everything else is enhancement.
- **Enhance, do not replace.** Layer behavior onto working markup; never make the baseline
  depend on the enhancement to function.
- **Feature-detect, do not assume.** Check for a capability before using it, and provide a
  working fallback when it is absent.
- **The network is unreliable.** Treat a failed or slow script as the expected case, not
  an edge case.
- **Forms and links are the backbone.** A real `<form action>` and real `<a href>` already
  work without JS; enhance them with `fetch`/history rather than reinventing them.

## Best Practices

- Build real, submittable forms with `action` and `method`; add client-side `fetch`
  handling as an enhancement that intercepts the working submit. See [forms](08-forms.md).
- Use real `<a href="…">` for navigation so links work, open in new tabs, and are
  crawlable; enhance to client-side routing on top of the real URL. See [links](04-links.md).
- Render meaningful content in the initial HTML (server-side or static) rather than an
  empty `<div id="root">` filled by JS — this is faster to first paint and works without
  script. See [performance](18-performance.md).
- Feature-detect APIs (`if ('IntersectionObserver' in window)`) and ship a fallback path
  instead of assuming support.
- Keep interactive controls as native elements (`<button>`, `<details>`, `<dialog>`) so
  they work before your script hydrates them.
- Never hide core content behind a JS-only interaction (e.g. an accordion whose panels are
  `display:none` until script runs) without a no-JS fallback.

## Examples

**Good Example** — works without JS, enhanced when available

```html
<!-- Real form: submits and reloads with a plain server response if JS never runs -->
<form action="/search" method="get">
  <label for="q">Search</label>
  <input id="q" name="q" type="search" />
  <button type="submit">Go</button>
</form>

<!-- Native disclosure works with zero JavaScript -->
<details>
  <summary>Shipping options</summary>
  <p>Standard, express, and pickup.</p>
</details>

<script>
  // Enhancement: intercept the working form only if fetch exists
  if ('fetch' in window) {
    document.querySelector('form').addEventListener('submit', enhanceSearch);
  }
</script>
```

**Bad Example** — nothing works until JS runs

```html
<!-- Empty shell: blank screen until the bundle loads and executes -->
<div id="root"></div>

<!-- Fake link: no href → not crawlable, no middle-click, dead if JS fails -->
<span class="link" onclick="router.go('/about')">About</span>

<!-- Content hidden by default, only revealed by script the user may never receive -->
<div class="panel" style="display:none">Critical info</div>
<button onclick="toggle()">Details</button>
```

## Common Mistakes

- Shipping an empty root element and rendering everything client-side with no SSR/fallback.
- `<span onclick>` or `<div role="button">` instead of real `<a>`/`<button>`.
- Hiding essential content behind JS-only toggles with no no-script path.
- Assuming an API exists instead of feature-detecting and providing a fallback.
- Reinventing form submission in JS while breaking the underlying `action`/`method`.
- Treating "JavaScript disabled" as the only failure mode — slow and failed loads matter more.

## Production Tips

- Test the page with JavaScript disabled and on a throttled network; the core task should
  still complete.
- Prefer server-side rendering or static generation for content pages so first paint and
  crawlers get real HTML.
- Monitor real-user JS error rates; a spike means many users are silently on the fallback
  path, which must therefore actually work.

## AI Review Checklist

- Does the core content and primary action work with JavaScript disabled?
- Are navigation and submission built on real `<a href>` and `<form action>`?
- Is meaningful HTML present on first load rather than an empty JS-filled shell?
- Are optional APIs feature-detected with a working fallback?
- Are interactive controls native elements before script enhances them?
- Is any essential content reachable without a JS-only interaction?

## Related

- `knowledge/html/08-forms.md`
- `knowledge/html/04-links.md`
- `knowledge/html/21-best-practices.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/18-performance.md`
