---
id: divi/30-engineering-principles
topic: divi
slug: engineering-principles
title: "Divi Engineering Principles"
type: doc
order: 30
status: ready
tags: [divi, engineering-principles, wp_enqueue_style, wp_get_theme, get_stylesheet_directory_uri, add_action, post_content, wp_enqueue_script, update-safe, correct, durable]
related: [divi/24-best-practices, divi/01-architecture, divi/10-performance, divi/16-wordpress-hooks, divi/09-custom-css]
when_to_use: "Read before making any non-trivial Divi decision to apply the durable principles that keep a build correct, fast, and update-safe."
---
# Divi Engineering Principles

## Purpose

This document states the durable engineering principles behind every other Divi doc.
Where [best-practices](24-best-practices.md) gives you rules to apply, this gives you the
*reasoning* those rules derive from — so an agent can make a sound decision even when no
specific rule covers the situation. Read it to calibrate judgment, not to copy steps.

Divi is a visual builder layered on WordPress. Almost every mistake in a Divi project
traces back to ignoring one of a small number of principles: fighting the builder's
model, editing the parent theme, or trading long-term maintainability for a fast first
build. These principles are how you avoid all three.

## Why It Matters

Divi lets you build a page in minutes with zero code. That same freedom makes it trivial
to create something no one can maintain: inline CSS on a hundred modules, a header
rebuilt on every page, PHP hacked into the parent theme. It all *works* — until a Divi
update ships, a client opens the Visual Builder, or Core Web Vitals fail in production.
Because Divi enforces none of this for you, the discipline must come from principle. An
agent that internalizes the "why" ships builds that survive updates and hand-off; one
that only pattern-matches ships builds that rot.

## Core Principles

- **Work with the builder's model, never against it.** Content is a defined structure —
  shortcodes in Divi 4, JSON in Divi 5. Respect the section → row → column → module tree
  and edit through the builder. Bypassing the model corrupts layouts silently. See
  [architecture](01-architecture.md).
- **The parent theme is read-only.** All PHP, CSS, JS, and hooks live in a child theme.
  Do X (child theme) because Y (updates overwrite the parent); the cost is one extra
  theme folder, which is trivial. See [wordpress-hooks](16-wordpress-hooks.md).
- **Style at the highest level that works.** Prefer global colors, fonts, and presets
  over per-module custom CSS, because one central edit should propagate everywhere. The
  cost of per-module CSS is N-times the maintenance and invisible drift.
- **Reuse over duplication.** Global modules, presets, layouts, and the
  [Theme Builder](02-theme-builder.md) exist so one change fans out. Copy-paste is the
  single largest source of Divi rot.
- **Performance is a design constraint, not a cleanup step.** Every module, plugin, and
  font is weight you must justify up front, because you cannot optimize bloat away later
  without a rebuild. See [performance](10-performance.md).
- **Verify on the rendered front end.** The Visual Builder renders differently from the
  live page. A change is not done until confirmed in the front end at every breakpoint.

## Best Practices

- Decide **Divi 4 (shortcode) vs Divi 5 (JSON)** before writing anything; their content
  formats and module APIs differ and guidance does not transfer blindly.
- Set global styles and Theme Builder templates **before** building individual pages, so
  pages inherit rather than redefine.
- Treat every repeated style as a **preset**; treat every repeated section as a **global**
  layout. If you paste the same thing twice, stop and centralize it.
- Enqueue custom CSS/JS through `wp_enqueue_style`/`wp_enqueue_script` in the child theme
  with declared dependencies — never paste `<script>`/`<style>` into a Code module.
- Budget page weight and request count as you build; do not "add now, optimize later".
- Keep a short project record of global colors, presets, and template locations so the
  next editor inherits your decisions instead of guessing.

## Examples

**Good Example** — customization added the update-safe, reusable way

```php
// child-theme/functions.php — survives Divi updates, loaded once, versioned.
add_action( 'wp_enqueue_scripts', function () {
  wp_enqueue_style(
    'site-custom',
    get_stylesheet_directory_uri() . '/assets/custom.css',
    array( 'divi-style' ),                  // depends on the parent stylesheet
    wp_get_theme()->get( 'Version' )        // cache-busts on each release
  );
} );
// Buttons use ONE Divi preset, so a brand color change is a single edit sitewide.
```

**Bad Example** — parent-theme edit plus per-module inline CSS

```css
/* Edited directly in the Divi PARENT theme's style.css and pasted into the
   Advanced > Custom CSS box of 40 separate button modules. The next Divi update
   wipes the parent edit, and a color change now means editing 40 modules by hand,
   each invisible until you open it. Both violations are silent until they bite. */
.et_pb_button_0 { background: #1a73e8 !important; border-radius: 8px; }
```

## Common Mistakes

- Editing the Divi parent theme, so the next update erases the work.
- Styling modules inline instead of with presets, multiplying maintenance surface.
- Rebuilding headers/footers per page instead of once in the Theme Builder.
- Hand-editing `post_content` shortcodes/JSON in the database, corrupting the layout.
- Adding a plugin for an effect Divi already ships, inflating CSS/JS weight.
- Declaring a change "done" from the Visual Builder without checking the front end.

## Production Tips

- Keep global styles, presets, and Theme Builder templates under version control via
  Divi's export, and include them in every backup. See [deployment](22-deployment.md).
- Audit unused presets and Code modules periodically; dead styles still ship to browsers.
- Pin the Divi version and test updates on staging before production, because Divi
  updates can change module markup and CSS.

## AI Review Checklist

- Is the Divi version (4 vs 5) identified before any edit or code is written?
- Is all PHP/CSS/JS in a child theme and enqueued, never in the parent or a Code module?
- Are repeated styles driven by presets/globals rather than per-module inline CSS?
- Are global styles and Theme Builder templates set before individual pages were built?
- Was the change verified on the rendered front end at every breakpoint?
- Was performance (weight, requests) considered during the build, not deferred?

## Related

- `knowledge/divi/24-best-practices.md`
- `knowledge/divi/01-architecture.md`
- `knowledge/divi/10-performance.md`
- `knowledge/divi/16-wordpress-hooks.md`
- `knowledge/divi/09-custom-css.md`
