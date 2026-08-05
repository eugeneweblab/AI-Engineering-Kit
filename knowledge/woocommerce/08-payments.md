---
id: woocommerce/08-payments
topic: woocommerce
slug: payments
title: "Payments"
type: doc
order: 8
status: ready
tags: [woocommerce, payments, payment_complete, wc_get_order, process_payment, WC_Payment_Gateway, charge, get_total]
related: [woocommerce/07-checkout, woocommerce/05-orders, woocommerce/16-security, woocommerce/11-coupons]
when_to_use: "Read before building or reviewing a payment gateway, webhook handler, or refund flow."
---
# Payments

## Purpose

This document defines how WooCommerce takes money: the `WC_Payment_Gateway` contract,
the `process_payment()` return protocol, asynchronous confirmation via webhooks, and
refunds. It is written so an agent can integrate a gateway without capturing the wrong
amount, double-charging, or marking unpaid orders as paid.

Payments are the one place where a code bug moves real money. The rules here are
non-negotiable because the failure mode is financial loss or a chargeback, not a broken
page.

## Why It Matters

A payment integration spans three parties — the browser, WooCommerce, and the payment
processor — over an unreliable network. The customer may close the tab mid-redirect;
the processor may deliver a webhook twice or out of order. If the gateway trusts the
amount from the browser, marks the order paid before the processor confirms, or
processes the same webhook twice, the store either loses money or ships goods that were
never paid for. Because card data is involved, PCI scope also makes this the most
regulated code in the store.

## Core Principles

- **The order total is the source of truth for the amount.** Charge
  `$order->get_total()`, never a value from the request. The client cannot set its own
  price.
- **Only the processor confirms payment.** Mark an order paid via
  `$order->payment_complete( $txn_id )` after the gateway (return or webhook) confirms —
  never on redirect alone.
- **Webhooks must be idempotent.** The same event will arrive more than once; guard on
  the transaction id so re-delivery is a no-op.
- **Verify webhook authenticity.** Check the signature/HMAC before acting; an unsigned
  webhook is an attacker-controlled request.
- **Keep card data out of your server.** Use the processor's tokenization/hosted fields
  to stay out of PCI scope. Never log a PAN or CVV.

## Best Practices

- Extend `WC_Payment_Gateway` and return the documented array from `process_payment()`:
  `[ 'result' => 'success', 'redirect' => ... ]`, or add a `wc_add_notice()` error and
  return failure. Do not `echo` or redirect manually.
- Call `$order->payment_complete( $transaction_id )` exactly once on confirmation; store
  the transaction id so re-entry is detectable.
- In webhook handlers, load the order, check its current status, and short-circuit if it
  is already paid before doing anything.
- Verify the webhook signature with the processor's shared secret and reject on mismatch
  with a 4xx.
- Issue refunds through `wc_create_refund()` (or the gateway's refund method), which
  writes the refund record and adjusts totals — never just call the processor's API.
- Store the customer's saved payment method as a WooCommerce token
  (`WC_Payment_Token_CC`) for off-session and subscription charges.

## Examples

**Good Example** — order-total amount, idempotent confirmation

```php
public function process_payment( $order_id ) {
    $order  = wc_get_order( $order_id );
    // Charge what the server computed, not anything from the browser.
    $charge = $this->api->charge( $order->get_total(), $order->get_currency() );

    if ( 'succeeded' === $charge->status ) {
        // payment_complete() moves the order to processing/completed and is the
        // single authoritative "paid" transition.
        $order->payment_complete( $charge->id );
        return [ 'result' => 'success', 'redirect' => $this->get_return_url( $order ) ];
    }
    wc_add_notice( __( 'Payment failed.', 'my-gw' ), 'error' );
    return [ 'result' => 'failure' ];
}

public function handle_webhook( $event ) {
    $this->verify_signature( $event );              // reject forged webhooks
    $order = wc_get_order( $event->order_id );
    if ( $order->is_paid() ) {
        return; // idempotent: re-delivery of the same event is a no-op
    }
    $order->payment_complete( $event->transaction_id );
}
```

**Bad Example** — trusts the client, no idempotency, paid on redirect

```php
public function process_payment( $order_id ) {
    $order = wc_get_order( $order_id );
    // Buyer controls the amount → they set their own price.
    $this->api->charge( $_POST['amount'] );
    // Marks paid before the processor confirms; a closed tab = free order.
    $order->update_status( 'completed' );
    return [ 'result' => 'success' ];
}

public function handle_webhook( $event ) {
    // No signature check → anyone can POST "paid". No idempotency → double fulfillment.
    wc_get_order( $event->order_id )->payment_complete( $event->transaction_id );
}
```

## Common Mistakes

- Charging an amount from `$_POST` instead of `$order->get_total()`.
- Marking the order paid on redirect return, before the processor confirms.
- Webhook handlers with no signature verification, accepting forged "paid" events.
- Non-idempotent webhooks that fulfill twice when the processor re-delivers.
- Refunding via the raw processor API without `wc_create_refund()`, so totals drift.
- Logging card numbers, CVVs, or full webhook payloads containing them.
- Building custom card forms that pull PAN through your server and expand PCI scope.

## Production Tips

- Make webhooks the primary confirmation path; treat the browser return as a hint only.
- Return non-2xx from webhook handlers on transient failure so the processor retries.
- Reconcile daily: compare processor settlements against WooCommerce paid orders to
  catch missed webhooks.
- Test with the processor's sandbox for the negative paths: declined card, duplicate
  webhook, out-of-order events, refund.

## AI Review Checklist

- Is the charge amount taken from `$order->get_total()`, never the request?
- Is "paid" set only via `payment_complete()` after processor confirmation?
- Are webhook signatures verified before any action?
- Are webhook handlers idempotent (guarded on paid status / transaction id)?
- Are refunds issued through `wc_create_refund()` so totals stay correct?
- Is card data tokenized and kept out of logs and your server?

## Related

- `knowledge/woocommerce/07-checkout.md`
- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/11-coupons.md`
