---
id: woocommerce/07-checkout
topic: woocommerce
slug: checkout
title: "Checkout"
type: doc
order: 7
status: ready
tags: [woocommerce, checkout, add_action, set_total, update_meta_data, sanitize_text_field, woocommerce_order_status_processing, woocommerce_checkout_create_order, customizing, blocks, fields]
related: [woocommerce/06-customers, woocommerce/08-payments, woocommerce/05-orders, woocommerce/16-security]
when_to_use: "Read before customizing checkout fields, validation, or the order-creation flow (Blocks or shortcode)."
---
# Checkout

## Purpose

This document defines how the WooCommerce checkout turns a cart into an order:
the two checkout surfaces (the Blocks/Store API checkout and the legacy `[woocommerce_checkout]`
shortcode), field customization, server-side validation, and the create-order flow.
It is written so an agent can extend checkout without breaking payments, tax, or the
order record.

Checkout is the single most fragile page in the store: it composes cart, customer,
shipping, tax, coupons, and payment into one atomic action. A change that "works" in
the browser can still silently drop a field from the order or bypass validation.

## Why It Matters

Everything the store earns passes through checkout, and every downstream document —
[payments](08-payments.md), [taxes](10-taxes.md), [shipping](09-shipping.md) — depends
on the data it captures. As of 2026 there are two distinct implementations: the default
**block checkout** (React front end talking to the **Store API**) and the older
**shortcode checkout** (server-rendered, `WC_Checkout`). Code written for one does not
automatically work on the other. Customizing the wrong layer, or validating only in
JavaScript, produces orders with missing or malformed data that you discover after the
customer has paid.

## Core Principles

- **Know which checkout you are on.** Block checkout extends via the
  `@woocommerce/blocks-checkout` API and Store API endpoints; shortcode checkout extends
  via `WC_Checkout` hooks. Do not mix them.
- **Validate on the server, always.** Client validation is UX; the server is the
  authority. Re-check every field in a server hook.
- **Never trust cart totals from the request.** WooCommerce recalculates the cart
  server-side; the price the client shows is advisory only.
- **Persist custom fields onto the order explicitly.** A field on the form does not
  reach the order unless you save it.
- **Keep checkout idempotent and side-effect-free until payment.** Do not ship, email,
  or fulfill from a checkout hook; wait for the paid status.

## Best Practices

- For block checkout, register custom fields with
  `woocommerce_register_additional_checkout_field()` (built-in persistence and
  validation), not by injecting raw HTML.
- For shortcode checkout, add fields via the `woocommerce_checkout_fields` filter and
  save them on `woocommerce_checkout_create_order` using `$order->update_meta_data()`.
- Put server validation in `woocommerce_after_checkout_validation` (shortcode) or the
  field's registered `validate_callback` (blocks); add errors with `wc_add_notice()` or
  a `WP_Error`.
- Let WooCommerce create the order — call `WC()->checkout()->process_checkout()` or the
  Store API; never hand-build a `WC_Order` mid-checkout.
- Rely on the framework's nonce/session handling; do not disable nonce checks to "fix"
  an AJAX error.
- Keep fulfillment logic on `woocommerce_order_status_processing`/`_completed`, not on
  checkout submission.

## Examples

**Good Example** — validate server-side, persist to the order (shortcode checkout)

```php
// Server-side validation is authoritative — runs even if JS was bypassed.
add_action( 'woocommerce_after_checkout_validation', function ( $data, $errors ) {
    if ( empty( $data['billing_vat'] ) && $data['billing_country'] === 'DE' ) {
        $errors->add( 'vat', __( 'VAT number is required for DE orders.', 'my-plugin' ) );
    }
}, 10, 2 );

// A form field reaches the order only when explicitly saved onto it.
add_action( 'woocommerce_checkout_create_order', function ( $order, $data ) {
    if ( ! empty( $data['billing_vat'] ) ) {
        $order->update_meta_data( '_billing_vat', sanitize_text_field( $data['billing_vat'] ) );
    }
}, 10, 2 );
```

**Bad Example** — client-only checks, trusting the posted total

```php
// Validation lives only in JavaScript, so a crafted POST skips it entirely.
add_action( 'woocommerce_checkout_create_order', function ( $order ) {
    // Trusting a total from the request lets the buyer set their own price.
    $order->set_total( floatval( $_POST['order_total'] ) ); // never trust the client
    // Field never saved to the order, so fulfillment has no VAT number.
} );
```

## Common Mistakes

- Extending block checkout with shortcode hooks (or the reverse) and seeing no effect.
- Validating only in JavaScript, so a direct POST bypasses every rule.
- Reading totals from `$_POST` instead of `WC()->cart->get_total()` after recalculation.
- Adding a checkout field but never saving it, so it is absent from the order and emails.
- Triggering fulfillment, shipping labels, or license keys on submit, before payment.
- Disabling nonce verification to work around an AJAX 403 instead of sending the nonce.

## Production Tips

- Test both checkout surfaces if the store may switch; a theme update can flip the
  default.
- Log validation failures (field name and rule, not PII) to find broken integrations
  before conversion drops.
- Load-test checkout, not just product pages — it holds locks and recalculates totals.

## AI Review Checklist

- Does the code target the correct checkout (Blocks/Store API vs shortcode)?
- Is every custom field validated on the server, not only in JavaScript?
- Are custom fields explicitly saved onto the order via `update_meta_data()`?
- Are cart totals taken from server recalculation, never from the request body?
- Is fulfillment deferred to a paid order status, not run at submission?
- Are nonces and sessions left intact rather than disabled to fix errors?

## Related

- `knowledge/woocommerce/06-customers.md`
- `knowledge/woocommerce/08-payments.md`
- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/16-security.md`
