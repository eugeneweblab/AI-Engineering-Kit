---
id: divi/00-overview
topic: divi
slug: overview
title: "Overview"
type: doc
order: 0
status: ready
tags: [divi, overview]
related: [divi/01-architecture, divi/03-modules, divi/04-custom-modules, divi/05-layouts, divi/02-theme-builder]
when_to_use: "Read first when starting any Divi build to understand how the topic's docs fit together."
---
# Overview

## Purpose

This document orients an agent working in **Divi** — the WordPress visual page builder
and theme from Elegant Themes. It maps the topic's docs and states the vocabulary and
mental model you must share before touching a Divi site. Read it first; each linked doc
goes deep on one area.

Divi is not "just a theme". It is a builder that stores page content as **shortcodes**
(Divi 4) or a **structured JSON content model** (Divi 5) and renders it through a
React-based Visual Builder. Editing Divi content correctly means respecting that model,
not treating pages as free-form HTML.

## Why It Matters

Divi powers millions of production sites, often maintained by non-developers. An agent
that edits Divi like a normal codebase will corrupt layouts: hand-writing shortcodes with
a wrong attribute, pasting HTML into the wrong place, or bypassing the builder all produce
pages that look fine until a client opens the Visual Builder and it fails to load. Divi
also has a deserved reputation for bloat — undisciplined use ships megabytes of unused CSS.
Knowing the architecture is what separates a fast, maintainable Divi site from a slow,
unmaintainable one.

## Core Principles

- **Edit through the builder's model, never around it.** Content lives in a defined
  structure (shortcodes or JSON). Corrupt the structure and the Visual Builder breaks.
- **Section → Row → Column → Module is the only hierarchy.** Every layout decomposes into
  this tree. See [architecture](01-architecture.md).
- **Reuse over duplication.** Global modules, presets, and the Theme Builder exist so one
  change propagates everywhere. Copy-paste is the primary source of Divi rot.
- **Performance is opt-in.** Divi can be fast, but only if you enable its performance
  features and avoid per-module custom CSS sprawl. See [performance](10-performance.md).

## How the Docs Fit Together

- **Foundation** — [architecture](01-architecture.md) explains the section/row/column/module
  tree, the content model, and the render pipeline. Start here after this overview.
- **Structure & templating** — [theme-builder](02-theme-builder.md) sets site-wide headers,
  footers, and dynamic templates. [layouts](05-layouts.md) covers saving and reusing whole
  page designs.
- **Content units** — [modules](03-modules.md) is the catalog of built-in modules and how
  to configure them. [custom-modules](04-custom-modules.md) covers building your own module
  in PHP/React when no built-in fits.
- **Dynamic & integration** — dynamic-content, custom-fields, and woocommerce docs wire
  Divi to real data instead of hard-coded text.
- **Quality gates** — performance, responsive-design, accessibility, and the
  production-checklist / ai-review-checklist enforce the non-negotiables before launch.

## Best Practices

- Decide the version first: **Divi 5** (current, JSON content model, new module API) vs
  **Divi 4** (shortcode model). Their content formats and module APIs differ; do not mix
  guidance blindly.
- Never edit page content in the raw `post_content` database field by hand. Use the builder
  or its documented import/export.
- Establish global styles and Theme Builder templates before building individual pages, so
  pages inherit instead of redefining.
- Keep a child theme for all PHP customization; never edit the Divi parent theme.

## Common Mistakes

- Treating Divi pages as editable HTML and pasting markup that the builder cannot parse.
- Building the same header on every page instead of once in the Theme Builder.
- Adding custom CSS to individual modules when a global preset would do, multiplying
  maintenance surface.
- Editing the parent theme, so the next Divi update wipes the change.

## AI Review Checklist

- Is the Divi version (4 vs 5) identified before any edit or code is written?
- Are content edits made through the builder model, not by hand-writing shortcodes/JSON?
- Is every layout expressed as section → row → column → module?
- Is PHP customization in a child theme, never the parent?
- Have global/reuse features been considered before duplicating a design?

## Related

- `knowledge/divi/01-architecture.md`
- `knowledge/divi/02-theme-builder.md`
- `knowledge/divi/03-modules.md`
- `knowledge/divi/04-custom-modules.md`
- `knowledge/divi/05-layouts.md`
