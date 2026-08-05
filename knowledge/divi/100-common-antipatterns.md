---
id: divi/100-common-antipatterns
topic: divi
slug: common-antipatterns
title: "Divi Common Antipatterns"
type: antipatterns
order: 100
status: ready
tags: [divi, common-antipatterns, wp_enqueue_style, wp_get_theme, get_stylesheet_directory_uri, wp_kses, add_action, post_content]
related: [divi/24-best-practices, divi/30-engineering-principles, divi/09-custom-css, divi/10-performance, divi/16-wordpress-hooks]
when_to_use: "Read before or during a Divi build to recognize and avoid the recurring mistakes that corrupt, slow, or break a site."
---
# Divi Common Antipatterns

## Purpose

This document catalogs the recurring Divi mistakes that a reviewer sees again and again,
each paired with why it is wrong and the concrete fix. It is the inverse of
[best-practices](24-best-practices.md): if you catch yourself doing any of these, stop and
apply the fix. An agent should scan this list before building and again during
[review](29-review.md).

## Why It Matters

Every antipattern below "works" at first — that is precisely why it survives to
production. Each one trades a fast first build for a slow, fragile, or unmaintainable site
that bites on the next update, hand-off, or traffic spike. Naming them makes them easy to
refuse.

## Antipatterns

### 1. Editing the Divi parent theme

**Why it is wrong:** Any change to the parent theme's files is overwritten the next time
Divi updates, silently erasing your work — and updates are frequent and often mandatory
for security.

**The fix:** Put all PHP, CSS, JS, and template overrides in a **child theme**. Use hooks
and filters, and enqueue assets from the child. See [wordpress-hooks](16-wordpress-hooks.md).

### 2. Per-module inline CSS duplicated across the site

**Why it is wrong:** Styling forty buttons in each module's Advanced > Custom CSS box means
a single brand change requires forty edits, each invisible until you open the module.
Drift and inconsistency are guaranteed.

**The fix:** Create one **preset** (or global module) and apply it. Change the preset once;
every instance updates. Keep shared CSS in the child theme. See [custom-css](09-custom-css.md).

### 3. Rebuilding headers and footers on every page

**Why it is wrong:** Duplicated headers drift out of sync, and a navigation change becomes
an N-page chore. Pages also miss the change when someone forgets one.

**The fix:** Define the header, footer, and post/archive templates **once** in the
[Theme Builder](02-theme-builder.md); every page inherits them.

### 4. Pasting `<script>` / `<style>` into Code modules

**Why it is wrong:** Inline scripts load without dependency management or versioning, can
run multiple times, are hard to find later, and bypass caching/minification. They also
scatter logic across pages instead of the codebase.

**The fix:** Enqueue via `wp_enqueue_script` / `wp_enqueue_style` in the child theme with
declared dependencies and a version string. See [wordpress-hooks](16-wordpress-hooks.md).

### 5. Hand-editing `post_content` shortcodes or JSON

**Why it is wrong:** Divi's content is a strict structure. A single malformed attribute or
mismatched tag corrupts the layout, and the Visual Builder fails to load with no obvious
cause.

**The fix:** Edit through the Visual Builder, or use Divi's documented import/export. Never
regex-edit the database content field by hand. See [architecture](01-architecture.md).

### 6. Reaching for a plugin Divi already covers

**Why it is wrong:** Each plugin ships its own CSS, JS, and DOM, inflating page weight and
adding update/compatibility surface — often to duplicate a Divi module you already have.

**The fix:** Build the effect with a built-in [module](03-modules.md) first. Add a plugin
only when Divi genuinely cannot do it, and weigh the performance cost. See
[performance](10-performance.md).

### 7. Ignoring Divi's performance features

**Why it is wrong:** Left at defaults, Divi can ship large render-blocking CSS/JS bundles,
failing Core Web Vitals even on a well-designed page.

**The fix:** Enable dynamic CSS, the dynamic module framework, critical CSS, and deferred
jQuery; size, compress, and lazy-load images (except the LCP image). See
[performance](10-performance.md).

### 8. Unescaped output in custom modules

**Why it is wrong:** Echoing user or dynamic data without escaping is a stored-XSS hole —
an attacker's markup runs in every visitor's browser. This passes every visual test.

**The fix:** Sanitize on input and **escape on output** with `esc_html`, `esc_attr`,
`esc_url`, or `wp_kses`. Never trust field values. See [custom-modules](04-custom-modules.md).

### 9. Testing only in the Visual Builder

**Why it is wrong:** The builder renders differently from the live page — spacing,
dynamic content, and third-party scripts behave differently. "Looks right in the builder"
routinely ships broken front ends.

**The fix:** Verify every change on the **rendered front end** at phone, tablet, and
desktop breakpoints. See [responsive-design](11-responsive-design.md).

### 10. Building live instead of on staging

**Why it is wrong:** Editing production directly risks visible breakage and offers no
rollback, and Divi updates can alter module markup mid-session.

**The fix:** Build and update on **staging**, verify, then promote. Keep tested backups of
the database, files, Theme Builder templates, and layouts. See [deployment](22-deployment.md).

## Good vs Bad Example

**Good** — one preset-driven button, enqueued from the child theme

```php
// child-theme/functions.php — update-safe, versioned, dependency-aware.
add_action( 'wp_enqueue_scripts', function () {
  wp_enqueue_style(
    'site-custom',
    get_stylesheet_directory_uri() . '/assets/custom.css',
    array( 'divi-style' ),
    wp_get_theme()->get( 'Version' )
  );
} );
```

**Bad** — inline CSS in a Code module, duplicated by hand

```html
<!-- Pasted into a Code module on every page. No versioning, no dependencies,
     unfindable later, and a color change means editing every page by hand. -->
<style>.et_pb_button_0 { background:#1a73e8 !important; border-radius:8px; }</style>
```

## AI Review Checklist

- Is the work free of all ten antipatterns above, or is each exception justified?
- Are the two highest-severity ones — parent-theme edits and unescaped output — absent?
- Is styling preset/global-driven, code in the child theme, and content edited through the
  builder model?
- Was the result verified on the front end and promoted from staging?

## Related

- `knowledge/divi/24-best-practices.md`
- `knowledge/divi/30-engineering-principles.md`
- `knowledge/divi/09-custom-css.md`
- `knowledge/divi/10-performance.md`
- `knowledge/divi/16-wordpress-hooks.md`
