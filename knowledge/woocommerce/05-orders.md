---
id: woocommerce/05-orders
topic: woocommerce
slug: orders
title: "Orders"
type: doc
order: 5
status: ready
tags: [woocommerce, orders, processing, update_post_meta, WP_User, calculate_totals, add_product, update_status]
related: [woocommerce/00-overview, woocommerce/01-architecture, woocommerce/04-product-management, woocommerce/08-payments, woocommerce/18-emails]
when_to_use: "Read before writing code that creates, reads, updates, or transitions the status of orders."
---
# Orders

## Purpose

This document defines the WooCommerce order lifecycle and how to work with orders in code:
statuses and their meaning, the CRUD API for reading and mutating orders, and the events
that fire on status transitions. Orders are the record of money changing hands, so this is
the highest-stakes data in the store — correctness here is non-negotiable.

## Why It Matters

An order ties together payment, inventory, fulfillment, tax, and customer communication. A
status set incorrectly can charge a card without reserving stock, ship an unpaid order, or
suppress the receipt email — each a real financial or trust failure. Since HPOS, orders
live in dedicated tables and *must* be accessed through the CRUD API; code that queries
`wp_posts` returns nothing on modern stores. And because status transitions fire hooks that
trigger emails, stock changes, and payment capture, forcing a status by writing meta
skips all of it and leaves the order half-processed. The lifecycle is the contract.

## Core Principles

- **Statuses are a state machine.** The core flow is `pending` → `processing`/`on-hold` →
  `completed`, with `cancelled`, `refunded`, and `failed` as terminal branches. Payment
  gateways and fulfillment move orders between these; don't skip states.
- **Transition with `update_status()`, never by writing meta.** `update_status()` persists
  the change *and* fires `woocommerce_order_status_*` hooks that drive stock, email, and
  capture. `set_status()` without `save()` fires nothing.
- **Read and query through the API.** `wc_get_order( $id )` and `wc_get_orders( $args )`
  are HPOS-safe; `WP_Query`/`$wpdb` on `shop_order` are not.
- **Totals are computed, not assigned.** Add line items, then call `calculate_totals()`;
  never set `_order_total` by hand.
- **`processing` means paid.** For most gateways, `processing` (or `completed` for virtual
  goods) is the "payment received" state that reduces stock and sends the receipt.

## Best Practices

- Create programmatic orders with `wc_create_order()`, add products via `add_product()`,
  then `calculate_totals()` and `save()`.
- Pass a note to `update_status()` (e.g. `update_status( 'completed', 'Shipped via UPS' )`)
  so the order timeline records why it moved.
- Distinguish guest orders (no user id) from customer orders; read the customer via
  `get_customer_id()` / billing fields, not by assuming a `WP_User` exists.
- Use order notes (`add_order_note()`) for audit trail; use meta only for structured
  integration data, vendor-prefixed.
- Hook `woocommerce_order_status_completed` (etc.) for side effects instead of polling for
  status changes.

## Examples

**Good Example** — create an order and transition it properly

```php
$order = wc_create_order();
$order->add_product( wc_get_product( 42 ), 2 ); // qty 2; line totals derived from product
$order->set_address( $billing, 'billing' );
$order->calculate_totals();                     // computes item, tax, shipping totals
$order->save();

// Fires status hooks → stock reduced, receipt emailed, gateway capture triggered.
$order->update_status( 'processing', 'Payment confirmed by gateway webhook.' );
```

**Bad Example** — forcing status via meta, hand-set total

```php
// Assumes orders are posts (empty under HPOS) and writes status as raw meta:
// no hooks fire, so no stock reduction, no email, no payment capture.
update_post_meta( $order_id, '_order_status', 'wc-completed' );
update_post_meta( $order_id, '_order_total', '50.00' ); // arbitrary, unverified total
```

## Common Mistakes

- Setting order status by writing meta, so stock/email/capture side effects never run.
- Querying orders through `WP_Query`/`$wpdb`, returning nothing on HPOS stores.
- Hand-assigning `_order_total` instead of calling `calculate_totals()`.
- Marking an order `completed` before payment clears, shipping unpaid goods.
- Assuming every order has a `WP_User`, breaking on guest checkouts.
- Doing fulfillment work in a page request instead of on a status-transition hook.

## Production Tips

- Make status-transition side effects idempotent; gateways retry webhooks, and the same
  `processing` transition can fire more than once.
- Never delete orders for GDPR/accounting; use WooCommerce's anonymization and refund flows
  instead so records stay intact.
- Reconcile order totals against gateway settlement reports; a mismatch signals a
  miscomputed total or a skipped `calculate_totals()`.
- For high volume, move fulfillment and export work to a queue keyed on order id; see
  `24-scaling.md`.

## AI Review Checklist

- Are status changes done via `update_status()` (with a note), never by writing meta?
- Are orders read/queried with `wc_get_order()` / `wc_get_orders()` (HPOS-safe)?
- Are totals produced by `calculate_totals()` rather than assigned directly?
- Is `processing`/`completed` set only after payment is confirmed?
- Does order code handle guest orders with no user id?
- Are status-hook side effects idempotent against retried webhooks?

## Related

- `knowledge/woocommerce/00-overview.md`
- `knowledge/woocommerce/01-architecture.md`
- `knowledge/woocommerce/04-product-management.md`
- `knowledge/woocommerce/08-payments.md`
- `knowledge/woocommerce/18-emails.md`
