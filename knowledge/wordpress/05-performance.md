---
id: wordpress/05-performance
topic: wordpress
slug: performance
title: "WordPress Performance"
type: doc
order: 5
status: ready
tags: [wordpress, performance, WP_Query, add_action, plugins_url, get_col, wp_enqueue_script, get_the_title, performance-sensitive, features, optimizing]
related: [wordpress/12-queries, wordpress/23-caching, wordpress/19-database, wordpress/21-media-and-uploads, performance/13-database-performance]
when_to_use: "Read before optimizing or building performance-sensitive WordPress features."
---
# WordPress Performance

## Purpose

This document defines the engineering principles for building high-performance WordPress applications.

Performance is not achieved by applying isolated optimizations after development is complete.

Performance should be considered during architecture, implementation, deployment, and long-term maintenance.

The objective is to deliver fast, scalable, and efficient applications that remain performant as content, traffic, and features grow.

---

## Core Principle

Optimize architecture before optimizing code.

The largest performance improvements usually come from better system design rather than micro-optimizations.

Always identify the real bottleneck before implementing changes.

---

## Performance Mindset

Every implementation should consider:

- CPU usage;
- memory usage;
- database load;
- network requests;
- rendering time;
- cache efficiency;
- frontend performance.

Avoid optimizing areas that are not measurable bottlenecks.

---

## Measure Before Optimizing

Before making performance changes:

- reproduce the issue;
- collect performance metrics;
- identify the bottleneck;
- establish a baseline.

Never optimize based on assumptions.

---

## Database Performance

Prefer:

- WordPress APIs;
- indexed queries;
- WP_Query;
- lazy loading;
- pagination;
- object caching.

Avoid:

- repeated database queries;
- querying inside loops;
- unnecessary JOIN operations;
- loading entire datasets.

Every database query should have a clear purpose.

When a custom `$wpdb` query is unavoidable, always pass values through `$wpdb->prepare()`. This prevents SQL injection and keeps the query cacheable at the MySQL layer.

Good:

```php
global $wpdb;

$product_ids = $wpdb->get_col(
	$wpdb->prepare(
		"SELECT ID FROM {$wpdb->posts}
		 WHERE post_type = %s AND post_status = %s
		 LIMIT %d",
		'product',
		'publish',
		20
	)
);
```

Bad:

```php
global $wpdb;

// Values interpolated directly: SQL injection risk and unstable query cache.
$product_ids = $wpdb->get_col(
	"SELECT ID FROM {$wpdb->posts}
	 WHERE post_type = '$post_type' AND post_status = 'publish'"
);
```

Note that table names (`{$wpdb->posts}`) are safe to interpolate because they come from WordPress, but every dynamic value must use a `%s`, `%d`, or `%f` placeholder.

---

## Query Optimization

Before writing a query ask:

- Can existing data be reused?
- Can the result be cached?
- Is every selected field required?
- Can pagination be applied?
- Is this query executed repeatedly?

Duplicate queries should be eliminated whenever possible.

`WP_Query` primes several caches and counts total rows by default. When those features are not needed, disable them explicitly. Each disabled feature removes work from the request.

Good:

```php
$query = new WP_Query(
	array(
		'post_type'              => 'product',
		'post_status'            => 'publish',
		'posts_per_page'         => 20,
		'fields'                 => 'ids',   // Return IDs only when full post objects are not needed.
		'no_found_rows'          => true,    // Skip SQL_CALC_FOUND_ROWS when total pages are not needed.
		'update_post_meta_cache' => false,   // Skip meta priming when meta is not read.
		'update_post_term_cache' => false,   // Skip term priming when terms are not read.
	)
);

$product_ids = $query->posts;
```

Set `no_found_rows` to `true` only when pagination controls do not need `$query->max_num_pages`, because that value is derived from the row count.

Bad:

```php
// A fresh WP_Query on every loop iteration (N+1 queries).
foreach ( $category_ids as $category_id ) {
	$related = new WP_Query(
		array(
			'post_type' => 'product',
			'tax_query' => array(
				array(
					'taxonomy' => 'product_cat',
					'terms'    => $category_id,
				),
			),
		)
	);

	// ...
}
```

Prefer a single query that passes every term in one `terms` array over one query per iteration.

---

## Object Caching

Use object caching for frequently requested data.

Suitable examples:

- settings;
- navigation;
- taxonomy data;
- expensive calculations;
- API responses.

Avoid caching data that changes frequently unless invalidation is well defined.

Use `wp_cache_get()` and `wp_cache_set()` with a dedicated cache group. Remember that `wp_cache_get()` returns `false` on a miss, so use a Yoda condition to distinguish a real cached value from a miss.

```php
function my_get_active_promotions() {
	$cache_key   = 'active_promotions';
	$cache_group = 'my_plugin';

	$promotions = wp_cache_get( $cache_key, $cache_group );
	if ( false !== $promotions ) {
		return $promotions;
	}

	$promotions = my_query_active_promotions(); // Expensive query.
	wp_cache_set( $cache_key, $promotions, $cache_group, HOUR_IN_SECONDS );

	return $promotions;
}
```

