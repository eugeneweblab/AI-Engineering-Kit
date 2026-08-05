---
id: html/98-production-checklist
topic: html
slug: production-checklist
title: "HTML Production Checklist"
type: checklist
order: 98
status: ready
tags: [html, production-checklist, html-validate, autocomplete, defer]
related: [html/30-engineering-principles, html/11-accessibility, html/18-performance, html/12-seo, html/19-security]
when_to_use: "Read before shipping any HTML page or template to production, as the final gate on markup quality."
---
# HTML Production Checklist

## Purpose

This is the pre-ship gate for HTML. Every item is a verifiable yes/no an agent or
reviewer can check against the actual markup. If any box is unchecked, the page is not
ready. Do not treat this as aspirational — treat it as blocking.

## Why It Matters

Most HTML defects — missing `alt`, broken heading order, unlabeled inputs, absent
metadata — never surface in a casual look at the rendered page. They surface as failed
audits, lost search ranking, excluded users, and layout shift on real networks. A
concrete checklist converts "looks done" into "is done" and catches the silent failures
that visual review misses.

## Document Foundation

**Rules:** [Document Structure](01-document-structure.md) · [Metadata](10-metadata.md)

- [ ] `<!DOCTYPE html>` is the first line of the document.
- [ ] `<html>` has a valid `lang` attribute (e.g. `lang="en"`).
- [ ] `<meta charset="utf-8">` is the first element in `<head>`.
- [ ] `<meta name="viewport" content="width=device-width, initial-scale=1">` is present.
- [ ] Every page has exactly one `<title>` that is unique and descriptive.
- [ ] The markup validates (W3C Nu or `html-validate`) with no errors.

## Structure & Semantics

**Rules:** [Semantic HTML](02-semantic-html.md)

- [ ] Exactly one `<main>` element wraps the primary content.
- [ ] Landmark elements (`<header>`, `<nav>`, `<main>`, `<footer>`) are used, not `<div>` substitutes.
- [ ] Heading levels are logical and never skip a level.
- [ ] All `id` attributes are unique within the document.
- [ ] Lists use `<ul>`/`<ol>`/`<li>`; tabular data uses `<table>` with `<th scope>`.

## Accessibility

**Rules:** [Accessibility](11-accessibility.md)

- [ ] Every `<img>` has an `alt` attribute (empty for decorative images).
- [ ] Every form control has an associated `<label>` (via `for`/`id` or wrapping).
- [ ] All interactive controls are keyboard-reachable and operable in a logical tab order.
- [ ] Focus is visible on every interactive element (no `outline: none` without a replacement).
- [ ] ARIA is used only to fill gaps native HTML cannot, and every `role` is valid.
- [ ] Color is never the sole means of conveying information.

## Forms

**Rules:** [Forms](08-forms.md)

- [ ] Inputs use the correct `type` (`email`, `tel`, `url`, `number`, etc.).
- [ ] `autocomplete` attributes are set on personal-data fields.
- [ ] Required fields use the `required` attribute, not JS-only validation.
- [ ] Submit buttons are `<button type="submit">`, and the form works without JavaScript.

## Metadata & SEO

**Rules:** [Metadata](10-metadata.md) · [SEO](12-seo.md)

- [ ] A `<meta name="description">` is present and unique per page.
- [ ] Open Graph / Twitter Card tags are set for shareable pages.
- [ ] A canonical `<link rel="canonical">` is present where duplicate URLs can exist.
- [ ] Structured data (JSON-LD) is included where relevant and validates.

## Performance

**Rules:** [Performance](18-performance.md) · [Browser Rendering](20-browser-rendering.md)

- [ ] Images specify `width` and `height` (or `aspect-ratio`) to prevent layout shift.
- [ ] Below-the-fold images use `loading="lazy"`; hero images do not.
- [ ] Render-blocking scripts use `defer` or `async` as appropriate.
- [ ] Responsive images use `srcset`/`sizes` or `<picture>` where warranted.
- [ ] Fonts are preloaded and use `font-display: swap` to avoid invisible text.

## Security

**Rules:** [Security](19-security.md)

- [ ] External `target="_blank"` links include `rel="noopener"`.
- [ ] No untrusted content is injected as raw HTML without sanitization.
- [ ] A Content-Security-Policy is set; no inline event handlers rely on unsafe-inline.
- [ ] Sensitive form pages are served over HTTPS and post to HTTPS endpoints.

## Cross-Environment

**Rules:** [Progressive Enhancement](23-progressive-enhancement.md) · [Microdata](26-microdata.md)

- [ ] Core content and navigation work with JavaScript disabled.
- [ ] The page is legible and operable with CSS disabled.
- [ ] The layout is verified on mobile widths, not only desktop.

## AI Review Checklist

- [ ] Would the W3C validator and an `axe` scan both pass with zero errors?
- [ ] Is every image, form control, and interactive element accessible by keyboard and screen reader?
- [ ] Are all required metadata, SEO, and social tags present and unique?
- [ ] Do images reserve space to prevent cumulative layout shift?
- [ ] Does the page degrade gracefully with JS and CSS disabled?

## Related

- `knowledge/html/30-engineering-principles.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/18-performance.md`
- `knowledge/html/12-seo.md`
- `knowledge/html/19-security.md`
