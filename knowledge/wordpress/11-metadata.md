---
id: wordpress/11-metadata
topic: wordpress
slug: metadata
title: "WordPress Metadata"
type: doc
order: 11
status: ready
tags: [wordpress, metadata, WP_Query, update_post_meta, meta_query, get_post_meta, register_post_meta, gmdate]
related: [wordpress/10-taxonomies, wordpress/12-queries, wordpress/16-block-editor, wordpress/19-database, wordpress/06-security, wordpress/09-custom-post-types]
when_to_use: "Read before storing custom fields — registering post meta, exposing it to the block editor or REST, or querying by meta value."
---
# WordPress Metadata

## Purpose

This document defines how to store and retrieve custom data attached to posts, terms, users,
and comments: registering meta so the editor and REST API can use it, sanitizing what gets
written, and understanding why `meta_query` is expensive.

Post meta is the most-used and most-misused storage in WordPress. It is a key-value store
with one index — on the key, not the value — and every design decision follows from that.

---

## Core Principle

Meta is an **attribute of one object**, read alongside that object. The moment you need to
*find* objects by a meta value at scale, the data probably belongs in a taxonomy or its own
column.

```sql
-- What the database actually has:
KEY meta_key (meta_key(191))     -- indexed
-- meta_value is LONGTEXT with NO index
```

So `get_post_meta( $id, 'price', true )` is cheap — it reads a cached row set for one post.
`meta_query` on `price` is not: it filters an unindexed column across every row with that key.

---

## Registering Meta

Unregistered meta works with `get_post_meta()`, but is invisible to the block editor and the
REST API, and nothing validates what gets written. Register it.

```php
add_action( 'init', 'myplugin_register_event_meta' );

function myplugin_register_event_meta() {
	register_post_meta(
		'myplugin_event',                 // '' registers for every post type
		'_myplugin_event_start',
		array(
			'type'              => 'string',
			'single'            => true,
			'default'           => '',
			'show_in_rest'      => true,   // required for the block editor and REST
			'sanitize_callback' => 'myplugin_sanitize_date',
			'auth_callback'     => function ( $allowed, $meta_key, $post_id ) {
				return current_user_can( 'edit_post', $post_id );
			},
		)
	);
}

function myplugin_sanitize_date( $value ) {
	$date = DateTimeImmutable::createFromFormat( 'Y-m-d', (string) $value );
	return $date ? $date->format( 'Y-m-d' ) : '';
}
```

Three arguments carry the weight:

- **`sanitize_callback`** runs on every write, including writes from the REST API and
  WP-CLI. Without it, whatever the client sent is what lands in the database.
- **`auth_callback`** decides who may write this key through REST. The default for protected
  keys is deny; for public keys it is `edit_post`. Never return `true` unconditionally.
- **`show_in_rest`** exposes the field. For structured values, pass a schema rather than
  `true`:

```php
'show_in_rest' => array(
	'schema' => array(
		'type'       => 'object',
		'properties' => array(
			'lat' => array( 'type' => 'number' ),
			'lng' => array( 'type' => 'number' ),
		),
	),
),
```

---

## Protected Keys

A meta key beginning with `_` is **protected**: hidden from the Custom Fields UI and not
writable through the generic meta box. Use it for anything your code owns.

```php
update_post_meta( $post_id, '_myplugin_external_id', $id );  // internal, hidden
update_post_meta( $post_id, 'subtitle', $subtitle );          // editor-visible field
```

Protection is about the UI, not security — capability checks are still required.

---

## Reading and Writing

```php
$start = get_post_meta( $post_id, '_myplugin_event_start', true );   // single value
$all   = get_post_meta( $post_id, '_myplugin_speaker', false );      // array of values

update_post_meta( $post_id, '_myplugin_event_start', '2026-09-01' ); // add or update
add_post_meta( $post_id, '_myplugin_speaker', 'Ada', false );        // append (multi-value)
delete_post_meta( $post_id, '_myplugin_speaker', 'Ada' );            // delete one value
```

