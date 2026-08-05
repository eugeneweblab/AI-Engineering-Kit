---
id: woocommerce/15-performance
topic: woocommerce
slug: performance
title: "WooCommerce Performance"
type: doc
order: 15
status: ready
tags: [woocommerce, performance, limit, set_transient, get_transient, get_post_meta, wp_postmeta, update_meta_cache]
related: [woocommerce/24-scaling, woocommerce/12-hooks, woocommerce/13-rest-api, woocommerce/01-architecture, woocommerce/100-common-antipatterns]
when_to_use: "Read before adding queries, hooks, or caching to a WooCommerce store, or when diagnosing slow pages."
---
# WooCommerce Performance

## Purpose

This document defines how to keep a WooCommerce store fast under real catalog and order
volume. It covers database queries, object caching, page/fragment caching, and the hooks
that quietly run on every request. It is written so an agent can add features without
introducing an N+1 query, an uncached repeated lookup, or a hook that fires expensive
work on every cart change.

WooCommerce performance is dominated by the database. Products, orders, and their meta
live in WordPress tables (with High-Performance Order Storage using dedicated order
tables since WooCommerce 8+). Most slowness is too many queries or unbounded queries,
not slow PHP.

## Why It Matters

Stores that are instant with 50 products time out at 50,000 because a listing loop does
one query per product. Slow pages cost conversions directly — every added second of load
measurably drops checkout completion — and a slow admin makes fulfillment painful for
staff. Unlike a bug, a performance regression usually ships green: it passes tests and
looks fine in dev, then degrades as data grows. That is why query discipline and caching
must be designed in, not retrofitted after an outage.

## Core Principles

- **No queries in loops.** Fetch the set you need in one query, then iterate in memory.
  One query per row (the N+1 pattern) is the default failure mode.
- **Bound every query.** Always pass `limit`/`posts_per_page`; never `-1` (unlimited) on
  user-facing paths. Unbounded queries scale with catalog size until they OOM.
- **Cache the expensive and repeated.** Wrap costly, reused computations in transients or
  the object cache; do not recompute per request what changes hourly.
- **Enable a persistent object cache.** Redis/Memcached turns repeated meta and option
  lookups into memory hits; without it every request re-queries the DB.
- **Use HPOS and proper indexes.** Query orders through `wc_get_orders()` so they use
  High-Performance Order Storage, not slow `wp_postmeta` scans.

## Best Practices

- Use `wc_get_products()` / `wc_get_orders()` with explicit `limit`, `status`, and
  `return => 'ids'` when you only need IDs; hydrate objects only when required.
- Kill N+1s: fetch IDs in one query, then batch-load with a single `_prime_*` /
  `update_meta_cache()` pass instead of touching the DB inside the loop.
- Cache read-heavy, tolerably-stale data with the Transients API
  (`get_transient`/`set_transient`) and a sensible TTL; invalidate on the relevant
  `save_post`/order hook.
- Keep hooks like `woocommerce_before_calculate_totals` and
  `woocommerce_cart_calculate_fees` cheap — they run on every cart mutation. No remote
  calls, no per-item queries there.
- Serve page/fragment cache for anonymous traffic (full-page cache or a CDN), and mark
  cart/checkout/my-account as **never cached**.
- Never disable the object cache or set `WP_DEBUG` / `SAVEQUERIES` on in production;
  they add per-query overhead.
- Exclude cart, checkout, account, and REST/AJAX from any full-page cache, or you serve
  one shopper's cart to another.

## Examples

**Good Example** — one bounded query, batched meta, cached result

```php
// Fetch IDs once, prime meta in a single pass, then read from cache in the loop.
function acme_featured_skus(): array {
    $cached = get_transient( 'acme_featured_skus' );
    if ( false !== $cached ) {
        return $cached; // Skip the DB entirely on the common path.
    }

    $ids = wc_get_products( [
        'featured' => true,
        'limit'    => 20,       // Bounded — never -1 on a page render.
        'return'   => 'ids',    // Don't hydrate full objects to read one field.
    ] );
    update_meta_cache( 'post', $ids ); // One query warms meta for all 20 products.

    $skus = array_map( fn( $id ) => get_post_meta( $id, '_sku', true ), $ids ); // cache hits
    set_transient( 'acme_featured_skus', $skus, HOUR_IN_SECONDS );
    return $skus;
}
```

**Bad Example** — N+1 query, unbounded fetch, no cache

```php
function acme_featured_skus(): array {
    // BAD: limit => -1 loads the entire catalog into memory; OOMs as it grows.
    $products = wc_get_products( [ 'featured' => true, 'limit' => -1 ] );

    $skus = [];
    foreach ( $products as $product ) {
        // BAD: a fresh DB query per product (N+1); 10k products = 10k queries per request.
        $skus[] = get_post_meta( $product->get_id(), '_sku', true );
    }
    return $skus; // BAD: recomputed on every single request — no caching.
}
```

## Common Mistakes

- `limit => -1` / `posts_per_page => -1` on a user-facing query, scaling with catalog
  size until timeout.
- Querying meta inside a loop instead of priming it once (the N+1 pattern).
- Running remote HTTP calls or heavy work inside per-request hooks like
  `before_calculate_totals`.
- No persistent object cache, so every request re-hits the database for options and meta.
- Full-page caching cart/checkout/account pages, serving stale or cross-shopper data.
- Querying orders via `wp_postmeta` instead of `wc_get_orders()` with HPOS.

## Production Tips

- Turn on Redis/Memcached object caching and confirm it is actually used
  (`wp_using_ext_object_cache()` returns true).
- Profile with Query Monitor in staging to find slow and duplicated queries before they
  reach production; alert on p95 page time and DB query counts.
- Schedule heavy work (reports, syncs) via Action Scheduler off the request path rather
  than inline on page load — see scaling.

## AI Review Checklist

- Does every product/order query pass an explicit, non-`-1` `limit`?
- Are there any DB/meta calls inside a loop that should be batched or primed?
- Is expensive, reusable computation cached (transient/object cache) with invalidation?
- Do per-request hooks avoid remote calls and per-item queries?
- Are cart, checkout, account, and REST/AJAX excluded from full-page caching?
- Is a persistent object cache enabled and are orders queried via HPOS?

## Related

- `knowledge/woocommerce/24-scaling.md`
- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/13-rest-api.md`
- `knowledge/woocommerce/01-architecture.md`
- `knowledge/woocommerce/100-common-antipatterns.md`
