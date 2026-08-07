---
id: divi/25-production
topic: divi
slug: production
title: "Divi Production"
type: doc
order: 25
status: ready
tags: [divi, production, define, DISALLOW_FILE_EDIT, noindex, wp-admin, WP_AUTO_UPDATE_CORE, FORCE_SSL_ADMIN]
related: [divi/10-performance, divi/22-deployment, divi/19-security, divi/98-production-checklist, divi/13-seo]
when_to_use: "Read before launching or hardening a Divi site so it ships fast, secure, and safe to update in production."
---
# Divi Production

## Purpose

This document defines what a Divi site must satisfy to be considered production-ready:
performance, security, caching, update safety, and the operational habits that keep it
healthy after launch. It complements the actionable [production-checklist](98-production-checklist.md);
this doc explains the reasoning, the checklist verifies it.

Production for Divi is different from a generic WordPress launch because Divi adds its own
render pipeline, its own asset bundles, and a builder that clients will keep editing after
you leave. Getting to production means hardening all three.

## Why It Matters

A Divi site that is beautiful in the builder can still fail in production: a 4 MB page that
tanks Core Web Vitals, an out-of-date theme with a known CVE, or a caching layer that
serves the builder's editing UI to logged-out visitors. These failures are invisible during
development and expensive after launch — lost rankings, exploited vulnerabilities, or a
support fire when a cached page will not update. Production discipline turns "it works on my
screen" into "it works for every visitor, under load, over time".

## Core Principles

- **Ship the minimum bytes.** Enable Divi's performance framework and let it emit only the
  CSS/JS a page actually uses. Unused asset weight is the default failure mode. See
  [performance](10-performance.md).
- **Cache, but exclude the builder.** Page/object caching is mandatory for speed, but the
  Visual Builder and logged-in editing must bypass the cache or you will serve stale or
  broken markup.
- **Stay current, safely.** Keep WordPress, Divi, and plugins updated for security — but
  update on staging first, because Divi releases can change render output. See
  [deployment](22-deployment.md).
- **Least privilege and hardening.** Production is a security boundary: limited admin
  accounts, no file editing in the dashboard, HTTPS everywhere. See [security](19-security.md).
- **Backups are part of "done".** A release is not complete until a tested restore path
  exists for both database and uploads.

## Best Practices

- Turn on Divi's **performance options**: dynamic CSS, dynamic module framework, critical
  CSS, deferred/async assets, and disable Google Fonts you do not use.
- Serve **correctly sized, lazy-loaded, next-gen (WebP/AVIF)** images; Divi galleries and
  sliders are the usual weight offenders.
- Put a **page cache** (server or plugin) plus a **CDN** in front of the site, and configure
  cache exclusions for `wp-admin`, the builder, carts, and logged-in users.
- Run the site on a **PHP line that still receives security fixes** — 8.1 went end of
  life in December 2025, so 8.2 is the floor — with OPcache, and confirm Divi's minimum
  PHP/WordPress versions are met before launch.
- **Force HTTPS**, set security headers (HSTS, X-Content-Type-Options, a CSP where feasible),
  and disable the dashboard file editor (`DISALLOW_FILE_EDIT`).
- Automate **daily backups** of database + `wp-content/uploads`, stored off-server, and test
  a restore before you rely on it.
- Configure a **staging environment** that mirrors production; apply Divi/plugin/core updates
  there first, then promote.
- Verify **SEO basics** at launch: titles, meta, sitemap, canonical URLs, and that no
  `noindex` from staging leaked to production. See [seo](13-seo.md).

## Examples

**Good Example** — production hardening in `wp-config.php`

```php
// Update-safe, in wp-config.php — enforced by the platform, not per-page.
define( 'DISALLOW_FILE_EDIT', true );   // no theme/plugin editing from the dashboard
define( 'WP_AUTO_UPDATE_CORE', 'minor' ); // security patches auto-apply; majors are manual
define( 'FORCE_SSL_ADMIN', true );      // admin/login only over HTTPS
// Divi builder must bypass the page cache; configure the cache plugin to exclude
// et_fb=1 requests and logged-in users so editors never see cached markup.
```

**Bad Example** — cache everything, edit live, no backups

```
- Full-page cache with no exclusions → the Visual Builder loads stale HTML and
  "won't save"; logged-out visitors sometimes get the editor shell.
- Divi updated directly on production → a render change breaks a live layout with
  no rollback.
- No off-server backup → a bad update or hack means starting over.
```

## Common Mistakes

- Launching without Divi's performance features on, shipping the full CSS/JS bundle.
- Caching the Visual Builder or logged-in sessions, causing "changes won't save" bugs.
- Updating Divi or plugins on production first, breaking a live layout with no rollback.
- Leaving a staging `noindex` in place, deindexing the production site.
- No tested backup/restore, so recovery is impossible when something breaks.
- Running an outdated Divi/WordPress with known vulnerabilities to avoid "risky" updates.

## Production Tips

- Add real-user monitoring (Core Web Vitals) and an uptime check; regressions after a Divi
  update show up here first.
- Keep an update log: date, versions, and what changed on staging, so a regression is
  traceable to a specific release.
- Warm the cache after a deploy or purge so the first real visitor does not pay the
  full-render cost.

## AI Review Checklist

- Are Divi's performance features (dynamic CSS/JS, critical CSS) enabled?
- Is page caching in place with the builder, admin, and logged-in users excluded?
- Were updates applied on staging before production, with a rollback path?
- Is HTTPS forced, the dashboard file editor disabled, and Divi/core up to date?
- Are automated, off-server backups configured and a restore actually tested?
- Are images correctly sized, lazy-loaded, and served as WebP/AVIF?

## Related

- `knowledge/divi/10-performance.md`
- `knowledge/divi/13-seo.md`
- `knowledge/divi/19-security.md`
- `knowledge/divi/22-deployment.md`
- `knowledge/divi/98-production-checklist.md`
