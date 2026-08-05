---
id: woocommerce/20-multisite
topic: woocommerce
slug: multisite
title: "WooCommerce Multisite"
type: doc
order: 20
status: ready
tags: [woocommerce, multisite, shop_order, switch_to_blog, restore_current_blog, get_var, wc_get_orders, wp_2_options]
related: [woocommerce/01-architecture, woocommerce/16-security, woocommerce/15-performance, woocommerce/22-deployment]
when_to_use: "Read before running WooCommerce on a WordPress Multisite network or writing code that touches more than one site."
---
# WooCommerce Multisite

## Purpose

This document defines how to run WooCommerce correctly on a WordPress Multisite network:
per-site data isolation, safe cross-site queries, plugin activation scope, and shared vs.
per-store configuration. It is written so an agent can build network features without
leaking one store's orders into another or corrupting the network on activation.

On Multisite, each site (blog) has its own table prefix (`wp_2_options`, `wp_2_posts`, …)
and therefore its own products, orders, customers, and settings. WooCommerce is a
per-site store, not a network-wide one. The network shares only the users table and a few
network tables. Understand this boundary before writing anything that spans sites — it is
the source of nearly every Multisite bug.

## Why It Matters

Multisite multiplies both the value and the danger of every mistake. A query that forgets
to switch context reads or writes the *wrong store's* orders — a data breach between
tenants who may be unrelated businesses. An activation routine that runs once instead of
per-site leaves half the network with missing tables and fatal errors on the storefront.
Because one code path executes across many stores with shared user identity but isolated
commerce data, a subtle context bug becomes a cross-tenant leak, and a naive network loop
becomes an O(sites) performance cliff. The failures are also uneven: they appear only on
site 37, not on your dev site, so they survive testing and surface in production.

## Core Principles

- **Each site owns its own commerce data.** Products, orders, and customers live in that
  site's prefixed tables. There is no shared order pool unless you build one deliberately.
- **Always switch context to touch another site.** Wrap cross-site work in
  `switch_to_blog()` / `restore_current_blog()`; never assume the current prefix.
- **Activation, tables, and upgrades run per site.** WooCommerce creates tables per site,
  so network activation must loop sites or defer table creation to first load.
- **Users are shared; capabilities are per site.** A user exists network-wide but their
  roles and `customer`/`shop_manager` capabilities are granted per site.
- **Restore context in `finally`.** A missing `restore_current_blog()` leaves the rest of
  the request pointed at the wrong store — the classic cross-tenant leak.

## Best Practices

- Decide activation scope explicitly: network-activate only if every site should be a
  store; otherwise activate per site. Handle `wp_insert_site` to provision new stores.
- Loop network sites with `get_sites()` and `switch_to_blog()`; pair every switch with a
  `restore_current_blog()`, ideally in a `try/finally`.
- Never build cross-site table prefixes by hand (`$wpdb->prefix . '2_posts'`); switch
  context and use the normal WooCommerce APIs so caches and hooks stay correct.
- Keep per-store settings in that site's options; reserve `get_site_option()` / network
  tables for genuinely network-wide config (license keys, shared feature flags).
- Be explicit about object caching: a shared cache backend must be keyed by blog id, which
  WordPress does by default — do not defeat it with global cache keys.
- Budget for scale: a network sync that loops thousands of sites belongs in a batched
  background job (Action Scheduler / WP-CLI), not a page load — see [performance](15-performance.md).
- Test cross-tenant isolation directly: create an order on site A, assert it is invisible
  from site B's queries — see [security](16-security.md).

## Examples

**Good Example** — switch context, restore in `finally`

```php
/** Return the pending-order count for one network store, safely. */
function my_store_pending_count( int $blog_id ): int {
    switch_to_blog( $blog_id );
    try {
        // Runs against this site's prefixed tables and object cache.
        return count( wc_get_orders( [
            'status' => 'pending',
            'limit'  => -1,
            'return' => 'ids',
        ] ) );
    } finally {
        // Restore ALWAYS, even on exception, or the rest of the request
        // keeps reading the wrong store's data.
        restore_current_blog();
    }
}
```

**Bad Example** — hand-built prefix, no context switch, no restore

```php
function my_store_pending_count( int $blog_id ): int {
    global $wpdb;
    // Hardcoding another site's prefix bypasses WooCommerce APIs, the object
    // cache, and HPOS — and silently returns stale or wrong-tenant rows.
    $prefix = $wpdb->base_prefix . $blog_id . '_';
    $rows = $wpdb->get_var( // no context switch: caps and hooks run as the wrong site
        "SELECT COUNT(*) FROM {$prefix}posts
         WHERE post_type = 'shop_order' AND post_status = 'wc-pending'"
    );
    // Assumes legacy CPT storage; on an HPOS store this reads nothing.
    return (int) $rows;
}
```

## Common Mistakes

- Touching another site's data by constructing its table prefix instead of switching context.
- Forgetting `restore_current_blog()`, leaving the request pointed at the wrong store.
- Network-activating WooCommerce without provisioning tables per site, so new sites fatal.
- Storing per-store settings in network options, so every store shares one config.
- Looping thousands of sites synchronously in a request instead of batching in the background.
- Assuming legacy `shop_order` CPT storage in raw SQL, which breaks under HPOS.
- Granting capabilities globally and assuming a shop manager on site A manages site B.

## Production Tips

- Provision new stores from a `wp_insert_site` handler so tables and defaults exist before
  the first storefront request; verify with a smoke test — see [deployment](22-deployment.md).
- Run network-wide maintenance with `wp ... --network` WP-CLI loops, not admin-page jobs,
  so a timeout does not half-complete the network.
- Monitor per-site health, not just the primary site; a broken site 37 will not show up in
  aggregate uptime checks.

## AI Review Checklist

- Does cross-site code use `switch_to_blog()` and restore context in a `finally`?
- Is there any hand-built cross-site table prefix that should be a context switch instead?
- Is plugin activation/table creation handled per site, including newly created sites?
- Are per-store settings in site options and only network-wide config in network options?
- Do network loops run batched in the background rather than in a web request?
- Do raw queries account for HPOS, or do they assume the legacy `shop_order` CPT?
- Is cross-tenant isolation tested (site A's orders invisible to site B)?

## Related

- `knowledge/woocommerce/01-architecture.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/15-performance.md`
- `knowledge/woocommerce/22-deployment.md`
