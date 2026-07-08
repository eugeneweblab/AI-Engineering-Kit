---
id: css/10-typography
topic: css
slug: typography
title: "Typography"
type: doc
order: 10
status: ready
tags: [css, typography]
related: [css/08-sizing, css/11-colors, css/23-accessibility, css/17-responsive-design, css/20-css-variables]
when_to_use: "Read before setting font-size, line-height, font-family, or loading web fonts."
---
# Typography

## Purpose

This document defines how to set type on the web: units for `font-size`, `line-height`,
line length, font stacks, web-font loading, and fluid type. It is written so an agent
produces text that is readable, accessible, respects user preferences, and does not cause
layout shift while fonts load.

Type interacts with [sizing](08-sizing.md) (line length), [colors](11-colors.md)
(contrast), and [accessibility](23-accessibility.md) (zoom, minimum sizes) — this doc
focuses on the type properties themselves.

## Why It Matters

Text is the majority of almost every interface, so typography decisions affect every
user on every screen. Two failures dominate: sizing type in `px`, which ignores the
user's browser font setting and breaks zoom for low-vision users; and loading web fonts
carelessly, which produces invisible text (FOIT) or a jarring reflow (FOUT) and hurts
Core Web Vitals. Getting units, line length, and font loading right makes text legible,
accessible, and stable — the baseline of a professional UI.

## Core Principles

- **Size type in `rem`, not `px`.** `rem` scales with the user's root font-size preference
  and with zoom; `px` overrides both, which is an accessibility failure. Reserve `px` for
  hairline borders, never for text.
- **Use unitless `line-height`.** A unitless value (e.g. `1.5`) multiplies the element's
  own font-size, so it stays correct when the font-size changes; a fixed `line-height:
  24px` breaks on larger text.
- **Constrain line length for readability.** Aim for ~45–75 characters per line
  (`max-width: 65ch`); lines that are too long are hard to track, too short are choppy.
- **Load fonts without hiding or shifting text.** Use `font-display: swap` and a matched
  fallback so text is visible immediately and the swap causes minimal reflow.
- **Respect the cascade and system stack.** A system font stack renders instantly with no
  download; only pull in a web font when the brand truly requires it.

## Best Practices

- Set the root font-size in a relative way (or leave the default 16px) and size everything
  else in `rem`; never set `html { font-size: 62.5% }` hacks that break user settings.
- Use `line-height` values without units — `1.4`–`1.6` for body, tighter (`1.1`–`1.25`)
  for large headings.
- Cap measure with `max-width: 65ch` on prose containers; `ch` tracks the font so the
  bound stays right across sizes.
- For fluid headings, use `clamp()`: `font-size: clamp(1.5rem, 4vw, 3rem)` scales with
  the viewport but stays bounded and, crucially, remains zoomable because the `rem`
  bounds still respond to user settings.
- Load web fonts with `font-display: swap`, `preload` the critical weight, and self-host
  (or use `size-adjust`/`ascent-override` on a `@font-face` fallback) to minimize the
  FOUT reflow.
- Provide a real fallback stack (`font-family: "Brand", system-ui, sans-serif`) so text is
  styled before and if the web font fails.
- Set `text-wrap: balance` on headings and `text-wrap: pretty` on paragraphs (supported in
  current browsers) to avoid orphans and ragged wraps — with graceful degradation.

## Examples

**Good Example** — accessible, stable, readable type

```css
:root { --font-body: system-ui, -apple-system, sans-serif; }

body {
  font-family: var(--font-body);
  font-size: 1rem;      /* scales with user setting + zoom */
  line-height: 1.5;     /* unitless: adapts to any font-size */
}
.prose { max-width: 65ch; } /* legible measure, tracks the font */

h1 {
  font-size: clamp(1.75rem, 4vw, 3rem); /* fluid but bounded and zoomable */
  line-height: 1.15;
  text-wrap: balance;   /* avoid a lone word on the last heading line */
}

@font-face {
  font-family: "Brand";
  src: url("/fonts/brand.woff2") format("woff2");
  font-display: swap;   /* show fallback immediately, swap when loaded */
}
```

**Bad Example** — pixel type, fixed leading, invisible-text font load

```css
body {
  font-size: 14px;      /* ignores user font-size and zoom → inaccessible */
  line-height: 20px;    /* fixed leading breaks if text scales */
}
h1 { font-size: 48px; } /* not fluid, not zoom-respecting */
.prose { width: 900px; } /* ~150 chars per line: hard to read, overflows mobile */

@font-face {
  font-family: "Brand";
  src: url("/fonts/brand.woff2");
  /* no font-display → FOIT: text is invisible until the font downloads */
}
```

## Common Mistakes

- Sizing text in `px`, defeating the user's font-size preference and browser zoom.
- Using a fixed-unit `line-height` that does not scale with font-size.
- Unbounded line length (full-width paragraphs) that is exhausting to read.
- Omitting `font-display`, causing flash-of-invisible-text and failed LCP.
- No fallback font stack, so text is unstyled (or invisible) if the web font fails.
- Loading many weights/styles you do not use, bloating the critical path.

## Production Tips

- `preload` only the one or two font files above the fold; preloading everything defeats
  the purpose and blocks rendering.
- Reduce layout shift by tuning the fallback with `size-adjust` and `ascent-override` on a
  fallback `@font-face` so the swap barely moves text (measurable CLS improvement).
- Subset fonts to the character ranges you actually ship (e.g. Latin) to cut file size
  dramatically.
- Prefer `system-ui` for UI chrome where brand type is not required — zero bytes, instant
  render, native feel.

## AI Review Checklist

- Is `font-size` in `rem` (or `em`), never `px`, for all text?
- Is `line-height` unitless so it scales with font-size?
- Is prose line length capped near 65ch for readability?
- Do all `@font-face` rules set `font-display: swap` (or `optional`)?
- Is there a real fallback stack ending in a generic family?
- Does fluid type via `clamp()` keep `rem`-based bounds so zoom still works?
- Are only the needed weights/styles loaded and critical ones preloaded?

## Related

- `knowledge/css/08-sizing.md`
- `knowledge/css/11-colors.md`
- `knowledge/css/23-accessibility.md`
- `knowledge/css/17-responsive-design.md`
- `knowledge/css/20-css-variables.md`
