---
id: css/98-production-checklist
topic: css
slug: production-checklist
title: "CSS Production Checklist"
type: doc
order: 98
status: ready
tags: [css, production-checklist, optional, will-change, left, opacity, prefers-color-scheme]
related: [css/22-performance, css/23-accessibility, css/26-browser-compatibility, css/17-responsive-design, css/30-engineering-principles]
when_to_use: "Read before shipping a stylesheet, design system, or styled feature to production."
---
# CSS Production Checklist

## Purpose

This is the final gate before CSS ships. Each item is a verifiable yes/no check an agent
can confirm against the code, the built bundle, or a rendered page. If an item cannot be
answered "yes", the styling is not production-ready.

## Why It Matters

CSS ships to every user on every device and can never be assumed to run in a controlled
environment. A layout that works on the author's laptop can break on a narrow phone, in
RTL, in high-contrast mode, or on a slow connection. This checklist catches the failures
that only appear in the field, where they are expensive to fix and visible to everyone.

## Cross-Browser and Device

**Rules:** [Browser Compatibility](26-browser-compatibility.md) · [Modern CSS](25-modern-css.md)

- [ ] Verified in the current versions of Chrome, Firefox, Safari, and Edge.
- [ ] Tested on real mobile viewport widths (360px and up), not just a resized desktop window.
- [ ] Any modern feature (`:has()`, container queries, subgrid) has a fallback or a documented
      `@supports` guard — see [browser compatibility](26-browser-compatibility.md).
- [ ] Vendor prefixes are added by Autoprefixer, not hand-written, and match the browserslist.
- [ ] No horizontal scrollbar appears at any supported width.

## Responsive Layout

**Rules:** [Responsive Design](17-responsive-design.md) · [Media Queries](18-media-queries.md)

- [ ] Layout is fluid between breakpoints, not fixed-width — see [responsive design](17-responsive-design.md).
- [ ] Breakpoints are content-driven (where the layout breaks), not device-model specific.
- [ ] Text remains readable and untruncated when the user zooms to 200%.
- [ ] Touch targets are at least 44x44px on interactive elements.
- [ ] Layout uses logical properties so it adapts to RTL where the product is localized.

## Accessibility

**Rules:** [Accessibility](23-accessibility.md)

- [ ] Text meets WCAG AA contrast (4.5:1 body, 3:1 large) — see [accessibility](23-accessibility.md).
- [ ] A visible `:focus-visible` style exists on every interactive element; focus is never `outline: none` without replacement.
- [ ] `@media (prefers-reduced-motion: reduce)` disables or reduces non-essential animation.
- [ ] Content is not conveyed by color alone.
- [ ] Layout does not depend on `order`/absolute positioning in a way that breaks the DOM reading order.

## Performance

**Rules:** [Performance](22-performance.md)

- [ ] The CSS bundle is minified and within its size budget — see [performance](22-performance.md).
- [ ] Critical/above-the-fold CSS loads render-blocking; the rest is deferred or split.
- [ ] Unused CSS has been purged; coverage of the shipped bundle is measured.
- [ ] Animations use only `transform` and `opacity` (compositor-friendly), not `top`/`left`/`width`.
- [ ] `will-change` is applied narrowly and removed after the animation, not left globally.
- [ ] Web fonts use `font-display: swap` (or `optional`) and are preloaded if critical.

## Robustness

**Rules:** [Specificity](03-specificity.md) · [Browser Compatibility](26-browser-compatibility.md)

- [ ] No `!important` except in documented, isolated utility layers.
- [ ] Maximum selector specificity is a single class unless justified — see [engineering principles](30-engineering-principles.md).
- [ ] Colors, spacing, type, and breakpoints come from tokens/custom properties, not magic numbers.
- [ ] Layouts tolerate variable content: long strings, empty states, and missing images do not break them.
- [ ] Dark mode (if supported) is driven by `prefers-color-scheme` or a token switch, with no hard-coded light-only colors.

## Tooling and Hygiene

**Rules:** [Debugging](27-debugging.md) · [Best Practices](28-best-practices.md)

- [ ] Stylelint passes with the project config; no disabled rules without a comment.
- [ ] The stylesheet builds with no warnings and no `@import` chains that block loading.
- [ ] Print styles are provided or explicitly deemed out of scope.
- [ ] Dead vendor prefixes and legacy hacks for unsupported browsers are removed.

## AI Review Checklist

- Have all six groups above been checked, with every box confirmed or explicitly waived?
- For any unchecked item, is there a written reason and a follow-up, rather than silence?
- Were the checks performed against the built bundle and a rendered page, not just source?
- Does the change hold up at 360px width, at 200% zoom, and in reduced-motion mode?

## Related

- `knowledge/css/22-performance.md`
- `knowledge/css/23-accessibility.md`
- `knowledge/css/26-browser-compatibility.md`
- `knowledge/css/17-responsive-design.md`
- `knowledge/css/30-engineering-principles.md`
