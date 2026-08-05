---
id: wordpress/14-theme-development
topic: wordpress
slug: theme-development
title: "Theme Development"
type: doc
order: 14
status: ready
tags: [wordpress, theme-development]
related: [wordpress/13-template-hierarchy, wordpress/17-block-themes, wordpress/02-project-structure, wordpress/24-internationalization, wordpress/05-performance, wordpress/16-block-editor]
when_to_use: "Read before building or modifying a theme — creating a child theme, enqueuing assets, declaring theme support, or registering menus and image sizes."
---
# Theme Development

## Purpose

This document defines how to build and modify WordPress themes: the file contract a theme
must satisfy, how to enqueue assets so caching and dependencies work, and what belongs in a
theme rather than a plugin.

A theme owns presentation. Every time content modelling or business logic moves into a theme,
that logic disappears the day the site is redesigned.

---

## Core Principle

**Themes are presentation. Plugins are behavior.**

The test: if switching the theme should delete this, it belongs in the theme. Post types,
taxonomies, shortcodes, REST endpoints, and integrations all fail that test — see
[Project Structure](02-project-structure.md).

| Belongs in the theme | Belongs in a plugin |
|---|---|
| Templates and template parts | Post types and taxonomies |
| Styles and front-end scripts | Shortcodes and blocks |
| Menu locations, image sizes | REST endpoints |
| `add_theme_support()` | Third-party integrations |
| Widget areas | Business logic, cron jobs |

---

## Never Edit a Parent Theme

Edits to a third-party theme are erased by its next update. Use a child theme.

**Good Example** — a child theme that enqueues the parent stylesheet correctly

```css
/* child-theme/style.css */
/*
Theme Name:  Acme Child
Template:    acme            <- directory name of the parent, exactly
Version:     1.0.0
Text Domain: acme-child
*/
```

```php
<?php
// child-theme/functions.php
add_action( 'wp_enqueue_scripts', 'acme_child_enqueue_styles' );

function acme_child_enqueue_styles() {
	$parent = 'acme-parent-style';

	wp_enqueue_style(
		$parent,
		get_template_directory_uri() . '/style.css',       // PARENT directory
		array(),
		wp_get_theme( get_template() )->get( 'Version' )
	);

	wp_enqueue_style(
		'acme-child-style',
		get_stylesheet_directory_uri() . '/style.css',     // CHILD directory
		array( $parent ),                                   // load after the parent
		filemtime( get_stylesheet_directory() . '/style.css' )   // cache-busts on change
	);
}
```

**Bad Example**

```php
// @import is render-blocking and serializes the downloads.
// Hardcoded version strings go stale, so browsers serve outdated CSS after a deploy.
wp_enqueue_style( 'child', get_template_directory_uri() . '/style.css', array(), '1.0' );
// ^ get_template_directory_uri() in a child theme points at the PARENT: the child's own
//   stylesheet is never loaded, and the bug is invisible until someone looks.
```

---

## Enqueuing Assets

Never print `<script>` or `<link>` tags directly. The queue exists so dependencies resolve,
duplicates collapse, and plugins can deregister or replace assets.

```php
add_action( 'wp_enqueue_scripts', 'acme_enqueue_assets' );

function acme_enqueue_assets() {
	$dir = get_stylesheet_directory();
	$uri = get_stylesheet_directory_uri();

	wp_enqueue_script(
		'acme-app',
		$uri . '/assets/js/app.js',
		array(),                                  // dependencies, e.g. array( 'wp-i18n' )
		filemtime( $dir . '/assets/js/app.js' ),  // version from mtime, not a literal
		array(
			'strategy'  => 'defer',               // WordPress 6.3+
			'in_footer' => true,
		)
	);

	// Pass data to the script — never echo a <script> block with inline JSON.
	wp_localize_script(
		'acme-app',
		'acmeSettings',
		array(
			'restUrl' => esc_url_raw( rest_url( 'acme/v1/' ) ),
			'nonce'   => wp_create_nonce( 'wp_rest' ),
		)
	);

	// Conditional loading: do not ship the map bundle on every page.
	if ( is_singular( 'myplugin_event' ) ) {
		wp_enqueue_script( 'acme-map', $uri . '/assets/js/map.js', array( 'acme-app' ), filemtime( $dir . '/assets/js/map.js' ), true );
	}
}
```

