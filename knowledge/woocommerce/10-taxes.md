---
id: woocommerce/10-taxes
topic: woocommerce
slug: taxes
title: "Taxes"
type: doc
order: 10
status: ready
tags: [woocommerce, taxes]
related: [woocommerce/09-shipping, woocommerce/07-checkout, woocommerce/04-product-management, woocommerce/05-orders]
when_to_use: "Read before configuring tax rates/classes or writing code that computes or displays tax."
---
# Taxes

## Purpose

This document defines how WooCommerce calculates and displays tax: tax classes, rate
tables, tax-inclusive versus tax-exclusive pricing, the address the tax is based on, and
rounding. It is written so an agent can configure or extend tax logic without producing
totals that are legally wrong or that fail an audit.

Tax is calculated by WooCommerce's own engine (`WC_Tax`) from configured rate tables.
The job of code is to feed that engine correct inputs (price entry mode, class, address)
and to display results honestly — not to reimplement the math.

## Why It Matters

Tax is a legal obligation, and the amount depends on inputs that are easy to get subtly
wrong: whether entered prices already include tax, which address the tax is based on
(shop base, billing, or shipping), the product's tax class, and how rounding is applied.
A store that computes tax per line and rounds differently than the invoice, or that
treats tax-inclusive prices as exclusive, will overcharge or undercharge on every order —
and the discrepancy compounds across thousands of transactions before anyone notices.

## Core Principles

- **Configure tax; do not compute it in code.** Enter rates in the tax tables and let
  `WC_Tax`/`wc_get_price_including_tax()` do the math. Ad-hoc `price * 0.2` ignores
  classes, zones, and rounding.
- **"Prices include tax" is a global mode, not a per-value flag.** All entered prices
  are interpreted the same way; know which mode the store is in before touching prices.
- **Tax follows the configured address basis.** Rates resolve against shop base, billing,
  or shipping address per settings — never assume the shop's own country.
- **Rounding happens once, consistently.** Respect the "round at subtotal" setting;
  rounding each line independently drifts from the legal total.
- **Product tax class decides the rate.** Standard, reduced, zero, and custom classes map
  to different rows; assign the class, don't special-case in code.

## Best Practices

- Read prices with tax-aware helpers: `wc_get_price_including_tax( $product )` and
  `wc_get_price_excluding_tax( $product )`, so the store's inclusive/exclusive mode is
  honored automatically.
- Assign products to the correct tax class (e.g. reduced-rate for books/food) rather than
  overriding amounts at checkout.
- Set "calculate tax based on" (customer billing/shipping vs shop base) deliberately, and
  match it to your jurisdiction's rules (destination vs origin based).
- Keep display consistent: if you show tax-inclusive prices in the catalog, show
  tax-inclusive totals at checkout; mixing the two confuses and misleads customers.
- For cross-border digital sales (EU VAT / OSS), capture and validate the customer's
  location evidence and apply the destination rate; store it on the order for audit.
- Read collected tax off the order with `$order->get_total_tax()` and the tax-item rows,
  not by re-deriving it.

## Examples

**Good Example** — tax-aware helpers, class-driven, engine does the math

```php
// Honors the store's inclusive/exclusive mode and the product's tax class + zone.
$display_price = wc_get_price_to_display( $product ); // shop-setting aware

// Trust the engine's line calculation; read tax off the order for reporting.
$tax_collected = $order->get_total_tax();

foreach ( $order->get_taxes() as $tax_item ) {
    // Per-rate breakdown for the invoice — the same numbers the customer was charged.
    $rate_label = $tax_item->get_label();
    $amount     = $tax_item->get_tax_total();
}
```

**Bad Example** — hard-coded rate, wrong rounding, ignores mode

```php
$price = $product->get_price();          // may already INCLUDE tax → double-taxed
$tax   = round( $price * 0.20, 2 );      // hard-coded 20%: ignores class + zone
$total = $price + $tax;                  // rounds per line → drifts from invoice total
// Uses shop country implicitly, ignoring the customer's billing/shipping basis.
```

## Common Mistakes

- Multiplying by a hard-coded rate instead of using the tax tables and `WC_Tax`.
- Treating tax-inclusive entered prices as exclusive (or vice versa), double-charging.
- Rounding each line separately when the store is set to round at subtotal.
- Assuming the shop's country for the rate instead of the configured address basis.
- Ignoring product tax classes, so reduced/zero-rated goods get the standard rate.
- Showing tax-inclusive catalog prices but tax-exclusive checkout totals.
- Re-deriving collected tax for reports instead of reading `get_total_tax()`.

## Production Tips

- Reconcile `get_total_tax()` sums against your filing periods; a drift signals a
  rounding or basis misconfiguration.
- When rates change on a date, add new rate rows effective from that date rather than
  editing existing ones, so historical orders keep their original tax.
- Test each tax class and each zone boundary (including zero-rate and exempt customers)
  with fixture orders in CI.

## AI Review Checklist

- Is tax computed by `WC_Tax`/tax-aware helpers, never a hard-coded multiplier?
- Does price handling respect the store's inclusive/exclusive mode?
- Is the rate resolved against the configured address basis, not the shop country?
- Is rounding applied per the store setting (line vs subtotal), consistently?
- Are products assigned the correct tax class instead of overriding amounts?
- Is collected tax read from the order (`get_total_tax()`, tax items) for reporting?

## Related

- `knowledge/woocommerce/09-shipping.md`
- `knowledge/woocommerce/07-checkout.md`
- `knowledge/woocommerce/04-product-management.md`
- `knowledge/woocommerce/05-orders.md`
