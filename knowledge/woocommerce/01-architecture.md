---
id: woocommerce/01-architecture
topic: woocommerce
slug: architecture
title: "Architecture"
type: doc
order: 1
status: ready
tags: [woocommerce, architecture]
related: [woocommerce/00-overview, woocommerce/04-product-management, woocommerce/05-orders, woocommerce/12-hooks, woocommerce/13-rest-api]
when_to_use: "Read before writing any code that reads or writes WooCommerce products, orders, or store data."
---
# Architecture

## Purpose

This document defines how WooCommerce stores and exposes its data, so an agent reads and
writes it through the correct layer. It covers the CRUD object model, the data stores
behind it (including High-Performance Order Storage), the hook system, and how these map
onto WordPress. Get this wrong and code will appear to work in testing, then corrupt data
or silently stop reading orders after an upgrade.

## Why It Matters

WooCommerce deliberately hides its storage behind an abstraction. Products live in the
WordPress post tables; orders, since HPOS became the default in WooCommerce 8.2, live in
dedicated `wc_orders*` tables instead of `wp_posts`. The CRUD layer is what lets the same
`wc_get_order()` call work regardless of which storage is active. Code that bypasses it —
raw SQL, direct post-meta access — binds itself to one storage backend and breaks the
moment a store toggles HPOS or WooCommerce changes internals. The abstraction is not
optional politeness; it is the contract that keeps your code portable and upgrade-safe.

## Core Principles

- **CRUD objects are the public API.** `WC_Product`, `WC_Order`, `WC_Customer`, and their
  data stores are how you interact with data. Getters/setters plus `save()` — never touch
  the tables directly.
- **Data stores decouple objects from storage.** A CRUD object delegates persistence to a
  `WC_Data_Store`. This is why the same code works under legacy post storage and HPOS.
- **Hooks are the extension surface.** Actions let you run code at defined points; filters
  let you modify data in flight. This is the only supported way to change behavior.
- **WooCommerce sits on WordPress.** Products are the `product` custom post type; customers
  are `WP_User`s. WordPress's request lifecycle, capabilities, and hooks all apply.
- **Never assume the storage backend.** Query orders through `wc_get_orders()`, not
  `WP_Query` or `$wpdb`, because their table may be `wp_posts` or `wc_orders`.

## Best Practices

- Load objects with the factory functions (`wc_get_product()`, `wc_get_order()`); they
  return the correct subclass and use the active data store.
- Mutate through setters and call `save()` once at the end; batching one save is cheaper
  and keeps the object consistent.
- Declare HPOS compatibility in any custom plugin via
  `FeaturesUtil::declare_compatibility( 'custom_order_tables', __FILE__ )`; incompatible
  plugins force the store back to legacy storage.
- Use `wc_get_orders()` / `wc_get_products()` for queries instead of hand-written SQL.
- Namespace custom meta with a vendor prefix (e.g. `_acme_gift_note`) to avoid collisions.

## Examples

**Good Example** — storage-agnostic order query and update

```php
// wc_get_orders() runs against whatever data store is active (HPOS or legacy).
$orders = wc_get_orders( [
    'status' => 'processing',
    'limit'  => 20,
] );

foreach ( $orders as $order ) {
    $order->update_status( 'completed', 'Fulfilled by warehouse job.' );
    // update_status() persists and fires the right hooks/emails; no manual save needed.
}
```

**Bad Example** — hard-coded to legacy post storage

```php
// Assumes orders are posts. Returns nothing once HPOS is enabled, and writing
// _order_total directly skips totals recalculation and every order hook.
global $wpdb;
$ids = $wpdb->get_col(
    "SELECT ID FROM {$wpdb->posts} WHERE post_type = 'shop_order' AND post_status = 'wc-processing'"
);
update_post_meta( $ids[0], '_order_total', '0' ); // corrupts the order silently
```

## Common Mistakes

- Querying `wp_posts`/`wp_postmeta` for orders after HPOS moved them to custom tables.
- Writing product or order fields with `update_post_meta()` instead of setters + `save()`.
- Calling `save()` inside a loop for each setter, multiplying database writes.
- Shipping a plugin that never declares HPOS compatibility, silently disabling HPOS
  for the whole store.
- Assuming a customer is only a row in a WooCommerce table; they are WordPress users and
  guest checkouts have no user at all.

## Production Tips

- Check the store's active storage before debugging data issues: WooCommerce → Settings →
  Advanced → Features shows whether HPOS is on.
- When migrating a store to HPOS, run the built-in synchronization and verify the
  legacy/new tables match before disabling the old store.
- Cache expensive product/order reads at the object level; do not re-query per template.

## AI Review Checklist

- Are all product/order reads and writes done through CRUD objects and `save()`?
- Are order queries using `wc_get_orders()` rather than `WP_Query`/`$wpdb`?
- Does the code avoid assuming orders live in `wp_posts` (HPOS-safe)?
- Does any custom plugin declare `custom_order_tables` compatibility?
- Is custom meta vendor-prefixed to avoid collisions?
- Are setters batched into a single `save()` rather than saving repeatedly?

## Related

- `knowledge/woocommerce/00-overview.md`
- `knowledge/woocommerce/04-product-management.md`
- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/13-rest-api.md`
