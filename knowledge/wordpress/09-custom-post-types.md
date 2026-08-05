---
id: wordpress/09-custom-post-types
topic: wordpress
slug: custom-post-types
title: "Custom Post Types"
type: doc
order: 9
status: ready
tags: [wordpress, custom-post-types, supports, show_in_rest, init, flush_rewrite_rules, register_post_type, WP_Query]
related: [wordpress/10-taxonomies, wordpress/11-metadata, wordpress/12-queries, wordpress/18-rest-api, wordpress/20-users-and-capabilities, wordpress/13-template-hierarchy]
when_to_use: "Read before registering a custom post type — deciding whether content needs one, choosing arguments, or fixing 404s and missing REST support."
---
# Custom Post Types

## Purpose

This document defines how to model content as a custom post type (CPT): when a CPT is the
right container, which registration arguments actually matter, and the failure modes —
404s, missing editor features, invisible REST endpoints — that follow from getting them
wrong.

A post type is a long-lived content contract. Its slug is stored in the database on every
row, appears in every URL, and is referenced by every query. Changing it later is a
migration, not an edit.

---

## Core Principle

Reach for a custom post type when the content has its own lifecycle, its own archive, or its
own permissions. Reach for a taxonomy when it classifies existing content, and for post meta
when it is an attribute of a single item.

| Requirement | Correct container |
|---|---|
| "Case studies with their own listing page" | Custom post type |
| "Case studies grouped by industry" | Taxonomy on that post type |
| "Each case study has a client name and date" | Post meta |
| "A one-off About page" | A regular page |
| "Site-wide contact email" | Option, not a post |

A CPT that holds a single row is almost always an option or a settings page in disguise.

---

## Registration

Register on `init`. Earlier, and the required APIs are not loaded; later, and rewrite rules
and REST routes are already resolved.

**Good Example** — explicit arguments, editor and REST enabled

```php
add_action( 'init', 'myplugin_register_event_post_type' );

function myplugin_register_event_post_type() {
	$labels = array(
		'name'               => _x( 'Events', 'post type general name', 'myplugin' ),
		'singular_name'      => _x( 'Event', 'post type singular name', 'myplugin' ),
		'add_new_item'       => __( 'Add New Event', 'myplugin' ),
		'edit_item'          => __( 'Edit Event', 'myplugin' ),
		'search_items'       => __( 'Search Events', 'myplugin' ),
		'not_found'          => __( 'No events found.', 'myplugin' ),
	);

	register_post_type(
		'myplugin_event',                      // prefixed: the slug is a global namespace
		array(
			'labels'       => $labels,
			'public'       => true,            // visible on the front end and queryable
			'has_archive'  => 'events',        // /events/ listing; true would use the slug
			'rewrite'      => array( 'slug' => 'events', 'with_front' => false ),
			'menu_icon'    => 'dashicons-calendar-alt',
			'menu_position'=> 20,

			// Without 'editor' there is no block editor; without 'custom-fields'
			// meta is not exposed to the editor at all.
			'supports'     => array( 'title', 'editor', 'excerpt', 'thumbnail', 'revisions', 'custom-fields' ),

			// Required for the block editor and any headless client.
			'show_in_rest' => true,
			'rest_base'    => 'events',

			'taxonomies'   => array( 'myplugin_event_type' ),
		)
	);
}
```

**Bad Example** — defaults left implicit, slug unprefixed

```php
add_action( 'init', function () {
	register_post_type( 'event', array(       // unprefixed: collides with other plugins
		'public' => true,
		// no 'supports' → defaults to title + editor only; no thumbnail, no revisions
		// no 'show_in_rest' → classic editor only, invisible to the REST API
		// no 'has_archive' → /events/ is a 404, and nobody knows why
	) );
} );
```

---

## The Arguments That Matter

- **`public`** is a convenience that sets four others (`show_ui`, `publicly_queryable`,
  `show_in_nav_menus`, `exclude_from_search`). Set it deliberately — a private data type
  should be `'public' => false, 'show_ui' => true`, not `public` with patches.
- **`show_in_rest`** controls both the block editor and REST availability. Its absence is the
  single most common "why is this stuck on the classic editor" cause.
- **`supports`** is not additive with defaults. Declaring it replaces them, so anything
  omitted is off — including `revisions`, `thumbnail`, and `custom-fields`.
