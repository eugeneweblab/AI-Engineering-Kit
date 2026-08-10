---
id: wordpress/10-taxonomies
topic: wordpress
slug: taxonomies
title: "Taxonomies"
type: doc
order: 10
status: ready
tags: [wordpress, taxonomies, register_taxonomy, wp_set_object_terms, add_action, show_in_rest, WP_Query, WP_Error, term, meta, querying]
related: [wordpress/09-custom-post-types, wordpress/11-metadata, wordpress/12-queries, wordpress/19-database, wordpress/05-performance]
when_to_use: "Read before classifying content — registering a taxonomy, deciding between a taxonomy and post meta, or querying by term."
---
# Taxonomies

## Purpose

This document defines how to classify content with taxonomies: when a taxonomy is the right
tool instead of post meta, how registration arguments change behavior, and how to query by
term without producing an expensive join.

Taxonomies are WordPress's only indexed classification mechanism. Choosing meta where a
taxonomy belongs is the most common cause of a site that works fine with 200 posts and
collapses at 20,000.

---

## Core Principle

Use a **taxonomy** when the value groups content and you will filter or list by it. Use
**post meta** when the value belongs to one item and is only ever read alongside it.

The difference is structural, not stylistic:

| | Taxonomy | Post meta |
|---|---|---|
| Storage | `wp_term_relationships` — indexed join | `wp_postmeta` — `meta_value` is **not** indexed |
| Query by value | Fast at any scale | Full scan of the meta table; degrades with row count |
| Shared vocabulary | Yes — one term, many posts | No — the string is duplicated per row |
| Archive page | Automatic (`/genre/jazz/`) | Requires custom routing |
| Rename a value | One update, everywhere | Update every row |

"Genre", "region", "product category", "difficulty level" are taxonomies. "Event start date",
"SKU", "external ID", "seat count" are meta.

---

## Registration

Register on `init`, alongside the post types the taxonomy applies to.

**Good Example**

```php
add_action( 'init', 'myplugin_register_event_type_taxonomy' );

function myplugin_register_event_type_taxonomy() {
	register_taxonomy(
		'myplugin_event_type',                 // prefixed; max 32 characters
		array( 'myplugin_event' ),             // object types it classifies
		array(
			'labels'            => array(
				'name'          => _x( 'Event Types', 'taxonomy general name', 'myplugin' ),
				'singular_name' => _x( 'Event Type', 'taxonomy singular name', 'myplugin' ),
				'add_new_item'  => __( 'Add New Event Type', 'myplugin' ),
			),
			'public'            => true,
			'hierarchical'      => true,       // category-like: parents and checkboxes
			'show_admin_column' => true,       // adds a column to the post list table
			'show_in_rest'      => true,       // required for the block editor sidebar
			'rewrite'           => array( 'slug' => 'event-type', 'with_front' => false ),
		)
	);
}
```

**Bad Example**

```php
add_action( 'init', function () {
	register_taxonomy( 'type', 'myplugin_event', array(   // unprefixed, collides
		'hierarchical' => true,
		// no 'show_in_rest'      → invisible in the block editor
		// no 'show_admin_column' → editors cannot see or sort by it
		// no labels              → the admin UI reads "Tags" everywhere
	) );
} );
```

---

## Hierarchical or Flat

`hierarchical` changes storage semantics, admin UI, and query cost:

- **`true`** — category-like. Parent/child relationships, a checkbox list in the editor, and
  `WP_Term_Query` walks descendants on query. Correct for a fixed, curated vocabulary.
- **`false`** — tag-like. A free-text field, no hierarchy, cheaper queries. Correct for
  open-ended labelling.

A hierarchical taxonomy with thousands of terms makes the editor's checkbox metabox load all
of them on every post edit. If the vocabulary is large and flat in practice, register it flat.

---

## Assigning and Reading Terms

