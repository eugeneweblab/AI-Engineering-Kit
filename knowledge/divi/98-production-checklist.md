---
id: divi/98-production-checklist
topic: divi
slug: production-checklist
title: "Divi Production Checklist"
type: doc
order: 98
status: ready
tags: [divi, production-checklist]
related: [divi/25-production, divi/10-performance, divi/22-deployment, divi/19-security, divi/13-seo]
when_to_use: "Read and run through before launching or handing off any Divi site, to confirm every non-negotiable is in place."
---
# Divi Production Checklist

## Purpose

This is the go-live gate for a Divi site. It converts the deeper docs —
[performance](10-performance.md), [security](19-security.md), [seo](13-seo.md),
[deployment](22-deployment.md) — into concrete yes/no items an agent can verify before a
site ships. Every item is checkable against the live front end, the child theme, or the
WordPress admin, not by opinion.

Run the whole list. A single unchecked box (a debug flag left on, a broken Theme Builder
template, an unoptimized hero image) is enough to embarrass a launch.

## Why It Matters

Divi sites are often launched by people who did not build them, on deadlines, with the
Visual Builder as the only test surface. That is exactly when regressions slip through:
the builder looks fine while the front end ships render-blocking CSS, exposed debug
output, or a header that only exists on the home page. A checklist catches the failure
modes that "it looks right in the builder" always misses.

## Content & Structure

**Rules:** [Architecture](01-architecture.md) · [Templates](08-templates.md)

- [ ] Every layout is expressed as section → row → column → module, with no orphaned or
      empty modules left from editing.
- [ ] Headers, footers, and post/archive templates are defined once in the
      [Theme Builder](02-theme-builder.md), not rebuilt per page.
- [ ] Repeated styles use presets/global modules; there is no per-module inline CSS
      duplicated across the site.
- [ ] All placeholder/Lorem Ipsum content and stock demo images are replaced.
- [ ] Dynamic content and custom fields resolve correctly with real data, not fallbacks.

## Performance

**Rules:** [Performance](10-performance.md)

- [ ] Divi performance features are enabled: dynamic CSS, dynamic module framework,
      critical CSS, and deferred/removed unused jQuery where compatible.
- [ ] Images are correctly sized, compressed, and lazy-loaded; the hero/LCP image is not
      lazy-loaded and is preloaded if needed.
- [ ] Total page weight and request count are within budget; no plugin was added for an
      effect Divi already provides.
- [ ] Core Web Vitals (LCP, CLS, INP) pass on a real mobile profile, tested on the front
      end. See [performance](10-performance.md).
- [ ] A caching layer (page/object cache or CDN) is active and verified.

## Responsive & Accessibility

**Rules:** [Responsive Design](11-responsive-design.md) · [Accessibility](12-accessibility.md)

- [ ] Every page is checked at phone, tablet, and desktop breakpoints on the rendered
      front end. See [responsive-design](11-responsive-design.md).
- [ ] Images have meaningful `alt` text; decorative images have empty `alt`.
- [ ] Color contrast meets WCAG AA; interactive elements are keyboard-reachable with
      visible focus. See [accessibility](12-accessibility.md).
- [ ] Heading levels are hierarchical (one H1 per page, no skipped levels).

## SEO & Metadata

**Rules:** [SEO](13-seo.md)

- [ ] Titles, meta descriptions, and Open Graph/social tags are set per page.
- [ ] A single canonical H1 per page; semantic heading structure throughout.
- [ ] XML sitemap and `robots.txt` are correct and not blocking production.
- [ ] Redirects for any changed URLs are in place; no broken internal links. See
      [seo](13-seo.md).

## Security & Configuration

**Rules:** [Security](19-security.md) · [Production](25-production.md)

- [ ] `WP_DEBUG` and Divi debug/static-CSS-off flags are disabled in production.
- [ ] All custom PHP/CSS/JS lives in a **child theme**, never the parent.
- [ ] WordPress core, Divi, and plugins are updated; Divi license is active for updates.
- [ ] Admin accounts use strong credentials/MFA; default "admin" username is not in use.
- [ ] User-supplied data in custom modules is sanitized on input and escaped on output.
      See [security](19-security.md).

## Deployment & Backup

**Rules:** [Deployment](22-deployment.md) · [Maintenance](23-maintenance.md)

- [ ] The site was promoted from staging, not built live; staging matches production
      config. See [deployment](22-deployment.md).
- [ ] A full backup (database + files) exists and restore was tested, including exported
      Theme Builder templates and layout library.
- [ ] Forms deliver (test submission received); analytics and consent/cookie tooling fire.
- [ ] SSL is valid and all URLs are HTTPS with no mixed-content warnings.

## AI Review Checklist

- Is every item above verifiable on the live front end or in the admin, and checked?
- Are debug flags off and is all customization in the child theme?
- Do Core Web Vitals pass on a real mobile profile, not just in the builder?
- Is a tested backup — including Divi templates and layouts — in place before launch?

## Related

- `knowledge/divi/25-production.md`
- `knowledge/divi/10-performance.md`
- `knowledge/divi/22-deployment.md`
- `knowledge/divi/19-security.md`
- `knowledge/divi/13-seo.md`
