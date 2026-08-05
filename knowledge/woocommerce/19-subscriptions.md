---
id: woocommerce/19-subscriptions
topic: woocommerce
slug: subscriptions
title: "WooCommerce Subscriptions"
type: doc
order: 19
status: ready
tags: [woocommerce, subscriptions, get_meta, on-hold, cancelled, add_action, payment_complete, charge_card]
related: [woocommerce/05-orders, woocommerce/08-payments, woocommerce/12-hooks, woocommerce/23-monitoring]
when_to_use: "Read before building, extending, or debugging any recurring-billing flow with WooCommerce Subscriptions."
---
# WooCommerce Subscriptions

## Purpose

This document defines how to build and maintain recurring billing on WooCommerce:
subscription products, renewal orders, the subscription lifecycle, payment-method changes,
and gateway tokenization. It is written so an agent can extend subscription behavior
without silently dropping charges, double-billing customers, or corrupting the renewal
schedule.

Recurring billing is powered by the WooCommerce Subscriptions extension, which adds a
`shop_subscription` post type, the `wcs_get_subscription()` API, scheduled renewal actions
run through Action Scheduler, and gateway "payment token" support. A renewal is a *new
order* linked to the subscription — see [orders](05-orders.md) — not an edit of the
original order.

## Why It Matters

Subscriptions convert a one-time bug into a repeating one. A mistake in renewal handling
does not fail once; it fails every billing cycle, for every subscriber, until someone
notices in the revenue report. The two failure modes are both severe: silently missing a
charge starves revenue, and double-charging triggers disputes and refunds that damage
gateway standing. Renewals also run *unattended* — no customer is present to retry — so the
code must handle expired cards, gateway timeouts, and duplicate scheduler runs on its own.
Because the money moves on a timer with no human in the loop, correctness and idempotency
are non-negotiable.

## Core Principles

- **A renewal is a new order created by the extension.** Read subscription state through
  `wcs_get_subscription()` / `WC_Subscription`; never mutate the original parent order to
  represent a renewal.
- **Renewals must be idempotent.** Action Scheduler can run the same renewal action twice.
  Key every charge to the subscription + period so a retry never bills twice.
- **Charge stored tokens, never stored card data.** Gateways bill renewals off a saved
  payment token; storing PANs is out of scope and a PCI violation — see [payments](08-payments.md).
- **Model the lifecycle explicitly.** `active`, `on-hold`, `pending-cancel`, `cancelled`,
  and `expired` each grant or revoke access differently. Gate entitlements on live status.
- **Prorate and switch deliberately.** Upgrades, downgrades, and early cancellations have
  money implications; use the extension's switching APIs rather than editing line items.

## Best Practices

- Hook renewal lifecycle actions: `woocommerce_scheduled_subscription_payment_{gateway}`
  to charge, `woocommerce_subscription_renewal_payment_complete` and
  `..._payment_failed` to react.
- Grant and revoke access on status change hooks (`woocommerce_subscription_status_active`,
  `..._status_on-hold`, `..._status_cancelled`), not on the initial purchase alone.
- For custom gateways, implement `process_payment` for signup and a renewal handler that
  reuses the saved token; return failure cleanly so the retry system can back off.
- Use the extension's failed-payment retry system instead of hand-rolling retries; it
  applies exponential backoff and dunning email.
- Read amounts from the subscription object (`$sub->get_total()`), which reflects switches
  and coupons, rather than recomputing from the parent order.
- Test against expired cards, declined charges, and duplicate scheduler runs, not just the
  happy path — see [testing](21-testing.md).
- Keep long-running renewal batches inside Action Scheduler so they survive deploys and
  retries; do not process renewals in a web request.

## Examples

**Good Example** — idempotent renewal charge keyed to the period

```php
// Fired by the scheduler for each due renewal on this gateway.
add_action( 'woocommerce_scheduled_subscription_payment_my_gateway', function ( $amount, WC_Order $renewal_order ) {
    $subscription = wcs_get_subscription( $renewal_order->get_meta( '_subscription_renewal' ) );
    // Idempotency key ties the charge to this subscription + billing period,
    // so a duplicate scheduler run reuses the same charge instead of billing twice.
    $idem = 'sub_' . $subscription->get_id() . '_' . $renewal_order->get_date_created()->format( 'Ym' );
    $token = WC_Payment_Tokens::get( $renewal_order->get_meta( '_payment_token_id' ) );

    $result = MyGateway::charge( $token->get_token(), $amount, $idem );

    if ( $result->succeeded ) {
        $renewal_order->payment_complete( $result->transaction_id );
    } else {
        // Let the extension's dunning/retry system own the backoff and email.
        $renewal_order->update_status( 'failed', $result->message );
    }
}, 10, 2 );
```

**Bad Example** — non-idempotent, mutates the parent order, no failure path

```php
add_action( 'woocommerce_scheduled_subscription_payment_my_gateway', function ( $amount, $renewal_order ) {
    $sub    = wcs_get_subscription( $renewal_order->get_meta( '_subscription_renewal' ) );
    $parent = $sub->get_parent();
    // Re-charging the stored card with no idempotency key: a second scheduler
    // run double-bills the customer and triggers a dispute.
    $txn = MyGateway::charge_card( $parent->get_meta( '_card_number' ), $amount );
    // Storing/reading a raw PAN is a PCI violation.
    // Mutating the parent order corrupts history; the renewal order is left in limbo.
    $parent->set_total( $amount );
    $parent->save();
    // No failure branch: a decline is silently swallowed and access is never revoked.
}, 10, 2 );
```

## Common Mistakes

- Charging renewals with no idempotency key, so a duplicate scheduler run double-bills.
- Storing raw card numbers instead of gateway tokens — a PCI violation and a breach risk.
- Editing the parent order to represent a renewal instead of using the renewal order.
- Granting access at purchase but never revoking it on `on-hold`/`cancelled`.
- Hand-rolling retry loops that hammer the gateway instead of using dunning/backoff.
- Recomputing totals from the original order, ignoring switches, proration, and coupons.
- Running renewals in a web request, so a deploy or timeout drops in-flight charges.

## Production Tips

- Alert on renewal success rate and failed-payment volume; a sudden dip means a broken
  token migration or gateway change — see [monitoring](23-monitoring.md).
- Reconcile WooCommerce renewal orders against gateway settlements daily to catch charges
  that succeeded at the gateway but failed to record locally.
- When migrating gateways, migrate tokens first and run a dry-run renewal batch in staging
  before switching production traffic.
- Keep Action Scheduler healthy and monitored; a stalled queue silently stops all billing.

## AI Review Checklist

- Is every renewal charge idempotent (keyed to subscription + period)?
- Are renewals billed against saved tokens, never stored card data?
- Does the code create/use the renewal order rather than mutating the parent order?
- Are entitlements granted and revoked on subscription status-change hooks?
- Is failure handled by returning to the extension's dunning/retry system, not a manual loop?
- Are amounts read from the subscription object so switches and proration are respected?
- Do renewals run through Action Scheduler rather than a web request?

## Related

- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/08-payments.md`
- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/23-monitoring.md`
