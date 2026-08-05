---
id: wordpress/23-caching
topic: wordpress
slug: caching
title: "Caching"
type: doc
order: 23
status: ready
tags: [wordpress, caching]
related: [wordpress/05-performance, wordpress/12-queries, wordpress/18-rest-api, wordpress/19-database, wordpress/29-maintenance]
when_to_use: "Read before caching anything in WordPress — choosing between transients and the object cache, invalidating on write, or diagnosing stale or personalized content."
---
# Caching

## Purpose

This document defines the caching layers available to a WordPress site, which one to use for
a given problem, how to invalidate correctly, and the failure modes — stale content,
personalized data served to the wrong user, cache stampedes — that follow from getting it
wrong.

Caching is the highest-leverage performance work available on WordPress, and the easiest place
to introduce a correctness bug.

---

## Core Principle

**Cache the expensive and stable; never cache the personalized.**

The two questions to answer before adding any cache:

1. What invalidates this? If the answer is "it expires eventually", the site will serve stale
   data on every write.
2. Who is it for? If the value differs per user, it does not belong in a shared cache under a
   shared key.

---

## The Layers

| Layer | Scope | Lifetime | Use for |
|---|---|---|---|
| Page cache | Whole HTML response | Minutes–hours | Anonymous traffic |
| Object cache | Any PHP value | Request, or persistent with a drop-in | Query results, computed values |
| Transients | Any PHP value | Explicit expiry | Expensive results with a natural TTL |
| OPcache | Compiled PHP | Until deploy | Always on; nothing to code |
| CDN | Static assets, sometimes HTML | Hours–days | Media, CSS, JS |
| Browser | Assets | Per `Cache-Control` | Versioned assets |

The most common misconfiguration is having no persistent object cache while relying heavily on
transients — which turns every transient read and write into a database query.

---

## Object Cache

`wp_cache_*` is per-request by default. With a drop-in (`object-cache.php` from a Redis or
Memcached plugin), it becomes persistent across requests — the same code, a different
lifetime.

```php
function acme_get_event_stats( int $event_id ): array {
	$cache_key   = "event_stats_{$event_id}";
	$cache_group = 'acme_events';

	$stats = wp_cache_get( $cache_key, $cache_group );

	if ( false !== $stats ) {
		return $stats;
	}

	global $wpdb;
	$stats = array(
		'signups' => (int) $wpdb->get_var(
			$wpdb->prepare( "SELECT COUNT(*) FROM {$wpdb->prefix}acme_event_signups WHERE event_id = %d", $event_id )
		),
	);

	wp_cache_set( $cache_key, $stats, $cache_group, 5 * MINUTE_IN_SECONDS );

	return $stats;
}
```

Note `false !== $stats`. A cached value that is legitimately `0`, `''`, or `array()` is
indistinguishable from a miss under a loose comparison, so the cache never hits and the code
looks merely slow rather than broken.

Always pass a **group**. Groups namespace keys and allow targeted invalidation, and without
one a key collides with every other plugin using the same name.

---

## Transients

A transient is a cached value with an explicit expiry. With a persistent object cache it is
stored there; without one it goes to the options table.

```php
function acme_get_upcoming_events(): array {
	$events = get_transient( 'acme_upcoming_events' );

	if ( false === $events ) {
		$events = get_posts( array(
			'post_type'      => 'acme_event',
			'posts_per_page' => 10,
			'fields'         => 'ids',
			'meta_key'       => '_acme_event_start',
			'orderby'        => 'meta_value',
			'no_found_rows'  => true,
		) );

		set_transient( 'acme_upcoming_events', $events, HOUR_IN_SECONDS );
	}

	return $events;
}
```

Two operational details specific to transients:

- **Expiry is lazy.** An expired transient is deleted when someone asks for it, not on
  schedule. A site that writes many short-lived transients without a persistent object cache
  accumulates rows in `wp_options`.
- **No expiry means autoloaded.** `set_transient( $key, $value )` with no third argument
  stores an autoloaded option, which is then loaded on *every* request forever. Always pass an
  expiry.

---

## Invalidate on Write

Expiry alone is not invalidation. Clear the cache where the data changes:

