---
id: woocommerce/03-product-types
topic: woocommerce
slug: product-types
title: "Product Types"
type: doc
order: 3
status: ready
tags: [woocommerce, product-types]
related: [woocommerce/00-overview, woocommerce/01-architecture, woocommerce/04-product-management, woocommerce/05-orders, woocommerce/09-shipping]
when_to_use: "Read before creating or modeling a product, to choose the correct product type and class."
---
# Product Types

## Purpose

This document defines WooCommerce's built-in product types and when to use each, so an
agent models a catalog with the correct type instead of forcing everything into a simple
product. The type you pick determines the class, how price and stock behave, whether it
ships, and how it appears at checkout. Choosing wrong means brittle workarounds later.

## Why It Matters

Product type is a modeling decision, not a label. A "variable" product manages child
variations, each with its own SKU, price, and stock; a "simple" product cannot. Model a
t-shirt-with-sizes as a simple product and you will end up hacking stock and price logic
that the platform already provides for free — and get overselling and wrong prices as a
result. Because orders, shipping, tax, and inventory all branch on product type, the wrong
type propagates errors through the entire sale. Get the type right once and the rest of
WooCommerce does the work correctly.

## Core Principles

- **Four core types cover most catalogs.** `simple`, `variable`, `grouped`, and
  `external/affiliate`. Variations of a variable product are their own class
  (`WC_Product_Variation`).
- **Virtual and downloadable are flags, not types.** Any product can be marked *virtual*
  (no shipping) and/or *downloadable* (grants file access). They modify a type; they are
  not a separate type.
- **Variable ≠ grouped.** A variable product is one purchasable item with attribute-driven
  variations (size/color). A grouped product is a container listing several independently
  purchasable simple products.
- **External products are not sold on your store.** They link out to a third-party "Buy"
  URL and create no order or inventory locally.
- **Load with the factory.** `wc_get_product( $id )` returns the correct subclass; never
  instantiate `WC_Product` directly for a typed product.

## Best Practices

- Use `variable` whenever a single item has purchasable options (size, color); define the
  options as attributes marked "used for variations," then create the variations.
- Mark digital goods `virtual` + `downloadable` so they skip shipping and grant files on
  a completed/processing order.
- Reserve `grouped` for catalog presentation of related standalone products (e.g. a camera
  body plus lenses each sold separately), not for options of one product.
- Set stock and price on the *variation* for variable products, not only on the parent.
- Check `$product->get_type()` (or `is_type()`) before type-specific logic instead of
  assuming `simple`.

## Examples

**Good Example** — model sizes as a variable product

```php
$product = new WC_Product_Variable();
$product->set_name( 'Classic Tee' );

$attribute = new WC_Product_Attribute();
$attribute->set_name( 'Size' );
$attribute->set_options( [ 'S', 'M', 'L' ] );
$attribute->set_variation( true ); // marks it as driving variations
$product->set_attributes( [ $attribute ] );
$product->save();

$variation = new WC_Product_Variation();
$variation->set_parent_id( $product->get_id() );
$variation->set_attributes( [ 'size' => 'M' ] );
$variation->set_regular_price( '25.00' ); // per-variation price & stock — handled for you
$variation->set_stock_quantity( 40 );
$variation->set_manage_stock( true );
$variation->save();
```

**Bad Example** — sizes crammed into simple products

```php
// One simple product per size means duplicated data, no shared attribute UI,
// and a broken "out of stock" experience — the platform can't relate them.
$m = new WC_Product_Simple(); $m->set_name( 'Classic Tee - M' ); $m->save();
$l = new WC_Product_Simple(); $l->set_name( 'Classic Tee - L' ); $l->save();
// Customer sees three unrelated listings instead of one product with a size selector.
```

## Common Mistakes

- Using multiple simple products for what is one variable product with options.
- Confusing `grouped` (container of standalone products) with `variable` (options of one).
- Forgetting to set the variation's own price/stock, so it inherits nothing and shows
  "price on request" or oversells.
- Not marking digital products `virtual`, so WooCommerce charges shipping on a download.
- Instantiating `WC_Product` directly and losing type-specific behavior.

## Production Tips

- Variable products with dozens of variations are expensive to load; cap the variation
  count or split into separate products, and see `15-performance.md`.
- For subscriptions or bookings, use the dedicated extension types rather than bending a
  core type; see `19-subscriptions.md`.
- Validate that every variation of a variable product has a price before publishing;
  a priceless variation is unpurchasable.

## AI Review Checklist

- Is the chosen product type the natural fit (variable for options, grouped for bundles
  of standalone items, external for off-site links)?
- Are digital goods flagged `virtual` and `downloadable`?
- Do variable products define attributes with `set_variation(true)` and per-variation
  price/stock?
- Is the product loaded with `wc_get_product()` and type checked via `is_type()`?
- Does every variation have a price before the product is published?

## Related

- `knowledge/woocommerce/00-overview.md`
- `knowledge/woocommerce/01-architecture.md`
- `knowledge/woocommerce/04-product-management.md`
- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/09-shipping.md`
