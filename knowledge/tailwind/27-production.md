---
id: tailwind/27-production
topic: tailwind
slug: production
title: "Tailwind CSS Production"
type: doc
order: 27
status: ready
tags: [tailwind, production]
related: [tailwind/19-performance, tailwind/20-optimization, tailwind/01-installation, tailwind/29-tooling, tailwind/98-production-checklist]
when_to_use: "Read before shipping a Tailwind build to production or setting up the production CSS pipeline."
---
# Tailwind CSS Production

## Purpose

This document defines how to take Tailwind from a development setup to a correct,
minimal production build: how content detection decides what ships, how to keep
dynamic classes from being purged, why the Play CDN must never reach production,
and how to cache and budget the resulting CSS. It is written so an agent can wire
a production pipeline that is small, cache-friendly, and free of missing-style
regressions.

In production, Tailwind's compiler scans your source, emits only the classes it
finds, and minifies the result. A correct build is almost entirely about making
sure the scanner sees every class that will actually render.

## Why It Matters

The production build is where the two worst Tailwind failure modes appear: a class
that worked in dev is purged and the style disappears, or the un-purged Play CDN
ships a multi-megabyte runtime that recompiles CSS in the browser on every load.
The first is a silent visual regression; the second is a hard performance and
reliability hit that also breaks under a strict Content-Security-Policy. Both are
avoidable, but only if the pipeline is set up deliberately — dev "just working" is
not evidence the production build is correct.

## Core Principles

- **The scanner ships only what it can statically find.** Any class name that is
  not a complete literal in a scanned file will be absent in production.
- **Never use the Play CDN in production.** It is a dev convenience that ships the
  whole engine and JITs in the browser; production must use a real build.
- **Minify and hash.** Emit minified CSS with a content hash in the filename so it
  caches forever and busts on change.
- **Make the build reproducible.** Same source, same output — no environment-
  dependent classes, no runtime-generated styles.
- **Budget the CSS.** A well-purged Tailwind site is small (tens of KB gzipped);
  track it so regressions are visible.

## Best Practices

- Build with the framework plugin (`@tailwindcss/vite`) or the PostCSS plugin
  (`@tailwindcss/postcss`), not the CDN, so purging and minification run.
- Let automatic content detection scan your source, and add explicit `@source`
  directives for template files or packages outside the default roots (e.g. a
  shared UI library in `node_modules`).
- Safelist only the classes that are legitimately dynamic and cannot be made static
  — a color from a CMS, a class assembled at runtime — using `@source inline(...)`;
  keep the list tiny.
- Serve CSS with long-lived immutable cache headers and a hashed filename; let the
  bundler handle the hash so a deploy invalidates it automatically.
- Gzip or Brotli the stylesheet at the CDN/edge; Tailwind output compresses
  extremely well because of repeated utility names.
- Load the stylesheet in the document head so it is render-blocking-by-design and
  there is no flash of unstyled content.
- Verify the build in CI, not just locally: run the production build and assert the
  CSS exists and is under a size budget.

## Examples

**Good Example** — Vite plugin build, explicit source, tiny safelist

```css
/* app.css — compiled at build time, minified, tree-shaken to used classes */
@import "tailwindcss";

/* Scan a sibling UI package the default roots would miss. */
@source "../../packages/ui/src/**/*.{ts,tsx}";

/* Keep the ONE genuinely dynamic class the scanner can't see. */
@source inline("bg-brand text-white");
```

```ts
// vite.config.ts — real build pipeline, produces hashed, minified CSS
import tailwindcss from "@tailwindcss/vite";
export default { plugins: [tailwindcss()] };
```

**Bad Example** — Play CDN in production

```html
<!-- Ships the full compiler (~hundreds of KB) and recompiles CSS in the browser
     on every page load. No purging, no minification, blocked by strict CSP,
     and slow. Fine for a throwaway prototype; never for production. -->
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config = { theme: { extend: {} } }</script>
```

## Common Mistakes

- Shipping the Play CDN because "it works in dev," paying a large runtime cost and
  breaking under CSP.
- Assuming automatic detection covers everything, then losing classes that live in
  an un-scanned package or a `.mdx`/template file — fix with `@source`.
- Safelisting broadly ("just in case") and bloating the stylesheet with unused
  utilities.
- No hashed filename, so a deploy serves stale cached CSS to returning users.
- Not running the production build in CI, so a purge regression reaches users
  before anyone sees it.
- Injecting styles at runtime (dynamic `<style>` from class strings) that the
  scanner never processed.

## Production Tips

- Add a CI gate that greps the built CSS for critical dynamic classes and fails if
  any are missing — cheaper than a visual regression in production.
- Set an explicit CSS size budget (e.g. warn > 50KB gzipped) and alert on growth;
  spikes usually mean an over-broad safelist or arbitrary-value sprawl.
- Keep one canonical build command shared by local, CI, and deploy so "works on my
  machine" cannot diverge from what ships.

## AI Review Checklist

- Is the production CSS produced by a real build (Vite/PostCSS plugin), never the
  Play CDN?
- Are all dynamic classes either made static or covered by a minimal `@source
  inline` safelist?
- Are sources outside the default roots (packages, templates) added via `@source`?
- Is the output minified, content-hashed, and served with immutable cache headers?
- Does CI run the production build and assert the CSS is present and within budget?
- Is compression (gzip/Brotli) enabled at the edge?

## Related

- `knowledge/tailwind/19-performance.md`
- `knowledge/tailwind/20-optimization.md`
- `knowledge/tailwind/01-installation.md`
- `knowledge/tailwind/29-tooling.md`
- `knowledge/tailwind/98-production-checklist.md`