```php
// Replace all terms for this taxonomy on the post.
wp_set_object_terms( $post_id, array( 'workshop', 'online' ), 'myplugin_event_type' );

// Append instead of replacing.
wp_set_object_terms( $post_id, array( 'featured' ), 'myplugin_event_type', true );

// Read.
$terms = get_the_terms( $post_id, 'myplugin_event_type' );   // cached per post
if ( $terms && ! is_wp_error( $terms ) ) {
	foreach ( $terms as $term ) {
		echo esc_html( $term->name );
	}
}
```

`get_the_terms()` uses the object cache; `wp_get_object_terms()` queries directly. In a loop,
the cached variant is the one you want.

---

## Querying by Term

```php
$query = new WP_Query(
	array(
		'post_type' => 'myplugin_event',
		'tax_query' => array(
			array(
				'taxonomy' => 'myplugin_event_type',
				'field'    => 'slug',              // 'term_id' is marginally faster
				'terms'    => array( 'workshop' ),
			),
		),
		'posts_per_page' => 12,
	)
);
```

Two things worth knowing:

- **`'operator' => 'NOT IN'`** produces a subquery that does not use the relationship index
  efficiently. On large data sets, prefer expressing the query positively.
- **Multiple `tax_query` clauses** each add a join. Three or four clauses on a large site is
  where query time becomes visible; consider a denormalized flag or a cached result instead.

Compare with the meta equivalent, which is what a taxonomy avoids:

```php
// Bad at scale: meta_value has no index, so this scans the postmeta table.
'meta_query' => array(
	array( 'key' => 'event_type', 'value' => 'workshop' ),
),
```

---

## Term Meta

Terms carry their own metadata — useful for colors, icons, ordering, or an external ID.

```php
add_term_meta( $term_id, 'myplugin_color', '#2563EB', true );
$color = get_term_meta( $term_id, 'myplugin_color', true );

// Register it so the REST API and block editor can see it.
add_action( 'init', function () {
	register_term_meta(
		'myplugin_event_type',
		'myplugin_color',
		array(
			'type'              => 'string',
			'single'            => true,
			'show_in_rest'      => true,
			'sanitize_callback' => 'sanitize_hex_color',
			'auth_callback'     => function () {
				return current_user_can( 'manage_categories' );
			},
		)
	);
} );
```

---

## Slug Collisions

Taxonomy slugs, post type slugs, and page slugs share one rewrite namespace. A taxonomy with
`slug => 'events'` on a site that also has an `events` post type archive produces a 404 —
and the URL that breaks is often not the one you just added.

Before choosing a rewrite slug, check that no page, post type archive, or other taxonomy
already claims it.

---

## Common Mistakes

- **Storing classification in post meta**, then discovering the archive page and the filter
  query cannot scale.
- **Unprefixed taxonomy names** colliding with plugins.
- **Omitting `show_in_rest`**, so the taxonomy is missing from the block editor sidebar.
- **Omitting `show_admin_column`**, leaving editors no way to see assignments in the list
  table.
- **Rewrite slug collisions** with a post type archive or an existing page.
- **`wp_set_object_terms()` without the `$append` argument**, silently deleting the terms
  that were already assigned.
- **Hierarchical taxonomies with thousands of terms**, making the editor unusable.
- **Ignoring `is_wp_error()`** on term functions, which return `WP_Error` rather than
  throwing.

---

## Verification Checklist

- Is this classification, filtering, or grouping? Then it is a taxonomy, not meta.
- Is the name prefixed and under 32 characters?
- Are `show_in_rest`, `show_admin_column`, and labels all set?
- Is `hierarchical` chosen from how the vocabulary is actually used?
- Does the rewrite slug collide with any post type archive, page, or other taxonomy?
- Do calls to `wp_set_object_terms()` pass `$append` deliberately?
- Are `WP_Error` returns checked before use?

---

## Summary

Taxonomies are the indexed way to classify content in WordPress, and post meta is not a
substitute. Register them prefixed on `init` with REST and admin visibility, pick hierarchy
based on real usage, and keep `tax_query` clauses few.

## Related

- `knowledge/wordpress/09-custom-post-types.md`
- `knowledge/wordpress/11-metadata.md`
- `knowledge/wordpress/12-queries.md`
- `knowledge/wordpress/19-database.md`
- `knowledge/wordpress/05-performance.md`
