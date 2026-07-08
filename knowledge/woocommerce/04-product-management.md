---
id: woocommerce/04-product-management
topic: woocommerce
slug: product-management
title: "Product Management"
type: doc
order: 4
status: ready
tags: [woocommerce, product-management]
related: [woocommerce/00-overview, woocommerce/01-architecture, woocommerce/03-product-types, woocommerce/05-orders, woocommerce/13-rest-api]
when_to_use: "Read before writing code that creates, updates, imports, or manages stock for products."
---
# Product Management

## Purpose

This document defines how to create, update, categorize, and manage stock for products
programmatically, so an agent's catalog code is correct and safe under concurrency. It
covers the product CRUD API, inventory operations, taxonomies, and bulk imports. Products
are the backbone of the catalog; sloppy writes here surface as wrong prices, oversold
stock, and broken product pages.

## Why It Matters

Product data is read on nearly every store page and written by imports, syncs, and admin
edits — often concurrently. Two failure modes dominate: bypassing the CRUD layer (which
skips price/tax/lookup-table logic and corrupts data) and mishandling stock under
concurrency (which oversells). Stock especially is a race condition waiting to happen: two
orders reading the same "1 left" and both succeeding. Using WooCommerce's atomic stock
operations and the CRUD API is what prevents these; hand-rolled meta writes reintroduce
every bug the platform already solved.

## Core Principles

- **Create and edit through CRUD objects.** Use `WC_Product_*` classes, setters, and one
  `save()`. Never `wp_insert_post()` + `update_post_meta()` to build a product.
- **Change stock atomically.** Use `wc_update_product_stock()` or
  `$product->set_stock_quantity()` guarded by the platform's reduce/restore helpers, not a
  read-modify-write on meta.
- **Categories and tags are taxonomies.** Assign them with the term API
  (`wp_set_object_terms`) or product setters, not by writing meta strings.
- **SKUs are unique keys.** Enforce uniqueness; a duplicate SKU throws and breaks imports.
- **Batch and defer for bulk work.** For imports, defer term/lookup recounts and save in
  batches; per-item full saves do not scale.

## Best Practices

- Set a canonical price with `set_regular_price()`; use `set_sale_price()` (with optional
  from/to dates) for promotions rather than overwriting the regular price.
- Enable `set_manage_stock( true )` and let WooCommerce decrement stock on order; only call
  stock helpers directly for syncs and corrections.
- Assign categories with `set_category_ids()` and attributes/global attributes via the
  proper taxonomy so filtering and lookup tables stay correct.
- Give every product a unique, stable SKU and treat it as the external identifier for
  imports and integrations.
- For imports, wrap batches, call `wc_defer_product_sync()` where appropriate, and prefer
  the REST API's batch endpoint for external sources (see `13-rest-api.md`).

## Examples

**Good Example** — create a product and adjust stock safely

```php
$product = new WC_Product_Simple();
$product->set_name( 'Ceramic Mug' );
$product->set_sku( 'MUG-CER-001' );        // unique external key
$product->set_regular_price( '12.00' );
$product->set_manage_stock( true );
$product->set_stock_quantity( 100 );
$product->set_category_ids( [ 15 ] );      // taxonomy term id, not a string
$product->save();                          // single write, fires product hooks

// Atomic decrement — safe when two requests hit the same product at once.
wc_update_product_stock( $product, 5, 'decrease' );
```

**Bad Example** — raw meta writes and a stock race

```php
$id = wp_insert_post( [ 'post_type' => 'product', 'post_title' => 'Ceramic Mug' ] );
update_post_meta( $id, '_price', '12.00' );          // skips tax/sale logic
update_post_meta( $id, '_sku', 'MUG-CER-001' );      // no uniqueness check

// Read-modify-write: two concurrent orders both read 100 and both write 99 → oversold.
$stock = (int) get_post_meta( $id, '_stock', true );
update_post_meta( $id, '_stock', $stock - 1 );
```

## Common Mistakes

- Building products with `wp_insert_post()`/`update_post_meta()` instead of the CRUD API.
- Read-modify-write stock updates that lose writes and oversell under concurrency.
- Overwriting `regular_price` to run a sale, losing the original price.
- Duplicate or missing SKUs that break imports and integrations.
- Assigning categories as meta strings instead of taxonomy terms, breaking filters.
- Full per-item saves during large imports, blowing the request time budget.

## Production Tips

- Regenerate the product lookup tables after bulk price/stock changes if you wrote outside
  the CRUD path; stale lookup tables cause wrong sort/filter results.
- Set a low-stock threshold and backorder policy per product so the store degrades
  predictably rather than silently overselling.
- Run large imports via WP-CLI or a queued background job, not a web request, to avoid
  timeouts; see `24-scaling.md`.
- Log stock changes with reason and actor for auditability during disputes.

## AI Review Checklist

- Are products created and updated exclusively through CRUD objects and `save()`?
- Are stock changes atomic (`wc_update_product_stock` / platform helpers), never
  read-modify-write on meta?
- Do sales use `set_sale_price()` rather than overwriting the regular price?
- Are SKUs unique and validated before save/import?
- Are categories/attributes assigned as taxonomy terms, not meta strings?
- Are bulk imports batched, deferred, and run outside a web request?

## Related

- `knowledge/woocommerce/00-overview.md`
- `knowledge/woocommerce/01-architecture.md`
- `knowledge/woocommerce/03-product-types.md`
- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/13-rest-api.md`
