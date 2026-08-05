---
id: woocommerce/11-coupons
topic: woocommerce
slug: coupons
title: "Coupons"
type: doc
order: 11
status: ready
tags: [woocommerce, coupons, Exception, get_total, apply_coupon, set_total, strtotime, get_current_user_id]
related: [woocommerce/07-checkout, woocommerce/08-payments, woocommerce/05-orders, woocommerce/04-product-management]
when_to_use: "Read before creating coupons programmatically or writing custom discount/validation logic."
---
# Coupons

## Purpose

This document defines how WooCommerce discounts work: the `WC_Coupon` object, discount
types, usage limits and restrictions, validation, and applying coupons to the cart and
order. It is written so an agent can create or extend coupon logic without letting a
discount be abused, stacked incorrectly, or reused past its limit.

A coupon is a stored object with rules; the cart engine reads those rules to compute the
discount. Correct coupon code means letting the engine enforce the rules and adding
validation through the proper hooks — not discounting totals by hand.

## Why It Matters

Coupons directly reduce revenue, and unlike a pricing bug they are adversarial: customers
share codes, script redemptions, and probe for stacking loopholes. WooCommerce enforces
usage limits, expiry, minimum spend, and product restrictions — but only when the discount
flows through `WC_Coupon` and the cart's coupon API. Code that subtracts from the total
directly, or checks limits client-side, bypasses every guard: a single-use code becomes
infinite-use, an expired code keeps working, and margins evaporate at scale.

## Core Principles

- **Let the cart apply and enforce coupons.** Use `WC()->cart->apply_coupon( $code )` and
  `WC_Coupon`; never subtract a discount from the total yourself.
- **Usage limits are enforced at redemption, server-side.** Set `usage_limit` /
  `usage_limit_per_user`; the engine increments counts on order completion. Do not track
  usage in client state.
- **Restrictions are data on the coupon.** Minimum/maximum spend, included/excluded
  products and categories, and individual-use are coupon fields — set them, don't
  reimplement the checks.
- **Add custom rules via validation hooks.** Extend eligibility through
  `woocommerce_coupon_is_valid` (throw `Exception`), so the standard flow still applies.
- **Codes are case-insensitive and must be unique.** Generate unpredictable codes for
  single-use promos so they cannot be guessed.

## Best Practices

- Create coupons with the CRUD object and `save()`, setting the discount type and
  restrictions explicitly, rather than inserting `shop_coupon` posts by hand.
- Choose the right `discount_type`: `percent`, `fixed_cart`, or `fixed_product`; each
  applies at a different scope, so the wrong one over- or under-discounts.
- Set `individual_use` on codes that must not stack, and `exclude_sale_items` where
  promos should not compound with markdowns.
- Enforce redemption caps with `usage_limit` and `usage_limit_per_user`; add expiry with
  `date_expires`.
- For custom eligibility (customer segment, first order, cart composition), hook
  `woocommerce_coupon_is_valid` and throw an `Exception` with a clear message.
- Generate single-use codes with a cryptographically random suffix and one redemption cap
  so a leaked code cannot be mass-redeemed.

## Examples

**Good Example** — CRUD coupon with real restrictions, engine applies it

```php
$coupon = new WC_Coupon();
$coupon->set_code( 'WELCOME10-' . wp_generate_password( 8, false ) ); // unguessable
$coupon->set_discount_type( 'percent' );
$coupon->set_amount( 10 );
$coupon->set_minimum_amount( 30 );          // enforced server-side by the cart engine
$coupon->set_individual_use( true );        // cannot stack with other coupons
$coupon->set_usage_limit( 1 );              // single redemption, counted on completion
$coupon->set_date_expires( strtotime( '+30 days' ) );
$coupon->save();

// Applying goes through the cart so every restriction and limit is checked.
$applied = WC()->cart->apply_coupon( $coupon->get_code() );
```

Custom eligibility via the validation hook:

```php
add_filter( 'woocommerce_coupon_is_valid', function ( $valid, $coupon ) {
    if ( 'firstorder' === $coupon->get_code() && wc_get_customer_order_count( get_current_user_id() ) > 0 ) {
        // Throwing keeps the standard failure UX and messaging.
        throw new Exception( __( 'This code is for first orders only.', 'my-plugin' ) );
    }
    return $valid;
}, 10, 2 );
```

**Bad Example** — manual discount, no limits, client-trusted

```php
// Bypasses WC_Coupon entirely: no usage limit, no expiry, no min-spend, no restrictions.
if ( $_POST['coupon'] === 'SAVE20' ) {
    $new_total = WC()->cart->get_total( 'edit' ) * 0.8; // hand-computed discount
    WC()->cart->set_total( $new_total );                // stackable + reusable forever
}
```

## Common Mistakes

- Subtracting a discount from the total directly, bypassing all limits and restrictions.
- Tracking usage counts in client/session state instead of the coupon's server-side limit.
- Using the wrong `discount_type` (`fixed_cart` vs `fixed_product`), mis-scaling the
  discount.
- Forgetting `individual_use`/`exclude_sale_items`, so promos stack and compound.
- Predictable single-use codes that get guessed and mass-redeemed.
- Implementing custom eligibility outside `woocommerce_coupon_is_valid`, so the standard
  apply/remove flow does not enforce it.
- No `date_expires`, leaving promotional codes live indefinitely.

## Production Tips

- Log coupon apply failures (code + reason, not PII) to spot abuse and broken promos.
- For high-value promos, prefer per-user unique codes over one shared code so a leak is
  contained.
- Reconcile discount totals per campaign against order reports to catch stacking loopholes.

## AI Review Checklist

- Are discounts applied via `WC()->cart->apply_coupon()` / `WC_Coupon`, never manually?
- Are usage limits, expiry, and minimum spend set as coupon data and enforced server-side?
- Is `individual_use` / `exclude_sale_items` set where stacking must be prevented?
- Is the `discount_type` correct for the intended scope?
- Is custom eligibility added through `woocommerce_coupon_is_valid`?
- Are single-use codes unpredictable and capped so a leak cannot be mass-redeemed?

## Related

- `knowledge/woocommerce/07-checkout.md`
- `knowledge/woocommerce/08-payments.md`
- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/04-product-management.md`
