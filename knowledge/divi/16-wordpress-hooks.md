---
id: divi/16-wordpress-hooks
topic: divi
slug: wordpress-hooks
title: "WordPress Hooks"
type: doc
order: 16
status: ready
tags: [divi, wordpress-hooks, remove_filter, wp_enqueue_scripts, init, add_filter, remove_action, template_redirect]
related: [divi/04-custom-modules, divi/15-custom-fields, divi/01-architecture, divi/10-performance, divi/19-security]
when_to_use: "Read before adding any PHP that hooks into WordPress or Divi to change behavior or output."
---
# WordPress Hooks

## Purpose

This document defines how to extend **Divi** and **WordPress** through **hooks** — `actions`
and `filters` — instead of editing core, theme, or plugin files. It is written so an agent can
add behavior to a Divi site in a way that survives updates, runs at the right time, and does not
leak performance or security problems.

Hooks are WordPress's extension contract: an **action** lets you *do* something at a point in the
lifecycle (`init`, `wp_enqueue_scripts`, `save_post`); a **filter** lets you *change* a value
before it is used (`the_content`, `body_class`, `et_pb_module_shortcode_attributes`). All correct
Divi customization goes through hooks placed in a **child theme** or a small plugin — never by
modifying the Divi parent theme.

## Why It Matters

Editing the Divi parent theme or a plugin file "works" until the next update overwrites it, silently
reverting the change and any security fix baked into it. Hooks exist precisely to avoid that: code in
a child theme is untouched by parent-theme updates. But hooks are also easy to misuse — registering
work on the wrong hook runs it too early (before Divi is loaded) or on every request (a performance
tax on the whole site), and unremoved or mis-prioritized callbacks produce heisenbugs that only appear
under certain page types. Because a hook can run globally, one careless callback degrades or breaks the
entire site, so hooks demand the same care as the code they modify.

## Core Principles

- **Never edit core, parent theme, or plugin files.** Put customizations in a child theme's
  `functions.php` or a dedicated small plugin, so updates cannot wipe them.
- **Choose the correct hook and timing.** Match the action to the lifecycle stage it needs
  (`init` for registration, `wp_enqueue_scripts` for assets, `template_redirect` for request-time).
  Running too early means Divi/WordPress isn't ready; too broad means it runs where it shouldn't.
- **Filters must return.** A filter callback that forgets to `return` the (possibly modified) value
  blanks whatever it filtered. Always return the value, modified or not.
- **Scope the work.** Guard callbacks with conditions (`is_admin()`, `is_singular()`, post type) so
  they only run where needed, not on every page load.
- **Match `add_filter`/`remove_filter` signatures.** Priority and accepted-arg count must match to
  remove a callback or to receive the arguments you expect.

## Best Practices

- Keep all PHP customization in a child theme (or feature plugin) under version control. This is the
  single most important rule for a maintainable Divi site.
- Enqueue scripts and styles with `wp_enqueue_scripts` and `wp_enqueue_script/style` — never
  hard-code `<script>`/`<link>` tags in a Code module or `header.php`. Enqueuing handles
  dependencies, versioning (cache-busting), and load order.
- Use Divi-specific filters where they exist (e.g. `et_pb_module_shortcode_attributes`,
  `et_builder_*`) to alter module behavior, rather than post-processing rendered HTML.
- Set an explicit priority when order matters, and pass the accepted-args count when your callback
  needs more than the first argument.
- Prefer named functions or invokable classes over sprawling closures so you can `remove_action`/
  `remove_filter` later and so hooks are testable.
- Register post types, taxonomies, and shortcodes on `init`; do request-conditional logic on
  `template_redirect` or `wp`, not on `init` (too early to know the query).
- Sanitize input and escape output inside hook callbacks — a hook is not a trust boundary. See
  [custom-fields](15-custom-fields.md) and [security](19-security.md).

## Examples

**Good Example** — child-theme hook, correct timing, escaped, scoped

```php
// child theme functions.php — enqueue on the right hook, with a version for
// cache-busting, only on the front end.
add_action( 'wp_enqueue_scripts', function () {
    if ( is_admin() ) {
        return; // don't load front-end assets in wp-admin
    }
    wp_enqueue_style(
        'site-custom',
        get_stylesheet_directory_uri() . '/assets/custom.css',
        [ 'divi-style' ],          // load after Divi's stylesheet
        filemtime( get_stylesheet_directory() . '/assets/custom.css' ) // cache-bust
    );
} );

// A filter that ALWAYS returns the value it received.
add_filter( 'body_class', function ( $classes ) {
    if ( is_front_page() ) {
        $classes[] = 'is-home';
    }
    return $classes; // returning is mandatory, modified or not
} );
```

**Bad Example** — parent-theme edit, filter that drops its value

```php
// Editing Divi's parent header.php directly — wiped on the next Divi update,
// taking any fix with it.
echo '<script src="/wp-content/themes/Divi/custom.js"></script>'; // also unversioned, unmanaged

add_filter( 'the_content', function ( $content ) {
    do_something( $content );
    // No return: every post body renders EMPTY across the whole site.
} );
```

## Common Mistakes

- Editing the Divi parent theme or a plugin file, so updates silently revert the change.
- Filter callbacks that don't `return`, blanking titles, content, or class lists site-wide.
- Registering work on the wrong hook — too early (Divi not loaded) or too broad (runs everywhere).
- Hard-coding `<script>`/`<link>` tags instead of enqueuing, breaking dependencies and cache-busting.
- Mismatched priority/arg-count, so `remove_action`/`remove_filter` silently no-ops or args arrive missing.
- Anonymous closures on shared hooks that can never be removed or overridden later.
- Treating a hook callback as trusted, skipping input sanitization and output escaping.

## Production Tips

- When a plugin/Divi hook "won't remove", confirm you're calling `remove_action`/`remove_filter`
  with the *exact* callback, priority, and arg count it was added with — all must match.
- Profile hooks that run on every request (query filters, `init` work); move heavy logic behind
  conditions or caching. Broad hooks are a common source of slow Divi sites. See [performance](10-performance.md).
- Keep customizations in a feature plugin (not just the child theme) when they must survive a theme
  switch — hooks in a plugin are theme-independent.

## AI Review Checklist

- Is the customization in a child theme or plugin, never the parent theme/core/plugin files?
- Does every filter callback return the value (modified or not)?
- Is each callback on the correct hook for its timing, and scoped to where it should run?
- Are assets enqueued via `wp_enqueue_scripts` with dependencies and a cache-busting version?
- Do `add`/`remove` calls share matching priority and accepted-arg counts?
- Is input sanitized and output escaped inside the callback?

## Related

- `knowledge/divi/04-custom-modules.md`
- `knowledge/divi/15-custom-fields.md`
- `knowledge/divi/01-architecture.md`
- `knowledge/divi/10-performance.md`
- `knowledge/divi/19-security.md`
