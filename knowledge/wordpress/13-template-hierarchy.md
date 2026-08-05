---
id: wordpress/13-template-hierarchy
topic: wordpress
slug: template-hierarchy
title: "Template Hierarchy"
type: doc
order: 13
status: ready
tags: [wordpress, template-hierarchy]
related: [wordpress/14-theme-development, wordpress/17-block-themes, wordpress/09-custom-post-types, wordpress/12-queries, wordpress/01-wordpress-architecture]
when_to_use: "Read before creating or overriding a theme template — choosing the right filename, adding template parts, or debugging which template WordPress actually loaded."
---
# Template Hierarchy

## Purpose

This document defines how WordPress chooses which template file renders a request, how to
name templates so the right one is selected without conditional logic, and how to override
templates from a child theme or a plugin.

The hierarchy is a naming convention, not an API. Getting the filename right replaces a page
of `if ( is_singular( 'event' ) )` branching with a file that WordPress finds on its own.

---

## Core Principle

WordPress picks the **most specific matching filename**, falling back until it reaches
`index.php`. Specificity is expressed in the name, not in code.

```
Request: /events/summer-workshop/   (post type: myplugin_event, slug: summer-workshop)

single-myplugin_event-summer-workshop.php   ← most specific
single-myplugin_event.php
single.php
singular.php
index.php                                   ← always exists; the final fallback
```

A theme that renders everything through `index.php` with conditionals is fighting a system
designed to remove those conditionals.

---

## The Chains Worth Memorizing

**Single post**

```
single-{post-type}-{slug}.php → single-{post-type}.php → single.php → singular.php → index.php
```

**Page**

```
{custom-template}.php → page-{slug}.php → page-{id}.php → page.php → singular.php → index.php
```

**Post type archive**

```
archive-{post-type}.php → archive.php → index.php
```

**Taxonomy term**

```
taxonomy-{taxonomy}-{term}.php → taxonomy-{taxonomy}.php → taxonomy.php → archive.php → index.php
```

**Category / tag** (taxonomies with their own chain)

```
category-{slug}.php → category-{id}.php → category.php → archive.php → index.php
tag-{slug}.php → tag-{id}.php → tag.php → archive.php → index.php
```

**Front page and blog index** — the pair that causes the most confusion:

```
front-page.php  → used for BOTH a static front page and the blog index, if present
home.php        → the blog post index (whether at / or at /blog/)
page.php        → a static front page, when front-page.php does not exist
```

If a static front page renders the blog list, `front-page.php` exists and is winning. That is
the answer to that particular bug almost every time.

**Others**

```
404.php · search.php · author-{nicename}.php → author.php · date.php · attachment.php
```

---

## Template Parts

Split templates into parts so markup is written once. `get_template_part()` is
child-theme-aware and silently does nothing if the file is missing.

```php
// Loads content-event.php, falling back to content.php.
get_template_part( 'template-parts/content', get_post_type() );

// Pass data (WordPress 5.5+); do not rely on globals or `set_query_var()`.
get_template_part( 'template-parts/card', 'event', array( 'featured' => true ) );
```

In the part, the third argument arrives as `$args`:

```php
<?php
// template-parts/card-event.php
$featured = ! empty( $args['featured'] );
?>
<article class="card <?php echo $featured ? 'card--featured' : ''; ?>">
	<h3><?php the_title(); ?></h3>
</article>
```

---

## Overriding Templates

**From a child theme** — place a file with the same relative path; the child wins:

```
parent-theme/single-myplugin_event.php
child-theme/single-myplugin_event.php     ← used instead
```

**From a plugin** — a plugin cannot add to the hierarchy directly, so filter it. The correct
pattern also lets the theme override the plugin's version:

```php
add_filter( 'template_include', 'myplugin_event_template' );

function myplugin_event_template( $template ) {
	if ( ! is_singular( 'myplugin_event' ) ) {
		return $template;
	}

	// Let the theme win if it provides its own template.
	$theme_template = locate_template( array( 'single-myplugin_event.php' ) );
	if ( $theme_template ) {
		return $theme_template;
	}

	return plugin_dir_path( __FILE__ ) . 'templates/single-event.php';
}
```

`locate_template()` searches the child theme, then the parent — which is why the plugin
should call it rather than checking file paths itself.

---

## Custom Page Templates

A page template is selectable in the editor when it declares a header comment:

```php
<?php
/**
 * Template Name: Full Width Landing
 * Template Post Type: page, myplugin_event
 */

get_header();
// …
get_footer();
```