Two rules that prevent most asset bugs: bundle your own copy of a library rather than loading
it from a CDN (version conflicts with plugins are silent and hard to trace), and never
deregister core's jQuery to replace it with a different version — plugins depend on the one
WordPress ships.

---

## Declaring Theme Support

```php
add_action( 'after_setup_theme', 'acme_setup' );

function acme_setup() {
	add_theme_support( 'title-tag' );            // core manages <title>; never hardcode it
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'editor-styles' );
	add_theme_support( 'align-wide' );
	add_theme_support( 'custom-logo', array( 'height' => 60, 'flex-width' => true ) );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );

	register_nav_menus(
		array(
			'primary' => __( 'Primary Menu', 'acme' ),
			'footer'  => __( 'Footer Menu', 'acme' ),
		)
	);

	add_image_size( 'acme-card', 640, 400, true );   // hard crop

	load_theme_textdomain( 'acme', get_stylesheet_directory() . '/languages' );
}
```

`add_image_size()` only affects images uploaded *after* it is registered. Existing media needs
regeneration:

```bash
wp media regenerate --image_size=acme-card --yes
```

---

## `functions.php` Discipline

`functions.php` loads on every request, front end and admin. It is a bootstrap file, not a
place to implement features.

```php
<?php
// Good: functions.php wires things up and delegates.
require_once get_stylesheet_directory() . '/inc/setup.php';
require_once get_stylesheet_directory() . '/inc/assets.php';
require_once get_stylesheet_directory() . '/inc/template-tags.php';
```

Never produce output from `functions.php`. A stray blank line after the closing `?>` sends
headers early and breaks redirects, cookies, and the REST API with the notorious "headers
already sent" error. Omit the closing tag entirely in PHP-only files.

---

## Escaping in Templates

Templates output user- and editor-supplied data on every line. Escape at the point of output:

```php
<article <?php post_class(); ?>>
	<h2><?php echo esc_html( get_the_title() ); ?></h2>

	<a href="<?php echo esc_url( get_permalink() ); ?>">
		<?php echo esc_html__( 'Read more', 'acme' ); ?>
	</a>

	<?php // the_content() is filtered through wp_kses on save; do not double-escape it. ?>
	<div class="entry"><?php the_content(); ?></div>

	<img src="<?php echo esc_url( $img ); ?>" alt="<?php echo esc_attr( $alt ); ?>" />
</article>
```

See [Security](06-security.md) for the full escaping matrix.

---

## Common Mistakes

- **Editing the parent theme** rather than using a child.
- **`get_template_directory()` in a child theme** where the child's own path was meant.
- **`@import` in `style.css`** instead of enqueuing.
- **Hardcoded version strings**, so browsers cache stale CSS after deploys.
- **Printing `<script>` tags** and bypassing the dependency system.
- **Loading jQuery from a CDN** or deregistering core's copy.
- **Registering post types in `functions.php`**, so content disappears with the theme.
- **Output in `functions.php`**, causing "headers already sent".
- **Loading every asset on every page** instead of enqueuing conditionally.
- **Hardcoded `<title>`** instead of `add_theme_support( 'title-tag' )`.
- **Untranslated strings** — see [Internationalization](24-internationalization.md).

---

## Verification Checklist

- Is this a child theme, with the parent untouched?
- Do path calls distinguish `get_stylesheet_directory()` from `get_template_directory()`?
- Are all assets enqueued, with dependencies declared and versions from `filemtime()`?
- Are heavy assets conditionally loaded rather than global?
- Is `functions.php` a bootstrap that produces no output?
- Are theme supports, menus, and image sizes declared on `after_setup_theme`?
- Is every dynamic value in a template escaped for its context?
- Are all user-facing strings wrapped in translation functions with the theme's text domain?

---

## Summary

A theme is presentation and nothing else. Work in a child theme, enqueue assets through the
queue with real versions and declared dependencies, declare support on `after_setup_theme`,
and keep content modelling in plugins where it survives a redesign.

## Related


- `knowledge/wordpress/13-template-hierarchy.md`
- `knowledge/wordpress/17-block-themes.md`
- `knowledge/wordpress/02-project-structure.md`
- `knowledge/wordpress/24-internationalization.md`
- `knowledge/wordpress/05-performance.md`
- `knowledge/wordpress/16-block-editor.md`
