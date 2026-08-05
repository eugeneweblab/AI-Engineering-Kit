---
id: wordpress/12-queries
topic: wordpress
slug: queries
title: "Queries and The Loop"
type: doc
order: 12
status: ready
tags: [wordpress, queries]
related: [wordpress/08-hooks, wordpress/11-metadata, wordpress/19-database, wordpress/23-caching, wordpress/05-performance, wordpress/09-custom-post-types]
when_to_use: "Read before writing a WP_Query, altering the main query, or diagnosing a slow page caused by database queries."
---
# Queries and The Loop

## Purpose

This document defines how to retrieve posts in WordPress: the difference between the main
query and a secondary one, which `WP_Query` arguments determine cost, and how to avoid the
N+1 patterns that dominate slow WordPress pages.

Most WordPress performance problems are query problems, and most query problems come from
three habits: querying inside a loop, fetching more rows than needed, and running a second
query for something the main query already returned.

---

## Core Principle

The page already ran a query before your code executes. Work with it before adding another.

WordPress parses the URL, builds the **main query**, and runs it before any template loads.
A template that ignores that result and runs its own `WP_Query` has paid for two queries and
broken pagination — the main query still determines `$wp_query->max_num_pages`, which the
pagination functions read.

```php
// The main query's results — already fetched, already cached.
if ( have_posts() ) {
	while ( have_posts() ) {
		the_post();
		get_template_part( 'template-parts/content', get_post_type() );
	}
}
```

To change *what* the page lists, filter the main query with `pre_get_posts` rather than
replacing it — see [Hooks](08-hooks.md).

---

## Never Use `query_posts()`

`query_posts()` replaces the global main query object mid-request. It breaks pagination,
conditional tags, and anything that runs later expecting the original query.

```php
// Never. Not in a template, not in a shortcode, not "just this once".
query_posts( 'post_type=event' );
```

The replacements: `pre_get_posts` to alter the main query, `WP_Query` for a secondary loop,
`get_posts()` for a simple list.

---

## Secondary Queries

```php
$events = new WP_Query(
	array(
		'post_type'      => 'myplugin_event',
		'post_status'    => 'publish',
		'posts_per_page' => 6,
		'no_found_rows'  => true,   // not paginating → skip the row-count query
	)
);

if ( $events->have_posts() ) {
	while ( $events->have_posts() ) {
		$events->the_post();
		the_title( '<h3>', '</h3>' );
	}
	wp_reset_postdata();   // restore the global $post — omitting this breaks the rest of the page
}
```

`wp_reset_postdata()` is not optional. Without it, everything after the loop — the sidebar,
the footer, comment templates — sees the last post of your custom loop as the current post.

---

## The Arguments That Determine Cost

| Argument | Effect |
|---|---|
| `no_found_rows => true` | Skips `SQL_CALC_FOUND_ROWS`. Use whenever you are not paginating |
| `fields => 'ids'` | Returns IDs only, no post objects hydrated |
| `posts_per_page` | An explicit bound. `-1` means "every matching row" |
| `update_post_meta_cache` | Primes meta for the whole set in one query — leave on if you read meta |
| `update_post_term_cache` | Same for terms — leave on if you read terms |
| `ignore_sticky_posts` | Sticky handling costs an extra query on the front page |
| `orderby => 'rand'` | Cannot be cached and cannot use an index; avoid on large tables |

**Good Example** — an ID list, then a single primed read

```php
$ids = get_posts(
	array(
		'post_type'      => 'myplugin_event',
		'posts_per_page' => 20,
		'fields'         => 'ids',
		'no_found_rows'  => true,
	)
);

update_meta_cache( 'post', $ids );   // one query for all meta

foreach ( $ids as $id ) {
	$start = get_post_meta( $id, '_myplugin_event_start', true );   // cache hit
}
```

**Bad Example** — the classic N+1