`Template Post Type` extends the template beyond pages; without it, the template only appears
for pages.

---

## Child Theme Path Functions

The most common child-theme bug is a path function that silently resolves to the parent:

```php
get_stylesheet_directory()      // CHILD theme directory  — use for your own files
get_template_directory()        // PARENT theme directory — use for parent assets

get_stylesheet_directory_uri()  // child URL
get_template_directory_uri()    // parent URL
```

In a theme with no child, both return the same path — so the mistake is invisible until
someone creates a child theme, and then every include breaks at once.

---

## Debugging Which Template Loaded

```php
// Log the chosen template on every request (development only).
add_filter( 'template_include', function ( $template ) {
	error_log( 'Template: ' . $template );
	return $template;
}, PHP_INT_MAX );   // last, so it reports the final decision
```

`template_include` at maximum priority reports what actually rendered, after every other
plugin has had its turn. The Query Monitor plugin shows the same information plus the full
candidate list — see [Debugging](28-debugging.md).

---

## Block Themes Change This

In a block theme the hierarchy still applies, but the files are HTML templates under
`templates/` and parts under `parts/`, and the database copy of an edited template takes
precedence over the file:

```
templates/single-myplugin_event.html
templates/archive-myplugin_event.html
parts/header.html
```

See [Block Themes](17-block-themes.md). A classic theme and a block theme should not be mixed
in one project — pick one model.

---

## Examples

**Good Example** — specificity expressed in filenames

```text
wp-content/themes/acme/
├── single-myplugin_event.php     one event
├── archive-myplugin_event.php    the event archive
├── taxonomy-event_type.php       one event-type term
├── template-parts/
│   ├── event/card.php
│   └── event/meta.php
└── index.php                     final fallback, stays short
```

```php
<?php
// single-myplugin_event.php — no conditionals about "which page is this".
get_header();

while ( have_posts() ) :
	the_post();
	get_template_part( 'template-parts/event/meta' );
	the_content();
endwhile;

get_footer();
```

Adding a distinct layout for one event type means adding
`single-myplugin_event-summer-workshop.php`. Nothing existing is edited.

**Bad Example** — one template plus a conditional ladder

```php
<?php
// index.php — the hierarchy is switched off and reimplemented by hand.
get_header();

if ( is_singular( 'myplugin_event' ) ) {
	include get_template_directory() . '/parts/event-single.php';
} elseif ( is_post_type_archive( 'myplugin_event' ) ) {
	include get_template_directory() . '/parts/event-archive.php';
} elseif ( is_tax( 'event_type' ) ) {
	include get_template_directory() . '/parts/event-tax.php';
} else {
	include get_template_directory() . '/parts/default.php';
}

get_footer();
```

Every new content type extends the ladder, a child theme can no longer override one view by
filename, and `get_template_directory()` hardcodes the parent theme so child overrides are
skipped entirely.

---

## Common Mistakes

- **`index.php` with conditionals** instead of correctly named templates.
- **`front-page.php` present but unexpected**, overriding `home.php` for the blog index.
- **`get_template_directory()` in a child theme**, silently loading parent files.
- **Editing the parent theme** instead of overriding in a child.
- **Missing `get_header()` / `get_footer()`** in a custom template, producing a page with no
  `wp_head()` — so no styles, no scripts, and no plugin output.
- **A plugin returning its template unconditionally**, preventing any theme override.
- **`include` instead of `get_template_part()`**, bypassing child-theme resolution.
- **Post type registered with `has_archive => false`** while `archive-{type}.php` exists —
  the file is never reached.

---

## Verification Checklist

- Is the template named so WordPress selects it without conditional logic?
- For a child theme, do all path calls use `get_stylesheet_directory()` where intended?
- Does every custom template call `get_header()` and `get_footer()` (or output `wp_head()` /
  `wp_footer()`)?
- Do plugin templates defer to a theme override via `locate_template()`?
- Are repeated blocks of markup extracted into template parts?
- Is `front-page.php` present intentionally, given how the site's front page is configured?

---

## Summary

The hierarchy resolves a request to a file by name, from most specific to `index.php`. Name
templates correctly instead of branching, override through a child theme, and have plugins
defer to the theme when it supplies its own version.

## Related

- `knowledge/wordpress/14-theme-development.md`
- `knowledge/wordpress/17-block-themes.md`
- `knowledge/wordpress/12-queries.md`
- `knowledge/wordpress/01-wordpress-architecture.md`