```php
add_action( 'save_post_acme_event', 'acme_flush_event_caches' );
add_action( 'deleted_post', 'acme_flush_event_caches' );

function acme_flush_event_caches( int $post_id ): void {
	delete_transient( 'acme_upcoming_events' );
	wp_cache_delete( "event_stats_{$post_id}", 'acme_events' );

	// If a full-page cache plugin is present, tell it too.
	if ( function_exists( 'wp_cache_clear_cache' ) ) {
		wp_cache_clear_cache();
	}
}
```

`save_post` fires for autosaves and revisions as well, so guard anything expensive:

```php
if ( wp_is_post_autosave( $post_id ) || wp_is_post_revision( $post_id ) || defined( 'DOING_AUTOSAVE' ) ) {
	return;
}
```

---

## Never Cache Personalized Output

This is the failure that turns a performance improvement into a data leak — one user's cart,
name, or dashboard served to everyone.

**Bad Example**

```php
// The key ignores the user. The first visitor's greeting is cached for all of them.
$html = get_transient( 'acme_user_panel' );
if ( false === $html ) {
	$html = acme_render_panel( wp_get_current_user() );
	set_transient( 'acme_user_panel', $html, HOUR_IN_SECONDS );
}
```

**Good Example**

```php
// Cache the expensive shared part; render the personal part live.
$shared = get_transient( 'acme_panel_shared' );
if ( false === $shared ) {
	$shared = acme_render_shared_panel();
	set_transient( 'acme_panel_shared', $shared, HOUR_IN_SECONDS );
}

echo $shared;                                    // already escaped at build time
echo acme_render_greeting( wp_get_current_user() );  // per-user, never cached
```

At the page-cache layer, exclude such responses explicitly:

```php
if ( is_user_logged_in() && ! defined( 'DONOTCACHEPAGE' ) ) {
	define( 'DONOTCACHEPAGE', true );   // honored by most page-cache plugins
}
```

Nonces are the other trap: a nonce embedded in a cached page expires while the page is still
being served, producing "link expired" errors. Fetch nonces over AJAX or REST on pages that
are full-page cached.

---

## Cache Stampede

When a popular cached value expires, every concurrent request rebuilds it at once — the
database sees the full unfiltered load precisely when it is busiest.

```php
function acme_get_expensive_report(): array {
	$key    = 'acme_report';
	$report = get_transient( $key );

	if ( false !== $report ) {
		return $report;
	}

	// Only one process rebuilds; the rest serve the slightly stale copy.
	if ( ! add_option( $key . '_rebuilding', time(), '', 'no' ) ) {
		return get_transient( $key . '_stale' ) ?: array();
	}

	$report = acme_build_report();

	set_transient( $key, $report, 10 * MINUTE_IN_SECONDS );
	set_transient( $key . '_stale', $report, DAY_IN_SECONDS );   // fallback copy
	delete_option( $key . '_rebuilding' );

	return $report;
}
```

Alternatively, rebuild ahead of expiry from a scheduled job — see
[Cron and Background Tasks](22-cron-and-background-tasks.md).

---

## What Not to Cache

- **Anything already cached by WordPress.** `WP_Query` results, post objects, and meta are in
  the object cache already; wrapping them adds a layer without a benefit.
- **Values cheaper to compute than to fetch.** A cache lookup is not free.
- **Anything that must be correct immediately** — stock levels, balances, permission checks.
- **Admin screens**, where staleness is confusing and traffic is low.

---

## Common Mistakes

- **`if ( ! $cached )`** instead of `false !== $cached`, so falsy values never hit.
- **No cache group**, colliding with other plugins.
- **`set_transient()` without an expiry**, creating a permanently autoloaded option.
- **Expiry treated as invalidation**, leaving stale content after every edit.
- **Caching personalized output** under a shared key.
- **Nonces inside full-page-cached HTML.**
- **No stampede protection** on an expensive, popular value.
- **Heavy work on `save_post`** without excluding autosaves and revisions.
- **Transients used heavily with no persistent object cache**, bloating `wp_options`.

---

## Verification Checklist

- Does every cache read compare against `false` explicitly?
- Does every cached value have both an expiry and an invalidation path on write?
- Are cache keys namespaced with a group, and do they include every input that changes the
  result — including the user, when relevant?
- Is anything personalized excluded from shared and page caches?
- Does the site have a persistent object cache if it relies on transients?
- Are expensive popular values protected against stampede?
- Are nonces kept out of cached HTML?

---

## Summary

Pick the layer that matches the data's lifetime, key it by everything that changes the result,
invalidate where the data is written rather than trusting expiry, and keep anything
user-specific out of shared caches entirely.
