---
id: divi/05-layouts
topic: divi
slug: layouts
title: "Layouts"
type: doc
order: 5
status: ready
tags: [divi, layouts]
related: [divi/01-architecture, divi/02-theme-builder, divi/03-modules, divi/06-global-elements, divi/22-deployment]
when_to_use: "Read before saving, importing, or reusing a whole page design across pages or sites."
---
# Layouts

## Purpose

This document covers **Divi layouts** — saved, reusable page designs. It explains the Divi
Library (saved and global layouts), premade layout packs, and the portability
(import/export) system that moves designs between pages, sites, and environments. Layouts are
Divi's unit of design reuse above the [module](03-modules.md) level.

## Why It Matters

Layouts are how a team ships consistent, on-brand pages quickly and moves work from staging to
production reliably. Misusing them is a top source of Divi maintenance pain: importing a
layout pack wholesale drags in demo images, custom CSS, and unused sections; saving everything
as a non-global copy means a brand change must be redone on every page. Understanding
saved vs global layouts and clean import/export keeps a site both fast to build and easy to
change.

## Core Principles

- **Saved layout = a copy; global layout = a shared instance.** A saved layout you insert is
  duplicated and edits stay local. A **global** layout is referenced — editing it updates every
  place it is used. Choose deliberately.
- **The Divi Library is the reuse store.** Save sections, rows, or whole pages to the Library,
  then insert them. It is the correct place for repeated designs (testimonial blocks, CTA
  sections).
- **Portability is JSON.** Export/import produces a `.json` file capturing the layout's model.
  This is the supported way to move designs — not database copying.
- **Premade packs are starting points, not finished pages.** They include demo content and
  styling you must prune before shipping.
- **Global layouts trade flexibility for consistency.** One edit everywhere is powerful and
  dangerous — an unintended change propagates site-wide.

## Best Practices

- Use **global** layouts/sections for anything that must stay identical everywhere (a shared
  CTA, a footer band). Use plain saved layouts when instances should diverge.
- Save reusable blocks to the Library with clear, categorized names so they are findable, not
  a flat list of "Section 1, Section 2".
- After importing a premade pack, delete unused sections and replace demo images/copy before
  publishing; do not ship placeholder content or unused assets.
- Move designs between environments with portability exports checked into your repo, so staging
  and production match. See [deployment](22-deployment.md).
- Combine layouts with [global elements](06-global-elements.md) and Theme Builder templates so
  reuse compounds instead of fragmenting.

## Examples

**Good Example** — global section for a shared CTA

```text
Design a "Contact CTA" section once → Save to Library as GLOBAL.
Insert it on Home, Services, About.
Later: change the phone number in the global section once.
→ All three pages update automatically. One source of truth.
```

**Bad Example** — non-global copies duplicated everywhere

```text
Build the CTA section, Save to Library as a normal (non-global) layout.
Insert copies on Home, Services, About.
Phone number changes → edit it on Home, Services, About separately.
→ One page gets missed; the site now shows two phone numbers.
```

## Common Mistakes

- Saving as a normal layout when the design should be global, forcing manual multi-page edits.
- Making everything global, so an intended local tweak silently changes the whole site.
- Importing a full premade pack and shipping its demo images, copy, and unused CSS.
- Copying layouts by duplicating the database row instead of using portability export/import,
  breaking IDs and references.
- Unnamed or uncategorized Library items that no one can find or reuse later.

## Production Tips

- Keep a small, curated Library of vetted blocks; prune stale layouts so the team reuses the
  approved ones.
- Store portability `.json` exports of key layouts in version control as the deployable
  artifact, alongside Theme Builder exports. See [deployment](22-deployment.md).
- Before publishing an imported pack, run the page through the [performance](10-performance.md)
  and [accessibility](12-accessibility.md) checks — packs are not tuned for either.

## AI Review Checklist

- Is each reused design correctly chosen as global (shared) vs saved (independent copy)?
- Are Library items named and categorized so they are discoverable?
- Has all demo content and unused sections/assets been removed from imported packs?
- Are layouts moved via portability export/import, not raw database copying?
- Are key layout exports version-controlled for environment parity?

## Related

- `knowledge/divi/01-architecture.md`
- `knowledge/divi/02-theme-builder.md`
- `knowledge/divi/03-modules.md`
- `knowledge/divi/06-global-elements.md`
- `knowledge/divi/22-deployment.md`
