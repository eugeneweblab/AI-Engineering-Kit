---
id: tailwind/09-typography
topic: tailwind
slug: typography
title: "Typography"
type: doc
order: 9
status: ready
tags: [tailwind, typography]
related: [tailwind/10-colors, tailwind/08-sizing, tailwind/16-theme, tailwind/22-accessibility, tailwind/11-responsive-design]
when_to_use: "Read before styling any text — headings, body copy, labels, or long-form article content."
---
# Typography

## Purpose

This document defines how to style text with Tailwind's `text-*` (size and color),
`font-*` (family and weight), `leading-*` (line-height), `tracking-*` (letter-spacing),
and the `text-balance` / `text-pretty` / `line-clamp-*` helpers. It also covers the
`@tailwindcss/typography` plugin for rendered Markdown. It is written so an agent produces
readable, consistent, accessible text instead of ad-hoc font sizing.

Type is where most of an interface's content lives, so its rules compound: a scale applied
consistently reads as polished, while per-element font tweaks read as amateur and are
painful to unify later.

## Why It Matters

Typography is legibility, and legibility is accessibility. Text that is too small, too
tightly leaded, too long per line, or too low in contrast excludes real users and can fail
WCAG. These issues rarely throw errors — the text renders fine — so they slip through
review and reach users who then can't read the page. Because type appears on every screen,
a small systematic mistake (a hard-coded `text-[13px]` everywhere) multiplies into a
site-wide readability problem that is expensive to walk back.

## Core Principles

- **Use the type scale, not arbitrary sizes.** `text-sm`, `text-base`, `text-lg`,
  `text-xl` … carry paired, sensible line-heights. Arbitrary `text-[13px]` opts out of the
  scale and usually forgets line-height.
- **Never go below the readable floor for body text.** Body copy should be `text-base`
  (~16px) or larger; smaller sizes hurt legibility and accessibility.
- **Cap line length.** Comfortable reading is ~60–75 characters per line — pair type with a
  `max-w-*` (see [Sizing](08-sizing.md)); full-width paragraphs are hard to track.
- **Set line-height to match size.** Tight leading suits large headings (`leading-tight`);
  generous leading suits body (`leading-relaxed`). The scale's defaults are a good start.
- **Convey meaning with weight and hierarchy, not just size.** `font-semibold` on a heading
  plus a size step communicates structure; do not lean on color alone (color-blind users
  miss it).

## Best Practices

- Establish a family with `font-sans` / `font-serif` / `font-mono` at a high level and let
  it inherit; don't repeat the family on every element.
- Use the semantic scale for hierarchy: `text-3xl font-bold` headings, `text-base` body,
  `text-sm text-gray-500` captions.
- Apply `text-balance` to headings so they wrap into even lines, and `text-pretty` to body
  paragraphs to avoid orphans — both improve visual quality for free.
- Truncate with `truncate` (single line) or `line-clamp-3` (multi-line) for cards and lists
  where overflow must be bounded; pair `truncate` with `min-w-0` inside Flex.
- Use `tracking-tight` on large display headings and `tracking-wide` on all-caps labels;
  leave body tracking at default.
- For rendered Markdown/CMS content, apply the `prose` class from
  `@tailwindcss/typography` rather than styling every tag by hand.

## Examples

**Good Example** — semantic scale, capped measure, balanced heading, readable body

```html
<article class="mx-auto max-w-prose">
  <!-- Scale size + weight for hierarchy; text-balance evens the heading's line wrap -->
  <h1 class="text-3xl font-bold tracking-tight text-balance">
    How Tailwind keeps type consistent
  </h1>
  <!-- Body at the readable floor with relaxed leading and pretty wrapping -->
  <p class="mt-4 text-base leading-relaxed text-pretty text-gray-700">
    Body copy that stays legible at a comfortable measure…
  </p>
  <p class="mt-2 text-sm text-gray-500">Posted 7 July 2026</p>
</article>
```

**Bad Example** — arbitrary tiny sizes, no measure cap, no hierarchy

```html
<article>
  <!-- Arbitrary size with no line-height, no weight distinction from body -->
  <h1 class="text-[19px]">How Tailwind keeps type consistent</h1>
  <!-- 13px body is below the readable floor; no max-width means lines run too long -->
  <p class="text-[13px]">Body copy that is hard to read and runs edge to edge…</p>
  <!-- Caption relies on size alone, indistinguishable from body at a glance -->
  <p class="text-[12px]">Posted 7 July 2026</p>
</article>
```

## Common Mistakes

- Arbitrary font sizes (`text-[13px]`) that skip the scale and its paired line-heights.
- Body text below ~16px, hurting legibility and accessibility.
- Paragraphs with no `max-w-*`, running to unreadable line lengths on wide screens.
- Hard-coding font family on every element instead of inheriting from a parent.
- Using `truncate` without `min-w-0` in a Flex row, so it never actually truncates.
- Signaling hierarchy or state with color only, which color-blind users cannot perceive.
- Hand-styling Markdown output tag by tag instead of using the `prose` class.

## Production Tips

- Load web fonts with `font-display: swap` and preload the primary family to avoid invisible
  text (FOIT) on first paint; define the stack once in the theme so `font-sans` maps to it.
- Tune `prose` with modifier classes (`prose-lg`, `prose-headings:font-semibold`) instead of
  overriding its generated selectors — overrides are brittle across plugin versions.
- For responsive display type, step the size at breakpoints (`text-2xl md:text-4xl`) rather
  than one large size that dwarfs small screens.

## AI Review Checklist

- Do all text sizes come from the type scale, not arbitrary `[13px]`-style values?
- Is body text at least `text-base` (~16px)?
- Is long-form text capped to a readable measure with `max-w-prose` or similar?
- Does hierarchy use size + weight, not color alone?
- Are truncating flex children given `min-w-0` alongside `truncate`?
- Is rendered Markdown styled with the `prose` class rather than per-tag rules?
- Is line-height chosen to suit the size (tight for headings, relaxed for body)?

## Related

- `knowledge/tailwind/10-colors.md`
- `knowledge/tailwind/08-sizing.md`
- `knowledge/tailwind/16-theme.md`
- `knowledge/tailwind/22-accessibility.md`
- `knowledge/tailwind/11-responsive-design.md`