**The return-value trap.** `update_post_meta()` returns `false` both when the write fails
*and* when the value was already identical. Branching on it as if it meant failure produces
phantom errors:

```php
// Bad: reports failure whenever nothing changed.
if ( ! update_post_meta( $post_id, '_myplugin_status', $status ) ) {
	return new WP_Error( 'save_failed', 'Could not save status' );
}

// Good: compare first if you genuinely need to know.
$current = get_post_meta( $post_id, '_myplugin_status', true );
if ( $current !== $status ) {
	update_post_meta( $post_id, '_myplugin_status', $status );
}
```

---

## Querying by Meta

`meta_query` works, and it is the right tool for a bounded set. It is the wrong tool for the
primary filter of a large archive.

**Acceptable** — narrow the set with an indexed condition first

```php
new WP_Query(
	array(
		'post_type'      => 'myplugin_event',
		'posts_per_page' => 10,
		'tax_query'      => array(                       // indexed: cuts the set down
			array( 'taxonomy' => 'myplugin_event_type', 'field' => 'slug', 'terms' => 'workshop' ),
		),
		'meta_query'     => array(                       // then filter the remainder
			array(
				'key'     => '_myplugin_event_start',
				'value'   => gmdate( 'Y-m-d' ),
				'compare' => '>=',
				'type'    => 'DATE',                     // without this it compares as a string
			),
		),
		'orderby'        => 'meta_value',
		'meta_key'       => '_myplugin_event_start',
		'order'          => 'ASC',
	)
);
```

**Bad** — an unbounded meta scan as the only filter

```php
new WP_Query(
	array(
		'post_type'      => 'any',
		'posts_per_page' => -1,          // unbounded result set
		'meta_query'     => array(
			'relation' => 'AND',
			array( 'key' => 'featured', 'value' => '1' ),
			array( 'key' => 'region', 'value' => 'eu' ),
			array( 'key' => 'price', 'value' => 100, 'compare' => '<' ),
		),
	)
);
// Three self-joins on an unindexed column, over every post on the site.
```

Rules that keep meta queries survivable:

- Always set `type` for numeric and date comparisons — the column is text, so `'10' < '9'`.
- Never combine `posts_per_page => -1` with `meta_query`.
- `'compare' => 'LIKE'` cannot use the key index either; treat it as a full scan.
- If a meta field is the main filter for an archive, promote it to a taxonomy or add a custom
  table — see [Database](19-database.md).

---

## Serialized Values

Passing an array to `update_post_meta()` stores it serialized. That is fine for a blob read
as a whole, and unusable for anything else:

```php
update_post_meta( $post_id, '_myplugin_settings', array( 'color' => 'blue', 'size' => 3 ) );
// Stored as: a:2:{s:5:"color";s:4:"blue";s:4:"size";i:3;}
```

You cannot query inside it, cannot index it, and a `LIKE` search over serialized data breaks
on string-length prefixes. Store queryable fields as separate keys.

---

## Meta and the Object Cache

`WP_Query` primes the meta cache for the whole result set in one query. Disabling that
priming turns one query into one per post:

```php
// Fine: you genuinely only need IDs and titles.
new WP_Query( array( 'update_post_meta_cache' => false, /* … */ ) );

// Then this in the loop is N+1 queries — the priming you disabled was the fix.
foreach ( $ids as $id ) {
	$price = get_post_meta( $id, '_price', true );
}
```

When working with IDs collected outside `WP_Query`, prime explicitly:

```php
update_meta_cache( 'post', $post_ids );   // one query for all of them
```

---

## Examples

**Good Example** — meta for attributes, a taxonomy for the listing dimension

