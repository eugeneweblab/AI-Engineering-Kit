---
id: woocommerce/100-common-antipatterns
topic: woocommerce
slug: common-antipatterns
title: "Common Antipatterns"
type: doc
order: 100
status: ready
tags: [woocommerce, common-antipatterns]
related: [woocommerce/01-architecture, woocommerce/12-hooks, woocommerce/16-security, woocommerce/30-engineering-principles, woocommerce/99-ai-review-checklist]
when_to_use: "Read before customizing WooCommerce data access, checkout, or payments, to check you are not walking into a known trap."
---
# Common Antipatterns

## Purpose

This document catalogs the recurring WooCommerce mistakes an agent is most likely to make
or approve, and for each states *why it is wrong* and *the fix*. These are the patterns
that look reasonable in a clean test store and cost dearly beside real data, HPOS, and
other plugins. Recognizing the shape of a trap is faster than re-deriving why it hurts, so
use this as a lookup during design and [review](99-ai-review-checklist.md).

## Why It Matters

These antipatterns spread by copy-paste. One tutorial reads `_price` from post meta and a
thousand plugins inherit the bug; one gateway integration ignores webhook retries and every
fork double-charges. Because each instance "works" in the store where it was written,
nothing stops the spread until an upgrade, a traffic spike, or a duplicate webhook exposes
it in production. Naming the antipattern is what lets a reviewer reject it early, while it
is one instance and cheap to undo.

## Data-Access Antipatterns

### Reaching Around the CRUD API

- **What it is:** Reading or writing products and orders with `get_post_meta()`,
  `update_post_meta()`, or `$wpdb` instead of `wc_get_product()` / `wc_get_order()` and
  their setters.
- **Why it is wrong:** It skips price, tax, and stock logic, ignores the object cache, and
  breaks entirely under [HPOS](01-architecture.md), where orders no longer live in
  `wp_posts`/`wp_postmeta`. The code returns stale, wrong, or empty data with no error.
- **The fix:** Use CRUD objects and their getters/setters, then `->save()`. Drop to `$wpdb`
  only when profiling proves a hot path needs it, with `$wpdb->prepare()` and isolation.

### Racy Read-Modify-Write on Stock

- **What it is:** `get_post_meta('_stock')`, subtract, `update_post_meta()` — implementing
  inventory by hand.
- **Why it is wrong:** Two concurrent orders both read the same starting value and both
  write the decremented one, overselling the item. There is no lock.
- **The fix:** Let WooCommerce manage stock (`wc_reduce_stock_levels( $order )`,
  `$product->set_stock_quantity()` inside the order flow), which handles atomicity.

## Trust & Money Antipatterns

### Trusting Client-Supplied Prices

- **What it is:** Taking a price, line total, quantity, or discount from `$_POST`/request and
  using it to build the order or charge.
- **Why it is wrong:** The browser is hostile input; a user can set their own price or
  quantity. Prices and totals are server-side *state*, not display values to accept back.
- **The fix:** Recompute every money value through the cart/order API on the server; the
  client may only supply *which* product and *how many* — never the amount (see
  [checkout](07-checkout.md)).

### Non-Idempotent Payment Handlers

- **What it is:** A webhook/IPN handler that captures payment, reduces stock, or fulfills on
  every delivery, assuming exactly-once.
- **Why it is wrong:** Gateways retry on timeout, so the same `payment_intent.succeeded`
  arrives twice and the order is double-fulfilled or double-refunded.
- **The fix:** Make handlers idempotent — key on the transaction ID, check the order's
  current status, and no-op if the action already happened (see [payments](08-payments.md)).

## Extension Antipatterns

### Editing Core Instead of Using Hooks

- **What it is:** Changing WooCommerce plugin files or parent-theme templates directly to
  alter behavior.
- **Why it is wrong:** The next `wp update` overwrites the change without warning, silently
  reintroducing the old behavior — a regression no one can trace to a diff.
- **The fix:** Deliver every customization through an action or filter, or a child-theme
  template override that is version-checked on upgrade (see [hooks](12-hooks.md)).

### Heavy Work Inside Request Hooks

- **What it is:** Running an external API sync, a bulk update, or a slow report query inside
  a checkout hook or `init`/page-load hook.
- **Why it is wrong:** It blocks the customer's request, times out under load, and can lock
  the orders table during a sale.
- **The fix:** Enqueue the work into **Action Scheduler** and process it in batches off the
  request (see [performance](15-performance.md)).

### Ignoring Block (Store API) Checkout

- **What it is:** A customization that only hooks the legacy shortcode checkout form.
- **Why it is wrong:** New stores ship the block checkout, which runs on the Store API and
  does not fire the old form hooks — the customization silently does nothing there.
- **The fix:** Target the Store API / block checkout (and the shortcode path only if it is
  still in use); test on the checkout customers actually see.

## Security Antipatterns

### Skipping Nonces, Capabilities, and Escaping

- **What it is:** An admin action or AJAX/REST route that changes data without verifying a
  nonce and `current_user_can()`, or that echoes unescaped values.
- **Why it is wrong:** It opens CSRF, privilege escalation, and XSS — WooCommerce is
  WordPress, so WordPress's security rules are not optional (see [security](16-security.md)).
- **The fix:** Verify a nonce and capability on every state change, sanitize input on the
  way in, escape on output, and give every REST/Store API route a real `permission_callback`.

## Example — the client-price trap and its fix

```php
// Bad: builds the order from a price the browser sent. A user edits the request
// and buys a $900 item for $9. The total is attacker-controlled.
$item_total = (float) $_POST['price'] * (int) $_POST['qty']; // hostile input
$order->add_product( wc_get_product( $id ), $qty, [ 'total' => $item_total ] );

// Good: the client chooses the product and quantity; WooCommerce computes the price,
// applying sale, tax, and currency rules. Nothing money-related comes from the client.
$order->add_product( wc_get_product( $id ), absint( $_POST['qty'] ) );
$order->calculate_totals(); // server is the source of truth for money
```

## Common Mistakes

- Querying `wp_posts`/`wp_postmeta` for orders after HPOS moved them to custom tables.
- Hand-rolling stock decrements instead of using `wc_reduce_stock_levels()`, causing oversell.
- Accepting a price, total, or discount from the request instead of recomputing it.
- Webhook handlers with no idempotency, double-charging on gateway retries.
- Editing core/theme-parent files for something a hook could do.
- Missing `permission_callback`, nonce, or capability check on a data-changing route.

## AI Review Checklist

- Does any code read/write products or orders via raw meta or `$wpdb`? (Reject unless
  profiled and isolated.)
- Is stock changed with a read-modify-write on meta instead of WooCommerce's methods?
- Is any price, total, or quantity trusted from the client rather than recomputed?
- Are payment/webhook handlers idempotent against duplicate deliveries?
- Is any customization a core/template edit an update will revert, or does it ignore block
  checkout?
- Does every state-changing route verify nonce, capability, and escape its output?

## Related

- `knowledge/woocommerce/01-architecture.md`
- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/30-engineering-principles.md`
- `knowledge/woocommerce/99-ai-review-checklist.md`
