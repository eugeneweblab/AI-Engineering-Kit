---
id: woocommerce/24-scaling
topic: woocommerce
slug: scaling
title: "Scaling"
type: doc
order: 24
status: ready
tags: [woocommerce, scaling]
related: [woocommerce/15-performance, woocommerce/23-monitoring, woocommerce/13-rest-api, woocommerce/22-deployment, woocommerce/27-production]
when_to_use: "Read before a store's traffic, catalog, or order volume grows past what a single tuned server handles."
---
# Scaling

## Purpose

This document defines how to scale a WooCommerce store — more concurrent shoppers,
larger catalogs, and higher order volume — without rewriting it. It covers where load
actually lands (the database and PHP), and which layers you add cache, replicas, and
async processing to. Scaling is distinct from [performance](15-performance.md) tuning:
performance makes one request faster; scaling keeps thousands of them fast at once.

## Why It Matters

WooCommerce runs on WordPress, so every uncached request boots the full PHP stack and
hits MySQL. The parts that *cannot* be page-cached — cart, checkout, and My Account —
are exactly the parts that convert revenue. A flash sale or a large catalog import will
overwhelm the database long before it overwhelms bandwidth. If you scale the wrong layer
(more web servers behind a single database), you spend money and still fall over. Scale
the layer that is actually saturated, and prove it with metrics first.

## Core Principles

- **The database is the bottleneck, not PHP.** WooCommerce reads and writes to MySQL on
  every dynamic request. Add caching and replicas before adding web servers.
- **Cache in layers, and know what each layer skips.** Page cache serves static pages;
  a persistent object cache (Redis) serves query results to logged-in and cart pages.
- **Move work out of the request.** Anything that does not need to finish before the
  response — emails, ERP sync, report generation — belongs in Action Scheduler.
- **Use HPOS.** High-Performance Order Storage stores orders in dedicated tables, not
  `wp_posts`/`wp_postmeta`. It is the single biggest lever for high order volume.
- **Scale reads horizontally, writes vertically.** Reads fan out to replicas; writes go
  to one primary. Checkout is write-heavy, so keep the primary healthy.

## Best Practices

- Enable a **persistent object cache** (Redis or Memcached) via a drop-in. Without it,
  every transient and option lookup is a database round-trip.
- Turn on **HPOS** and keep custom code compatible (`wc_get_orders()`, order CRUD — never
  `WP_Query` on `shop_order`). HPOS lets order queries scale independently of content.
- Serve a **full-page cache** (Varnish, a CDN, or a plugin) for catalog and home pages;
  exclude `cart`, `checkout`, `my-account`, and any page reading `WC()->session`.
- Offload async work to **Action Scheduler** with bounded batches; do not fire external
  HTTP calls inside checkout hooks.
- Add **read replicas** for reporting and admin list tables; route writes to the primary.
- Keep **autoloaded options small** — audit `wp_options` where `autoload='yes'`; a bloated
  autoload set is loaded on *every* request.
- Put media and static assets on a **CDN**; do not serve product images from origin PHP.
- Load-test cart and checkout paths (k6, Locust) against production-like data, not an
  empty store — an empty catalog hides every slow query.

## Examples

**Good Example** — offload a slow external sync to Action Scheduler

```php
// Checkout returns immediately; the ERP push runs in a background batch,
// retries on failure, and never blocks the customer's order confirmation.
add_action( 'woocommerce_order_status_processing', function ( $order_id ) {
    as_enqueue_async_action( 'erp_sync_order', [ 'order_id' => $order_id ], 'erp' );
} );

add_action( 'erp_sync_order', function ( $order_id ) {
    $order = wc_get_order( $order_id );          // HPOS-safe CRUD lookup
    if ( ! $order ) {
        return;                                   // order gone; let the action end cleanly
    }
    ERP_Client::push( $order );                   // safe to be slow / to throw and retry
} );
```

**Bad Example** — synchronous external call inside checkout

```php
add_action( 'woocommerce_checkout_order_processed', function ( $order_id ) {
    $order = wc_get_order( $order_id );
    // Blocks the customer on a third-party API. Every ERP slowdown becomes a
    // checkout slowdown; an ERP outage becomes lost orders under load.
    ERP_Client::push( $order );
} );
```

## Common Mistakes

- Adding web servers while a single MySQL primary is the actual bottleneck.
- Running without a persistent object cache, so transients hit the database every time.
- Page-caching cart/checkout, leaking one customer's cart to the next visitor.
- Querying orders with `WP_Query`/`get_posts` under HPOS, forcing a slow compatibility path.
- Doing image resizing, PDF generation, or ERP calls inside the request instead of async.
- Letting autoloaded options grow to megabytes, taxing every single page load.
- Load-testing an empty store, so the queries that break at 100k products are never seen.

## Production Tips

- Watch the **slow query log** and MySQL `Threads_running` during peak; that is your
  real ceiling. Correlate spikes with the endpoints in [monitoring](23-monitoring.md).
- Keep the **Action Scheduler queue** drained — a growing `wc-action-scheduler` backlog
  means workers cannot keep up; add a dedicated cron/worker process.
- Cap `WP_CRON` jitter by disabling `DISABLE_WP_CRON` pseudo-cron and running a real
  system cron every minute, so background work is predictable under load.

## AI Review Checklist

- Is a persistent object cache (Redis/Memcached) configured, not just page cache?
- Is HPOS enabled and does all order code use CRUD (`wc_get_orders`, not `WP_Query`)?
- Are cart, checkout, and My Account excluded from full-page cache?
- Are external/slow operations offloaded to Action Scheduler, not run in checkout hooks?
- Are reads routed to replicas and writes to the primary where replication exists?
- Are autoloaded options audited and kept small?
- Was load testing done against production-scale data, not an empty catalog?

## Related

- `knowledge/woocommerce/15-performance.md`
- `knowledge/woocommerce/23-monitoring.md`
- `knowledge/woocommerce/13-rest-api.md`
- `knowledge/woocommerce/22-deployment.md`
- `knowledge/woocommerce/27-production.md`
