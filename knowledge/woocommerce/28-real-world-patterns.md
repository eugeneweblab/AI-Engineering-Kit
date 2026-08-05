---
id: woocommerce/28-real-world-patterns
topic: woocommerce
slug: real-world-patterns
title: "WooCommerce Real World Patterns"
type: doc
order: 28
status: ready
tags: [woocommerce, real-world-patterns, add_action, create_order, ERP_Client, wp_postmeta, as_enqueue_async_action, wp_posts]
related: [woocommerce/05-orders, woocommerce/12-hooks, woocommerce/13-rest-api, woocommerce/24-scaling, woocommerce/25-best-practices]
when_to_use: "Read before implementing a common store customization — custom order status, ERP sync, programmatic orders, or checkout fields."
---
# WooCommerce Real World Patterns

## Purpose

This document collects the customizations almost every non-trivial WooCommerce store needs —
a custom order status, programmatic order creation, syncing orders to an external system, and
adding checkout data — with the correct, upgrade-safe way to build each. These are the shapes
that recur; getting them right once prevents the same bugs from reappearing per project.

## Why It Matters

Most WooCommerce work is not net-new invention; it is wiring the store into a business:
an ERP, a 3PL, a subscription flow, a custom fulfilment state. There is a right way and a
tempting wrong way for each, and the wrong way (raw SQL, synchronous API calls, editing core)
looks fine in a demo and fails in production under HPOS, updates, or load. Learning the canonical
pattern means your integration is HPOS-safe, retryable, and survives the next update.

## Core Principles

- **Compose with the CRUD API and hooks.** Build orders, statuses, and fields with the
  documented objects and events — never by writing tables directly.
- **Make integrations async and idempotent.** External sync runs in Action Scheduler, retries
  safely, and re-running it does not double-post.
- **Model state as order status, not scattered meta.** A real workflow step is a registered
  status with transitions, not a boolean flag someone forgets to check.
- **Keep the source of truth in one place.** Inventory, price, and status have one owner; the
  integration mirrors it, it does not fork it.
- **Fail loudly to the operator, gracefully to the shopper.** Log and alert on integration
  failure; never surface a stack trace at checkout.

## Best Practices

- Register **custom order statuses** with `register_post_status()` and add them via
  `wc_order_statuses` so they appear in reports, bulk actions, and emails.
- Create orders programmatically with **`wc_create_order()`** / the order CRUD, calling
  `calculate_totals()` and `save()` — never insert into `wp_posts` yourself.
- Sync to external systems from **status-transition hooks** into an **Action Scheduler** job,
  keyed by order id so retries are idempotent.
- Store an **external reference** (`_erp_id`) on the order via CRUD meta to detect and skip
  already-synced orders.
- Add checkout data through the **Store API / block checkout** additional-fields API on
  modern stores; use `woocommerce_checkout_create_order` to persist it via CRUD.
- Query orders for automation with **`wc_get_orders()`** and status/date args — HPOS-safe and
  paginated — not `get_posts()`.

## Examples

**Good Example** — register a status and sync it idempotently

```php
// 1) A real workflow step, visible in reports and bulk actions.
add_action( 'init', function () {
    register_post_status( 'wc-awaiting-erp', [
        'label'                     => _x( 'Awaiting ERP', 'Order status', 'acme' ),
        'public'                    => false,
        'show_in_admin_status_list' => true,
        'label_count'               => _n_noop( 'Awaiting ERP (%s)', 'Awaiting ERP (%s)', 'acme' ),
    ] );
} );
add_filter( 'wc_order_statuses', function ( $statuses ) {
    $statuses['wc-awaiting-erp'] = _x( 'Awaiting ERP', 'Order status', 'acme' );
    return $statuses;
} );

// 2) On payment, enqueue an async sync; the job is safe to retry.
add_action( 'woocommerce_order_status_processing', function ( $order_id ) {
    as_enqueue_async_action( 'acme_push_to_erp', [ 'order_id' => $order_id ], 'erp' );
} );
add_action( 'acme_push_to_erp', function ( $order_id ) {
    $order = wc_get_order( $order_id );
    if ( ! $order || $order->get_meta( '_erp_id' ) ) {
        return;                                   // missing or already synced → idempotent
    }
    $erp_id = ERP_Client::create_order( $order ); // slow/failing call is safe here
    $order->update_meta_data( '_erp_id', $erp_id );
    $order->save();                               // one CRUD write, HPOS-safe
} );
```

**Bad Example** — synchronous, non-idempotent, HPOS-blind

```php
add_action( 'woocommerce_checkout_order_processed', function ( $order_id ) {
    global $wpdb;
    // Blocks checkout on the ERP, has no dedupe (a retry double-creates the order),
    // and writes meta with raw SQL that HPOS order tables never see.
    $erp_id = ERP_Client::create_order( $order_id );
    $wpdb->query( "INSERT INTO wp_postmeta (post_id, meta_key, meta_value)
                   VALUES ($order_id, '_erp_id', '$erp_id')" );
} );
```

## Common Mistakes

- Modeling workflow state as a meta flag instead of a registered order status, so reports and
  bulk actions do not see it.
- Building orders by inserting into `wp_posts`/`wp_postmeta` instead of `wc_create_order()`.
- Synchronous external calls in checkout hooks that block the shopper and lose orders on outage.
- Non-idempotent sync jobs that double-post to the ERP on a retry.
- Querying orders with `get_posts()`/`WP_Query` under HPOS, hitting the slow compat path.
- Storing integration data with raw SQL that CRUD and HPOS cannot read back.
- Surfacing integration errors to the customer at checkout instead of logging and alerting.

## Production Tips

- Give every integration an **admin-visible sync status** (a column or order note) so support
  can see which orders failed to push, using the logging from [debugging](26-debugging.md).
- Provide a **manual re-sync** bulk action; idempotent jobs make "just re-run it" the standard
  recovery for a transient ERP outage.

## AI Review Checklist

- Are workflow steps modeled as registered order statuses, not loose meta flags?
- Are orders created with `wc_create_order()`/CRUD and `calculate_totals()`, not raw inserts?
- Do external integrations run async via Action Scheduler, off the checkout path?
- Are sync jobs idempotent, keyed by order id or an external-reference guard?
- Is all order data read/written through CRUD so it is HPOS-safe?
- Are order queries done with `wc_get_orders()` rather than `WP_Query`/`get_posts`?
- Do integration failures log and alert instead of surfacing to the shopper?

## Related

- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/13-rest-api.md`
- `knowledge/woocommerce/24-scaling.md`
- `knowledge/woocommerce/25-best-practices.md`
