---
id: frontend/10-responsive-design
topic: frontend
slug: responsive-design
title: "Frontend Responsive Design"
type: doc
order: 10
status: ready
tags: [frontend, responsive-design, minmax, min-width, sizes, srcset, clamp]
related: [css/17-responsive-design, frontend/09-accessibility, frontend/15-styling, frontend/16-css-architecture, frontend/08-performance, frontend/18-assets]
defers_to: css/17-responsive-design
when_to_use: "Read before building any layout or component that must work across phone, tablet, and desktop."
---
# Frontend Responsive Design

## Purpose

This document defines how to build layouts that adapt to any viewport, input, and pixel
density: fluid layout, breakpoints, responsive images, and touch targets. It is written so
an agent can build one layout that works everywhere, rather than a desktop layout that
breaks on a phone.

Responsive design is the default, not an enhancement. Most traffic is mobile, screen sizes
form a continuum (not three fixed devices), and the same page is read on a watch and a 4K
monitor. Design for the range, not for your laptop.

## Why It Matters

The majority of web traffic is on mobile, and search engines index the mobile version of
your site first. A layout that only works at 1440px wide loses more than half its users to
overflow, tiny tap targets, and horizontal scroll. These breakages are easy to miss because
developers work on wide screens where everything looks fine — the failure only appears on
the devices where most usage actually happens. Building mobile-first makes the constrained
case the one you can't forget.

## Core Principles

- **Mobile-first.** Write base styles for the smallest screen, then add complexity at larger
  breakpoints with `min-width` media queries. Progressive enhancement is simpler than
  stripping a desktop layout down, and it keeps mobile CSS lean.
- **Fluid by default, fixed by exception.** Use relative units (`%`, `rem`, `fr`, `ch`,
  `min()`/`clamp()`) so layout flexes with the viewport. Fixed pixel widths are what overflow.
- **Breakpoints follow content, not devices.** Add a breakpoint where *the layout breaks*,
  not at named device widths — device sizes change every year; your content's needs don't.
- **Design for touch and pointer.** Tap targets ≥ 44×44px, no hover-only interactions, and
  respect both fine (mouse) and coarse (finger) input.
- **The viewport meta tag is mandatory.** Without `width=device-width, initial-scale=1`,
  mobile browsers render a zoomed-out desktop page and every media query is wrong.

## Best Practices

- Prefer intrinsic layout — **Flexbox** and **Grid** with `auto-fit`/`minmax`, `flex-wrap`,
  and `gap` — so items reflow without any media queries at all. Fewer breakpoints, fewer bugs.
- Use `clamp()` for fluid type and spacing (`font-size: clamp(1rem, 0.5rem + 2vw, 1.5rem)`)
  so values scale smoothly between bounds instead of jumping at breakpoints.
- Serve responsive images with `srcset`/`sizes` (or `<picture>` for art direction) so phones
  download small files, not desktop-sized ones (see [assets](18-assets.md) and [performance](08-performance.md)).
- Use **container queries** for reusable components that adapt to their container's width, not
  the viewport's — a card in a sidebar and the same card full-width should each lay out correctly.
- Test the real range: 320px minimum width up to large desktops, plus landscape phones and
  200% zoom. Content must reflow to 320px with no horizontal scroll (a WCAG requirement).
- Size text and controls in `rem`, not `px`, so the layout respects the user's browser font
  setting instead of overriding it.
- Handle the safe-area insets and dynamic viewport units (`dvh`) so content is not hidden
  behind notches or mobile browser chrome.

## Examples

**Good Example** — fluid, intrinsic grid that needs no breakpoints

```css
/* auto-fit + minmax: cards flow from 1 column on a phone to many on desktop,
   with no media queries — the browser fits as many 16rem tracks as will fit. */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: 1rem;
}

/* Fluid type scales smoothly between 1rem and 1.5rem instead of jumping. */
h1 { font-size: clamp(1.5rem, 1rem + 3vw, 2.5rem); }
```

```html
<!-- Mandatory: without this, media queries and layout are wrong on mobile. -->
<meta name="viewport" content="width=device-width, initial-scale=1" />
<!-- Phones fetch the 400w file, not the 1200w one. -->
<img src="hero-800.jpg" srcset="hero-400.jpg 400w, hero-800.jpg 800w, hero-1200.jpg 1200w"
     sizes="(max-width: 600px) 100vw, 50vw" width="800" height="400" alt="" />
```

**Bad Example** — fixed widths, desktop-first, tiny touch targets

```css
.container {
  width: 1200px;        /* fixed px → horizontal scroll on every phone */
}
@media (max-width: 768px) {
  .container { width: 1000px; } /* desktop-first patching, still overflows */
}
.icon-btn {
  width: 20px; height: 20px;    /* far below the 44px minimum tap target */
}
.menu:hover .submenu { display: block; } /* hover-only → unusable on touch */
```

## Common Mistakes

- Omitting the viewport meta tag, so mobile renders a zoomed-out desktop page.
- Fixed pixel widths and heights that overflow narrow screens and cause horizontal scroll.
- Desktop-first `max-width` queries that patch a broken layout instead of building up from mobile.
- Breakpoints pinned to specific device widths rather than where the content actually breaks.
- Tap targets under 44px and hover-only menus that touch users cannot open.
- Sizing everything in `px`, ignoring the user's font-size preference.
- Serving one large image to every device, wasting mobile bandwidth.

## Production Tips

- Test on real devices and throttled networks, not just the browser's device emulator.
- Add a visual-regression or responsive-screenshot check at key widths (320, 768, 1280) to CI.
- Verify 200% zoom and 320px reflow as part of the accessibility pass (see [accessibility](09-accessibility.md)).

## AI Review Checklist

- Is the viewport meta tag present with `width=device-width, initial-scale=1`?
- Are base styles mobile-first, enhanced with `min-width` queries?
- Is layout fluid (relative units, Flexbox/Grid) rather than fixed pixel widths?
- Do breakpoints track content, and do reusable components use container queries where apt?
- Are tap targets ≥ 44px and is nothing hover-only?
- Are images responsive via `srcset`/`sizes`, and does text use `rem`?
- Does content reflow to 320px and 200% zoom with no horizontal scroll?

## Related

- `knowledge/css/17-responsive-design.md`
- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/15-styling.md`
- `knowledge/frontend/16-css-architecture.md`
- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/18-assets.md`
