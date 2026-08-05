---
id: woocommerce/00-overview
topic: woocommerce
slug: overview
title: "WooCommerce Overview"
type: doc
order: 0
status: ready
tags: [woocommerce, overview, wc_get_product, get_price, get_post_meta, wp_posts, wp_postmeta]
related: [woocommerce/01-architecture, woocommerce/02-installation, woocommerce/03-product-types, woocommerce/12-hooks, woocommerce/13-rest-api]
when_to_use: "Read first when starting any WooCommerce task, to orient yourself and find the right specific doc."
---
# WooCommerce Overview

## Purpose

This topic teaches an AI agent how to build, extend, and review WooCommerce stores
correctly. WooCommerce is a PHP plugin that turns WordPress into an e-commerce
platform: it adds products, a cart, checkout, orders, payments, shipping, and tax on
top of WordPress's post, user, and hook systems. This overview is a map — it tells you
which sibling doc owns which concern so you read the right one before writing code.

## Why It Matters

WooCommerce handles money, inventory, and customer PII, so mistakes are expensive in a
way that a blog plugin's are not: a double-charged order, an oversold item, or a leaked
address is a real-world failure, not a cosmetic bug. It is also deeply convention-bound.
The platform gives you CRUD objects, hooks, and data stores that must be used a specific
way; bypassing them (raw SQL, direct `$_POST` reads, direct post-meta writes) appears to
work and then breaks caching, High-Performance Order Storage (HPOS), and every other
extension on the site. Knowing the conventions is most of the job.

## Core Principles

- **Go through the API, never around it.** Read and write products and orders with the
  CRUD objects (`wc_get_product()`, `wc_get_order()`, `->save()`), never with raw
  `get_post_meta()`/`$wpdb`. The API is the only layer that stays correct across HPOS,
  caching, and version upgrades.
- **Extend with hooks, never by editing core.** WooCommerce and its updates will
  overwrite any change to plugin files. All customization goes through actions and
  filters (see `12-hooks.md`).
- **Treat WooCommerce as WordPress.** Products are a custom post type; customers are
  WordPress users. WordPress security, escaping, and nonce rules all apply.
- **Prices and stock are state, not display.** Compute them server-side through the API;
  never trust a total, price, or quantity that arrived from the browser.

## Best Practices

- Start every task by identifying the owning doc below, then read it before coding.
- Pin the WooCommerce and WordPress versions you target; APIs and defaults (HPOS, block
  checkout) change between major releases.
- Prefer official extensions and the REST/Store API over custom database work.
- When in doubt about a data write, ask "does a CRUD setter exist for this?" — it almost
  always does.

## Document Map

Read these in roughly this order; jump straight to the one that owns your task.

- **Foundations** — `01-architecture.md` (data model, CRUD, HPOS), `02-installation.md`
  (setup, environments, versions).
- **Catalog** — `03-product-types.md` (simple, variable, grouped, external),
  `04-product-management.md` (create/update products, stock, categories).
- **Selling** — `05-orders.md` (order lifecycle, statuses), `06-customers.md`,
  `07-checkout.md`, `08-payments.md`, `09-shipping.md`, `10-taxes.md`, `11-coupons.md`.
- **Extending** — `12-hooks.md` (actions/filters), `13-rest-api.md`, `14-headless.md`,
  `17-customization.md`, `18-emails.md`, `19-subscriptions.md`, `20-multisite.md`.
- **Operating** — `15-performance.md`, `16-security.md`, `21-testing.md` through
  `27-production.md`, `28-real-world-patterns.md`.
- **Standards** — `25-best-practices.md`, `29-ai-review.md`, `30-engineering-principles.md`,
  `98-production-checklist.md`, `99-ai-review-checklist.md`, `100-common-antipatterns.md`.

## Examples

**Good Example** — read a product through the API

```php
// wc_get_product() returns the right class (simple/variable/…) and is HPOS-safe.
$product = wc_get_product( $product_id );
if ( $product && $product->is_in_stock() ) {
    $price = $product->get_price(); // computed value, respecting sales and tax config
}
```

**Bad Example** — reaching around the API

```php
// Reads a raw meta value: skips price/tax logic, breaks if storage changes,
// and returns a bare string with no type or currency handling.
$price = get_post_meta( $product_id, '_price', true );
```

## Common Mistakes

- Editing core WooCommerce files instead of using hooks; updates silently revert them.
- Querying `wp_posts`/`wp_postmeta` for orders after HPOS moved them to custom tables.
- Trusting cart totals or prices sent from the client instead of recomputing server-side.
- Treating WooCommerce as separate from WordPress and skipping nonce/escaping rules.
- Not pinning versions, so a plugin update changes checkout or storage under you.

## AI Review Checklist

- Does the code read/write products and orders through CRUD objects, not raw meta/SQL?
- Is every customization delivered via a hook rather than a core-file edit?
- Are WordPress security rules (nonces, capability checks, escaping) applied?
- Did you consult the specific sibling doc that owns this task before writing code?
- Are target WooCommerce and WordPress versions pinned and stated?

## Related

- `knowledge/woocommerce/01-architecture.md`
- `knowledge/woocommerce/02-installation.md`
- `knowledge/woocommerce/03-product-types.md`
- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/13-rest-api.md`