Without a persistent object cache (Redis or Memcached) drop-in, `wp_cache_*` data lives for a single request only. That still eliminates duplicate work within one page load. When the underlying data changes, invalidate the entry with `wp_cache_delete( 'active_promotions', 'my_plugin' )`.

---

## Transients

Use transients for temporary cached data.

Suitable examples:

- remote API responses;
- expensive reports;
- computed statistics;
- third-party integrations.

Always define an expiration strategy.

Transients persist across requests (in the options table, or in the object cache when one is configured). They are the correct tool for caching a slow remote call. Always set a timeout and always degrade gracefully when the remote call fails.

```php
function my_get_exchange_rates() {
	$rates = get_transient( 'my_exchange_rates' );
	if ( false !== $rates ) {
		return $rates;
	}

	$response = wp_remote_get(
		'https://api.example.com/rates',
		array( 'timeout' => 5 )
	);

	if ( is_wp_error( $response ) || 200 !== wp_remote_retrieve_response_code( $response ) ) {
		return array(); // Degrade gracefully; do not cache a failure.
	}

	$rates = json_decode( wp_remote_retrieve_body( $response ), true );
	set_transient( 'my_exchange_rates', $rates, HOUR_IN_SECONDS );

	return $rates;
}
```

Do not store a failed or empty response under the transient key. Caching a failure hides the outage until the timeout expires.

---

## REST API Performance

Review:

- response size;
- number of requests;
- unnecessary fields;
- repeated computations;
- authentication overhead.

Return only the data required by the client.

Register routes on `rest_api_init`, always supply a `permission_callback` (WordPress logs a notice without one), sanitize incoming arguments, and shape the response to contain only the fields the client uses.

```php
add_action( 'rest_api_init', 'my_register_products_route' );

function my_register_products_route() {
	register_rest_route(
		'my-plugin/v1',
		'/products',
		array(
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => 'my_get_products',
			'permission_callback' => '__return_true', // Public read endpoint.
			'args'                => array(
				'page' => array(
					'default'           => 1,
					'sanitize_callback' => 'absint',
				),
			),
		)
	);
}

function my_get_products( WP_REST_Request $request ) {
	$query = new WP_Query(
		array(
			'post_type'              => 'product',
			'post_status'            => 'publish',
			'posts_per_page'         => 20,
			'paged'                  => $request->get_param( 'page' ),
			'no_found_rows'          => true,
			'update_post_term_cache' => false,
		)
	);

	$products = array();
	foreach ( $query->posts as $product ) {
		$products[] = array(
			'id'    => $product->ID,
			'title' => $product->post_title,
		);
	}

	return rest_ensure_response( $products );
}
```

Returning the full `WP_Post` object (or the default `/wp/v2/` response) sends dozens of fields the client may never read. A hand-built array keeps the payload small.

---

## Asset Loading

Load only required assets.

Review:

- CSS bundles;
- JavaScript bundles;
- fonts;
- icons;
- images;
- third-party libraries.

Avoid loading assets globally when they are page-specific.

Enqueue on `wp_enqueue_scripts`, gate page-specific bundles behind a conditional tag, and let WordPress defer non-critical scripts. Since WordPress 6.3 the loading strategy is passed through the `$args` array of `wp_enqueue_script()`.

Good:

```php
add_action( 'wp_enqueue_scripts', 'my_enqueue_checkout_assets' );

function my_enqueue_checkout_assets() {
	// Load the checkout bundle only on the checkout page.
	if ( ! is_page( 'checkout' ) ) {
		return;
	}

	wp_enqueue_script(
		'my-checkout',
		plugins_url( 'assets/checkout.js', __FILE__ ),
		array( 'wp-element' ),
		'1.0.0',
		array(
			'in_footer' => true,
			'strategy'  => 'defer',
		)
	);
}
```

Bad:

```php
add_action( 'wp_enqueue_scripts', 'my_enqueue_checkout_assets' );

function my_enqueue_checkout_assets() {
	// Loads the checkout bundle on every page, blocking in the head.
	wp_enqueue_script(
		'my-checkout',
		plugins_url( 'assets/checkout.js', __FILE__ ),
		array(),
		'1.0.0'
	);
}
```

Always pass an explicit version string as the fourth argument. Passing `null` makes WordPress append its own version and can break cache busting after a deploy.

---

## Image Optimization

Prefer:

- modern image formats;
- responsive images;
- lazy loading;
- appropriate image dimensions;
- optimized compression.

Avoid serving oversized images.

---

## JavaScript Performance

Reduce:

- unnecessary renders;
- duplicate event listeners;
- unnecessary API requests;
- unused libraries;
- blocking scripts.

Move expensive work away from the critical rendering path.

---

## CSS Performance

Maintain:

- reusable utility classes;
- consistent design tokens;
- minimal specificity;
- small bundle size.

Avoid duplicated styles across components.

---

## External APIs

External services introduce latency.

Before adding an integration:

- determine timeout strategy;
- define retry behavior;
- define fallback behavior;
- consider caching responses.