```php
add_action( 'init', 'myplugin_register_event_storage' );

function myplugin_register_event_storage() {
	// An attribute read alongside the post → meta.
	register_post_meta(
		'myplugin_event',
		'_event_start',
		array(
			'type'              => 'string',
			'single'            => true,
			'show_in_rest'      => true,
			'sanitize_callback' => 'sanitize_text_field',
			'auth_callback'     => 'myplugin_can_edit_events',
		)
	);

	// The dimension archives are filtered by → a taxonomy, indexed through
	// term_relationships rather than scanned in an unindexed LONGTEXT column.
	register_taxonomy(
		'event_month',
		'myplugin_event',
		array( 'public' => false, 'show_in_rest' => true, 'hierarchical' => false )
	);
}

// Derive the term from the meta on save, so the two cannot drift apart.
add_action( 'save_post_myplugin_event', 'myplugin_sync_event_month' );

function myplugin_sync_event_month( int $post_id ) {
	$start = get_post_meta( $post_id, '_event_start', true );
	if ( $start ) {
		wp_set_object_terms( $post_id, gmdate( 'Y-m', strtotime( $start ) ), 'event_month' );
	}
}

// The archive query touches an indexed relationship.
$september = new WP_Query(
	array(
		'post_type'      => 'myplugin_event',
		'posts_per_page' => 20,
		'no_found_rows'  => true,
		'tax_query'      => array(
			array( 'taxonomy' => 'event_month', 'field' => 'slug', 'terms' => '2026-09' ),
		),
	)
);
```

**Bad Example** — unregistered meta used as the primary archive filter

```php
// No registration: invisible to the block editor and REST, and nothing sanitizes
// what gets written.
update_post_meta( $post_id, 'event_start', $_POST['start'] );

// The archive now depends on a LIKE against an unindexed LONGTEXT column, on every
// request. It is fast with 50 events and unusable with 50,000.
$september = new WP_Query(
	array(
		'post_type'  => 'myplugin_event',
		'meta_query' => array(
			array( 'key' => 'event_start', 'value' => '2026-09', 'compare' => 'LIKE' ),
		),
	)
);
```

---

## Common Mistakes

- **Unregistered meta**, invisible to the editor and REST and unvalidated on write.
- **`auth_callback` returning `true`**, letting any authenticated user write the field
  through the REST API.
- **Missing `sanitize_callback`**, so unvalidated input is persisted.
- **Treating `update_post_meta()`'s `false` as an error** when nothing changed.
- **`meta_query` as the primary archive filter**, at a scale where it cannot hold up.
- **Omitting `type` in comparisons**, producing string comparison on numbers and dates.
- **Serialized arrays** for values that later need to be queried.
- **Unprefixed keys** (`price`, `status`) colliding with other plugins.
- **Meta on autoloaded options confusion** — options have `autoload`, meta does not; a large
  autoloaded option is a separate performance problem, see [Performance](05-performance.md).

---

## Verification Checklist

- Is every custom field registered with `type`, `single`, `sanitize_callback`, and
  `auth_callback`?
- Is `show_in_rest` set where the editor or an API client needs the field?
- Are internal keys prefixed and underscore-protected?
- Is any `meta_query` bounded by an indexed condition and a real `posts_per_page`?
- Do numeric and date comparisons declare `type`?
- Are values that need querying stored as discrete keys rather than serialized blobs?
- Is meta priming left enabled, or primed explicitly when working from an ID list?

---

## Summary

Meta is an indexed-by-key, unindexed-by-value store for attributes of a single object.
Register it with sanitization and capability checks, keep queryable data out of serialized
blobs, and move anything that becomes a primary filter into a taxonomy or a real table.

## Related

- `knowledge/wordpress/10-taxonomies.md`
- `knowledge/wordpress/12-queries.md`
- `knowledge/wordpress/16-block-editor.md`
- `knowledge/wordpress/19-database.md`
- `knowledge/wordpress/06-security.md`
- `knowledge/wordpress/09-custom-post-types.md`