```php
$events = new WP_Query( array( 'post_type' => 'myplugin_event', 'posts_per_page' => -1 ) );

while ( $events->have_posts() ) {
	$events->the_post();

	// One query per post, every time:
	$venue = get_posts( array( 'post_type' => 'venue', 'meta_key' => 'event', 'meta_value' => get_the_ID() ) );
	$author = get_userdata( get_the_author_meta( 'ID' ) );
	$terms  = wp_get_object_terms( get_the_ID(), 'myplugin_event_type' );  // uncached variant
}
```

Three fixes, in order of impact: bound `posts_per_page`; resolve the relationship with a
single query outside the loop keyed by post ID; use the cached `get_the_terms()`.

---

## `WP_Query` vs `get_posts()`

`get_posts()` is `WP_Query` with different defaults, and the defaults matter:

```php
// get_posts() implies:
//   'no_found_rows'       => true       (no pagination)
//   'suppress_filters'    => true       (posts_where / posts_join filters DO NOT run)
//   'ignore_sticky_posts' => true
```

`suppress_filters => true` is the surprising one: plugins that filter queries — including
multilingual plugins — are bypassed. For a simple internal list that is desirable. For
anything user-facing on a site with translation or access-control plugins, it is a bug.

---

## Search Queries

The `s` parameter runs `LIKE '%term%'` across title, excerpt, and content. It cannot use an
index, and it scales badly.

```php
new WP_Query( array( 's' => $term, 'posts_per_page' => 10 ) );
```

For anything beyond a small site, put search behind a dedicated engine (Elasticsearch,
Meilisearch, or a hosted service) rather than tuning the `LIKE`. At minimum, always bound the
result count and never expose an unbounded search to anonymous traffic.

---

## Query Caching

Since WordPress 6.1, `WP_Query` results are cached in the object cache by default
(`cache_results => true`). With a persistent object cache (Redis, Memcached) that removes
repeat queries between requests; without one, the cache lives only for the current request.

Two things defeat it: `orderby => 'rand'`, and queries built from values that change on every
request. If a query is both expensive and stable, cache the result explicitly:

```php
$ids = get_transient( 'myplugin_upcoming_events' );

if ( false === $ids ) {
	$ids = get_posts( array( /* … */ 'fields' => 'ids' ) );
	set_transient( 'myplugin_upcoming_events', $ids, HOUR_IN_SECONDS );
}
```

Invalidate it on write rather than relying only on expiry — see [Caching](23-caching.md).

---

## Common Mistakes

- **`query_posts()`** anywhere.
- **A second query in the template** for data the main query already returned.
- **Missing `wp_reset_postdata()`** after a custom loop.
- **`posts_per_page => -1`** on any set that can grow.
- **Queries inside the loop** — the single largest cause of slow WordPress pages.
- **Disabling meta/term cache priming**, then reading meta or terms in the loop.
- **`no_found_rows` left off** on non-paginated queries, paying for a count nobody reads.
- **`orderby => 'rand'`** on a large table.
- **Unbounded `s` searches** exposed to anonymous traffic.
- **Ignoring that `get_posts()` suppresses filters** on a site that depends on them.

---

## Verification Checklist

- Could this use the main query, or `pre_get_posts`, instead of a new `WP_Query`?
- Is `posts_per_page` explicitly bounded?
- Is `no_found_rows => true` set when pagination is not used?
- Does every custom loop call `wp_reset_postdata()`?
- Are there any queries inside a loop? Can they be hoisted or batched?
- If meta or terms are read in the loop, is cache priming still enabled?
- Is `suppress_filters` acceptable for this context if using `get_posts()`?
- Are expensive stable queries cached, with invalidation on write?

---

## Summary

Use the query the page already ran, alter it with `pre_get_posts`, and reach for `WP_Query`
only for genuinely secondary data. Bound every result set, keep queries out of loops, and let
WordPress prime the caches it knows how to prime.

## Related

- `knowledge/wordpress/08-hooks.md`
- `knowledge/wordpress/11-metadata.md`
- `knowledge/wordpress/19-database.md`
- `knowledge/wordpress/23-caching.md`
- `knowledge/wordpress/05-performance.md`
- `knowledge/wordpress/09-custom-post-types.md`