External dependencies should degrade gracefully.

---

## Background Processing

Long-running tasks should execute outside the request lifecycle whenever possible.

Examples:

- imports;
- exports;
- image processing;
- email delivery;
- synchronization jobs.

Keep page requests fast.

Schedule recurring work with WP-Cron. Guard the scheduler with `wp_next_scheduled()` so the event is registered exactly once, and hook the actual work to the event name.

```php
add_action( 'init', 'my_schedule_daily_sync' );

function my_schedule_daily_sync() {
	if ( ! wp_next_scheduled( 'my_daily_sync' ) ) {
		wp_schedule_event( time(), 'daily', 'my_daily_sync' );
	}
}

add_action( 'my_daily_sync', 'my_run_daily_sync' );

function my_run_daily_sync() {
	// Long-running synchronization runs outside the visitor's page request.
}
```

WP-Cron fires on page traffic, not on a fixed clock. For time-critical or heavy jobs, disable it with `define( 'DISABLE_WP_CRON', true )` and trigger `wp-cron.php` from the system crontab, or use a queue library such as Action Scheduler for jobs that must survive retries. Remember to clear the schedule on plugin deactivation with `wp_clear_scheduled_hook( 'my_daily_sync' )`.

---

## Monitoring

Continuously monitor:

- response times;
- slow queries;
- error rates;
- cache hit ratio;
- memory usage;
- CPU usage.

Performance is an ongoing engineering activity.

---

## AI Execution Checklist

## Investigation

☐ Identify the bottleneck.

☐ Collect performance metrics.

☐ Review database queries.

☐ Review network requests.

☐ Review asset loading.

---

## Planning

☐ Identify optimization opportunities.

☐ Estimate implementation impact.

☐ Preserve existing behavior.

☐ Define verification strategy.

---

## Implementation

☐ Minimize database queries.

☐ Reuse cached data.

☐ Reduce unnecessary rendering.

☐ Optimize asset loading.

☐ Preserve maintainability.

---

## Verification

☐ Compare before and after.

☐ Review response times.

☐ Review cache usage.

☐ Review memory usage.

☐ Verify functionality.

---

## Examples

**Good Example** — one query, primed caches, a bounded result

```php
function myplugin_render_event_list( int $limit = 20 ): string {
	$query = new WP_Query(
		array(
			'post_type'              => 'myplugin_event',
			'posts_per_page'         => $limit,   // always bounded
			'no_found_rows'          => true,     // no pagination here, so skip the row count
			'update_post_meta_cache' => true,     // one meta query for the whole set
			'update_post_term_cache' => false,    // terms are not rendered; do not load them
		)
	);

	$out = '';
	foreach ( $query->posts as $event ) {
		// Already in the object cache from the primed meta query above — no extra SQL.
		$starts = get_post_meta( $event->ID, '_event_start', true );
		$out   .= sprintf(
			'<li>%s — %s</li>',
			esc_html( get_the_title( $event ) ),
			esc_html( $starts )
		);
	}

	return '<ul>' . $out . '</ul>';
}
```

**Bad Example** — a query per row, unbounded, uncached

```php
function myplugin_render_event_list(): string {
	$ids = get_posts(
		array(
			'post_type'      => 'myplugin_event',
			'posts_per_page' => -1,       // every event ever published
			'fields'         => 'ids',
		)
	);

	$out = '';
	foreach ( $ids as $id ) {
		// One uncached round trip per event, then another for the organiser.
		$starts    = $GLOBALS['wpdb']->get_var(
			$GLOBALS['wpdb']->prepare(
				"SELECT meta_value FROM {$GLOBALS['wpdb']->postmeta}
				 WHERE post_id = %d AND meta_key = '_event_start'",
				$id
			)
		);
		$organiser = get_user_by( 'id', get_post_field( 'post_author', $id ) );

		$out .= '<li>' . get_the_title( $id ) . ' — ' . $starts . '</li>';
	}

	return '<ul>' . $out . '</ul>';
}
```

At 40 events this looks acceptable in development. At 4,000 it is 8,000 queries per page load,
and the fix is architectural — bound the set and prime the cache — not a faster loop.

---

## Common Mistakes

Avoid:

Optimizing without measurement.

Querying inside loops.

Loading unnecessary assets.

Ignoring caching.

Returning excessive API data.

Premature optimization.

Optimizing code instead of architecture.

Ignoring long-term scalability.

---

## Completion Criteria

Performance work is complete only if:

- the bottleneck has been verified;
- measurable improvements have been achieved;
- functionality remains unchanged;
- maintainability has not been reduced;
- documentation has been updated when appropriate.

---

## Summary

Performance is the result of good architecture, efficient data access, responsible resource usage, and continuous measurement.

The fastest code is often the code that never executes because unnecessary work has been eliminated.

## Related

- `knowledge/wordpress/12-queries.md`
- `knowledge/wordpress/23-caching.md`
- `knowledge/wordpress/19-database.md`
- `knowledge/wordpress/21-media-and-uploads.md`
- `knowledge/performance/13-database-performance.md`