- **`has_archive`** creates the listing route. A CPT with archive content but
  `has_archive => false` produces a 404 that looks like a template problem.
- **`hierarchical => true`** makes the type behave like pages (parents, menu order) and
  changes which templates and admin UI apply. It also makes large data sets expensive — the
  parent dropdown loads every post.
- **`capability_type` / `map_meta_cap`** define who can edit what — see
  [Users and Capabilities](20-users-and-capabilities.md).

---

## Rewrite Rules and the 404 Problem

Registering a post type does not create its URLs. Rewrite rules are cached in the database,
so a new type 404s until they are regenerated.

```php
// Correct: flush ONCE, on activation, after the type is registered.
register_activation_hook( __FILE__, 'myplugin_activate' );

function myplugin_activate() {
	myplugin_register_event_post_type();   // must run before the flush
	flush_rewrite_rules();
}

register_deactivation_hook( __FILE__, 'flush_rewrite_rules' );
```

**Never** call `flush_rewrite_rules()` on `init`. It rewrites the whole rules option on
every request — one of the most expensive things a plugin can do, and a well-known cause of
sitewide slowdowns.

---

## Registering in a Plugin, Not a Theme

Content outlives presentation. A post type registered in `functions.php` disappears when the
theme changes, leaving orphaned rows in `wp_posts` that no query can reach.

```
theme/functions.php   → presentation: menus, image sizes, template behavior
plugin/               → content model: post types, taxonomies, meta, business logic
```

This is the clearest practical application of the theme/plugin split described in
[Project Structure](02-project-structure.md).

---

## Querying a Custom Post Type

`get_posts()` and `WP_Query` default to `post_type => 'post'`. Anything custom must be named
explicitly — including in a `pre_get_posts` filter or a REST request.

```php
$events = new WP_Query(
	array(
		'post_type'      => 'myplugin_event',
		'post_status'    => 'publish',
		'posts_per_page' => 10,
		'no_found_rows'  => true,       // skip the COUNT query when not paginating
	)
);
```

See [Queries](12-queries.md) for the arguments that determine whether that query is cheap or
expensive.

---

## Changing a Post Type Later

The slug is stored in `wp_posts.post_type` for every row. Renaming it in code orphans all
existing content — the posts remain in the database but no query returns them.

```php
// Migration, run once via WP-CLI — never as a hook on a normal request.
global $wpdb;
$wpdb->update(
	$wpdb->posts,
	array( 'post_type' => 'myplugin_event' ),
	array( 'post_type' => 'event' )
);

// Object caches still hold the old rows.
wp_cache_flush();
flush_rewrite_rules();
```

Choosing a prefixed, stable slug at registration time is considerably cheaper than this.

---

## Common Mistakes

- **Unprefixed slugs** (`event`, `product`, `team`) that collide with plugins and themes.
- **Registering in the theme**, so content vanishes with a theme switch.
- **`flush_rewrite_rules()` on `init`**, degrading every request on the site.
- **Missing `show_in_rest`**, leaving the type on the classic editor and invisible to
  headless clients.
- **Declaring `supports` without `revisions` or `thumbnail`** and later concluding WordPress
  "lost" them.
- **A CPT used for a single record** that should have been an option.
- **Post-type slugs longer than 20 characters** — `register_post_type()` rejects them,
  because the database column is `varchar(20)`.
- **Forgetting `post_type` in queries**, then debugging why the loop is empty.

---

## Verification Checklist

- Is the slug prefixed, under 20 characters, and final?
- Is registration in a plugin rather than the theme?
- Is `show_in_rest` set if the editor or any API client needs the type?
- Does `supports` list everything required, including `thumbnail` and `revisions`?
- Is `has_archive` set when the type needs a listing page, with rewrite rules flushed on
  activation only?
- Are capabilities defined if this content should not be editable by every author?
- Do all queries for this content name `post_type` explicitly?

---

## Summary

A custom post type is a permanent contract expressed through registration arguments. Prefix
the slug, register it from a plugin on `init`, declare `supports` and `show_in_rest`
explicitly, and flush rewrite rules only on activation.

## Related

- `knowledge/wordpress/10-taxonomies.md`
- `knowledge/wordpress/11-metadata.md`
- `knowledge/wordpress/12-queries.md`
- `knowledge/wordpress/18-rest-api.md`
- `knowledge/wordpress/20-users-and-capabilities.md`
- `knowledge/wordpress/13-template-hierarchy.md`
