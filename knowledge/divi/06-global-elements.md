---
id: divi/06-global-elements
topic: divi
slug: global-elements
title: "Global Elements"
type: doc
order: 6
status: ready
tags: [divi, global-elements]
related: [divi/05-layouts, divi/02-theme-builder, divi/03-modules, divi/09-custom-css, divi/10-performance]
when_to_use: "Read before reusing a header, footer, CTA, or any module across more than one page."
---
# Global Elements

## Purpose

This document defines how to reuse a single, centrally-managed element across many pages
in Divi: **global modules**, **global rows/sections**, **presets**, and **global colors**.
It is written so an agent can choose the right reuse mechanism and avoid the copy-paste
sprawl that makes Divi sites unmaintainable.

A *global* element is one instance edited in one place; every location that references it
updates at once. This is different from a *layout* (a saved design you paste and then own
a separate copy of — see [layouts](05-layouts.md)) and from a Theme Builder template (which
replaces the whole header/footer/body — see [theme-builder](02-theme-builder.md)).

## Why It Matters

The single largest source of rot on a Divi site is the same button, hero, or contact block
duplicated across 40 pages. When the phone number changes, someone must find and edit all 40 —
and misses three. Global elements collapse that maintenance surface to one edit. They also keep
markup and CSS consistent, which matters for performance: Divi generates critical CSS per unique
module configuration, so ten copies of "the same" module that drifted apart ship ten variants of
CSS instead of one. Reuse is not a nicety in Divi; it is how you keep a site fast and correct.

## Core Principles

- **One source of truth per repeated element.** If a block appears on more than one page, it
  should exist once as a global module/row or as a Theme Builder area, never as N copies.
- **Presets over per-module overrides.** A *preset* is a named default for a module type
  (e.g. "Primary Button"). Style the preset, assign it, and every instance inherits — change
  the preset once to restyle all instances. The cost of skipping presets is unbounded drift.
- **Global colors, not hard-coded hex.** Define brand colors in the Global Color palette and
  reference them; a rebrand becomes one palette edit instead of a site-wide find-and-replace.
- **Choose the narrowest reuse tool.** Repeated *content* → global module. Repeated *styling*
  of otherwise-different content → preset. Repeated *color* → global color. Whole
  header/footer/body → Theme Builder, not a global module.
- **Detaching is deliberate and one-way.** Turning a global element local ("disable global")
  forks it; there is no re-link. Only detach when a location genuinely must diverge.

## Best Practices

- Build the element once, save it to the Divi Library as **Global**, then insert it everywhere.
  Editing any instance opens the shared definition — confirm the "Global" badge before editing.
- Use presets for buttons, headings, and blurbs so brand styling lives in the preset, not in
  20 individual modules. Name presets by role ("Primary Button"), not by look ("Blue Button").
- Reference Global Colors for every brand color. Never paste raw hex into individual modules
  when a palette slot exists.
- Keep global rows/sections small and single-purpose (a CTA band, a testimonial block). Large
  "global everything" containers are hard to reason about and force awkward per-page exceptions.
- For anything that appears on *every* page identically (site header, footer), prefer a Theme
  Builder template over a global module — it renders once site-wide and is easier to scope.
- Document in the layout name which elements are global (e.g. "CTA Band — GLOBAL") so the next
  editor knows an edit propagates before they make it.

## Examples

**Good Example** — one global CTA referenced by many pages, styled via preset and global color

```text
Divi Library
└── "Newsletter CTA — GLOBAL"        (Global Row: shared instance)
     └── Button module → preset "Primary Button"
           → background: Global Color "Brand/Primary"

Home page      → inserts the SAME global row  ┐
Pricing page   → inserts the SAME global row  ├─ edit once, all update
Blog sidebar   → inserts the SAME global row  ┘
```

Why: the phone number, copy, and styling exist once. Editing the preset restyles the button
everywhere; editing "Brand/Primary" rebrands the whole site; editing the row updates the copy
on every page — no page-by-page hunting, and Divi emits one CSS variant, not many.

**Bad Example** — copy-paste that drifts

```text
Home page    → Button module: bg #1a73e8, "Sign up"     (local copy)
Pricing page → Button module: bg #1976d2, "Sign Up"     (copied, hue drifted, casing drifted)
Blog page    → Button module: bg #1a73e8, "Subscribe"   (copied, then edited)
```

Why this is wrong: three independent copies. The brand blue already diverged (`#1a73e8` vs
`#1976d2`), the label casing is inconsistent, and a rebrand now means editing every page and
hoping none are missed. Divi ships three near-identical CSS blocks instead of one.

## Common Mistakes

- Saving a layout as **non-global** and treating it as reusable — pasting it forks a copy that
  no longer tracks the original.
- Using a global module for the site header/footer instead of the Theme Builder, then fighting
  scope and conditional-display limits it was never meant to handle.
- Hard-coding hex colors in modules while a Global Color palette exists, so rebrands miss spots.
- Detaching a global element for a one-off tweak and forgetting it is now permanently forked.
- Nesting a global row inside another global row, creating circular, hard-to-edit references.
- Skipping presets, so every button is individually styled and there is no single place to
  restyle them.

## Production Tips

- Before launch, audit the Divi Library: every element used on 2+ pages should be Global or a
  preset. Duplicated locals are a maintenance debt to pay down now, not later.
- Name global items with a `GLOBAL` marker so editors know changes propagate.
- When migrating a site to global elements, do it once and delete the old local copies —
  leaving both means editors update the wrong one.

## AI Review Checklist

- Is every element that repeats across pages a single global instance, preset, or Theme Builder
  area — not a duplicated local copy?
- Are buttons/headings styled through named, role-based presets rather than per-module overrides?
- Do brand colors reference the Global Color palette instead of hard-coded hex?
- Is the site header/footer built in the [Theme Builder](02-theme-builder.md), not as a global module?
- Are any global elements accidentally detached (forked) when they should still be linked?

## Related

- `knowledge/divi/05-layouts.md`
- `knowledge/divi/02-theme-builder.md`
- `knowledge/divi/03-modules.md`
- `knowledge/divi/09-custom-css.md`
- `knowledge/divi/10-performance.md`
