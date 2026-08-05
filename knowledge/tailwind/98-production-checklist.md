---
id: tailwind/98-production-checklist
topic: tailwind
slug: production-checklist
title: "Tailwind CSS Production Checklist"
type: checklist
order: 98
status: ready
tags: [tailwind, production-checklist, "motion-reduce:", optional, prettier-plugin-tailwindcss, "focus-visible:"]
related: [tailwind/27-production, tailwind/19-performance, tailwind/20-optimization, tailwind/22-accessibility, tailwind/99-ai-review-checklist]
when_to_use: "Read before shipping a Tailwind build to production or cutting a release that changes styling."
---
# Tailwind CSS Production Checklist

## Purpose

A verifiable, pre-ship checklist for a Tailwind CSS (v4) build. Every item is a yes/no
question with a concrete way to confirm it. Work top to bottom before a release; a "no"
is a blocker until fixed or explicitly waived. This complements the runtime-focused
[production](27-production.md) and [performance](19-performance.md) docs.

## Build & Bundle

**Rules:** [Optimization](20-optimization.md) · [Performance](19-performance.md)

- [ ] Is the CSS produced by a real build step (Vite/PostCSS/CLI), not a CDN `<script>`
      that ships every utility to users?
- [ ] Does the built stylesheet contain only used utilities (spot-check that unused
      classes like `bg-fuchsia-950` are absent from the output)?
- [ ] Is content detection covering every template source, so no class is missing in
      production but present in dev?
- [ ] Are content globs precise and free of `node_modules`, keeping build time and CSS
      size down?
- [ ] Is the final CSS minified and served with long-lived cache headers plus a
      content hash in the filename?
- [ ] Is the production CSS bundle size tracked in CI, with an alert on unexpected growth?

## Theme & Configuration

**Rules:** [Theme](16-theme.md) · [Customization](15-customization.md)

- [ ] Is the theme configured once (v4 `@theme` in CSS, or a single config) with no
      conflicting duplicate definitions?
- [ ] Are brand colors, spacing, and radii defined as tokens rather than scattered
      arbitrary values across templates?
- [ ] Are custom fonts loaded with `font-display: swap` (or `optional`) and preloaded so
      text is not invisible during load?
- [ ] Is the base/reset layer (Preflight) intact, or are intentional overrides
      documented?

## Responsiveness & Layout

**Rules:** [Responsive Design](11-responsive-design.md) · [Layout](04-layout.md)

- [ ] Does every page render correctly at mobile, tablet, and desktop breakpoints with no
      horizontal scroll?
- [ ] Are responsive variants mobile-first (base styles unprefixed, `md:`/`lg:` add on
      top)?
- [ ] Do interactive targets meet a minimum tap size (~44px) on touch viewports?
- [ ] Does the layout survive long text and empty states without overflow or clipping?

## Dark Mode & Theming

**Rules:** [Dark Mode](12-dark-mode.md)

- [ ] If dark mode ships, does every surface, text, and border have a `dark:` counterpart
      with no unreadable low-contrast pairs?
- [ ] Is the dark-mode strategy (`class`/`data` attribute vs `prefers-color-scheme`)
      consistent across the app, with no flash of the wrong theme on load?

## Accessibility

**Rules:** [Accessibility](22-accessibility.md)

- [ ] Do text/background color pairs meet WCAG AA contrast (4.5:1 body, 3:1 large text)
      in both themes?
- [ ] Is focus visibility preserved — `focus-visible:` styles present and Preflight's
      outline not globally removed?
- [ ] Is meaning never conveyed by color alone (error states also use text/icon)?
- [ ] Do animations respect `motion-reduce:` / `prefers-reduced-motion`?

## Performance

**Rules:** [Performance](19-performance.md) · [Optimization](20-optimization.md)

- [ ] Is critical CSS small enough that first paint is not blocked by a huge stylesheet?
- [ ] Are heavy effects (`backdrop-blur`, large `shadow`, gradients) used sparingly on
      scroll-critical paths?
- [ ] Are you avoiding hundreds of unique arbitrary values that each generate a distinct
      rule and bloat the bundle?

## Tooling & CI

**Rules:** [Tooling](29-tooling.md) · [Production](27-production.md)

- [ ] Does `prettier-plugin-tailwindcss` run in CI so class order is consistent?
- [ ] Does a lint step flag unknown/typo'd class names before merge?
- [ ] Is the Tailwind version pinned and its upgrade notes reviewed (no deprecated APIs in
      use)?

## Related

- `knowledge/tailwind/27-production.md`
- `knowledge/tailwind/19-performance.md`
- `knowledge/tailwind/20-optimization.md`
- `knowledge/tailwind/22-accessibility.md`
- `knowledge/tailwind/99-ai-review-checklist.md`
