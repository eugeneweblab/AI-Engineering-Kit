---
id: woocommerce/09-shipping
topic: woocommerce
slug: shipping
title: "Shipping"
type: doc
order: 9
status: ready
tags: [woocommerce, shipping, quote, get_cart, wp_list_pluck, in_array]
related: [woocommerce/07-checkout, woocommerce/10-taxes, woocommerce/04-product-management, woocommerce/05-orders]
when_to_use: "Read before configuring shipping zones/methods or writing a custom shipping-rate calculation."
---
# Shipping

## Purpose

This document defines how WooCommerce calculates shipping: zones, methods, shipping
classes, packages, and custom `WC_Shipping_Method` rate calculation. It is written so
an agent can add or modify shipping logic without producing wrong rates, unshippable
carts, or rates that leak across regions.

Shipping in WooCommerce is a matching problem: the cart's destination is matched to the
first zone that contains it, and that zone's methods produce the rates. Get the model
wrong and customers either see no options or the wrong price.

## Why It Matters

Shipping cost is added to the order total, so an error here is a pricing error — you
either overcharge (lost sales, disputes) or undercharge (eroded margin on every order).
The zone-matching order is significant and non-obvious: WooCommerce evaluates zones
top-to-bottom and stops at the first match, with "Rest of the World" as the fallback.
Custom rate code that mutates global state, ignores the passed package, or forgets
per-item shipping classes silently produces rates that look plausible but are wrong.

## Core Principles

- **Zones are matched in order; first match wins.** Order specific zones above broad
  ones. A destination never sees a lower zone once an earlier one matches.
- **Rates are computed per package, from the passed `$package`.** Read the destination
  and contents from the argument, not from `WC()->cart` global state.
- **Register rates with `add_rate()`.** Do not echo, set session, or write totals
  directly; return rates through the method's API.
- **Shipping classes drive per-product cost.** Assign classes on products and read them
  in the method; do not hard-code product ids.
- **Free shipping is a condition, not a zero rate.** Use the free-shipping method with a
  minimum-amount/coupon requirement so it appears only when it should.

## Best Practices

- Model geography with zones (country/state/postcode), and put the most specific zones
  first; keep "Rest of the World" as the explicit fallback.
- Implement custom carriers by extending `WC_Shipping_Method` and implementing
  `calculate_shipping( $package )`; call `$this->add_rate( [...] )` for each option.
- Compute weight/dimensions from `$package['contents']` items, honoring each product's
  shipping class, so bulky/heavy goods cost correctly.
- Cache slow live-rate API calls (carrier quotes) keyed by destination + contents hash;
  checkout recalculates often and a slow call blocks the page.
- Return an empty rate set (no options) rather than a bogus fallback when a destination
  is genuinely unserviceable — a wrong rate is worse than none.
- Set `taxable` correctly on each rate so [tax](10-taxes.md) applies to shipping where
  the jurisdiction requires it.

## Examples

**Good Example** — reads the package, adds rates via the API

```php
class My_Shipping_Method extends WC_Shipping_Method {
    public function calculate_shipping( $package = [] ) {
        // Weight comes from THIS package's contents, honoring shipping class per item.
        $weight = 0.0;
        foreach ( $package['contents'] as $item ) {
            $weight += (float) $item['data']->get_weight() * $item['quantity'];
        }
        $country = $package['destination']['country']; // from the argument, not globals

        $cost = $this->quote( $country, $weight ); // your rating logic / cached carrier call

        $this->add_rate( [
            'id'        => $this->get_rate_id(),
            'label'     => $this->title,
            'cost'      => $cost,
            'taxable'   => true, // let tax settings decide if shipping is taxed
        ] );
    }
}
```

**Bad Example** — global state, echoed price, hard-coded product

```php
public function calculate_shipping( $package = [] ) {
    // Reads the global cart, so nested/multi-package carts compute the wrong weight.
    $weight = WC()->cart->get_cart_contents_weight();

    if ( in_array( 123, wp_list_pluck( WC()->cart->get_cart(), 'product_id' ), true ) ) {
        $cost = 0; // hard-coded product id — breaks the moment the catalog changes
    } else {
        $cost = 9.99; // flat guess, ignores destination entirely
    }
    echo $cost; // never echo; rates are returned via add_rate()
}
```

## Common Mistakes

- Ordering a broad zone above a specific one, so the specific zone is never reached.
- Reading cart contents from `WC()->cart` instead of the passed `$package`.
- Returning a flat fallback rate for unserviceable destinations, silently mispricing.
- Ignoring shipping classes, so heavy or oversized items ship at the light-item price.
- Making an uncached carrier API call on every recalculation, stalling checkout.
- Forgetting `taxable`, so shipping tax is under- or over-charged.
- Hard-coding product ids in rate logic instead of using shipping classes.

## Production Tips

- Log the chosen zone and method id per order to diagnose "wrong rate" reports fast.
- Add a circuit breaker around live carrier APIs: on timeout, fall back to a table rate
  rather than blocking checkout.
- Recalculate shipping after cart edits in tests — quantity and address changes must
  reprice.

## AI Review Checklist

- Are zones ordered specific-to-broad, with an explicit "Rest of the World" fallback?
- Does custom rate code read destination and contents from `$package`, not globals?
- Are rates returned via `add_rate()`, never echoed or written to session/totals?
- Do per-item costs honor shipping classes rather than hard-coded product ids?
- Are slow carrier calls cached and guarded against timeouts?
- Is each rate's `taxable` flag set so shipping tax is correct?

## Related

- `knowledge/woocommerce/07-checkout.md`
- `knowledge/woocommerce/10-taxes.md`
- `knowledge/woocommerce/04-product-management.md`
- `knowledge/woocommerce/05-orders.md`
