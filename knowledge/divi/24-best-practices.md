---
id: divi/24-best-practices
topic: divi
slug: best-practices
title: "Divi Best Practices"
type: doc
order: 24
status: ready
tags: [divi, best-practices, wp_enqueue_style, wp_get_theme, get_stylesheet_directory_uri, add_action, post_content, wp_enqueue_script]
related: [divi/00-overview, divi/09-custom-css, divi/10-performance, divi/06-global-elements, divi/16-wordpress-hooks]
when_to_use: "Read before starting or reviewing any Divi build to apply the conventions that keep a site fast, maintainable, and update-safe."
---
# Divi Best Practices

## Purpose

This document collects the day-to-day conventions that separate a Divi site a team can
maintain for years from one that rots after the first client edit. It is the practical
distillation of the deeper docs — [architecture](01-architecture.md),
[performance](10-performance.md), [custom-css](09-custom-css.md) — into rules an agent
can apply while building.

These are not style preferences. Each rule prevents a specific, recurring failure mode
in Divi projects: layout corruption, update wipeouts, CSS bloat, or unmaintainable
copy-paste sprawl.

## Why It Matters

Divi's low-friction visual editing is exactly what makes it easy to build an
unmaintainable site. Nothing stops you from adding inline CSS to a hundred modules,
building the same header on every page, or editing the parent theme. It all works — until
an update ships, a client opens the Visual Builder, or the page weight crosses the point
where Core Web Vitals fail. Best practices exist because Divi will not enforce them for
you; the discipline has to come from the builder.

## Core Principles

- **Reuse beats repetition.** Global modules, presets, and the [Theme Builder](02-theme-builder.md)
  let one change propagate everywhere. Duplication is the primary source of Divi rot.
- **Never touch the parent theme.** All PHP, CSS, and functions live in a child theme, so
  a Divi update cannot wipe your work. See [wordpress-hooks](16-wordpress-hooks.md).
- **Style at the highest level that works.** Prefer global presets and the theme's Design
  settings over per-module custom CSS. Per-module CSS is the last resort, not the first.
- **Keep content in the builder's model.** Edit through the Visual Builder or documented
  import/export — never hand-edit `post_content` shortcodes/JSON in the database.
- **Fewer modules, fewer requests.** Every module and every third-party plugin adds CSS,
  JS, and DOM. Build the effect with what Divi already ships before adding a plugin.

## Best Practices

- Establish **global colors**, fonts, and spacing in the Theme Builder and Divi's Design
  settings *before* building pages, so pages inherit instead of redefining.
- Use **presets** for every repeated module style (buttons, headings, cards). Changing the
  preset updates every instance; inline styling does not.
- Put shared headers, footers, and post templates in the **Theme Builder** once — never
  rebuild them per page.
- Keep custom CSS in **one place**: the child theme stylesheet or Divi's global "Custom
  CSS" box, organized and commented — not scattered across module Advanced tabs.
- Name and save reusable sections as **global** layouts when they appear on more than one
  page; edit the global, and all instances update.
- Enable Divi's **performance features** (dynamic CSS, dynamic module framework, deferred
  jQuery, critical CSS) and set an image strategy — lazy-load and correct sizes.
- Load custom scripts and styles through `wp_enqueue_script`/`wp_enqueue_style` in the
  child theme, with dependencies declared — never paste `<script>` tags into a Code module.
- Test every change at each **responsive breakpoint** and in the front end, not only inside
  the builder, which renders differently. See [responsive-design](11-responsive-design.md).

## Examples

**Good Example** — one preset, styled centrally, enqueued properly

```php
// child-theme/functions.php — custom CSS/JS added the update-safe way
add_action( 'wp_enqueue_scripts', function () {
  // Loads only on the front end, versioned for cache-busting, in the child theme
  // so a Divi update never removes it.
  wp_enqueue_style(
    'site-custom',
    get_stylesheet_directory_uri() . '/assets/custom.css',
    array( 'divi-style' ),                 // depends on the parent stylesheet
    wp_get_theme()->get( 'Version' )
  );
} );
```

Buttons use a single Divi **preset**, so a brand color change is one edit that
propagates to every button on the site.

**Bad Example** — per-module inline CSS, duplicated everywhere

```css
/* Pasted into the Advanced > Custom CSS box of ONE button module.
   Repeated by hand on 40 other buttons. A color change now means
   editing 41 modules — and each is invisible until you open it. */
.et_pb_button_0 { background: #1a73e8 !important; border-radius: 8px; }
```

## Common Mistakes

- Styling each module inline instead of using presets, multiplying maintenance surface.
- Rebuilding the header/footer on every page rather than once in the Theme Builder.
- Editing the Divi parent theme, so the next update erases the change.
- Pasting `<script>`/`<style>` into Code modules instead of enqueuing in the child theme.
- Reaching for a plugin for an effect Divi already provides, adding CSS/JS weight.
- Only checking the Visual Builder view, which differs from the rendered front end.

## Production Tips

- Keep a short project README listing global colors, presets, Theme Builder templates, and
  where custom CSS lives, so the next editor does not reinvent them.
- Export the layout library and Theme Builder templates as part of every backup.
- Audit unused presets and Code modules periodically; dead styles still ship to the browser.

## AI Review Checklist

- Are repeated styles driven by presets/global modules, not per-module inline CSS?
- Are headers, footers, and templates defined once in the Theme Builder?
- Is all PHP/CSS/JS in a child theme and enqueued, never in the parent or a Code module?
- Are global colors/fonts/spacing set before individual pages were built?
- Were performance features enabled and the change verified on the front end at each breakpoint?

## Related

- `knowledge/divi/00-overview.md`
- `knowledge/divi/06-global-elements.md`
- `knowledge/divi/09-custom-css.md`
- `knowledge/divi/10-performance.md`
- `knowledge/divi/16-wordpress-hooks.md`
