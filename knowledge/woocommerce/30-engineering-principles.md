---
id: woocommerce/30-engineering-principles
topic: woocommerce
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [woocommerce, engineering-principles]
related: [woocommerce/01-architecture, woocommerce/12-hooks, woocommerce/25-best-practices, woocommerce/16-security, woocommerce/100-common-antipatterns]
when_to_use: "Read before making any non-trivial WooCommerce design decision, so choices are reasoned against the platform's conventions rather than guessed."
---
# Engineering Principles

## Purpose

This document defines the durable principles that govern *how* to build on WooCommerce —
the reasoning an agent applies before touching a product, an order, the cart, or a
payment. The concrete docs ([hooks](12-hooks.md), [orders](05-orders.md),
[payments](08-payments.md)) tell you *what* API to call; this tells you *whether* and
*why*, so an extension survives a WooCommerce update, an HPOS migration, and a plugin
running next to it. Read it before the pattern docs.

## Why It Matters

WooCommerce is a shared runtime. Your code runs inside WordPress, beside the theme, the
payment gateway plugin, the shipping plugin, and forty hooks you did not write. It also
moves money and inventory, so a wrong write is not a cosmetic bug — it is a double charge,
an oversold item, or a leaked address. The platform already solved these problems with
CRUD objects, hooks, and data stores. Every time you go around them (raw SQL, direct
`$_POST` reads, direct post-meta writes) the code appears to work in your test store and
then breaks caching, High-Performance Order Storage, or a neighboring extension in
production. These principles keep you on the path the platform maintains for you.

## Core Principles

- **Go through the API, never around it.** Read and write products and orders with CRUD
  objects (`wc_get_product()`, `wc_get_order()`, `$order->save()`), never with
  `get_post_meta()` or `$wpdb`. The API is the only layer that stays correct across HPOS,
  object caching, and version upgrades. The cost is a few more lines; the payoff is code
  that does not silently break when storage changes.
- **Extend with hooks, never by editing core.** All customization goes through actions and
  filters. Editing a WooCommerce or WordPress file works until the next `wp update`, which
  reverts it without warning. The cost of a hook is finding the right one; the cost of a
  core edit is a regression no one can trace.
- **Never trust anything the browser sent.** Prices, totals, quantities, and coupon values
  are *state*, computed server-side through the API — not display values to accept back.
  Recompute on the server every time. The cost is one lookup; the alternative is a customer
  setting their own price.
- **Prices and stock are shared state — mutate them transactionally.** Stock reduction,
  order status transitions, and payment capture race with other requests and webhooks.
  Use WooCommerce's own methods (`wc_reduce_stock_levels()`, order status setters) that
  handle locking and idempotency, rather than read-modify-write on meta.
- **Treat WooCommerce as WordPress.** Products are a custom post type; customers are
  WordPress users. Nonces, capability checks, escaping on output, and sanitizing on input
  all apply. There is no separate "WooCommerce security" — it is WordPress security.
- **Pin and target explicit versions.** WooCommerce changes defaults between majors (HPOS,
  block checkout, Store API shape). Code that assumes "current behavior" without stating
  the version it targets breaks on upgrade.

## Best Practices

- Before writing a data mutation, ask "does a CRUD setter exist for this?" It almost always
  does (`$product->set_stock_quantity()`, `$order->update_status()`); reach for `$wpdb`
  only when profiling proves the CRUD path is the bottleneck, and isolate it if you must.
- Prefer the highest-level hook that fits. A filter on `woocommerce_product_get_price` is
  narrower and safer than intercepting the whole template; template overrides are the last
  resort and must be version-checked against the plugin's template on every upgrade.
- Make webhook and payment handlers **idempotent**. Gateways retry; the same
  `payment_intent.succeeded` can arrive twice. Key on the transaction ID and no-op if the
  order is already paid.
- Escape on output, sanitize on input, verify a nonce on every state-changing request.
  Use `wc_get_template()` and the `esc_*`/`wp_kses` family rather than echoing raw values.
- Do expensive work off the request. Long report queries, external syncs, and bulk updates
  belong in Action Scheduler jobs, not in a checkout or page-load hook.
- Design for the block (Store API) checkout as the default, not the legacy shortcode. New
  stores ship block checkout; a customization that only hooks the old form silently does
  nothing there.

## Examples

**Good Example** — a price change through the correct filter, computed server-side

```php
// Adjust price via the documented filter. WooCommerce still owns tax, currency,
// and sale logic; we only change the base number, and only on the server.
add_filter( 'woocommerce_product_get_price', function ( $price, $product ) {
    if ( has_term( 'clearance', 'product_cat', $product->get_id() ) ) {
        return (string) round( (float) $price * 0.9, wc_get_price_decimals() );
    }
    return $price; // untouched otherwise — never trust a price from the client
}, 10, 2 );
```

**Bad Example** — raw meta write that races and bypasses the platform

```php
// Reads and writes stock directly on post meta. Not HPOS-safe, not cache-aware,
// and a read-modify-write with no lock: two concurrent orders both read 1,
// both write 0, and the item is oversold. Editing core would be even worse.
$stock = (int) get_post_meta( $product_id, '_stock', true );
update_post_meta( $product_id, '_stock', $stock - 1 ); // silent data corruption
```

## Common Mistakes

- Reading or writing orders via `wp_posts`/`wp_postmeta` after HPOS moved them to custom
  order tables — the code compiles and returns stale or empty data.
- Trusting a cart total, line price, or quantity from the request instead of recomputing
  through the cart/order API.
- Editing plugin or theme-parent files for a customization that a hook could deliver.
- Non-idempotent payment webhook handlers that capture or fulfill twice on a retry.
- Skipping nonce and capability checks because "it's just a WooCommerce admin action".
- Building against the shortcode checkout only, so block-checkout stores get none of the
  customization.

## Production Tips

- Log order state *transitions* and payment events, never card data or full PII; alert on
  stuck "pending payment" orders, which usually signal a webhook that never landed.
- Run bulk product and order updates through Action Scheduler with batching, so a 50k-row
  update does not time out the request or lock the orders table.
- Keep a staging store on the exact production WooCommerce/WordPress/PHP versions and run
  the HPOS and block-checkout paths there before shipping.

## AI Review Checklist

- Does the code read and write products and orders through CRUD objects, not raw meta/SQL?
- Is every customization delivered via a hook rather than a core-file or template edit
  that an update will revert?
- Are prices, totals, and quantities recomputed server-side, never trusted from the client?
- Are payment and webhook handlers idempotent against retries and duplicate deliveries?
- Are nonces, capability checks, and output escaping applied to every state change?
- Are the targeted WooCommerce, WordPress, and PHP versions stated, and does the code work
  under HPOS and block checkout?

## Related

- `knowledge/woocommerce/01-architecture.md`
- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/25-best-practices.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/100-common-antipatterns.md`
